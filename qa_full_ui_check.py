from __future__ import annotations

import tempfile
from pathlib import Path

import main as app_main
import aura_clicker.windows.main_window as main_window_module
import aura_clicker.windows.advanced_window as advanced_window_module
import aura_clicker.windows.key_presser_window as key_window_module


def pump(root) -> None:
    root.update_idletasks()
    root.update()


def fake_capture_mouse(callback):
    callback(321, 654)


def fake_capture_keys(callback):
    callback("CTRL+SHIFT+A")


def run() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        profile_path = Path(tmp_dir) / "qa_profile.aura_profile.json"

        app_main.filedialog.asksaveasfilename = lambda **kwargs: str(profile_path)
        app_main.filedialog.askopenfilename = lambda **kwargs: str(profile_path)

        main_window_module.capture_mouse_position = fake_capture_mouse
        advanced_window_module.capture_mouse_position = fake_capture_mouse
        advanced_window_module.capture_hotkey_combination = fake_capture_keys
        key_window_module.capture_hotkey_combination = fake_capture_keys

        app = app_main.AuraClickerApplication()
        root = app.root
        root.withdraw()
        pump(root)

        def fake_click_start(config, status, on_action=None):
            status("[QA] click start OK")
            if on_action:
                on_action("[QA] click action")

        def fake_click_stop():
            app.history.push("[QA] click stop OK")

        def fake_seq_start(config, sequence, status, on_action=None):
            status("[QA] seq start OK")
            if on_action:
                on_action(f"[QA] seq actions: {len(sequence)}")

        def fake_seq_stop():
            app.history.push("[QA] seq stop OK")

        def fake_key_start(config, status, on_action=None):
            status("[QA] key start OK")
            if on_action:
                on_action("[QA] key action")

        def fake_key_stop():
            app.history.push("[QA] key stop OK")

        app.click_worker.start = fake_click_start
        app.click_worker.stop = fake_click_stop

        app.sequence_worker.start = fake_seq_start
        app.sequence_worker.stop = fake_seq_stop

        app.key_worker.start = fake_key_start
        app.key_worker.stop = fake_key_stop

        mw = app.main_window
        assert mw is not None

        mw.pick_btn.invoke()
        pump(root)
        assert mw.x_entry.get() == "321"
        assert mw.y_entry.get() == "654"

        mw.start_btn.invoke()
        mw.stop_btn.invoke()
        mw.toggle_btn.invoke()
        pump(root)

        mw._save_state()
        mw._export_profile()
        assert profile_path.exists(), "Le profil exporté est absent"
        mw._import_profile()
        pump(root)

        mw._on_open_hotkeys()
        pump(root)
        hotkeys_windows = [w for w in root.winfo_children() if w.__class__.__name__ == "HotkeySettingsWindow"]
        assert hotkeys_windows, "Fenêtre hotkeys non ouverte"
        hk = hotkeys_windows[0]
        hk.start_entry.delete(0, "end")
        hk.start_entry.insert(0, "F9")
        hk._save()
        pump(root)

        mw._on_open_advanced()
        pump(root)
        aw = app.advanced_window
        assert aw is not None and aw.winfo_exists()

        aw.pick_btn.invoke()
        pump(root)
        assert aw.x_entry.get() == "321"
        assert aw.y_entry.get() == "654"

        aw._capture_keys()
        pump(root)

        aw.repeats_entry.delete(0, "end")
        aw.repeats_entry.insert(0, "3")
        aw._add_mouse_action()
        aw._add_key_action()
        assert len(app.state.sequence_actions) >= 2

        aw._start()
        aw._stop()
        aw._delete_action()
        aw._clear_actions()
        pump(root)

        mw._on_open_key_presser()
        pump(root)
        kw = app.key_window
        assert kw is not None and kw.winfo_exists()

        kw.capture_btn.invoke()
        pump(root)
        assert "ctrl+shift+a" in kw.key_entry.get().lower()

        kw.start_btn.invoke()
        kw.stop_btn.invoke()
        kw.save_btn.invoke()
        pump(root)

        assert mw.history_box.get("1.0", "end").strip(), "Historique principal vide"
        assert aw.history_box.get("1.0", "end").strip(), "Historique avancé vide"
        assert kw.history_box.get("1.0", "end").strip(), "Historique key presser vide"

        app._on_close()


if __name__ == "__main__":
    run()
    print("QA UI 0.1.1: OK")
