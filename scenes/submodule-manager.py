"""Capture submodule-manager.png — the Submodules dialog with registered
submodules, one of which has a pointer change.

Run it through main.py; it prepares the clone, settings and publishing.
"""
import os
import subprocess as _sp
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, capture, repo

BOXES = [
    {"rect": (510, 282, 1410, 682)},
    ]

GIT_ENV = dict(
    os.environ,
    GIT_AUTHOR_NAME="bot",
    GIT_AUTHOR_EMAIL="bot@x",
    GIT_COMMITTER_NAME="bot",
    GIT_COMMITTER_EMAIL="bot@x",
)


def _mini_repo(path, content):
    d = Path(path)
    d.mkdir(parents=True)
    (d / "readme.txt").write_text(content)
    _sp.run(["git", "init"], cwd=d, capture_output=True, check=True)
    _sp.run(["git", "add", "-A"], cwd=d, capture_output=True, check=True)
    _sp.run(["git", "commit", "-m", "init"], cwd=d, capture_output=True, check=True, env=GIT_ENV)


def main():
    repo.reset_to_base()

    for d in (Path(f"/tmp/submod-{i}") for i in (1, 2, 3)):
        if d.exists():
            shutil.rmtree(d)

    _mini_repo("/tmp/submod-1", "minimal submodule one")
    _mini_repo("/tmp/submod-2", "minimal submodule two")
    _mini_repo("/tmp/submod-3", "minimal submodule three")

    repo.run("-c", "protocol.file.allow=always", "submodule", "add", "/tmp/submod-1", "lib/submod1")
    repo.run("-c", "protocol.file.allow=always", "submodule", "add", "/tmp/submod-2", "lib/submod2")
    repo.run("-c", "protocol.file.allow=always", "submodule", "add", "/tmp/submod-3", "lib/submod3")
    repo.run("commit", "-m", "add test submodules")

    with open(repo.path / "lib" / "submod2" / "readme.txt", "a") as fh:
        fh.write("modified\n")
    repo.run("-C", str(repo.path / "lib" / "submod2"), "commit", "-am", "advance submod2")

    tool = Tool(args=["HEAD~13"], log_name="submodule-manager.log")
    try:
        tool.wait_for_window()
        tool.maximize()

        tool.sleep(1)
        tool.click_repo_button()

        tool.sleep(.5)
        for _ in range(16):
            tool.press("Down")
            tool.sleep(.1)

        tool.sleep(.2)
        tool.press("Return")

        tool.sleep(1.5)
        img = capture(
            tool,
            description="Submodules dialog: 3 registered, submod2 pointer changed",
            size=(1920, 1042),
        )
        img.draw_box(BOXES)
        img.save("submodule-manager.png")

        tool.sleep(.5)
        tool.press("Escape")

        tool.sleep(.5)
        tool.press("Escape")

    finally:
        tool.sleep(.5)
        tool.close()


if __name__ == "__main__":
    main()
