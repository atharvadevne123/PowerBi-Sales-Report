"""Simple in-process LRU cache utilities for expensive computations."""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def lru_cached(maxsize: int = 128) -> Callable[[F], F]:
    """Decorator that applies functools.lru_cache with logging on cache miss.

    Args:
        maxsize: Maximum cache size.

    Returns:
        Decorator function.
    """

    def decorator(fn: F) -> F:
        cached_fn = functools.lru_cache(maxsize=maxsize)(fn)

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = cached_fn(*args, **kwargs)
            info = cached_fn.cache_info()
            if info.misses and info.hits == 0:
                logger.debug("Cache miss for %s; size=%d", fn.__name__, info.currsize)
            return result

        wrapper.cache_info = cached_fn.cache_info  # type: ignore[attr-defined]
        wrapper.cache_clear = cached_fn.cache_clear  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator
