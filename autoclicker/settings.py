from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


APP_NAME = "Autoclicker"
SETTINGS_FILENAME = "settings.json"


@dataclass(frozen=True)
class Settings:
    delay_ms: int = 100
    random_min_ms: int = 1
    random_max_ms: int = 20
    hold_ms: int = 50
    start_stop_hotkey: str = "page_up"
    show_menu_hotkey: str = "page_down"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Settings":
        return cls(
            delay_ms=_coerce_int(data.get("delay_ms"), cls.delay_ms),
            random_min_ms=_coerce_int(data.get("random_min_ms"), cls.random_min_ms),
            random_max_ms=_coerce_int(data.get("random_max_ms"), cls.random_max_ms),
            hold_ms=_coerce_int(data.get("hold_ms"), cls.hold_ms),
            start_stop_hotkey=normalize_hotkey_text(
                str(data.get("start_stop_hotkey", cls.start_stop_hotkey))
            ),
            show_menu_hotkey=normalize_hotkey_text(
                str(data.get("show_menu_hotkey", cls.show_menu_hotkey))
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SettingsError(ValueError):
    """Raised when settings cannot be validated."""


def get_settings_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / APP_NAME
    return Path.home() / f".{APP_NAME.lower()}"


def get_settings_path() -> Path:
    return get_settings_dir() / SETTINGS_FILENAME


def load_settings(settings_path: Path | None = None) -> Settings:
    path = settings_path or get_settings_path()
    if path.exists():
        try:
            settings = Settings.from_dict(json.loads(path.read_text(encoding="utf-8")))
            validate_settings(settings)
            return settings
        except (OSError, json.JSONDecodeError, SettingsError, TypeError, ValueError):
            return Settings()

    return Settings()


def save_settings(settings: Settings, settings_path: Path | None = None) -> None:
    validate_settings(settings)
    path = settings_path or get_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(settings.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def validate_settings(settings: Settings) -> None:
    errors: list[str] = []

    if settings.delay_ms < 1:
        errors.append("Delay between clicks must be at least 1 ms.")
    if settings.random_min_ms < 0:
        errors.append("Random delay minimum cannot be negative.")
    if settings.random_max_ms < 0:
        errors.append("Random delay maximum cannot be negative.")
    if settings.random_max_ms < settings.random_min_ms:
        errors.append("Random delay maximum must be greater than or equal to the minimum.")
    if settings.hold_ms < 0:
        errors.append("Click hold time cannot be negative.")
    if not settings.start_stop_hotkey:
        errors.append("Start / Stop hotkey is required.")
    if not settings.show_menu_hotkey:
        errors.append("Show menu hotkey is required.")
    if settings.start_stop_hotkey and settings.start_stop_hotkey == settings.show_menu_hotkey:
        errors.append("Start / Stop and Show menu hotkeys must be different.")

    if errors:
        raise SettingsError("\n".join(errors))


def normalize_hotkey_text(value: str) -> str:
    normalized = value.strip().lower()
    if not normalized:
        return ""

    replacements = {
        "pgup": "page_up",
        "prior": "page_up",
        "pageup": "page_up",
        "page up": "page_up",
        "page_up": "page_up",
        "pgdn": "page_down",
        "next": "page_down",
        "pagedn": "page_down",
        "pagedown": "page_down",
        "page down": "page_down",
        "page_down": "page_down",
        "esc": "esc",
        "escape": "esc",
        "ctrl": "ctrl",
        "control": "ctrl",
        "alt": "alt",
        "shift": "shift",
        "win": "cmd",
        "windows": "cmd",
        "cmd": "cmd",
        "space": "space",
        "return": "enter",
        "enter": "enter",
        "control_l": "ctrl",
        "control_r": "ctrl",
        "shift_l": "shift",
        "shift_r": "shift",
        "alt_l": "alt",
        "alt_r": "alt",
        "super_l": "cmd",
        "super_r": "cmd",
        "win_l": "cmd",
        "win_r": "cmd",
        "plus": "+",
        "x1": "mouse_x1",
        "button.x1": "mouse_x1",
        "mouse_x1": "mouse_x1",
        "mouse x1": "mouse_x1",
        "mouse4": "mouse_x1",
        "mouse_4": "mouse_x1",
        "mouse back": "mouse_x1",
        "browser_back": "mouse_x1",
        "x2": "mouse_x2",
        "button.x2": "mouse_x2",
        "mouse_x2": "mouse_x2",
        "mouse x2": "mouse_x2",
        "mouse5": "mouse_x2",
        "mouse_5": "mouse_x2",
        "mouse forward": "mouse_x2",
        "browser_forward": "mouse_x2",
    }

    parts = [
        replacements.get(part.strip(), part.strip())
        for part in normalized.replace("-", "+").split("+")
        if part.strip()
    ]
    return "+".join(parts)


def format_hotkey_label(value: str) -> str:
    labels = {
        "page_up": "PgUp",
        "page_down": "PgDn",
        "ctrl": "Ctrl",
        "alt": "Alt",
        "shift": "Shift",
        "cmd": "Win",
        "esc": "Esc",
        "space": "Space",
        "enter": "Enter",
        "mouse_x1": "Mouse Back",
        "mouse_x2": "Mouse Forward",
    }
    formatted_parts = []
    for part in value.split("+"):
        if part in labels:
            formatted_parts.append(labels[part])
        elif _is_function_key(part):
            formatted_parts.append(part.upper())
        elif len(part) == 1:
            formatted_parts.append(part.upper())
        else:
            formatted_parts.append(part)
    return " + ".join(formatted_parts)


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _is_function_key(value: str) -> bool:
    if not value.startswith("f"):
        return False
    try:
        number = int(value[1:])
    except ValueError:
        return False
    return 1 <= number <= 24
