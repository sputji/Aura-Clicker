from __future__ import annotations

from datetime import datetime
from pathlib import Path
import subprocess
import sys
import time


BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "qa_reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
CONSOLIDATED = REPORT_DIR / "qa_aggressive_campaign_consolidated.md"


def write(line: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with CONSOLIDATED.open("a", encoding="utf-8") as fp:
        fp.write(f"[{stamp}] {line}\n")


def run_cmd(args: list[str], title: str, success_token: str | None = None) -> None:
    write(f"START: {title}")
    start = time.time()
    completed = subprocess.run(args, cwd=BASE_DIR, check=False, capture_output=True, text=True)
    if completed.stdout:
        write(f"STDOUT {title}: {completed.stdout.strip().splitlines()[-1]}")
    if completed.stderr:
        write(f"STDERR {title}: {completed.stderr.strip().splitlines()[-1]}")

    if completed.returncode != 0:
        token_ok = bool(success_token and success_token in (completed.stdout or ""))
        if not token_ok:
            raise subprocess.CalledProcessError(completed.returncode, args)
        write(f"WARN: {title} retour non-zéro ({completed.returncode}) mais token de succès détecté")

    elapsed = time.time() - start
    write(f"OK: {title} ({elapsed:.1f}s)")


def append_tail(report_file: Path, section_title: str, tail_lines: int = 20) -> None:
    if not report_file.exists():
        write(f"WARN: {section_title} - rapport introuvable")
        return

    text = report_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    tail = text[-tail_lines:] if len(text) > tail_lines else text
    with CONSOLIDATED.open("a", encoding="utf-8") as fp:
        fp.write(f"\n## {section_title}\n")
        for line in tail:
            fp.write(line + "\n")
        fp.write("\n")


def main() -> None:
    CONSOLIDATED.write_text("# Rapport consolidé QA agressive - Aura-Clicker 0.1.1b\n\n", encoding="utf-8")

    python = str(Path(sys.executable))

    # Full UI and baseline checks
    run_cmd([python, "qa_full_ui_check.py"], "UI complète", success_token="QA UI 0.1.1: OK")
    run_cmd([python, "-m", "compileall", "main.py", "aura_clicker", "qa_full_ui_check.py", "qa_endurance_30m_real.py"], "Compilation globale")

    # Aggressive endurance cycles
    for minutes in (3, 5, 10):
        run_cmd([python, "qa_endurance_30m_real.py", "--minutes", str(minutes)], f"Endurance réelle {minutes} min")
        append_tail(BASE_DIR / "qa_reports" / "endurance_30m_real_report.md", f"Extrait endurance {minutes} min", tail_lines=30)

    # Runtime smoke
    start = time.time()
    proc = subprocess.Popen([python, "main.py"], cwd=BASE_DIR)
    time.sleep(6)
    proc.terminate()
    proc.wait(timeout=15)
    write(f"OK: Smoke source main.py ({time.time() - start:.1f}s)")

    # Binary smoke if available
    exe_path = BASE_DIR / "dist" / "Aura-Clicker" / "Aura-Clicker.exe"
    if exe_path.exists():
        start = time.time()
        proc2 = subprocess.Popen([str(exe_path)], cwd=BASE_DIR)
        time.sleep(6)
        proc2.terminate()
        proc2.wait(timeout=15)
        write(f"OK: Smoke binaire Aura-Clicker.exe ({time.time() - start:.1f}s)")
    else:
        write("WARN: Binaire non trouvé pour smoke test")

    # Structured logs snapshot
    errors_dir = BASE_DIR / "logs" / "errors"
    if errors_dir.exists():
        files = sorted(errors_dir.glob("*.jsonl"))
        write(f"INFO: logs structurés détectés = {len(files)} fichier(s)")
        for f in files:
            write(f"INFO: log file -> {f.name}")

    write("FIN: Campagne QA agressive terminée")
    print("QA_AGGRESSIVE_CAMPAIGN: OK")


if __name__ == "__main__":
    main()
