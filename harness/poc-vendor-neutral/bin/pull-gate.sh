#!/usr/bin/env bash
# pull-gate — harness process gate R12 (pull-before-change).
#   gate1 : TRƯỚC khi sửa framework — fetch + chặn nếu local SAU remote (có cache freshness để rẻ).
#   gate2 : TRƯỚC khi push        — luôn fetch tươi + chặn nếu local SAU/diverge remote.
#
# Triết lý harness: lỗi hạ tầng (offline, không remote) => FAIL-OPEN (exit 0) — không khoá cứng người dùng.
# Chỉ CHẶN (exit 2) khi chắc chắn local đang SAU remote (cần pull --rebase trước).
set -uo pipefail

GATE="${1:-gate1}"
FRESH_SECS="${PULL_GATE_FRESH_SECS:-300}"   # gate1: bỏ fetch nếu vừa fetch < 5' trước

# không ở git repo => fail-open
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "pull-gate: không ở git repo — fail-open"; exit 0; }

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '')"
[ -z "$BRANCH" ] || [ "$BRANCH" = "HEAD" ] && { echo "pull-gate: detached/không branch — fail-open"; exit 0; }

# có upstream/remote không?
git remote get-url origin >/dev/null 2>&1 || { echo "pull-gate: không có remote origin — fail-open"; exit 0; }

GITDIR="$(git rev-parse --git-dir 2>/dev/null)"
STAMP="$GITDIR/.pull-gate-last-fetch"
NOW="$(date +%s)"

do_fetch=1
if [ "$GATE" = "gate1" ] && [ -f "$STAMP" ]; then
  LAST="$(cat "$STAMP" 2>/dev/null || echo 0)"
  if [ $((NOW - LAST)) -lt "$FRESH_SECS" ]; then do_fetch=0; fi   # vừa fetch xong → khỏi gọi mạng lần nữa
fi

if [ "$do_fetch" = "1" ]; then
  if git fetch --quiet origin "$BRANCH" 2>/dev/null; then
    echo "$NOW" > "$STAMP" 2>/dev/null || true
  else
    echo "pull-gate $GATE: fetch thất bại (offline?) — fail-open"; exit 0
  fi
fi

# remote-tracking ref tồn tại?
git rev-parse --verify --quiet "origin/$BRANCH" >/dev/null 2>&1 || { echo "pull-gate $GATE: chưa có origin/$BRANCH — fail-open"; exit 0; }

BEHIND="$(git rev-list --count "HEAD..origin/$BRANCH" 2>/dev/null || echo 0)"
AHEAD="$(git rev-list --count "origin/$BRANCH..HEAD" 2>/dev/null || echo 0)"

if [ "${BEHIND:-0}" -gt 0 ]; then
  if [ "${AHEAD:-0}" -gt 0 ]; then
    echo "⛔ pull-gate $GATE [R12]: local DIVERGE remote ($AHEAD ahead / $BEHIND behind) trên '$BRANCH'."
  else
    echo "⛔ pull-gate $GATE [R12]: local SAU remote $BEHIND commit trên '$BRANCH'."
  fi
  echo "   → PULL trước rồi mới tiếp: git pull --rebase origin $BRANCH"
  exit 2
fi

echo "✓ pull-gate $GATE: '$BRANCH' đồng bộ remote (ahead=$AHEAD, behind=0)."
exit 0
