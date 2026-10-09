"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

BOXES = [
    {"rect": (571, 25, 752, 87)},
    ]

from capture_lib import Tool, capture, repo

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

        tool.click(320, 200)
        tool.sleep(.2)
        tool.click(1254, 260)
        tool.sleep(.2)
        tool.click(1265, 331)
        tool.sleep(.2)

        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        img.crop(1147, 206, 1915, 308)
        img.draw_box(BOXES)
        tool.sleep(.2)
        img.save("file-list-hover-toolbar.png")
    finally:
        # 4. close the tool - even when a step above failed
        tool.sleep(.2)
        tool.close()


if __name__ == "__main__":
    main()
