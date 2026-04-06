from __future__ import annotations

from typing import Callable

import keyboard


class GlobalHotkeyManager:
    def __init__(self) -> None:
        self._handlers: list[int] = []

    def register(self, hotkeys: dict[str, str], callbacks: dict[str, Callable[[], None]]) -> None:
        self.unregister_all()

        for action, hotkey in hotkeys.items():
            callback = callbacks.get(action)
            if not callback or not hotkey:
                continue
            try:
                handle = keyboard.add_hotkey(
                    hotkey.lower(),
                    callback,
                    suppress=False,
                    trigger_on_release=False,
                )
            except Exception:
                continue
            self._handlers.append(handle)

    def unregister_all(self) -> None:
        for handle in self._handlers:
            keyboard.remove_hotkey(handle)
        self._handlers.clear()
