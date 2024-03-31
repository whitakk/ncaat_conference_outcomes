from typing import List

from src.classes.constants import WIN_PROBABILITY_BOUNDS

def normalize_probabilities(p_list: List[float]) -> float: 
    """
    normalize probabilities to sum to 1
    """

    lower, upper = WIN_PROBABILITY_BOUNDS
    adj_list = [min(upper, max(lower, p)) for p in p_list]
    sum_p = sum(adj_list)
    return [p/sum_p for p in adj_list]
    

def flatten_list(list_2d: List[List]) -> List: 
    """
    turn 2-d list into 1-d list 
    """
    return [item for sublist in list_2d for item in sublist]
