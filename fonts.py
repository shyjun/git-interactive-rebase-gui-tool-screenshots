"""Capture fonts.webp - test shot: Git Status dialog over the main window.

Run it through main.py; it prepares the clone, settings and publishing.
"""
from capture_lib import Tool, capture, repo

# Red frame around the Git Status button, measured off the button itself.
BOXES = [{"rect": (692, 717, 822, 770)}]


def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 2. open the tool: HEAD~13 shows the 13 newest commits (the list excludes
    #    the base commit itself, so the arg must be one further back)
    tool = Tool(args=["HEAD~13"], log_name="fonts.log")
    tool.wait_for_window()
    tool.set_size(1506, 952)  # exact size of the screenshot, title bar included
    tool.sleep(4)  # commit list, diff pane and status labels have settled

    # 3. click the Git Status button (center of the box above) and wait for
    #    the "git status" dialog it opens
    tool.click(757, 743)
    tool.wait_for_name("git status")
    tool.sleep(0.5)

    # 4. take the picture: main window + dialog, with the red box
    capture(
        tool,
        name="fonts.webp",
        description="git status dialog open over the main window",
        boxes=BOXES,
        size=(1506, 952),
    )

    # 5. close the dialog, then the tool
    tool.press("Escape")
    tool.close()


if __name__ == "__main__":
    main()
