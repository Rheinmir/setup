#!/usr/bin/env bash
# install-ps1-test.sh — proof cho harness/poc-vendor-neutral/install.ps1 (Windows entry point).
# Bỏ qua fail-open nếu máy CI không có pwsh (không phải mọi runner có PowerShell Core).
#
# Bài học 150926: ca "giả lập KHÔNG có bash" từng thử ẨN bash bằng cách bó hẹp PATH quanh thư
# mục của pwsh — ăn may trên macOS (nơi pwsh và bash không chung thư mục) nhưng SẬP trên
# runner Ubuntu của GitHub Actions (pwsh và bash CÙNG nằm /usr/bin), khiến detection vẫn thấy
# bash, chạy tiếp mà KHÔNG có --Root cô lập → cài đè thật lên chính checkout CI đang chạy.
# Trên Linux, bash LUÔN có sẵn — nhánh "không có shell POSIX nào" chỉ tái hiện được trên
# Windows trần không Git/WSL, môi trường CI này không có. Nên bài kiểm KHÔNG còn cố giả lập
# nhánh đó bằng cách ẩn PATH; thay vào đó kiểm TĨNH rằng nhánh bảo vệ đó tồn tại đúng chữ
# (ca 1), và kiểm ĐỘNG đường thật-sẽ-chạy trên Windows qua Git Bash/WSL bằng cách cho bash
# đóng vai đó — LUÔN trong thư mục CÔ LẬP (mktemp), không bao giờ chạm checkout đang chạy (ca 2).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT="$ROOT/harness/poc-vendor-neutral/install.ps1"
fail() { echo "✗ $*" >&2; exit 1; }

[ -f "$SCRIPT" ] || fail "thiếu $SCRIPT"

echo "== ca 1 (tĩnh): nhánh 'không có Git Bash/WSL' phải tồn tại đúng chữ =="
grep -q 'Get-Command bash -ErrorAction SilentlyContinue' "$SCRIPT" || fail "ca 1: thiếu dò bash"
grep -q 'Get-Command wsl -ErrorAction SilentlyContinue' "$SCRIPT" || fail "ca 1: thiếu dò wsl"
grep -q 'if (-not \$bash -and -not \$wsl)' "$SCRIPT" || fail "ca 1: thiếu điều kiện chặn khi cả hai đều thiếu"
grep -q 'Git for Windows' "$SCRIPT" || fail "ca 1: thiếu hướng dẫn cài Git for Windows"
echo "  ok — nhánh bảo vệ có mặt (không giả lập được trên Linux CI vì Linux luôn có bash sẵn)"

command -v pwsh >/dev/null 2>&1 || { echo "⚠ bỏ qua ca 2: không có pwsh trên máy này"; exit 0; }

echo "== ca 2 (động): có bash (đóng vai Git Bash trên Windows thật) — LUÔN trong thư mục cô lập =="
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
set +e
OUT2="$(pwsh -NoProfile -File "$SCRIPT" -Root "$TMP" -HarnessOnly -NoVerify 2>&1)"
CODE2=$?
set -e
[ "$CODE2" -eq 0 ] || fail "ca 2: kỳ vọng exit 0, được $CODE2 — output: $OUT2"
[ -d "$TMP/.harness" ] || fail "ca 2: không thấy $TMP/.harness sau khi cài"
[ -f "$TMP/CAPABILITIES.md" ] || fail "ca 2: thiếu CAPABILITIES.md — B3 chưa chạy"
echo "$OUT2" | grep -qi 'skills.*BỎ QUA\|BỎ QUA.*skill' && ! echo "$OUT2" | grep -qi 'demo.sh (' \
  || fail "ca 2: -HarnessOnly/-NoVerify có vẻ KHÔNG được tôn trọng (log: $OUT2)"
echo "  ok — .harness/ + CAPABILITIES.md xuất hiện, harness-only + no-verify được tôn trọng, exit 0"

echo "✓ install-ps1-test.sh PASS"
