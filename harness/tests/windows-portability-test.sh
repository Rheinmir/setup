#!/usr/bin/env bash
# windows-portability-test — GH#168/#169: người dùng Windows (Git Bash + Python native) cài được trọn vẹn.
#   Python native Windows ghi stdout theo code page cp1252/cp437 → mọi print tiếng Việt/"→" crash UnicodeEncodeError
#   giữa chừng cài. Ở đây giả lập bằng PYTHONIOENCODING=cp1252 đặt SẴN trong môi trường (y như máy Windows):
#   (1) bootstrap + install + install-harness --global chạy trọn trong HOME trống (chưa có ~/.claude) — không crash
#   (2) settings.json global hợp lệ, có hook                  (3) engine orca-graph --help không crash
#   (4) ÂM TÍNH: bỏ ép UTF-8 thì gen-converters crash đúng như issue — chứng minh test không PASS giả
#   (5) cảnh báo WSL có trong bootstrap (không giả lập được /proc/version ở đây — kiểm có mặt + cú pháp)
set -uo pipefail
SRC="$(cd "$(dirname "$0")/../.." && pwd)"
PASS=0; FAIL=0; ok(){ PASS=$((PASS+1)); echo "  PASS  $*"; }; no(){ FAIL=$((FAIL+1)); echo "  FAIL  $*"; }
OG_BIN="$HOME/.orca-graph/bin/orca-graph"

export PYTHONIOENCODING=cp1252
. "$SRC/harness/tests/downstream-fixture.sh"
if make_downstream_fixture "$SRC"; then
  ok "(1) bootstrap + global chạy trọn dưới stdout cp1252, HOME trống"
else
  no "(1) cài lỗi dưới cp1252: $(grep -m1 -i 'UnicodeEncodeError\|Error' "$FX_TMP/install.log" "$FX_TMP"/*.log 2>/dev/null | head -1)"
fi
S="$HOME/.claude/settings.json"
python3 -c "import json,sys; d=json.load(open(sys.argv[1])); assert d.get('hooks')" "$S" 2>/dev/null \
  && ok "(2) ~/.claude/settings.json global hợp lệ, có hook" || no "(2) settings.json global thiếu/hỏng: $S"

if [ -x "$OG_BIN" ]; then
  "$OG_BIN" --help >/dev/null 2>&1 && ok "(3) orca-graph --help sạch dưới cp1252" || no "(3) orca-graph --help crash dưới cp1252"
else echo "  SKIP  (3) máy chưa cài engine orca-graph"; fi

T="$(mktemp -d)"
env -u PYTHONUTF8 PYTHONIOENCODING=cp1252 python3 "$SRC/harness/poc-vendor-neutral/gen-converters.py" --out "$T" >/dev/null 2>"$T/err"
grep -q UnicodeEncodeError "$T/err" && ok "(4) âm tính: không ép UTF-8 thì crash đúng như issue" || no "(4) giả lập cp1252 không tái hiện lỗi — test vô hiệu"

grep -q 'OVERSTACK_WSL_OK' "$SRC/harness/poc-vendor-neutral/bootstrap.sh" && bash -n "$SRC/harness/poc-vendor-neutral/bootstrap.sh" \
  && ok "(5) bootstrap có cảnh báo WSL-vs-Windows" || no "(5) thiếu cảnh báo WSL"

# (6) Windows PowerShell 5.1 đọc .ps1 KHÔNG BOM theo cp1252 → ký tự ngoài ASCII (—, →) vỡ thành dấu đóng chuỗi, file
#     không parse được (review t8 #4). Giữ install.ps1 thuần ASCII.
python3 -c "import sys; b=open(sys.argv[1],'rb').read(); sys.exit(0 if all(c<128 for c in b) else 1)" "$SRC/harness/poc-vendor-neutral/install.ps1" \
  && ok "(6) install.ps1 thuần ASCII (PowerShell 5.1 đọc cp1252)" || no "(6) install.ps1 có ký tự ngoài ASCII — PS 5.1 parse lỗi"

rm -rf "$T" "${FX_TMP:-/nonexistent}"
echo ""; echo "windows-portability-test: $PASS PASS · $FAIL FAIL"; [ "$FAIL" = 0 ]
