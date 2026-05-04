from __future__ import annotations

import pytest

from pynput.mouse import Button

from autoclicker.hotkeys import is_mouse_hotkey, mouse_button_to_hotkey, normalize_hotkey
from autoclicker.settings import Settings, SettingsError, validate_settings


def test_validation_rejects_negative_delay_values() -> None:
    with pytest.raises(SettingsError):
        validate_settings(Settings(delay_ms=-1))


def test_validation_rejects_random_max_less_than_min() -> None:
    with pytest.raises(SettingsError):
        validate_settings(Settings(random_min_ms=20, random_max_ms=10))


def test_validation_rejects_duplicate_hotkeys() -> None:
    with pytest.raises(SettingsError):
        validate_settings(Settings(start_stop_hotkey="page_up", show_menu_hotkey="page_up"))


def test_hotkey_normalization_maps_page_keys() -> None:
    assert normalize_hotkey("PgUp") == "page_up"
    assert normalize_hotkey("PgDn") == "page_down"
    assert normalize_hotkey("Prior") == "page_up"
    assert normalize_hotkey("Next") == "page_down"


def test_hotkey_normalization_maps_mouse_side_buttons() -> None:
    assert normalize_hotkey("Mouse Back") == "mouse_x1"
    assert normalize_hotkey("Mouse Forward") == "mouse_x2"
    assert is_mouse_hotkey("mouse_x1")
    assert is_mouse_hotkey("mouse_x2")
    assert mouse_button_to_hotkey(Button.x1) == "mouse_x1"
    assert mouse_button_to_hotkey(Button.x2) == "mouse_x2"
