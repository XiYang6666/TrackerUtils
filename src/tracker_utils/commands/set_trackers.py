from pathlib import Path
from typing import List, Optional

import click
import typer

from ..app import app
from ..functions.set_tracker import BtClientOptions, set_tracker
from ..util import read_lines


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


@app.command("set-trackers", help="Set trackers for qbittorrent client")
def cmd_set_trackers(
    url: str = typer.Argument(..., help="Url of the qbittorrent web ui"),
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
    trackers_urls: List[str] = typer.Option(
        [],
        "--trackers-urls",
        "-t",
        help="List of trackers urls",
        callback=tracker_url_checker,
    ),
    tackers_file: Optional[Path] = typer.Option(
        None,
        "--tackers-file",
        "-f",
        callback=tracker_file_checker,
        help="Path to the file containing trackers",
    ),
):
    urls = trackers_urls
    if tackers_file:
        urls += read_lines(tackers_file.read_text())
    set_tracker(
        urls,
        BtClientOptions(url=url, user=username, pwd=password),
    )
