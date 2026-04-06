from __future__ import annotations

import threading
import time
from typing import Callable

from pynput import keyboard, mouse


class MacroRecorder:
    def __init__(self) -> None:
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._mouse_listener: mouse.Listener | None = None
        self._keyboard_listener: keyboard.Listener | None = None

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(
        self,
        on_action: Callable[[dict], None],
        on_status: Callable[[str], None],
        stop_key: str = "f9",
    ) -> None:
        if self.running:
            return

        self._stop_event.clear()

        def _runner() -> None:
            start_ts = time.time()

            def _elapsed() -> float:
                return round(time.time() - start_ts, 4)

            def on_click(x: int, y: int, button: mouse.Button, pressed: bool) -> None:
                if not pressed or self._stop_event.is_set():
                    return
                payload = {
                    "type": "mouse",
                    "coords": (int(x), int(y)),
                    "button": "right" if button == mouse.Button.right else "left",
                    "click_type": "single",
                    "repeats": 1,
                    "timestamp": _elapsed(),
                    "source": "macro_record",
                }
                on_action(payload)

            def on_press(key: keyboard.Key | keyboard.KeyCode):
                if self._stop_event.is_set():
                    return False

                key_text = _key_to_text(key)
                if not key_text:
                    return True

                if key_text.lower() == stop_key.lower():
                    self._stop_event.set()
                    return False

                payload = {
                    "type": "keyboard",
                    "keys": key_text.lower(),
                    "timestamp": _elapsed(),
                    "source": "macro_record",
                }
                on_action(payload)
                return True

            self._mouse_listener = mouse.Listener(on_click=on_click)
            self._keyboard_listener = keyboard.Listener(on_press=on_press)
            self._mouse_listener.start()
            self._keyboard_listener.start()
            on_status("Enregistrement macro en cours... Appuyez sur F9 pour arrêter")

            while not self._stop_event.wait(0.1):
                time.sleep(0.02)

            if self._mouse_listener is not None:
                self._mouse_listener.stop()
                self._mouse_listener = None
            if self._keyboard_listener is not None:
                self._keyboard_listener.stop()
                self._keyboard_listener = None
            on_status("Enregistrement macro arrêté")

        self._thread = threading.Thread(target=_runner, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()


def _key_to_text(key: keyboard.Key | keyboard.KeyCode) -> str:
    if isinstance(key, keyboard.KeyCode):
        if key.char:
            return key.char
        return ""

    key_name_map = {
        keyboard.Key.space: "space",
        keyboard.Key.enter: "enter",
        keyboard.Key.tab: "tab",
        keyboard.Key.backspace: "backspace",
        keyboard.Key.esc: "esc",
        keyboard.Key.up: "up",
        keyboard.Key.down: "down",
        keyboard.Key.left: "left",
        keyboard.Key.right: "right",
        keyboard.Key.f1: "f1",
        keyboard.Key.f2: "f2",
        keyboard.Key.f3: "f3",
        keyboard.Key.f4: "f4",
        keyboard.Key.f5: "f5",
        keyboard.Key.f6: "f6",
        keyboard.Key.f7: "f7",
        keyboard.Key.f8: "f8",
        keyboard.Key.f9: "f9",
        keyboard.Key.f10: "f10",
        keyboard.Key.f11: "f11",
        keyboard.Key.f12: "f12",
    }
    return key_name_map.get(key, "")
