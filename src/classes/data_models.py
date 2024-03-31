from typing import Optional

class Team:
    def __init__(
        self,
        name,
        seed,
        rating=None
    ):
        self.name: str = name
        self.seed: int = seed
        self.rating: Optional[float] = rating


class Bye(Team): 
    def __init__(
            self
    ): 
        self.name: str = "Bye"
        self.seed: int = -1
        self.rating: Optional[float] = None