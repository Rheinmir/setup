#!/usr/bin/env bash
# wiki-graph-user-reachability-test — chặn AP-1 "dev-repo-only reachability trap" (GH#51 → v4 GH#63).
#
# v4 GLOBAL-SHARED (council-036/038, đảo GH#51): engine KHÔNG travel vào repo user nữa —
# nằm ở ~/.claude/harness (cài 1 lần), hook resolve qua hooklib.resolve_tool repo-local → global.
# Test từ góc USER-DEV (người CÀI framework vào dự án của họ), KHÔNG phải dev framework:
#   A) REACHABILITY (hermetic, không mạng): engine CÓ trong đường giao hàng GLOBAL —
#      install-harness.sh --global copy engine vào ~/.claude/harness; install.sh --with-wiki
#      đảm bảo global + ghi .harness-stamp + KHÔNG kéo engine vào repo (đảo GH#51).
#   B) FUNCTIONAL: mô phỏng dự án user SẠCH (0 engine in-repo) + global giả (OVERSTACK_HARNESS_HOME)
#      → hook stop.py resolve engine TỪ GLOBAL, tự regen wiki-graph, tôn trọng scope .overstack.yaml.
#      NEGATIVE-control: xóa engine global → graph KHÔNG sinh (chứng minh đường resolve là thật).
#
# Pass = thay đổi engine/hook/scope THẬT SỰ tới + fire ở dự án user qua GLOBAL (repo user sạch).
# Usage: bash harness/tests/wiki-graph-user-reachability-test.sh [repo-root]   (exit 0 pass, 1 fail)
set -u
ROOT="${1:-.}"; cd "$ROOT" || { echo "không vào được $ROOT"; exit 2; }
ROOT="$(pwd)"
pass=0; fail=0
ok(){  printf '  \033[1;32m✓\033[0m %s\n' "$1"; pass=$((pass+1)); }
bad(){ printf '  \033[1;31m✗\033[0m %s — %s\n' "$1" "$2"; fail=$((fail+1)); }
hdr(){ printf '\n\033[1m%s\033[0m\n' "$1"; }

hdr "A — REACHABILITY: engine nằm trong ĐƯỜNG GIAO HÀNG GLOBAL tới user"
IH="harness/scripts/install-harness.sh"
grep -q 'fdk/tools/"\*\.py.*\$GH/fdk/tools' "$IH" 2>/dev/null \
  && ok "install-harness --global ship engine fdk/tools → ~/.claude/harness" \
  || bad "install-harness --global không copy fdk/tools" "engine không tới global (AP-1 v4)"
grep -q 'harness/scripts/"\*\.py.*\$GH/harness/scripts' "$IH" 2>/dev/null \
  && ok "install-harness --global ship harness/scripts → ~/.claude/harness" \
  || bad "install-harness --global không copy harness/scripts" "tool nền không tới global"
grep -q 'version\.json.*\$GH/version\.json' "$IH" 2>/dev/null \
  && ok "install-harness --global ghi version.json (nguồn so-khớp stamp U11)" \
  || bad "global thiếu version.json" "session_start không so được skew"
grep -q 'llmwiki/\.harness-stamp" \]' "$IH" 2>/dev/null \
  && ok "hook global gate theo .harness-stamp (hợp đồng install, thay [ -d llmwiki ])" \
  || bad "guard settings chưa theo stamp" "repo chưa bootstrap vẫn bị hook fire / repo v4 không được gác"

IS="harness/poc-vendor-neutral/install.sh"
grep -q 'install-harness\.sh' "$IS" 2>/dev/null && grep -q -- '--global' "$IS" 2>/dev/null \
  && ok "install.sh --with-wiki tự cài global khi thiếu (install-harness --global)" \
  || bad "install.sh không ensure-global" "user curl xong vẫn không có engine (AP-1 v4)"
grep -q '\.harness-stamp' "$IS" 2>/dev/null \
  && ok "install.sh ghi llmwiki/.harness-stamp (guarded_by — travel theo git)" \
  || bad "install.sh không ghi stamp" "hook global không fire (guard stamp) + không so được skew"
grep -q 'template-manifest\.json' "$IS" 2>/dev/null \
  && bad "install.sh còn kéo engine từ manifest vào repo" "GH#51 chưa đảo — repo user vẫn phình engine" \
  || ok "install.sh KHÔNG kéo engine vào repo (đảo GH#51 — repo user sạch)"
grep -q 'rm -rf "\$ROOT/\${d:?}"' "$IS" 2>/dev/null \
  && ok "install.sh gỡ engine-in-repo đời cũ (fdk/tools, harness/scripts — U10)" \
  || bad "install.sh không dọn engine cũ" "repo cũ giữ 2 nguồn chân lý (skew ngầm)"
grep -q 'fdk/wiki' "$IS" 2>/dev/null \
  && ok "gỡ engine có guard fdk/wiki (không bao giờ dọn repo framework)" \
  || bad "thiếu guard repo framework" "chạy nhầm trong repo framework sẽ xóa engine nguồn"

hdr "C — SKILL→TOOL reachability (GH#54): skill-shipped trỏ .py nào thì .py đó phải ship"
# Bẫy AP-1 lớp 2: skill SHIP xuống user (llmwiki/skills/**) hướng dẫn chạy harness/scripts/X.py
# hoặc fdk/tools/X.py. v4: tool đến user qua GLOBAL (install-harness --global copy fdk/tools +
# harness/scripts nguyên cây) — assert tool được skill tham chiếu TỒN TẠI trong cây nguồn đó
# (nguồn của bản global), không phải trong manifest per-repo như GH#51.
MAN=".template-manifest.json"
python3 - "$MAN" <<'PY'
import json, re, sys, os
man = sys.argv[1]
inc = set(json.load(open(man)).get("includes", []))
skills = [f for f in inc if f.startswith("llmwiki/skills/") and f.endswith(".md")]
# CHỈ bắt dạng LỆNH CHẠY `python3 …X.py` (user/agent thật sự gọi) — bỏ qua nhắc-tên mô tả.
REF = re.compile(r"python3\s+(harness/scripts/[\w./-]+\.py|fdk/tools/[\w./-]+\.py)")
bad = 0
for s in skills:
    if not os.path.isfile(s):
        continue
    for ref in sorted(set(REF.findall(open(s, encoding="utf-8", errors="ignore").read()))):
        # v4: nguồn giao hàng = cây repo framework (install-harness --global copy nguyên thư mục)
        if os.path.isfile(ref):
            print("  \033[1;32m✓\033[0m %s → %s (có trong cây global-ship)" % (os.path.basename(s), ref))
        else:
            print("  \033[1;31m✗\033[0m %s trỏ %s — KHÔNG tồn tại (AP-1: user gọi skill sẽ lỗi)" % (os.path.basename(s), ref))
            bad += 1
if bad == 0:
    print("  \033[1;32m✓\033[0m mọi tool .py mà skill-shipped tham chiếu đều nằm trong cây global-ship")
sys.exit(1 if bad else 0)
PY
if [ $? -eq 0 ]; then pass=$((pass+1)); else fail=$((fail+1)); fi

hdr "B — FUNCTIONAL: dự án USER SẠCH + global giả → hook resolve engine từ GLOBAL"
FX="$(mktemp -d)"; trap 'rm -rf "$FX"' EXIT
FXHOME="$FX/fake-harness-home"          # global giả — KHÔNG đụng ~/.claude thật
FXREPO="$FX/user-repo"
mkdir -p "$FXREPO/pkg" "$FXREPO/tests" "$FXREPO/llmwiki/wiki/concepts" "$FXREPO/llmwiki/html" \
         "$FXHOME/fdk/tools" "$FXHOME/hooks"
# code user: pkg/ trong scope, tests/ NGOÀI scope
printf 'def a(): return 1\n' > "$FXREPO/pkg/a.py"
printf 'from a import a\ndef b(): return a()\n' > "$FXREPO/pkg/b.py"
printf 'from a import a\n' > "$FXREPO/tests/test_a.py"
printf -- '---\ntype: concept\ntitle: X\nstatus: shipped\ntags: [t]\ntimestamp: 2026-07-05\nid: x\n---\n# X\n## Origin\ns\n' > "$FXREPO/llmwiki/wiki/concepts/x.md"
printf '# i\n' > "$FXREPO/llmwiki/wiki/index.md"; printf '# l\n' > "$FXREPO/llmwiki/wiki/log.md"
printf 'wiki_dir: llmwiki/wiki\ncode_root: pkg\n' > "$FXREPO/.overstack.yaml"
printf '{"schema": 1, "guarded_by": "test"}\n' > "$FXREPO/llmwiki/.harness-stamp"
# mô phỏng install-harness --global: engine + hooks vào GLOBAL giả (repo user KHÔNG có bản nào)
cp fdk/tools/build-wiki-graph.py fdk/tools/code_imports.py "$FXHOME/fdk/tools/" 2>/dev/null
cp llmwiki/.claude/hooks/*.py "$FXHOME/hooks/" 2>/dev/null
( cd "$FXREPO" && git init -q && git add -A 2>/dev/null )
# repo user phải SẠCH: 0 engine in-repo (điều kiện v4)
{ [ ! -d "$FXREPO/fdk" ] && [ ! -d "$FXREPO/harness" ]; } \
  && ok "repo user sạch (0 fdk/ 0 harness/ — engine chỉ ở global)" \
  || bad "fixture bẩn" "repo user còn engine in-repo, test không chứng minh được global-path"
# gọi regen_docs như hook Stop thật (chạy từ bản hooks GLOBAL, opt-in downstream)
OVERSTACK_WIKIGRAPH=1 OVERSTACK_HARNESS_HOME="$FXHOME" python3 - "$FXREPO" "$FXHOME" <<'PY'
import sys, os
fxrepo, fxhome = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(fxhome, "hooks"))   # hook chạy từ bản GLOBAL, không phải repo
import stop
stop.regen_docs(fxrepo)
PY
G="$FXREPO/llmwiki/html/wiki-graph.html"
[ -f "$G" ] && ok "hook (bản global) tự sinh wiki-graph.html ở dự án user — engine resolve từ GLOBAL" \
           || bad "graph không sinh" "resolve_tool không tìm thấy engine global (đường v4 đứt)"
if [ -f "$G" ]; then
  grep -q 'a\.py' "$G" && grep -q 'b\.py' "$G" \
    && ok "graph có node code trong scope (pkg/a.py, pkg/b.py)" \
    || bad "thiếu node code" "engine không index code user"
  grep -q 'tests/' "$G" \
    && bad "scope sai" "kéo tests/ dù .overstack.yaml code_root=pkg" \
    || ok "tôn trọng scope .overstack.yaml (bỏ tests/ ngoài code_root)"
fi
# NEGATIVE-control: xóa engine global → graph KHÔNG sinh (chứng minh graph ở trên đến từ global thật)
rm -f "$G" "$FXHOME/fdk/tools/build-wiki-graph.py"
OVERSTACK_WIKIGRAPH=1 OVERSTACK_HARNESS_HOME="$FXHOME" python3 - "$FXREPO" "$FXHOME" <<'PY'
import sys, os, importlib
fxrepo, fxhome = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(fxhome, "hooks"))
import stop
stop.regen_docs(fxrepo)
PY
[ -f "$G" ] && bad "NEGATIVE-control fail" "xóa engine global mà graph vẫn sinh — test không đo đường global" \
            || ok "NEGATIVE-control: xóa engine global → graph không sinh (đường resolve là thật)"

printf '\n\033[1m%d pass · %d fail\033[0m\n' "$pass" "$fail"
[ "$fail" -eq 0 ] || exit 1
