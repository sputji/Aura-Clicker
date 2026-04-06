from __future__ import annotations

from datetime import datetime
import argparse
import os
from pathlib import Path
import threading
import tkinter as tk

import pyautogui

from aura_clicker.automation_workers import SequenceWorker
from aura_clicker.structured_error_logger import init_structured_logger, get_structured_logger


BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "qa_reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_FILE = REPORT_DIR / "endurance_30m_real_report.md"
REPORT_LOCK = threading.Lock()
LOCK_FILE = REPORT_DIR / "endurance_30m_real.lock"


def append_report(line: str) -> None:
    stamp = datetime.now().strftime("%H:%M:%S")
    with REPORT_LOCK:
        with REPORT_FILE.open("a", encoding="utf-8") as fp:
            fp.write(f"[{stamp}] {line}\n")


def create_target_window() -> tuple[tk.Tk, tuple[int, int]]:
    root = tk.Tk()
    root.title("AURA CLICK TARGET - NE PAS FERMER")
    root.geometry("520x300+120+120")
    root.attributes("-topmost", True)
    label = tk.Label(root, text="Zone de test endurance 30 min\nLaisser cette fenêtre au premier plan", font=("Segoe UI", 14))
    label.pack(expand=True)
    root.update_idletasks()
    root.update()

    x = root.winfo_rootx() + 220
    y = root.winfo_rooty() + 170
    return root, (x, y)


def main(minutes: int = 30) -> None:
    init_structured_logger(BASE_DIR)
    logger = get_structured_logger()
    pyautogui.FAILSAFE = False

    try:
        fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode("utf-8"))
        os.close(fd)
    except FileExistsError:
        stale = True
        try:
            pid_text = LOCK_FILE.read_text(encoding="utf-8").strip()
            pid = int(pid_text)
            os.kill(pid, 0)
            stale = False
        except Exception:
            stale = True

        if stale:
            LOCK_FILE.unlink(missing_ok=True)
            fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("utf-8"))
            os.close(fd)
        else:
            raise RuntimeError("Un test endurance est déjà en cours. Supprimez le lockfile si nécessaire.")

    REPORT_FILE.write_text("# Rapport Endurance 30 min - Aura-Clicker 0.1.1b\n\n", encoding="utf-8")
    append_report(f"Démarrage scénario réel ({minutes} minute(s))")

    root, coords = create_target_window()
    append_report(f"Fenêtre cible créée en coordonnée test: {coords}")

    sequence = [
        {
            "type": "mouse",
            "coords": coords,
            "button": "left",
            "click_type": "single",
            "repeats": 2,
        },
        {
            "type": "mouse",
            "coords": (coords[0] + 40, coords[1]),
            "button": "left",
            "click_type": "single",
            "repeats": 1,
        },
        {
            "type": "mouse",
            "coords": (coords[0], coords[1] + 35),
            "button": "right",
            "click_type": "single",
            "repeats": 1,
        },
    ]

    config = {
        "repeat_sequence": True,
        "interval_seconds": 0,
        "interval_milliseconds": 500,
        "humanized_mode": False,
        "humanized_jitter": 0,
    }

    worker = SequenceWorker()

    def on_status(msg: str) -> None:
        append_report(f"STATUS: {msg}")

    def on_action(msg: str) -> None:
        append_report(f"ACTION: {msg}")

    worker.start(config, sequence, on_status, on_action)

    total_seconds = max(1, minutes) * 60
    state = {"seconds": 0}

    def tick() -> None:
        try:
            state["seconds"] += 1
            current = state["seconds"]

            if current % 60 == 0:
                append_report(f"Heartbeat minute {current // 60}/{max(1, minutes)}")

            if current >= total_seconds:
                worker.stop()
                append_report(f"Scénario endurance {max(1, minutes)} minute(s) terminé")
                root.after(200, root.destroy)
                return

            root.after(1000, tick)
        except Exception as exc:
            append_report(f"ERREUR DURANT TEST: {exc}")
            if logger:
                logger.log_exception("qa_endurance_30m_real.py", exc)
            worker.stop()
            root.after(200, root.destroy)

    root.after(1000, tick)
    try:
        root.mainloop()
    finally:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--minutes", type=int, default=30)
    args = parser.parse_args()

    main(minutes=args.minutes)
    print("ENDURANCE_REAL: OK")
