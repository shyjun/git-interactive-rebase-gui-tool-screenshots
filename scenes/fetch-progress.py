"""Prepare the throwaway "old vim" repo and open the tool on it.

Not registered in SCENES - run it directly from the repo root:

    python3 scenes/fetch-progress.py

What it does:

  1. builds /tmp/screenshot_robot_vim_legacy with only vim 7.0002's commit
     (a depth=1 fetch of the hardcoded SHA, so no discovery clone is needed),
     plus a local origin/old-history ref so the Pull options pass the tool's
     upstream check instead of bailing out instantly
  2. opens the tool there, maximized, with the Origin group visible
  3. leaves the tool open so you can trigger fetch/pull and capture the
     progress dialog yourself
  4. closes the tool and deletes the /tmp repo when you close the window
     (or press Ctrl+C in this terminal)

The existing origin-options.webp / push-dialog.webp are untouched - this
script only provides the slow-fetch instance for the progress shot.
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, _sh_ok, capture_screen
from main import seed_settings

LEGACY_REPO = Path("/tmp/screenshot_robot_vim_legacy")
VIM_URL = "https://github.com/vim/vim.git"
# vim 7.0002 - the 10th commit on origin/HEAD's first-parent chain.
OLD_COMMIT = "f4b8e57ffd048f9ca46dd7618939ba7a1b2294ec"


def prepare_legacy_repo():
    """Create the /tmp repo per the block-2 recipe (safe to re-run)."""
    if LEGACY_REPO.exists():
        shutil.rmtree(LEGACY_REPO)
    LEGACY_REPO.mkdir(parents=True)

    def run(*args):
        _sh_ok(["git", "-C", str(LEGACY_REPO), *args], f"git {' '.join(args)}")

    run("init", "-q")
    run("remote", "add", "origin", VIM_URL)
    run("fetch", "--progress", "--depth=1", "origin", OLD_COMMIT)
    run("switch", "-c", "old-history", "FETCH_HEAD")
    # Give the tool an upstream to check for the Pull options (it refuses to
    # fetch when origin/<branch> is missing). The ref is local only - GitHub
    # has no old-history branch - but it lets "Fetch and merge / rebase" run
    # the slow fetch under the "Git Pull" progress dialog.
    run("update-ref", "refs/remotes/origin/old-history", OLD_COMMIT)
    run("config", "branch.old-history.remote", "origin")
    run("config", "branch.old-history.merge", "refs/heads/old-history")
    print(f"  repo ready: {LEGACY_REPO} (old-history @ {OLD_COMMIT[:8]})", flush=True)


def show_origin_group(tool):
    """Configure -> Show/Hide -> Show Origin, like origin-options.py."""
    tool.click_config_button()
    tool.sleep(.2)
    tool.click(1472, 904)
    tool.sleep(.2)
    tool.press("Down")
    tool.sleep(.2)
    tool.press("Return")
    tool.sleep(.5)

BOXES = [
    {"rect": (720, 370, 1180, 592)},
    ]

def main():
    prepare_legacy_repo()
    seed_settings()  # same theme/font/visible groups as every other scene

    tool = Tool(args=[], log_name="fetch-progress.log", repo_path=LEGACY_REPO)
    try:
        tool.wait_for_window()
        tool.maximize()
        tool.sleep(1)

        tool.sleep(.4)
        tool.click(1566, 1029)

        tool.sleep(.2)
        tool.press("Down")

        tool.sleep(.2)
        tool.press("Right")

        tool.sleep(.2)
        tool.press("Return")

        tool.sleep(.5)
        tool.click(532, 973)

        tool.sleep(.5)

        tool.sleep(.5)
        tool.click(1131, 603)


        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)
        tool.sleep(.5)



        # menu open, window still maximized
        img = capture_screen(
            0, 0, 1920, 1042,          # whole screen, taskbar included
            description="Origin group with git fetch/pull menu open",
        )

        img.draw_box(BOXES)
        img.save("fetch-progress.png")

        tool.sleep(.5)
        tool.sleep(.5)



    finally:
        tool.close()
        shutil.rmtree(LEGACY_REPO, ignore_errors=True)
        print(f"  removed {LEGACY_REPO}", flush=True)


if __name__ == "__main__":
    main()
