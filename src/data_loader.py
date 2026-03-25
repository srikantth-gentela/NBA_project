"""Fetch league game log via nba_api; optional CSV cache under the repo (no Desktop paths)."""

from __future__ import annotations

import random
import time
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import leaguegamelog
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout

# Browser-like headers help avoid slow reads / blocks from stats.nba.com.
NBA_STATS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.nba.com/",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.nba.com",
}


_RETRYABLE_REQUEST_ERRORS = (ReadTimeout, ConnectTimeout, ConnectionError)


def load_games_df(
    season: str = "2024-25",
    season_type_all_star: str = "Regular Season",
    *,
    cache_path: str | Path | None = None,
    timeout: int = 180,
    headers: dict[str, str] | None = None,
    max_retries: int = 5,
    retry_base_seconds: float = 4.0,
) -> pd.DataFrame:
    """
    Same end result as:

        gamelog = leaguegamelog.LeagueGameLog(...)
        games_df = gamelog.get_data_frames()[0]

    If ``cache_path`` points to an existing CSV, loads from disk instead.

    Retries on transient timeouts / connection errors (common with stats.nba.com).
    """
    if cache_path is not None:
        p = Path(cache_path)
        if p.is_file():
            return pd.read_csv(p)

    hdr = headers if headers is not None else NBA_STATS_HEADERS
    games_df: pd.DataFrame | None = None
    last_err: BaseException | None = None
    for attempt in range(max(1, max_retries)):
        try:
            gamelog = leaguegamelog.LeagueGameLog(
                season=season,
                season_type_all_star=season_type_all_star,
                headers=hdr,
                timeout=timeout,
            )
            games_df = gamelog.get_data_frames()[0]
            break
        except _RETRYABLE_REQUEST_ERRORS as e:
            last_err = e
            if attempt >= max_retries - 1:
                raise
            delay = retry_base_seconds * (2**attempt) + random.uniform(0, 2.0)
            time.sleep(delay)

    if games_df is None:
        raise RuntimeError("load_games_df failed without returning data") from last_err

    if cache_path is not None:
        p = Path(cache_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        games_df.to_csv(p, index=False)

    return games_df
