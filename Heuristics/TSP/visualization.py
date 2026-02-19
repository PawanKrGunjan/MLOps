import os
import matplotlib
import matplotlib.pyplot as plt
from .tsp_pandas import create_cities

# Use non-interactive backend in CI / headless environments
if os.environ.get("CI"):
    matplotlib.use("Agg")


def plot_path(route, save_path="tsp_route.png"):
    """
    Plots the TSP route.

    Parameters:
    - route: list of city names in order
    - save_path: file path to save the plot (default: tsp_route.png)

    Behavior:
    - In CI (headless), the plot is saved automatically.
    - Locally, the plot window is displayed for interactive viewing.
    """
    df = create_cities()
    df = df.set_index("city").loc[route]  # order cities

    plt.figure(figsize=(8, 6))
    plt.plot(df["longitude"], df["latitude"], marker="o", linestyle="-", color="blue")

    for i, city in enumerate(df.index):
        plt.text(
            df.loc[city, "longitude"], df.loc[city, "latitude"], f"{i + 1}. {city}"
        )

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("TSP Route")
    plt.grid(True)

    # Save the plot to file
    plt.savefig(save_path)

    # Only show the plot locally (not in CI)
    if not os.environ.get("CI"):
        plt.show()

    plt.close()
