from datetime import timedelta
from typing import Any, Callable, Optional

import typer

from .. import config
from ..config import ConfigKeys
from .base import timedelta_parser
from .function_patcher import PatchParamsOption, del_params, merge_params, patch_params


def add_config_options(hides: list[ConfigKeys] = [], defaults: dict[ConfigKeys, Any] = {}) -> Callable:
    def decorator(func: Callable):
        @del_params({k: None for k in hides})
        @patch_params(
            PatchParamsOption("show_failed", annotation=bool),
            PatchParamsOption("rich_output", annotation=bool),
            PatchParamsOption("retry_times", annotation=int),
            PatchParamsOption("timeout", annotation=timedelta),
        )
        def config_func(
            show_failed: Optional[bool] = typer.Option(False, "--show-failed", help="Show failed tasks"),
            rich_output: Optional[bool] = typer.Option(True, "--rich-output/--plain-output", help="Use rich output"),
            retry_times: Optional[int] = typer.Option(3, "--retry-times", "-r", help="Retry times for failed tasks"),
            timeout: Optional[timedelta] = typer.Option("10s", "--timeout", "-t", help="Timeout for each task", click_type=timedelta_parser),
        ):
            config.show_failed = show_failed if show_failed is not None else config.show_failed
            config.rich_output = rich_output if rich_output is not None else config.rich_output
            config.retry_times = retry_times if retry_times is not None else config.retry_times
            config.timeout = timeout.total_seconds() if timeout is not None else config.timeout

        return merge_params(patch_params(*[PatchParamsOption(k, default=v) for k, v in defaults.items()])(config_func))(func)

    return decorator
