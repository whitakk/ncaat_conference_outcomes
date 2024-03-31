# TODO: add argument for # iterations
from tqdm import tqdm
import argparse

import pandas as pd
import numpy as np
np.random.seed(11)

from src.classes.tourney import Tournament
from src.classes.data_models import Team
from src.classes.constants import (
    SEASON_RANGE, 
    TOURNEY_ROUNDS, 
    DEFAULT_SIMS_PER_SEASON, 
    DATA_PATH,
    MODEL_PATH
)   

parser = argparse.ArgumentParser(description="Simulate tournaments")
parser.add_argument(
    "--simulations",
    type=int,
    help='number of simulations to run', 
    default=DEFAULT_SIMS_PER_SEASON
)

if __name__ == "__main__":
    args = parser.parse_args()

    all_teams = pd.read_csv(f'{MODEL_PATH}/tourney_teams.csv')
    all_outcomes = {}
    summary_outcomes = pd.DataFrame()
    
    for season in tqdm(SEASON_RANGE):

        team_data = all_teams[all_teams.season==season].to_dict('records')
        teams = []
        season_outcomes = {}
        for td in team_data:
            # already loaded in corret order upstream 
            teams.append(Team(td['team'], td['seed']))
            season_outcomes[td['team']] = []
    
        for _ in tqdm(range(args.simulations)):            
            tourney = Tournament(rounds=TOURNEY_ROUNDS)
            tourney.load_first_round_teams(teams)
            tourney_bracket = tourney.get_bracket()

            for r in range(TOURNEY_ROUNDS): 
                for g in tourney_bracket[r]: 
                    g.refresh_participants()
                    g.simulate_game()

            wins = dict(tourney.count_wins_by_team())
            # can probably optimize this better
            for tm in season_outcomes: 
                season_outcomes[tm].append(wins.get(tm, 0))

        season_summary = {k:sum(v)/len(v) for k,v in season_outcomes.items()}
        season_df = pd.DataFrame(list(season_summary.items()), columns=['team','wins'])
        season_df['season'] = season
        summary_outcomes = pd.concat([summary_outcomes, season_df])

        # perhas useful for bootstrapping analysis
        all_outcomes[season] = season_outcomes

    summary_outcomes = summary_outcomes.merge(
        all_teams[['season','team','conf','seed']], how='left', on=['season','team']
    )
    seed_expectations = summary_outcomes.groupby('seed')['wins'].mean().reset_index()
    summary_outcomes = summary_outcomes.merge(
        seed_expectations, how='left', on='seed', suffixes=('','_exp')
    )
    summary_outcomes['pase'] = summary_outcomes['wins'] - summary_outcomes['wins_exp']

    # do remaining analysis in notebook
    summary_outcomes.to_csv(f'{DATA_PATH}sim_pase.csv', index=False)

