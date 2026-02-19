# tests/test_tsp_dict.py

from TSP import tsp_dict
import pytest


@pytest.fixture
def cities():
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





def test_tsp_dict():
    cities = {
        "A": {"A": 0, "B": 1, "C": 2},
        "B": {"A": 1, "B": 0, "C": 1},
        "C": {"A": 2, "B": 1, "C": 0},
    }
    distance, route = tsp_dict(cities)
    assert isinstance(distance, (int, float))
    assert isinstance(route, list)
    assert len(route) == 3
    assert distance >= 0


def test_tsp_deterministic(cities):
    distance1, route1 = tsp_dict(cities, seed=1)
    distance2, route2 = tsp_dict(cities, seed=1)

    # With same seed, results must match
    assert distance1 == distance2
    assert route1 == route2
