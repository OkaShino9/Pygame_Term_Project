import random

class Dice:
    def roll(self) -> int:
        return random.randint(1, 6)
