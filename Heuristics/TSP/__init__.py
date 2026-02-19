"""
Heuristics – collection of greedy algorithms and heuristic optimization methods
(coin change, TSP approximations, etc.)
"""

__version__ = "0.1.0"

# ───────────────────────────────────────────────
# Public API (library functions only)
# ───────────────────────────────────────────────

# Coin algorithms
from .coin import greedy_coin_change
from .greedy_coin import greedy_coin

# TSP algorithms
from .tsp import tsp
from .tsp_dict import tsp as tsp_dict
from .tsp_pandas import create_cities, tsp_pandas

# City utilities
from .fetch_cities_lat_long import (
    my_cities,
    create_cities_dataframe,
    main,

)

# CLI entry
from .cli import cli

__all__ = [
    "greedy_coin_change",
    "greedy_coin",
    "tsp",
    "tsp_dict",
    "tsp_pandas",
    "create_cities",
    "my_cities",
    "create_cities_dataframe",
    "cli",
    "main"
]
