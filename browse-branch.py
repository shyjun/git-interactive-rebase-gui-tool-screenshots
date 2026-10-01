"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
from capture_lib import Tool, capture, repo, image_new

BOXES = [
    {"rect": (349, 187, 669, 332)},
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
        tool.click(1288, 831)

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Return")              # activate

        tool.sleep(.5)
        # 3. take the picture (this shot has no red boxes)
        branch_config = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        branch_config.crop(756, 362, 1144, 600)
        tool.sleep(.5)

        tool.sleep(.1)
        tool.press("o")
        tool.sleep(.1)
        tool.press("r")
        tool.sleep(.1)
        tool.press("i")
        tool.sleep(.1)
        tool.press("g")
        tool.sleep(.1)
        tool.press("i")
        tool.sleep(.1)
        tool.press("n")
        tool.sleep(.1)
        tool.press("slash")
        tool.sleep(.1)
        tool.press("m")
        tool.sleep(.1)
        tool.press("a")
        tool.sleep(.1)
        tool.press("s")
        tool.sleep(.1)
        tool.press("t")
        tool.sleep(.1)
        tool.press("e")
        tool.sleep(.1)
        tool.press("r")

        tool.sleep(.5)
        tool.click(1076, 556)

        tool.sleep(.5)
        tool.click(359, 197, button=3)

        tool.sleep(.5)
        # 3. take the picture (this shot has no red boxes)
        img = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        tool.sleep(.5)
        img.draw_box(BOXES)

        x,y=branch_config.getsize()

        img.resize(70, 70)
        x2,y2 = img.getsize()

        final = image_new(x+x2, y2)
        final.add(0, (y2/2)-50, branch_config)
        final.add(x,0, img)

        img.save("browse-branch.png")

        tool.sleep(.5)
        tool.press("Escape")
        tool.sleep(.5)
        tool.press("Escape")
        tool.sleep(.5)
        tool.press("Escape")
    finally:
        tool.sleep(.5)
        # 4. close the tool - even when a step above failed
        tool.close()


if __name__ == "__main__":
    main()
