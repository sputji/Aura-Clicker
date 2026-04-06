from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import threading
import traceback
from typing import Any


class StructuredErrorLogger:
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._errors_dir = self._base_dir / "logs" / "errors"
        self._errors_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def log_exception(self, source_file: str, exc: BaseException, context: dict[str, Any] | None = None) -> None:
        payload = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "source_file": source_file,
            "error_type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
            "context": context or {},
        }
        self._write(source_file, payload)

    def log_message(self, source_file: str, message: str, level: str = "INFO", context: dict[str, Any] | None = None) -> None:
        payload = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "source_file": source_file,
            "level": level,
            "message": message,
            "context": context or {},
        }
        self._write(source_file, payload)

    def _write(self, source_file: str, payload: dict[str, Any]) -> None:
        filename = source_file.replace("\\", "_").replace("/", "_").replace(":", "_")
        log_file = self._errors_dir / f"{filename}.jsonl"
        line = json.dumps(payload, ensure_ascii=False)
        with self._lock:
            with log_file.open("a", encoding="utf-8") as fp:
                fp.write(line + "\n")


_logger: StructuredErrorLogger | None = None


def init_structured_logger(base_dir: Path) -> None:
    global _logger
    _logger = StructuredErrorLogger(base_dir)


def get_structured_logger() -> StructuredErrorLogger | None:
    return _logger
