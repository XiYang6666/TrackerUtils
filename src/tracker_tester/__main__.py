import asyncio
import sys

from .app import app
from .commands import load_commands


def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    load_commands()
    app()


if __name__ == "__main__":
    main()
