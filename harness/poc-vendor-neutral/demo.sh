#!/usr/bin/env bash
# demo.sh — chứng minh PoC chạy thật: 1 LÕI deny đúng/sai, rồi sinh wiring mọi vendor.
set -uo pipefail
cd "$(dirname "$0")"
CLI="bin/llmwiki-validate.py"
pass=0; fail=0
ok()   { printf '  \033[1;32mPASS\033[0m %s\n' "$1"; pass=$((pass+1)); }
bad()  { printf '  \033[1;31mFAIL\033[0m %s\n' "$1"; fail=$((fail+1)); }
# expect <mô tả> <exit-mong-đợi> -- <lệnh...>
expect() { local d="$1" want="$2"; shift 3; "$@" >/dev/null 2>&1; local got=$?; [ "$got" = "$want" ] && ok "$d (exit $got)" || bad "$d (muốn $want, được $got)"; }

echo "── 1. LÕI: mode path (layer=session) ──"
expect "chặn ghi llmwiki/raw/x.md"            2 -- python3 "$CLI" path llmwiki/raw/x.md
expect "chặn ghi raw/note.md (no prefix)"     2 -- python3 "$CLI" path raw/note.md
expect "cho ghi wiki/concepts/foo.md"         0 -- python3 "$CLI" path llmwiki/wiki/concepts/foo.md
expect "cho ghi src/app.ts"                   0 -- python3 "$CLI" path src/app.ts

echo "── 2. LÕI: mode claude-hook (PreToolUse JSON stdin) ──"
echo '{"tool_name":"Write","tool_input":{"file_path":"llmwiki/raw/leak.md","content":"x"}}' | python3 "$CLI" claude-hook >/dev/null 2>&1
[ $? = 2 ] && ok "Write→raw/ bị chặn" || bad "Write→raw/ KHÔNG bị chặn"
echo '{"tool_name":"Bash","tool_input":{"command":"echo hi > llmwiki/raw/x.md"}}' | python3 "$CLI" claude-hook >/dev/null 2>&1
[ $? = 2 ] && ok "Bash redirect→raw/ bị chặn" || bad "Bash→raw/ KHÔNG bị chặn"
echo '{"tool_name":"Bash","tool_input":{"command":"cat llmwiki/raw/x.md"}}' | python3 "$CLI" claude-hook >/dev/null 2>&1
[ $? = 0 ] && ok "Bash ĐỌC raw/ được phép" || bad "Bash đọc raw/ bị chặn nhầm"
echo '{"tool_name":"Write","tool_input":{"file_path":"llmwiki/wiki/concepts/x.md","content":"---\ntype: concept\n---\n# x\n## Origin\n- src"}}' | python3 "$CLI" claude-hook >/dev/null 2>&1
[ $? = 0 ] && ok "concept CÓ ## Origin được phép" || bad "concept có Origin bị chặn nhầm"
echo '{"tool_name":"Write","tool_input":{"file_path":"llmwiki/wiki/concepts/y.md","content":"# y no origin"}}' | python3 "$CLI" claude-hook >/dev/null 2>&1
[ $? = 2 ] && ok "concept THIẾU ## Origin bị chặn" || bad "concept thiếu Origin KHÔNG bị chặn"

echo "── 3. LÕI: mode files (layer=repo — KHÔNG áp no_write_raw vì enforce_at=[session]) ──"
tmp="$(mktemp -d)"; mkdir -p "$tmp/llmwiki/raw" "$tmp/llmwiki/wiki/concepts"
echo "human inbox" > "$tmp/llmwiki/raw/human.md"
echo "---
type: concept
---
# c
## Origin
- src" > "$tmp/llmwiki/wiki/concepts/good.md"
echo "# c no origin" > "$tmp/llmwiki/wiki/concepts/bad.md"
expect "repo: raw/ KHÔNG bị chặn (con người commit hợp lệ)" 0 -- python3 "$CLI" files "$tmp/llmwiki/raw/human.md"
expect "repo: concept tốt qua"                              0 -- python3 "$CLI" files "$tmp/llmwiki/wiki/concepts/good.md"
expect "repo: concept thiếu Origin bị fail"                 1 -- python3 "$CLI" files "$tmp/llmwiki/wiki/concepts/bad.md"
rm -rf "$tmp"

echo "── 4. fail-open: policy lỗi → KHÔNG chặn ──"
expect "policy thiếu → exit 0 (fail-open)" 0 -- python3 "$CLI" --policy /no/such/policy.yaml path llmwiki/raw/x.md

echo "── 5. Sinh wiring mọi vendor từ 1 policy.yaml ──"
python3 gen-converters.py

echo
echo "── Cây out/ ──"
find out -type f | sort | sed 's,^,  ,'
echo
printf '\033[1mKẾT QUẢ: %d PASS · %d FAIL\033[0m\n' "$pass" "$fail"
[ "$fail" = 0 ] || exit 1
