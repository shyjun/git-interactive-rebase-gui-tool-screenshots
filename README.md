# git-interactive-rebase-gui-tool-screenshots

Screenshots and visual documentation for git-interactive-rebase-gui-tool.

## Layout

- `screenshots/` - all documentation images (`.webp`), linked from the tool's
  `docs/screenshots.md`
- `scenes/main.py` - screenshot robot entry point (5 steps: preflight, work
  folder, clone, capture, publish)
- `lib/capture_lib.py` - robot plumbing (window control, annotation drawing)
- `config/` - committed capture settings (source of truth; copied to
  `.work/config` for every run)
- `scenes/head-commits.py`, `scenes/main-interface.py` - one capture script
  per screenshot
- `capture.sh` - refreshes the tool copy in `.work/` from the dev repo, then
  runs `scenes/main.py`

## Running the robot

Needs an X11 desktop session with `xdotool`, `xdg` tools and ImageMagick
installed. From the repo root:

    ./capture.sh         # refresh the tool copy, then capture and commit

or, with an existing tool copy:

    python3 scenes/main.py

A single scene can also be run directly (`python3 scenes/pr-diff.py`).

Images land in `screenshots/` and are committed on a `screenshots-YYYYMMDD`
branch. Settings (tool repo location, pinned commit, scene list) live at the
top of `scenes/main.py`. The robot refuses to run on a dirty repo.
