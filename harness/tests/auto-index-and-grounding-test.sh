#!/usr/bin/env bash
# auto-index-and-grounding-test — verify 2 cơ chế (goal-set 2026-06-28):
#   (1) AUTO-INDEX khi wiki thay đổi: Stop hook tự chạy index_sync --fix → file wiki mới
#       tự vào index.md, không bắt agent sửa tay.
#   (2) FORCE-QUERY khi propose: R7 (proposal_complete) chặn draft thiếu '## Context' có nội dung
#       → ép query wiki liên quan trước khi propose.
#
# Usage: bash harness/tests/auto-index-and-grounding-test.sh [repo-root]   (exit 0 = pass)
set -u
ROOT="${1:-.}"; cd "$ROOT" || { echo "không vào được $ROOT"; exit 2; }
pass=0; fail=0
ok(){  printf '  \033[1;32m✓\033[0m %s\n' "$1"; pass=$((pass+1)); }
bad(){ printf '  \033[1;31m✗\033[0m %s — %s\n' "$1" "$2"; fail=$((fail+1)); }
hdr(){ printf '\n\033[1m%s\033[0m\n' "$1"; }
IDX=harness/validators/index_sync.py
R7=harness/validators/proposal_complete.py

hdr "(1) AUTO-INDEX khi wiki thay đổi"
grep -qE 'index_sync\.py".*--fix|--fix' llmwiki/.claude/hooks/stop.py \
  && ok "Stop hook wire index_sync --fix (auto-heal)" \
  || bad "stop.py" "không wire --fix → không auto-index"
# functional: file wiki MỚI chưa có trong index → --fix tự thêm
FX="$(mktemp -d)"; mkdir -p "$FX/wiki/concepts"
printf '# Wiki Index\n\n| File | Type | Summary |\n|---|---|---|\n' > "$FX/wiki/index.md"
printf -- '---\ntype: concept\n---\n# Khai niem moi\n## Origin\n- test\n' > "$FX/wiki/concepts/khai-niem-moi.md"
python3 "$IDX" --wiki-dir "$FX/wiki" --fix >/dev/null 2>&1
grep -q 'khai-niem-moi' "$FX/wiki/index.md" \
  && ok "file wiki mới TỰ vào index.md sau --fix" \
  || bad "auto-index" "index.md không tự thêm file mới"
rm -rf "$FX"

hdr "(2) FORCE-QUERY khi propose (R7-f chặn draft thiếu ## Context)"
FX2="$(mktemp -d)"; mkdir -p "$FX2/wiki/sources/draft"
# draft proposed CÓ Plan nhưng THIẾU ## Context → R7 phải flag (f)
NOC="$FX2/wiki/sources/draft/280626-test-no-context.md"
printf -- '---\ntype: draft\n---\n# Test\n**Status:** proposed\n## Plan\n- [ ] task 1\n' > "$NOC"
python3 "$R7" "$NOC" 2>&1 | grep -q '(f)' \
  && ok "R7 CHẶN draft thiếu ## Context (force-query)" \
  || bad "R7-f" "không chặn draft thiếu Context"
# draft CÓ ## Context (>=20 ký tự) → R7 KHÔNG còn flag (f)
WC="$FX2/wiki/sources/draft/280626-test-with-context.md"
printf -- '---\ntype: draft\n---\n# Test\n**Status:** proposed\n## Context\nĐã query wiki: liên quan [[rule-registry]] và ADR-008 về the kit.\n## Plan\n- [ ] task 1\n' > "$WC"
python3 "$R7" "$WC" 2>&1 | grep -q '(f)' \
  && bad "R7-f" "vẫn flag dù đã có ## Context" \
  || ok "R7 KHÔNG flag (f) khi draft có ## Context grounded"
rm -rf "$FX2"

printf '\n\033[1m═══ TỔNG: %d test — \033[1;32m%d PASS\033[0m / \033[1;31m%d FAIL\033[0m\033[0m\n' "$((pass+fail))" "$pass" "$fail"
[ "$fail" -eq 0 ]
