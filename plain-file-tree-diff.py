"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
from capture_lib import Tool, capture, image_new, repo

BOXES = [
    {"rect": (517, 148, 1384, 808)},
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

        tool.click(230, 165, button=3)   # right-click the commit row

        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.2)
        tool.press("Return")              # activate

        # 3. take the picture (this shot has no red boxes)
        tool.sleep(.2)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        img.draw_box(BOXES)
        img.add_text(645, 144, " plain diff ", 25, border=1, fill="red")
        img.crop(517, 148, 1384, 808)


        plain = img.copy()
        img.draw_box(BOXES)
        plain.save("plain.png")

        tool.sleep(.2)
        tool.click(664, 353)
        # 3. take the picture (this shot has no red boxes)
        tool.sleep(.2)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        img.draw_box(BOXES)
        img.add_text(645, 144, " filewise diff ", 25, border=1, fill="red")
        img.crop(517, 148, 1384, 808)

        filewise = img.copy()
        filewise.save("filewise.png")

        tool.sleep(.2)
        tool.click(770, 351)
        # 3. take the picture (this shot has no red boxes)
        tool.sleep(.2)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        img.draw_box(BOXES)
        img.add_text(645, 144, " treewise diff ", 25, border=1, fill="red")
        img.crop(517, 148, 1384, 808)

        treewise = img.copy()
        treewise.save("treewise.png")

        width = 1384-517
        height = 808-148
        extra = 10

        final = image_new((width+extra*3), height)

        x = 0
        y = 0
        final.add(x, y, plain)
        x = x + width + 10
        final.add(x, y, filewise)
        x = x + width + 10
        final.add(x, y, treewise)
        treewise.save("plain-file-tree-diff.png")



        tool.sleep(.5)
        tool.press("Escape")

        tool.sleep(.5)
        tool.press("Escape")

    finally:
        # 4. close the tool - even when a step above failed
        tool.close()


if __name__ == "__main__":
    main()
