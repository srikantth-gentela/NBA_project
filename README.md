# NBA upset probability (Elo vs Monte Carlo)

Research code that pulls NBA team game logs with **`nba_api`**, builds an in-season Elo rating, defines team “DNA” tiers, then compares **Elo-based** best-of-seven upset probabilities to **Monte Carlo** series simulations.

## Repo layout

```text
data/raw/                 # CSV cache after the first successful API call (optional to commit)
src/
  __init__.py
  data_loader.py          # LeagueGameLog + optional cache (no absolute laptop paths)
  models.py               # Elo init/update, Static_DNA, tier splits (same logic as original notebook)
  simulation.py           # get_elo_series_prob, simulate_monte_carlo_series
notebooks/
  research_final.ipynb    # Clean version of the analysis (mirrors Assignment2 flow)
requirements.txt
README.md
```

## Setup

```bash
cd nba-upset-research
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the notebook

From the repo root:

```bash
jupyter notebook notebooks/research_final.ipynb
```

The first code cell sets `ROOT` and adds `src/` to `sys.path`. Game data is loaded via the NBA Stats API (or from `data/raw/league_gamelog_2024_25.csv` if that cache file already exists). Delete the cache file to force a new download.

## GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

To avoid committing large cached CSVs, add `_data/raw/*.csv` to `.gitignore` (see `.gitignore` comments).
