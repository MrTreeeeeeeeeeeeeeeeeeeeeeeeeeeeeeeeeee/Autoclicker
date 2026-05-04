from __future__ import annotations

from autoclicker.clicker import ClickerService
from autoclicker.hotkeys import HotkeyError, HotkeyManager
from autoclicker.settings import Settings, load_settings, save_settings
from autoclicker.ui import AutoclickerUI


class AutoclickerApp:
    def __init__(self) -> None:
        self.settings = load_settings()
        self.clicker = ClickerService()
        self.hotkeys = HotkeyManager()
        self.ui = AutoclickerUI(
            settings=self.settings,
            on_toggle=self.toggle_clicking,
            on_save=self.save_ui_settings,
            on_close=self.shutdown,
        )

    def run(self) -> None:
        try:
            self.hotkeys.start(
                self.settings,
                on_toggle=self.toggle_from_hotkey,
                on_show_menu=self.show_menu,
            )
        except Exception as exc:
            self.ui.set_hotkey_error(str(exc))
        self.ui.mainloop()

    def toggle_clicking(self, settings: Settings) -> bool:
        self.settings = settings
        running = self.clicker.toggle(settings)
        self.ui.set_running(running)
        return running

    def toggle_from_hotkey(self) -> None:
        if self.ui.is_capturing_hotkey():
            return
        self.ui.after(0, self._toggle_from_hotkey_on_ui_thread)

    def show_menu(self) -> None:
        if self.ui.is_capturing_hotkey():
            return
        self.ui.restore_window()

    def save_ui_settings(self, settings: Settings) -> None:
        try:
            self.hotkeys.restart(settings)
        except HotkeyError as exc:
            self.ui.set_hotkey_error(str(exc))
            raise
        save_settings(settings)
        self.settings = settings
        self.clicker.update_settings(settings)

    def shutdown(self) -> None:
        self.hotkeys.stop()
        self.clicker.shutdown()

    def _toggle_from_hotkey_on_ui_thread(self) -> None:
        running = self.clicker.toggle(self.settings)
        self.ui.set_running(running)


def main() -> None:
    app = AutoclickerApp()
    app.run()
