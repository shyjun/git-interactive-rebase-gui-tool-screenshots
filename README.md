# git-interactive-rebase-gui-tool-screenshots

Screenshots and visual documentation for git-interactive-rebase-gui-tool.

## Layout

- `screenshots/` - all documentation images (`.webp`), linked from the tool's
  `docs/screenshots.md`
- `main.py` - screenshot robot entry point (5 steps: preflight, work folder,
  clone, capture, publish)
- `capture_lib.py` - robot plumbing (window control, annotation drawing)
- `head-commits.py`, `main-interface.py` - one capture script per screenshot

## Running the robot

Needs an X11 desktop session with `xdotool`, `xdg` tools and ImageMagick
installed. From the repo root:

    python3 main.py                # capture, commit and push a fresh branch
    SKIP_PUSH=1 python3 main.py    # capture and commit locally, no push

Images land in `screenshots/` and are committed on a `screenshots-YYYYMMDD`
branch. Settings (tool repo location, pinned commit, scene list) live at the
top of `main.py`. The robot refuses to run on a dirty repo.
