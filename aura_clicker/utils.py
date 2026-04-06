from __future__ import annotations


def safe_int(value: str, default: int = 0, minimum: int | None = None) -> int:
    try:
        number = int(value.strip())
    except (ValueError, AttributeError):
        return default

    if minimum is not None:
        return max(number, minimum)
    return number


def interval_to_seconds(hours: int, minutes: int, seconds: int, milliseconds: int) -> float:
    total_ms = (
        max(0, hours) * 3_600_000
        + max(0, minutes) * 60_000
        + max(0, seconds) * 1_000
        + max(0, milliseconds)
    )
    return max(0.001, total_ms / 1000.0)


def bool_to_int(flag: bool) -> int:
    return 1 if flag else 0
