from __future__ import annotations

import random
import threading
from time import monotonic
from typing import Any

from autoclicker.settings import Settings


class ClickerService:
    def __init__(self, mouse_controller: Any | None = None, button: Any | None = None) -> None:
        self._mouse = mouse_controller
        self._button = button
        self._thread: threading.Thread | None = None
        self._settings: Settings | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def start(self, settings: Settings) -> None:
        with self._lock:
            if self._thread and self._thread.is_alive():
                self._settings = settings
                return
            self._ensure_mouse()
            self._settings = settings
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run,
                name="AutoclickerThread",
                daemon=True,
            )
            self._thread.start()

    def stop(self) -> None:
        thread: threading.Thread | None
        with self._lock:
            self._stop_event.set()
            thread = self._thread

        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=1.0)

        with self._lock:
            if self._thread is thread:
                self._thread = None

    def toggle(self, settings: Settings) -> bool:
        if self.is_running():
            self.stop()
            return False
        self.start(settings)
        return True

    def is_running(self) -> bool:
        with self._lock:
            return bool(self._thread and self._thread.is_alive() and not self._stop_event.is_set())

    def shutdown(self) -> None:
        self.stop()

    def update_settings(self, settings: Settings) -> None:
        with self._lock:
            self._settings = settings

    def _run(self) -> None:
        while not self._stop_event.is_set():
            settings = self._get_settings()
            self._click(settings.hold_ms / 1000)
            delay_ms = settings.delay_ms + random.randint(
                settings.random_min_ms,
                settings.random_max_ms,
            )
            self._interruptible_sleep(delay_ms / 1000)

    def _click(self, hold_seconds: float) -> None:
        self._mouse.press(self._button)
        try:
            self._interruptible_sleep(hold_seconds)
        finally:
            self._mouse.release(self._button)

    def _interruptible_sleep(self, seconds: float) -> None:
        if seconds <= 0:
            return

        end = monotonic() + seconds
        while not self._stop_event.is_set():
            remaining = end - monotonic()
            if remaining <= 0:
                return
            self._stop_event.wait(min(remaining, 0.05))

    def _ensure_mouse(self) -> None:
        if self._mouse is not None and self._button is not None:
            return

        from pynput.mouse import Button, Controller

        self._mouse = Controller()
        self._button = Button.left

    def _get_settings(self) -> Settings:
        with self._lock:
            if self._settings is None:
                return Settings()
            return self._settings
