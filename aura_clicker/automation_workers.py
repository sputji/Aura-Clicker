from __future__ import annotations

import random
import threading
import time
from typing import Callable

import keyboard
import pyautogui

from .structured_error_logger import get_structured_logger
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
                if temporal_jitter_min > temporal_jitter_max:
                    temporal_jitter_min, temporal_jitter_max = temporal_jitter_max, temporal_jitter_min

                on_status("Auto-clic actif")
                if on_action:
                    on_action("Auto-clic démarré")
                while not self._stop_event.is_set() and (infinite or remaining > 0):
                    if not config["current_position"]:
                        pyautogui.moveTo(config["x"], config["y"])

                    pyautogui.click(button=mouse_button, clicks=clicks_per_action)
                    if on_action:
                        if config["current_position"]:
                            on_action(f"Clic {mouse_button} ({clicks_per_action}x) à la position courante")
                        else:
                            on_action(
                                f"Clic {mouse_button} ({clicks_per_action}x) en X={config['x']} Y={config['y']}"
                            )

                    if not infinite:
                        remaining -= 1

                    wait_delay = interval
                    if temporal_jitter_enabled:
                        wait_delay = random.uniform(temporal_jitter_min, temporal_jitter_max)

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
                on_status(f"Erreur auto-clic: {exc}")
                if on_action:
                    on_action(f"Erreur auto-clic: {exc}")
            finally:
                on_status("Auto-clic arrêté")
                if on_action:
                    on_action("Auto-clic arrêté")

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
                    on_status("Aucune touche sélectionnée")
                    return

                on_status(f"Auto-touche actif: {key_name}")
                if on_action:
                    on_action(f"Auto-touche démarré: {key_name}")
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
                        on_action(f"Touche exécutée: {key_name}")

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
                on_status(f"Erreur auto-touche: {exc}")
                if on_action:
                    on_action(f"Erreur auto-touche: {exc}")
            finally:
                on_status("Auto-touche arrêté")
                if on_action:
                    on_action("Auto-touche arrêté")

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
                if not sequence:
                    on_status("Aucune action dans la séquence")
                    return

                interval = interval_to_seconds(0, 0, config["interval_seconds"], config["interval_milliseconds"])
                repeat_sequence = config["repeat_sequence"]
                repeat_delay_seconds = max(0.0, float(config.get("repeat_delay_seconds", 0.0)))
                humanized_mode = config["humanized_mode"]
                jitter = max(0, config["humanized_jitter"])
                temporal_jitter_enabled = bool(config.get("temporal_jitter_enabled", False))
                temporal_jitter_min = float(config.get("temporal_jitter_min", 0.008))
                temporal_jitter_max = float(config.get("temporal_jitter_max", 0.015))
                if temporal_jitter_min > temporal_jitter_max:
                    temporal_jitter_min, temporal_jitter_max = temporal_jitter_max, temporal_jitter_min

                on_status("Séquence avancée en cours")
                if on_action:
                    on_action("Séquence avancée démarrée")
                while self.running and not self._stop_event.is_set():
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

                            for _ in range(max(1, action["repeats"])):
                                pyautogui.click(button=button, clicks=clicks_per_trigger)
                                if on_action:
                                    on_action(
                                        f"Action souris: X={x} Y={y} bouton={button} type={click_type}"
                                    )
                                click_delay = 0.01
                                if temporal_jitter_enabled:
                                    click_delay = random.uniform(temporal_jitter_min, temporal_jitter_max)
                                if self._stop_event.wait(max(0.001, click_delay)):
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
                                        on_action(
                                            f"Action image: trouvé ({target_x}, {target_y}) fichier={image_path}"
                                        )
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
                                    on_action(
                                        f"Image non trouvée ({attempt + 1}/{retries}) : {image_path}"
                                    )

                                retry_delay = interval
                                if temporal_jitter_enabled:
                                    retry_delay = random.uniform(temporal_jitter_min, temporal_jitter_max)
                                if self._stop_event.wait(max(0.001, retry_delay)):
                                    break

                            if not found and on_action:
                                on_action("Action image ignorée après épuisement des tentatives")

                        elif action["type"] == "keyboard":
                            keyboard.send(action["keys"])
                            if on_action:
                                on_action(f"Action clavier: {action['keys']}")

                        action_delay = interval
                        if temporal_jitter_enabled:
                            action_delay = random.uniform(temporal_jitter_min, temporal_jitter_max)

                        if self._stop_event.wait(max(0.001, action_delay)):
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
                on_status(f"Erreur séquence avancée: {exc}")
                if on_action:
                    on_action(f"Erreur séquence avancée: {exc}")
            finally:
                on_status("Séquence avancée arrêtée")
                if on_action:
                    on_action("Séquence avancée arrêtée")

        self._start_thread(_run_sequence)
