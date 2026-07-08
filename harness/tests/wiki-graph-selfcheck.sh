#!/usr/bin/env bash
# wiki-graph-selfcheck — tự chẩn đoán đường AUTO-DRAW vector (wiki-graph.html) ở BẤT KỲ dự án nào.
#
# Portable: copy 1 file này vào dự án downstream rồi chạy  `bash wiki-graph-selfcheck.sh`.
# Nó dò 5 mắt xích của đường auto-draw, ÉP chạy generator để tách lỗi-engine vs lỗi-trigger,
# rồi TỰ in verdict (mắt xích ✗ đầu tiên + cách sửa) — không cần đọc cây quyết định bằng tay.
#
# Đường auto-draw (Stop hook → stop.regen_docs):
#   [A] engine reachable (repo-local → global ~/.claude/harness)
#   [B] wikigraph_on = engine AND (is_framework OR env OVERSTACK_WIKIGRAPH==1)
#   [C] Stop hook wired trong .claude/settings.json
#   [D] llmwiki/.harness-stamp (guard hook global fire)
#   [F] generator chạy → llmwiki/html/wiki-graph.html (scope theo .overstack.yaml)
set -u
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"; cd "$ROOT" || exit 2
GH="${OVERSTACK_HARNESS_HOME:-$HOME/.claude/harness}"
g(){ printf '  \033[1;32m✓\033[0m %s\n' "$1"; }
r(){ printf '  \033[1;31m✗\033[0m %s\n' "$1"; }
h(){ printf '\n\033[1m%s\033[0m\n' "$1"; }
verdict=""; setv(){ [ -z "$verdict" ] && verdict="$1"; }   # giữ mắt xích gãy ĐẦU TIÊN

echo "ROOT=$ROOT"
echo "GLOBAL=$GH"

h "[A] engine build-wiki-graph.py reachable?"
WG=""
if   [ -f fdk/tools/build-wiki-graph.py ];      then WG="fdk/tools/build-wiki-graph.py";      g "repo-local: $WG"
elif [ -f "$GH/fdk/tools/build-wiki-graph.py" ]; then WG="$GH/fdk/tools/build-wiki-graph.py"; g "global: $WG"
else r "KHÔNG thấy engine ở repo-local lẫn global"; setv "A"; fi

h "[B] opt-in downstream: is_framework HOẶC .harness-stamp HOẶC env OVERSTACK_WIKIGRAPH=1?"
# GH#70: enablement khoá vào .harness-stamp (cùng tín hiệu gate hook global), không còn env-only.
IS_FW=0; [ -f fdk/tools/build-overstack-docs.py ] && IS_FW=1 && g "repo FRAMEWORK → auto-on, không cần cờ"
FLAG="$(grep -h "OVERSTACK_WIKIGRAPH" .claude/settings.json "$HOME/.claude/settings.json" 2>/dev/null | grep -o '"[01]"' | head -1)"
if [ "$IS_FW" = 1 ]; then :
elif [ -f llmwiki/.harness-stamp ]; then g "llmwiki/.harness-stamp có → downstream auto-on (v4)"
elif echo "$FLAG" | grep -q '"1"'; then g "settings.json env OVERSTACK_WIKIGRAPH=1 (override)"
else r "không .harness-stamp, không env=1 → downstream return sớm, không vẽ (chạy install-harness ghi stamp)"; setv "B"; fi

h "[C] Stop hook wired?"
grep -q "stop.py" .claude/settings.json 2>/dev/null && g "Stop → stop.py có trong .claude/settings.json" \
  || { r ".claude/settings.json chưa wire Stop hook"; setv "C"; }

h "[D] .harness-stamp (guard hook global)?"
[ -f llmwiki/.harness-stamp ] && g "llmwiki/.harness-stamp có" \
  || { [ "$IS_FW" = 1 ] && g "repo framework — không cần stamp" || { r "thiếu stamp → hook global không fire"; setv "D"; }; }

h "[E] file kết quả + tuổi"
[ -f llmwiki/html/wiki-graph.html ] && ls -la llmwiki/html/wiki-graph.html || r "chưa có llmwiki/html/wiki-graph.html"

h "[F] ÉP chạy generator (tách lỗi-engine vs lỗi-trigger)"
NODES=0
if [ -n "$WG" ]; then
  also=(); [ -d fdk/wiki ] && also=(--also fdk/wiki)
  OUT="$(python3 "$WG" llmwiki/wiki ${also[@]+"${also[@]}"} --code-root . 2>&1 | tail -3)"; echo "$OUT"
  echo "$OUT" | grep -q "✓" && g "generator OK" || { r "generator LỖI (xem trên) — lỗi engine THẬT, không phải trigger"; setv "F"; }
  NODES="$(grep -c "nodes" llmwiki/html/wiki-graph.html 2>/dev/null || echo 0)"
  [ "$NODES" -gt 0 ] && g "HTML có data blob → vẽ được" || r "HTML thiếu data blob"
else
  r "bỏ qua — không có engine ([A] gãy)"
fi

# ---------- VERDICT ----------
h "════ VERDICT ════"
case "${verdict:-OK}" in
  A) echo "  ✗ ENGINE CHƯA CÀI. Sửa:"
     echo "     bash <repo-framework>/harness/scripts/install-harness.sh --global" ;;
  B) echo "  ✗ THIẾU OPT-IN — engine chạy được nhưng hook return sớm ở downstream. Sửa:"
     echo "     chạy install.sh --with-wiki (bootstrap.sh) — ghi llmwiki/.harness-stamp → auto-on (v4/GH#70)"
     echo "     (override tạm: \"env\": { \"OVERSTACK_WIKIGRAPH\": \"1\" } trong .claude/settings.json)" ;;
  C) echo "  ✗ STOP HOOK CHƯA WIRE — chạy install-harness.sh vào repo." ;;
  D) echo "  ✗ THIẾU .harness-stamp — chạy install-harness.sh (ghi stamp)." ;;
  F) echo "  ✗ LỖI ENGINE THẬT (không phải trigger). Dán output [F] + \`cat .overstack.yaml\` để soi scope." ;;
  OK)
     if [ "$NODES" -gt 0 ]; then
       echo "  ✓ ENGINE + CỜ ĐỦ — vector VẼ ĐƯỢC ($NODES data blob)."
       echo "    Nếu 'tự động' vẫn không chạy khi Stop: git-status KHÔNG có diff ở wiki/ hay file code"
       echo "    → hook (B) không có gì để regen (KHÔNG phải bug). Đổi 1 file wiki/code rồi Stop lại,"
       echo "    hoặc dùng chính lệnh [F] ở trên để vẽ ngay."
     else
       echo "  ⚠ đường thông nhưng HTML rỗng — kiểm .overstack.yaml (wiki_dir/code_root) + nội dung llmwiki/wiki."
     fi ;;
esac
[ "${verdict:-OK}" = "OK" ] && exit 0 || exit 1
