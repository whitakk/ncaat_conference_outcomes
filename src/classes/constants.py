from typing import Tuple, List

# repo params
# from root
DATA_PATH = './data/'
MODEL_PATH = './models/'
SEED_MODEL_PATH: str = MODEL_PATH + 'seed_advancement.csv'

# simulation params
DEFAULT_SIMS_PER_SEASON: int = 1000
# no tourney in 2020 :(
SEASON_RANGE: List = [i for i in range(2008,2024) if i!=2020]
# bound estimated probabilities to avoid too-extreme predictions
# and handle potential divide-by-zero problems
WIN_PROBABILITY_BOUNDS: Tuple = (0.01, 0.99)

# tournament params
SEED_ORDER: List = [1,16,8,9,4,13,5,12,6,11,3,14,7,10,2,15]
TOURNEY_ROUNDS: int = 6
