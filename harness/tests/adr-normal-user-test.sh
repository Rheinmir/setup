#!/usr/bin/env bash
# adr-normal-user-test — ADR là first-class trong khuôn wiki PER-PROJECT (pattern thông thường của user).
#
# Trả lời câu hỏi "ADR có work với pattern thông thường của user chưa": verify cả hai mặt —
#   A) GAP đã đóng: skeleton mặc định (installer + demo) GỒM sources/adr/ + scaffolding.
#   B) FUNCTIONAL: một ADR do user thường viết (sources/adr/ADR-NNN.md, type: decision)
#      pass R5 folder-structure + R9 OKF + R2 Origin + R3 index-sync.
#
# Usage: bash harness/tests/adr-normal-user-test.sh [repo-root]   (exit 0 = pass, 1 = fail)
set -u
ROOT="${1:-.}"; cd "$ROOT" || { echo "không vào được $ROOT"; exit 2; }
pass=0; fail=0
ok(){  printf '  \033[1;32m✓\033[0m %s\n' "$1"; pass=$((pass+1)); }
bad(){ printf '  \033[1;31m✗\033[0m %s — %s\n' "$1" "$2"; fail=$((fail+1)); }
hdr(){ printf '\n\033[1m%s\033[0m\n' "$1"; }

hdr "A — sources/adr/ là first-class trong khuôn mặc định (gap đã đóng)"
grep -qE 'sources/adr' harness/scripts/install-harness.sh \
  && ok "installer tạo sẵn sources/adr/ trong skeleton" \
  || bad "installer skeleton" "thiếu sources/adr/ (gap chưa đóng)"
[ -d llmwiki/wiki/sources/adr ] \
  && ok "demo per-project có sources/adr/" \
  || bad "demo skeleton" "thiếu llmwiki/wiki/sources/adr/"
[ -f llmwiki/wiki/sources/adr/_template.md ] && [ -f llmwiki/wiki/sources/adr/README.md ] \
  && ok "có scaffolding _template.md + README.md" \
  || bad "scaffolding" "thiếu _template.md/README.md"

hdr "B — ADR do user THƯỜNG viết pass mọi validator (functional)"
FX="$(mktemp -d)"
mkdir -p "$FX/wiki/sources/adr"
printf '# Wiki Index\n\n| File | Type | Summary |\n|---|---|---|\n| [ADR-001-vi-du](sources/adr/ADR-001-vi-du.md) | decision | quyết định ví dụ của user |\n' > "$FX/wiki/index.md"
printf -- '---\ntype: decision\n---\n# ADR-001 ví dụ\n## Status\nAccepted\n## Context\nbối cảnh\n## Decision\nchọn X\n## Consequences\n- (+) tốt\n## Origin\n- **Source:** user\n' > "$FX/wiki/sources/adr/ADR-001-vi-du.md"
A="$FX/wiki/sources/adr/ADR-001-vi-du.md"
python3 harness/validators/folder_structure.py "$A" >/dev/null 2>&1 && ok "R5 folder-structure (sources/adr hợp lệ)" || bad "R5" "sources/adr bị từ chối"
python3 harness/validators/okf_frontmatter.py "$A"  >/dev/null 2>&1 && ok "R9 OKF (type: decision)"             || bad "R9" "OKF frontmatter fail"
python3 harness/validators/origin_required.py "$A"  >/dev/null 2>&1 && ok "R2 Origin"                            || bad "R2" "Origin fail"
python3 harness/validators/index_sync.py --wiki-dir "$FX/wiki" >/dev/null 2>&1 && ok "R3 index-sync (ADR khớp index)" || bad "R3" "index lệch"
rm -rf "$FX"

printf '\n\033[1m═══ TỔNG: %d test — \033[1;32m%d PASS\033[0m / \033[1;31m%d FAIL\033[0m\033[0m\n' "$((pass+fail))" "$pass" "$fail"
[ "$fail" -eq 0 ]
