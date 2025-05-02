from typing import Literal

__all__ = ["show_failed", "retry_times", "timeout", "ConfigKeys"]


show_failed: bool = False
rich_output: bool = True
retry_times: int = 3
timeout: float = 10.0


type ConfigKeys = Literal["show_failed"] | Literal["rich_output"] | Literal["retry_times"] | Literal["timeout"]
