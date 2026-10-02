"""Capture add-untracked-files.png - the Add Untracked File(s) dialog.

Run it through main.py; it prepares the clone, settings and publishing.
"""
import shutil

from capture_lib import Tool, capture, repo

BOXES = [
    {"rect": (608, 235, 844, 277)},
    {"rect": (966, 729, 1291, 793)},
    {"rect": (600, 299, 1165, 465)},
    ]

BOXES1 = [
    {"rect": (646, 256, 1253, 706)},
    ]

BOXES2 = [
    {"rect": (673, 749, 1375, 796)},
    {"rect": (522, 294, 1135, 462)},
    ]


def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 1b. seven new_*.c copies show up as untracked files for the dialog
    #     (reset_to_base's git clean -fdx removes them again next run)
    for stem in ("gui", "list", "screen", "json", "regexp", "indent", "kitty"):
        shutil.copyfile(repo.path / "src" / f"{stem}.c",
                        repo.path / "src" / f"new_{stem}.c")

    # 2. open the tool: HEAD~13 shows the 13 newest commits (the list excludes
    #    the base commit itself, so the arg must be one further back)
    tool = Tool(args=["HEAD~13"], log_name="add-untracked-files.log")
    # everything below runs inside the finally - no matter which step fails,
    # the tool gets closed and cannot poison the next run
    try:
        tool.wait_for_window()
        tool.maximize()

        tool.sleep(1)
        tool.click(1288, 831)             # Repo button

        tool.sleep(.5)
        for _ in range(10):               # menu: ... 6th item from the bottom
            tool.press("Up")
            tool.sleep(.1)

        tool.sleep(.2)
        tool.press("Return")              # Add Untracked File(s)...

        tool.sleep(1)
        tool.click(662, 254)

        tool.sleep(1.5)
        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="Repo menu -> Add Untracked File(s): seven new_*.c files listed",
            size=(1920, 1042),
        )
        img.draw_box(BOXES)
        img.save("add-untracked-files.png")

        tool.sleep(1)
        tool.click(1087, 768)

        tool.sleep(1)
        tool.click(1072, 541)

        tool.sleep(1)
        tool.click(1288, 831)

        tool.sleep(1)
        tool.click(1337, 493)

        tool.sleep(1.5)
        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="Repo menu -> Add Untracked File(s): seven new_*.c files listed",
            size=(1920, 1042),
        )
        img.draw_box(BOXES1)
        img.save("handle-staged-changes.png")

        tool.sleep(1)
        tool.click(940, 394)

        tool.sleep(1.5)
        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="Repo menu -> Add Untracked File(s): seven new_*.c files listed",
            size=(1920, 1042),
        )
        img.draw_box(BOXES2)
        img.save("commit_or_unstage-staged-selectively.png")


        tool.sleep(.5)
        tool.press("Escape")

        tool.sleep(.5)
        tool.press("Escape")

    finally:
        # 4. close the tool - even when a step above failed
        tool.sleep(.5)
        tool.close()


if __name__ == "__main__":
    main()
