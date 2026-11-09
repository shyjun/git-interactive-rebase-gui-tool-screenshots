#!/usr/bin/env bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
DEV=/home/snarangaprath/WORK/git-interactive-rebase-gui-tool
COPY="$HERE/.work/git-interactive-rebase-gui-tool"
DOCS="$DEV/docs/screenshots.md"

mkdir -p "$HERE/.work"
rm -rf "$COPY"
cp -a "$DEV" "$COPY"
cd "$COPY"
git reset --hard origin/master
git pull

cd "$HERE"

# delete all files in screenshots/ - docs/screenshots.md decides what must come back
find screenshots -type f -delete

# invoke python (don't abort on failure - verification must still run)
set +e
python3 scenes/main.py
RC=$?
set -e

# ---- verification: what we captured vs what docs/screenshots.md references ----
# The docs cite every image twice (**Screenshot:** URL + ![]()), so count
# unique names, not raw matches.  The anchored regex skips the bare `.webp`
# mention in the docs intro and keeps underscores (commit_or_unstage-...).
DOC_NAMES=$(grep -oE '[A-Za-z0-9][A-Za-z0-9_-]*\.webp' "$DOCS" | sort -u || true)
DOC_EXPECTED=$(printf '%s\n' "$DOC_NAMES" | sed '/^$/d' | wc -l)
ACTUAL_NAMES=$(find screenshots -name '*.webp' -printf '%f\n' | sort || true)
ACTUAL=$(printf '%s\n' "$ACTUAL_NAMES" | sed '/^$/d' | wc -l)

MISSING=$(comm -23 <(printf '%s\n' "$DOC_NAMES" | sed '/^$/d') \
                   <(printf '%s\n' "$ACTUAL_NAMES" | sed '/^$/d'))
EXTRA=$(comm -13 <(printf '%s\n' "$DOC_NAMES" | sed '/^$/d') \
                  <(printf '%s\n' "$ACTUAL_NAMES" | sed '/^$/d'))
MISSING_COUNT=$(printf '%s\n' "$MISSING" | sed '/^$/d' | wc -l)
EXTRA_COUNT=$(printf '%s\n' "$EXTRA" | sed '/^$/d' | wc -l)

# short form for the popup: first 3 names, then "+N more"
names_msg() {
    printf '%s\n' "$1" | sed '/^$/d' | head -3 | paste -sd, - | sed 's/,/, /g'
}
DETAIL=""
if [ "$MISSING_COUNT" -gt 0 ]; then
    DETAIL="; missing: $(names_msg "$MISSING")"
    if [ "$MISSING_COUNT" -gt 3 ]; then
        DETAIL="$DETAIL +$((MISSING_COUNT - 3)) more"
    fi
fi
if [ "$EXTRA_COUNT" -gt 0 ]; then
    DETAIL="$DETAIL; extra not in docs: $(names_msg "$EXTRA")"
    if [ "$EXTRA_COUNT" -gt 3 ]; then
        DETAIL="$DETAIL +$((EXTRA_COUNT - 3)) more"
    fi
fi

# full report for the terminal (the popup only carries the summary)
echo "--- docs cross-check: $DOCS ---"
echo "expected in doc: $DOC_EXPECTED unique .webp, captured: $ACTUAL (scenes rc=$RC)"
if [ "$MISSING_COUNT" -gt 0 ]; then
    echo "missing:"
    printf '%s\n' "$MISSING" | sed '/^$/d;s/^/  /'
fi
if [ "$EXTRA_COUNT" -gt 0 ]; then
    echo "extra:"
    printf '%s\n' "$EXTRA" | sed '/^$/d;s/^/  /'
fi

# notify either way - the exit code stays the scenes' rc
if [ "$RC" -ne 0 ]; then
    MSG="capture FAILED: scenes rc=$RC - expected in doc is $DOC_EXPECTED, but we captured only $ACTUAL$DETAIL"
elif [ "$MISSING_COUNT" -gt 0 ]; then
    MSG="capture MISMATCH: expected in doc is $DOC_EXPECTED, but we captured only $ACTUAL (rc=0)$DETAIL"
else
    MSG="capture OK: $ACTUAL/$DOC_EXPECTED webp (rc=0)$DETAIL"
fi
/home/snarangaprath/WORK/BASH_CMDS/buildresultshow.sh 15 "$MSG"

exit $RC
