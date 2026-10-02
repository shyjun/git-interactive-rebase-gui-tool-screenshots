"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, capture, repo
BOXES = [
    {"rect": (1, 35, 212, 70)},
    {"rect": (1422, 31, 1472, 69)},
    {"rect": (11, 456, 811, 504)},
    {"rect": (10, 245, 811, 293)},
    {"rect": (10, 107, 811, 153)},
    {"rect": (1474, 28, 1911, 137)},
    ]

def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 2. open the tool: HEAD~13 shows the 13 newest commits (the list excludes
    #    the base commit itself, so the arg must be one further back)
    tool = Tool(args=["HEAD~13"], log_name="mark-commits.log")
    # everything below runs inside the finally - no matter which step fails,
    # the tool gets closed and cannot poison the next run
    try:
        tool.wait_for_window()
        tool.maximize()

        tool.sleep(.5)
        tool.click(16, 52)

        tool.press("t")
        tool.sleep(.1)
        tool.press("e")
        tool.sleep(.1)
        tool.press("s")
        tool.sleep(.1)
        tool.press("t")

        tool.sleep(.1)
        tool.click(1593, 52)



        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        img.draw_box(BOXES)
        img.save("search-filter.png")

        tool.sleep(.1)
        tool.press("Escape")
    finally:
        # 4. close the tool - even when a step above failed
        tool.close()


if __name__ == "__main__":
    main()
