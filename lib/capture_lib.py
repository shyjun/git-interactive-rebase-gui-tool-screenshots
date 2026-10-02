"""Plumbing for the screenshot robot.

Scene scripts import exactly what they need from here:

    from capture_lib import Tool, capture, image_new, repo

- repo.reset_to_base()   put the clone back to the pinned commit
- repo.run("stash", "clear")   run a git command in the clone
- repo.path / <file>     a file inside the clone (append with open(..., "a"))
- Tool(...)              open / control / close the GUI
- img = capture(tool, description=..., size=(W, H))
                         screenshot the tool window into a working image
- img.draw_box(boxes)    red frames / plates / labels (BOXES-style dicts)
- img.crop(x1,y1,x2,y2)  crop in place, inclusive corners = BOXES rect coords
- img.add(x, y, other)   composite another Image, its top-left at (x, y)
- img.add_text(x, y, "text", size, border=0)
                         red Times-Roman text, top-left at (x, y)
- img.save("name")       write <name>.png AND <name>.webp into .work/out/
- image_new(w, h)        blank white image to draw/compose on

Captures are plain pngs on disk; every op edits in place, so crop, draw
and compose in any order before img.save(). main.py step 5 still converts
and publishes the .webp batch.

You normally never edit this file.
"""
import itertools
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from main import (
    CLONE_DIR,
    CONFIG_DIR,
    LOG_DIR,
    MARKER_DIR,
    OUT_DIR,
    REF_COMMIT,
    TOOL_ROOT,
)


class RobotError(RuntimeError):
    """Any problem the robot cannot continue past."""


def _sh(args, timeout=30):
    return subprocess.run([str(a) for a in args], capture_output=True, text=True, timeout=timeout)


def _sh_ok(args, what, timeout=30):
    res = _sh(args, timeout=timeout)
    if res.returncode != 0:
        raise RobotError(
            f"{what} failed (rc={res.returncode}): {' '.join(str(a) for a in args)}\n"
            f"{res.stdout}\n{res.stderr}"
        )
    return res


def log_tail(path, lines=40):
    try:
        return "".join(Path(path).read_text().splitlines(True)[-lines:])
    except OSError:
        return "(no log)\n"


def _crop_png(png, x1, y1, x2, y2):
    """Crop the png in place to inclusive corners (x1, y1)-(x2, y2).

    Same coordinate space as BOXES rects - a rect can be pasted in directly.
    Returns the new size as "WxH".
    """
    png = Path(png)
    dims = _sh_ok(["identify", "-format", "%wx%h", str(png)], "identify").stdout.strip()
    img_w, img_h = (int(v) for v in dims.split("x"))
    w, h = x2 - x1 + 1, y2 - y1 + 1
    if x1 < 0 or y1 < 0 or w <= 0 or h <= 0 or x2 >= img_w or y2 >= img_h:
        raise RobotError(
            f"crop: box ({x1},{y1})-({x2},{y2}) does not fit "
            f"{png.name} ({dims})"
        )
    tmp = png.with_name(f"_{png.stem.lstrip('_')}.crop.png")
    _sh_ok(
        ["convert", str(png), "-crop", f"{w}x{h}+{x1}+{y1}", "+repage", str(tmp)],
        "crop",
    )
    tmp.replace(png)
    got = _sh_ok(["identify", "-format", "%wx%h", str(png)], "identify").stdout.strip()
    if got != f"{w}x{h}":
        raise RobotError(f"crop: {png.name} came out {got}, expected {w}x{h}")
    print(f"  cropped {png.name} ({got})", flush=True)
    return got


class Repo:
    """The reference clone the tool is launched against."""

    path = CLONE_DIR

    def run(self, *args):
        """Run a git command in the clone (scenes: repo.run("stash", "clear"))."""
        return _sh_ok(["git", "-C", str(CLONE_DIR), *args], f"git {' '.join(str(a) for a in args)}")

    def reset_to_base(self):
        """Back to the pinned commit, on branch master, clean working tree.

        The clone can start detached (your vim repo's HEAD is), which would
        show branch=DETACHED and hide the [master] badge - so always
        force-attach master at the pinned commit first.

        Also deletes every other local branch: a leftover 'test' branch makes
        the tool's branch-base detection pick it as upstream and reload the
        history from its tip (merge-base HEAD~5 -> "Showing: 5"). Scenes that
        need 'test' recreate it after this call.
        """
        _sh_ok(["git", "-C", CLONE_DIR, "checkout", "-f", "-B", "master", REF_COMMIT], "checkout master")
        _sh_ok(["git", "-C", CLONE_DIR, "clean", "-fdx"], "git clean")
        res = _sh_ok(
            ["git", "-C", CLONE_DIR, "for-each-ref", "--format=%(refname:short)", "refs/heads/"],
            "list local branches",
        )
        for branch in res.stdout.split():
            if branch != "master":
                _sh_ok(["git", "-C", CLONE_DIR, "branch", "-D", branch], f"delete branch {branch}")
        # Keeps the [origin/master] badge on the HEAD row, like in the docs shot.
        _sh_ok(
            ["git", "-C", CLONE_DIR, "update-ref", "refs/remotes/origin/master", REF_COMMIT],
            "update-ref origin/master",
        )

    def create_test_branch(self):
        """Create/reset the local 'test' branch at HEAD~5 (safe to re-run)."""
        self.run("branch", "-f", "test", "HEAD~5")


repo = Repo()


def _sweep_markers():
    """Drop unclean-exit markers left in MARKER_DIR.

    A force-killed tool cannot remove its own marker, and the next launch
    would pop the tool's "Previous Run" dialog over the scene. Clearing on
    every Tool() start and every close() keeps that dialog from ever firing.
    """
    if not MARKER_DIR.is_dir():
        return
    for p in MARKER_DIR.glob("git-interactive-rebase-gui-*.json"):
        try:
            p.unlink()
        except OSError:
            pass


class Tool:
    """One running instance of the GUI."""

    def __init__(self, args, log_name, sweep_markers=True):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        self._log_path = LOG_DIR / log_name
        self._log = open(self._log_path, "w")
        env = dict(os.environ)
        env["XDG_CONFIG_HOME"] = str(CONFIG_DIR)  # private copy of the tool's settings
        env["GIT_REBASE_GUI_MARKER_DIR"] = str(MARKER_DIR)  # private unclean-exit markers
        env.pop("QT_QPA_PLATFORM", None)  # never allow an offscreen platform
        if sweep_markers:
            _sweep_markers()  # stale markers from a killed run would pop "Previous Run"
        self.proc = subprocess.Popen(
            [sys.executable, str(TOOL_ROOT / "git_interactive_rebase.py"), *[str(a) for a in args]],
            cwd=str(CLONE_DIR),
            stdout=self._log,  # not a tty on purpose: stops the tool from forking away from us
            stderr=subprocess.STDOUT,
            env=env,
            start_new_session=True,
        )
        self.window_id = None

    @property
    def _title_marker(self):
        # Contains the clone path, so we never grab another instance's window.
        return f"path={CLONE_DIR}"

    def _our_windows(self):
        """Title matches our clone AND belongs to our own process.

        The title alone is not enough: an orphan left behind by a failed run
        (or your own manual instance on the same clone) carries the same
        marker, and grabbing it would drive the wrong window.
        """
        res = _sh(["xdotool", "search", "--name", self._title_marker])
        mine = []
        for wid in res.stdout.split():
            prop = _sh(["xprop", "-id", wid, "_NET_WM_PID"])
            match = re.search(r"=\s*(\d+)", prop.stdout)
            if match and int(match.group(1)) == self.proc.pid:
                mine.append(wid)
        return mine

    def wait_for_window(self, timeout=30):
        """Block until our tool window exists; store its window id."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise RobotError(
                    f"tool exited with code {self.proc.returncode} before showing a window\n"
                    f"--- log tail ---\n{log_tail(self._log_path)}"
                )
            ids = self._our_windows()
            if ids:
                self.window_id = ids[-1]
                self.activate()
                return
            time.sleep(0.5)
        raise RobotError(
            f"no window matching {self._title_marker!r} after {timeout}s\n"
            f"--- log tail ---\n{log_tail(self._log_path)}"
        )

    def wait_for_name(self, marker, timeout=10):
        """Block until any window whose title matches marker exists."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            res = _sh(["xdotool", "search", "--name", marker])
            if res.stdout.split():
                return
            time.sleep(0.3)
        raise RobotError(f"no window matching {marker!r} after {timeout}s")

    def press(self, keys):
        """Send key presses (xdotool key syntax, e.g. 'Escape', 'ctrl+q')."""
        _sh_ok(["xdotool", "key", "--clearmodifiers", keys], "key")

    def click(self, rel_x, rel_y, button=1):
        """Click at frame-relative coordinates (origin: window frame top-left,
        the same space the capture boxes use when pads are 0)."""
        self.activate()
        left, _, top, _ = self._frame_extents()
        x, y, _, _ = self._client_geometry()
        tx, ty = x - left + int(rel_x), y - top + int(rel_y)
        pos = _sh(["xdotool", "getmouselocation", "--shell"]).stdout
        cur = dict(
            line.split("=", 1) for line in pos.splitlines() if "=" in line
        )
        # mousemove --sync stalls ~15s when the pointer is already at the
        # target: it waits for a motion event that then never arrives
        if (cur.get("X"), cur.get("Y")) != (str(tx), str(ty)):
            _sh_ok(["xdotool", "mousemove", "--sync", str(tx), str(ty)], "mousemove")
        time.sleep(0.2)
        _sh_ok(["xdotool", "click", str(button)], "click")
        time.sleep(0.2)

    def drag(self, x1, y1, x2, y2, steps=12):
        """Press at (x1, y1), drag to (x2, y2), release. Frame-relative
        coordinates, same space as click()."""
        self.activate()
        left, _, top, _ = self._frame_extents()
        x, y, _, _ = self._client_geometry()
        sx, sy = x - left, y - top
        _sh_ok(["xdotool", "mousemove", str(sx + int(x1)), str(sy + int(y1))],
               "drag move")
        time.sleep(0.2)
        _sh_ok(["xdotool", "mousedown", "1"], "drag mousedown")
        time.sleep(0.1)
        # interpolated steps: Qt needs the motion to exceed its drag threshold
        # (~10px) and each hop updates the drop indicator; no --sync here -
        # mid-drag it would stall whenever a hop lands on the current position
        for i in range(1, steps + 1):
            fx = sx + int(x1 + (x2 - x1) * i / steps)
            fy = sy + int(y1 + (y2 - y1) * i / steps)
            _sh_ok(["xdotool", "mousemove", str(fx), str(fy)], "drag move")
            time.sleep(0.03)
        time.sleep(0.2)
        _sh_ok(["xdotool", "mouseup", "1"], "drag mouseup")
        time.sleep(0.3)  # drop event + dialog

    def activate(self):
        """Raise and focus our window (so nothing overlaps it during capture)."""
        active = _sh(["xdotool", "getactivewindow"]).stdout.strip()
        if active:
            # our own main window or one of its child windows/dialogs is
            # focused (matched by PID - their titles differ from the marker):
            # leave the stacking alone. Re-raising main would bury the child
            # window and steal the next click, and windowactivate --sync
            # would stall ~15s waiting for a focus change that never happens
            prop = _sh(["xprop", "-id", active, "_NET_WM_PID"])
            match = re.search(r"=\s*(\d+)", prop.stdout)
            if match and int(match.group(1)) == self.proc.pid:
                return
        _sh_ok(["xdotool", "windowactivate", "--sync", self.window_id], "windowactivate")

    def sleep(self, seconds):
        time.sleep(seconds)

    def _frame_extents(self, timeout=5):
        """(left, right, top, bottom) pixel size of the window decorations."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            res = _sh(["xprop", "-id", self.window_id, "_NET_FRAME_EXTENTS"])
            match = re.search(r"=\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)", res.stdout)
            if match:
                return tuple(int(g) for g in match.groups())
            time.sleep(0.3)
        return (0, 0, 0, 0)

    def _client_geometry(self):
        """Absolute (x, y) of the client window plus its (width, height)."""
        res = _sh_ok(["xwininfo", "-id", self.window_id], "xwininfo")
        wanted = {
            "Absolute upper-left X:": "x",
            "Absolute upper-left Y:": "y",
            "Width:": "w",
            "Height:": "h",
        }
        found = {}
        for line in res.stdout.splitlines():
            for prefix, key in wanted.items():
                if prefix in line:
                    found[key] = int(line.split(":")[-1].strip())
        if len(found) != 4:
            raise RobotError(f"could not read window geometry:\n{res.stdout}")
        return found["x"], found["y"], found["w"], found["h"]

    def set_size(self, width, height):
        """Resize the window to exactly width x height INCLUDING its title bar."""
        self.activate()
        left, right, top, bottom = self._frame_extents()
        client_w, client_h = width - left - right, height - top - bottom
        _sh_ok(
            ["xdotool", "windowsize", "--sync", self.window_id, str(client_w), str(client_h)],
            "windowsize",
        )
        deadline = time.time() + 5
        while time.time() < deadline:
            if self._client_geometry()[2:] == (client_w, client_h):
                return
            time.sleep(0.3)
        _, _, w, h = self._client_geometry()
        raise RobotError(f"window stayed at {w}x{h}, expected {client_w}x{client_h} (is it maximized?)")

    def _workarea(self):
        """(x, y, w, h) of the usable screen area (screen minus panels)."""
        res = _sh(["xprop", "-root", "_NET_WORKAREA"])
        match = re.search(r"=\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)", res.stdout)
        if match:
            return tuple(int(g) for g in match.groups())
        w, h = _sh_ok(["xdotool", "getdisplaygeometry"], "getdisplaygeometry").stdout.split()
        return 0, 0, int(w), int(h)

    def maximize(self):
        """Grow the window to fill the screen workarea (for maximized captures).

        The geometry is set by hand (KWin's Alt+F10 shortcut does not fire for
        synthetic keys here). Frame extents can change while resizing - KWin
        drops the side borders once the window is full-width - so re-read them
        and resize again until the frame matches the workarea exactly, twice
        in a row; a frame even 2px short would fail capture()'s size
        assertion. Finally slide the window to the workarea origin.
        """
        self.activate()
        wx, wy, ww, wh = self._workarea()
        exact = 0
        for _ in range(6):
            left, right, top, bottom = self._frame_extents()
            _, _, w, h = self._client_geometry()
            if w + left + right == ww and h + top + bottom == wh:
                exact += 1
                if exact >= 2:
                    break
            else:
                exact = 0
                _sh_ok(
                    ["xdotool", "windowsize", "--sync", self.window_id,
                     str(ww - left - right), str(wh - top - bottom)],
                    "windowsize",
                )
            time.sleep(0.4)
        else:
            left, right, top, bottom = self._frame_extents()
            _, _, w, h = self._client_geometry()
            raise RobotError(
                f"frame {w + left + right}x{h + top + bottom} never reached "
                f"the workarea {ww}x{wh}"
            )
        for _ in range(3):  # frame origin should sit at the workarea origin
            x, y, _, _ = self._client_geometry()
            left, _, top, _ = self._frame_extents()
            dx, dy = (wx + left) - x, (wy + top) - y
            if abs(dx) <= 1 and abs(dy) <= 1:
                break
            _sh_ok(
                ["xdotool", "windowmove", "--sync", "--relative",
                 self.window_id, str(dx), str(dy)],
                "windowmove",
            )
            time.sleep(0.3)

    def close(self, sweep_markers=True):
        """Quit the tool with Ctrl+Q (its own shortcut) and wait for a clean exit.

        A modal dialog can swallow Ctrl+Q, so on the first miss the dialog is
        dismissed with Escape and Ctrl+Q is sent again before escalating to
        terminate/kill - the tool must never be left running.

        Always also drops the underscore working files (_wip/_blank/copies):
        images a scene never saved are scratch, not captures.

        sweep_markers: pass False when a scene must keep this run's
        unclean-exit marker behind for a later relaunch to find.
        """
        try:
            self._quit()
        finally:
            for p in OUT_DIR.glob("_*"):
                try:
                    p.unlink()
                except OSError:
                    pass
            if sweep_markers:
                _sweep_markers()  # a force-killed tool never removes its own marker

    def _quit(self):
        if self.proc.poll() is not None:
            # Already reaped (the scene SIGTERMed it): there is no window
            # left to poke - just close the log and judge the exit code.
            self._log.close()
            self._check_rc()
            return
        if self.window_id:
            self.activate()
            _sh(["xdotool", "key", "--clearmodifiers", "ctrl+q"])
        attempts = 2 if self.window_id else 1
        for attempt in range(attempts):
            try:
                self.proc.wait(timeout=4)
                break
            except subprocess.TimeoutExpired:
                if attempt == 0 and self.window_id:
                    _sh(["xdotool", "key", "--clearmodifiers", "Escape"])
                    _sh(["xdotool", "key", "--clearmodifiers", "ctrl+q"])
        else:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        self._log.close()
        self._check_rc()

    def _check_rc(self):
        rc = self.proc.returncode
        if rc in (-15, -9):
            # -15/-9 is the terminate()/kill() escalation above (or the scene's
            # own kill): the scene's work is already done, cleanup must not
            # fail it. Any other non-zero exit is a genuine crash and raises.
            print(
                f"  warning: tool did not exit gracefully, force-terminated (code {rc})",
                flush=True,
            )
            return
        if rc != 0:
            raise RobotError(
                f"tool closed with code {rc}\n"
                f"--- log tail ---\n{log_tail(self._log_path)}"
            )


LABEL_FONT = "Times-Roman"
LABEL_POINTSIZE = 20


def _text_size(text):
    """Pixel size of a label rendered the way capture() draws it."""
    res = _sh_ok(
        ["convert", "-background", "none", "-fill", "red", "-font", LABEL_FONT,
         "-pointsize", str(LABEL_POINTSIZE), f"label:{text}", "-format", "%w %h", "info:"],
        "measure label",
    )
    w, h = res.stdout.split()
    return int(w), int(h)


_wip_seq = itertools.count(1)


def _dims(path):
    """Pixel size "WxH" of an image file."""
    return _sh_ok(["identify", "-format", "%wx%h", str(path)], "identify").stdout.strip()


def _geom(x, y):
    """ImageMagick geometry offset "+x+y" with proper signs for negatives."""
    return f"{'+' if x >= 0 else '-'}{abs(x)}{'+' if y >= 0 else '-'}{abs(y)}"


class Image:
    """A png on disk with the ops a scene needs (ImageMagick underneath).

    Every op edits the file in place, so crop, draw and compose in any
    order; img.save("name") finally writes <name>.png and <name>.webp
    into .work/out/.
    """

    def __init__(self, path):
        self.path = Path(path)  # working file under .work/out/ (or a saved png)

    def _tmp(self):
        # always underscore-prefixed: close() sweeps every _* working file
        return self.path.with_name(f"_{self.path.stem.lstrip('_')}.op{next(_wip_seq)}.png")

    def getsize(self):
        """(width, height) of the image in pixels."""
        w, h = _dims(self.path).split("x")
        return int(w), int(h)

    def crop(self, x1, y1, x2, y2):
        """Crop in place to inclusive corners - same coords as BOXES rects."""
        return _crop_png(self.path, x1, y1, x2, y2)

    def resize(self, x_percent, y_percent=None):
        """Scale in place; percentages of the CURRENT size (50, 50 → half).
        y defaults to x for a uniform scale. Later draw_box/crop coordinates
        are in the resized pixel space. Returns self (chainable)."""
        y = y_percent if y_percent is not None else x_percent
        tmp = self._tmp()
        _sh_ok(
            ["convert", str(self.path), "-resize", f"{x_percent}%x{y}%", str(tmp)],
            "resize",
        )
        tmp.replace(self.path)
        got = _sh_ok(["identify", "-format", "%wx%h", str(self.path)], "identify").stdout.strip()
        print(f"  resized {self.path.name} ({got})", flush=True)
        return self

    def copy(self):
        """Independent duplicate on its own working file - crop one, keep the other."""
        dup = self._tmp()
        dup.write_bytes(self.path.read_bytes())
        return Image(dup)

    def draw_box(self, boxes):
        """Draw BOXES-style red frames / plates / labels on the image.

        boxes: [] or [{"rect": (x1, y1, x2, y2),              # red frame: outer pixel bounds
                       "label": "text",                        # red serif text
                       "label_at": (cx, cy),                   # label text center
                       "plate": (x1, y1, x2, y2)}, ...]        # white plate behind the label
               coordinates are in pixels of the image, (0, 0) top-left.
               The frame is drawn as four 2px bands, so every edge lands on exact
               pixel rows (strokes rasterize differently per coordinate).
               Draw order: all frames, then all plates, then all labels - so a plate
               can deliberately cut a frame short, like in the original shots.
        """
        if not boxes:
            return self
        png = self.path
        args = ["convert", str(png)]
        for box in boxes:
            x1, y1, x2, y2 = (int(v) for v in box["rect"])
            top_h = int(box.get("top_h", 2))
            bot_h = int(box.get("bottom_h", 2))
            args += ["-fill", "red", "-stroke", "none",
                     "-draw", f"rectangle {x1},{y1} {x2},{y1 + top_h - 1}",
                     "-draw", f"rectangle {x1},{y2 - bot_h + 1} {x2},{y2}",
                     "-draw", f"rectangle {x1},{y1} {x1 + 1},{y2}",
                     "-draw", f"rectangle {x2 - 1},{y1} {x2},{y2}"]
        for box in boxes:
            if box.get("plate"):
                p = tuple(int(v) for v in box["plate"])
                args += ["-fill", "white", "-stroke", "none",
                         "-draw", f"rectangle {p[0]},{p[1]} {p[2]},{p[3]}"]
        for box in boxes:
            label = box.get("label")
            if label:
                text_w, text_h = _text_size(label)
                x1, y1, x2, y2 = (int(v) for v in box["rect"])
                cx, cy = box.get("label_at", ((x1 + x2) // 2, y1 - 8))
                lx, ly = int(cx) - text_w // 2, int(cy) - text_h // 2
                args += ["(",
                         "-background", "none", "-fill", "red",
                         "-font", LABEL_FONT, "-pointsize", str(LABEL_POINTSIZE),
                         f"label:{label}",
                         ")",
                         "-geometry", f"+{lx}+{ly}", "-composite"]
        args.append(str(png))
        _sh_ok(args, "drawing red boxes")
        return self

    def add(self, x, y, other):
        """Composite another Image onto this one, its top-left at (x, y)."""
        tmp = self._tmp()
        _sh_ok(
            ["convert", str(self.path), str(other.path),
             "-geometry", _geom(x, y), "-composite", str(tmp)],
            "add",
        )
        tmp.replace(self.path)
        return self

    def add_text(self, x, y, text, size, border=0, fill="red", plate=False):
        """Text with its top-left at (x, y).

        border>0: white plate behind the text with a `border`-px frame around
        it; plate=True: white plate without a frame; default: transparent,
        only the glyphs are drawn.

        Spaces pad the plate: "   text   " keeps leading and trailing
        spaces (label: drops leading ones, so they are rendered as
        no-break spaces - same glyph, same width).
        """
        want_plate = bool(plate or border)
        lead = len(text) - len(text.lstrip(" "))
        rendered = "\u00a0" * lead + text[lead:] if lead else text
        label = self._tmp()
        _sh_ok(
            ["convert", "-background", "white" if want_plate else "none",
             "-fill", fill,
             "-font", LABEL_FONT, "-pointsize", str(int(size)),
             f"label:{rendered}", str(label)],
            "add_text",
        )
        w, h = (int(v) for v in _dims(label).split("x"))
        # plate first, frame after: a frame drawn before the composite would
        # be half-covered by the label's white background
        self.add(x, y, Image(label))
        label.unlink()
        if border:
            _sh_ok(
                ["convert", str(self.path), "-fill", "none",
                 "-stroke", fill, "-strokewidth", str(int(border)),
                 "-draw", f"rectangle {x},{y} {x + w - 1},{y + h - 1}",
                 str(self.path)],
                "add_text border",
            )
        return self

    def _stamp_tick(self, size=24, margin=10):
        """Composite a small check mark at bottom-center (white glyph with a
        thin dark outline, so it shows on light and dark backgrounds alike)."""
        tick = self._tmp()
        _sh_ok(
            ["convert", "-background", "none",
             "-fill", "white", "-stroke", "black", "-strokewidth", "1",
             "-font", "DejaVu-Sans", "-pointsize", str(int(size)),
             "label:✓", str(tick)],
            "watermark",
        )
        w, h = (int(v) for v in _dims(tick).split("x"))
        W, H = (int(v) for v in _dims(self.path).split("x"))
        self.add((W - w) // 2, H - h - int(margin), Image(tick))
        tick.unlink()

    def save(self, name, watermark=True):
        """Write .work/out/<name>.png and <name>.webp (quality 90).

        watermark=True: stamp a small check mark at bottom-center first,
        so both the .png and the .webp carry it.
        """
        if watermark:
            self._stamp_tick()
        base = name[:-4] if name.endswith(".png") else name[:-5] if name.endswith(".webp") else name
        png = OUT_DIR / f"{base}.png"
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        if self.path != png:
            if self.path.name.startswith("_"):
                self.path.replace(png)  # consume the working file
            else:
                png.write_bytes(self.path.read_bytes())
            self.path = png
        webp = OUT_DIR / f"{base}.webp"
        _sh_ok(["convert", str(png), "-quality", "90", str(webp)], "save webp")
        print(f"  saved {png.name} + {webp.name} ({_dims(png)})", flush=True)
        return self


def image_new(width, height, fill="white"):
    """Blank width x height image; draw/compose on it, then img.save("name")."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"_blank-{next(_wip_seq)}.png"
    _sh_ok(["convert", "-size", f"{width}x{height}", f"xc:{fill}", str(path)], "image_new")
    return Image(path)


def capture(tool, description="", size=None):
    """Screenshot the tool window (title bar included) into a working image.

    Returns an Image: crop/draw_box/add/add_text anytime, then
    img.save("name") writes <name>.png and <name>.webp into .work/out/.

    size: expected (width, height) of the shot; RobotError when it differs.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tool.sleep(.1)
    tool.activate()
    tool.sleep(0.5)  # let the compositor finish raising the window
    left, right, top, bottom = tool._frame_extents()
    x, y, w, h = tool._client_geometry()
    frame_x, frame_y = x - left, y - top
    frame_w, frame_h = w + left + right, h + top + bottom
    wip = OUT_DIR / f"_wip-{next(_wip_seq)}.png"
    _sh_ok(
        ["import", "-window", "root", "-crop", f"{frame_w}x{frame_h}+{frame_x}+{frame_y}",
         "+repage", str(wip)],
        "screenshot",
    )
    dims = _dims(wip)
    if size and dims != f"{size[0]}x{size[1]}":
        raise RobotError(f"capture came out {dims}, expected {size[0]}x{size[1]}")
    print(f"  captured ({dims})" + (f" - {description}" if description else ""), flush=True)
    return Image(wip)


def capture_screen(x, y, w, h, description="", size=None):
    """Screenshot an absolute screen rectangle into a working image.

    For windows that exist outside the tool's frame (e.g. a dialog shown
    before the main window appears, so there is no Tool to capture yet).
    Returns an Image, same contract as capture().
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    wip = OUT_DIR / f"_wip-{next(_wip_seq)}.png"
    _sh_ok(
        ["import", "-window", "root", "-crop", f"{w}x{h}+{x}+{y}", "+repage", str(wip)],
        "screenshot",
    )
    dims = _dims(wip)
    if size and dims != f"{size[0]}x{size[1]}":
        raise RobotError(f"capture came out {dims}, expected {size[0]}x{size[1]}")
    print(f"  captured ({dims})" + (f" - {description}" if description else ""), flush=True)
    return Image(wip)
