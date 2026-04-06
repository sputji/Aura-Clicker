from __future__ import annotations

from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Callable

from .constants import HISTORY_FILE_NAME


class ActionHistory:
    def __init__(self, base_dir: Path, max_items: int = 250) -> None:
        self._max_items = max_items
        self._events: deque[str] = deque(maxlen=max_items)
        self._listeners: list[Callable[[str], None]] = []
        self._log_path = base_dir / HISTORY_FILE_NAME

    def subscribe(self, listener: Callable[[str], None]) -> None:
        self._listeners.append(listener)

    def get_events(self) -> list[str]:
        return list(self._events)

    def push(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}"
        self._events.appendleft(line)
        try:
            with self._log_path.open("a", encoding="utf-8") as fp:
                fp.write(line + "\n")
        except OSError:
            pass

        for listener in self._listeners:
            listener(line)
