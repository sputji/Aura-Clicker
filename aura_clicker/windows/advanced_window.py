from __future__ import annotations

from tkinter import filedialog

import customtkinter as ctk

from ..capture import capture_hotkey_combination, capture_mouse_position
from ..macro_recorder import MacroRecorder
from ..translations import get_text
from ..utils import safe_int
from ..widgets import CTkListbox


class AdvancedWindow(ctk.CTkToplevel):
    def __init__(self, master, state, on_start, on_stop, on_save_state):
        super().__init__(master)
        self.title("Créateur d'Automatisation Avancé")
        self.geometry("1180x760")
        self.minsize(1080, 700)
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
        self._on_save_state = on_save_state
        self._macro_recorder = MacroRecorder()

        self._build_ui()
        self._load_state()

        # Force la fenêtre au premier plan de l'OS
        self.attributes("-topmost", True)
        # Attend 200ms que la fenêtre soit dessinée, puis retire le topmost pour qu'elle redescende dans le flux normal, tout en restant focus
        self.after(200, lambda: self.attributes("-topmost", False))
        self.focus_force()

    def _build_ui(self) -> None:
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, columnspan=3, sticky="ew", padx=14, pady=(14, 8))
        self.header_label = ctk.CTkLabel(
            header,
            text="Créez des séquences sophistiquées de clics souris et de raccourcis clavier.",
            font=ctk.CTkFont(size=17, weight="bold"),
        )
        self.header_label.pack(anchor="w", padx=14, pady=14)

        mouse_frame = ctk.CTkFrame(self)
        mouse_frame.grid(row=1, column=0, sticky="nsew", padx=(14, 7), pady=8)
        mouse_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.mouse_title_label = ctk.CTkLabel(mouse_frame, text="Actions de clic souris", font=ctk.CTkFont(size=18, weight="bold"))
        self.mouse_title_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(12, 10))

        self.target_type_label = ctk.CTkLabel(mouse_frame, text="Cible du clic")
        self.target_type_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 0))
        self.target_mode = ctk.StringVar(value="coords")
        self.target_coords_radio = ctk.CTkRadioButton(mouse_frame, text="Coordonnées", variable=self.target_mode, value="coords", command=self._toggle_target_mode)
        self.target_coords_radio.grid(row=2, column=0, sticky="w", padx=12, pady=(2, 0))
        self.target_image_radio = ctk.CTkRadioButton(mouse_frame, text="Image", variable=self.target_mode, value="image", command=self._toggle_target_mode)
        self.target_image_radio.grid(row=2, column=1, sticky="w", padx=12, pady=(2, 0))

        ctk.CTkLabel(mouse_frame, text="X").grid(row=3, column=0, sticky="w", padx=(12, 4))
        self.x_entry = ctk.CTkEntry(mouse_frame, width=100)
        self.x_entry.grid(row=3, column=1, sticky="ew", pady=6)

        ctk.CTkLabel(mouse_frame, text="Y").grid(row=4, column=0, sticky="w", padx=(12, 4))
        self.y_entry = ctk.CTkEntry(mouse_frame, width=100)
        self.y_entry.grid(row=4, column=1, sticky="ew", pady=6)

        self.pick_btn = ctk.CTkButton(mouse_frame, text="◎", width=44, command=self._capture_target)
        self.pick_btn.grid(row=3, column=2, rowspan=2, padx=(8, 12), pady=6)

        self.image_file_label = ctk.CTkLabel(mouse_frame, text="Image (PNG/JPG)")
        self.image_file_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=12, pady=(8, 0))
        self.image_path_entry = ctk.CTkEntry(mouse_frame)
        self.image_path_entry.grid(row=6, column=0, columnspan=2, sticky="ew", padx=12, pady=6)
        self.browse_image_btn = ctk.CTkButton(mouse_frame, text="Parcourir", width=90, command=self._browse_image)
        self.browse_image_btn.grid(row=6, column=2, padx=(8, 12), pady=6)

        self.button_label = ctk.CTkLabel(mouse_frame, text="Bouton")
        self.button_label.grid(row=7, column=0, sticky="w", padx=12, pady=(8, 0))
        self.mouse_button = ctk.CTkComboBox(mouse_frame, values=["Gauche", "Droit"])
        self.mouse_button.grid(row=8, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

        self.click_type_label = ctk.CTkLabel(mouse_frame, text="Type de clic")
        self.click_type_label.grid(row=9, column=0, sticky="w", padx=12, pady=(8, 0))
        self.click_type = ctk.CTkComboBox(mouse_frame, values=["Simple", "Double"])
        self.click_type.grid(row=10, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

        self.click_retries_label = ctk.CTkLabel(mouse_frame, text="Nombre de clics / tentatives")
        self.click_retries_label.grid(row=11, column=0, columnspan=2, sticky="w", padx=12, pady=(8, 0))
        self.repeats_entry = ctk.CTkEntry(mouse_frame)
        self.repeats_entry.grid(row=12, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

        self.add_mouse_btn = ctk.CTkButton(mouse_frame, text="+ Ajouter action Clic", fg_color="#4F46E5", hover_color="#4338CA", command=self._add_mouse_action)
        self.add_mouse_btn.grid(row=13, column=0, columnspan=3, sticky="ew", padx=12, pady=(10, 12))

        keyboard_frame = ctk.CTkFrame(self)
        keyboard_frame.grid(row=1, column=1, sticky="nsew", padx=7, pady=8)
        keyboard_frame.grid_columnconfigure(0, weight=1)

        self.keyboard_title_label = ctk.CTkLabel(keyboard_frame, text="Raccourcis clavier", font=ctk.CTkFont(size=18, weight="bold"))
        self.keyboard_title_label.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 10))
        self.keyboard_help_label = ctk.CTkLabel(keyboard_frame, text="Supporte Ctrl+C, Ctrl+Alt+Suppr, etc.")
        self.keyboard_help_label.grid(row=1, column=0, sticky="w", padx=12)

        self.key_preview = ctk.CTkTextbox(keyboard_frame, height=96)
        self.key_preview.grid(row=2, column=0, sticky="ew", padx=12, pady=10)
        self.key_preview.insert("1.0", "Aucune touche capturée")

        self.record_keys_btn = ctk.CTkButton(keyboard_frame, text="Enregistrer les touches", command=self._capture_keys)
        self.record_keys_btn.grid(row=3, column=0, sticky="ew", padx=12, pady=6)
        self.add_key_btn = ctk.CTkButton(keyboard_frame, text="+ Ajouter action Touche", fg_color="#4F46E5", hover_color="#4338CA", command=self._add_key_action)
        self.add_key_btn.grid(row=4, column=0, sticky="ew", padx=12, pady=(6, 12))
        self.record_macro_btn = ctk.CTkButton(
            keyboard_frame,
            text="Enregistrer une macro (F9 pour Stop)",
            fg_color="#0EA5E9",
            hover_color="#0284C7",
            command=self._toggle_macro_recording,
        )
        self.record_macro_btn.grid(row=5, column=0, sticky="ew", padx=12, pady=(0, 12))

        sequence_frame = ctk.CTkFrame(self)
        sequence_frame.grid(row=1, column=2, rowspan=2, sticky="nsew", padx=(7, 14), pady=8)
        sequence_frame.grid_columnconfigure((0, 1), weight=1)
        sequence_frame.grid_rowconfigure(1, weight=1)

        self.sequence_title_label = ctk.CTkLabel(sequence_frame, text="Séquence d'actions", font=ctk.CTkFont(size=18, weight="bold"))
        self.sequence_title_label.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 8))

        self.listbox = CTkListbox(sequence_frame, height=360)
        self.listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=8)

        self.delete_action_btn = ctk.CTkButton(sequence_frame, text="Supprimer action", fg_color="#EF4444", hover_color="#DC2626", command=self._delete_action)
        self.delete_action_btn.grid(row=2, column=0, sticky="ew", padx=(10, 5), pady=(6, 12))
        self.clear_actions_btn = ctk.CTkButton(sequence_frame, text="Effacer tout", fg_color="#64748B", hover_color="#475569", command=self._clear_actions)
        self.clear_actions_btn.grid(row=2, column=1, sticky="ew", padx=(5, 10), pady=(6, 12))

        execution_frame = ctk.CTkFrame(self)
        execution_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=14, pady=(0, 14))
        execution_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.execution_title_label = ctk.CTkLabel(execution_frame, text="Paramètres d'exécution", font=ctk.CTkFont(size=18, weight="bold"))
        self.execution_title_label.grid(row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(12, 10))

        self.repeat_seq_var = ctk.BooleanVar(value=False)
        self.repeat_seq_checkbox = ctk.CTkCheckBox(execution_frame, text="Répéter la séquence continuellement", variable=self.repeat_seq_var)
        self.repeat_seq_checkbox.grid(row=1, column=0, columnspan=2, sticky="w", padx=12, pady=4)

        self.humanized_var = ctk.BooleanVar(value=True)
        self.humanized_checkbox = ctk.CTkCheckBox(execution_frame, text="Mode humanisé exclusif (jitter)", variable=self.humanized_var)
        self.humanized_checkbox.grid(row=1, column=2, columnspan=2, sticky="w", padx=12, pady=4)

        self.interval_actions_label = ctk.CTkLabel(execution_frame, text="Intervalle entre actions: sec")
        self.interval_actions_label.grid(row=2, column=0, sticky="w", padx=12, pady=8)
        self.interval_s_entry = ctk.CTkEntry(execution_frame, width=100)
        self.interval_s_entry.grid(row=2, column=1, sticky="w", pady=8)

        self.ms_label = ctk.CTkLabel(execution_frame, text="ms")
        self.ms_label.grid(row=2, column=2, sticky="e", padx=6, pady=8)
        self.interval_ms_entry = ctk.CTkEntry(execution_frame, width=100)
        self.interval_ms_entry.grid(row=2, column=3, sticky="w", pady=8)

        self.pixel_jitter_label = ctk.CTkLabel(execution_frame, text="Jitter (pixels)")
        self.pixel_jitter_label.grid(row=3, column=0, sticky="w", padx=12, pady=(0, 8))
        self.jitter_entry = ctk.CTkEntry(execution_frame, width=100)
        self.jitter_entry.grid(row=3, column=1, sticky="w", pady=(0, 8))

        self.repeat_delay_label = ctk.CTkLabel(execution_frame, text="Délai entre répétitions (s)")
        self.repeat_delay_label.grid(row=3, column=2, sticky="w", padx=12, pady=(0, 8))
        self.repeat_delay_entry = ctk.CTkEntry(execution_frame, width=120)
        self.repeat_delay_entry.grid(row=3, column=3, sticky="w", pady=(0, 8))

        self.temporal_jitter_var = ctk.BooleanVar(value=False)
        self.temporal_jitter_checkbox = ctk.CTkCheckBox(execution_frame, text="Jitter temporel", variable=self.temporal_jitter_var)
        self.temporal_jitter_checkbox.grid(row=4, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 8))

        self.min_label = ctk.CTkLabel(execution_frame, text="Min (s)")
        self.min_label.grid(row=4, column=2, sticky="e", padx=(0, 6), pady=(0, 8))
        self.temporal_jitter_min_entry = ctk.CTkEntry(execution_frame, width=100)
        self.temporal_jitter_min_entry.grid(row=4, column=3, sticky="w", pady=(0, 8))

        self.max_label = ctk.CTkLabel(execution_frame, text="Max (s)")
        self.max_label.grid(row=5, column=2, sticky="e", padx=(0, 6), pady=(0, 8))
        self.temporal_jitter_max_entry = ctk.CTkEntry(execution_frame, width=100)
        self.temporal_jitter_max_entry.grid(row=5, column=3, sticky="w", pady=(0, 8))

        self.adv_status = ctk.CTkLabel(execution_frame, text="Prêt")
        self.adv_status.grid(row=5, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 8))

        self.start_advanced_btn = ctk.CTkButton(execution_frame, text="Démarrer (F3)", fg_color="#10B981", hover_color="#059669", command=self._start)
        self.start_advanced_btn.grid(row=6, column=0, columnspan=2, sticky="ew", padx=12, pady=(4, 12))
        self.stop_advanced_btn = ctk.CTkButton(execution_frame, text="Arrêter (F4)", fg_color="#EF4444", hover_color="#DC2626", command=self._stop)
        self.stop_advanced_btn.grid(row=6, column=2, columnspan=2, sticky="ew", padx=12, pady=(4, 12))

        history_frame = ctk.CTkFrame(self)
        history_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=14, pady=(0, 14))
        self.history_title_label = ctk.CTkLabel(history_frame, text="Historique temps réel", font=ctk.CTkFont(size=16, weight="bold"))
        self.history_title_label.pack(anchor="w", padx=12, pady=(10, 6))
        self.history_box = ctk.CTkTextbox(history_frame, height=110)
        self.history_box.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self.update_ui_language()

    def _load_state(self) -> None:
        self.interval_s_entry.delete(0, "end")
        self.interval_ms_entry.delete(0, "end")
        self.jitter_entry.delete(0, "end")
        self.repeat_delay_entry.delete(0, "end")
        self.temporal_jitter_min_entry.delete(0, "end")
        self.temporal_jitter_max_entry.delete(0, "end")

        cfg = self._state.advanced_execution
        self.repeat_seq_var.set(cfg.repeat_sequence)
        self.interval_s_entry.insert(0, str(cfg.interval_seconds))
        self.interval_ms_entry.insert(0, str(cfg.interval_milliseconds))
        self.humanized_var.set(cfg.humanized_mode)
        self.jitter_entry.insert(0, str(cfg.humanized_jitter))
        self.repeat_delay_entry.insert(0, str(cfg.repeat_delay_seconds))
        self.temporal_jitter_var.set(cfg.temporal_jitter_enabled)
        self.temporal_jitter_min_entry.insert(0, str(cfg.temporal_jitter_min))
        self.temporal_jitter_max_entry.insert(0, str(cfg.temporal_jitter_max))

        labels = [self._format_action(item) for item in self._state.sequence_actions]
        self.listbox.set_items(labels)

        self.target_mode.set("coords")
        self.mouse_button.set("Gauche")
        self.click_type.set("Simple")
        self.image_path_entry.delete(0, "end")
        self.repeats_entry.delete(0, "end")
        self.repeats_entry.insert(0, "1")
        self._toggle_target_mode()

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
        repeats = safe_int(self.repeats_entry.get(), default=1, minimum=1)
        button = "left" if self.mouse_button.get() in ("Gauche", "Left") else "right"
        click_type = "single" if self.click_type.get() in ("Simple", "Single") else "double"

        if self.target_mode.get() == "image":
            image_path = self.image_path_entry.get().strip()
            if not image_path:
                self.adv_status.configure(text="Sélectionnez une image avant d'ajouter l'action")
                return
            action = {
                "type": "image",
                "image_path": image_path,
                "button": button,
                "click_type": click_type,
                "retries": repeats,
            }
        else:
            x = safe_int(self.x_entry.get(), default=0)
            y = safe_int(self.y_entry.get(), default=0)
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
        if not keys or keys in ("Aucune touche capturée", "No key captured"):
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
        if action["type"] == "image":
            image_path = action.get("image_path", "")
            button = "Gauche" if action.get("button") == "left" else "Droit"
            click_type = "Simple" if action.get("click_type") == "single" else "Double"
            retries = int(action.get("retries", 1))
            return f"[Image: {image_path}] | [Bouton: {button}, Type: {click_type}] | [Tentatives: {retries}]"
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
        jitter_min = _safe_float(self.temporal_jitter_min_entry.get(), default=0.008, minimum=0.001)
        jitter_max = _safe_float(self.temporal_jitter_max_entry.get(), default=0.015, minimum=0.001)
        if jitter_min > jitter_max:
            jitter_min, jitter_max = jitter_max, jitter_min

        return {
            "repeat_sequence": self.repeat_seq_var.get(),
            "interval_seconds": safe_int(self.interval_s_entry.get(), default=0, minimum=0),
            "interval_milliseconds": safe_int(self.interval_ms_entry.get(), default=0, minimum=0),
            "humanized_mode": self.humanized_var.get(),
            "humanized_jitter": safe_int(self.jitter_entry.get(), default=3, minimum=0),
            "repeat_delay_seconds": _safe_float(self.repeat_delay_entry.get(), default=0.0, minimum=0.0),
            "temporal_jitter_enabled": self.temporal_jitter_var.get(),
            "temporal_jitter_min": jitter_min,
            "temporal_jitter_max": jitter_max,
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
        self._state.advanced_execution.repeat_delay_seconds = cfg["repeat_delay_seconds"]
        self._state.advanced_execution.temporal_jitter_enabled = cfg["temporal_jitter_enabled"]
        self._state.advanced_execution.temporal_jitter_min = cfg["temporal_jitter_min"]
        self._state.advanced_execution.temporal_jitter_max = cfg["temporal_jitter_max"]
        self._on_save_state()

    def _browse_image(self) -> None:
        image_path = filedialog.askopenfilename(
            title="Sélectionner une image cible",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp"), ("Tous les fichiers", "*.*")],
        )
        if not image_path:
            return
        self.image_path_entry.delete(0, "end")
        self.image_path_entry.insert(0, image_path)
        self.target_mode.set("image")
        self._toggle_target_mode()

    def _toggle_target_mode(self) -> None:
        is_image_mode = self.target_mode.get() == "image"
        state_coords = "disabled" if is_image_mode else "normal"
        state_image = "normal" if is_image_mode else "disabled"

        self.x_entry.configure(state=state_coords)
        self.y_entry.configure(state=state_coords)
        self.pick_btn.configure(state=state_coords)
        self.image_path_entry.configure(state=state_image)
        self.browse_image_btn.configure(state=state_image)

    def _toggle_macro_recording(self) -> None:
        if self._macro_recorder.running:
            self._macro_recorder.stop()
            self.record_macro_btn.configure(text="Enregistrer une macro (F9 pour Stop)")
            self.adv_status.configure(text="Arrêt de l'enregistrement macro demandé")
            return

        self.record_macro_btn.configure(text="Stop enregistrement (F9)")

        def on_action(action: dict) -> None:
            self.after(0, lambda: self._append_recorded_action(action))

        def on_status(message: str) -> None:
            self.after(0, lambda: self._on_macro_status(message))

        self._macro_recorder.start(on_action=on_action, on_status=on_status, stop_key="f9")

    def _append_recorded_action(self, action: dict) -> None:
        self._state.sequence_actions.append(action)
        self.listbox.insert(self._format_action(action))
        self._save_runtime_state()

    def _on_macro_status(self, message: str) -> None:
        self.adv_status.configure(text=message)
        if any(token in message.lower() for token in ("arrêté", "stopped")):
            self.record_macro_btn.configure(text=get_text(self._state.current_language, "record_macro"))

    def update_ui_language(self) -> None:
        lang = self._state.current_language
        self.title(get_text(lang, "advanced_title"))
        self.header_label.configure(text=get_text(lang, "advanced_header"))
        self.mouse_title_label.configure(text=get_text(lang, "advanced_mouse_title"))
        self.target_type_label.configure(text=get_text(lang, "target_type"))
        self.target_coords_radio.configure(text=get_text(lang, "target_coords"))
        self.target_image_radio.configure(text=get_text(lang, "target_image"))
        self.image_file_label.configure(text=get_text(lang, "image_file"))
        self.browse_image_btn.configure(text=get_text(lang, "browse"))
        self.button_label.configure(text=get_text(lang, "button"))
        self.click_type_label.configure(text=get_text(lang, "click_type"))
        self.click_retries_label.configure(text=get_text(lang, "click_count_or_retries"))
        self.add_mouse_btn.configure(text=get_text(lang, "add_mouse_action"))
        self.keyboard_title_label.configure(text=get_text(lang, "advanced_keyboard_title"))
        self.keyboard_help_label.configure(text=get_text(lang, "advanced_keyboard_help"))
        if self.key_preview.get("1.0", "end").strip() in ("Aucune touche capturée", "No key captured"):
            self.key_preview.delete("1.0", "end")
            self.key_preview.insert("1.0", get_text(lang, "no_key_captured"))
        self.record_keys_btn.configure(text=get_text(lang, "record_keys"))
        self.add_key_btn.configure(text=get_text(lang, "add_key_action"))
        self.record_macro_btn.configure(
            text=get_text(lang, "stop_macro") if self._macro_recorder.running else get_text(lang, "record_macro")
        )
        self.sequence_title_label.configure(text=get_text(lang, "sequence_title"))
        self.delete_action_btn.configure(text=get_text(lang, "delete_action"))
        self.clear_actions_btn.configure(text=get_text(lang, "clear_all"))
        self.execution_title_label.configure(text=get_text(lang, "execution_settings"))
        self.repeat_seq_checkbox.configure(text=get_text(lang, "repeat_sequence"))
        self.humanized_checkbox.configure(text=get_text(lang, "humanized_mode"))
        self.interval_actions_label.configure(text=get_text(lang, "interval_between_actions"))
        self.pixel_jitter_label.configure(text=get_text(lang, "pixel_jitter"))
        self.repeat_delay_label.configure(text=get_text(lang, "repeat_delay"))
        self.temporal_jitter_checkbox.configure(text=get_text(lang, "temporal_jitter"))
        self.min_label.configure(text=get_text(lang, "min_seconds"))
        self.max_label.configure(text=get_text(lang, "max_seconds"))
        self.start_advanced_btn.configure(text=get_text(lang, "start_advanced"))
        self.stop_advanced_btn.configure(text=get_text(lang, "stop_advanced"))
        self.history_title_label.configure(text=get_text(lang, "history_realtime"))

        if lang == "fr":
            self.mouse_button.configure(values=["Gauche", "Droit"])
            self.click_type.configure(values=["Simple", "Double"])
        else:
            self.mouse_button.configure(values=["Left", "Right"])
            self.click_type.configure(values=["Single", "Double"])

    def destroy(self) -> None:
        if self._macro_recorder.running:
            self._macro_recorder.stop()
        super().destroy()


def _safe_float(value: str, default: float = 0.0, minimum: float | None = None) -> float:
    try:
        number = float(value.strip())
    except (ValueError, AttributeError):
        return default

    if minimum is not None:
        return max(number, minimum)
    return number
