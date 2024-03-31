"""
Download historical tourney outcomes from barttorvik.com and store locally
"""

import json
import requests
import ssl
import time
from copy import copy 

import pandas as pd
import numpy as np

from src.classes.constants import SEASON_RANGE, DATA_PATH

ssl._create_default_https_context = ssl._create_unverified_context


def scrape_tourney_outcomes(yr): 
    """
    get tourney outcomes (advancement, PASE, PAKE)

    please don't scrape Bart's site like this usually!
    I'm only doing it here because it's a couple dozen years
    and a small table for each year, which I couldn't find 
    through his other data extracts
    """

    url = f"https://barttorvik.com/cgi-bin/ncaat.cgi?conlimit=&yrlow={yr}&yrhigh={yr}&type=team&sort=1"
    df = pd.read_html(url)[0]
    df['season'] = yr
    df.columns = [c.lower() for c in df.columns]

    conf_map = get_team_conferences(yr)
    df = df.merge(conf_map)
    return df

def get_team_conferences(yr):
    """
    get a list of conference affiliations by team for the given year
    """

    r = requests.get(f'https://barttorvik.com/{yr}_team_results.json')
    json_data = json.loads(r.text)

    # data has no labels -> manually identify columns
    all_cols = ['rank','team','conf'] + ['_']*42 # unused columns
    df = pd.DataFrame(json_data, columns=all_cols)[['team','conf']]

    return df

def get_team_seeds(): 
    """
    get seed by team for all years
    """

    r = requests.get(f'https://barttorvik.com/all_ncaa.json')
    json_data = json.loads(r.text)

    df = pd.DataFrame(json_data)
    df = df.reset_index().rename(columns={'index':'team'}).melt(id_vars='team',var_name='season',value_name='seed').dropna()
    for c in ['season','seed']: 
        df[c] = pd.to_numeric(df[c])

    # correct one data point that's wrong
    df.loc[(df.season==2016)&(df.team=='Iona'), 'seed'] = 13

    return df.sort_values(['season','seed','team'])

def get_all_seed_outcomes(): 
    """
    get advancement by round for all seeds for use in simulation
    """

    url = 'https://barttorvik.com/cgi-bin/ncaat.cgi?conlimit=&yrlow=2008&yrhigh=2023&type=seed'
    df = pd.read_html(url)[0]
    df.columns = [c.lower() for c in df.columns]
    return df

def get_team_regions(): 
    """
    there's no single source of teams by region in the bracket 
    but we can infer it recursively from the game history 
    since each final 4 team comes out of a distinct region 
    """

    game_stats = get_all_games()
    game_stats['date'] = pd.to_datetime(game_stats['date'])
    game_stats['year'] = game_stats['date'].dt.year
    game_stats['month'] = game_stats['date'].dt.month
    game_stats['season'] = np.where(
        game_stats['month']>4,
        game_stats['year'] + 1, 
        game_stats['year']
    )

    all_regions = pd.DataFrame()

    for season in SEASON_RANGE: 
        season_games = game_stats[game_stats.season==season].sort_values('date').copy()
        
        # get list of final 4 teams (one from each region) 
        # preserving order of teams meeting each other in final
        final_game = season_games.sort_values(['date'], ascending=True).tail(2) 
            # each game listed twice, once for each team 
        final_teams = list(final_game.team.unique())
        final_date = final_game['date'].unique()[0]
        
        f4_teams = []
        for team in final_teams: 
            f4_game = season_games[(season_games.team==team)&(season_games['date']<final_date)].tail(1)
            f4_date = f4_game['date'].values[0]
            f4_opp = f4_game.opp.values[0]
            f4_teams = f4_teams + [team, f4_opp]
        
        # add all other teams in the same region
        regions = {}
        for i in range(len(f4_teams)): 
            team = f4_teams[i]
            region_teams = [team]
            prior_date = copy(f4_date)
            for round in range(4): # ignore first four, in line with Torvik PASE analysis
                new_teams = []
                new_date = copy(prior_date)
                for team in region_teams: 
                    prior_game = season_games[(season_games.team==team)&(season_games['date']<prior_date)].tail(1)
                    prior_game_date = prior_game['date'].values[0]
                    prior_opp = prior_game.opp.values[0]

                    # ad-hoc correction for covid year when a game got canceled
                    if season==2021 and round==3 and team=='Oregon': 
                        prior_opp = 'VCU'
                        prior_game_date = new_date
                    
                    new_date = min(new_date, prior_game_date)
                    new_teams.append(prior_opp)

                prior_date = copy(new_date)
                region_teams = region_teams + new_teams

            regions[i] = region_teams

        season_df = pd.DataFrame(regions).melt(var_name='region', value_name='team')
        season_df['season'] = season

        all_regions = pd.concat([all_regions, season_df])

    return all_regions


def get_all_games():
    """
    get game-by-game records,
    with each team having a record for each game
    """

    r = requests.get('https://barttorvik.com/getgamestats.php')
    json_data = json.loads(r.text)

    # print("team-games found:", len(json_data))

    all_cols = ['date', 'del_1', 'team', 'conf', 'opp', 'location', 'result', 'adj_o', 'adj_d', 'o_ppp', 'o_efg', 'o_to', 'o_or', 'o_ftr', 'd_ppp', 'd_efg',
                'd_to', 'd_or', 'd_ftr', 'gsc', 'conf_opp', 'team_id', 'season', 'pace', 'game_id', 'coach', 'opp_coach', 'plus_minus', 'del_2', 'del_3', 'del_4']
    # data has no labels -> manually identified columns
    df = pd.DataFrame(json_data, columns=all_cols)

    return df

def main(): 
    
    data = pd.DataFrame()
    
    for yr in SEASON_RANGE: 
        print(f"adding data for {yr}")
        yr_df = scrape_tourney_outcomes(yr)
        data = pd.concat([data, yr_df])

        # be nice while scraping
        time.sleep(5)

    seeds = get_team_seeds()
    all_regions = get_team_regions()
    data = data.merge(seeds, how='left', on=['season','team']
                      ).merge(all_regions, how='left', on=['season','team'])
    data.to_csv(f'{DATA_PATH}tourney_outcomes.csv', index=False)

    seed_outcomes = get_all_seed_outcomes()
    seed_outcomes.to_csv(f'{DATA_PATH}seed_outcomes.csv', index=False)

main()