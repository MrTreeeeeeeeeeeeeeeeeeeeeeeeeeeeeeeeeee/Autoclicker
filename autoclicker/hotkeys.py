from __future__ import annotations

from collections.abc import Callable
from typing import Any

from autoclicker.settings import Settings, format_hotkey_label, normalize_hotkey_text


SPECIAL_KEY_ALIASES = {
    "page_up": "page_up",
    "page_down": "page_down",
    "esc": "esc",
    "space": "space",
    "enter": "enter",
    "tab": "tab",
    "backspace": "backspace",
    "delete": "delete",
    "insert": "insert",
    "home": "home",
    "end": "end",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
}

MODIFIER_ALIASES = {
    "ctrl": "ctrl",
    "alt": "alt",
    "shift": "shift",
    "cmd": "cmd",
}

MOUSE_BUTTON_ALIASES = {
    "mouse_x1": "x1",
    "mouse_x2": "x2",
}


class HotkeyError(RuntimeError):
    """Raised when global hotkeys cannot be registered."""


class HotkeyManager:
    def __init__(self) -> None:
        self._listeners: list[Any] = []
        self._settings: Settings | None = None
        self._on_toggle: Callable[[], None] | None = None
        self._on_show_menu: Callable[[], None] | None = None

    def start(
        self,
        settings: Settings,
        on_toggle: Callable[[], None],
        on_show_menu: Callable[[], None],
    ) -> None:
        self._settings = settings
        self._on_toggle = on_toggle
        self._on_show_menu = on_show_menu
        self._replace_listener(settings)

    def restart(self, settings: Settings) -> None:
        if self._on_toggle is None or self._on_show_menu is None:
            raise HotkeyError("Hotkey manager has not been started.")

        previous_listeners = self._listeners
        previous_settings = self._settings

        try:
            self._settings = settings
            self._replace_listener(settings, stop_existing=False)
            self._stop_listeners(previous_listeners)
        except Exception as exc:
            self._settings = previous_settings
            new_listeners = self._listeners
            self._listeners = previous_listeners
            if new_listeners is not previous_listeners:
                self._stop_listeners(new_listeners)
            raise HotkeyError(f"Could not register hotkeys: {exc}") from exc

    def stop(self) -> None:
        self._stop_listeners(self._listeners)
        self._listeners = []

    def _replace_listener(self, settings: Settings, stop_existing: bool = True) -> None:
        listeners = self._start_listeners(settings)
        old_listeners = self._listeners
        self._listeners = listeners

        if stop_existing:
            self._stop_listeners(old_listeners)

    def _start_listeners(self, settings: Settings) -> list[Any]:
        if self._on_toggle is None or self._on_show_menu is None:
            raise HotkeyError("Hotkey callbacks have not been configured.")

        from pynput import keyboard, mouse

        configured_hotkeys = {
            normalize_hotkey(settings.start_stop_hotkey): self._on_toggle,
            normalize_hotkey(settings.show_menu_hotkey): self._on_show_menu,
        }
        keyboard_hotkeys: dict[str, Callable[[], None]] = {}
        mouse_hotkeys: dict[str, Callable[[], None]] = {}

        for hotkey, callback in configured_hotkeys.items():
            if is_mouse_hotkey(hotkey):
                mouse_hotkeys[hotkey] = callback
            else:
                keyboard_hotkeys[to_pynput_hotkey(hotkey)] = callback

        listeners: list[Any] = []
        try:
            if keyboard_hotkeys:
                keyboard_listener = keyboard.GlobalHotKeys(keyboard_hotkeys)
                keyboard_listener.start()
                listeners.append(keyboard_listener)
            if mouse_hotkeys:
                mouse_listener = mouse.Listener(
                    on_click=lambda x, y, button, pressed: self._handle_mouse_click(
                        button,
                        pressed,
                        mouse_hotkeys,
                    )
                )
                mouse_listener.start()
                listeners.append(mouse_listener)
        except Exception:
            self._stop_listeners(listeners)
            raise

        return listeners

    def _handle_mouse_click(
        self,
        button: Any,
        pressed: bool,
        mouse_hotkeys: dict[str, Callable[[], None]],
    ) -> None:
        if not pressed:
            return

        hotkey = mouse_button_to_hotkey(button)
        callback = mouse_hotkeys.get(hotkey)
        if callback is not None:
            callback()

    @staticmethod
    def _stop_listeners(listeners: list[Any]) -> None:
        for listener in listeners:
            listener.stop()


def normalize_hotkey(value: str) -> str:
    return normalize_hotkey_text(value)


def to_pynput_hotkey(value: str) -> str:
    normalized = normalize_hotkey_text(value)
    if is_mouse_hotkey(normalized):
        raise HotkeyError(f"{display_hotkey(normalized)} is a mouse hotkey, not a keyboard hotkey.")

    parts = normalized.split("+")
    if not parts or any(not part for part in parts):
        raise HotkeyError("Hotkey cannot be empty.")

    pynput_parts: list[str] = []
    for part in parts:
        if part in MODIFIER_ALIASES:
            pynput_parts.append(f"<{MODIFIER_ALIASES[part]}>")
        elif part in SPECIAL_KEY_ALIASES:
            pynput_parts.append(f"<{SPECIAL_KEY_ALIASES[part]}>")
        elif _is_function_key(part):
            pynput_parts.append(f"<{part}>")
        elif len(part) == 1:
            pynput_parts.append(part)
        else:
            raise HotkeyError(f"Unsupported hotkey key: {format_hotkey_label(part)}")

    return "+".join(pynput_parts)


def display_hotkey(value: str) -> str:
    return format_hotkey_label(normalize_hotkey_text(value))


def is_mouse_hotkey(value: str) -> bool:
    return normalize_hotkey_text(value) in MOUSE_BUTTON_ALIASES


def mouse_button_to_hotkey(button: Any) -> str:
    button_name = getattr(button, "name", "")
    if button_name:
        normalized = normalize_hotkey_text(f"button.{button_name}")
        if is_mouse_hotkey(normalized):
            return normalized

    normalized = normalize_hotkey_text(str(button))
    if is_mouse_hotkey(normalized):
        return normalized

    return ""


def _is_function_key(value: str) -> bool:
    if not value.startswith("f"):
        return False
    try:
        number = int(value[1:])
    except ValueError:
        return False
    return 1 <= number <= 24
