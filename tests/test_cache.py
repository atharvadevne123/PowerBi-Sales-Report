"""Tests for src.cache LRU cache decorator."""

from __future__ import annotations

from src.cache import lru_cached


def test_lru_cached_returns_correct_value() -> None:
    @lru_cached(maxsize=32)
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3


def test_lru_cached_caches_result() -> None:
    call_count = 0

    @lru_cached(maxsize=32)
    def expensive(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    expensive(5)
    expensive(5)
    assert call_count == 1


def test_lru_cached_cache_clear() -> None:
    @lru_cached(maxsize=32)
    def double(x: int) -> int:
        return x * 2

    double(3)
    double.cache_clear()
    info = double.cache_info()
    assert info.currsize == 0


def test_lru_cached_maxsize_respected() -> None:
    @lru_cached(maxsize=2)
    def identity(x: int) -> int:
        return x

    for i in range(10):
        identity(i)
    info = identity.cache_info()
    assert info.currsize <= 2
