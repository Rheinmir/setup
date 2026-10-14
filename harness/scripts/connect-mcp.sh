#!/usr/bin/env bash
# connect-mcp.sh — trỏ máy dev về SERVER TRUNG TÂM của overstack, chạy MẶC ĐỊNH ở cuối bootstrap (opt-out: --no-mcp / OVERSTACK_MCP=0).
#   1. Claude Code: `claude mcp add -s user --transport http overstack <URL>` → mọi dự án trên máy thấy tool skill_find/skill_get/
#      rules_list… và 106 skill dưới dạng prompt, không cần ai dặn.
#   2. ~/.claude/settings.json env.OVERSTACK_VERSION_URL = <URL>/healthz → hook đầu phiên so bản harness/skill với bản chuẩn.
# Không ghi đè cấu hình người dùng đã đặt tay (settings env chỉ setdefault; --force để ghi đè). Idempotent. Không có `claude` → ghi chú, rc 0.
# Dò /healthz TRƯỚC: server chưa lên thì KHÔNG đăng ký MCP (một MCP chết làm mọi phiên Claude Code báo lỗi) — chỉ ghi env (hook
# đầu phiên tự lùi về raw GitHub khi URL không trả lời) và in lệnh chạy lại; --no-probe đăng ký ngay không dò; --force ghi đè env.
#   bash connect-mcp.sh                 # URL mặc định https://skills.giatbh.io.vn/mcp (đổi: OVERSTACK_MCP_URL=…)
#   OVERSTACK_MCP_TOKEN=… bash connect-mcp.sh   # server đặt bearer → gửi kèm header (đọc công khai thì không cần)
#   bash connect-mcp.sh --off           # gỡ: xoá MCP overstack (scope user) + env OVERSTACK_VERSION_URL
#   bash connect-mcp.sh --status        # đang trỏ đi đâu
set -euo pipefail
URL="${OVERSTACK_MCP_URL:-https://skills.giatbh.io.vn/mcp}"
TOKEN="${OVERSTACK_MCP_TOKEN:-}"
NAME="${OVERSTACK_MCP_NAME:-overstack}"
SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"
HEALTH="${URL%/mcp}/healthz"
MODE=on; FORCE=0; PROBE=1
for a in "$@"; do case "$a" in --off) MODE=off;; --status) MODE=status;; --force) FORCE=1;; --no-probe) PROBE=0;; -h|--help) sed -n 2,11p "$0"; exit 0;; *) echo "connect-mcp: cờ lạ $a" >&2; exit 1;; esac; done
say(){ printf '\033[1;36m[connect-mcp]\033[0m %s\n' "$*"; }

settings_env(){ # $1 = set|unset|get
  python3 - "$SETTINGS" "$1" "$HEALTH" "$FORCE" <<'PY'
import json, os, sys
path, op, url, force = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == "1"
cur = {}
if os.path.exists(path):
    try: cur = json.load(open(path, encoding="utf-8"))
    except ValueError: cur = {}
env = cur.setdefault("env", {}) if isinstance(cur.get("env", {}), dict) else {}
if op == "get":
    print(env.get("OVERSTACK_VERSION_URL", "")); sys.exit(0)
if op == "set":
    if force or "OVERSTACK_VERSION_URL" not in env: env["OVERSTACK_VERSION_URL"] = url; changed = "set"
    else: changed = "kept"
else:
    changed = "unset" if env.pop("OVERSTACK_VERSION_URL", None) is not None else "absent"
os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
json.dump(cur, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False); open(path, "a").write("\n")
print(changed)
PY
}

if [ "$MODE" = status ]; then
  say "settings env OVERSTACK_VERSION_URL = $(settings_env get || echo '(không đọc được)')"
  command -v claude >/dev/null 2>&1 && claude mcp get "$NAME" 2>/dev/null | head -6 || say "claude CLI không có trên PATH"
  exit 0
fi

if [ "$MODE" = off ]; then
  r=$(settings_env unset); say "env OVERSTACK_VERSION_URL: $r"
  if command -v claude >/dev/null 2>&1; then claude mcp remove -s user "$NAME" >/dev/null 2>&1 && say "đã gỡ MCP $NAME (scope user)" || say "MCP $NAME không có ở scope user"; fi
  exit 0
fi

r=$(settings_env set); say "env OVERSTACK_VERSION_URL=$HEALTH ($r$([ "$r" = kept ] && echo ' — đã có giá trị riêng, giữ; --force để ghi đè'))"
if ! command -v claude >/dev/null 2>&1; then
  say "không thấy \`claude\` trên PATH — bỏ qua đăng ký MCP; cài Claude Code rồi chạy lại: bash ~/.claude/harness/harness/scripts/connect-mcp.sh"
  exit 0
fi
HB=""
if [ "$PROBE" = 1 ]; then
  if command -v curl >/dev/null 2>&1; then HB=$(curl -fsS --max-time 8 "$HEALTH" 2>/dev/null || true); fi
  if [ -z "$HB" ]; then
    say "healthz chưa trả lời ($HEALTH) — CHƯA đăng ký MCP $NAME (MCP chết sẽ làm mỗi phiên Claude Code báo lỗi)."
    say "  server lên rồi thì chạy: bash ~/.claude/harness/harness/scripts/connect-mcp.sh   (hoặc --no-probe để đăng ký ngay)"
    exit 0
  fi
fi
# scope user = mọi dự án trên máy này. Gỡ bản cũ (URL/header có thể đổi) rồi thêm lại — idempotent.
claude mcp remove -s user "$NAME" >/dev/null 2>&1 || true
if [ -n "$TOKEN" ]; then
  claude mcp add -s user --transport http "$NAME" "$URL" --header "Authorization: Bearer $TOKEN" >/dev/null
  say "MCP $NAME → $URL (scope user, có bearer)"
else
  claude mcp add -s user --transport http "$NAME" "$URL" >/dev/null
  say "MCP $NAME → $URL (scope user, đọc công khai — server đòi bearer thì đặt OVERSTACK_MCP_TOKEN rồi chạy lại)"
fi
[ -n "$HB" ] && say "healthz: $(printf '%s' "$HB" | python3 -c 'import json,sys; d=json.load(sys.stdin); s=d.get("skills") or {}; print(f"harness {d.get(\"harness\")} · skills {s.get(\"version\")} ({s.get(\"count\")}) · mode {d.get(\"mode\")}")' 2>/dev/null || printf '%s' "$HB" | head -c 120)"
exit 0
