import asyncio
from pathlib import Path
from typing import List, Optional

import click
import typer

from ..functions.test import test
from ..utils.base import read_lines
from ..utils.commands import add_config_options

cmd = typer.Typer(
    name="test",
    help="Test trackers",
)


def final_check(ctx: click.Context):
    obj: dict = ctx.obj
    if "has_url" not in obj or "has_file" not in obj:
        return
    if not (obj["has_url"] or obj["has_file"]):
        raise click.UsageError("Please provide tracker provider urls or file.")


def provider_url_checker(ctx: click.Context, value: List[str]):
    ctx.obj = ctx.obj or {}
    ctx.obj["has_url"] = bool(value)
    final_check(ctx)
    return value


def provider_file_checker(ctx: click.Context, value: Optional[Path]):
    ctx.obj = ctx.obj or {}
    ctx.obj["has_file"] = value is not None
    final_check(ctx)
    return value


@cmd.callback()
@add_config_options()
def cmd_test(
    tracker_provider_urls: List[str] = typer.Option(
        [],
        "--tracker-provider-urls",
        "-u",
        help="Tracker provider urls",
        callback=provider_url_checker,
    ),
    tracker_provider_file: Optional[Path] = typer.Option(
        None,
        "--tracker-provider-file",
        "-f",
        help="Tracker provider file",
        callback=provider_file_checker,
    ),
    output_txt_dir: Optional[Path] = typer.Option(
        None,
        "--output-txt-dir",
        "-o",
        help="Output directory for txt files",
    ),
    output_json_path: Optional[Path] = typer.Option(
        None,
        "--output-json-path",
        help="Output path for json file",
    ),
    format_json: bool = typer.Option(
        False,
        "--format-json/--no-format-json",
        help="Format json file",
    ),
    sort: bool = typer.Option(
        True,
        "--sort/--no-sort",
        help="Sort output data",
    ),
):
    urls = tracker_provider_urls
    if tracker_provider_file:
        urls += read_lines(tracker_provider_file.read_text())
    asyncio.run(
        test(
            urls,
            output_txt_dir=output_txt_dir,
            output_json_path=output_json_path,
            format_json=format_json,
            sort=sort,
        )
    )
