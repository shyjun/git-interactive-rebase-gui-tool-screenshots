"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
from capture_lib import Tool, capture, repo

BOXES=[{"rect": (692, 717, 822, 770)}]

def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 2. open the tool: HEAD~13 shows the 13 newest commits (the list excludes
    #    the base commit itself, so the arg must be one further back)
    tool = Tool(args=["HEAD~13"], log_name="test.log")
    tool.wait_for_window()
    tool.set_size(1506, 952)  # exact size of the original screenshot, title bar included
    tool.sleep(4)  # commit list, diff pane and status labels have settled

    # 3. take the picture (this shot has no red boxes)
    capture(
        tool,
        name="test.webp",
        description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
        boxes=BOXES,
        size=(1506, 952),
    )

    # 4. close the tool again
    tool.close()


if __name__ == "__main__":
    main()
