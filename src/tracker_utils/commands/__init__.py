from importlib.metadata import version

import typer

from ..app import app
from ..utils.commands import add_config_options


def version_callback(value: bool):
    if value:
        version_str = version("tracker-utils")
        print(f"{version_str}")
        raise typer.Exit()


def load_commands():
    @app.callback()
    @add_config_options(hides=["show_failed", "rich_output", "retry_times", "timeout"])
    def main(version: bool = typer.Option(False, "--version", "-v", help="Show version and exit.", callback=version_callback)): ...

    from . import (  # noqa: I001
        test,  # noqa: F401
        client_test,  # noqa: F401
        set_trackers,  # noqa: F401
    )
