#!/usr/bin/env bash
# install-ps1-test.sh — proof cho harness/poc-vendor-neutral/install.ps1 (Windows entry point).
# Bỏ qua fail-open nếu máy CI không có pwsh (không phải mọi runner có PowerShell Core).
#
# Ca 1: KHÔNG có shell POSIX nào trên PATH → dừng đúng thông báo, exit 1 (không âm thầm treo).
# Ca 2: có bash trên PATH (đóng vai Git Bash) → -HarnessOnly -NoVerify cài thật vào thư mục
#       sạch, exit 0, và .harness/ phải xuất hiện. Đây là đường thật install.ps1 sẽ đi trên
#       Windows qua Git Bash/WSL — bash ở đây chỉ khác BINARY, không khác LOGIC (script không
#       phân biệt bash nào, chỉ gọi `& $bash.Source -s -- args`).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT="$ROOT/harness/poc-vendor-neutral/install.ps1"
fail() { echo "✗ $*" >&2; exit 1; }

command -v pwsh >/dev/null 2>&1 || { echo "⚠ bỏ qua: không có pwsh trên máy này"; exit 0; }
[ -f "$SCRIPT" ] || fail "thiếu $SCRIPT"

echo "== ca 1: không có shell POSIX nào =="
PWSH_BIN="$(command -v pwsh)"; PWSH_DIR="$(dirname "$PWSH_BIN")"
set +e
OUT="$(env -i PATH="$PWSH_DIR" HOME="$HOME" pwsh -NoProfile -File "$SCRIPT" 2>&1)"
CODE=$?
set -e
[ "$CODE" -eq 1 ] || fail "ca 1: kỳ vọng exit 1, được $CODE — output: $OUT"
echo "$OUT" | grep -q "Git for Windows" || fail "ca 1: thiếu hướng dẫn cài Git for Windows"
echo "  ok — dừng đúng thông báo, exit 1"

echo "== ca 2: có bash (đóng vai Git Bash) — cài thật --harness-only --no-verify =="
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
set +e
OUT2="$(pwsh -NoProfile -File "$SCRIPT" -Root "$TMP" -HarnessOnly -NoVerify 2>&1)"
CODE2=$?
set -e
[ "$CODE2" -eq 0 ] || fail "ca 2: kỳ vọng exit 0, được $CODE2 — output: $OUT2"
[ -d "$TMP/.harness" ] || fail "ca 2: không thấy $TMP/.harness sau khi cài"
[ -f "$TMP/CAPABILITIES.md" ] || fail "ca 2: thiếu CAPABILITIES.md — B3 chưa chạy"
echo "  ok — .harness/ + CAPABILITIES.md xuất hiện, exit 0"

echo "✓ install-ps1-test.sh PASS"
