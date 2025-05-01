from typing import Literal

__all__ = ["show_failed", "retry_times", "timeout", "ConfigKeys"]


show_failed: bool = False
retry_times: int = 3
timeout: float = 10.0


def __str__() -> str:
    return f"Config(show_failed={show_failed}, retry_times={retry_times}, timeout={timeout})"


type ConfigKeys = Literal["show_failed"] | Literal["retry_times"] | Literal["timeout"]
