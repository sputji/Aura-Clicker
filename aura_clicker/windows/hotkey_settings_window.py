from __future__ import annotations

import customtkinter as ctk


class HotkeySettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, initial_hotkeys: dict[str, str], on_save):
        super().__init__(master)
        self.title("Configuration des raccourcis")
        self.geometry("420x240")
        self.resizable(False, False)
        try:
            icon_path = getattr(master, "icon_path", None)
            if icon_path:
                self.iconbitmap(icon_path)
        except Exception:
            pass

        self._on_save = on_save
        self._defaults = dict(initial_hotkeys)

        ctk.CTkLabel(self, text="Start Hotkey:").place(x=30, y=35)
        ctk.CTkLabel(self, text="Stop Hotkey:").place(x=30, y=85)
        ctk.CTkLabel(self, text="Toggle Hotkey:").place(x=30, y=135)

        self.start_entry = ctk.CTkEntry(self, width=180, justify="center")
        self.start_entry.place(x=200, y=35)
        self.stop_entry = ctk.CTkEntry(self, width=180, justify="center")
        self.stop_entry.place(x=200, y=85)
        self.toggle_entry = ctk.CTkEntry(self, width=180, justify="center")
        self.toggle_entry.place(x=200, y=135)

        self.start_entry.insert(0, initial_hotkeys.get("start", "F6"))
        self.stop_entry.insert(0, initial_hotkeys.get("stop", "F7"))
        self.toggle_entry.insert(0, initial_hotkeys.get("toggle", "F8"))

        ctk.CTkButton(self, text="Enregistrer", width=160, command=self._save).place(x=25, y=185)
        ctk.CTkButton(self, text="Réinitialiser", width=160, fg_color="#6B7280", hover_color="#4B5563", command=self._reset).place(x=225, y=185)

    def _save(self) -> None:
        payload = {
            "start": self.start_entry.get().strip().upper(),
            "stop": self.stop_entry.get().strip().upper(),
            "toggle": self.toggle_entry.get().strip().upper(),
        }
        self._on_save(payload)
        self.destroy()

    def _reset(self) -> None:
        self.start_entry.delete(0, "end")
        self.stop_entry.delete(0, "end")
        self.toggle_entry.delete(0, "end")

        self.start_entry.insert(0, self._defaults.get("start", "F6"))
        self.stop_entry.insert(0, self._defaults.get("stop", "F7"))
        self.toggle_entry.insert(0, self._defaults.get("toggle", "F8"))
