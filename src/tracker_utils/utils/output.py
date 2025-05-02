from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn, TimeRemainingColumn

from .. import config

colored_console = Console(color_system="auto")
plain_console = Console(color_system=None)


def get_console():
    if config.rich_output:
        return colored_console
    return plain_console


def print(s: str):
    get_console().print(s)


def fail(s: str):
    if config.show_failed:
        print(f"[yellow]{s}[/yellow]")


def create_progress() -> Progress:
    return Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[progress.completed]{task.completed}/{task.total}"),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        console=get_console(),
    )
