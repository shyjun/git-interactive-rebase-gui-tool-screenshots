"""Capture update-available.png - the startup "Update available" status-bar label.

Requires the tool copy in .work/ (run capture.sh, or its copy steps). The
script amends the copy's HEAD so the startup check sees a local sha that
differs from the remote, then restores the copy and the auto-check setting.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from capture_lib import Tool, capture, _sh_ok, repo
from main import CONFIG_DIR, TOOL_ROOT

BOXES = [
    {"rect": (1152, 1016, 1368, 1037)},
    ]

CONFIG_FILE = CONFIG_DIR / "git-interactive-rebase-gui-tool" / "config.conf"


def set_auto_check(enabled):
    value = "true" if enabled else "false"
    lines = CONFIG_FILE.read_text().splitlines() if CONFIG_FILE.exists() else []
    out, section, seen = [], "", False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped
            out.append(line)
            continue
        if section == "[startup]" and stripped.startswith("auto_check_updates"):
            line = f"auto_check_updates={value}"
            seen = True
        out.append(line)
    if not seen:
        out += ["", "[startup]", f"auto_check_updates={value}"]
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text("\n".join(out) + "\n")


def main():
    repo.reset_to_base()
    set_auto_check(True)
    _sh_ok(["git", "-C", str(TOOL_ROOT), "commit", "--amend", "--no-edit"], "amend tool copy")

    tool = Tool(args=[], log_name="update-available.log")
    try:
        tool.wait_for_window()
        tool.maximize()

        tool.sleep(.5)
        tool.click(1426, 1029)

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.1)
        tool.press("Up")

        tool.sleep(.2)
        tool.press("Return")              # activate

        tool.sleep(8)
        img = capture(
            tool,
            description="startup update check: Update(<sha>) available in the status bar",
            size=(1920, 1042),
        )

        img.draw_box(BOXES)
        img.save("update-available.png")
        tool.sleep(.5)

    finally:
        tool.sleep(.5)
        tool.close()
        _sh_ok(["git", "-C", str(TOOL_ROOT), "reset", "--hard", "origin/master"], "reset tool copy")
        set_auto_check(False)


if __name__ == "__main__":
    main()
