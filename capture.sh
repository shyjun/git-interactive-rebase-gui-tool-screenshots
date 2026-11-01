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

# count .webp files, then delete all files in screenshots/
EXPECTED=$(find screenshots -name "*.webp" | wc -l)
find screenshots -type f -delete

# invoke python (don't abort on failure - verification must still run)
set +e
python3 scenes/main.py
RC=$?
set -e

# count again and compare - notify either way
ACTUAL=$(find screenshots -name "*.webp" | wc -l)
if [ "$ACTUAL" -eq "$EXPECTED" ] && [ "$RC" -eq 0 ]; then
    MSG="capture OK: $ACTUAL/$EXPECTED webp (rc=0)"
else
    MSG="capture MISMATCH: expected $EXPECTED, got $ACTUAL (rc=$RC)"
fi
/home/snarangaprath/WORK/BASH_CMDS/buildresultshow.sh 15 "$MSG"

exit $RC
