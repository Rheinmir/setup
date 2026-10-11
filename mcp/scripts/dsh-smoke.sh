#!/usr/bin/env bash
# dsh thật nối vào overstack-mcp và gọi một tool trong MỘT lượt model — bằng chứng "plug được vào dsh".
#   cd <repo dsh>  (DEEPSEEK_API_KEY trong .env hoặc env)
#   OVERSTACK_MCP_URL=http://127.0.0.1:8791/mcp OVERSTACK_MCP_TOKEN=… \
#   DSH_EXTRA_PATCHES="path/to/model.overlay.yml path/to/other.overlay.yml" \
#   bash <repo overstack>/mcp/scripts/dsh-smoke.sh
# Kiểm: (1) headless --json kết thúc không lỗi, (2) log phiên (~/.dsh/sessions/<slug>/<sid>/session.v4.jsonl[.zstd]) có
# tool/call tên mcp__overstack__skill_find và tool/result tương ứng. rc 0 khi cả hai qua.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OVERLAY="$HERE/../clients/dsh.overlay.yml"
: "${OVERSTACK_MCP_URL:=http://127.0.0.1:8791/mcp}"
: "${OVERSTACK_MCP_TOKEN:?set OVERSTACK_MCP_TOKEN to the server bearer token}"
export OVERSTACK_MCP_URL OVERSTACK_MCP_TOKEN
TOOL="${SMOKE_TOOL:-mcp__overstack__skill_find}"
DEFAULT_TASK="Gọi tool $TOOL với query 'render markdown to html' và k=3, rồi trả lời đúng một dòng: tên skill xếp đầu."
TASK="${SMOKE_TASK:-$DEFAULT_TASK}"
OUT="${SMOKE_OUT:-$(mktemp -t dsh-smoke.XXXXXX).jsonl}"

PATCHES=(--patch "$OVERLAY")
for p in ${DSH_EXTRA_PATCHES:-}; do PATCHES+=(--patch "$p"); done
# launcher flags (--patch) đứng trước app-args (--json, task): mọi thứ sau cờ launcher đầu tiên lạ sẽ rơi vào app
echo "→ dsh headless ${PATCHES[*]} --json"
set +e
corepack pnpm --silent dsh headless "${PATCHES[@]}" --json "$TASK" > "$OUT" 2> "$OUT.err"
RC=$?
set -e
echo "   rc=$RC  events=$(wc -l < "$OUT")  log=$OUT"
SID=$(python3 -c 'import json,sys
for ln in open(sys.argv[1]):
    try: o=json.loads(ln)
    except Exception: continue
    if o.get("type")=="session": print(o["sessionId"]); break' "$OUT")
FINAL=$(python3 -c 'import json,sys
for ln in open(sys.argv[1]):
    try: o=json.loads(ln)
    except Exception: continue
    if o.get("type")=="final": print(o.get("text","")[:300])' "$OUT")
ERR=$(python3 -c 'import json,sys
for ln in open(sys.argv[1]):
    try: o=json.loads(ln)
    except Exception: continue
    if o.get("type")=="status" and o.get("phase")=="turn_end" and o.get("reason",{}).get("kind")=="error": print(json.dumps(o["reason"])[:400])' "$OUT")
echo "   session=$SID"
echo "   final=${FINAL:-<empty>}"
[[ -n "$ERR" ]] && { echo "✖ turn ended with error: $ERR"; tail -20 "$OUT.err"; exit 1; }
[[ -z "$SID" ]] && { echo "✖ no session event"; tail -20 "$OUT.err"; exit 1; }

DIR=$(find "${DSH_HOME:-$HOME/.dsh}/sessions" -maxdepth 2 -type d -name "$SID" | head -1)
[[ -z "$DIR" ]] && { echo "✖ session dir for $SID not found under ${DSH_HOME:-$HOME/.dsh}/sessions"; exit 1; }
LOG="$OUT.session.jsonl"
if [[ -f "$DIR/session.v4.jsonl.zstd" ]]; then zstd -d -c -q "$DIR/session.v4.jsonl.zstd" > "$LOG"; else cp "$DIR/session.v4.jsonl" "$LOG"; fi
# Đếm bằng python: mọi event tool/call có name == $TOOL, và tool/result nói chung (định dạng log là JSONL, mỗi dòng một event)
python3 - "$LOG" "$TOOL" <<'PY'
import json, sys
log, tool = sys.argv[1], sys.argv[2]
calls = results = 0
for ln in open(log, encoding="utf-8", errors="replace"):
    ln = ln.strip()
    if not ln:
        continue
    try:
        o = json.loads(ln)
    except json.JSONDecodeError:
        continue
    s = json.dumps(o)
    if '"tool/call"' in s and tool in s:
        calls += 1
    if '"tool/result"' in s:
        results += 1
print(f"   tool/call {tool}: {calls} - tool/result (any): {results}")
if calls >= 1 and results >= 1:
    print(f"dsh-smoke: OK - dsh called {tool} through overstack-mcp")
    sys.exit(0)
print(f"X dsh did not call {tool} (see {log})")
sys.exit(1)
PY
