import matplotlib.pyplot as plt
from .tsp_pandas import create_cities

def plot_path(route):
    """
    route: list of city names in order
    """
    df = create_cities()
    df = df.set_index("city").loc[route]  # order cities

    plt.figure(figsize=(8, 6))
    plt.plot(df["longitude"], df["latitude"], marker="o", linestyle="-", color="blue")

    for i, city in enumerate(df.index):
        plt.text(df.loc[city, "longitude"], df.loc[city, "latitude"], f"{i+1}. {city}")

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("TSP Route")
    plt.grid(True)
    plt.show()
