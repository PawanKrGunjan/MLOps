"""
Greedy Nearest-Neighbor TSP implementation (DataFrame input).

Returns:
    (total_distance: float, route: list[str])
"""

import math
import random
import pandas as pd


def euclidean_distance(lat1, lon1, lat2, lon2):
    """Compute Euclidean distance between two coordinates."""
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)


def tsp(df: pd.DataFrame):
    """
    Solve TSP using greedy nearest neighbor algorithm.

    Parameters
    ----------
    df : pandas.DataFrame
        Must contain columns: city, latitude, longitude

    Returns
    -------
    total_distance : float
    route : list[str]
    """

    if df.empty:
        return 0.0, []

    # Copy to avoid mutation
    df = df.copy()

    # Deterministic start for test reproducibility
    random.seed(42)

    start_city = random.choice(df["city"].tolist())

    route = [start_city]

    remaining = df[df["city"] != start_city].copy()

    total_distance = 0.0
    current_row = df[df["city"] == start_city].iloc[0]

    while not remaining.empty:
        distances = remaining.apply(
            lambda row: euclidean_distance(
                current_row["latitude"],
                current_row["longitude"],
                row["latitude"],
                row["longitude"],
            ),
            axis=1,
        )

        nearest_idx = distances.idxmin()
        nearest_row = remaining.loc[nearest_idx]

        total_distance += distances.loc[nearest_idx]

        route.append(nearest_row["city"])

        current_row = nearest_row
        remaining = remaining.drop(index=nearest_idx)

    return float(total_distance), route
