from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from autoclicker.hotkeys import display_hotkey, mouse_button_to_hotkey, normalize_hotkey
from autoclicker.settings import Settings, SettingsError, validate_settings


WINDOW_WIDTH = 480
COMPACT_HEIGHT = 345
ERROR_HEIGHT = 385


class AutoclickerUI(ctk.CTk):
    def __init__(
        self,
        settings: Settings,
        on_save: Callable[[Settings], None],
        on_close: Callable[[], None],
    ) -> None:
        super().__init__()
        self._on_save = on_save
        self._on_close = on_close
        self._running = False
        self._capturing_hotkey: str | None = None
        self._mouse_capture_listener: Any | None = None

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Autoclicker")
        self._set_window_height(COMPACT_HEIGHT)
        self.protocol("WM_DELETE_WINDOW", self._handle_close)

        self.delay_var = tk.StringVar(value=str(settings.delay_ms))
        self.random_min_var = tk.StringVar(value=str(settings.random_min_ms))
        self.random_max_var = tk.StringVar(value=str(settings.random_max_ms))
        self.hold_var = tk.StringVar(value=str(settings.hold_ms))
        self.start_hotkey_var = tk.StringVar(value=display_hotkey(settings.start_stop_hotkey))
        self.menu_hotkey_var = tk.StringVar(value=display_hotkey(settings.show_menu_hotkey))

        self._build()
        self.bind("<KeyPress>", self._handle_keypress)
        self.set_status("Stopped", "neutral")

    def restore_window(self) -> None:
        self.after(0, self._restore_window)

    def set_running(self, running: bool) -> None:
        self._running = running
        self.after(0, self._refresh_running_state)

    def set_hotkey_error(self, message: str) -> None:
        self.after(0, lambda: self._show_error(f"Hotkey error: {message}"))

    def is_capturing_hotkey(self) -> bool:
        return self._capturing_hotkey is not None

    def set_status(self, text: str, kind: str = "neutral") -> None:
        colors = {
            "neutral": ("#94a3b8", "#334155"),
            "running": ("#22c55e", "#14532d"),
            "error": ("#f87171", "#7f1d1d"),
            "saved": ("#38bdf8", "#164e63"),
        }
        text_color, bg_color = colors.get(kind, colors["neutral"])
        self.status_label.configure(text=text, text_color=text_color)
        self.status_pill.configure(fg_color=bg_color)

    def _set_window_height(self, height: int) -> None:
        self.resizable(True, True)
        self.geometry(f"{WINDOW_WIDTH}x{height}")
        self.minsize(WINDOW_WIDTH, height)
        self.maxsize(WINDOW_WIDTH, height)
        self.resizable(False, False)

    def read_settings(self) -> Settings:
        settings = Settings(
            delay_ms=self._read_int(self.delay_var.get(), "Delay between clicks"),
            random_min_ms=self._read_int(self.random_min_var.get(), "Random delay minimum"),
            random_max_ms=self._read_int(self.random_max_var.get(), "Random delay maximum"),
            hold_ms=self._read_int(self.hold_var.get(), "Click hold time"),
            start_stop_hotkey=normalize_hotkey(self.start_hotkey_var.get()),
            show_menu_hotkey=normalize_hotkey(self.menu_hotkey_var.get()),
        )
        validate_settings(settings)
        return settings

    def _build(self) -> None:
        title_font = ctk.CTkFont(size=26, weight="bold")
        status_font = ctk.CTkFont(size=14, weight="bold")
        label_font = ctk.CTkFont(size=15)
        entry_font = ctk.CTkFont(size=16)
        hotkey_font = ctk.CTkFont(size=15)
        save_font = ctk.CTkFont(size=16, weight="bold")
        arrow_font = ctk.CTkFont(size=13, weight="bold")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=22, pady=(8, 4))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Autoclicker",
            font=title_font,
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="w")

        self.status_pill = ctk.CTkFrame(header, corner_radius=8, fg_color="#334155")
        self.status_pill.grid(row=0, column=1, sticky="e")
        self.status_label = ctk.CTkLabel(
            self.status_pill,
            text="Stopped",
            font=status_font,
            padx=12,
            pady=4,
        )
        self.status_label.pack()

        body = ctk.CTkFrame(self, corner_radius=8)
        body.grid(row=1, column=0, sticky="ew", padx=22, pady=4)
        body.grid_columnconfigure(1, weight=1)

        top_spacer = ctk.CTkFrame(body, fg_color="transparent", height=10)
        top_spacer.grid(row=0, column=0, columnspan=2, sticky="ew")
        top_spacer.grid_propagate(False)

        self._add_number_entry(
            body,
            1,
            "Delay between clicks (ms)",
            self.delay_var,
            label_font,
            entry_font,
            arrow_font,
            minimum=1,
        )
        self._add_number_entry(
            body,
            2,
            "Random delay min (ms)",
            self.random_min_var,
            label_font,
            entry_font,
            arrow_font,
        )
        self._add_number_entry(
            body,
            3,
            "Random delay max (ms)",
            self.random_max_var,
            label_font,
            entry_font,
            arrow_font,
        )
        self._add_number_entry(
            body,
            4,
            "Click hold time (ms)",
            self.hold_var,
            label_font,
            entry_font,
            arrow_font,
        )
        self._add_hotkey(
            body,
            5,
            "Start / Stop hotkey",
            self.start_hotkey_var,
            "start",
            label_font,
            hotkey_font,
        )
        self._add_hotkey(
            body,
            6,
            "Show menu hotkey",
            self.menu_hotkey_var,
            "menu",
            label_font,
            hotkey_font,
        )

        self.error_label = ctk.CTkLabel(
            body,
            text="",
            text_color="#f87171",
            font=ctk.CTkFont(size=13),
            wraplength=390,
            justify="left",
            anchor="w",
        )
        bottom_spacer = ctk.CTkFrame(body, fg_color="transparent", height=10)
        bottom_spacer.grid(row=7, column=0, columnspan=2, sticky="ew")
        bottom_spacer.grid_propagate(False)

        self.error_label.grid(row=8, column=0, columnspan=2, sticky="ew", padx=12, pady=(4, 0))
        self.error_label.grid_remove()

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=22, pady=(8, 8))
        actions.grid_columnconfigure(0, weight=1)

        self.save_button = ctk.CTkButton(
            actions,
            text="Save",
            height=36,
            font=save_font,
            fg_color="#475569",
            hover_color="#64748b",
            command=self._handle_save,
        )
        self.save_button.grid(row=0, column=0, sticky="ew")

    def _add_number_entry(
        self,
        parent: ctk.CTkFrame,
        row: int,
        label: str,
        variable: tk.StringVar,
        label_font: ctk.CTkFont,
        entry_font: ctk.CTkFont,
        arrow_font: ctk.CTkFont,
        minimum: int = 0,
    ) -> None:
        ctk.CTkLabel(parent, text=label, font=label_font, anchor="w").grid(
            row=row,
            column=0,
            sticky="w",
            padx=12,
            pady=(6 if row == 0 else 4, 0),
        )

        control = ctk.CTkFrame(parent, fg_color="transparent")
        control.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=12,
            pady=(6 if row == 0 else 4, 0),
        )
        control.grid_columnconfigure(0, weight=1)

        entry = ctk.CTkEntry(
            control,
            textvariable=variable,
            justify="right",
            font=entry_font,
            height=30,
        )
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        step_up = ctk.CTkButton(
            control,
            text="▲",
            width=30,
            height=30,
            corner_radius=6,
            font=arrow_font,
            fg_color="#475569",
            hover_color="#64748b",
            command=lambda: self._adjust_number(variable, label, 5, minimum),
        )
        step_up.grid(row=0, column=1, sticky="ew", padx=(0, 4))

        step_down = ctk.CTkButton(
            control,
            text="▼",
            width=30,
            height=30,
            corner_radius=6,
            font=arrow_font,
            fg_color="#475569",
            hover_color="#64748b",
            command=lambda: self._adjust_number(variable, label, -5, minimum),
        )
        step_down.grid(row=0, column=2, sticky="ew")

    def _add_hotkey(
        self,
        parent: ctk.CTkFrame,
        row: int,
        label: str,
        variable: tk.StringVar,
        target: str,
        label_font: ctk.CTkFont,
        button_font: ctk.CTkFont,
    ) -> None:
        ctk.CTkLabel(parent, text=label, font=label_font, anchor="w").grid(
            row=row,
            column=0,
            sticky="w",
            padx=12,
            pady=(4, 0),
        )
        button = ctk.CTkButton(
            parent,
            textvariable=variable,
            height=30,
            font=button_font,
            fg_color="#1f2937",
            hover_color="#334155",
            command=lambda: self._begin_hotkey_capture(target),
        )
        button.grid(row=row, column=1, sticky="ew", padx=12, pady=(4, 0))

    def _handle_save(self) -> None:
        try:
            settings = self.read_settings()
            self._on_save(settings)
            self._clear_error()
            self.set_status("Saved", "saved")
            self.after(1500, self._refresh_running_state)
        except (SettingsError, ValueError, RuntimeError, OSError) as exc:
            self._show_error(str(exc))

    def _handle_close(self) -> None:
        self._stop_mouse_capture()
        self._on_close()
        self.destroy()

    def _begin_hotkey_capture(self, target: str) -> None:
        self._stop_mouse_capture()
        self._capturing_hotkey = target
        if target == "start":
            self.start_hotkey_var.set("Press a key or side button...")
        else:
            self.menu_hotkey_var.set("Press a key or side button...")
        self.focus_set()
        self._start_mouse_capture()

    def _handle_keypress(self, event: tk.Event) -> None:
        if not self._capturing_hotkey:
            return

        key_name = self._event_to_hotkey(event)
        if not key_name:
            return

        self._set_captured_hotkey(key_name)

    def _handle_mouse_capture(self, button: Any, pressed: bool) -> bool | None:
        if not pressed or not self._capturing_hotkey:
            return None

        hotkey = mouse_button_to_hotkey(button)
        if not hotkey:
            return None

        self.after(0, lambda: self._set_captured_hotkey(hotkey))
        return False

    def _set_captured_hotkey(self, hotkey: str) -> None:
        if self._capturing_hotkey == "start":
            self.start_hotkey_var.set(display_hotkey(hotkey))
        else:
            self.menu_hotkey_var.set(display_hotkey(hotkey))
        self._capturing_hotkey = None
        self._stop_mouse_capture()

    def _event_to_hotkey(self, event: tk.Event) -> str:
        keysym = str(event.keysym)
        modifiers: list[str] = []
        state = int(getattr(event, "state", 0))
        if state & 0x0004:
            modifiers.append("ctrl")
        if state & 0x0008:
            modifiers.append("alt")
        if state & 0x0001:
            modifiers.append("shift")

        key_name = normalize_hotkey(keysym)
        if key_name in {"ctrl", "alt", "shift", "cmd"}:
            return ""
        return "+".join([*modifiers, key_name]) if modifiers else key_name

    def _start_mouse_capture(self) -> None:
        try:
            from pynput import mouse

            self._mouse_capture_listener = mouse.Listener(
                on_click=lambda x, y, button, pressed: self._handle_mouse_capture(
                    button,
                    pressed,
                )
            )
            self._mouse_capture_listener.start()
        except Exception as exc:
            self._mouse_capture_listener = None
            self._show_error(f"Could not listen for mouse side buttons: {exc}")

    def _stop_mouse_capture(self) -> None:
        if self._mouse_capture_listener is not None:
            self._mouse_capture_listener.stop()
            self._mouse_capture_listener = None

    def _restore_window(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.after(250, lambda: self.attributes("-topmost", False))

    def _refresh_running_state(self) -> None:
        if self._running:
            self.set_status("Running", "running")
        else:
            self.set_status("Stopped", "neutral")

    def _show_error(self, message: str) -> None:
        self._set_window_height(ERROR_HEIGHT)
        self.error_label.configure(text=message)
        self.error_label.grid()
        self.set_status("Hotkey error" if "hotkey" in message.lower() else "Error", "error")

    def _clear_error(self) -> None:
        self.error_label.configure(text="")
        self.error_label.grid_remove()
        self._set_window_height(COMPACT_HEIGHT)

    def _adjust_number(
        self,
        variable: tk.StringVar,
        label: str,
        delta: int,
        minimum: int,
    ) -> None:
        try:
            current = self._read_int(variable.get(), label)
        except ValueError as exc:
            self._show_error(str(exc))
            return

        variable.set(str(max(minimum, current + delta)))
        self._clear_error()

    @staticmethod
    def _read_int(value: str, label: str) -> int:
        try:
            return int(value.strip())
        except ValueError as exc:
            raise ValueError(f"{label} must be a whole number.") from exc
