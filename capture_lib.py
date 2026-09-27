"""Plumbing for the screenshot robot.

Scene scripts import exactly three things from here:

    from capture_lib import Tool, capture, repo

- repo.reset_to_base()   put the clone back to the pinned commit
- Tool(...)              open / control / close the GUI
- capture(...)           take the picture and save it as .webp

You normally never edit this file.
"""
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


class Repo:
    """The reference clone the tool is launched against."""

    def reset_to_base(self):
        """Back to the pinned commit, on branch master, clean working tree.

        The clone can start detached (your vim repo's HEAD is), which would
        show branch=DETACHED and hide the [master] badge - so always
        force-attach master at the pinned commit first.
        """
        _sh_ok(["git", "-C", CLONE_DIR, "checkout", "-f", "-B", "master", REF_COMMIT], "checkout master")
        _sh_ok(["git", "-C", CLONE_DIR, "clean", "-fdx"], "git clean")
        # Keeps the [origin/master] badge on the HEAD row, like in the docs shot.
        _sh_ok(
            ["git", "-C", CLONE_DIR, "update-ref", "refs/remotes/origin/master", REF_COMMIT],
            "update-ref origin/master",
        )


repo = Repo()


class Tool:
    """One running instance of the GUI."""

    def __init__(self, args, log_name):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        self._log_path = LOG_DIR / log_name
        self._log = open(self._log_path, "w")
        env = dict(os.environ)
        env["XDG_CONFIG_HOME"] = str(CONFIG_DIR)  # private copy of the tool's settings
        env["GIT_REBASE_GUI_MARKER_DIR"] = str(MARKER_DIR)  # private unclean-exit markers
        env.pop("QT_QPA_PLATFORM", None)  # never allow an offscreen platform
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

    def wait_for_window(self, timeout=30):
        """Block until our tool window exists; store its window id."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise RobotError(
                    f"tool exited with code {self.proc.returncode} before showing a window\n"
                    f"--- log tail ---\n{log_tail(self._log_path)}"
                )
            res = _sh(["xdotool", "search", "--name", self._title_marker])
            ids = res.stdout.split()
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
        _sh_ok(
            ["xdotool", "mousemove", "--sync", str(x - left + int(rel_x)),
             str(y - top + int(rel_y))],
            "mousemove",
        )
        time.sleep(0.2)
        _sh_ok(["xdotool", "click", str(button)], "click")
        time.sleep(0.2)

    def activate(self):
        """Raise and focus our window (so nothing overlaps it during capture)."""
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

    def close(self):
        """Quit the tool with Ctrl+Q (its own shortcut) and wait for a clean exit."""
        if self.window_id:
            self.activate()
            _sh(["xdotool", "key", "--clearmodifiers", "ctrl+q"])
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        self._log.close()
        if self.proc.returncode != 0:
            raise RobotError(
                f"tool closed with code {self.proc.returncode}\n"
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


def capture(tool, name, description, boxes, size=None, pads=(0, 0, 0, 0), quality=90):
    """Screenshot our tool window (title bar included) into .work/out/<name>.

    pads: (left, right, top, bottom) white margin added around the window.
          Some docs shots sit on a white canvas with room above the title bar
          for an annotation - the scene script decides.

    boxes: [] or [{"rect": (x1, y1, x2, y2),              # red frame: outer pixel bounds
                   "label": "text",                        # red serif text
                   "label_at": (cx, cy),                   # label text center
                   "plate": (x1, y1, x2, y2)}, ...]        # white plate behind the label
           coordinates are in pixels of the FINAL (padded) image, (0, 0) top-left.
           The frame is drawn as four 2px bands, so every edge lands on exact
           pixel rows (strokes rasterize differently per coordinate).
           Draw order: all frames, then all plates, then all labels - so a plate
           can deliberately cut a frame short, like in the original shots.

    size: expected final (width, height). Computed from window + pads when omitted.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tool.activate()
    tool.sleep(0.3)  # let the compositor finish raising the window
    left, right, top, bottom = tool._frame_extents()
    x, y, w, h = tool._client_geometry()
    frame_x, frame_y = x - left, y - top
    frame_w, frame_h = w + left + right, h + top + bottom
    win_png = OUT_DIR / (Path(name).stem + ".win.png")
    _sh_ok(
        ["import", "-window", "root", "-crop", f"{frame_w}x{frame_h}+{frame_x}+{frame_y}",
         "+repage", str(win_png)],
        "screenshot",
    )

    pad_l, pad_r, pad_t, pad_b = pads
    png = OUT_DIR / (Path(name).stem + ".png")
    final_w, final_h = frame_w + pad_l + pad_r, frame_h + pad_t + pad_b
    if any(pads):
        _sh_ok(
            ["convert", "-size", f"{final_w}x{final_h}", "xc:white",
             str(win_png), "-geometry", f"+{pad_l}+{pad_t}", "-composite", str(png)],
            "padding window onto white canvas",
        )
        win_png.unlink()
    else:
        win_png.rename(png)

    if boxes:
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

    out = OUT_DIR / name
    _sh_ok(["cwebp", "-q", str(quality), str(png), "-o", str(out)], "cwebp")

    dims = _sh_ok(["identify", "-format", "%wx%h", str(out)], "identify").stdout.strip()
    expected = size if size else (final_w, final_h)
    if dims != f"{expected[0]}x{expected[1]}":
        raise RobotError(f"{name} came out {dims}, expected {expected[0]}x{expected[1]}")
    print(f"  captured {name} ({dims}) - {description}", flush=True)
    return out
