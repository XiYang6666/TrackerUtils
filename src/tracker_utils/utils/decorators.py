import asyncio
from typing import Any, Callable, Coroutine

from rich.progress import Progress, TaskID

from .. import config
from .output import fail


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


def with_semaphone(semaphone: asyncio.Semaphore):
    def decorator[T](func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        async def wrapper(*args, **kwargs):
            async with semaphone:
                return await func(*args, **kwargs)

        return wrapper

    return decorator
