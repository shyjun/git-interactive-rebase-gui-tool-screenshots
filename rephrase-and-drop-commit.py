"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
from capture_lib import Tool, capture, repo


def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 2. open the tool: HEAD~13 shows the 13 newest commits (the list excludes
    #    the base commit itself, so the arg must be one further back)
    tool = Tool(args=["HEAD~13"], log_name="head-commits.log")
    tool.wait_for_window()
    tool.maximize()  # capture in maximized view (screen workarea)
    tool.sleep(4)  # commit list, diff pane and status labels have settled
    tool.click(370, 165, button=3)   # right-click the commit row
    tool.sleep(1)  # commit list, diff pane and status labels have settled

    tool.press("Down")
    tool.sleep(.5)
    tool.press("Down")
    tool.sleep(.5)
    tool.press("Down")
    tool.sleep(.5)
    tool.press("Down")
    tool.sleep(.5)
    tool.press("Down")
    tool.sleep(.5)
    tool.press("Down")
    tool.sleep(.5)
    tool.press("Down")
    tool.sleep(.5)
    tool.press("Down")
    tool.sleep(.5)

    tool.press("Return")              # activate                                                                                         screenshots/ and commit
    tool.wait_for_name("Rephrase Commit")  # verify the dialog really opened

    # 3. take the picture (this shot has no red boxes)
    capture(
        tool,
        name="rephrase-and-drop-commit.webp",
        description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
        boxes=[],
        size=(1920, 1042),
    )

    tool.press("Escape")
    # 4. close the tool again
    tool.close()


if __name__ == "__main__":
    main()
