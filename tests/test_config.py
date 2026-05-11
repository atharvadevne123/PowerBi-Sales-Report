"""Tests for app.config settings."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


def test_settings_defaults() -> None:
    from app.config import Settings

    s = Settings()
    assert s.port == 8000
    assert s.log_level == "INFO"
    assert s.rate_limit == 120


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    from importlib import reload

    import app.config as cfg_module

    reload(cfg_module)
    s = cfg_module.Settings()
    assert s.port == 9000
    assert s.log_level == "DEBUG"


def test_settings_data_dir_default() -> None:
    from app.config import Settings

    s = Settings()
    assert isinstance(s.data_dir, Path)


def test_settings_rate_limit_positive() -> None:
    from app.config import Settings

    s = Settings(rate_limit=60)
    assert s.rate_limit == 60


def test_settings_invalid_port() -> None:
    from pydantic import ValidationError

    from app.config import Settings

    with pytest.raises(ValidationError):
        Settings(port=0)
