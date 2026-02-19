# tests/test_cli.py

from click.testing import CliRunner
from TSP import cli

def test_simulate_command():
    runner = CliRunner()
    # Only use existing --plot option
    result = runner.invoke(cli, ["simulate", "--plot"])
    assert result.exit_code == 0


