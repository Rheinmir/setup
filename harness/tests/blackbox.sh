#!/usr/bin/env bash
# blackbox — nghiệm thu một lỗi chập chờn đã sửa: chạy lệnh của <id> trong harness/tests/FLAKY.md
# N lần (mặc định 10), mỗi lần với TMPDIR mới. PASS chỉ khi N/N — một lần đỏ = vẫn chập chờn.
# Usage: bash harness/tests/blackbox.sh <id> [N]      (exit 0 = N/N pass)
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
ID="${1:?usage: blackbox.sh <id> [N]}"; N="${2:-10}"
CMD="$(awk -F'|' -v id="$ID" '{gsub(/^ +| +$/,"",$2)} $2==id {print $3; exit}' harness/tests/FLAKY.md | sed -E 's/^ *`//; s/` *$//')"
[ -n "$CMD" ] || { echo "✗ không có id '$ID' trong harness/tests/FLAKY.md"; exit 2; }
echo "blackbox $ID × $N: $CMD"; pass=0
for i in $(seq 1 "$N"); do
  T="$(mktemp -d)"; t0=$(date +%s)
  if TMPDIR="$T" bash -c "$CMD" >"$T.log" 2>&1; then pass=$((pass+1)); r=✓; else r=✗; fi
  echo "  $r lần $i/$N ($(( $(date +%s)-t0 ))s)$( [ $r = ✗ ] && echo " — log: $T.log")"
  [ $r = ✓ ] && rm -rf "$T" "$T.log"
done
echo "═══ blackbox $ID: $pass/$N · $(uptime | sed 's/.*load averages*: //')"
[ "$pass" -eq "$N" ]
