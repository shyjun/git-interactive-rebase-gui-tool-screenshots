"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, capture, repo
BOXES = [
    {"rect": (358, 448, 680, 481)},
    {"rect": (734, 449, 1019, 571)},
    ]

def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 2. open the tool: HEAD~13 shows the 13 newest commits (the list excludes
    #    the base commit itself, so the arg must be one further back)
    tool = Tool(args=["HEAD~13"], log_name="rephrase.log")
    # everything below runs inside the finally - no matter which step fails,
    # the tool gets closed and cannot poison the next run
    try:
        tool.wait_for_window()
        tool.maximize()  # capture in maximized view (screen workarea)
        tool.sleep(1)  # commit list, diff pane and status labels have settled
        tool.click(370, 165, button=3)   # right-click the commit row
        tool.sleep(.5)  # commit list, diff pane and status labels have settled

        tool.press("Up")
        tool.sleep(.1)

        tool.press("Up")
        tool.sleep(.1)

        tool.press("Up")
        tool.sleep(.1)

        tool.press("Up")
        tool.sleep(.1)

        tool.press("Up")
        tool.sleep(.1)

        tool.press("Return")              # activate
        tool.sleep(.5)

        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        img.draw_box(BOXES)
        img.save("consolidated-diff.png")

        tool.press("Escape")
    finally:
        tool.sleep(.1)
        # 4. close the tool - even when a step above failed
        tool.close()


if __name__ == "__main__":
    main()
