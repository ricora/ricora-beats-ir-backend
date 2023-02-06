import math


def calculate(score: float, level: int) -> int:
    ratio = 0.8 / (1 + math.exp(-0.8 * score + 74)) if score <= 95.371 else 0.059 * (score - 100) + 1
    return int(ratio * level * 50)
