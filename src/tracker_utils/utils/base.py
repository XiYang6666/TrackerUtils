from datetime import timedelta
from pathlib import Path
from typing import Any, Iterable

import click


def safe_div(a: int, b: int) -> float:
    if b == 0:
        return 0.0
    return a / b


def create_rate_str(a: int, b: int) -> str:
    return f"{a}/{b} ({safe_div(a, b):.2%})"


def read_lines(content: str) -> list[str]:
    return [line.strip() for line in content.strip().splitlines() if line.strip()]


def write_lines(path: Path | str, lines: Iterable[str], sort: bool = False):
    f = open(path, "w")
    for line in if_sort(lines, sort):
        f.write(line)
        f.write("\n")
    f.close()


def if_sort[T: Any](iterable: Iterable[T], sort: bool) -> Iterable[T]:
    if sort:
        return sorted(iterable)
    return iterable


class TimedeltaParser(click.ParamType):
    name = "timedelta"

    def convert(self, value: str, param, ctx) -> timedelta:
        if value.endswith("ms"):
            return timedelta(milliseconds=float(value[:-2]))
        if value.endswith("s"):
            return timedelta(seconds=float(value[:-1]))
        if value.endswith("m"):
            return timedelta(minutes=float(value[:-1]))
        if value.endswith("h"):
            return timedelta(hours=float(value[:-1]))
        return timedelta(seconds=float(value))


timedelta_parser = TimedeltaParser()
