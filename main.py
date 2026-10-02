#!/usr/bin/env python3
"""Screenshot robot for git-interactive-rebase-gui-tool.

What it does, in plain words:

  1. Checks that the screenshots repo is clean and ready to receive images
  2. Prepares a private work folder (.work/) with settings, logs and markers
  3. Clones your vim repo into /tmp (only the first time)
  4. Runs every capture script - one script = one screenshot
  5. Copies the new images into screenshots/ on a fresh branch and commits them

How to run it (from this folder):

    python3 main.py
"""
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
import time

# ======================== settings ========================
# The tool repo the robot launches (this repo only holds images and the robot).
TOOL_ROOT = Path("/home/snarangaprath/WORK/git-interactive-rebase-gui-tool")

# The repo that provides the commit history for the screenshots.
VIM_REPO = "/home/snarangaprath/WORK/vim"

# The clone the tool is opened against. Wiped on reboot, re-cloned automatically.
CLONE_DIR = Path("/tmp/screenshot_robot_vim")

# The exact commit every screenshot is taken at (the HEAD shown in the docs shots).
REF_COMMIT = "f893b2a853e1559d51291a3731d6cd6df79f1a51"

# Your live tool settings are copied from here (font, theme, column widths ...).
USER_CONFIG = Path.home() / ".config"

# One line per screenshot: (script, [images the script must produce]).

SCENES = []
'''
SCENES += [("rephrase-and-drop-commit.py", ["rephrase-and-drop-commit.png"])]
SCENES += [("mark-commits.py", ["mark-commits.png"])]
SCENES += [("tag-commit.py", ["tag-commit.png"])]
SCENES += [("external-tools-dialog.py", ["external-tools-dialog.png"])]
SCENES += [("font-selection-dialog.py", ["font-selection-dialog.png"])]
SCENES += [("search-filter.py", ["search-filter.png"])]
SCENES += [("diff-search.py", ["diff-search.png"])]
SCENES += [("squash-context-menu.py", ["squash-context-menu.png"])]
SCENES += [("squash-dialogue.py", ["squash-dialogue.png"])]
SCENES += [("split-context-menu.py", ["split-context-menu.png"])]
SCENES += [("reset-options.py", ["reset-options.png"])]
SCENES += [("browse-file-log.py", ["browse-file-log.png"])]
SCENES += [("browse-reflog.py", ["browse-reflog.png"])]
SCENES += [("browse-stash.py", ["browse-stash.png"])]
SCENES += [("consolidated-diff.py", ["consolidated-diff.png"])]
SCENES += [("dark-theme.py", ["dark-theme.png"])]
SCENES += [("blame-a-file.py", ["blame-a-file.png"])]
SCENES += [("browse-tags.py", ["browse-tags.png"])]
SCENES += [("rebase-options.py", ["rebase-options.png"])]
SCENES += [("add-untracked-files.py", ["add-untracked-files.png"])]
SCENES += [("commit-viewer-and-file-operations-menu.py", ["commit-viewer-and-file-operations-menu.png"])]
SCENES += [("main-interface.py", ["main-interface.png"])]
SCENES += [("plain-file-tree-diff.py", ["plain-file-tree-diff.png"])]
SCENES += [("split-each-to-separate.py", ["split-each-to-separate.png"])]
SCENES += [("split-all-to-separate.py", ["split-all-to-separate.png"])]
SCENES += [("drag-reorder.py", ["drag-reorder.png"])]
SCENES += [("split-move-single-file-1.py", ["split-move-single-file-1.png", "split-move-single-file-2.png"])]
SCENES += [("rescan-repository.py", ["rescan-repository.png", "commit-selectively.png"])]
SCENES += [("refine-changes-in-file.py", ["refine-changes-in-file-1.png", "refine-changes-in-file-2.png"])]
SCENES += [("viewer-mode.py", ["viewer-mode.png"])]
SCENES += [("head-commits.py", ["head-commits.png"])]
SCENES += [("browse-branch.py", ["browse-branch.png"])]
SCENES += [("main-menus.py", ["main-menus.png"])]
SCENES += [("find-merge-base.py", ["find-merge-base.png"])]
SCENES += [("pr-diff.py", ["pr-diff.png"])]
'''

SCENES += [("staged-unstaged-changes-warning.py", ["staged-unstaged-changes-warning.png"])]



# SCENES += [("test.py", ["test.png"])]

# ==========================================================

HERE = Path(__file__).resolve().parent
SCREENSHOTS_REPO = HERE  # the robot lives in the screenshots repo itself
SHOTS_DIR = SCREENSHOTS_REPO / "screenshots"  # where the .webp files are committed
WORK_DIR = HERE / ".work"
CONFIG_DIR = WORK_DIR / "config"
MARKER_DIR = WORK_DIR / "markers"
LOG_DIR = WORK_DIR / "logs"
OUT_DIR = WORK_DIR / "out"
BRANCH = f"screenshots-{date.today():%Y%m%d}"


def say(message):
    print(f"\n=== {message}", flush=True)


def fail(message):
    print(f"\nERROR: {message}", file=sys.stderr, flush=True)
    sys.exit(1)


def run(args, cwd=None, check=True):
    """Run a command quietly; print its output when it fails."""
    print(f"  $ {' '.join(str(a) for a in args)}", flush=True)
    res = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True)
    if check and res.returncode != 0:
        fail(f"command failed ({res.returncode}):\n{res.stdout}\n{res.stderr}")
    return res


def run_live(args, cwd=None, check=True):
    """Run a command with its output going straight to the terminal."""
    print(f"  $ {' '.join(str(a) for a in args)}", flush=True)
    res = subprocess.run([str(a) for a in args], cwd=cwd)
    if check and res.returncode != 0:
        fail(f"command failed with code {res.returncode}")
    return res


def seed_settings():
    """Copy your tool settings into .work/config, with capture-friendly tweaks:

    - the robot's window must not start maximized and must not restore your
      saved position (we place and size the window ourselves)
    - browse windows (file log, viewers) open maximized by default, so every
      scene shows them full-screen without per-scene geometry fiddling
    - the blame dialog opens maximized too (harvested from a real double-click
      title-bar maximize - restoreGeometry replays size AND maximized state)
    - the startup update check is disabled so no "Update available" label
      can appear in a screenshot
    """
    src = USER_CONFIG / "shyjun" / "GitInteractiveRebase.conf"
    dst = CONFIG_DIR / "shyjun" / "GitInteractiveRebase.conf"
    dst.parent.mkdir(parents=True, exist_ok=True)
    # blame/geometry captured while the dialog was maximized (1920x1042 frame)
    blame_maximized = (
        r"@ByteArray(\x1\xd9\xd0\xcb\0\x3\0\0\0\0\0\0\0\0\0\0\0\0\a\x7f\0\0\x4\x11\0\0\x1\\"
        r"\0\0\0\xc7\0\0\x6\xaf\0\0\x3\xcc\0\0\0\0\x2\0\0\0\a\x80\0\0\0\0\0\0\0\x1d\0\0"
        r"\a\x7f\0\0\x4\x11)"
    )
    lines = src.read_text().splitlines() if src.exists() else []
    out, section, seen_startup, seen_browse_max = [], "", False, False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped
            out.append(line)
            continue
        if section == "[General]" and stripped.startswith("font_size="):
            line = "font_size=11"  # zoom 110% - the zoom level all docs shots use
        if section == "[General]" and stripped.startswith("theme="):
            line = "theme=light"  # docs shots are light; dark-theme.py switches in-session
        if section == "[main]" and stripped.startswith("geometry"):
            continue  # saved window position - not wanted, we size the window ourselves
        if section == "[main]" and stripped.startswith("isMaximized"):
            line = "isMaximized=false"
        if section == "[blame]" and stripped.startswith("geometry="):
            line = "geometry=" + blame_maximized  # dialog restores maximized
        if section == "[browse]" and stripped.startswith("isMaximized"):
            line = "isMaximized=true"  # browse windows restore maximized (closeEvent re-saves true)
            seen_browse_max = True
        if section == "[startup]" and stripped.startswith("auto_check_updates"):
            line = "auto_check_updates=false"
            seen_startup = True
        out.append(line)
    if not seen_startup:
        out += ["", "[startup]", "auto_check_updates=false"]
    if not seen_browse_max:
        out += ["", "[browse]", "isMaximized=true"]
    dst.write_text("\n".join(out) + "\n")

    theme_dir = USER_CONFIG / "git-interactive-rebase-gui-tool"
    if theme_dir.exists():
        shutil.copytree(theme_dir, CONFIG_DIR / theme_dir.name, dirs_exist_ok=True)
    # The startup update check reads this file (not shyjun's). A visible
    # "Update(...) available" label would contaminate the screenshots and
    # depends on the network, so force the check off here too.
    upd = CONFIG_DIR / "git-interactive-rebase-gui-tool" / "config.conf"
    upd.parent.mkdir(parents=True, exist_ok=True)
    lines = upd.read_text().splitlines() if upd.exists() else []
    out, section, seen_upd = [], "", False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped
            out.append(line)
            continue
        if section == "[startup]" and stripped.startswith("auto_check_updates"):
            line = "auto_check_updates=false"
            seen_upd = True
        out.append(line)
    if not seen_upd:
        out += ["", "[startup]", "auto_check_updates=false"]
    upd.write_text("\n".join(out) + "\n")


def step1_preflight():
    say("Step 1/5 preflight: screenshots repo is clean")
    if not os.environ.get("DISPLAY"):
        fail("DISPLAY is not set - run this on the laptop with the desktop session")
    if not (TOOL_ROOT / "git_interactive_rebase.py").exists():
        fail(f"tool entry point not found at {TOOL_ROOT / 'git_interactive_rebase.py'}")
    if not (SCREENSHOTS_REPO / ".git").exists():
        fail(f"screenshots repo not found at {SCREENSHOTS_REPO}")
    res = run(["git", "status", "--porcelain"], cwd=SCREENSHOTS_REPO)
    if res.stdout.strip():
        fail(f"screenshots repo has uncommitted changes - commit or stash them first:\n{res.stdout}")


def step2_work_folder():
    say("Step 2/5 clear previous logs and captures, seed settings")
    if MARKER_DIR.exists():
        shutil.rmtree(MARKER_DIR)  # fresh marker dir: the "Previous Run" dialog can never fire
    MARKER_DIR.mkdir(parents=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # start every run from scratch: stale logs/captures could be mistaken
    # for this run's output (step4's existence checks, step5's conversion)
    stale = sorted(LOG_DIR.glob("*.log")) + sorted(OUT_DIR.iterdir())
    for path in stale:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    if stale:
        print(f"  cleared {len(stale)} previous log/capture files")
    seed_settings()
    print(f"  seeded {CONFIG_DIR}")


def step3_clone():
    say("Step 3/5 prepare reference repo (clone of your vim repo)")
    if not (CLONE_DIR / ".git").exists():
        if CLONE_DIR.exists():
            shutil.rmtree(CLONE_DIR)
        run_live(["git", "clone", VIM_REPO, str(CLONE_DIR)])
    else:
        res = run(["git", "-C", CLONE_DIR, "remote", "get-url", "origin"])
        if res.stdout.strip() != VIM_REPO:
            fail(f"{CLONE_DIR} was cloned from {res.stdout.strip()!r}, not {VIM_REPO!r} - delete it and rerun")
    run(["git", "-C", CLONE_DIR, "cat-file", "-e", f"{REF_COMMIT}^{{commit}}"])
    print(f"  clone ready at {CLONE_DIR}")


def step4_scenes():
    say("Step 4/5 run capture scenes")
    for script, images in SCENES:
        print(f"\n  --- {script} ---", flush=True)
        time.sleep(.1)
        res = run_live([sys.executable, str(HERE / script)], cwd=HERE, check=False)
        if res.returncode != 0:
            for log in sorted(LOG_DIR.glob("*.log")):
                tail = "".join(log.read_text().splitlines(True)[-40:])
                print(f"\n--- tail of {log.name} ---\n{tail}", file=sys.stderr)
            fail(f"{script} failed with code {res.returncode}")
        for image in images:
            if not (OUT_DIR / image).exists():
                fail(f"{script} did not produce {image}")


def step5_publish():
    say("Step 5/5 convert captures to webp, save images to screenshots/")
    images = [image for _, image_list in SCENES for image in image_list]  # the .png captures
    # One single batch command over every captured .png - temporary step:
    # once the docs move to .png for good, drop this and publish the .pngs.
    # Underscore files are working images (wip/blank/intermediates) a scene
    # never saved - they are not captures and must never be published.
    pngs = sorted(p for p in OUT_DIR.glob("*.png") if not p.name.startswith("_"))
    if not pngs:
        fail(f"no captured .png files in {OUT_DIR}")
    run(["mogrify", "-format", "webp", "-quality", "90"] + [p.name for p in pngs], cwd=OUT_DIR)
    webps = [Path(image).with_suffix(".webp").name for image in images]
    for image in images:
        webp = Path(image).with_suffix(".webp")
        if not (OUT_DIR / webp).exists():
            fail(f"conversion did not produce {webp.name}")
    # Move to the target branch first: a fresh branch off the current HEAD (the
    # robot and the image layout live in this repo, so branching from HEAD keeps
    # them), forcing away any copies a previous (possibly interrupted) run left.
    # step1 guarantees the repo started clean, so -f only undoes our own copies.
    run(["git", "checkout", "-f", "-B", BRANCH], cwd=SCREENSHOTS_REPO)
    SHOTS_DIR.mkdir(parents=True, exist_ok=True)
    for webp in webps:
        shutil.copy(OUT_DIR / webp, SHOTS_DIR / webp)
        print(f"  copied {webp}")
    run(["git", "add", "--"] + [f"screenshots/{webp}" for webp in webps], cwd=SCREENSHOTS_REPO)
    res = run(["git", "commit", "-m", "capture: " + ", ".join(webps)], cwd=SCREENSHOTS_REPO, check=False)
    if res.returncode != 0 and "nothing to commit" not in res.stdout + res.stderr:
        fail(f"commit failed:\n{res.stdout}\n{res.stderr}")
    print(f"  committed on {BRANCH}")


def main():
    say("Screenshot robot starting")
    step1_preflight()
    step2_work_folder()
    step3_clone()
    step4_scenes()
    step5_publish()
    say("Done")


if __name__ == "__main__":
    main()
