"""Capture reorder-commit.webp - drag a commit row and confirm the reorder.

Run it through main.py; it prepares the clone, settings and publishing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, capture, repo
BOXES = [
    {"rect": (694, 406, 1204, 554)},
    ]


def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 2. open the tool and let the list settle
    tool = Tool(args=["HEAD~13"], log_name="reorder-commit.log")
    try:
        tool.wait_for_window()
        tool.maximize()  # capture in maximized view (screen workarea)
        tool.sleep(1)    # commit list, diff pane and status labels have settled

        # select the row, then drag it three rows down (rows are 27px apart)
        tool.click(230, 165)
        tool.sleep(0.3)
        tool.drag(230, 165, 230, 246)

        # 3. the drop pops the Confirm Reorder dialog - take its picture
        #    (the dialog is never answered, close() dismisses it)
        tool.sleep(0.5)
        img = capture(
            tool,
            description="dragged commit row three positions down, Confirm Reorder dialog",
            size=(1920, 1042),
        )
        img.draw_box(BOXES)
        img.save("drag-reorder.png", watermark=True)

    finally:
        # 4. close the tool - even when a step above failed
        tool.close()


if __name__ == "__main__":
    main()
