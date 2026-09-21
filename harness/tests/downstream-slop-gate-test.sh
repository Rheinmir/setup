#!/usr/bin/env bash
# downstream-slop-gate-test — trang framework sinh ra Ở MÁY KHÁCH (layout dot) phải qua CẢ HAI cổng.
#
# Vì sao cần một test riêng cho downstream: cả hai cổng chạy ở repo framework thì xanh, nhưng ở máy khách
# cây thư mục khác và tool chạy từ ~/.claude/harness. Smoke ngày 21/09/2026 bắt đúng ba lỗi chỉ lộ ở đó:
#   1. html-visual-gate.mjs không hề được cài xuống (installer chỉ copy *.py) → downstream mất cổng chạy-thật.
#   2. frontend-antipattern.py giải `data-src` theo parents[2] của CHÍNH nó → ở máy khách ra ~/.claude,
#      mọi neo bằng chứng resolve sai, cổng báo "sơ đồ nói dối" hàng loạt.
#   3. overstack.html mang neo trỏ vào cây framework (llmwiki/… · harness/… · .github/…) mà máy khách không có.
#
# Cổng chạy-thật SKIP (rc 4) khi máy không có Playwright — SKIP CÓ TÊN, không tính là PASS.
set -uo pipefail
SRC="$(cd "$(dirname "$0")/../.." && pwd)"
. "$SRC/harness/tests/downstream-fixture.sh"
make_downstream_fixture "$SRC" || { echo "FAIL: không dựng được fixture"; exit 1; }
cd "$FX" || exit 1

for t in build-docs-index build-health-dashboard build-control-room build-overstack-docs; do
  [ -f "$GH/fdk/tools/$t.py" ] && python3 "$GH/fdk/tools/$t.py" >/dev/null 2>&1
done

shopt -s nullglob
pages=(.llmwiki/html/*.html .llmwiki/graph/*.html)
if [ "${#pages[@]}" -eq 0 ]; then echo "FAIL: máy khách không có trang HTML nào"; exit 1; fi
echo "trang ở máy khách: ${#pages[@]}"

fail=0
if [ ! -f "$GH/fdk/tools/frontend-antipattern.py" ]; then
  echo "FAIL: cổng tĩnh không được cài xuống máy khách"; fail=1
else
  python3 "$GH/fdk/tools/frontend-antipattern.py" "${pages[@]}"
  rc=$?
  [ "$rc" = 0 ] && echo "PASS  cổng tĩnh: ${#pages[@]} trang sạch" || { echo "FAIL  cổng tĩnh rc=$rc"; fail=1; }
fi

if [ ! -f "$GH/fdk/tools/html-visual-gate.mjs" ]; then
  echo "FAIL: cổng chạy-thật không được cài xuống máy khách (installer bỏ sót *.mjs)"; fail=1
elif ! command -v node >/dev/null 2>&1; then
  echo "SKIP  cổng chạy-thật: máy không có node"
else
  NODE_PATH="$(npm root -g 2>/dev/null)" node "$GH/fdk/tools/html-visual-gate.mjs" "${pages[@]}"
  rc=$?
  if [ "$rc" = 4 ]; then echo "SKIP  cổng chạy-thật: không có Playwright"
  elif [ "$rc" = 0 ]; then echo "PASS  cổng chạy-thật: ${#pages[@]} trang sạch"
  else echo "FAIL  cổng chạy-thật rc=$rc"; fail=1; fi
fi

rm -rf "$FX_TMP"
[ "$fail" -eq 0 ] && { echo "downstream-slop-gate: PASS"; exit 0; } || { echo "downstream-slop-gate: FAIL"; exit 1; }
