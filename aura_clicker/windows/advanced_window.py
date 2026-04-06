from __future__ import annotations

import customtkinter as ctk

from ..capture import capture_hotkey_combination, capture_mouse_position
from ..utils import safe_int
from ..widgets import CTkListbox


class AdvancedWindow(ctk.CTkToplevel):
    def __init__(self, master, state, on_start, on_stop, on_save_state):
        super().__init__(master)
        self.title("Créateur d'Automatisation Avancé")
        self.geometry("1180x760")
        self.minsize(1080, 700)
        try:
            icon_path = getattr(master, "icon_path", None)
            if icon_path:
                self.iconbitmap(icon_path)
        except Exception:
            pass

        self._state = state
        self._on_start = on_start
        self._on_stop = on_stop
        self._on_save_state = on_save_state

        self._build_ui()
        self._load_state()

    def _build_ui(self) -> None:
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, columnspan=3, sticky="ew", padx=14, pady=(14, 8))
        ctk.CTkLabel(
            header,
            text="Créez des séquences sophistiquées de clics souris et de raccourcis clavier.",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).pack(anchor="w", padx=14, pady=14)

        mouse_frame = ctk.CTkFrame(self)
        mouse_frame.grid(row=1, column=0, sticky="nsew", padx=(14, 7), pady=8)
        mouse_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(mouse_frame, text="Actions de clic souris", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(12, 10))

        ctk.CTkLabel(mouse_frame, text="X").grid(row=1, column=0, sticky="w", padx=(12, 4))
        self.x_entry = ctk.CTkEntry(mouse_frame, width=100)
        self.x_entry.grid(row=1, column=1, sticky="ew", pady=6)

        ctk.CTkLabel(mouse_frame, text="Y").grid(row=2, column=0, sticky="w", padx=(12, 4))
        self.y_entry = ctk.CTkEntry(mouse_frame, width=100)
        self.y_entry.grid(row=2, column=1, sticky="ew", pady=6)

        self.pick_btn = ctk.CTkButton(mouse_frame, text="◎", width=44, command=self._capture_target)
        self.pick_btn.grid(row=1, column=2, rowspan=2, padx=(8, 12), pady=6)

        ctk.CTkLabel(mouse_frame, text="Bouton").grid(row=3, column=0, sticky="w", padx=12, pady=(8, 0))
        self.mouse_button = ctk.CTkComboBox(mouse_frame, values=["Gauche", "Droit"])
        self.mouse_button.grid(row=4, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

        ctk.CTkLabel(mouse_frame, text="Type de clic").grid(row=5, column=0, sticky="w", padx=12, pady=(8, 0))
        self.click_type = ctk.CTkComboBox(mouse_frame, values=["Simple", "Double"])
        self.click_type.grid(row=6, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

        ctk.CTkLabel(mouse_frame, text="Nombre de clics à cette position").grid(row=7, column=0, columnspan=2, sticky="w", padx=12, pady=(8, 0))
        self.repeats_entry = ctk.CTkEntry(mouse_frame)
        self.repeats_entry.grid(row=8, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

        ctk.CTkButton(mouse_frame, text="+ Ajouter action Clic", fg_color="#4F46E5", hover_color="#4338CA", command=self._add_mouse_action).grid(row=9, column=0, columnspan=3, sticky="ew", padx=12, pady=(10, 12))

        keyboard_frame = ctk.CTkFrame(self)
        keyboard_frame.grid(row=1, column=1, sticky="nsew", padx=7, pady=8)
        keyboard_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(keyboard_frame, text="Raccourcis clavier", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 10))
        ctk.CTkLabel(keyboard_frame, text="Supporte Ctrl+C, Ctrl+Alt+Suppr, etc.").grid(row=1, column=0, sticky="w", padx=12)

        self.key_preview = ctk.CTkTextbox(keyboard_frame, height=96)
        self.key_preview.grid(row=2, column=0, sticky="ew", padx=12, pady=10)
        self.key_preview.insert("1.0", "Aucune touche capturée")

        ctk.CTkButton(keyboard_frame, text="Enregistrer les touches", command=self._capture_keys).grid(row=3, column=0, sticky="ew", padx=12, pady=6)
        ctk.CTkButton(keyboard_frame, text="+ Ajouter action Touche", fg_color="#4F46E5", hover_color="#4338CA", command=self._add_key_action).grid(row=4, column=0, sticky="ew", padx=12, pady=(6, 12))

        sequence_frame = ctk.CTkFrame(self)
        sequence_frame.grid(row=1, column=2, rowspan=2, sticky="nsew", padx=(7, 14), pady=8)
        sequence_frame.grid_columnconfigure((0, 1), weight=1)
        sequence_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(sequence_frame, text="Séquence d'actions", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 8))

        self.listbox = CTkListbox(sequence_frame, height=360)
        self.listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=8)

        ctk.CTkButton(sequence_frame, text="Supprimer action", fg_color="#EF4444", hover_color="#DC2626", command=self._delete_action).grid(row=2, column=0, sticky="ew", padx=(10, 5), pady=(6, 12))
        ctk.CTkButton(sequence_frame, text="Effacer tout", fg_color="#64748B", hover_color="#475569", command=self._clear_actions).grid(row=2, column=1, sticky="ew", padx=(5, 10), pady=(6, 12))

        execution_frame = ctk.CTkFrame(self)
        execution_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=14, pady=(0, 14))
        execution_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(execution_frame, text="Paramètres d'exécution", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(12, 10))

        self.repeat_seq_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(execution_frame, text="Répéter la séquence", variable=self.repeat_seq_var).grid(row=1, column=0, columnspan=2, sticky="w", padx=12, pady=4)

        self.humanized_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(execution_frame, text="Mode humanisé exclusif (jitter)", variable=self.humanized_var).grid(row=1, column=2, columnspan=2, sticky="w", padx=12, pady=4)

        ctk.CTkLabel(execution_frame, text="Intervalle entre actions: sec").grid(row=2, column=0, sticky="w", padx=12, pady=8)
        self.interval_s_entry = ctk.CTkEntry(execution_frame, width=100)
        self.interval_s_entry.grid(row=2, column=1, sticky="w", pady=8)

        ctk.CTkLabel(execution_frame, text="ms").grid(row=2, column=2, sticky="e", padx=6, pady=8)
        self.interval_ms_entry = ctk.CTkEntry(execution_frame, width=100)
        self.interval_ms_entry.grid(row=2, column=3, sticky="w", pady=8)

        ctk.CTkLabel(execution_frame, text="Jitter (pixels)").grid(row=3, column=0, sticky="w", padx=12, pady=(0, 8))
        self.jitter_entry = ctk.CTkEntry(execution_frame, width=100)
        self.jitter_entry.grid(row=3, column=1, sticky="w", pady=(0, 8))

        self.adv_status = ctk.CTkLabel(execution_frame, text="Prêt")
        self.adv_status.grid(row=3, column=2, columnspan=2, sticky="w", padx=12, pady=(0, 8))

        ctk.CTkButton(execution_frame, text="Démarrer (F3)", fg_color="#10B981", hover_color="#059669", command=self._start).grid(row=4, column=0, columnspan=2, sticky="ew", padx=12, pady=(4, 12))
        ctk.CTkButton(execution_frame, text="Arrêter (F4)", fg_color="#EF4444", hover_color="#DC2626", command=self._stop).grid(row=4, column=2, columnspan=2, sticky="ew", padx=12, pady=(4, 12))

        history_frame = ctk.CTkFrame(self)
        history_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=14, pady=(0, 14))
        ctk.CTkLabel(history_frame, text="Historique temps réel", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=12, pady=(10, 6))
        self.history_box = ctk.CTkTextbox(history_frame, height=110)
        self.history_box.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    def _load_state(self) -> None:
        self.interval_s_entry.delete(0, "end")
        self.interval_ms_entry.delete(0, "end")
        self.jitter_entry.delete(0, "end")

        cfg = self._state.advanced_execution
        self.repeat_seq_var.set(cfg.repeat_sequence)
        self.interval_s_entry.insert(0, str(cfg.interval_seconds))
        self.interval_ms_entry.insert(0, str(cfg.interval_milliseconds))
        self.humanized_var.set(cfg.humanized_mode)
        self.jitter_entry.insert(0, str(cfg.humanized_jitter))

        labels = [self._format_action(item) for item in self._state.sequence_actions]
        self.listbox.set_items(labels)

        self.mouse_button.set("Gauche")
        self.click_type.set("Simple")
        self.repeats_entry.delete(0, "end")
        self.repeats_entry.insert(0, "1")

    def refresh_from_state(self) -> None:
        self.listbox.clear()
        self._load_state()

    def _capture_target(self) -> None:
        self.adv_status.configure(text="Capture position: cliquez n'importe où")

        def on_captured(x: int, y: int) -> None:
            self.after(0, lambda: self._apply_position(x, y))

        capture_mouse_position(on_captured)

    def _apply_position(self, x: int, y: int) -> None:
        self.x_entry.delete(0, "end")
        self.y_entry.delete(0, "end")
        self.x_entry.insert(0, str(x))
        self.y_entry.insert(0, str(y))
        self.adv_status.configure(text=f"Position capturée: {x}, {y}")

    def _capture_keys(self) -> None:
        self.adv_status.configure(text="Capture touches en cours...")

        def on_captured(combo: str) -> None:
            self.after(0, lambda: self._apply_keys(combo))

        capture_hotkey_combination(on_captured)

    def _apply_keys(self, combo: str) -> None:
        self.key_preview.delete("1.0", "end")
        self.key_preview.insert("1.0", combo)
        self.adv_status.configure(text=f"Touches capturées: {combo}")

    def _add_mouse_action(self) -> None:
        x = safe_int(self.x_entry.get(), default=0)
        y = safe_int(self.y_entry.get(), default=0)
        repeats = safe_int(self.repeats_entry.get(), default=1, minimum=1)
        button = "left" if self.mouse_button.get() == "Gauche" else "right"
        click_type = "single" if self.click_type.get() == "Simple" else "double"

        action = {
            "type": "mouse",
            "coords": (x, y),
            "button": button,
            "click_type": click_type,
            "repeats": repeats,
        }
        self._state.sequence_actions.append(action)
        self.listbox.insert(self._format_action(action))
        self._save_runtime_state()

    def _add_key_action(self) -> None:
        keys = self.key_preview.get("1.0", "end").strip()
        if not keys or keys == "Aucune touche capturée":
            self.adv_status.configure(text="Capturez d'abord une combinaison")
            return

        action = {"type": "keyboard", "keys": keys.lower()}
        self._state.sequence_actions.append(action)
        self.listbox.insert(self._format_action(action))
        self._save_runtime_state()

    def _format_action(self, action: dict) -> str:
        if action["type"] == "mouse":
            x, y = action["coords"]
            button = "Gauche" if action["button"] == "left" else "Droit"
            click_type = "Simple" if action["click_type"] == "single" else "Double"
            return f"[Pos: {x}, {y}] | [Bouton: {button}, Type: {click_type}] | [Clics: {action['repeats']}]"
        return f"[Touche: {action['keys'].upper()}]"

    def _delete_action(self) -> None:
        index = self.listbox.delete_selected()
        if index is None:
            return
        self._state.sequence_actions.pop(index)
        self._save_runtime_state()

    def _clear_actions(self) -> None:
        self._state.sequence_actions.clear()
        self.listbox.clear()
        self._save_runtime_state()

    def _build_execution_config(self) -> dict:
        return {
            "repeat_sequence": self.repeat_seq_var.get(),
            "interval_seconds": safe_int(self.interval_s_entry.get(), default=1, minimum=0),
            "interval_milliseconds": safe_int(self.interval_ms_entry.get(), default=0, minimum=0),
            "humanized_mode": self.humanized_var.get(),
            "humanized_jitter": safe_int(self.jitter_entry.get(), default=3, minimum=0),
        }

    def _start(self) -> None:
        config = self._build_execution_config()
        self._on_start(config, list(self._state.sequence_actions), self._set_status)
        self._save_runtime_state()

    def _stop(self) -> None:
        self._on_stop()
        self._set_status("Séquence avancée arrêtée")

    def _set_status(self, text: str) -> None:
        self.after(0, lambda: self.adv_status.configure(text=text))

    def append_history(self, line: str) -> None:
        def _append() -> None:
            self.history_box.insert("1.0", line + "\n")

        self.after(0, _append)

    def set_history(self, items: list[str]) -> None:
        self.history_box.delete("1.0", "end")
        if items:
            self.history_box.insert("1.0", "\n".join(items) + "\n")

    def _save_runtime_state(self) -> None:
        cfg = self._build_execution_config()
        self._state.advanced_execution.repeat_sequence = cfg["repeat_sequence"]
        self._state.advanced_execution.interval_seconds = cfg["interval_seconds"]
        self._state.advanced_execution.interval_milliseconds = cfg["interval_milliseconds"]
        self._state.advanced_execution.humanized_mode = cfg["humanized_mode"]
        self._state.advanced_execution.humanized_jitter = cfg["humanized_jitter"]
        self._on_save_state()
