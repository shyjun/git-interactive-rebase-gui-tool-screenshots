"""Capture previous-run.png - the "Previous Run" dialog after a hard kill.

Requires the tool copy in .work/ (run capture.sh, or its copy steps). The
script starts the tool, kills it with SIGTERM (its unclean-exit marker stays
behind, since atexit never runs), then relaunches with marker sweeping
disabled: the relaunch finds the stale marker and shows the "Previous Run"
dialog before the main window appears. Captured dialog-only - the main
window does not exist yet.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, capture_screen, repo

CROP = (0, 0, 1920, 1080)
BOXES = []


def main():
    repo.reset_to_base()

    tool1 = Tool(args=[], log_name="previous-run-1.log")
    try:
        tool1.wait_for_window()  # guarantees the unclean-exit marker exists
        tool1.sleep(1)
        tool1.proc.terminate()  # SIGTERM: atexit never runs, marker stays
        tool1.proc.wait(timeout=10)
    finally:
        tool1.close(sweep_markers=False)  # keep the stale marker for tool2

    tool2 = Tool(args=[], log_name="previous-run-2.log", sweep_markers=False)
    try:
        tool2.wait_for_name("Previous Run", timeout=15)
        tool2.sleep(1.5)  # let the dialog paint and settle
        img = capture_screen(
            *CROP,
            description="relaunch after a hard kill: Previous Run dialog",
        )
        img.draw_box(BOXES)
        img.save("previous-run.png")

        tool2.press("Escape")  # "Noted. Continue" - the tool ignores the result
        tool2.sleep(.5)
        tool2.wait_for_window()  # main window appears only after the dialog
        tool2.sleep(1)
    finally:
        tool2.close()


if __name__ == "__main__":
    main()
