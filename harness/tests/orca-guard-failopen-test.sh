#!/usr/bin/env bash
# Chặn hồi quy sự cố cozyroom: hook THIẾU file KHÔNG được brick tool.
# Khoá cả 2 chiều: (a) hook thiếu file → lệnh guard exit 0 (fail-open, KHÔNG chặn Bash);
#                  (b) hook có file → vẫn chạy (không vô tình tắt hẳn guard).
set -uo pipefail

SRC="${1:?usage: orca-guard-failopen-test.sh <repo-root>}"
cd "$SRC"
PASS=0; FAIL=0; N=0
ok()  { N=$((N+1)); PASS=$((PASS+1)); printf '  \033[1;32mPASS\033[0m  %s\n' "$1"; }
bad() { N=$((N+1)); FAIL=$((FAIL+1)); printf '  \033[1;31mFAIL\033[0m  %s — %s\n' "$1" "$2"; }
hdr() { printf '\n\033[1m── %s\033[0m\n' "$1"; }

INSTALLER="harness/scripts/install-harness.sh"
SETTINGS="llmwiki/.claude/settings.json"

hdr "A — mọi lệnh hook sinh ra phải fail-open (\`[ -f ... ]\` guard)"
# Lệnh trần `python3 "<path>"` KHÔNG được tồn tại trong installer (phải bọc -f).
if grep -nE 'command.*python3 "\{?[^"]*\.py"' "$INSTALLER" | grep -v 'if \[ -f' | grep -q .; then
  bad "installer" "còn lệnh hook TRẦN (chưa bọc [ -f ]) — sẽ brick khi thiếu file"
else
  ok "installer: mọi lệnh hook đều có guard [ -f ]"
fi
# settings.json committed: mọi command phải bắt đầu bằng `if [ -f`
if python3 - "$SETTINGS" <<'PY'
import json,sys
s=json.load(open(sys.argv[1]))
bad=[h["command"] for defs in s.get("hooks",{}).values() for d in defs for h in d.get("hooks",[])
     if not h.get("command","").strip().startswith("if [ -f")]
sys.exit(1 if bad else 0)
PY
then ok "settings.json: 7 hook command đều fail-open"
else bad "settings.json" "có hook command chưa fail-open"
fi

hdr "B — hành vi runtime: thiếu file → exit 0; có file → chạy"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
MISS="$TMP/nope.py"        # cố tình KHÔNG tạo
HAVE="$TMP/yes.py"; printf 'import sys; sys.exit(0)\n' > "$HAVE"
# Lệnh guard y hệt dạng installer sinh ra:
run_guard() { eval "if [ -f \"$1\" ]; then python3 \"$1\"; fi"; }
if run_guard "$MISS"; then ok "hook THIẾU file → exit 0 (fail-open, KHÔNG chặn)"; else bad "missing-hook" "exit $? — bị chặn (brick)"; fi
if run_guard "$HAVE"; then ok "hook CÓ file → chạy bình thường"; else bad "present-hook" "exit $? — không chạy được"; fi
# Guard vẫn truyền được exit≠0 khi hook CÓ file và muốn CHẶN (không nuốt mã chặn):
BLOCK="$TMP/block.py"; printf 'import sys; sys.exit(2)\n' > "$BLOCK"
run_guard "$BLOCK"; rc=$?
[ "$rc" = "2" ] && ok "hook CÓ file trả exit 2 → guard giữ mã chặn (không nuốt)" || bad "block-passthrough" "rc=$rc, mong đợi 2"

hdr "C — kênh giao hook: orca_guard.py nằm trong manifest (sync kéo được)"
if python3 -c "import json,sys; sys.exit(0 if 'llmwiki/.claude/hooks/orca_guard.py' in json.load(open('.template-manifest.json'))['includes'] else 1)"; then
  ok "orca_guard.py có trong .template-manifest.json includes"
else
  bad "manifest" "orca_guard.py KHÔNG trong manifest → /sync-template không giao được"
fi

printf '\n\033[1m═══ TỔNG: %d test — \033[1;32m%d PASS\033[0m / \033[1;31m%d FAIL\033[0m\n' "$N" "$PASS" "$FAIL"
[ "$FAIL" = "0" ] && exit 0 || exit 1
