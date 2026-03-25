"""Elo series probability and Monte Carlo series simulator"""

from __future__ import annotations

import numpy as np
from scipy.stats import binom


def get_elo_series_prob(elo_a, elo_b):
    p_a = 1 / (10 ** (-(elo_a - elo_b) / 400) + 1)
    p_a_series = binom.sf(3, 7, p_a)
    return p_a_series


def simulate_monte_carlo_series(fav_stats, und_stats, iterations=10000):
    und_game_series = 0

    for i in range(iterations):
        fav_game_wins = 0
        und_game_wins = 0

        while fav_game_wins < 4 and und_game_wins < 4:
            score_fav = np.random.normal(fav_stats["PPG"], fav_stats["STD_PTS"])
            score_und = np.random.normal(und_stats["PPG"], und_stats["STD_PTS"])

            if score_und > score_fav:
                und_game_wins += 1
            else:
                fav_game_wins += 1
        if und_game_wins == 4:
            und_game_series += 1
    return und_game_series / iterations
