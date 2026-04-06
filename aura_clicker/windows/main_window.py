from __future__ import annotations

import customtkinter as ctk

from ..capture import capture_mouse_position
from ..translations import format_text, get_text
from ..utils import safe_int


def _safe_float(value: str, default: float = 0.0, minimum: float | None = None) -> float:
    try:
        number = float(value.strip())
    except (ValueError, AttributeError):
        return default

    if minimum is not None:
        return max(number, minimum)
    return number


class MainWindow(ctk.CTkFrame):
    def __init__(
        self,
        master,
        state,
        on_start,
        on_stop,
        on_toggle,
        on_save,
        on_export_profile,
        on_import_profile,
        on_open_hotkeys,
        on_open_key_presser,
        on_open_advanced,
        on_language_change,
    ):
        super().__init__(master)
        self._state = state
        self._on_start = on_start
        self._on_stop = on_stop
        self._on_toggle = on_toggle
        self._on_save = on_save
        self._on_export_profile = on_export_profile
        self._on_import_profile = on_import_profile
        self._on_open_hotkeys = on_open_hotkeys
        self._on_open_key_presser = on_open_key_presser
        self._on_open_advanced = on_open_advanced
        self._on_language_change = on_language_change

        self.pack(fill="both", expand=True, padx=14, pady=12)

        self._build_ui()
        self._load_state()

    def _build_ui(self) -> None:
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(7, weight=1)

        interval_frame = ctk.CTkFrame(self)
        interval_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        self.interval_title_label = ctk.CTkLabel(interval_frame, text="", font=ctk.CTkFont(size=18, weight="bold"))
        self.interval_title_label.grid(row=0, column=0, columnspan=6, sticky="w", padx=14, pady=(12, 8))

        self.language_label = ctk.CTkLabel(interval_frame, text="")
        self.language_label.grid(row=0, column=6, sticky="e", padx=(6, 4), pady=(12, 8))
        self.language_menu = ctk.CTkOptionMenu(
            interval_frame,
            values=["Français", "English"],
            width=120,
            command=self._on_language_selected,
        )
        self.language_menu.grid(row=0, column=7, sticky="e", padx=(0, 14), pady=(12, 8))

        self.hours_label = ctk.CTkLabel(interval_frame, text="")
        self.hours_label.grid(row=1, column=0, padx=(14, 4), pady=(0, 12))
        self.h_entry = self._int_entry(interval_frame, 1, 1)

        self.minutes_label = ctk.CTkLabel(interval_frame, text="")
        self.minutes_label.grid(row=1, column=2, padx=(6, 4), pady=(0, 12))
        self.m_entry = self._int_entry(interval_frame, 1, 3)

        self.seconds_label = ctk.CTkLabel(interval_frame, text="")
        self.seconds_label.grid(row=1, column=4, padx=(6, 4), pady=(0, 12))
        self.s_entry = self._int_entry(interval_frame, 1, 5)

        self.milliseconds_label = ctk.CTkLabel(interval_frame, text="")
        self.milliseconds_label.grid(row=1, column=6, padx=(6, 4), pady=(0, 12))
        self.ms_entry = self._int_entry(interval_frame, 1, 7)

        repeat_frame = ctk.CTkFrame(self)
        repeat_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=8)

        self.repeat_title_label = ctk.CTkLabel(repeat_frame, text="", font=ctk.CTkFont(size=18, weight="bold"))
        self.repeat_title_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 8))

        self.repeat_mode = ctk.StringVar(value="infinite")
        self.repeat_infinite_radio = ctk.CTkRadioButton(repeat_frame, text="", variable=self.repeat_mode, value="infinite")
        self.repeat_infinite_radio.grid(row=1, column=0, sticky="w", padx=14, pady=4)
        self.repeat_count_radio = ctk.CTkRadioButton(repeat_frame, text="", variable=self.repeat_mode, value="count")
        self.repeat_count_radio.grid(row=2, column=0, sticky="w", padx=14, pady=4)
        self.repeat_count_entry = ctk.CTkEntry(repeat_frame, width=110)
        self.repeat_count_entry.grid(row=2, column=1, sticky="w", padx=8, pady=4)

        pos_frame = ctk.CTkFrame(self)
        pos_frame.grid(row=1, column=1, sticky="nsew", padx=(6, 0), pady=8)
        pos_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.position_title_label = ctk.CTkLabel(pos_frame, text="", font=ctk.CTkFont(size=18, weight="bold"))
        self.position_title_label.grid(row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(12, 8))

        self.pos_mode = ctk.StringVar(value="current")
        self.current_position_radio = ctk.CTkRadioButton(pos_frame, text="", variable=self.pos_mode, value="current")
        self.current_position_radio.grid(row=1, column=0, columnspan=2, sticky="w", padx=14, pady=4)
        self.specific_position_radio = ctk.CTkRadioButton(pos_frame, text="", variable=self.pos_mode, value="specific")
        self.specific_position_radio.grid(row=2, column=0, columnspan=2, sticky="w", padx=14, pady=4)

        ctk.CTkLabel(pos_frame, text="X").grid(row=2, column=2, sticky="e", padx=(0, 4))
        self.x_entry = ctk.CTkEntry(pos_frame, width=100)
        self.x_entry.grid(row=2, column=3, sticky="w", padx=(0, 6), pady=4)

        ctk.CTkLabel(pos_frame, text="Y").grid(row=3, column=2, sticky="e", padx=(0, 4))
        self.y_entry = ctk.CTkEntry(pos_frame, width=100)
        self.y_entry.grid(row=3, column=3, sticky="w", padx=(0, 6), pady=4)

        self.pick_btn = ctk.CTkButton(pos_frame, text="◎", width=52, command=self._capture_target)
        self.pick_btn.grid(row=3, column=0, padx=14, pady=(4, 12), sticky="w")

        options_frame = ctk.CTkFrame(self)
        options_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=8)
        options_frame.grid_columnconfigure((0, 1), weight=1)

        self.options_title_label = ctk.CTkLabel(options_frame, text="", font=ctk.CTkFont(size=18, weight="bold"))
        self.options_title_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 8))

        self.button_label = ctk.CTkLabel(options_frame, text="")
        self.button_label.grid(row=1, column=0, sticky="w", padx=14)
        self.mouse_button = ctk.CTkComboBox(options_frame, values=["Gauche", "Droit"])
        self.mouse_button.grid(row=2, column=0, sticky="ew", padx=14, pady=(4, 12))

        self.click_type_label = ctk.CTkLabel(options_frame, text="")
        self.click_type_label.grid(row=1, column=1, sticky="w", padx=14)
        self.click_type = ctk.CTkComboBox(options_frame, values=["Simple", "Double"])
        self.click_type.grid(row=2, column=1, sticky="ew", padx=14, pady=(4, 12))

        self.temporal_jitter_var = ctk.BooleanVar(value=False)
        self.temporal_jitter_checkbox = ctk.CTkCheckBox(options_frame, text="", variable=self.temporal_jitter_var)
        self.temporal_jitter_checkbox.grid(row=3, column=0, sticky="w", padx=14, pady=(0, 8))

        self.humanized_var = ctk.BooleanVar(value=False)
        self.humanized_checkbox = ctk.CTkCheckBox(options_frame, text="", variable=self.humanized_var)
        self.humanized_checkbox.grid(row=4, column=0, sticky="w", padx=14, pady=(0, 8))

        humanized_row = ctk.CTkFrame(options_frame, fg_color="transparent")
        humanized_row.grid(row=5, column=0, sticky="w", padx=14, pady=(0, 12))
        self.main_pixel_jitter_label = ctk.CTkLabel(humanized_row, text="")
        self.main_pixel_jitter_label.pack(side="left", padx=(0, 6))
        self.main_jitter_entry = ctk.CTkEntry(humanized_row, width=95)
        self.main_jitter_entry.pack(side="left")

        min_row = ctk.CTkFrame(options_frame, fg_color="transparent")
        min_row.grid(row=3, column=1, sticky="ew", padx=14, pady=(0, 8))
        self.min_seconds_label = ctk.CTkLabel(min_row, text="")
        self.min_seconds_label.pack(side="left", padx=(0, 6))
        self.temporal_jitter_min_entry = ctk.CTkEntry(min_row, width=95)
        self.temporal_jitter_min_entry.pack(side="left")

        max_row = ctk.CTkFrame(options_frame, fg_color="transparent")
        max_row.grid(row=5, column=1, sticky="ew", padx=14, pady=(0, 12))
        self.max_seconds_label = ctk.CTkLabel(max_row, text="")
        self.max_seconds_label.pack(side="left", padx=(0, 6))
        self.temporal_jitter_max_entry = ctk.CTkEntry(max_row, width=95)
        self.temporal_jitter_max_entry.pack(side="left")

        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=8)
        controls_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.start_btn = ctk.CTkButton(controls_frame, text="", fg_color="#10B981", hover_color="#059669", command=self._start)
        self.start_btn.grid(row=0, column=0, padx=8, pady=12, sticky="ew")

        self.stop_btn = ctk.CTkButton(controls_frame, text="", fg_color="#64748B", hover_color="#475569", command=self._stop)
        self.stop_btn.grid(row=0, column=1, padx=8, pady=12, sticky="ew")

        self.toggle_btn = ctk.CTkButton(controls_frame, text="", fg_color="#4F46E5", hover_color="#4338CA", command=self._toggle)
        self.toggle_btn.grid(row=0, column=2, padx=8, pady=12, sticky="ew")

        utils_frame = ctk.CTkFrame(self)
        utils_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=8)
        utils_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.save_settings_btn = ctk.CTkButton(utils_frame, text="", command=self._save_state)
        self.save_settings_btn.grid(row=0, column=0, padx=8, pady=12, sticky="ew")
        self.open_hotkeys_btn = ctk.CTkButton(utils_frame, text="", command=self._on_open_hotkeys)
        self.open_hotkeys_btn.grid(row=0, column=1, padx=8, pady=12, sticky="ew")
        self.export_btn = ctk.CTkButton(utils_frame, text="", command=self._export_profile)
        self.export_btn.grid(row=0, column=2, padx=8, pady=12, sticky="ew")
        self.import_btn = ctk.CTkButton(utils_frame, text="", command=self._import_profile)
        self.import_btn.grid(row=0, column=3, padx=8, pady=12, sticky="ew")

        self.topmost_var = ctk.BooleanVar(value=False)
        self.topmost_checkbox = ctk.CTkCheckBox(utils_frame, text="", variable=self.topmost_var, command=self._toggle_topmost)
        self.topmost_checkbox.grid(row=0, column=4, padx=8, pady=12, sticky="w")

        nav_frame = ctk.CTkFrame(self)
        nav_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(8, 2))
        nav_frame.grid_columnconfigure((0, 1), weight=1)

        self.open_key_presser_btn = ctk.CTkButton(nav_frame, text="", command=self._on_open_key_presser)
        self.open_key_presser_btn.grid(row=0, column=0, padx=8, pady=12, sticky="ew")
        self.open_advanced_btn = ctk.CTkButton(nav_frame, text="", fg_color="#4F46E5", hover_color="#4338CA", command=self._on_open_advanced)
        self.open_advanced_btn.grid(row=0, column=1, padx=8, pady=12, sticky="ew")

        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.status_title_label = ctk.CTkLabel(status_frame, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.status_title_label.pack(anchor="w", padx=12, pady=(10, 4))
        self.status_label = ctk.CTkLabel(status_frame, text="")
        self.status_label.pack(anchor="w", padx=12, pady=(0, 10))

        history_frame = ctk.CTkFrame(self)
        history_frame.grid(row=7, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
        self.history_title_label = ctk.CTkLabel(history_frame, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.history_title_label.pack(anchor="w", padx=12, pady=(10, 6))
        self.history_box = ctk.CTkTextbox(history_frame, height=150)
        self.history_box.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self.update_ui_language()

    def _int_entry(self, parent, row, column):
        entry = ctk.CTkEntry(parent, width=90, justify="center")
        entry.grid(row=row, column=column, pady=(0, 12), padx=4)
        return entry

    def _load_state(self) -> None:
        self.h_entry.delete(0, "end")
        self.m_entry.delete(0, "end")
        self.s_entry.delete(0, "end")
        self.ms_entry.delete(0, "end")
        self.repeat_count_entry.delete(0, "end")
        self.x_entry.delete(0, "end")
        self.y_entry.delete(0, "end")
        self.temporal_jitter_min_entry.delete(0, "end")
        self.temporal_jitter_max_entry.delete(0, "end")
        self.main_jitter_entry.delete(0, "end")

        data = self._state.main_click
        lang = self._state.current_language
        self.h_entry.insert(0, str(data.hours))
        self.m_entry.insert(0, str(data.minutes))
        self.s_entry.insert(0, str(data.seconds))
        self.ms_entry.insert(0, str(data.milliseconds))
        self.repeat_mode.set("infinite" if data.infinite else "count")
        self.repeat_count_entry.insert(0, str(data.repeat_count))
        self.pos_mode.set("current" if data.current_position else "specific")
        self.x_entry.insert(0, str(data.x))
        self.y_entry.insert(0, str(data.y))
        if lang == "fr":
            self.mouse_button.set("Gauche" if data.mouse_button == "left" else "Droit")
            self.click_type.set("Simple" if data.click_type == "single" else "Double")
        else:
            self.mouse_button.set("Left" if data.mouse_button == "left" else "Right")
            self.click_type.set("Single" if data.click_type == "single" else "Double")
        self.temporal_jitter_var.set(data.temporal_jitter_enabled)
        self.temporal_jitter_min_entry.insert(0, str(data.temporal_jitter_min))
        self.temporal_jitter_max_entry.insert(0, str(data.temporal_jitter_max))
        self.humanized_var.set(bool(getattr(data, "humanized_mode", False)))
        self.main_jitter_entry.insert(0, str(int(getattr(data, "humanized_jitter", 3))))
        self.topmost_var.set(data.always_on_top)
        self._toggle_topmost()
        self.update_ui_language()

    def refresh_from_state(self) -> None:
        self._load_state()

    def _capture_target(self) -> None:
        self._set_status(format_text(self._state.current_language, "status_capture_position"))

        def on_captured(x: int, y: int) -> None:
            self.after(0, lambda: self._apply_captured_position(x, y))

        capture_mouse_position(on_captured)

    def _apply_captured_position(self, x: int, y: int) -> None:
        self.x_entry.delete(0, "end")
        self.y_entry.delete(0, "end")
        self.x_entry.insert(0, str(x))
        self.y_entry.insert(0, str(y))
        self._set_status(format_text(self._state.current_language, "status_coordinates_captured", x=x, y=y))

    def _build_click_config(self) -> dict:
        jitter_min = _safe_float(self.temporal_jitter_min_entry.get(), default=0.008, minimum=0.001)
        jitter_max = _safe_float(self.temporal_jitter_max_entry.get(), default=0.015, minimum=0.001)
        if jitter_min > jitter_max:
            jitter_min, jitter_max = jitter_max, jitter_min

        return {
            "hours": safe_int(self.h_entry.get(), minimum=0),
            "minutes": safe_int(self.m_entry.get(), minimum=0),
            "seconds": safe_int(self.s_entry.get(), minimum=0),
            "milliseconds": safe_int(self.ms_entry.get(), default=1, minimum=1),
            "infinite": self.repeat_mode.get() == "infinite",
            "repeat_count": safe_int(self.repeat_count_entry.get(), default=1, minimum=1),
            "current_position": self.pos_mode.get() == "current",
            "x": safe_int(self.x_entry.get(), default=0),
            "y": safe_int(self.y_entry.get(), default=0),
            "mouse_button": "left" if self.mouse_button.get() in ("Gauche", "Left") else "right",
            "click_type": "single" if self.click_type.get() in ("Simple", "Single") else "double",
            "temporal_jitter_enabled": self.temporal_jitter_var.get(),
            "temporal_jitter_min": jitter_min,
            "temporal_jitter_max": jitter_max,
            "humanized_mode": self.humanized_var.get(),
            "humanized_jitter": safe_int(self.main_jitter_entry.get(), default=3, minimum=0),
            "language": self._state.current_language,
        }

    def _start(self) -> None:
        config = self._build_click_config()
        self._on_start(config, self._set_status)

    def _stop(self) -> None:
        self._on_stop()
        self._set_status(format_text(self._state.current_language, "status_main_stopped"))

    def _toggle(self) -> None:
        config = self._build_click_config()
        self._on_toggle(config, self._set_status)

    def _toggle_topmost(self) -> None:
        self.winfo_toplevel().attributes("-topmost", bool(self.topmost_var.get()))

    def _save_state(self) -> None:
        config = self._build_click_config()
        self._on_save(config, bool(self.topmost_var.get()))
        self._set_status(format_text(self._state.current_language, "status_settings_saved"))

    def _export_profile(self) -> None:
        self._on_export_profile()

    def _import_profile(self) -> None:
        self._on_import_profile()

    def append_history(self, line: str) -> None:
        def _append() -> None:
            self.history_box.insert("1.0", line + "\n")

        self.after(0, _append)

    def set_history(self, items: list[str]) -> None:
        self.history_box.delete("1.0", "end")
        if items:
            self.history_box.insert("1.0", "\n".join(items) + "\n")

    def _set_status(self, message: str) -> None:
        self.after(0, lambda: self.status_label.configure(text=message))

    def update_ui_language(self) -> None:
        lang = self._state.current_language
        display = "Français" if lang == "fr" else "English"
        self.language_menu.set(display)

        self.language_label.configure(text=get_text(lang, "language"))
        self.interval_title_label.configure(text=get_text(lang, "main_interval_title"))
        self.hours_label.configure(text=get_text(lang, "hours"))
        self.minutes_label.configure(text=get_text(lang, "minutes"))
        self.seconds_label.configure(text=get_text(lang, "seconds"))
        self.milliseconds_label.configure(text=get_text(lang, "milliseconds"))
        self.repeat_title_label.configure(text=get_text(lang, "main_repeat_title"))
        self.repeat_infinite_radio.configure(text=get_text(lang, "infinite"))
        self.repeat_count_radio.configure(text=get_text(lang, "repeat_count"))
        self.position_title_label.configure(text=get_text(lang, "main_position_title"))
        self.current_position_radio.configure(text=get_text(lang, "current_position"))
        self.specific_position_radio.configure(text=get_text(lang, "specific_position"))
        self.options_title_label.configure(text=get_text(lang, "main_options_title"))
        self.button_label.configure(text=get_text(lang, "button"))
        self.click_type_label.configure(text=get_text(lang, "click_type"))
        self.temporal_jitter_checkbox.configure(text=get_text(lang, "temporal_jitter"))
        self.humanized_checkbox.configure(text=get_text(lang, "humanized_main_mode"))
        self.main_pixel_jitter_label.configure(text=get_text(lang, "pixel_jitter"))
        self.min_seconds_label.configure(text=get_text(lang, "min_seconds"))
        self.max_seconds_label.configure(text=get_text(lang, "max_seconds"))

        self.mouse_button.configure(values=["Gauche", "Droit"] if lang == "fr" else ["Left", "Right"])
        self.click_type.configure(values=["Simple", "Double"] if lang == "fr" else ["Single", "Double"])

        self.start_btn.configure(text=get_text(lang, "start_main"))
        self.stop_btn.configure(text=get_text(lang, "stop_main"))
        self.toggle_btn.configure(text=get_text(lang, "toggle_main"))
        self.save_settings_btn.configure(text=get_text(lang, "save_settings"))
        self.open_hotkeys_btn.configure(text=get_text(lang, "hotkeys"))
        self.export_btn.configure(text=get_text(lang, "export_profile"))
        self.import_btn.configure(text=get_text(lang, "import_profile"))
        self.topmost_checkbox.configure(text=get_text(lang, "always_on_top"))
        self.open_key_presser_btn.configure(text=get_text(lang, "open_key_presser"))
        self.open_advanced_btn.configure(text=get_text(lang, "open_advanced"))
        self.status_title_label.configure(text=get_text(lang, "status"))
        self.history_title_label.configure(text=get_text(lang, "history_live"))
        if not self.status_label.cget("text"):
            self.status_label.configure(text=get_text(lang, "ready"))

    def _on_language_selected(self, selection: str) -> None:
        language = "en" if selection == "English" else "fr"
        if language == self._state.current_language:
            return
        self._state.current_language = language
        self.update_ui_language()
        self._on_language_change(language)
