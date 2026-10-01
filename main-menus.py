"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
from capture_lib import Tool, capture, repo

BOXES = [
    {"rect": (161, 160, 545, 578)},  # main context menu
    {"rect": (646, 793, 951, 958)},  # multi select menu
    {"rect": (1364, 892, 1593, 1041)},  # configure menu
    {"rect": (1587, 850, 1774, 1041)},  # configure submenu
    {"rect": (1234, 479, 1451, 817)},  # repo menu
    {"rect": (176, 508, 467, 570)},  # copy menu
    ]


def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 2. open the tool: HEAD~13 shows the 13 newest commits (the list excludes
    #    the base commit itself, so the arg must be one further back)
    tool = Tool(args=["HEAD~13"], log_name="head-commits.log")
    try:
        tool.wait_for_window()
        tool.maximize()
        tool.sleep(1)

        tool.sleep(1)
        tool.click(170, 170, button=3)

        tool.sleep(.2)
        # 3. take the picture (this shot has no red boxes)
        context_menu = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        context_menu.crop(161, 162, 545, 576)
        #context_menu.save("context-menu.png")

        tool.sleep(.2)
        tool.press("Escape")

        tool.sleep(.2)
        tool.click(278, 972)

        tool.sleep(.2)
        tool.click(27, 166)

        tool.sleep(.2)
        tool.click(27, 201)

        tool.sleep(.2)
        tool.click(808, 970)


        tool.sleep(.2)
        # 3. take the picture (this shot has no red boxes)
        multi_select_menu = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        multi_select_menu.crop(644, 778, 1275, 1000)
        #multi_select_menu.save("multi-select-menu.png")

        tool.sleep(.2)
        tool.press("Escape")

        tool.sleep(.2)
        tool.press("Escape")


        tool.sleep(1)
        tool.click(1289, 829)

        tool.sleep(.2)
        # 3. take the picture (this shot has no red boxes)
        repo_menu = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        repo_menu.crop(1233, 479, 1451, 857)
        #repo_menu.save("repo-menu.png")

        tool.sleep(.2)
        tool.press("Escape")

        tool.sleep(1)
        tool.click(1419, 1030)

        tool.sleep(.1)
        tool.press("Down")

        tool.sleep(.1)
        tool.press("Right")

        tool.sleep(.1)
        tool.press("Down")

        tool.sleep(.2)
        # 3. take the picture (this shot has no red boxes)
        configure_menu = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        configure_menu.add(161, 162, context_menu)
        configure_menu.add_text(259, 150-10-5, " main context menu ", 20, border=1, fill="red")

        configure_menu.add(644, 778, multi_select_menu)
        configure_menu.add_text(691, 798-10-10-10, " multi-select menu ", 20, border=1, fill="red")

        configure_menu.add(1233, 479, repo_menu)
        configure_menu.add_text(1276, 471-10-8, " repo menu ", 20, border=1, fill="red")

        configure_menu.add_text(1418, 880-13, " configure menu ", 20, border=1, fill="red")
        configure_menu.add_text(1616, 838-13, " configure sub menu ", 20, border=1, fill="red")

        configure_menu.draw_box(BOXES)

        configure_menu.add_text(462, 532, " copy menu ", 20, border=1, fill="red")

        configure_menu.save("configure-menu.png")

        tool.sleep(1)

    finally:
        tool.sleep(.2)
        # 4. close the tool - even when a step above failed
        tool.close()


if __name__ == "__main__":
    main()
