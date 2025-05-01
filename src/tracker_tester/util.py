import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Coroutine, Iterable, Optional

import typer
from rich import print
from rich.progress import BarColumn, Progress, TaskID, TextColumn, TimeElapsedColumn, TimeRemainingColumn

from . import config
from .config import ConfigKeys


def fail(s: str):
    if config.show_failed:
        print(f"[yellow]{s}[/yellow]")


def safe_div(a: int, b: int) -> float:
    if b == 0:
        return 0.0
    return a / b


def create_rate_str(a: int, b: int) -> str:
    return f"{a}/{b} ({safe_div(a, b):.2%})"


def read_lines(content: str) -> list[str]:
    return [line.strip() for line in content.strip().splitlines() if line.strip()]


def create_progress() -> Progress:
    return Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[progress.completed]{task.completed}/{task.total}"),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
    )


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


def retry_factory(progress: Progress, taskid: TaskID):
    def decorator[T](func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T | None]]:
        async def wrapper(*args, **kwargs):
            for i in range(config.retry_times):
                if i != 0:
                    fail(f"Retry func {func.__name__} {i + 1}/{config.retry_times}")
                result = await func(*args, **kwargs)
                if result is not None:
                    progress.update(taskid, advance=1)
                    return result
            progress.update(taskid, advance=1)
            return None

        return wrapper

    return decorator


def infinite_loop_factory[T](func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
    async def wrapper(*args, **kwargs):
        while True:
            await func(*args, **kwargs)

    return wrapper


def merge_params(func2: Callable):
    def decorator(func1: Callable):
        sig1 = inspect.signature(func1)
        sig2 = inspect.signature(func2)
        for param in sig2.parameters.values():
            if param.name in sig1.parameters:
                raise ValueError(f"Duplicate parameter {param.name} in {func1.__name__} and {func2.__name__}")
        new_params = list(sig1.parameters.values()) + list(sig2.parameters.values())
        new_sig = sig1.replace(parameters=new_params)

        def wrapper(*args, **kwargs):
            func1_kwargs = {k: v for k, v in kwargs.items() if k in sig1.parameters.keys()}
            func2_kwargs = {k: v for k, v in kwargs.items() if k in sig2.parameters.keys()}
            func2(**func2_kwargs)
            return func1(*args, **func1_kwargs)

        wrapper.__signature__ = new_sig
        return wrapper

    return decorator


def patch_param(name: str, default: Optional[Any] = None, annotation: Optional[Any] = None):
    def decorator(func: Callable):
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        new_params = [
            p
            if p.name != name
            else inspect.Parameter(
                name,
                p.kind,
                annotation=annotation if annotation is not None else p.annotation,
                default=default if default is not None else p.default,
            )
            for p in params
        ]
        new_sig = sig.replace(parameters=new_params)

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.__signature__ = new_sig
        return wrapper

    return decorator


@dataclass
class PatchParamsOption:
    name: str
    default: Optional[Any] = None
    annotation: Optional[Any] = None


def patch_params(*params: PatchParamsOption) -> Callable:
    def decorator(func: Callable):
        sig = inspect.signature(func)
        patch_param_map = {p.name: p for p in params}
        new_params = [
            p
            if p.name not in patch_param_map.keys()
            else inspect.Parameter(
                p.name,
                p.kind,
                annotation=patch_param_map[p.name].annotation if patch_param_map[p.name].annotation is not None else p.annotation,
                default=patch_param_map[p.name].default if patch_param_map[p.name].default is not None else p.default,
            )
            for p in sig.parameters.values()
        ]
        new_sig = sig.replace(parameters=new_params)

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.__signature__ = new_sig
        return wrapper

    return decorator


def del_params(map: dict[str, Any]) -> Callable:
    def decorator(func: Callable):
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        new_params = [p for p in params if p.name not in map.keys()]
        new_sig = sig.replace(parameters=new_params)

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs, **map)

        wrapper.__signature__ = new_sig
        return wrapper

    return decorator


def add_config_options(hides: list[ConfigKeys] = [], defaults: dict[ConfigKeys, Any] = {}) -> Callable:
    def decorator(func: Callable):
        @del_params({k: None for k in hides})
        @patch_params(
            PatchParamsOption("show_failed", annotation=bool),
            PatchParamsOption("retry_times", annotation=int),
            PatchParamsOption("timeout", annotation=float),
        )
        def config_func(
            show_failed: Optional[bool] = typer.Option(False, "--show-failed", help="Show failed tasks"),
            retry_times: Optional[int] = typer.Option(3, "--retry-times", "-r", help="Retry times for failed tasks"),
            timeout: Optional[float] = typer.Option(10.0, "--timeout", "-t", help="Timeout for each task"),
        ):
            config.show_failed = show_failed if show_failed is not None else config.show_failed
            config.retry_times = retry_times if retry_times is not None else config.retry_times
            config.timeout = timeout if timeout is not None else config.timeout

        for k, v in defaults.items():
            config_func = patch_param(k, default=v)(config_func)

        return merge_params(config_func)(func)

    return decorator
