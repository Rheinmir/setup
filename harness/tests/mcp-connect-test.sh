#!/usr/bin/env bash
# mcp-connect-test — connect-mcp.sh trỏ máy dev về server trung tâm đúng cách, không phá cấu hình người dùng:
#   (1) mặc định: `claude mcp add -s user --transport http overstack <URL>` + env OVERSTACK_VERSION_URL=<URL>/healthz, giữ key khác
#   (2) idempotent: chạy lại → remove rồi add, settings không nhân đôi
#   (3) env đã có giá trị riêng → giữ nguyên (--force mới ghi đè); token → header Bearer; URL tuỳ biến → healthz suy ra đúng
#   (4) --off gỡ cả hai; (5) không có claude trên PATH → vẫn ghi env, rc 0; (6) bootstrap có --no-mcp và gọi script này mặc định
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
S="$ROOT/harness/scripts/connect-mcp.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
PASS=0; FAIL=0; ok(){ PASS=$((PASS+1)); echo "  PASS  $*"; }; no(){ FAIL=$((FAIL+1)); echo "  FAIL  $*"; }
# claude giả: ghi argv từng lần gọi, `mcp remove` lần đầu báo "không có" (rc 1) như thật
mkdir -p "$T/bin"; cat > "$T/bin/claude" <<'EOF'
#!/usr/bin/env bash
echo "$*" >> "$CLAUDE_LOG"
case "$1 $2" in "mcp remove") grep -q "^mcp add" "$CLAUDE_LOG" 2>/dev/null || exit 1;; esac
exit 0
EOF
chmod +x "$T/bin/claude"
export CLAUDE_LOG="$T/claude.log" CLAUDE_SETTINGS="$T/settings.json" HOME="$T/home"; mkdir -p "$HOME"
printf '{"env":{"PYTHONUTF8":"1"},"permissions":{"deny":["Bash(rm -rf /)"]}}\n' > "$CLAUDE_SETTINGS"
# healthz giả trên cổng ngẫu nhiên: ca (1)-(4) chạy với server "đang lên"; ca (7) với URL chết
PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1])')
python3 - "$PORT" <<'PY' &
import sys, json
from http.server import BaseHTTPRequestHandler, HTTPServer
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"ok": True, "harness": "9.9.9", "skills": {"version": "9.9.9", "count": 106}, "mode": "read"}).encode()
        self.send_response(200 if self.path == "/healthz" else 404); self.send_header("content-type", "application/json"); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass
HTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
PY
HP=$!; disown $HP 2>/dev/null || true; trap 'kill $HP 2>/dev/null; wait $HP 2>/dev/null; rm -rf "$T"' EXIT
for i in $(seq 1 30); do curl -fsS "http://127.0.0.1:$PORT/healthz" >/dev/null 2>&1 && break; sleep 0.2; done
export OVERSTACK_MCP_URL="http://127.0.0.1:$PORT/mcp"
run(){ PATH="$T/bin:$PATH" bash "$S" "$@"; }

# (1)
run >/dev/null 2>&1 || true
grep -q "^mcp add -s user --transport http overstack http://127.0.0.1:$PORT/mcp$" "$CLAUDE_LOG" && ok "(1) claude mcp add scope user, http, không header (healthz đã trả lời)" || no "(1) add: $(cat "$CLAUDE_LOG")"
python3 - "$CLAUDE_SETTINGS" <<'PY' && ok "(1) env OVERSTACK_VERSION_URL=healthz, key khác còn nguyên" || no "(1) settings"
import json,sys; d=json.load(open(sys.argv[1]))
assert d["env"]["OVERSTACK_VERSION_URL"].endswith("/healthz") and "127.0.0.1" in d["env"]["OVERSTACK_VERSION_URL"], d
assert d["env"]["PYTHONUTF8"]=="1" and d["permissions"]["deny"]==["Bash(rm -rf /)"], d
PY
# (2)
run >/dev/null 2>&1 || true
[ "$(grep -c '^mcp add' "$CLAUDE_LOG")" = 2 ] && grep -q "^mcp remove -s user overstack" "$CLAUDE_LOG" && ok "(2) chạy lại: remove rồi add (idempotent)" || no "(2) $(cat "$CLAUDE_LOG")"
[ "$(python3 -c "import json,sys;print(len(json.load(open(sys.argv[1]))['env']))" "$CLAUDE_SETTINGS")" = 2 ] && ok "(2) settings không nhân đôi" || no "(2) settings env phình"
# (3)
python3 - "$CLAUDE_SETTINGS" <<'PY'
import json,sys; p=sys.argv[1]; d=json.load(open(p)); d["env"]["OVERSTACK_VERSION_URL"]="http://127.0.0.1:9/healthz"; json.dump(d,open(p,"w"))
PY
: > "$CLAUDE_LOG"
OVERSTACK_MCP_URL=https://mcp.example.vn/mcp OVERSTACK_MCP_TOKEN=tok-0123456789abcdef run --no-probe >/dev/null 2>&1 || true
grep -q '^mcp add -s user --transport http overstack https://mcp.example.vn/mcp --header Authorization: Bearer tok-0123456789abcdef$' "$CLAUDE_LOG" && ok "(3) URL tuỳ biến + token → header Bearer (--no-probe bỏ dò)" || no "(3) $(cat "$CLAUDE_LOG")"
[ "$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['env']['OVERSTACK_VERSION_URL'])" "$CLAUDE_SETTINGS")" = "http://127.0.0.1:9/healthz" ] && ok "(3) env người dùng đặt tay được GIỮ" || no "(3) env bị ghi đè"
OVERSTACK_MCP_URL=https://mcp.example.vn/mcp run --force --no-probe >/dev/null 2>&1 || true
[ "$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['env']['OVERSTACK_VERSION_URL'])" "$CLAUDE_SETTINGS")" = "https://mcp.example.vn/healthz" ] && ok "(3) --force ghi đè, healthz suy từ URL" || no "(3) --force"
# (4)
: > "$CLAUDE_LOG"; run --off >/dev/null 2>&1 || true
grep -q "^mcp remove -s user overstack" "$CLAUDE_LOG" && ! python3 -c "import json,sys;d=json.load(open(sys.argv[1]));sys.exit(0 if 'OVERSTACK_VERSION_URL' in d['env'] else 1)" "$CLAUDE_SETTINGS" && ok "(4) --off gỡ MCP + env" || no "(4) --off"
# (5)
: > "$CLAUDE_LOG"; rm -f "$CLAUDE_SETTINGS"
if PATH="/usr/bin:/bin:/usr/local/bin" bash "$S" >"$T/out5" 2>&1; then
  grep -q "không thấy" "$T/out5" && [ -f "$CLAUDE_SETTINGS" ] && ok "(5) không có claude: ghi env, nói rõ, rc 0" || no "(5) $(cat "$T/out5")"
else no "(5) rc≠0 khi thiếu claude"; fi
# (7) server chưa lên: env vẫn ghi, KHÔNG đăng ký MCP, nói rõ lệnh chạy lại
: > "$CLAUDE_LOG"; rm -f "$CLAUDE_SETTINGS"
if OVERSTACK_MCP_URL=http://127.0.0.1:9/mcp run >"$T/out7" 2>&1; then
  ! grep -q "^mcp add" "$CLAUDE_LOG" && grep -q "CHƯA đăng ký" "$T/out7" && python3 -c "import json,sys;d=json.load(open(sys.argv[1]));assert d['env']['OVERSTACK_VERSION_URL']=='http://127.0.0.1:9/healthz'" "$CLAUDE_SETTINGS" && ok "(7) server chưa lên: không add MCP, env vẫn đặt, rc 0" || no "(7) $(cat "$T/out7"; cat "$CLAUDE_LOG")"
else no "(7) rc≠0 khi server chưa lên"; fi
# (6)
grep -q -- "--no-mcp" "$ROOT/harness/poc-vendor-neutral/bootstrap.sh" && grep -q "connect-mcp.sh" "$ROOT/harness/poc-vendor-neutral/bootstrap.sh" && ok "(6) bootstrap: cờ --no-mcp + gọi connect-mcp.sh" || no "(6) bootstrap chưa nối"
grep -q "connect-mcp" "$ROOT/README.md" && ok "(6) README nói về cấu hình mặc định trỏ server" || no "(6) README"

echo ""; echo "mcp-connect-test: $PASS PASS · $FAIL FAIL"; [ "$FAIL" = 0 ]
