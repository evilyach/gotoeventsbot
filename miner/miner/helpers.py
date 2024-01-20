import asyncio
from functools import wraps
from typing import Any, Callable, Coroutine


def async_typer[T](func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def flatten_2d_container[T](matrix: list[list[T]]) -> list[T]:
    return [item for row in matrix for item in row]
