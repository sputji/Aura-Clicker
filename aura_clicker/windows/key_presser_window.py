from __future__ import annotations

import customtkinter as ctk

from ..capture import capture_hotkey_combination
from ..utils import safe_int


class KeyPresserWindow(ctk.CTkToplevel):
    def __init__(self, master, state, on_start, on_stop, on_save):
        super().__init__(master)
        self.title("Pression de touche automatique")
        self.geometry("900x650")
        self.minsize(900, 650)
        self.transient(master)
        try:
            icon_path = getattr(master, "icon_path", None)
            if icon_path:
                self.iconbitmap(icon_path)
        except Exception:
            pass

        self._state = state
        self._on_start = on_start
        self._on_stop = on_stop
        self._on_save = on_save

        self._build_ui()
        self._load_from_state()

        # Force la fenêtre au premier plan de l'OS
        self.attributes("-topmost", True)
        # Attend 200ms que la fenêtre soit dessinée, puis retire le topmost pour qu'elle redescende dans le flux normal, tout en restant focus
        self.after(200, lambda: self.attributes("-topmost", False))
        self.focus_force()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        key_frame = ctk.CTkFrame(self)
        key_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        key_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(key_frame, text="Sélection de touche", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=14, pady=(12, 8))
        ctk.CTkLabel(key_frame, text="Touche sélectionnée").grid(row=1, column=0, sticky="w", padx=14, pady=10)

        self.key_entry = ctk.CTkEntry(key_frame)
        self.key_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=10)

        self.capture_btn = ctk.CTkButton(key_frame, text="Capturer", width=140, command=self._capture_key)
        self.capture_btn.grid(row=1, column=2, padx=14, pady=10)

        ctk.CTkLabel(
            key_frame,
            text="Cliquez sur Capturer puis appuyez sur une touche ou combinaison (ex: Ctrl+Shift+A)",
            text_color=("#4F46E5", "#A5B4FC"),
        ).grid(row=2, column=0, columnspan=3, sticky="w", padx=14, pady=(0, 12))

        interval_frame = ctk.CTkFrame(self)
        interval_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=8)

        ctk.CTkLabel(interval_frame, text="Intervalle", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=8, sticky="w", padx=14, pady=(12, 8))

        self.h_entry = self._int_entry(interval_frame, 1, 0)
        ctk.CTkLabel(interval_frame, text="heures").grid(row=1, column=1, padx=8)
        self.m_entry = self._int_entry(interval_frame, 1, 2)
        ctk.CTkLabel(interval_frame, text="minutes").grid(row=1, column=3, padx=8)
        self.s_entry = self._int_entry(interval_frame, 1, 4)
        ctk.CTkLabel(interval_frame, text="secondes").grid(row=1, column=5, padx=8)
        self.ms_entry = self._int_entry(interval_frame, 1, 6)
        ctk.CTkLabel(interval_frame, text="millisecondes").grid(row=1, column=7, padx=(8, 14))

        repeat_frame = ctk.CTkFrame(self)
        repeat_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=8)
        repeat_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(repeat_frame, text="Répétition", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(12, 8))

        self.repeat_mode = ctk.StringVar(value="infinite")
        ctk.CTkRadioButton(repeat_frame, text="Infini (jusqu'à arrêt)", variable=self.repeat_mode, value="infinite").grid(row=1, column=0, sticky="w", padx=14, pady=6)
        self.repeat_count_entry = ctk.CTkEntry(repeat_frame, width=120)
        self.repeat_count_entry.grid(row=2, column=0, sticky="w", padx=44, pady=(0, 6))
        ctk.CTkLabel(repeat_frame, text="Nombre de fois").grid(row=2, column=1, sticky="w", pady=(0, 6))

        self.hold_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(repeat_frame, text="Maintenir la touche enfoncée", variable=self.hold_var).grid(row=1, column=2, sticky="w", padx=14, pady=6)

        ctk.CTkLabel(repeat_frame, text="Durée du maintien (ms)").grid(row=2, column=2, sticky="w", padx=14, pady=(0, 6))
        self.hold_duration_entry = ctk.CTkEntry(repeat_frame, width=120)
        self.hold_duration_entry.grid(row=2, column=3, sticky="w", pady=(0, 6))

        ctk.CTkRadioButton(repeat_frame, text="Nombre de fois", variable=self.repeat_mode, value="count").grid(row=3, column=0, sticky="w", padx=14, pady=(6, 12))

        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=8)
        ctk.CTkLabel(status_frame, text="Statut", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=14, pady=(12, 8))

        self.status_label = ctk.CTkLabel(status_frame, text="Prêt")
        self.status_label.pack(anchor="w", padx=14, pady=(0, 12))

        history_frame = ctk.CTkFrame(self)
        history_frame.grid(row=4, column=0, sticky="ew", padx=16, pady=8)
        ctk.CTkLabel(history_frame, text="Historique temps réel", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=14, pady=(10, 6))
        self.history_box = ctk.CTkTextbox(history_frame, height=95)
        self.history_box.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        controls = ctk.CTkFrame(self)
        controls.grid(row=5, column=0, sticky="ew", padx=16, pady=(8, 16))

        self.start_btn = ctk.CTkButton(controls, text="Démarrer (F1)", fg_color="#10B981", hover_color="#059669", command=self._start)
        self.start_btn.pack(side="left", padx=10, pady=12)

        self.stop_btn = ctk.CTkButton(controls, text="Arrêter (F2)", fg_color="#64748B", hover_color="#475569", command=self._stop)
        self.stop_btn.pack(side="left", padx=10, pady=12)

        self.save_btn = ctk.CTkButton(controls, text="Enregistrer les paramètres", fg_color="#4F46E5", hover_color="#4338CA", command=self._save_state)
        self.save_btn.pack(side="right", padx=10, pady=12)

    def _int_entry(self, parent, row, column):
        entry = ctk.CTkEntry(parent, width=80, justify="center")
        entry.grid(row=row, column=column, padx=(14 if column == 0 else 0, 0), pady=(0, 14))
        return entry

    def _load_from_state(self) -> None:
        data = self._state.key_presser
        self.key_entry.delete(0, "end")
        self.h_entry.delete(0, "end")
        self.m_entry.delete(0, "end")
        self.s_entry.delete(0, "end")
        self.ms_entry.delete(0, "end")
        self.repeat_count_entry.delete(0, "end")
        self.hold_duration_entry.delete(0, "end")

        self.key_entry.insert(0, data.key_name)
        self.h_entry.insert(0, str(data.hours))
        self.m_entry.insert(0, str(data.minutes))
        self.s_entry.insert(0, str(data.seconds))
        self.ms_entry.insert(0, str(data.milliseconds))
        self.repeat_count_entry.insert(0, str(data.repeat_count))
        self.hold_duration_entry.insert(0, str(data.hold_duration_ms))
        self.repeat_mode.set("infinite" if data.infinite else "count")
        self.hold_var.set(data.hold_key_down)

    def refresh_from_state(self) -> None:
        self._load_from_state()

    def _capture_key(self) -> None:
        self.status_label.configure(text="Capture en cours... appuyez sur une touche")

        def on_captured(combo: str) -> None:
            self.after(0, lambda: self._apply_captured_key(combo))

        capture_hotkey_combination(on_captured)

    def _apply_captured_key(self, combo: str) -> None:
        self.key_entry.delete(0, "end")
        self.key_entry.insert(0, combo)
        self.status_label.configure(text=f"Touche capturée: {combo}")

    def _build_config(self) -> dict:
        return {
            "key_name": self.key_entry.get().strip().lower(),
            "hours": safe_int(self.h_entry.get(), minimum=0),
            "minutes": safe_int(self.m_entry.get(), minimum=0),
            "seconds": safe_int(self.s_entry.get(), minimum=0),
            "milliseconds": safe_int(self.ms_entry.get(), default=1000, minimum=1),
            "infinite": self.repeat_mode.get() == "infinite",
            "repeat_count": safe_int(self.repeat_count_entry.get(), default=1, minimum=1),
            "hold_key_down": self.hold_var.get(),
            "hold_duration_ms": safe_int(self.hold_duration_entry.get(), default=100, minimum=1),
        }

    def _start(self) -> None:
        config = self._build_config()
        self._on_start(config, self._set_status)

    def _stop(self) -> None:
        self._on_stop()
        self._set_status("Auto-touche arrêté")

    def _save_state(self) -> None:
        config = self._build_config()
        self._on_save(config)
        self._set_status("Paramètres sauvegardés")

    def _set_status(self, text: str) -> None:
        self.after(0, lambda: self.status_label.configure(text=text))

    def append_history(self, line: str) -> None:
        def _append() -> None:
            self.history_box.insert("1.0", line + "\n")

        self.after(0, _append)

    def set_history(self, items: list[str]) -> None:
        self.history_box.delete("1.0", "end")
        if items:
            self.history_box.insert("1.0", "\n".join(items) + "\n")

