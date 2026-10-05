#!/usr/bin/env bash
# dot-layout-migrate-test.sh — chứng minh migrate layout ẩn chạy đúng (9 assertion).
# Sandbox trong $TMPDIR, không đụng repo thật.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
INSTALL="$HERE/../poc-vendor-neutral/install.sh"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
pass=0
ck(){ if [ "$2" = "$3" ]; then pass=$((pass+1)); echo "  ✓ $1"; else echo "  ✗ $1 (mong '$2', được '$3')"; exit 1; fi; }

# Trích ĐÚNG hàm migrate từ installer thật — test không được nhân bản logic.
extract(){ sed -n '/^migrate_dot_layout(){/,/^}/p' "$INSTALL"; }

run_migrate(){ # run_migrate <root>
  ROOT="$1"
  eval "log(){ :; }; warn(){ :; }"
  eval "$(extract)"
  migrate_dot_layout
}

# 1. Dự án chuẩn CŨ → dọn vào dấu chấm
P="$TMP/old"; mkdir -p "$P/llmwiki/wiki/concepts" "$P/harness/scripts" "$P/src"
echo "noi dung" > "$P/llmwiki/wiki/concepts/a.md"
mkdir -p "$P/.claude"
# settings.json ĐỜI CŨ (trước v4, hook per-project). Bản cài hiện tại KHÔNG ghi hook vào dự án khách:
# hook chạy từ ~/.claude/harness/hooks. Fixture này chỉ tồn tại để kiểm migrate viết lại con trỏ đời cũ.
printf '{"hooks":{"SessionStart":[{"command":"python3 \\"$CLAUDE_PROJECT_DIR/llmwiki/.claude/hooks/session_start.py\\""}]}}\n' > "$P/.claude/settings.json"
# Lệnh hook HIỆN HÀNH (wire bởi install-harness): engine global ~/.claude/harness/ KHÔNG được bị đổi thành ~/.claude/.harness/
printf '{"hooks":{"UserPromptSubmit":[{"command":"python3 \\"$HOME/.claude/harness/hooks/user_prompt_submit.py\\""}]}}\n' > "$P/.claude/settings.local.json"
printf 'llmwiki/html/*.png\n' > "$P/.gitignore"
( run_migrate "$P" ) >/dev/null 2>&1
ck "llmwiki/ được dọn vào .llmwiki/" "yes" "$([ -d "$P/.llmwiki" ] && [ ! -d "$P/llmwiki" ] && echo yes || echo no)"
ck "harness/ được dọn vào .harness/"  "yes" "$([ -d "$P/.harness" ] && [ ! -d "$P/harness" ] && echo yes || echo no)"
ck "nội dung không mất" "noi dung" "$(cat "$P/.llmwiki/wiki/concepts/a.md")"
ck "con trỏ hook được viết lại" "yes" \
   "$(grep -q '\.llmwiki/\.claude/hooks' "$P/.claude/settings.json" && echo yes || echo no)"
ck "engine global ~/.claude/harness/ giữ nguyên (không thành .claude/.harness/)" "yes" \
   "$(grep -q '\.claude/harness/hooks' "$P/.claude/settings.local.json" && ! grep -q '\.claude/\.harness/' "$P/.claude/settings.local.json" && echo yes || echo no)"
ck "gitignore được viết lại" "yes" \
   "$(grep -q '^\.llmwiki/html/' "$P/.gitignore" && echo yes || echo no)"

# 2. Chạy LẦN HAI trên cùng dự án → không đổi gì (idempotent)
before="$(cd "$P" && find . -maxdepth 2 | sort | md5)"
( run_migrate "$P" ) >/dev/null 2>&1
ck "chạy lại lần hai → im lặng, không đổi gì (idempotent)" "$before" "$(cd "$P" && find . -maxdepth 2 | sort | md5)"

# 3. Repo framework (có fdk/wiki) → KHÔNG BAO GIỜ tự migrate
F="$TMP/fw"; mkdir -p "$F/fdk/wiki" "$F/llmwiki/wiki" "$F/harness"
( run_migrate "$F" ) >/dev/null 2>&1
ck "repo framework giữ nguyên llmwiki/ (không tự migrate)" "yes" \
   "$([ -d "$F/llmwiki" ] && [ ! -d "$F/.llmwiki" ] && echo yes || echo no)"

# 4. Dự án ĐÃ bị regex cũ làm hỏng (~/.claude/.harness/) → bước sửa trong installer phải trả về ~/.claude/harness/
B="$TMP/broken"; mkdir -p "$B/.claude"
printf '{"hooks":{"UserPromptSubmit":[{"command":"python3 \\"$HOME/.claude/.harness/hooks/user_prompt_submit.py\\""}]}}\n' > "$B/.claude/settings.json"
( ROOT="$B"; log(){ :; }; eval "$(sed -n '/^# Sửa hậu quả của regex migrate cũ/,/^true$/p' "$INSTALL")" ) >/dev/null 2>&1
ck "dự án đã hỏng được sửa về ~/.claude/harness/" "yes" \
   "$(grep -q '\.claude/harness/hooks' "$B/.claude/settings.json" && ! grep -q '\.claude/\.harness/' "$B/.claude/settings.json" && echo yes || echo no)"

echo "dot-layout-migrate-test: $pass/9 assertion XANH"
