"""Capture crash-dialog.png then previous-run.png in one run.

Requires the tool copy in .work/ (run capture.sh, or its copy steps).
First: the tool's PYTHONPATH points at .work/inject/, whose sitecustomize
wraps QApplication.exec so a background thread raises a RuntimeError once the
window is up - the excepthook shows the "Unexpected Error" dialog over the
main window. Then: the tool is killed with SIGTERM (its unclean-exit marker
stays behind, atexit never runs) and relaunched with marker sweeping
disabled - the relaunch finds the stale marker and shows the "Previous Run"
dialog before the main window appears.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, capture, capture_screen, repo, image_new
from main import WORK_DIR


CROP = (0, 0, 1920, 1080)

INJECT_DIR = WORK_DIR / "inject"

SITECUSTOMIZE = '''"""Auto-imported when the crash-dialog capture sets PYTHONPATH.

Wraps QApplication.exec so that, once the GUI window is up and the tool's
excepthook is installed, a background thread raises an unhandled exception -
the tool then shows its own "Unexpected Error" crash dialog.
"""
import threading
import time


def _install():
    from PySide6 import QtWidgets

    original = QtWidgets.QApplication.exec

    def _exec(*args, **kwargs):
        def _boom():
            time.sleep(1)
            raise RuntimeError("deliberate exception for the crash-dialog screenshot")

        threading.Thread(target=_boom, daemon=True).start()
        return original()

    QtWidgets.QApplication.exec = _exec


try:
    _install()
except Exception:
    pass
'''


def main():
    repo.reset_to_base()
    INJECT_DIR.mkdir(parents=True, exist_ok=True)
    (INJECT_DIR / "sitecustomize.py").write_text(SITECUSTOMIZE)
    old_pythonpath = os.environ.get("PYTHONPATH")
    os.environ["PYTHONPATH"] = str(INJECT_DIR) + (
        os.pathsep + old_pythonpath if old_pythonpath else ""
    )

    # ---- 1. exception window ----
    tool1 = Tool(args=[], log_name="crash-dialog.log")
    try:
        tool1.wait_for_window()
        tool1.maximize()
        tool1.wait_for_name("Unexpected Error", timeout=15)
        tool1.sleep(2)  # let the dialog paint and settle
        exception = capture(
            tool1,
            description="unhandled exception: Unexpected Error crash dialog",
            size=(1920, 1042),
        )
        exception.crop(567, 199, 1333, 773)
        exception.save("exception-dialog.png", watermark=False)

    finally:
        if tool1.proc.poll() is None:
            tool1.proc.terminate()  # SIGTERM: atexit never runs, marker stays
            tool1.proc.wait(timeout=10)
        tool1.close(sweep_markers=False)  # keep the stale marker for the relaunch
        # the relaunch must run WITHOUT the injection, or it crashes again
        if old_pythonpath is None:
            os.environ.pop("PYTHONPATH", None)
        else:
            os.environ["PYTHONPATH"] = old_pythonpath

    # ---- 2. crash window: relaunch finds the stale marker ----
    tool2 = Tool(args=[], log_name="previous-run.log", sweep_markers=False)
    try:
        tool2.wait_for_name("Previous Run", timeout=15)
        tool2.sleep(1.5)  # let the dialog paint and settle
        crash = capture_screen(
            *CROP,
            description="relaunch after a hard kill: Previous Run dialog",
        )
        crash.crop(598, 239, 1302, 732)
        crash.save("previous-run.png", watermark=False)

        final = image_new(1519, 621)
        final.add(3, 20, exception)
        final.add_text(70, 2, " exception report ", 20, border=1, fill="red")

        final.add(797, 20, crash)
        final.add_text(860, 2, " previous run crash report ", 20, border=1, fill="red")

        final.save("fault-handling.png")

        tool2.press("Escape")  # "Noted. Continue" - the tool ignores the result
        tool2.sleep(1)
        tool2.sleep(.5)
        tool2.wait_for_window()  # main window appears only after the dialog
        tool2.sleep(1)
        tool2.sleep(1)
    finally:
        tool2.close()


if __name__ == "__main__":
    main()
