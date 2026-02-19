# tests/test_tsp.py
import pandas as pd
from TSP import tsp_pandas


def test_tsp_returns_distance_and_route():
    data = {
        "city": ["A", "B", "C"],
        "latitude": [0, 0, 1],
        "longitude": [0, 1, 1],
    }
    df = pd.DataFrame(data)

    path_df, total_distance = tsp_pandas(df)

    assert isinstance(total_distance, float)
    assert isinstance(path_df, list)
    assert len(path_df) == 3
    assert set(path_df) == {"A", "B", "C"}
    assert total_distance > 0
