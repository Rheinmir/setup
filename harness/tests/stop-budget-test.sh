#!/usr/bin/env bash
# stop-budget-test — sig `hook-timeout|Stop:stop.py|`: Claude Code giết stop.py ở 30s. stop.py gọi tuần tự
# ~15 subprocess, timeout con cộng lại >500s, không có ngân sách tổng → bước nặng (medic --ci 42s,
# build-wiki-graph 14s) ăn hết 30s và cổng R3 index-sync đứng cuối KHÔNG BAO GIỜ chạy.
# Fixture: medic.py + build-wiki-graph.py giả ngủ 60s, phiên chạm harness/ + thêm file wiki mới.
# PASS khi stop.py thoát < 28s VÀ auto-index R3 vẫn chạy (file wiki mới có trong index.md).
# Usage: bash harness/tests/stop-budget-test.sh [repo-root]   (exit 0 = pass)
set -u
ROOT="$(cd "${1:-.}" && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cp -R "$ROOT/llmwiki" "$TMP/llmwiki"; cp -R "$ROOT/fdk" "$TMP/fdk"; cp -R "$ROOT/harness" "$TMP/harness"
cp "$ROOT/.gitignore" "$TMP/.gitignore"
rm -f "$TMP"/harness/metrics/.stop-debounce.json
for f in fdk/tools/medic.py fdk/tools/build-wiki-graph.py; do printf 'import time; time.sleep(60)\n' > "$TMP/$f"; done
git -C "$TMP" -c init.defaultBranch=main init -q
printf -- '---\ntype: concept\ntitle: bb\n---\n# bb\n## Origin\nstop-budget\n' > "$TMP/llmwiki/wiki/concepts/bb-stop-budget.md"
T0=$(date +%s)
printf '{"session_id":"stop-budget-test"}' | CLAUDE_PROJECT_DIR="$TMP" OVERSTACK_TOUCHED_PATHS=0 \
  perl -e 'alarm 45; exec @ARGV' python3 "$TMP/llmwiki/.claude/hooks/stop.py" >/dev/null 2>&1
rc=$?; DT=$(( $(date +%s) - T0 ))
ok=1
if [ "$DT" -ge 28 ]; then echo "  ✗ stop.py chạy ${DT}s (rc=$rc) — vượt ngân sách hook 30s"; ok=0; else echo "  ✓ stop.py thoát sau ${DT}s (rc=$rc)"; fi
if grep -q 'bb-stop-budget' "$TMP/llmwiki/wiki/index.md"; then echo "  ✓ cổng R3 auto-index vẫn chạy sau bước nặng"
else echo "  ✗ cổng R3 auto-index KHÔNG chạy (bị bước nặng ăn hết ngân sách)"; ok=0; fi
[ $ok -eq 1 ] && printf '\n═══ stop-budget: PASS\n' || printf '\n═══ stop-budget: FAIL\n'
[ $ok -eq 1 ]
