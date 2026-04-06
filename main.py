from __future__ import annotations

import json
from pathlib import Path
import sys
from tkinter import filedialog, messagebox

import customtkinter as ctk

from aura_clicker.action_history import ActionHistory
from aura_clicker.app_state import AppState, SettingsStore
from aura_clicker.automation_workers import ClickWorker, KeyPresserWorker, SequenceWorker
from aura_clicker.constants import APP_NAME, APP_VERSION, APP_WINDOW_TITLE
from aura_clicker.hotkey_manager import GlobalHotkeyManager
from aura_clicker.profile_manager import ProfileManager
from aura_clicker.structured_error_logger import get_structured_logger, init_structured_logger
from aura_clicker.theme import apply_aura_theme
from aura_clicker.translations import format_text
from aura_clicker.windows.advanced_window import AdvancedWindow
from aura_clicker.windows.hotkey_settings_window import HotkeySettingsWindow
from aura_clicker.windows.key_presser_window import KeyPresserWindow
from aura_clicker.windows.main_window import MainWindow


class AuraClickerApplication:
    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parent
        init_structured_logger(self.base_dir)
        self.settings_store = SettingsStore(self.base_dir)
        self.profile_manager = ProfileManager(self.base_dir)
        self.history = ActionHistory(self.base_dir)
        self.state: AppState = self.settings_store.load()

        apply_aura_theme(self.base_dir)
        self.root = ctk.CTk()
        self.root.title(APP_WINDOW_TITLE)
        self.root.geometry("920x780")
        self.root.minsize(860, 740)

        self.icon_path = self._resolve_asset_path("logo_aura_clicker.ico")
        self._apply_window_icon()

        self.click_worker = ClickWorker()
        self.sequence_worker = SequenceWorker()
        self.key_worker = KeyPresserWorker()
        self.hotkey_manager = GlobalHotkeyManager()

        self.main_window: MainWindow | None = None
        self.advanced_window: AdvancedWindow | None = None
        self.key_window: KeyPresserWindow | None = None

        self.history.subscribe(self._broadcast_history)
        self._build_main_window()
        self._register_hotkeys()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.history.push(self._tf("history_app_init", app=APP_NAME, version=APP_VERSION))
        logger = get_structured_logger()
        if logger:
            logger.log_message("main.py", "Application initialisée", context={"version": APP_VERSION})

    def _tf(self, key: str, **kwargs) -> str:
        return format_text(self.state.current_language, key, **kwargs)

    def _resolve_asset_path(self, filename: str) -> Path:
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / "aura_clicker" / "assets" / filename
        return self.base_dir / "aura_clicker" / "assets" / filename

    def _apply_window_icon(self) -> None:
        try:
            if self.icon_path.exists():
                self.root.iconbitmap(str(self.icon_path))
                self.root.icon_path = str(self.icon_path)
        except Exception:
            pass

    def _build_main_window(self) -> None:
        self.main_window = MainWindow(
            self.root,
            state=self.state,
            on_start=self.start_main_click,
            on_stop=self.stop_main_click,
            on_toggle=self.toggle_main_click,
            on_save=self.save_main_click_settings,
            on_export_profile=self.export_profile,
            on_import_profile=self.import_profile,
            on_open_hotkeys=self.open_hotkey_settings,
            on_open_key_presser=self.open_key_presser_window,
            on_open_advanced=self.open_advanced_window,
            on_language_change=self.change_language,
        )
        self.main_window.set_history(self.history.get_events())
        self.main_window.update_ui_language()

    def _register_hotkeys(self) -> None:
        callbacks = {
            "start": self._hotkey_start_click,
            "stop": self.stop_main_click,
            "toggle": self._hotkey_toggle_click,
            "advanced_start": self._hotkey_start_advanced,
            "advanced_stop": self.stop_advanced,
            "key_start": self._hotkey_start_key_presser,
            "key_stop": self.stop_key_presser,
        }
        self.hotkey_manager.register(self.state.hotkeys, callbacks)

    def start_main_click(self, config: dict, status_callback) -> None:
        self._save_main_to_state(config)
        self.click_worker.start(config, status_callback, self.history.push)

    def stop_main_click(self) -> None:
        self.click_worker.stop()
        self.history.push(self._tf("history_stop_main_requested"))

    def toggle_main_click(self, config: dict, status_callback) -> None:
        if self.click_worker.running:
            self.stop_main_click()
            status_callback(self._tf("status_main_stopped"))
            return
        self.start_main_click(config, status_callback)

    def save_main_click_settings(self, config: dict, always_on_top: bool) -> None:
        self._save_main_to_state(config)
        self.state.main_click.always_on_top = always_on_top
        self._persist_state()
        self.history.push(self._tf("history_main_settings_saved"))

    def open_hotkey_settings(self) -> None:
        if self._window_alive(self.root, HotkeySettingsWindow):
            return

        def on_save(payload: dict[str, str]) -> None:
            self.state.hotkeys["start"] = payload["start"]
            self.state.hotkeys["stop"] = payload["stop"]
            self.state.hotkeys["toggle"] = payload["toggle"]
            self._persist_state()
            self._register_hotkeys()
            self.history.push(self._tf("history_hotkeys_updated"))
            if self.main_window:
                self.main_window._set_status(self._tf("status_hotkeys_saved"))

        hotkey_window = HotkeySettingsWindow(self.root, self.state.hotkeys, on_save)
        hotkey_window.transient(self.root)
        hotkey_window.grab_set()

    def open_advanced_window(self) -> None:
        if self.advanced_window is not None and self.advanced_window.winfo_exists():
            self._bring_window_to_front(self.advanced_window)
            return

        self.advanced_window = AdvancedWindow(
            self.root,
            state=self.state,
            on_start=self.start_advanced,
            on_stop=self.stop_advanced,
            on_save_state=self._persist_state,
        )
        self.advanced_window.set_history(self.history.get_events())
        self.advanced_window.update_ui_language()
        self._bring_window_to_front(self.advanced_window)

    def open_key_presser_window(self) -> None:
        if self.key_window is not None and self.key_window.winfo_exists():
            self._bring_window_to_front(self.key_window)
            return

        self.key_window = KeyPresserWindow(
            self.root,
            state=self.state,
            on_start=self.start_key_presser,
            on_stop=self.stop_key_presser,
            on_save=self.save_key_settings,
        )
        self.key_window.set_history(self.history.get_events())
        self.key_window.update_ui_language()
        self._bring_window_to_front(self.key_window)

    def start_advanced(self, config: dict, sequence: list[dict], status_callback) -> None:
        self._save_advanced_to_state(config)
        self.state.sequence_actions = list(sequence)
        self._persist_state()
        self.sequence_worker.start(config, sequence, status_callback, self.history.push)

    def stop_advanced(self) -> None:
        self.sequence_worker.stop()
        self.history.push(self._tf("history_stop_advanced_requested"))

    def start_key_presser(self, config: dict, status_callback) -> None:
        self._save_key_to_state(config)
        self.key_worker.start(config, status_callback, self.history.push)

    def stop_key_presser(self) -> None:
        self.key_worker.stop()
        self.history.push(self._tf("history_stop_key_requested"))

    def save_key_settings(self, config: dict) -> None:
        self._save_key_to_state(config)
        self._persist_state()
        self.history.push(self._tf("history_key_settings_saved"))

    def export_profile(self) -> None:
        initial_name = f"aura_clicker_profile_v{APP_VERSION}.aura_profile.json"
        target = filedialog.asksaveasfilename(
            title=self._tf("dialog_export_title"),
            defaultextension=".json",
            initialfile=initial_name,
            filetypes=[("Profil Aura-Clicker", "*.aura_profile.json"), ("JSON", "*.json")],
        )
        if not target:
            return

        path = self.profile_manager.export_profile(self.state, Path(target))
        self.history.push(self._tf("history_profile_exported", name=path.name))
        if self.main_window:
            self.main_window._set_status(self._tf("status_profile_exported", name=path.name))

    def import_profile(self) -> None:
        target = filedialog.askopenfilename(
            title=self._tf("dialog_import_title"),
            filetypes=[("Profil Aura-Clicker", "*.aura_profile.json"), ("JSON", "*.json")],
        )
        if not target:
            return

        try:
            payload = self.profile_manager.import_profile(Path(target))
            self._apply_profile_payload(payload)
        except (OSError, TypeError, ValueError) as exc:
            logger = get_structured_logger()
            if logger:
                logger.log_exception("main.py", exc, context={"step": "import_profile", "file": target})
            messagebox.showerror(self._tf("dialog_import_error_title"), self._tf("dialog_import_error_message", error=str(exc)))
            self.history.push(self._tf("history_profile_import_failed", error=str(exc)))
            return

        self._persist_state()
        self._register_hotkeys()
        self._refresh_windows_from_state()
        self.history.push(self._tf("history_profile_imported", name=Path(target).name))
        if self.main_window:
            self.main_window._set_status(self._tf("status_profile_imported", name=Path(target).name))

    def _apply_profile_payload(self, payload: dict) -> None:
        main_click = payload.get("main_click", {})
        advanced_execution = payload.get("advanced_execution", {})
        key_presser = payload.get("key_presser", {})
        sequence_actions = payload.get("sequence_actions", [])
        hotkeys = payload.get("hotkeys", {})

        for field, value in main_click.items():
            if hasattr(self.state.main_click, field):
                setattr(self.state.main_click, field, value)

        for field, value in advanced_execution.items():
            if hasattr(self.state.advanced_execution, field):
                setattr(self.state.advanced_execution, field, value)

        for field, value in key_presser.items():
            if hasattr(self.state.key_presser, field):
                setattr(self.state.key_presser, field, value)

        normalized_actions: list[dict] = []
        for action in sequence_actions:
            if action.get("type") == "mouse":
                coords = action.get("coords", [0, 0])
                if isinstance(coords, (list, tuple)) and len(coords) == 2:
                    action["coords"] = (int(coords[0]), int(coords[1]))
            normalized_actions.append(action)

        self.state.sequence_actions = normalized_actions
        self.state.hotkeys = {**self.state.hotkeys, **hotkeys}

    def _refresh_windows_from_state(self) -> None:
        if self.main_window:
            self.main_window.refresh_from_state()
        if self.advanced_window and self.advanced_window.winfo_exists():
            self.advanced_window.refresh_from_state()
        if self.key_window and self.key_window.winfo_exists():
            self.key_window.refresh_from_state()

    def _save_main_to_state(self, config: dict) -> None:
        self.state.main_click.hours = config["hours"]
        self.state.main_click.minutes = config["minutes"]
        self.state.main_click.seconds = config["seconds"]
        self.state.main_click.milliseconds = config["milliseconds"]
        self.state.main_click.infinite = config["infinite"]
        self.state.main_click.repeat_count = config["repeat_count"]
        self.state.main_click.current_position = config["current_position"]
        self.state.main_click.x = config["x"]
        self.state.main_click.y = config["y"]
        self.state.main_click.mouse_button = config["mouse_button"]
        self.state.main_click.click_type = config["click_type"]
        self.state.main_click.temporal_jitter_enabled = bool(config.get("temporal_jitter_enabled", False))
        self.state.main_click.temporal_jitter_min = float(config.get("temporal_jitter_min", 0.008))
        self.state.main_click.temporal_jitter_max = float(config.get("temporal_jitter_max", 0.015))
        self._persist_state()

    def _save_advanced_to_state(self, config: dict) -> None:
        self.state.advanced_execution.repeat_sequence = config["repeat_sequence"]
        self.state.advanced_execution.interval_seconds = config["interval_seconds"]
        self.state.advanced_execution.interval_milliseconds = config["interval_milliseconds"]
        self.state.advanced_execution.humanized_mode = config["humanized_mode"]
        self.state.advanced_execution.humanized_jitter = config["humanized_jitter"]
        self.state.advanced_execution.repeat_delay_seconds = float(config.get("repeat_delay_seconds", 0.0))
        self.state.advanced_execution.temporal_jitter_enabled = bool(config.get("temporal_jitter_enabled", False))
        self.state.advanced_execution.temporal_jitter_min = float(config.get("temporal_jitter_min", 0.008))
        self.state.advanced_execution.temporal_jitter_max = float(config.get("temporal_jitter_max", 0.015))

    def _save_key_to_state(self, config: dict) -> None:
        self.state.key_presser.key_name = config["key_name"]
        self.state.key_presser.hours = config["hours"]
        self.state.key_presser.minutes = config["minutes"]
        self.state.key_presser.seconds = config["seconds"]
        self.state.key_presser.milliseconds = config["milliseconds"]
        self.state.key_presser.infinite = config["infinite"]
        self.state.key_presser.repeat_count = config["repeat_count"]
        self.state.key_presser.hold_key_down = config["hold_key_down"]
        self.state.key_presser.hold_duration_ms = config["hold_duration_ms"]

    def _hotkey_start_click(self) -> None:
        if not self.main_window:
            return
        config = self.main_window._build_click_config()
        config["language"] = self.state.current_language
        self.start_main_click(config, self.main_window._set_status)

    def _hotkey_toggle_click(self) -> None:
        if not self.main_window:
            return
        config = self.main_window._build_click_config()
        config["language"] = self.state.current_language
        self.toggle_main_click(config, self.main_window._set_status)

    def _hotkey_start_advanced(self) -> None:
        config = {
            "repeat_sequence": self.state.advanced_execution.repeat_sequence,
            "repeat_delay_seconds": self.state.advanced_execution.repeat_delay_seconds,
            "interval_seconds": self.state.advanced_execution.interval_seconds,
            "interval_milliseconds": self.state.advanced_execution.interval_milliseconds,
            "humanized_mode": self.state.advanced_execution.humanized_mode,
            "humanized_jitter": self.state.advanced_execution.humanized_jitter,
            "temporal_jitter_enabled": self.state.advanced_execution.temporal_jitter_enabled,
            "temporal_jitter_min": self.state.advanced_execution.temporal_jitter_min,
            "temporal_jitter_max": self.state.advanced_execution.temporal_jitter_max,
            "language": self.state.current_language,
        }

        def status(msg: str) -> None:
            if self.advanced_window and self.advanced_window.winfo_exists():
                self.advanced_window._set_status(msg)
            elif self.main_window:
                self.main_window._set_status(msg)

        self.sequence_worker.start(config, list(self.state.sequence_actions), status, self.history.push)

    def _hotkey_start_key_presser(self) -> None:
        config = {
            "key_name": self.state.key_presser.key_name,
            "hours": self.state.key_presser.hours,
            "minutes": self.state.key_presser.minutes,
            "seconds": self.state.key_presser.seconds,
            "milliseconds": self.state.key_presser.milliseconds,
            "infinite": self.state.key_presser.infinite,
            "repeat_count": self.state.key_presser.repeat_count,
            "hold_key_down": self.state.key_presser.hold_key_down,
            "hold_duration_ms": self.state.key_presser.hold_duration_ms,
            "language": self.state.current_language,
        }

        def status(msg: str) -> None:
            if self.key_window and self.key_window.winfo_exists():
                self.key_window._set_status(msg)
            elif self.main_window:
                self.main_window._set_status(msg)

        self.key_worker.start(config, status, self.history.push)

    def _persist_state(self) -> None:
        self.settings_store.save(self.state)

    def change_language(self, language: str) -> None:
        self.state.current_language = "en" if language == "en" else "fr"
        self._persist_state()
        if self.main_window:
            self.main_window.update_ui_language()
        if self.advanced_window and self.advanced_window.winfo_exists():
            self.advanced_window.update_ui_language()
        if self.key_window and self.key_window.winfo_exists():
            self.key_window.update_ui_language()

    def _broadcast_history(self, line: str) -> None:
        if self.main_window:
            self.main_window.append_history(line)
        if self.advanced_window and self.advanced_window.winfo_exists():
            self.advanced_window.append_history(line)
        if self.key_window and self.key_window.winfo_exists():
            self.key_window.append_history(line)

    def _window_alive(self, root, window_type) -> bool:
        for child in root.winfo_children():
            if isinstance(child, window_type) and child.winfo_exists():
                self._bring_window_to_front(child)
                return True
        return False

    def _bring_window_to_front(self, window) -> None:
        window.update_idletasks()
        window.lift()
        window.attributes("-topmost", True)
        window.focus_force()
        window.after(220, lambda: window.attributes("-topmost", False))

    def _on_close(self) -> None:
        self.history.push(self._tf("history_app_closing"))
        self.click_worker.stop()
        self.sequence_worker.stop()
        self.key_worker.stop()
        self.hotkey_manager.unregister_all()
        self._persist_state()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = AuraClickerApplication()
    app.run()
