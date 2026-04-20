from collections.abc import Callable
from typing import TypeVar

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

T = TypeVar("T")


def with_retry(fn: Callable[..., T]) -> Callable[..., T]:
    return retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=6),
        reraise=True,
    )(fn)
