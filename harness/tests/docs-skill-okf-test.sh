#!/usr/bin/env bash
# Chặn hồi quy: skill TẠO wiki .md phải hướng/xuất chuẩn OKF v0.1 (R9).
# Skill xuất HTML (md-to-html, docs-site-macos) → KHÔNG áp OKF (N/A).
set -uo pipefail

SRC="${1:?usage: docs-skill-okf-test.sh <repo-root>}"
cd "$SRC"
OKF="harness/scripts/okf-check.py"
SK="llmwiki/skills"
PASS=0; FAIL=0; N=0
ok()  { N=$((N+1)); PASS=$((PASS+1)); printf '  \033[1;32mPASS\033[0m  %s\n' "$1"; }
bad() { N=$((N+1)); FAIL=$((FAIL+1)); printf '  \033[1;31mFAIL\033[0m  %s — %s\n' "$1" "$2"; }
hdr() { printf '\n\033[1m── %s\033[0m\n' "$1"; }

# Skill sinh wiki .md → BẮT BUỘC nhắc OKF/_template/R9 trong prose
WIKI_SKILLS=(
  "wiki-loop/ingest" "dev-loop/propose" "wiki-loop/query"
  "dev-loop/onboard-codebase" "dev-loop/new-project-setup"
)
# Skill xuất HTML → N/A
HTML_SKILLS=( "utils/md-to-html" "utils/docs-site-macos" )

hdr "A — skill tạo wiki .md phải nhắc OKF (R9)"
for s in "${WIKI_SKILLS[@]}"; do
  f="$SK/$s.md"
  if [ ! -f "$f" ]; then bad "$s" "không tìm thấy file"; continue; fi
  if grep -qiE 'OKF|_template\.md|R9|frontmatter.*type|type.*không rỗng|non-empty .?type' "$f"; then
    ok "$s nhắc OKF/_template/R9"
  else
    bad "$s" "KHÔNG nhắc OKF — skill này sẽ sinh nợ R9"
  fi
done

hdr "B — orca-onboard heredoc xuất YAML frontmatter (KHÔNG còn bold **Type:**)"
OB="$SK/orchestrate/orca-onboard.md"
# (b1) heredoc draft KHÔNG còn dòng '**Type:**' bold
if grep -qE '^\*\*Type:\*\*' "$OB"; then
  bad "orca-onboard bold" "vẫn còn '**Type:**' bold trong skill"
else
  ok "orca-onboard không còn '**Type:**' bold"
fi
# (b2) render khối frontmatter trong heredoc → has_okf_frontmatter() phải True
BLOCK=$(awk '/cat > "\$DRAFT_FILE" << EOF/{f=1;next} f{ if($0=="---"){n++; print; if(n==2) exit} else print }' "$OB" \
        | sed 's/${DATE}/230623/g; s/${PROJECT_SLUG}/demo/g; s/\$(date +%Y-%m-%d)/2026-06-23/g')
RENDER=$(printf '%s\n\n# 230623-onboard-demo\n' "$BLOCK")
RES=$(printf '%s' "$RENDER" | python3 -c "
import sys, importlib.util
spec=importlib.util.spec_from_file_location('okf','$OKF')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print('OKF' if m.has_okf_frontmatter(sys.stdin.read()) else 'FAIL')
")
[ "$RES" = "OKF" ] && ok "heredoc frontmatter parse được OKF v0.1 (type: draft)" || bad "heredoc OKF" "render: $RES — frontmatter không đạt"

hdr "C — skill xuất HTML: OKF N/A (không phải wiki .md)"
for s in "${HTML_SKILLS[@]}"; do
  f="$SK/$s.md"
  [ -f "$f" ] && ok "$s → HTML output, OKF N/A (bỏ qua đúng)" || bad "$s" "không tìm thấy file"
done

hdr "D — toàn wiki repo OKF (chỉ cho phép file legacy đã biết)"
ALLOW="220626-chown.md"   # draft legacy, ngoài phạm vi proposal này
BADF=$(python3 "$OKF" --wiki-dir llmwiki/wiki 2>/dev/null | awk '/chua dat chuan/{f=1;next} f&&/^ +- /{sub(/^ +- +/,"");print}' )
UNEXPECTED=""
for b in $BADF; do case "$b" in *"$ALLOW") : ;; *) UNEXPECTED="$UNEXPECTED $b" ;; esac; done
if [ -z "${UNEXPECTED// }" ]; then
  ok "wiki OKF: chỉ còn legacy đã biết ($ALLOW) — không file mới nào fail"
else
  bad "wiki OKF" "file fail ngoài dự kiến:$UNEXPECTED"
fi

printf '\n\033[1m═══ TỔNG: %d test — \033[1;32m%d PASS\033[0m / \033[1;31m%d FAIL\033[0m\n' "$N" "$PASS" "$FAIL"
[ "$FAIL" = "0" ] && exit 0 || exit 1
