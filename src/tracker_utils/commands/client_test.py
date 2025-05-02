import asyncio
from datetime import timedelta
from pathlib import Path
from typing import List, Optional

import click
import typer

from ..app import app
from ..functions.client_test import ClientTestOptions, client_test
from ..utils.base import read_lines, timedelta_parser
from ..utils.commands import add_config_options


def final_check(ctx: click.Context):
    obj: dict = ctx.obj
    if "has_url" not in obj or "has_file" not in obj:
        return
    if not (obj["has_url"] or obj["has_file"]):
        raise click.UsageError("Please provide tracker urls or file.")


def tracker_url_checker(ctx: click.Context, value: List[str]):
    ctx.obj = ctx.obj or {}
    ctx.obj["has_url"] = bool(value)
    final_check(ctx)
    return value


def tracker_file_checker(ctx: click.Context, value: Optional[Path]):
    ctx.obj = ctx.obj or {}
    ctx.obj["has_file"] = value is not None
    final_check(ctx)
    return value


@app.command(
    "client-test",
    help="Test Trackers by a qbittorrent client",
    rich_help_panel="Tracker Tester",
)
@add_config_options(
    hides=["retry_times"],
    defaults={"timeout": typer.Option("5m", "--timeout", "-t", help="Timeout for contact all trackers", click_type=timedelta_parser)},
)
def cmd_client_test(
    url: str = typer.Argument(..., help="Url of the qbittorrent web ui"),
    torrent: str = typer.Argument(..., help="Torrent name or hash"),
    output_path: Path = typer.Option(
        ...,
        "--output-path",
        "-o",
        help="Path to the output file",
    ),
    trackers_urls: List[str] = typer.Option(
        [],
        "--trackers-urls",
        "-t",
        callback=tracker_url_checker,
        help="List of trackers urls",
    ),
    tackers_file: Optional[Path] = typer.Option(
        None,
        "--tackers-file",
        "-f",
        callback=tracker_file_checker,
        help="Path to the file containing trackers",
    ),
    username: Optional[str] = typer.Option(
        None,
        "--username",
        "-u",
        envvar="QBITTORRENT_USERNAME",
        help="Username for the qbittorrent client",
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        envvar="QBITTORRENT_PASSWORD",
        help="Password for the qbittorrent client",
    ),
    fast_mode: bool = typer.Option(
        False,
        "--fast-mode",
        "-F",
        help="Connection failure if tracker is updating with errors in Fast mode",
    ),
    polling_interval: timedelta = typer.Option(
        "100ms",
        "--polling-interval",
        "-i",
        help="Interval in seconds between tracker contact attempts",
        click_type=timedelta_parser,
    ),
    yes_all: bool = typer.Option(
        False,
        "--yes-all",
        "-y",
        help="Answer yes to all prompts",
    ),
):
    urls = trackers_urls
    if tackers_file:
        urls += read_lines(tackers_file.read_text())
    asyncio.run(
        client_test(
            urls,
            ClientTestOptions(url=url, user=username, pwd=password, torrent=torrent),
            output_path,
            fast_mode=fast_mode,
            polling_interval=polling_interval.total_seconds(),
            yes_all=yes_all,
        )
    )
