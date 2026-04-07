from __future__ import annotations

import random
import threading
import time
from typing import Callable

import keyboard
import pyautogui

from .structured_error_logger import get_structured_logger
from .translations import format_text
from .utils import interval_to_seconds


pyautogui.FAILSAFE = True


class BaseWorker:
    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def stop(self) -> None:
        self._stop_event.set()

    def _start_thread(self, target: Callable[[], None]) -> None:
        if self.running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=target, daemon=True)
        self._thread.start()


class ClickWorker(BaseWorker):
    def start(
        self,
        config: dict,
        on_status: Callable[[str], None],
        on_action: Callable[[str], None] | None = None,
    ) -> None:
        def _loop() -> None:
            try:
                language = str(config.get("language", "fr"))
                interval = interval_to_seconds(
                    config["hours"],
                    config["minutes"],
                    config["seconds"],
                    config["milliseconds"],
                )
                mouse_button = config["mouse_button"]
                clicks_per_action = 2 if config["click_type"] == "double" else 1
                infinite = config["infinite"]
                remaining = max(1, config["repeat_count"])
                temporal_jitter_enabled = bool(config.get("temporal_jitter_enabled", False))
                temporal_jitter_min = float(config.get("temporal_jitter_min", 0.008))
                temporal_jitter_max = float(config.get("temporal_jitter_max", 0.015))
                humanized_mode = bool(config.get("humanized_mode", False))
                humanized_jitter = max(0, int(config.get("humanized_jitter", 3)))
                if temporal_jitter_min > temporal_jitter_max:
                    temporal_jitter_min, temporal_jitter_max = temporal_jitter_max, temporal_jitter_min

                on_status(format_text(language, "worker_click_running"))
                if on_action:
                    on_action(format_text(language, "worker_click_started"))
                    # Log des paramètres actifs
                    mode_info = []
                    if humanized_mode:
                        mode_info.append(f"Humanisé: ±{humanized_jitter}px")
                    if temporal_jitter_enabled:
                        mode_info.append(f"Jitter temporel: +{temporal_jitter_min:.3f}s-{temporal_jitter_max:.3f}s")
                    if mode_info:
                        on_action(f"Modes actifs: {', '.join(mode_info)}")
                while not self._stop_event.is_set() and (infinite or remaining > 0):
                    if config["current_position"]:
                        if humanized_mode and humanized_jitter > 0:
                            base_x, base_y = pyautogui.position()
                            pyautogui.moveTo(
                                base_x + random.randint(-humanized_jitter, humanized_jitter),
                                base_y + random.randint(-humanized_jitter, humanized_jitter),
                            )
                    else:
                        target_x = int(config["x"])
                        target_y = int(config["y"])
                        if humanized_mode and humanized_jitter > 0:
                            target_x += random.randint(-humanized_jitter, humanized_jitter)
                            target_y += random.randint(-humanized_jitter, humanized_jitter)
                        pyautogui.moveTo(target_x, target_y)

                    pyautogui.click(button=mouse_button, clicks=clicks_per_action)
                    if on_action:
                        if config["current_position"]:
                            on_action(
                                format_text(
                                    language,
                                    "worker_click_done_here",
                                    button=mouse_button,
                                    count=clicks_per_action,
                                )
                            )
                        else:
                            on_action(format_text(language, "worker_click_done_xy", button=mouse_button, count=clicks_per_action, x=config["x"], y=config["y"]))

                    if not infinite:
                        remaining -= 1

                    wait_delay = interval
                    if temporal_jitter_enabled:
                        wait_delay += random.uniform(temporal_jitter_min, temporal_jitter_max)

                    if self._stop_event.wait(max(0.001, wait_delay)):
                        break
            except Exception as exc:
                logger = get_structured_logger()
                if logger:
                    logger.log_exception(
                        "automation_workers.py",
                        exc,
                        context={"worker": "ClickWorker", "config": config},
                    )
                on_status(format_text(language, "worker_click_error", error=str(exc)))
                if on_action:
                    on_action(format_text(language, "worker_click_error", error=str(exc)))
            finally:
                on_status(format_text(language, "worker_click_stopped"))
                if on_action:
                    on_action(format_text(language, "worker_click_stopped"))

        self._start_thread(_loop)


class KeyPresserWorker(BaseWorker):
    def start(
        self,
        config: dict,
        on_status: Callable[[str], None],
        on_action: Callable[[str], None] | None = None,
    ) -> None:
        def _loop() -> None:
            try:
                language = str(config.get("language", "fr"))
                interval = interval_to_seconds(
                    config["hours"],
                    config["minutes"],
                    config["seconds"],
                    config["milliseconds"],
                )
                infinite = config["infinite"]
                remaining = max(1, config["repeat_count"])
                key_name = config["key_name"]
                hold_key = config["hold_key_down"]
                hold_duration = max(0.01, config["hold_duration_ms"] / 1000)

                if not key_name:
                    on_status(format_text(language, "worker_key_no_selection"))
                    return

                on_status(format_text(language, "worker_key_running", key_name=key_name))
                if on_action:
                    on_action(format_text(language, "worker_key_started", key_name=key_name))
                while not self._stop_event.is_set() and (infinite or remaining > 0):
                    if hold_key:
                        keyboard.press(key_name)
                        if self._stop_event.wait(hold_duration):
                            keyboard.release(key_name)
                            break
                        keyboard.release(key_name)
                    else:
                        keyboard.send(key_name)

                    if on_action:
                        on_action(format_text(language, "worker_key_executed", key_name=key_name))

                    if not infinite:
                        remaining -= 1

                    if self._stop_event.wait(interval):
                        break
            except Exception as exc:
                logger = get_structured_logger()
                if logger:
                    logger.log_exception(
                        "automation_workers.py",
                        exc,
                        context={"worker": "KeyPresserWorker", "config": config},
                    )
                on_status(format_text(language, "worker_key_error", error=str(exc)))
                if on_action:
                    on_action(format_text(language, "worker_key_error", error=str(exc)))
            finally:
                on_status(format_text(language, "worker_key_stopped"))
                if on_action:
                    on_action(format_text(language, "worker_key_stopped"))

        self._start_thread(_loop)


class SequenceWorker(BaseWorker):
    def start(
        self,
        config: dict,
        sequence: list[dict],
        on_status: Callable[[str], None],
        on_action: Callable[[str], None] | None = None,
    ) -> None:
        def _run_sequence() -> None:
            try:
                language = str(config.get("language", "fr"))
                if not sequence:
                    on_status(format_text(language, "worker_seq_empty"))
                    return

                # Parse interval values with proper type conversion
                interval_sec = float(config.get("interval_seconds", 0))
                interval_ms = float(config.get("interval_milliseconds", 0))
                total_interval = interval_sec + (interval_ms / 1000.0)
                # Allow minimum of 0.001s (1ms) for fast clicking
                total_interval = max(0.001, total_interval) if total_interval > 0 else 0.0
                
                # Log interval for debugging
                if on_action:
                    on_action(f"Intervalle configuré: {interval_sec}s + {interval_ms}ms = {total_interval:.3f}s")
                repeat_raw = config.get("repeat_sequence", False)
                repeat_sequence = repeat_raw is True or str(repeat_raw).strip().lower() in {"1", "true", "yes", "on"}
                repeat_delay_seconds = max(0.0, float(config.get("repeat_delay_seconds", 0.0)))
                humanized_mode = config["humanized_mode"]
                jitter = max(0, config["humanized_jitter"])
                temporal_jitter_enabled = bool(config.get("temporal_jitter_enabled", False))
                temporal_jitter_min = float(config.get("temporal_jitter_min", 0.008))
                temporal_jitter_max = float(config.get("temporal_jitter_max", 0.015))
                if temporal_jitter_min > temporal_jitter_max:
                    temporal_jitter_min, temporal_jitter_max = temporal_jitter_max, temporal_jitter_min

                on_status(format_text(language, "worker_seq_running"))
                if on_action:
                    on_action(format_text(language, "worker_seq_started"))
                    # Log des paramètres actifs
                    mode_info = []
                    if humanized_mode:
                        mode_info.append(f"Humanisé: ±{jitter}px")
                    if temporal_jitter_enabled:
                        mode_info.append(f"Jitter temporel: +{temporal_jitter_min:.3f}s-{temporal_jitter_max:.3f}s")
                    if repeat_sequence:
                        mode_info.append("Répétition: ON")
                    if mode_info:
                        on_action(f"Modes actifs: {', '.join(mode_info)}")

                def _compute_delay(base: float) -> float:
                    if temporal_jitter_enabled:
                        return max(0.0, base + random.uniform(temporal_jitter_min, temporal_jitter_max))
                    return max(0.0, base)

                while not self._stop_event.is_set():
                    for action in sequence:
                        if self._stop_event.is_set():
                            break

                        if action["type"] == "mouse":
                            x, y = action["coords"]
                            if humanized_mode and jitter > 0:
                                x += random.randint(-jitter, jitter)
                                y += random.randint(-jitter, jitter)
                            pyautogui.moveTo(x, y)

                            button = action["button"]
                            click_type = action["click_type"]
                            clicks_per_trigger = 2 if click_type == "double" else 1

                            repeat_count = max(1, int(action.get("repeats", 1)))
                            for index in range(repeat_count):
                                pyautogui.click(button=button, clicks=clicks_per_trigger)
                                if on_action:
                                    on_action(format_text(language, "worker_seq_mouse_action", x=x, y=y, button=button, click_type=click_type))
                                # Delay only between repeated clicks of the same action.
                                if index < repeat_count - 1:
                                    click_delay = _compute_delay(total_interval)
                                    if click_delay > 0 and self._stop_event.wait(click_delay):
                                        break
                                if self._stop_event.is_set():
                                    break

                        elif action["type"] == "image":
                            image_path = action.get("image_path", "")
                            button = action.get("button", "left")
                            click_type = action.get("click_type", "single")
                            retries = max(1, int(action.get("retries", 1)))
                            clicks_per_trigger = 2 if click_type == "double" else 1
                            found = False

                            for attempt in range(retries):
                                if self._stop_event.is_set():
                                    break

                                point = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)
                                if point:
                                    found = True
                                    target_x, target_y = int(point.x), int(point.y)
                                    pyautogui.moveTo(target_x, target_y)
                                    pyautogui.click(button=button, clicks=clicks_per_trigger)
                                    if on_action:
                                        on_action(format_text(language, "worker_seq_image_found", x=target_x, y=target_y, image_path=image_path))
                                    break

                                logger = get_structured_logger()
                                if logger:
                                    logger.log_message(
                                        "automation_workers.py",
                                        "Image introuvable pendant séquence",
                                        level="WARNING",
                                        context={
                                            "worker": "SequenceWorker",
                                            "action_type": "image",
                                            "attempt": attempt + 1,
                                            "retries": retries,
                                            "image_path": image_path,
                                        },
                                    )

                                if on_action:
                                    on_action(format_text(language, "worker_seq_image_not_found", attempt=attempt + 1, retries=retries, image_path=image_path))

                                retry_delay = _compute_delay(total_interval)
                                if retry_delay > 0 and self._stop_event.wait(retry_delay):
                                    break
                                if self._stop_event.is_set():
                                    break

                            if not found and on_action:
                                on_action(format_text(language, "worker_seq_image_skipped"))

                        elif action["type"] == "keyboard":
                            keyboard.send(action["keys"])
                            if on_action:
                                on_action(format_text(language, "worker_seq_keyboard_action", keys=action["keys"]))

                        action_delay = _compute_delay(total_interval)
                        if action_delay > 0 and self._stop_event.wait(action_delay):
                            break
                        if self._stop_event.is_set():
                            break

                    if self._stop_event.is_set() or not repeat_sequence:
                        break

                    if repeat_delay_seconds > 0 and self._stop_event.wait(repeat_delay_seconds):
                        break
            except Exception as exc:
                logger = get_structured_logger()
                if logger:
                    logger.log_exception(
                        "automation_workers.py",
                        exc,
                        context={"worker": "SequenceWorker", "config": config},
                    )
                on_status(format_text(language, "worker_seq_error", error=str(exc)))
                if on_action:
                    on_action(format_text(language, "worker_seq_error", error=str(exc)))
            finally:
                on_status(format_text(language, "worker_seq_stopped"))
                if on_action:
                    on_action(format_text(language, "worker_seq_stopped"))

        self._start_thread(_run_sequence)
