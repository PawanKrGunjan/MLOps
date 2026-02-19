# tests/test_fetch_cities.py
import pytest
import pandas as pd
from TSP import my_cities, create_cities_dataframe, main


@pytest.mark.slow
def test_my_cities():
    result = my_cities("New York", "Knoxville", "Los Angeles", "Chicago")
    assert isinstance(result, list)
    assert result == [
        "New York",
        "Knoxville",
        "Los Angeles",
        "Chicago",
    ]


@pytest.mark.slow
def test_create_cities_dataframe():
    cities = my_cities("New York", "Chicago")
    df = create_cities_dataframe(cities)
    assert isinstance(df, pd.DataFrame)
    assert all(col in df.columns for col in ["city", "latitude", "longitude"])
    assert len(df) == 2


@pytest.mark.slow
def test_main_runs_without_error():
    result = main(count=1)
    assert result is None
