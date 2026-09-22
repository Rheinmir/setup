#!/usr/bin/env bash
# html-font-lint-test — luật "mọi HTML framework sinh ra = Be Vietnam Pro, NHÚNG" được GÁC, không dựa vào nhớ.
#   (1) trang do GENERATOR của framework sinh (đang track) đều đạt        (2) engine orca-graph qua shim: graph + atlas đạt
#   (3) bản sao html_font ở repo engine khớp nguồn framework (--parity)   (4) template skill khai đúng font / skeleton đã nhúng
#   (5) ÂM TÍNH: trang thiếu font → rc 2 + chỉ lệnh sửa; --apply sửa được và idempotent
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
LINT="python3 fdk/tools/html-font-lint.py"; T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export ORCA_GRAPH_NO_DAEMON=1 ORCA_GRAPH_NO_ROOM=1 ORCA_GRAPH_HOME="$T/og-home"
PASS=0; FAIL=0; SKIP=0; ok(){ PASS=$((PASS+1)); echo "  PASS  $*"; }; no(){ FAIL=$((FAIL+1)); echo "  FAIL  $*"; }
# SKIP đếm RIÊNG, và trên CI (runner đã cài engine ở step trước) SKIP = FAIL — không để "không chạy gì" trông như xanh
sk(){ if [ -n "${CI:-}" ]; then no "$* (SKIP trên CI = FAIL)"; else SKIP=$((SKIP+1)); echo "  SKIP  $*"; fi; }

# overstack.html là trang DUY NHẤT trong llmwiki/html được track; các trang khác gitignored → runner sạch không có sẵn: tự sinh rồi mới soi.
python3 fdk/tools/build-docs-index.py >/dev/null 2>&1 || true
GEN="llmwiki/html/overstack.html"; [ -f llmwiki/html/index.html ] && GEN="$GEN llmwiki/html/index.html"
# shellcheck disable=SC2086
if $LINT $GEN >"$T/1.log" 2>&1; then ok "(1) trang do generator sinh: $(tail -1 "$T/1.log")"; else no "(1) $(grep '✗' "$T/1.log" | head -3)"; fi

if python3 harness/scripts/orca-graph.py --version >/dev/null 2>&1; then
  printf '# f\n\n### Task 1: A\n**Files:**\n- Tạo: `a`\n**Verify:** `true`\n' > "$T/PLAN.md"
  python3 harness/scripts/orca-graph.py --dir "$T/g" build "$T/PLAN.md" --id f >/dev/null 2>&1
  python3 fdk/tools/graph-viz.py "$T/g/f.graph.json" >/dev/null 2>&1; python3 fdk/tools/graph-atlas.py "$T/g" >/dev/null 2>&1
  python3 fdk/tools/build-control-room.py --dirs "$T/g" -o "$T/cr/control-room.html" >/dev/null 2>&1     # cockpit của framework dựng trên engine
  if $LINT "$T/g/f.graph.html" "$T/g/atlas.html" "$T/cr" >"$T/2.log" 2>&1; then ok "(2) engine qua shim: graph + atlas + control-room: $(tail -1 "$T/2.log")"; else no "(2) $(grep '✗' "$T/2.log" | head -2)"; fi
  $LINT --parity >"$T/3.log" 2>&1; prc=$?
  case $prc in 0) ok "(3) $(tail -1 "$T/3.log")";; 4) sk "(3) $(tail -1 "$T/3.log")";; *) no "(3) $(tail -1 "$T/3.log")";; esac
else sk "(2)(3) chưa cài engine orca-graph"; fi

{ grep -q "'Be Vietnam Pro'" skills/docs-site-macos/SKILL.md && grep -q "html_font.py --apply" skills/docs-site-macos/SKILL.md \
  && $LINT skills/orca-onboard/assets/docs-site-skeleton.html >/dev/null 2>&1; } && ok "(4) template docs-site-macos khai font + bước --apply; skeleton orca-onboard đã nhúng" || no "(4) template skill"

printf '<html><head><style>body{font-family:-apple-system,sans-serif}</style></head><body>Đường dẫn</body></html>' > "$T/bad.html"
$LINT "$T/bad.html" >"$T/5.log" 2>&1; rc=$?
{ [ $rc = 2 ] && grep -q -- "--apply" "$T/5.log"; } && ok "(5a) trang thiếu font → rc 2 + chỉ lệnh sửa" || no "(5a) rc=$rc"
python3 fdk/tools/html_font.py --apply "$T/bad.html" >/dev/null; S1=$(wc -c < "$T/bad.html"); python3 fdk/tools/html_font.py --apply "$T/bad.html" >/dev/null; S2=$(wc -c < "$T/bad.html")
{ $LINT "$T/bad.html" >/dev/null 2>&1 && [ "$S1" = "$S2" ] && grep -q "font-family:var(--font-text)" "$T/bad.html"; } && ok "(5b) --apply sửa được, idempotent, stack hệ thống chép tay được trỏ về token" || no "(5b) apply"

echo ""; echo "html-font-lint-test: $PASS PASS · $FAIL FAIL · $SKIP SKIP"; [ "$FAIL" = 0 ]
