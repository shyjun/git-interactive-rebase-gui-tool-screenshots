"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, capture, repo
BOXES = [
    {"rect": (280, 178, 661, 181)},
    {"rect": (280, 319, 661, 322)},
    {"rect": (280, 424, 661, 427)},
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
        tool.maximize()  # capture in maximized view (screen workarea)

        tool.sleep(1)  # commit list, diff pane and status labels have settled
        tool.click(230, 165, button=3)   # right-click the commit row

        tool.sleep(.1)  # commit list, diff pane and status labels have settled
        tool.press("Down")
        tool.sleep(.2)
        tool.press("Return")              # activate

        tool.sleep(1)  # commit list, diff pane and status labels have settled
        tool.click(260, 300, button=3)   # right-click the commit row
        tool.sleep(.1)  # commit list, diff pane and status labels have settled
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Return")              # activate

        tool.sleep(1)  # commit list, diff pane and status labels have settled
        tool.click(400, 410, button=3)   # right-click the commit row
        tool.sleep(.1)  # commit list, diff pane and status labels have settled
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Return")              # activate

        tool.sleep(1)  # commit list, diff pane and status labels have settled
        tool.press("Down")
        tool.sleep(.1)  # commit list, diff pane and status labels have settled
        tool.press("Down")


        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        img.draw_box(BOXES)
        img.save("mark-commits.png")

        tool.press("Escape")
    finally:
        # 4. close the tool - even when a step above failed
        tool.close()


if __name__ == "__main__":
    main()
