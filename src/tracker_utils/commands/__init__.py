from importlib.metadata import version

import typer

from ..app import app
from ..util import add_config_options, print


def version_callback(value: bool):
    if value:
        version_str = version("tracker-utils")
        print(f"{version_str}")
        raise typer.Exit()


@app.callback()
@add_config_options(hides=["show_failed", "retry_times", "timeout"])
def main(version: bool = typer.Option(False, "--version", "-v", help="Show version and exit.", callback=version_callback)): ...


def load_commands():
    from . import (
        client_test,  # noqa: F401
        set_trackers,  # noqa: F401
        test,  # noqa: F401
    )
