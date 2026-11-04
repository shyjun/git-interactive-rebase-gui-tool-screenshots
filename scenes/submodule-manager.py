"""Capture submodule-manager.png — the Submodules dialog with registered
submodules, one of which has a pointer change.

Run it through main.py; it prepares the clone, settings and publishing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, capture, repo

BOXES = [
    {"rect": (503, 283, 1397, 680)},
    ]

SUBMODULES = [
    ("https://github.com/DaveGamble/cJSON.git", "lib/cjson"),
    ("https://github.com/rxi/log.c.git", "lib/log"),
    ("https://github.com/akheron/jansson.git", "lib/jansson"),
    ("https://github.com/benhoyt/inih.git", "lib/inih"),
    ("https://github.com/rxi/vec.git", "lib/vec"),
    ("https://github.com/tidwall/hashmap.c.git", "lib/hashmap"),
    ("https://github.com/rxi/map.git", "lib/map"),
]

# The ones we advance to show "pointer changed" (log, inih, vec)
ADVANCE_PATHS = [SUBMODULES[1][1], SUBMODULES[3][1], SUBMODULES[4][1]]


def main():
    repo.reset_to_base()

    for url, path in SUBMODULES:
        repo.run("-c", "protocol.file.allow=always", "submodule", "add", url, path)

    repo.run("add", ".gitmodules")
    repo.run("commit", "-m", "add test submodules")

    for sub_path in ADVANCE_PATHS:
        with open(repo.path / sub_path / "readme.txt", "a") as fh:
            fh.write("modified\n")
        sub_log = str(repo.path / sub_path)
        repo.run("-C", sub_log, "add", "readme.txt")
        repo.run("-C", sub_log, "commit", "-m", "advance pointer")

    tool = Tool(args=["HEAD~13"], log_name="submodule-manager.log")
    try:
        tool.wait_for_window()
        tool.maximize()

        tool.sleep(1)
        tool.click_repo_button()

        tool.sleep(.5)
        for _ in range(18):
            tool.press("Down")
            tool.sleep(.1)

        tool.sleep(.2)
        tool.press("Return")

        tool.sleep(1.5)
        img = capture(
            tool,
            description="Submodules dialog: 7 libs, log/inih/vec pointer changed",
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
