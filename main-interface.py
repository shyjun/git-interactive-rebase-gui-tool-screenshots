"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
from capture_lib import Tool, capture, repo

BOXES = [
    {"rect": (587, 5, 1091, 28)},
    {"rect": (4, 68, 1148, 788)},
    {"rect": (1149, 70, 1914, 788)},
    {"rect": (1158, 230, 1912, 284)},
    {"rect": (1477, 1006, 1906, 1037)},
    {"rect": (1346, 1008, 1473, 1040)},
    {"rect": (2, 1012, 162, 1037)},
    {"rect": (4, 808, 137, 861)},
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

        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )

        img.draw_box(BOXES)
        img.save("main-interface.png")

    finally:
        # 4. close the tool - even when a step above failed
        tool.close()


if __name__ == "__main__":
    main()
