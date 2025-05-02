import asyncio
import sys

import typer

from .commands import load_commands

app = typer.Typer()
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_commands(app)
