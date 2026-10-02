"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
from capture_lib import Tool, capture, repo

BOXES = [
    {"rect": (108, 960, 479, 1012)},
    {"rect": (733, 1, 849, 31)},
    {"rect": (297, 87, 508, 184)},
    ]

def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 1b. give the stash browser rows to show - one stash per file, the same
    #     three every run (reset_to_base never touches refs/stash, so clear first)
    repo.run("stash", "clear")
    for name in ("src/version.c", "src/spell.c", "src/dict.c"):
        with open(repo.path / name, "a") as fh:
            fh.write("////\n")
        repo.run("stash")

    # 2. open the tool: HEAD~13 shows the 13 newest commits (the list excludes
    #    the base commit itself, so the arg must be one further back)
    tool = Tool(args=["HEAD~13"], log_name="mark-commits.log")
    # everything below runs inside the finally - no matter which step fails,
    # the tool gets closed and cannot poison the next run
    try:
        tool.wait_for_window()
        tool.maximize()

        tool.sleep(1)
        tool.click(1288, 831)

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Return")              # activate

        tool.sleep(.5)
        tool.click(307, 96, button=3)

        tool.sleep(.5)
        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        img.draw_box(BOXES)
        img.save("browse-stash.png")

        tool.press("Escape")
    finally:
        # 4. close the tool - even when a step above failed
        tool.close()


if __name__ == "__main__":
    main()
