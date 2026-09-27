"""Capture diff-search.webp - commit viewer with the diff search bar.

Right-click a row -> View Commit, then click the search bar's config
options in the viewer. Run it through main.py.
"""
from capture_lib import Tool, capture, repo

BOXES = [
    {"rect": (528, 360, 1212, 411)},
    {"rect": (1213, 363, 1320, 406)},
    {"rect": (1329, 364, 1508, 517)},
    ]

def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 2. open the tool: HEAD~13 shows the 13 newest commits (the list excludes
    #    the base commit itself, so the arg must be one further back)
    tool = Tool(args=["HEAD~13"], log_name="diff-search.log")
    # everything below runs inside the finally - no matter which step fails,
    # the tool gets closed and cannot poison the next run
    try:
        tool.wait_for_window()
        tool.maximize()

        tool.sleep(1)
        tool.click(230, 165, button=3)

        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.2)
        tool.press("Return")

        tool.sleep(.5)
        tool.click(1345, 384)

        tool.sleep(.5)
        # 3. take the picture, then crop to the search bar + open config menu
        img = capture(
            tool,
            description="commit viewer with the diff search bar's config options open",
            size=(1920, 1042),
        )
        img.draw_box(BOXES)
        img.crop(500, 340, 1528, 537)
        img.save("diff-search.png")

        tool.sleep(.5)
        tool.press("Escape")
    finally:
        tool.sleep(.5)
        # 4. close the tool - even when a step above failed
        tool.close()


if __name__ == "__main__":
    main()
