#!/usr/bin/env python

import random
from typing import Dict, Tuple, List


def tsp(
    cities: Dict[str, Dict[str, float]],
    seed: int | None = None,
) -> Tuple[float, List[str]]:
    """
    Generate a random TSP tour and compute its total distance.

    Args:
        cities: Dictionary of city-to-city distances.
        seed: Optional random seed for deterministic behavior.

    Returns:
        total_distance: Total round-trip distance.
        route: Ordered list of cities visited.
    """
    if seed is not None:
        random.seed(seed)

    route = list(cities.keys())
    random.shuffle(route)

    total_distance = 0.0
    n = len(route)

    for i in range(n):
        next_index = (i + 1) % n  # ensures return to start
        total_distance += cities[route[i]][route[next_index]]

    return total_distance, route


def create_cities() -> Dict[str, Dict[str, int]]:
    """Create sample distance matrix."""
    return {
        "New York": {
            "New York": 0,
            "Chicago": 800,
            "Denver": 1400,
            "Los Angeles": 2100,
        },
        "Chicago": {
            "New York": 800,
            "Chicago": 0,
            "Denver": 600,
            "Los Angeles": 1300,
        },
        "Denver": {
            "New York": 1400,
            "Chicago": 600,
            "Denver": 0,
            "Los Angeles": 700,
        },
        "Los Angeles": {
            "New York": 2100,
            "Chicago": 1300,
            "Denver": 700,
            "Los Angeles": 0,
        },
    }


def run_simulation(iterations: int = 100) -> Tuple[float, List[str]]:
    """
    Run multiple random tours and return the best one.
    """
    cities = create_cities()

    best_distance = float("inf")
    best_route: List[str] = []

    for _ in range(iterations):
        distance, route = tsp(cities)
        if distance < best_distance:
            best_distance = distance
            best_route = route

    return best_distance, best_route


def main() -> None:
    """CLI entry point."""
    best_distance, best_route = run_simulation()
    print(f"Best distance: {best_distance}")
    print(f"Route: {best_route}")


if __name__ == "__main__":
    main()
