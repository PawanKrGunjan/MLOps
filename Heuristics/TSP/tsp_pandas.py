import numpy as np
import pandas as pd
import random


def create_cities():
    return pd.DataFrame(
        {
            "city": [
                "New York",
                "Los Angeles",
                "Chicago",
                "Houston",
                "Philadelphia",
                "Phoenix",
                "San Antonio",
                "San Diego",
                "Dallas",
                "San Jose",
            ],
            "latitude": [
                40.7128,
                34.0522,
                41.8781,
                29.7604,
                39.9526,
                33.4484,
                29.4241,
                32.7157,
                32.7767,
                37.3382,
            ],
            "longitude": [
                -74.0060,
                -118.2437,
                -87.6298,
                -95.3698,
                -75.1652,
                -112.0740,
                -98.4936,
                -117.1611,
                -96.7970,
                -121.8863,
            ],
        }
    )


def euclidean_distance(lat1, lon1, lat2, lon2):
    return np.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)
#
#
# def tsp_pandas(df: pd.DataFrame):
#     df = df.copy()
#     random.seed(42)  # deterministic for testing
#
#     start_city = random.choice(df["city"].tolist())
#
#     route_df = df[df["city"] == start_city].copy()
#     remaining = df[df["city"] != start_city].copy()
#
#     while not remaining.empty:
#         last = route_df.iloc[-1]
#         distances = euclidean_distance(
#             remaining["latitude"], remaining["longitude"], last["latitude"], last["longitude"]
#         )
#         nearest_idx = distances.idxmin()
#         route_df = pd.concat([route_df, remaining.loc[[nearest_idx]]], ignore_index=True)
#         remaining = remaining.drop(index=nearest_idx)
#
#     # compute total distance
#     total_distance = 0.0
#     for i in range(1, len(route_df)):
#         total_distance += euclidean_distance(
#             route_df.iloc[i - 1]["latitude"],
#             route_df.iloc[i - 1]["longitude"],
#             route_df.iloc[i]["latitude"],
#             route_df.iloc[i]["longitude"],
#         )
#
#     route_list = route_df["city"].tolist()  # extract city order
#
#     # ✅ Return distance first, then route list
#     return float(total_distance), route_list

def tsp_pandas(df: pd.DataFrame):
    df = df.copy()
    random.seed(42)  # deterministic for testing
    start_city = random.choice(df["city"].tolist())

    route = df[df["city"] == start_city].copy()
    remaining = df[df["city"] != start_city].copy()

    while not remaining.empty:
        last = route.iloc[-1]
        distances = np.sqrt(
            (remaining["latitude"] - last["latitude"]) ** 2
            + (remaining["longitude"] - last["longitude"]) ** 2
        )
        nearest_idx = distances.idxmin()
        route = pd.concat([route, remaining.loc[[nearest_idx]]], ignore_index=True)
        remaining = remaining.drop(index=nearest_idx)

    # Compute total distance
    total_distance = 0.0
    for i in range(1, len(route)):
        total_distance += np.sqrt(
            (route.iloc[i]["latitude"] - route.iloc[i - 1]["latitude"]) ** 2
            + (route.iloc[i]["longitude"] - route.iloc[i - 1]["longitude"]) ** 2
        )

    # Return list of city names (for plotting) and total distance
    return route["city"].tolist(), float(total_distance)
