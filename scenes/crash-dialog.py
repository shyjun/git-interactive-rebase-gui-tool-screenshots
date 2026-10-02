"""Capture crash-dialog.png - the "Unexpected Error" window on an unhandled exception.

Requires the tool copy in .work/ (run capture.sh, or its copy steps). The
script points the tool's PYTHONPATH at .work/inject/, whose sitecustomize
wraps QApplication.exec so a background thread raises a RuntimeError once the
window is up; the tool's excepthook then shows the crash dialog over the
main window. PYTHONPATH is dropped again before the tool exits normally.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, capture, repo
from main import WORK_DIR

BOXES = [
    {"rect": (580, 270, 1340, 810)},
]

INJECT_DIR = WORK_DIR / "inject"

SITECUSTOMIZE = '''"""Auto-imported when scenes/crash-dialog.py sets PYTHONPATH.

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

    tool = Tool(args=[], log_name="crash-dialog.log")
    try:
        tool.wait_for_window()
        tool.maximize()
        tool.wait_for_name("Unexpected Error", timeout=15)
        tool.sleep(2)  # let the dialog paint and settle
        img = capture(
            tool,
            description="unhandled exception: Unexpected Error crash dialog",
            size=(1920, 1042),
        )
        img.draw_box(BOXES)
        img.save("crash-dialog.png")

        tool.press("Escape")  # dismiss the dialog; the app keeps running
        tool.sleep(.5)
    finally:
        tool.close()
        if old_pythonpath is None:
            os.environ.pop("PYTHONPATH", None)
        else:
            os.environ["PYTHONPATH"] = old_pythonpath


if __name__ == "__main__":
    main()
