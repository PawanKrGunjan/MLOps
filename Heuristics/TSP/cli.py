"""
Command Line Interface for Heuristics package.
"""

import click
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
from .tsp_pandas import create_cities, tsp_pandas
from .visualization import plot_path


@click.group()
def cli():
    """TSP command-line tool."""

@cli.command()
@click.option("--count", default=1, type=int, help="Number of simulations to run")
@click.option("--plot", is_flag=True, help="Plot the best route")
def simulate(count, plot):
    cities_df = create_cities()
    best_distance = float("inf")
    best_route_order = None

    for _ in range(count):
        route_order, total_distance = tsp_pandas(cities_df)
        if total_distance < best_distance:
            best_distance = total_distance
            best_route_order = route_order

    print("Best route:", best_route_order)
    print("Total distance:", best_distance)

    if plot and best_route_order:
        plot_path(best_route_order)



@cli.command()
@click.option(
    "--city",
    multiple=True,
    type=str,
    help="Custom city names (must include latitude & longitude in code).",
)
def cities(city):
    """
    Run simulation with custom city names (basic demo).
    """
    if not city:
        click.echo("Please provide at least one city using --city.")
        return

    click.echo(f"Received cities: {city}")
    click.echo("Custom city mode not fully implemented yet.")
