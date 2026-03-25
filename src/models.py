"""Elo state machine and team DNA / tiers (matches original Assignment2 notebook)."""

from __future__ import annotations

import pandas as pd


def init_elo_mature(all_games: pd.DataFrame) -> dict:
    """First 30 unique home teams start at 1500; returns a fresh dict you can mutate as ELO_MATURE."""
    current_elo = {}
    for team in all_games.get("HOME_TEAM"):
        if team in current_elo:
            continue
        else:
            current_elo[team] = 1500
        if len(current_elo) == 30:
            break
    return current_elo.copy()


def apply_elo_updates(all_games: pd.DataFrame, ELO_MATURE: dict, k_factor: float = 20) -> None:
    """Walk ``all_games`` rows and update ``ELO_MATURE`` in place (MOV multiplier as in notebook)."""
    for index, row in all_games.iterrows():
        home_team = row["HOME_TEAM"]
        away_team = row["AWAY_TEAM"]

        home_elo = ELO_MATURE[home_team]
        away_elo = ELO_MATURE[away_team]

        elo_diff = home_elo - away_elo

        expected_home = 1 / (10 ** (-elo_diff / 400) + 1)

        S = 1 if row["WL_HOME"] == "W" else 0

        margin = abs(row["HOME_PTS"] - row["AWAY_PTS"])
        elo_winner_diff = elo_diff if S == 1 else -elo_diff

        mov_mult = ((margin + 3) ** 0.8) / (7.5 + 0.006 * elo_winner_diff)

        shift = k_factor * mov_mult * (S - expected_home)

        ELO_MATURE[home_team] += shift
        ELO_MATURE[away_team] -= shift


def static_dna_from_games(games_df: pd.DataFrame) -> pd.DataFrame:
    """Same groupby/agg as ``Static_DNA`` in the notebook."""
    return (
        games_df.groupby("TEAM_NAME")
        .agg(
            PPG=("PTS", "mean"),
            STD_PTS=("PTS", "std"),
            AVG_3PM=("FG3M", "mean"),
            STD_3PM=("FG3M", "std"),
            AVG_3PA=("FG3A", "mean"),
        )
        .reset_index()
    )


def name_to_abbrev_map(games_df: pd.DataFrame) -> dict:
    mapping_df = games_df[["TEAM_NAME", "TEAM_ABBREVIATION"]].drop_duplicates()
    return dict(zip(mapping_df["TEAM_NAME"], mapping_df["TEAM_ABBREVIATION"]))


def build_elo_dna(Static_DNA: pd.DataFrame, name_to_abb: dict, ELO_MATURE: dict) -> pd.DataFrame:
    ELO_DNA = Static_DNA.copy()
    ELO_DNA["Abb"] = ELO_DNA["TEAM_NAME"].map(name_to_abb)
    ELO_DNA["ELO"] = ELO_DNA["Abb"].map(ELO_MATURE)
    return ELO_DNA


def tier_frames(ELO_DNA: pd.DataFrame):
    """Return (df_benchmark, df_wildcard, df_control) before the sort-by-Elo cells."""
    elo_67 = ELO_DNA["ELO"].quantile(0.67)
    elo_33 = ELO_DNA["ELO"].quantile(0.33)

    three_std_67 = ELO_DNA["STD_3PM"].quantile(0.67)
    three_std_33 = ELO_DNA["STD_3PM"].quantile(0.33)

    df_benchmark = ELO_DNA[ELO_DNA["ELO"] >= elo_67]
    df_wildcard = ELO_DNA[(ELO_DNA["ELO"] <= elo_33) & (ELO_DNA["STD_3PM"] >= three_std_67)]
    df_control = ELO_DNA[(ELO_DNA["ELO"] <= elo_67) & (ELO_DNA["STD_3PM"] <= three_std_33)]

    return df_benchmark, df_wildcard, df_control
