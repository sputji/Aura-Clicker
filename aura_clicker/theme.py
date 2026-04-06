from __future__ import annotations

from pathlib import Path

import customtkinter as ctk


def apply_aura_theme(base_dir: Path) -> None:
    theme_path = base_dir / "aura_clicker" / "assets" / "aura_neo_theme.json"
    if theme_path.exists():
        ctk.set_default_color_theme(str(theme_path))
    else:
        ctk.set_default_color_theme("blue")

    ctk.set_appearance_mode("System")
