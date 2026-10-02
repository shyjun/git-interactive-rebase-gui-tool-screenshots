#!/usr/bin/env bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
DEV=/home/snarangaprath/WORK/git-interactive-rebase-gui-tool
COPY="$HERE/.work/git-interactive-rebase-gui-tool"

mkdir -p "$HERE/.work"
rm -rf "$COPY"
cp -a "$DEV" "$COPY"
cd "$COPY"
git reset --hard origin/master
git pull

cd "$HERE"
exec python3 scenes/main.py
