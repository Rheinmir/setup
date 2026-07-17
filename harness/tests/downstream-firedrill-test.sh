#!/usr/bin/env bash
# downstream-firedrill-test — CI downstream phải TỰ chứng rule gốc còn cắn, và chứng ĐÚNG CÁCH.
#
# Bối cảnh: harness-doctor (fire-drill bắt dark-rail) trước đây không wire xuống downstream →
# guardrail của framework có thể mục ruỗng mà CI downstream không kêu. Nay wire vào job validate.
# NHƯNG có một cái bẫy tất phải chặn: chạy fire-drill từ GLOBAL (~/.claude/harness) báo dark-rail
# GIẢ (global thiếu hooks/pre-commit của repo → side-effect rail R4/R8/R10/R17 = missing). Phải
# chạy từ CHECKOUT ĐẦY ĐỦ ($RUNNER_TEMP/harness-src mà CI đã clone) → 18/18 thật.
#
# Hai nửa:
#   1. step harness-doctor CÓ trong out/ci/harness.yml (đã ship xuống)
#   2. nó chạy từ harness-src (full repo), KHÔNG từ $HOME/.claude (global) → không đỏ giả
#
# Usage: bash harness/tests/downstream-firedrill-test.sh [repo-root]   (exit 0 = pass)
set -u
ROOT="$(cd "${1:-.}" && pwd)"
CI="$ROOT/harness/poc-vendor-neutral/out/ci/harness.yml"
GEN="$ROOT/harness/poc-vendor-neutral/gen-converters.py"
fail=0
ok()  { printf '  \033[1;32m✓\033[0m %s\n' "$1"; }
bad() { printf '  \033[1;31m✗\033[0m %s\n' "$1"; fail=$((fail+1)); }

# out/ là build-artifact (gitignored) — install SINH nó tại chỗ rồi mới copy CI. Fresh
# checkout chưa có out/ → regen trước khi soi (idempotent, đúng như install.sh làm).
( cd "$ROOT/harness/poc-vendor-neutral" && python3 gen-converters.py >/dev/null 2>&1 ) \
  || bad "gen-converters.py chạy lỗi — không sinh được out/ci/harness.yml"
[ -f "$CI" ] || bad "không thấy out/ci/harness.yml sau regen"

# 1. fire-drill có mặt trong CI downstream đã sinh
grep -q 'harness-doctor.py" --ci' "$CI" 2>/dev/null \
  && ok "out/ci/harness.yml có step harness-doctor --ci (fire-drill đã ship xuống)" \
  || bad "CI downstream KHÔNG chạy fire-drill → dark rail của framework không nổi đỏ tại downstream"

# 2. chạy từ full checkout, KHÔNG từ global (bẫy đỏ-giả)
grep -q 'RUNNER_TEMP/harness-src/harness/scripts/harness-doctor.py" --ci' "$CI" 2>/dev/null \
  && ok "fire-drill chạy từ harness-src (full repo) → 18/18 thật" \
  || bad "fire-drill KHÔNG trỏ harness-src — nếu chạy từ global sẽ báo dark-rail GIẢ (R4/R8/R10/R17 missing)"

if grep -q 'HOME/.claude/harness/harness/scripts/harness-doctor.py" --ci' "$CI" 2>/dev/null; then
  bad "fire-drill trỏ \$HOME/.claude (global) — global thiếu hooks repo → CI đỏ giả mỗi PR"
else
  ok "fire-drill KHÔNG trỏ global (tránh đỏ-giả)"
fi

# 3. generator là nguồn — sửa output tay sẽ bị regen đè; đảm bảo generator cũng mang step
grep -q 'harness-doctor.py" --ci' "$GEN" 2>/dev/null \
  && ok "gen-converters.py (nguồn) mang step → regen không mất" \
  || bad "step chỉ có ở output, không ở generator → lần regen kế sẽ xoá mất"

if [ "$fail" -eq 0 ]; then
  printf '\n\033[1m═══ downstream-firedrill: \033[1;32mPASS\033[0m\033[0m\n'; exit 0
fi
printf '\n\033[1m═══ downstream-firedrill: \033[1;31m%d VI PHẠM\033[0m\033[0m\n' "$fail"; exit 1
