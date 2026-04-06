from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any

from .constants import DEFAULT_HOTKEYS, SETTINGS_FILE_NAME


@dataclass
class MainClickSettings:
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    milliseconds: int = 1
    infinite: bool = True
    repeat_count: int = 1
    current_position: bool = True
    x: int = 0
    y: int = 0
    mouse_button: str = "left"
    click_type: str = "single"
    always_on_top: bool = False
    temporal_jitter_enabled: bool = False
    temporal_jitter_min: float = 0.008
    temporal_jitter_max: float = 0.015


@dataclass
class AdvancedExecutionSettings:
    repeat_sequence: bool = False
    repeat_delay_seconds: float = 0.0
    interval_seconds: int = 1
    interval_milliseconds: int = 0
    humanized_mode: bool = True
    humanized_jitter: int = 3
    temporal_jitter_enabled: bool = False
    temporal_jitter_min: float = 0.008
    temporal_jitter_max: float = 0.015


@dataclass
class KeyPresserSettings:
    key_name: str = ""
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    milliseconds: int = 1000
    infinite: bool = True
    repeat_count: int = 1
    hold_key_down: bool = False
    hold_duration_ms: int = 100


@dataclass
class AppState:
    main_click: MainClickSettings = field(default_factory=MainClickSettings)
    advanced_execution: AdvancedExecutionSettings = field(default_factory=AdvancedExecutionSettings)
    key_presser: KeyPresserSettings = field(default_factory=KeyPresserSettings)
    sequence_actions: list[dict[str, Any]] = field(default_factory=list)
    hotkeys: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_HOTKEYS))
    current_language: str = "fr"


class SettingsStore:
    def __init__(self, base_dir: Path) -> None:
        self.file_path = base_dir / SETTINGS_FILE_NAME

    def load(self) -> AppState:
        if not self.file_path.exists():
            return AppState()

        try:
            payload = json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return AppState()

        main_click = self._safe_dataclass_load(MainClickSettings, payload.get("main_click", {}))
        advanced_execution = self._safe_dataclass_load(
            AdvancedExecutionSettings,
            payload.get("advanced_execution", {}),
        )
        key_presser = self._safe_dataclass_load(KeyPresserSettings, payload.get("key_presser", {}))

        sequence_actions = payload.get("sequence_actions", [])
        if not isinstance(sequence_actions, list):
            sequence_actions = []

        hotkeys = payload.get("hotkeys", {})
        if not isinstance(hotkeys, dict):
            hotkeys = {}

        return AppState(
            main_click=main_click,
            advanced_execution=advanced_execution,
            key_presser=key_presser,
            sequence_actions=sequence_actions,
            hotkeys={**DEFAULT_HOTKEYS, **hotkeys},
            current_language=str(payload.get("current_language", "fr") or "fr"),
        )

    def save(self, state: AppState) -> None:
        payload = {
            "main_click": asdict(state.main_click),
            "advanced_execution": asdict(state.advanced_execution),
            "key_presser": asdict(state.key_presser),
            "sequence_actions": state.sequence_actions,
            "hotkeys": state.hotkeys,
            "current_language": state.current_language,
        }
        self.file_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def _safe_dataclass_load(cls, payload: Any):
        if not isinstance(payload, dict):
            return cls()

        allowed = set(cls.__dataclass_fields__)
        filtered = {k: v for k, v in payload.items() if k in allowed}
        return cls(**filtered)
