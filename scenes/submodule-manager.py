"""Capture submodule-manager.png — the Submodules dialog with registered
submodules, one of which has a pointer change.

Run it through main.py; it prepares the clone, settings and publishing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, capture, repo

BOXES = [
    {"rect": (510, 282, 1410, 682)},
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

# The one we advance to show "pointer changed" (2nd entry, lib/log)
ADVANCE_PATH = SUBMODULES[1][1]


def main():
    repo.reset_to_base()

    for url, path in SUBMODULES:
        repo.run("-c", "protocol.file.allow=always", "submodule", "add", url, path)

    repo.run("add", ".gitmodules")
    repo.run("commit", "-m", "add test submodules")

    with open(repo.path / ADVANCE_PATH / "readme.txt", "a") as fh:
        fh.write("modified\n")
    sub_log = str(repo.path / ADVANCE_PATH)
    repo.run("-C", sub_log, "add", "readme.txt")
    repo.run("-C", sub_log, "commit", "-m", "advance pointer")

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
            description="Submodules dialog: 7 registered libs, lib/log pointer changed",
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
