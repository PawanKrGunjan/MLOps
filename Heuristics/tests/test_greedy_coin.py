# tests/test_greedy_coin.py
from TSP import greedy_coin


def test_greedy_coin_zero():
    assert greedy_coin(0.25) == {
        0.25: 1,
        0.10: 0,
        0.05: 0,
        0.01: 0,
    }


def test_greedy_coin_large_amount():
    result = greedy_coin(1.51)
    assert result[0.25] == 6
    assert result[0.01] == 1
    assert sum(result.values()) >= 1
