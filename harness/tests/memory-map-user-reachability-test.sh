#!/usr/bin/env bash
# memory-map-user-reachability-test — chặn AP-1 "dev-repo-only reachability trap" cho BỘ NHỚ THỨ CẤP.
#
# Song sinh của wiki-graph-user-reachability-test: memory-map (session→file + why) phải TỰ CHẠY ở
# dự án user MẶC ĐỊNH (không setting tay), ĐỐI XỨNG wiki-graph. Trước đây secondary_memory kiểm
# scratch-log.py REPO-LOCAL (no fallback) + không gate stamp → chỉ chạy ở repo framework, project
# khách cài về im lặng. Nay: engine resolve repo-local → GLOBAL ~/.claude/harness; bật theo
# llmwiki/.harness-stamp (cùng tín hiệu đã bật hook); cwd=root nên engine global ghi ĐÚNG project.
#
# Test từ góc USER-DEV (người CÀI framework vào dự án họ), repo user SẠCH (0 engine in-repo):
#   A) REACHABILITY (hermetic): engine (scratch-log + memory-map) ở cây global-ship; hook gate stamp.
#   B) FUNCTIONAL: dự án user sạch + global giả → secondary_memory resolve engine TỪ GLOBAL, tự sinh
#      memory-map.html VÀO project (không phải thư mục global). 3 negative-control:
#      STAMP (không stamp → không vẽ) · ENGINE (xóa engine global → không vẽ) · ISOLATION (global sạch).
#
# Pass = memory-map fire ở dự án user qua GLOBAL, gated stamp, ghi đúng project. exit 0 pass / 1 fail.
set -u
ROOT="${1:-.}"; cd "$ROOT" || { echo "không vào được $ROOT"; exit 2; }
ROOT="$(pwd)"
pass=0; fail=0
ok(){  printf '  \033[1;32m✓\033[0m %s\n' "$1"; pass=$((pass+1)); }
bad(){ printf '  \033[1;31m✗\033[0m %s — %s\n' "$1" "$2"; fail=$((fail+1)); }
hdr(){ printf '\n\033[1m%s\033[0m\n' "$1"; }

hdr "A — REACHABILITY: engine memory-map ở ĐƯỜNG GIAO HÀNG GLOBAL + hook gate stamp"
IH="harness/scripts/install-harness.sh"
grep -q 'harness/scripts/"\*\.py.*\$GH/harness/scripts' "$IH" 2>/dev/null \
  && ok "install-harness --global ship harness/scripts (scratch-log.py) → ~/.claude/harness" \
  || bad "scratch-log.py không tới global" "secondary_memory downstream không có engine (AP-1)"
grep -q 'fdk/tools/"\*\.py.*\$GH/fdk/tools' "$IH" 2>/dev/null \
  && ok "install-harness --global ship fdk/tools (memory-map.py) → ~/.claude/harness" \
  || bad "memory-map.py không tới global" "view bộ-nhớ-thứ-cấp không sinh được downstream"
[ -f "harness/scripts/scratch-log.py" ] && [ -f "fdk/tools/memory-map.py" ] \
  && ok "engine tồn tại trong cây nguồn global-ship (scratch-log + memory-map)" \
  || bad "thiếu engine nguồn" "install-harness copy rỗng → downstream không có gì để chạy"
SP="llmwiki/.claude/hooks/stop.py"
grep -q 'resolve_tool(root, "harness/scripts/scratch-log.py")' "$SP" 2>/dev/null \
  && ok "secondary_memory resolve scratch-log qua resolve_tool (repo-local → GLOBAL)" \
  || bad "secondary_memory còn kiểm repo-local" "downstream sạch không có scratch-log in-repo → im lặng (bug cũ)"
grep -q 'resolve_tool(root, "fdk/tools/memory-map.py")' "$SP" 2>/dev/null \
  && ok "secondary_memory resolve memory-map qua resolve_tool (repo-local → GLOBAL)" \
  || bad "memory-map còn kiểm repo-local" "downstream không vẽ được view"
grep -q 'has_stamp or os.environ.get("OVERSTACK_WIKIGRAPH")' "$SP" 2>/dev/null \
  && ok "secondary_memory gate is_framework|has_stamp|env (đối xứng wiki-graph)" \
  || bad "secondary_memory thiếu gate stamp" "không bật downstream / bật lung tung repo bất kỳ"

hdr "B — FUNCTIONAL: dự án USER SẠCH + global giả → secondary_memory resolve từ GLOBAL"
FX="$(mktemp -d)"; trap 'rm -rf "$FX"' EXIT
FXHOME="$FX/fake-harness-home"          # global giả — KHÔNG đụng ~/.claude thật
FXREPO="$FX/user-repo"
mkdir -p "$FXREPO/pkg" "$FXREPO/llmwiki/wiki/concepts" "$FXREPO/llmwiki/html" "$FXREPO/harness/metrics" \
         "$FXHOME/fdk/tools" "$FXHOME/harness/scripts" "$FXHOME/hooks"
printf 'def a(): return 1\n' > "$FXREPO/pkg/a.py"
printf -- '---\ntype: concept\ntitle: X\nstatus: shipped\ntags: [t]\ntimestamp: 2026-07-05\nid: x\n---\n# X\n## Origin\ns\n' > "$FXREPO/llmwiki/wiki/concepts/x.md"
printf '# i\n' > "$FXREPO/llmwiki/wiki/index.md"; printf '# l\n' > "$FXREPO/llmwiki/wiki/log.md"
printf '{"ts":"2026-07-12T10:00:00","session":"sess1234","target":"pkg/a.py","action":"add"}\n' > "$FXREPO/llmwiki/wiki/ledger.jsonl"
printf '{"schema": 1, "guarded_by": "test"}\n' > "$FXREPO/llmwiki/.harness-stamp"
# mô phỏng install-harness --global: engine vào GLOBAL giả (repo user KHÔNG có bản nào)
cp fdk/tools/memory-map.py fdk/tools/build-wiki-graph.py fdk/tools/code_imports.py "$FXHOME/fdk/tools/" 2>/dev/null
cp harness/scripts/scratch-log.py "$FXHOME/harness/scripts/"
cp llmwiki/.claude/hooks/*.py "$FXHOME/hooks/" 2>/dev/null
( cd "$FXREPO" && git init -q && printf 'x\n' > pkg/a.py && git add -A 2>/dev/null )   # git dirty (có mutation)
{ [ ! -d "$FXREPO/fdk" ] && [ ! -d "$FXREPO/harness/scripts" ]; } \
  && ok "repo user sạch (0 engine in-repo — chỉ ở global)" \
  || bad "fixture bẩn" "repo user còn engine in-repo, không chứng minh được global-path"

run_hook(){ OVERSTACK_HARNESS_HOME="$FXHOME" python3 - "$FXREPO" "$FXHOME" <<'PY'
import sys, os
fxrepo, fxhome = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(fxhome, "hooks"))   # hook chạy từ bản GLOBAL, không phải repo
import stop
stop.secondary_memory(fxrepo, "sess1234")
PY
}

M="$FXREPO/llmwiki/html/memory-map.html"
run_hook
[ -f "$M" ] && ok "secondary_memory (bản global) tự sinh memory-map.html ở dự án user — resolve từ GLOBAL" \
           || bad "memory-map không sinh" "resolve_tool không tìm engine global (đường downstream đứt)"
if [ -f "$M" ]; then
  grep -q 'sess1234' "$M" && ok "memory-map có node session (sess1234) từ ledger dự án user" \
                          || bad "thiếu node session" "engine không đọc data project"
fi
# ISOLATION: data + html ghi vào PROJECT, KHÔNG rò vào global giả
[ -f "$FXREPO/harness/metrics/scratch-log.jsonl" ] \
  && ok "scratch-log auto ghi LOG vào PROJECT (harness/metrics/) — cwd=root đúng" \
  || bad "LOG không vào project" "repo_root không ưu tiên cwd → ghi nhầm global"
{ [ ! -e "$FXHOME/llmwiki" ] && [ ! -e "$FXHOME/harness/metrics" ]; } \
  && ok "ISOLATION: global giả KHÔNG bị ghi data/html (engine global chỉ đọc/ghi project)" \
  || bad "rò vào global" "engine ghi nhầm vào thư mục engine thay vì project downstream"

# STAMP negative-control: repo KHÔNG stamp + KHÔNG env → KHÔNG vẽ (giữ opt-in downstream)
rm -f "$M"; mv "$FXREPO/llmwiki/.harness-stamp" "$FXREPO/llmwiki/.harness-stamp.off"
run_hook
[ -f "$M" ] && bad "STAMP-control fail" "repo không stamp mà vẫn vẽ — opt-in bị bỏ qua" \
            || ok "STAMP-control: không .harness-stamp + không env → không vẽ (opt-in giữ nguyên)"
mv "$FXREPO/llmwiki/.harness-stamp.off" "$FXREPO/llmwiki/.harness-stamp"
# ENGINE negative-control: xóa engine global → KHÔNG vẽ (chứng minh graph ở trên đến từ global thật)
rm -f "$M" "$FXHOME/harness/scripts/scratch-log.py"
run_hook
[ -f "$M" ] && bad "ENGINE-control fail" "xóa scratch-log global mà vẫn vẽ — test không đo đường global" \
            || ok "ENGINE-control: xóa engine global → không vẽ (đường resolve là thật)"

printf '\n\033[1m%d pass · %d fail\033[0m\n' "$pass" "$fail"
[ "$fail" -eq 0 ] || exit 1
