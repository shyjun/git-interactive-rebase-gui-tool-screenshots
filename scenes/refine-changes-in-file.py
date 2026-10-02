"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, capture, repo
BOXES1 = [
    {"rect": (497, 203, 735, 246)},
    {"rect": (1284, 261, 1439, 373)},
    {"rect": (493, 788, 1406, 847)},
    ]

BOXES2 = [
    {"rect": (548, 301, 1333, 620)},
    {"rect": (546, 647, 756, 698)},
    {"rect": (1094, 642, 1333, 694)},
    ]

def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 2. open the tool: HEAD~13 shows the 13 newest commits (the list excludes
    #    the base commit itself, so the arg must be one further back)
    tool = Tool(args=["HEAD~13"], log_name="head-commits.log")
    try:
        tool.wait_for_window()
        tool.maximize()
        tool.sleep(1)

        tool.sleep(1)
        tool.click(516, 235)

        tool.sleep(1)
        tool.click(1325, 260, button=3)

        tool.sleep(.3)  # commit list, diff pane and status labels have settled
        tool.press("Up")

        tool.sleep(.3)  # commit list, diff pane and status labels have settled
        tool.press("Up")

        tool.sleep(.2)
        tool.press("Return")

        tool.sleep(1)
        tool.click(1334, 285)

        tool.sleep(.5)
        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        img.draw_box(BOXES1)
        img.save("refine-changes-in-file-1.png")

        tool.sleep(.3)  # commit list, diff pane and status labels have settled
        tool.press("Down")

        tool.sleep(.2)
        tool.press("Return")

        tool.sleep(.5)
        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        img.draw_box(BOXES2)
        img.save("refine-changes-in-file-2.png")


        tool.sleep(.5)
        tool.press("Escape")

        tool.sleep(.5)
        tool.press("Escape")

        tool.sleep(.5)
        tool.press("Escape")


    finally:
        # 4. close the tool - even when a step above failed
        tool.close()
        pass


if __name__ == "__main__":
    main()
