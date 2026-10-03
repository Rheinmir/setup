#!/usr/bin/env bash
# llmwiki-validate: cache policy đã parse phải (1) cho cùng quyết định với lúc không cache, (2) mất hiệu lực
# ngay khi policy đổi nội dung, (3) không làm hỏng gì khi thư mục cache không ghi được.
set -uo pipefail
ROOT="$(cd "${1:-.}" && pwd)"
V="$ROOT/harness/poc-vendor-neutral/bin/llmwiki-validate.py"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
ok=0; fail=0
check() { if [ "$2" = "$3" ]; then echo "  ✓ $1"; ok=$((ok+1)); else echo "  ✗ $1 (mong $3, được $2)"; fail=$((fail+1)); fi; }
cat > "$T/p1.yaml" <<'Y'
rules:
  no_raw:
    id: RX
    kind: deny_write
    enforce_at: [session]
    deny_write_globs: ["**/raw/**"]
Y
sed 's#\*\*/raw/\*\*#**/secret/**#' "$T/p1.yaml" > "$T/p2.yaml"
hook() { echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$2\",\"content\":\"x\"}}" | XDG_CACHE_HOME="$3" python3 "$V" --policy "$1" claude-hook 2>/dev/null; echo $?; }
C="$T/cache"
check "lần đầu (chưa cache) chặn ghi raw/" "$(hook "$T/p1.yaml" a/raw/x.md "$C")" 2
check "đã tạo đúng 1 file cache" "$(ls "$C/overstack" | wc -l | tr -d ' ')" 1
check "lần sau (đọc cache) vẫn chặn ghi raw/" "$(hook "$T/p1.yaml" a/raw/x.md "$C")" 2
check "lần sau vẫn cho ghi chỗ khác" "$(hook "$T/p1.yaml" a/ok/x.md "$C")" 0
cp "$T/p2.yaml" "$T/p1.yaml"
check "policy đổi nội dung → luật mới có hiệu lực ngay (raw/ được ghi)" "$(hook "$T/p1.yaml" a/raw/x.md "$C")" 0
check "policy đổi nội dung → luật mới chặn secret/" "$(hook "$T/p1.yaml" a/secret/x.md "$C")" 2
mkdir -p "$T/ro" && chmod 500 "$T/ro"
check "thư mục cache không ghi được → vẫn chặn đúng" "$(hook "$T/p1.yaml" a/secret/x.md "$T/ro")" 2
chmod 700 "$T/ro"
echo "  $ok/$((ok+fail)) pass"
[ "$fail" -eq 0 ]
