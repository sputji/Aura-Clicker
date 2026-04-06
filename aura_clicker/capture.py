from __future__ import annotations

import threading
from typing import Callable

from pynput import mouse
import keyboard


def capture_mouse_position(on_captured: Callable[[int, int], None]) -> None:
    def _run_listener() -> None:
        def on_click(x: int, y: int, button, pressed: bool) -> bool:
            if pressed:
                on_captured(int(x), int(y))
                return False
            return True

        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

    threading.Thread(target=_run_listener, daemon=True).start()


def capture_hotkey_combination(on_captured: Callable[[str], None]) -> None:
    def _capture() -> None:
        combo = keyboard.read_hotkey(suppress=False)
        on_captured(combo.upper())

    threading.Thread(target=_capture, daemon=True).start()
