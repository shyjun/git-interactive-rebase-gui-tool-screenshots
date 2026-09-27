"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
from capture_lib import Tool, capture, repo

BOXES = [
    {"rect": (687, 302, 1213, 658)},
    ]

def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 2. open the tool: HEAD~13 shows the 13 newest commits (the list excludes
    #    the base commit itself, so the arg must be one further back)
    tool = Tool(args=["HEAD~13"], log_name="head-commits.log")
    try:
        tool.wait_for_window()
        tool.maximize()  # capture in maximized view (screen workarea)
        tool.sleep(1)  # commit list, diff pane and status labels have settled
        tool.click(1418, 1028)   # right-click the commit row
        tool.sleep(1)  # commit list, diff pane and status labels have settled
        tool.click(1409, 951)   # right-click the commit row

        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        img.draw_box(BOXES)
        img.save("external-tools-dialog.png")
    finally:
        tool.sleep(.1)
        # 4. close the tool - even when a step above failed
        tool.close()


if __name__ == "__main__":
    main()
