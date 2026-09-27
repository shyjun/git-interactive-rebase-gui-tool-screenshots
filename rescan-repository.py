"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
from capture_lib import Tool, capture, repo

BOXES = [
    {"rect": (623, 156, 1280, 808)},
    {"rect": (1339, 810, 1486, 857)},
    ]

BOXES1 = [
    {"rect": (506, 289, 1064, 462)},
    {"rect": (507, 733, 1392, 795)},
    ]

BOXES2 = [
    {"rect": (492, 176, 738, 218)},
    {"rect": (497, 220, 1118, 522)},
    {"rect": (998, 781, 1406, 842)},
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

        tool.sleep(1)
        tool.click(183, 304, button=3)

        tool.sleep(1)
        tool.click(254, 425, button=3)

        tool.sleep(1)
        tool.click(1022, 548)

        tool.sleep(1)
        tool.click(1156, 521)

        tool.sleep(1)
        tool.click(1408, 830)



        tool.sleep(1)  # commit list, diff pane and status labels have settled
        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        img.draw_box(BOXES)
        img.save("rescan-repository.png")

        tool.sleep(1)
        tool.click(955, 495)


        tool.sleep(1)  # commit list, diff pane and status labels have settled
        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        img.draw_box(BOXES1)
        img.save("commit-selectively.png")

        tool.sleep(1)
        tool.click(1220, 761)


        tool.sleep(1)  # commit list, diff pane and status labels have settled
        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        img.draw_box(BOXES2)
        img.save("git-add-p-hunks.png")


        tool.sleep(1)
        tool.press("Escape")

        tool.sleep(1)
        tool.press("Escape")

        tool.sleep(1)
        tool.press("Escape")

        tool.sleep(1)
        tool.press("Escape")

        tool.sleep(1)
        tool.press("Escape")

        tool.sleep(1)
        tool.click(321, 900)

        tool.sleep(1)
        tool.click(1081, 537)

        tool.sleep(1)
        tool.press("Escape")
        tool.sleep(.5)

    finally:
        tool.sleep(1)
        # 4. close the tool - even when a step above failed
        tool.close()


if __name__ == "__main__":
    main()
