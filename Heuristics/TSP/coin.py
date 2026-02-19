def greedy_coin_change(change: float) -> int:
    cents = round(change * 100)
    coins = 0

    for coin in [25, 10, 5, 1]:
        while cents >= coin:
            cents -= coin
            coins += 1

    return coins


def main():
    while True:
        change = float(input("Change owed: "))
        if change > 0:
            break

    print(greedy_coin_change(change))
