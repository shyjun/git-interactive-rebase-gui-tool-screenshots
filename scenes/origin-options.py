"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, capture, repo, capture_screen

BOXES = [
    {"rect": (5, 946, 1904, 1007)},
    {"rect": (716, 319, 1184, 642)},
    ]

BOXES1 = [
    {"rect": (5, 946, 1904, 1007)},
    {"rect": (716, 333, 1186, 629)},
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

        tool.sleep(.4)
        tool.click(1418, 1028)

        tool.sleep(.2)
        tool.click(1472, 904)

        tool.sleep(.2)
        tool.press("Down")

        tool.sleep(.2)
        tool.press("Return")              # activate

        tool.sleep(.5)
        tool.click(532, 973)

        tool.sleep(.5)

        # menu open, window still maximized
        img = capture_screen(
            0, 0, 1920, 1042,          # whole screen, taskbar included
            description="Origin group with git fetch/pull menu open",
        )

        img.draw_box(BOXES)

        img.save("origin-options.png")

        tool.sleep(.5)
        tool.press("Escape")

        tool.sleep(.4)
        tool.click(1495, 979)

        push = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )

        push.draw_box(BOXES1)

        push.save("push-dialog.png")


        tool.sleep(.5)
        tool.press("Escape")



        tool.sleep(.4)
        tool.click(1418, 1028)

        tool.sleep(.2)
        tool.click(1472, 904)

        tool.sleep(.2)
        tool.press("Down")

        tool.sleep(.2)
        tool.press("Return")              # activate

        tool.sleep(.5)
        tool.press("Escape")


        tool.sleep(1)

    finally:
        tool.sleep(.5)
        # 4. close the tool - even when a step above failed
        tool.close()
        tool.sleep(.5)


if __name__ == "__main__":
    main()
