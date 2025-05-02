import inspect
from dataclasses import dataclass
from typing import Any, Callable, Optional


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
