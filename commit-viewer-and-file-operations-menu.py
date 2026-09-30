"""Capture commit-viewer-and-file-operations-menu.png - viewer + file menu.

Commit viewer with the file-operations menu open, red boxes around both
plus white-plate labels. Run it through main.py.
"""
from capture_lib import Tool, capture, repo

BOXES = [
    {"rect": (517, 153, 1383, 809)},
    {"rect": (962, 377, 1159, 409)},
    {"rect": (650, 378, 957, 588)},
    ]

def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 2. open the tool: HEAD~13 shows the 13 newest commits (the list excludes
    #    the base commit itself, so the arg must be one further back)
    tool = Tool(args=["HEAD~13"], log_name="commit-viewer-and-file-operations-menu.log")
    # everything below runs inside the finally - no matter which step fails,
    # the tool gets closed and cannot poison the next run
    try:
        tool.wait_for_window()
        tool.maximize()  # capture in maximized view (screen workarea)
        tool.sleep(1)  # commit list, diff pane and status labels have settled
        tool.click(370, 165, button=3)   # right-click the commit row
        tool.sleep(.5)  # commit list, diff pane and status labels have settled

        tool.press("Down")
        tool.sleep(.1)

        tool.press("Down")
        tool.sleep(.1)

        tool.press("Return")              # activate
        tool.sleep(1)

        tool.click(666, 352)
        tool.sleep(.2)

        tool.click(660, 387, button=3)   # right-click the commit row
        tool.sleep(.2)

        tool.press("Down")
        tool.sleep(.1)

        tool.press("Right")
        tool.sleep(.1)

        tool.sleep(1)
        # 3. take the picture
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )

        img.draw_box(BOXES)
        img.add_text(687, 143, " commit viewer ", 20, border=1, fill="red")
        img.add_text(770, 364, " file-operations menu ", 20, border=1, fill="red")
        img.save("commit-viewer-and-file-operations-menu.png")



        tool.sleep(.1)
        tool.press("Escape")

        tool.sleep(.1)
        tool.press("Escape")

    finally:
        tool.sleep(.1)
        # 4. close the tool - even when a step above failed
        tool.close()


if __name__ == "__main__":
    main()
