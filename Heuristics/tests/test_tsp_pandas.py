# tests/test_tsp_pandas.py

import pytest
from TSP import create_cities, tsp_pandas


@pytest.fixture
def cities():
    return create_cities()


def test_tsp_pandas(cities):
    route, distance = tsp_pandas(cities)

    assert isinstance(distance, float)
    assert distance > 0
    assert isinstance(route, list)
    assert len(route) == len(cities)
