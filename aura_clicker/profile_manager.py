from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .app_state import AppState
from .constants import PROFILE_EXTENSION


class ProfileManager:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.default_profile_path = self.base_dir / f"default{PROFILE_EXTENSION}"

    def export_profile(self, state: AppState, profile_path: Path | None = None) -> Path:
        target = profile_path or self.default_profile_path
        payload = {
            "meta": {
                "name": "Aura-Clicker Profile",
                "version": "0.1.1",
            },
            "main_click": asdict(state.main_click),
            "advanced_execution": asdict(state.advanced_execution),
            "key_presser": asdict(state.key_presser),
            "sequence_actions": state.sequence_actions,
            "hotkeys": state.hotkeys,
        }
        target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return target

    def import_profile(self, profile_path: Path | None = None) -> dict:
        source = profile_path or self.default_profile_path
        payload = json.loads(source.read_text(encoding="utf-8"))
        return payload
