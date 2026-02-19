#!/usr/bin/env python

"""
CLI tool to approximate the shortest distance to visit all cities in a list.
Uses random TSP simulation.
"""

import json
import os
from random import shuffle
from typing import List, Tuple

import click
import pandas as pd
from geopy.distance import distance as geodistance
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

CACHE_FILE = "city_cache.json"


# -------------------------
# Utility / Helper Functions
# -------------------------


def my_cities(*args: str) -> List[str]:
    """Build a list of cities from input"""
    return list(args)


def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache: dict):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f)


# -------------------------
# Geocoding
# -------------------------


def create_cities_dataframe(
    cities: List[str] = None,
    geolocator=None,
) -> pd.DataFrame:
    """
    Create a Pandas DataFrame of cities and their latitudes and longitudes.
    Supports dependency injection for testing.
    """

    if cities is None:
        cities = [
            "New York",
            "Knoxville",
            "Birmingham",
            "Baltimore",
            "Bangor",
            "Cleveland",
            "Chicago",
            "Denver",
            "Los Angeles",
            "San Francisco",
            "Raleigh",
            "Seattle",
            "Boston",
            "Houston",
            "Dallas",
            "Miami",
            "Atlanta",
            "Fort Worth",
            "Phoenix",
            "San Diego",
        ]

    cache = load_cache()

    if geolocator is None:
        geolocator = Nominatim(user_agent="tsp_pandas")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    else:
        geocode = geolocator.geocode

    latitudes = []
    longitudes = []

    for city in cities:
        if city in cache:
            lat, lon = cache[city]
        else:
            location = geocode(city)
            if location is None:
                raise ValueError(f"Could not geocode city: {city}")
            lat, lon = location.latitude, location.longitude
            cache[city] = (lat, lon)

        latitudes.append(lat)
        longitudes.append(lon)

    save_cache(cache)

    return pd.DataFrame(
        {
            "city": cities,
            "latitude": latitudes,
            "longitude": longitudes,
        }
    )


# -------------------------
# TSP Logic (Pure Function)
# -------------------------


def tsp(cities_df: pd.DataFrame) -> Tuple[float, List[str]]:
    """
    Randomized Traveling Salesman approximation.
    Pure function — easy to test.
    """

    city_list = cities_df["city"].to_list()
    shuffle(city_list)

    total_distance = 0.0

    for i in range(len(city_list)):
        current_city = city_list[i]
        next_city = city_list[(i + 1) % len(city_list)]

        current_row = cities_df[cities_df["city"] == current_city].iloc[0]
        next_row = cities_df[cities_df["city"] == next_city].iloc[0]

        dist = geodistance(
            (current_row["latitude"], current_row["longitude"]),
            (next_row["latitude"], next_row["longitude"]),
        ).miles

        total_distance += dist

    return total_distance, city_list


# -------------------------
# Main Simulation
# -------------------------


def main(count: int, df: pd.DataFrame = None) -> None:
    """
    Run simulation multiple times and print shortest route.
    """

    if df is None:
        df = create_cities_dataframe()

    distances = []
    routes = []

    for i in range(count):
        distance, route = tsp(df)
        print(f"Simulation {i}: total distance = {distance:.2f} miles")
        distances.append(distance)
        routes.append(route)

    shortest_index = distances.index(min(distances))

    print("\nShortest Distance:", min(distances))
    print("Cities Visited:", routes[shortest_index])


# -------------------------
# CLI
# -------------------------


@click.group()
def cli():
    """TSP command-line tool."""


@cli.command("cities")
@click.argument("cities", nargs=-1)
@click.option("--count", default=5, help="Number of simulations to run")
def cities_cli(cities, count):
    """Run simulation for custom cities."""
    city_list = my_cities(*cities)
    cities_df = create_cities_dataframe(city_list)
    main(count, cities_df)


@cli.command("simulate")
@click.option("--count", default=10, help="Number of simulations to run")
def simulate(count):
    """Run simulation using default city list."""
    main(count)


# -------------------------
# Entry Point
# -------------------------
if __name__ == "__main__":
    cli()
