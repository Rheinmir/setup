#!/usr/bin/env bash
# pull-gate-sweep — R12 v3 (B): quét pull-gate cả WORKSPACE trước khi làm/fan-out.
#   - Discovery subrepo qua list-subrepos.py (manifest | fallback find).
#   - Mỗi subrepo: chạy pull-gate.sh gate1 (fetch + behind) SONG SONG.
#   - In bảng repo · trạng thái. Exit 2 nếu có subrepo TARGET behind; watch behind → chỉ cảnh báo.
#   - Triết lý harness: lỗi hạ tầng → fail-open. Chỉ chặn khi chắc TARGET sau remote.
#
# Dùng: pull-gate-sweep.sh [workspace_root]   (mặc định: cwd)
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${1:-$(pwd)}"
LIST="$HERE/list-subrepos.py"
GATE="$HERE/pull-gate.sh"

[ -f "$LIST" ] || { echo "sweep: thiếu list-subrepos.py — fail-open"; exit 0; }
[ -x "$GATE" ] || { echo "sweep: thiếu pull-gate.sh — fail-open"; exit 0; }

ROWS=()
while IFS= read -r line; do [ -n "$line" ] && ROWS+=("$line"); done < <(python3 "$LIST" "$ROOT" 2>/dev/null)
if [ "${#ROWS[@]}" -eq 0 ]; then
  echo "sweep: không thấy subrepo nào trong $ROOT — fail-open"; exit 0
fi

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
i=0
for row in "${ROWS[@]}"; do
  path="${row%%$'\t'*}"; kind="${row##*$'\t'}"
  i=$((i+1))
  # chạy nền song song; mỗi repo ghi 1 dòng kết quả: kind|path|rc|msg
  (
    out="$(cd "$path" 2>/dev/null && bash "$GATE" gate1 2>&1)"; rc=$?
    # rút gọn msg 1 dòng cuối
    last="$(printf '%s\n' "$out" | tail -1)"
    printf '%s\t%s\t%s\t%s\n' "$kind" "$path" "$rc" "$last" > "$TMP/r$i"
  ) &
done
wait

BLOCK=0
printf '\n  KIND    RC  REPO / TRẠNG THÁI\n'
printf '  ────────────────────────────────────────────────────\n'
for f in "$TMP"/r*; do
  [ -f "$f" ] || continue
  IFS=$'\t' read -r kind path rc msg < "$f"
  base="$(basename "$path")"
  if [ "$rc" = "2" ]; then
    if [ "$kind" = "target" ]; then mark="⛔ TARGET sau remote"; BLOCK=1; else mark="⚠ watch behind"; fi
  else mark="✓"; fi
  printf '  %-7s %-3s %s — %s\n' "$kind" "$rc" "$base" "$mark"
done
printf '  ────────────────────────────────────────────────────\n'

if [ "$BLOCK" = "1" ]; then
  echo "⛔ pull-gate-sweep: có subrepo TARGET sau remote → PULL trước khi làm/fan-out (git pull --rebase trong repo đó)."
  exit 2
fi
echo "✓ pull-gate-sweep: mọi target đồng bộ — an toàn để bắt đầu / fan-out."
exit 0
