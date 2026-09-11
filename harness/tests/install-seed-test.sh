#!/usr/bin/env bash
# install-seed-test.sh — GH#149: installer seed khung llmwiki ở MỌI mode (không chỉ MODE=new),
# không đè file có sẵn của project, chạy lại không đổi gì.
# Sandbox: project tạm + HOME tạm, không đụng máy thật.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
INST="$HERE/../scripts/install-harness.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
export HOME="$TMP/home"; mkdir -p "$HOME"
pass=0
assert() { if [ "$2" = "$3" ]; then pass=$((pass+1)); echo "  ✓ $1"; else echo "  ✗ $1 (mong '$2', được '$3')"; exit 1; fi; }
# 4 thư mục khung chỉ khối seed tạo: html · inbox tài liệu · skills · wiki
seed() { ls "$1/llmwiki" | grep -c -x -E 'html|raw|skills|wiki'; }
snap() { (cd "$1/llmwiki" && find . -type f ! -name log.md -print0 | sort -z | xargs -0 shasum) | shasum; }
inst() { bash "$INST" "$1" >"$TMP/log.$2" 2>&1; }

echo "[1] project mới trắng → đủ khung (không hồi quy)"
P1="$TMP/new"; mkdir -p "$P1"; git -C "$P1" init -q
inst "$P1" new; rc=$?
assert "installer rc=0" 0 "$rc"
assert "log ghi mode new" 1 "$(grep -c 'mode: new' "$TMP/log.new")"
assert "đủ 4 thư mục khung" 4 "$(seed "$P1")"
assert "wiki/index.md được tạo" 1 "$([ -f "$P1/llmwiki/wiki/index.md" ] && echo 1 || echo 0)"

echo "[2] project đã có llmwiki/wiki (BRD đặt sẵn ở draft) → migrate vẫn bổ sung khung, không đè"
P2="$TMP/mig"; mkdir -p "$P2/llmwiki/wiki/sources/draft"; git -C "$P2" init -q
printf 'BRD gốc\n' > "$P2/llmwiki/wiki/sources/draft/brd.md"
printf '# Index riêng\n' > "$P2/llmwiki/wiki/index.md"
inst "$P2" mig1; rc=$?
# rc=3 = "MIGRATE CÓ NỢ": hooks đã cài, baseline audit báo BRD thiếu Origin/dòng index — đúng kịch bản thật.
assert "installer rc=3 (migrate có nợ baseline, vẫn cài xong)" 3 "$rc"
assert "log ghi mode migrate" 1 "$(grep -c 'mode: migrate' "$TMP/log.mig1")"
assert "đủ 4 thư mục khung" 4 "$(seed "$P2")"
assert "BRD giữ nguyên" "BRD gốc" "$(cat "$P2/llmwiki/wiki/sources/draft/brd.md")"
assert "index.md không bị đè" "# Index riêng" "$(head -1 "$P2/llmwiki/wiki/index.md")"

echo "[3] chạy lần hai liên tiếp → cây llmwiki/ không đổi"
nbak() { ls -a "$1/.claude" "$1/llmwiki/.claude" 2>/dev/null | grep -c 'settings.json.bak'; }
before=$(snap "$P2"); b0=$(nbak "$P2"); inst "$P2" mig2; after=$(snap "$P2")
assert "snapshot llmwiki/ giống hệt (trừ log.md append)" "$before" "$after"
assert "không đẻ thêm settings.json.bak khi merge không đổi" "$b0" "$(nbak "$P2")"

echo "PASS $pass/$pass"
