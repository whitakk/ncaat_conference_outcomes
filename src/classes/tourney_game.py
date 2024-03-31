from typing import List, Dict, Optional
from abc import ABC, abstractmethod

import numpy as np 
import pandas as pd

from src.classes.data_models import Team
from src.classes.constants import SEED_MODEL_PATH
from src.classes.helpers import normalize_probabilities


class AbstractGame(ABC): 
    def __init__(
        self,  
    ): 
        @abstractmethod
        def get_winner(): 
            pass
        
        @abstractmethod
        def to_dict():
            pass


class TournamentGame(AbstractGame):
    def __init__(
        self, 
        round,
        game_index, 
        feeder_game_1=None,
        feeder_game_2=None,
    ): 
        self.round: int = round
        self.game_index: int = game_index

        self.team_1: Optional[Team] = None
        self.team_2: Optional[Team] = None
        self.winner: Optional[Team] = None

        self.feeder_game_1: AbstractGame = feeder_game_1
        self.feeder_game_2: AbstractGame = feeder_game_2
        
        self.refresh_participants()


    def to_dict(self) -> None: 
        """return a dict of attributes"""
        d = {
            'round': self.round,
            'game_index': self.game_index,
            'team_1': self.team_1,
            'team_2': self.team_2,
            'winner': self.winner
        }
        if self.feeder_game_1 is not None: 
            d['feeder_game_1'] = self.feeder_game_1
        if self.feeder_game_2 is not None: 
            d['feeder_game_2'] = self.feeder_game_2

    
    def load_teams(self, team_1: Team=None, team_2: Team=None) -> None: 
        """
        for loading teams when there is no feeder game
        (if a team was already loaded and is also passed in here,
        this will overwrite the prior team) 
        """

        if team_1 is not None: 
            self.team_1 = team_1
        
        if team_2 is not None: 
            self.team_2 = team_2


    def refresh_participants(self) -> None: 
        """
        update who is playing in the game
        based on winners of feeder games
        """

        if self.feeder_game_1 is not None: 
            self.team_1 = self.feeder_game_1.get_winner()
        if self.feeder_game_2 is not None: 
            self.team_2 = self.feeder_game_2.get_winner()


    def get_winner(self) -> Team:
        """
        return the winner if game has been simulated, 
        else None
        """

        return self.winner
    

    def set_feeder_game(self, feeder_game: AbstractGame, team_index: int) -> None: 
        """
        change one of the feeder games
        primary use case: adding byes into a balanced bracket
            that has already been created
        """

        if team_index==1: 
            self.feeder_game_1=feeder_game
        elif team_index==2: 
            self.feeder_game_2=feeder_game
        else: 
            raise ValueError(f"invalid team_index {team_index}")
        
        self.refresh_participants()


    def simulate_game(self) -> None: 
        """
        simulate a winner from the game
          - use team ratings if they exist 
          - otherwise use team seeds
        """

        if self.team_1 is None or self.team_2 is None: 
            raise ValueError(
                f"Teams not loaded for round {self.round}, ix {self.game_index}"
            )

        rating_1, rating_2 = self.team_1.rating, self.team_2.rating
        if rating_1 and rating_2: 
            team_1_win_pct = self._predict_wp_from_ratings()
        else: 
            team_1_win_pct = self._predict_wp_from_seeds()

        rnd = np.random.random()
        if rnd < team_1_win_pct: 
            self.winner = self.team_1
        else: 
            self.winner = self.team_2

    
    def _predict_wp_from_ratings(self) -> float: 
        raise NotImplementedError(
            "wp from ratings not yet implemented"
        )
    

    def _predict_wp_from_seeds(self) -> float: 
        """
        predict winner of game based on how teams of their seeds
        have performed in the given round
        """

        seed_model = pd.read_csv(SEED_MODEL_PATH)
        seed_1 = self.team_1.seed
        seed_2 = self.team_2.seed
        round = self.round
        
        p1_raw = seed_model.loc[seed_model.seed==seed_1, str(round)].values[0]
        p2_raw = seed_model.loc[seed_model.seed==seed_2, str(round)].values[0]

        norm_p = normalize_probabilities([p1_raw, p2_raw])
        return norm_p[0]
    

class TournamentBye(AbstractGame):
    def __init__(
            self, 
            round, 
            game_index,
            team=None
    ): 
        self.round: int = round
        self.game_index: int = game_index

        self.team: Optional[Team] = team
        self.winner = self.team

    
    def to_dict(self) -> Dict: 
        d = {
            'round': self.round, 
            'game_index': self.game_index
        }
        if self.team is not None: 
            d['team'] = self.team 
        if self.winner is not None: 
            d['winner'] = self.winner

        return d
    
    
    def load_team(self, team: Team) -> None: 
        self.team = team
        self.winner = team


    def get_winner(self) -> Team: 
        if self.winner is None: 
            raise ValueError("bye team has not yet been loaded")
        
        return self.winner

