from typing import List, Dict
from collections import Counter

from src.classes.tourney_game import AbstractGame, TournamentGame
from src.classes.data_models import Team
from src.classes.helpers import flatten_list

class Tournament: 
    def __init__(
        self, 
        rounds
    ):
        self.bracket: List[List[AbstractGame]] = self._create_bracket(rounds)

    
    def _create_bracket(self, rounds: int) -> None: 
        """
        creates a balanced bracket with given # of rounds

        for imbalanced brackets, replace games with byes
        """

        bracket = []
        for r in range(rounds): 
            round = []
            games = 2**(rounds-r-1)
            for g in range(games): 
                
                feeder_game_1 = None
                feeder_game_2 = None
                if r>0: 
                    feeder_game_1 = bracket[r-1][g*2]
                    feeder_game_2 = bracket[r-1][g*2+1]

                game = TournamentGame(
                    r+1,  # 1-index rounds
                    g, 
                    feeder_game_1, 
                    feeder_game_2
                )
                round.append(game)

            bracket.append(round)

        return bracket
    

    def get_bracket(self) -> List[List[AbstractGame]]: 
        return self.bracket


    def load_first_round_teams(self, teams: List[Team]) -> None: 
        """
        Load teams for first round games
        """

        # teams must be loaded in order they will play in bracket
        # 0 vs 1 play in R1, winner plays winner of 2 vs 3, etc

        if len(teams) > len(self.bracket[0])*2: 
            raise ValueError(f"""
                too many teams in list {len(teams)}
                for tournament with {len(self.bracket[0])}
                first round games
            """)
        
        if len(teams) < len(self.bracket[0])*2: 
            raise NotImplementedError(
                "Tournament requires byes which are not yet implemented"
            )
        
        for g in range(len(self.bracket[0])): 
            team_1 = teams[g*2]
            team_2 = teams[g*2+1]
            self.bracket[0][g].load_teams(team_1, team_2) 


    def count_wins_by_team(self) -> Dict: 
        """
        return a dict of team name and wins in the tournament, 
        for all teams winning at least one game
        """

        tourney_games = flatten_list(self.bracket)
        game_winners = [g.get_winner().name for g in tourney_games]
        return Counter(game_winners)