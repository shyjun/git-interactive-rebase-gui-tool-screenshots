"""Capture head-commits.webp - docs section 1 (Launch with HEAD~N).

Run it through main.py; it prepares the clone, settings and publishing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, capture, repo, image_new
def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 2. open the tool: HEAD~13 shows the 13 newest commits (the list excludes
    #    the base commit itself, so the arg must be one further back)
    tool = Tool(args=["HEAD~13"], log_name="rephrase.log")
    # everything below runs inside the finally - no matter which step fails,
    # the tool gets closed and cannot poison the next run
    try:
        tool.wait_for_window()
        tool.maximize()  # capture in maximized view (screen workarea)


        # echo "////" >> src/version.c
        with open(repo.path / "src" / "version.c", "a") as fh:
            fh.write("////\n")
        # git add src/version.c
        repo.run("add", "src/version.c")

        # echo "////" >> src/spell.c
        with open(repo.path / "src" / "spell.c", "a") as fh:
            fh.write("////\n")



        tool.sleep(1)  # commit list, diff pane and status labels have settled
        tool.click(370, 165, button=3)   # right-click the commit row
        tool.sleep(.5)  # commit list, diff pane and status labels have settled

        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)

        tool.press("Return")              # activate
        tool.sleep(1)

        # 3. take the picture (this shot has no red boxes)
        unstaged = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        unstaged.crop(704, 408, 1197, 553)

        #img.save("1.png")

        tool.press("Escape")


        # discard src/spell.c
        repo.run("checkout", "src/spell.c")


        tool.sleep(1)  # commit list, diff pane and status labels have settled
        tool.click(370, 165, button=3)   # right-click the commit row
        tool.sleep(.5)  # commit list, diff pane and status labels have settled

        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)
        tool.press("Down")
        tool.sleep(.1)

        tool.press("Return")              # activate
        tool.sleep(1)

        # 3. take the picture (this shot has no red boxes)
        staged = capture(
            tool,
            description="launched with HEAD~13: 13 newest commits, HEAD row selected, Plain Diff",
            size=(1920, 1042),
        )
        staged.crop(697, 401, 1203, 560)
        #staged.save("2.png")

        final = image_new(533, 379)
        final.add(10, 210, staged)
        final.add_text(38, 191, " staged changes warning ", 20, border=1, fill="red")
        final.add(10, 30, unstaged)
        final.add_text(38, 5, " unstaged changes warning ", 20, border=1, fill="red")

        final.save("staged-unstaged-changes-warning.png")


        tool.sleep(.1)
        tool.press("Escape")

        tool.sleep(.1)
        tool.press("Escape")


    finally:
        tool.sleep(.1)
        # 4. close the tool - even when a step above failed
        tool.close()




if __name__ == "__main__":
    main()
