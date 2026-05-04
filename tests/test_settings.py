from __future__ import annotations

import json
from pathlib import Path

from autoclicker.settings import Settings, load_settings, save_settings


def test_defaults_are_used_without_json_file(tmp_path: Path) -> None:
    settings = load_settings(settings_path=tmp_path / "missing" / "settings.json")

    assert settings == Settings()


def test_corrupt_json_values_fall_back_to_defaults(tmp_path: Path) -> None:
    settings_path = tmp_path / "settings.json"
    settings_path.write_text("{bad json", encoding="utf-8")

    settings = load_settings(settings_path=settings_path)
    assert settings == Settings()


def test_json_settings_load_correctly(tmp_path: Path) -> None:
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(
        json.dumps(
            {
                "delay_ms": 175,
                "random_min_ms": 3,
                "random_max_ms": 18,
                "hold_ms": 22,
                "start_stop_hotkey": "F6",
                "show_menu_hotkey": "ctrl+F7",
            }
        ),
        encoding="utf-8",
    )

    assert load_settings(settings_path=settings_path) == Settings(
        delay_ms=175,
        random_min_ms=3,
        random_max_ms=18,
        hold_ms=22,
        start_stop_hotkey="f6",
        show_menu_hotkey="ctrl+f7",
    )


def test_json_settings_save_correctly(tmp_path: Path) -> None:
    settings_path = tmp_path / "settings.json"
    settings = Settings(delay_ms=125, random_min_ms=0, random_max_ms=10, hold_ms=12)

    save_settings(settings, settings_path)

    assert json.loads(settings_path.read_text(encoding="utf-8")) == settings.to_dict()
