from importlib.metadata import version

import typer

from ..utils.commands import add_config_options
from ..utils.output import print
from . import (
    client_test,
    set_trackers,
    test,
)


def version_callback(value: bool):
    if value:
        version_str = version("tracker-utils")
        print(f"{version_str}")
        raise typer.Exit()


def load_commands(app: typer.Typer):
    @app.callback()
    @add_config_options(hides=["show_failed", "retry_times", "timeout"])
    def main(version: bool = typer.Option(False, "--version", "-v", help="Show version and exit.", callback=version_callback)): ...

    app.add_typer(test.cmd)
    app.add_typer(client_test.cmd)
    app.add_typer(set_trackers.cmd)
