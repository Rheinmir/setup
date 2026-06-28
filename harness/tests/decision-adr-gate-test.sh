#!/usr/bin/env bash
# decision-adr-gate-test — R13 decision→ADR gate + vòng đời edit/delete-when-superseded.
#   A) DECISION→ADR: row Type=architecture trong decisions.md phải ref 'ADR-N' (hoặc '(no-adr:)').
#   B) DELETE-NEEDS-SUPERSEDE: xóa ADR còn LIVE bị chặn; xóa khi đã có ADR đè thì cho.
#   (EDIT không bị chặn — validator chỉ soi linkage + xóa, không soi nội dung.)
#
# Usage: bash harness/tests/decision-adr-gate-test.sh [repo-root]   (exit 0 = pass)
set -u
ROOT="$(cd "${1:-.}" && pwd)"
V="$ROOT/harness/validators/decision_adr.py"
pass=0; fail=0
ok(){  printf '  \033[1;32m✓\033[0m %s\n' "$1"; pass=$((pass+1)); }
bad(){ printf '  \033[1;31m✗\033[0m %s\n' "$1"; fail=$((fail+1)); }
hdr(){ printf '\n\033[1m%s\033[0m\n' "$1"; }
H='| Date | Decision | Type | Context | Outcome |\n|---|---|---|---|---|\n'

hdr "A — decision→ADR (architecture phải ref ADR; type khác miễn)"
T="$(mktemp -d)"
printf "$H| d | tách X | architecture | c | đã làm (no ref) |\n" > "$T/decisions.md"
python3 "$V" "$T/decisions.md" >/dev/null 2>&1; [ $? -eq 2 ] && ok "CHẶN arch thiếu ADR" || bad "không chặn arch thiếu ADR"
printf "$H| d | tách X | architecture | c | ADR-008: ... |\n| d | nhỏ | design | c | x |\n" > "$T/decisions.md"
python3 "$V" "$T/decisions.md" >/dev/null 2>&1; [ $? -eq 0 ] && ok "cho qua arch CÓ ADR + design miễn" || bad "chặn nhầm"
printf "$H| d | tách X | architecture | c | (no-adr: quá nhỏ) |\n" > "$T/decisions.md"
python3 "$V" "$T/decisions.md" >/dev/null 2>&1; [ $? -eq 0 ] && ok "cho qua khi khai (no-adr:)" || bad "chặn (no-adr:)"
rm -rf "$T"

hdr "B — delete-needs-supersede (xóa khi có cái đè)"
G="$(mktemp -d)"
( cd "$G"; git init -q; git config user.email t@t; git config user.name t
  mkdir -p fdk/wiki/sources/adr
  printf -- '---\ntype: decision\n---\n# ADR-001\n## Status\nAccepted\n' > fdk/wiki/sources/adr/ADR-001-live.md
  git add -A; git commit -qm init; git rm -q fdk/wiki/sources/adr/ADR-001-live.md ) >/dev/null 2>&1
CLAUDE_PROJECT_DIR="$G" python3 "$V" --guard-deletions >/dev/null 2>&1; [ $? -eq 2 ] && ok "CHẶN xóa ADR còn LIVE" || bad "không chặn xóa ADR live"
( cd "$G"; git reset -q --hard HEAD   # khôi phục ADR-001
  printf -- '---\ntype: decision\n---\n# ADR-002\n## Status\nAccepted\n\nsupersedes ADR-001.\n' > fdk/wiki/sources/adr/ADR-002-new.md
  git add -A; git commit -qm adr2; git rm -q fdk/wiki/sources/adr/ADR-001-live.md ) >/dev/null 2>&1
CLAUDE_PROJECT_DIR="$G" python3 "$V" --guard-deletions >/dev/null 2>&1; [ $? -eq 0 ] && ok "CHO xóa ADR khi đã bị đè (ADR-002 supersedes)" || bad "chặn nhầm khi đã bị đè"
rm -rf "$G"

printf '\n\033[1m═══ TỔNG: %d test — \033[1;32m%d PASS\033[0m / \033[1;31m%d FAIL\033[0m\033[0m\n' "$((pass+fail))" "$pass" "$fail"
[ "$fail" -eq 0 ]
