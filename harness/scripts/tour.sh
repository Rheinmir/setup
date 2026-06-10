#!/usr/bin/env bash
# tour.sh — máy diễn 5 cảnh để bạn THẤY harness làm gì, trong sandbox /tmp, tự dọn sạch.
# Usage: bash harness/scripts/tour.sh        (chạy từ bất kỳ đâu, không đụng project của bạn)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SBX="$(mktemp -d /tmp/harness-tour.XXXXXX)"
trap 'rm -rf "$SBX"' EXIT

B=$'\033[1m'; G=$'\033[1;32m'; Y=$'\033[1;33m'; R=$'\033[0;90m'; N=$'\033[0m'
scene(){ printf '\n%s🎬 Cảnh %s — %s%s\n' "$B" "$1" "$2" "$N"; }
act()  { printf '   %s$ %s%s\n' "$R" "$1" "$N"; }
hit()  { printf '   %s⛔ BỊ CHẶN%s %s\n' "$Y" "$N" "$1"; }
ok()   { printf '   %s✓%s %s\n' "$G" "$N" "$1"; }

printf '%s════ HARNESS TOUR — hệ thống này làm gì? (sandbox: %s) ════%s\n' "$B" "$SBX" "$N"

# Cài harness vào sandbox (im lặng) — đây cũng chính là demo installer
( cd "$SBX" && git init -q . && bash "$SCRIPT_DIR/install-harness.sh" "$SBX" >/dev/null 2>&1 ) || true
V="$SBX/harness/validators"
[ -d "$V" ] || { echo "Cài sandbox thất bại — chạy từ repo có harness/"; exit 1; }
ok "Đã cài harness vào sandbox bằng install-harness.sh (mode NEW)"

scene 1 "Agent cố ghi vào raw/ — inbox của con người"
act 'Write llmwiki/raw/hack.md'
OUT=$(printf '%s' '{"action":"write","file_path":"llmwiki/raw/hack.md"}' | python3 "$V/no_write_raw.py" 2>&1) && true
hit "$OUT"
act 'bash: echo "x" > llmwiki/raw/hack.md   (lách qua đường bash cũng không thoát)'
OUT=$(printf '%s' '{"action":"bash","command":"echo x > llmwiki/raw/hack.md"}' | python3 "$V/no_write_raw.py" 2>&1) && true
hit "$OUT"

scene 2 "Wiki file thiếu '## Origin' — tri thức không truy được nguồn"
act 'Write llmwiki/wiki/concepts/demo.md (không có Origin)'
OUT=$(printf '%s' '{"action":"write","file_path":"llmwiki/wiki/concepts/demo.md","content":"# Demo"}' | python3 "$V/origin_required.py" 2>&1) && true
hit "$OUT"
ok "Trong phiên thật: stderr này quay về Claude → nó PHẢI tự thêm Origin ngay"

scene 3 "File .md vứt bừa vào wiki/ root"
act 'Write llmwiki/wiki/notes.md'
OUT=$(printf '%s' '{"action":"write","file_path":"llmwiki/wiki/notes.md"}' | python3 "$V/folder_structure.py" 2>&1) && true
hit "$OUT"

scene 4 "index.md nói dối — có file mà index không ghi"
act 'tạo wiki/concepts/real-page.md (có Origin) nhưng KHÔNG cập nhật index.md'
printf '# Real\n\n## Origin\n- tour demo\n' > "$SBX/llmwiki/wiki/concepts/real-page.md"
OUT=$(python3 "$V/index_sync.py" --wiki-dir "$SBX/llmwiki/wiki" 2>&1) && true
hit "$OUT"
ok "Trong phiên thật: Stop hook dùng đúng check này — Claude KHÔNG ĐƯỢC kết thúc lượt khi index lệch"

scene 5 "Audit — máy ghi log, model không thể quên"
act 'giả lập 1 tool call đi qua PostToolUse hook'
printf '%s' "{\"session_id\":\"tour\",\"cwd\":\"$SBX\",\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$SBX/llmwiki/wiki/concepts/real-page.md\"}}" \
  | CLAUDE_PROJECT_DIR="$SBX" python3 "$SBX/llmwiki/.claude/hooks/post_tool_use.py" >/dev/null 2>&1 || true
AUDIT=$(ls "$SBX/.claude/audit/"*.jsonl 2>/dev/null | head -1)
if [ -n "$AUDIT" ]; then ok "JSONL xuất hiện tự động: $(basename "$AUDIT") — nội dung:"; sed 's/^/      /' "$AUDIT"; fi

printf '\n%s════ TÓM TẮT ════%s\n' "$B" "$N"
ok "R1 chặn ghi raw/ (cả Write lẫn bash)"
ok "R2 ép mọi tri thức có '## Origin'"
ok "R5 giữ wiki đúng cấu trúc folder"
ok "R3 không cho kết thúc phiên khi index nói dối"
ok "R4 log bằng máy — audit JSONL + log.md tự sinh"
printf '   %sTất cả 0 token, chạy ngầm, không lệnh mới phải nhớ. Sandbox đã tự dọn.%s\n' "$R" "$N"
printf '   %sXem nó cắn Claude thật: gọi /harness-tour trong phiên Claude Code.%s\n\n' "$R" "$N"
