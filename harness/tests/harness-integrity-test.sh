#!/usr/bin/env bash
# harness-integrity-test — U11 (GH#63 Phase 5): session_start.harness_integrity()
# so llmwiki/.harness-stamp (hợp đồng repo) vs ~/.claude/harness/version.json (global đang cài).
#
# 4 kịch bản, hermetic (global giả qua OVERSTACK_HARNESS_HOME, không đụng ~/.claude thật):
#   1. LỆCH MAJOR (stamp 1.x vs global 2.x)  → cảnh báo TO "LỆCH MAJOR"
#   2. lệch minor (1.3.6 vs 1.4.0)           → nhắc nhẹ, KHÔNG có "LỆCH MAJOR"
#   3. có stamp nhưng global CHƯA cài        → cảnh báo "CHƯA cài"
#   4. không có stamp (repo chưa bootstrap)  → im lặng tuyệt đối (fail-open)
# Usage: bash harness/tests/harness-integrity-test.sh [repo-root]   (exit 0 pass, 1 fail)
set -u
ROOT="${1:-.}"; cd "$ROOT" || { echo "không vào được $ROOT"; exit 2; }
pass=0; fail=0
ok(){  printf '  \033[1;32m✓\033[0m %s\n' "$1"; pass=$((pass+1)); }
bad(){ printf '  \033[1;31m✗\033[0m %s — %s\n' "$1" "$2"; fail=$((fail+1)); }

FX="$(mktemp -d)"; trap 'rm -rf "$FX"' EXIT
run_integrity(){ # run_integrity <repo> <harness_home> — in stdout của harness_integrity()
  OVERSTACK_HARNESS_HOME="$2" python3 - "$1" <<'PY'
import sys, os, pathlib
sys.path.insert(0, "llmwiki/.claude/hooks")
import session_start
session_start.harness_integrity(pathlib.Path(sys.argv[1]))
PY
}

# 1. LỆCH MAJOR
mkdir -p "$FX/r1/llmwiki" "$FX/g1"
printf '{"schema": 1, "guarded_by": "1.3.6"}\n' > "$FX/r1/llmwiki/.harness-stamp"
printf '{"template_version": "2.0.0"}\n' > "$FX/g1/version.json"
out=$(run_integrity "$FX/r1" "$FX/g1")
echo "$out" | grep -q "LỆCH MAJOR" \
  && ok "MAJOR-skew (stamp 1.3.6 vs global 2.0.0) → cảnh báo TO" \
  || bad "MAJOR-skew không cảnh báo" "U11 vô hiệu — agent không biết repo được gác bản khác hẳn"

# 2. lệch minor — nhắc nhẹ, không hét MAJOR
mkdir -p "$FX/r2/llmwiki" "$FX/g2"
printf '{"schema": 1, "guarded_by": "1.3.6"}\n' > "$FX/r2/llmwiki/.harness-stamp"
printf '{"template_version": "1.4.0"}\n' > "$FX/g2/version.json"
out=$(run_integrity "$FX/r2" "$FX/g2")
if echo "$out" | grep -q "LỆCH MAJOR"; then
  bad "minor-skew bị hét thành MAJOR" "noise — user sẽ lờn cảnh báo thật"
elif echo "$out" | grep -q "harness-integrity"; then
  ok "minor-skew (1.3.6 vs 1.4.0) → nhắc nhẹ đúng mức"
else
  bad "minor-skew im lặng" "skew không observable"
fi

# 3. stamp có, global chưa cài
mkdir -p "$FX/r3/llmwiki"
printf '{"schema": 1, "guarded_by": "1.3.6"}\n' > "$FX/r3/llmwiki/.harness-stamp"
out=$(run_integrity "$FX/r3" "$FX/khong-ton-tai")
echo "$out" | grep -qi "CHƯA cài" \
  && ok "stamp có + global thiếu → cảnh báo cài global" \
  || bad "global thiếu mà im lặng" "repo tưởng được gác nhưng engine không chạy (dark-rail)"

# 4. không stamp → im lặng (fail-open)
mkdir -p "$FX/r4/llmwiki" "$FX/g4"
printf '{"template_version": "1.3.6"}\n' > "$FX/g4/version.json"
out=$(run_integrity "$FX/r4" "$FX/g4")
[ -z "$out" ] \
  && ok "không stamp → im lặng tuyệt đối (repo chưa bootstrap không bị nhiễu)" \
  || bad "không stamp mà vẫn in" "nhiễu mọi repo chưa dùng v4"

# 5. stamp JSON hỏng → không được crash (fail-open)
mkdir -p "$FX/r5/llmwiki" "$FX/g5"
printf 'not-json{{{' > "$FX/r5/llmwiki/.harness-stamp"
printf '{"template_version": "1.3.6"}\n' > "$FX/g5/version.json"
if run_integrity "$FX/r5" "$FX/g5" >/dev/null 2>&1; then
  ok "stamp hỏng → fail-open, không crash phiên"
else
  bad "stamp hỏng làm hook crash" "SessionStart gãy vì 1 file rác"
fi

printf '\n\033[1m%d pass · %d fail\033[0m\n' "$pass" "$fail"
[ "$fail" -eq 0 ] || exit 1
