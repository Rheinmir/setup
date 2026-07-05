#!/usr/bin/env bash
# wiki-graph-user-reachability-test — chặn AP-1 "dev-repo-only reachability trap" (GH#51).
#
# Test từ góc USER-DEV (người CÀI framework vào dự án của họ), KHÔNG phải dev framework:
#   A) REACHABILITY (hermetic, không mạng): engine + hook wiki-graph CÓ trong đường giao hàng —
#      .template-manifest.json (sync-template) VÀ install.sh --with-wiki (bootstrap one-liner).
#   B) FUNCTIONAL: mô phỏng dự án user vừa cài (copy engine+hook từ repo, wire ROOT .claude/settings.json
#      như install.sh làm) → hook stop.py TỰ regen wiki-graph, tôn trọng scope .overstack.yaml.
#
# Pass = thay đổi engine/hook/scope THẬT SỰ tới + fire ở dự án user (không chỉ chạy trong repo framework).
# Usage: bash harness/tests/wiki-graph-user-reachability-test.sh [repo-root]   (exit 0 pass, 1 fail)
set -u
ROOT="${1:-.}"; cd "$ROOT" || { echo "không vào được $ROOT"; exit 2; }
ROOT="$(pwd)"
pass=0; fail=0
ok(){  printf '  \033[1;32m✓\033[0m %s\n' "$1"; pass=$((pass+1)); }
bad(){ printf '  \033[1;31m✗\033[0m %s — %s\n' "$1" "$2"; fail=$((fail+1)); }
hdr(){ printf '\n\033[1m%s\033[0m\n' "$1"; }

hdr "A — REACHABILITY: engine + hook nằm trong ĐƯỜNG GIAO HÀNG tới user"
MAN=".template-manifest.json"
for f in fdk/tools/build-wiki-graph.py fdk/tools/code_imports.py llmwiki/.claude/hooks/stop.py; do
  grep -q "\"$f\"" "$MAN" 2>/dev/null \
    && ok "manifest ship: $f" \
    || bad "manifest thiếu $f" "sync-template không kéo → user không có (AP-1)"
done
IS="harness/poc-vendor-neutral/install.sh"
grep -q 'template-manifest.json' "$IS" 2>/dev/null \
  && ok "install.sh --with-wiki kéo file-list từ manifest (bootstrap cũng ship engine)" \
  || bad "install.sh không đọc manifest" "bootstrap one-liner không ship engine (AP-1 tái diễn)"
grep -q 'llmwiki/.claude/hooks/%s.py\|llmwiki/.claude/hooks/' "$IS" 2>/dev/null \
  && ok "install.sh wire llmwiki hooks vào ROOT .claude/settings.json" \
  || bad "install.sh không wire root settings" "hook tới nơi nhưng không fire (Claude đọc root)"

hdr "B — FUNCTIONAL: dự án USER vừa cài → hook tự regen wiki-graph, tôn trọng scope"
FX="$(mktemp -d)"; trap 'rm -rf "$FX"' EXIT
mkdir -p "$FX/pkg" "$FX/tests" "$FX/llmwiki/wiki/concepts" "$FX/llmwiki/html" "$FX/.claude" "$FX/fdk/tools" "$FX/llmwiki/.claude"
# code user: pkg/ trong scope, tests/ NGOÀI scope
printf 'def a(): return 1\n' > "$FX/pkg/a.py"
printf 'from a import a\ndef b(): return a()\n' > "$FX/pkg/b.py"
printf 'from a import a\n' > "$FX/tests/test_a.py"
printf -- '---\ntype: concept\ntitle: X\nstatus: shipped\ntags: [t]\ntimestamp: 2026-07-05\nid: x\n---\n# X\n## Origin\ns\n' > "$FX/llmwiki/wiki/concepts/x.md"
printf '# i\n' > "$FX/llmwiki/wiki/index.md"; printf '# l\n' > "$FX/llmwiki/wiki/log.md"
printf 'wiki_dir: llmwiki/wiki\ncode_root: pkg\n' > "$FX/.overstack.yaml"
# mô phỏng install: copy engine + hooks TỪ repo (đúng thứ install.sh kéo)
cp fdk/tools/build-wiki-graph.py fdk/tools/code_imports.py "$FX/fdk/tools/" 2>/dev/null
cp -R llmwiki/.claude/hooks "$FX/llmwiki/.claude/" 2>/dev/null
# ROOT settings wire stop.py (đúng thứ install.sh --with-wiki tạo)
cat > "$FX/.claude/settings.json" <<JSON
{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"if [ -f \"\$CLAUDE_PROJECT_DIR/llmwiki/.claude/hooks/stop.py\" ]; then python3 \"\$CLAUDE_PROJECT_DIR/llmwiki/.claude/hooks/stop.py\"; fi"}]}]}}
JSON
( cd "$FX" && git init -q && git add -A 2>/dev/null )
# gọi regen_docs như hook Stop thật (opt-in downstream)
OVERSTACK_WIKIGRAPH=1 python3 - "$FX" <<'PY'
import sys, os
fx = sys.argv[1]
sys.path.insert(0, os.path.join(fx, "llmwiki", ".claude", "hooks"))
import stop
stop.regen_docs(fx)
PY
G="$FX/llmwiki/html/wiki-graph.html"
[ -f "$G" ] && ok "hook tự sinh wiki-graph.html ở dự án user" || bad "graph không sinh" "hook không fire downstream"
if [ -f "$G" ]; then
  grep -q 'a\.py' "$G" && grep -q 'b\.py' "$G" \
    && ok "graph có node code trong scope (pkg/a.py, pkg/b.py)" \
    || bad "thiếu node code" "engine không index code user"
  grep -q 'tests/' "$G" \
    && bad "scope sai" "kéo tests/ dù .overstack.yaml code_root=pkg" \
    || ok "tôn trọng scope .overstack.yaml (bỏ tests/ ngoài code_root)"
fi

printf '\n\033[1m%d pass · %d fail\033[0m\n' "$pass" "$fail"
[ "$fail" -eq 0 ] || exit 1
