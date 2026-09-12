#!/usr/bin/env bash
# dot-layout-runtime-test.sh — hook GLOBAL chạy trong dự án downstream layout DOT có làm đúng việc không.
# Bốn bất biến (mỗi cái từng gãy thật, đo 2026-09-11):
#   (a) session_start phải KÊU khi stamp lệch MAJOR với global (harness_integrity không được câm)
#   (b) stop KHÔNG được đẻ thư mục trần llmwiki/ hoặc harness/ cạnh .llmwiki/ .harness/ (GH#153)
#   (c) stop phải ghi session-provenance vào .llmwiki/wiki/sources/ (đúng cây), và vẽ wiki-graph nếu engine có
#   (d) CI sinh cho downstream không chứa đường trần llmwiki/ · harness/ ngoài harness-src và $HOME/.claude
set -uo pipefail
SRC="${1:?usage: dot-layout-runtime-test.sh <repo-root>}"
HERE="$(cd "$(dirname "$0")" && pwd)"; source "$HERE/downstream-fixture.sh"
PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  \033[1;32mPASS\033[0m  %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  \033[1;31mFAIL\033[0m  %s — %s\n' "$1" "$2"; }
make_downstream_fixture "$SRC" || exit 1
trap 'rm -rf "$FX_TMP"' EXIT

# (a) hạ global về 1.0.0 → stamp (1.3.x) lệch MAJOR → phải in dòng harness-integrity
python3 - "$GH/version.json" <<'PY'
import json,sys; p=sys.argv[1]; d=json.load(open(p)); d["template_version"]="1.0.0"; json.dump(d,open(p,"w"))
PY
OUT="$(echo '{"session_id":"t"}' | CLAUDE_PROJECT_DIR="$FX" python3 "$GH/hooks/session_start.py" 2>&1)"
grep -q "harness-integrity" <<<"$OUT" \
  && ok "(a) session_start kêu lệch MAJOR trong layout dot" \
  || bad "(a) session_start câm" "không có dòng harness-integrity — stamp đọc ở llmwiki/ trần?"

# (b)+(c) chạy stop với một wiki có nội dung
mkdir -p "$FX/.llmwiki/wiki/concepts"
printf -- '---\ntype: concept\ntitle: t\ntags: [t]\ntimestamp: 2026-09-11\nid: t\n---\n# t\n\n## Origin\n- test\n' > "$FX/.llmwiki/wiki/concepts/t.md"
echo '{"session_id":"t","stop_hook_active":false}' | CLAUDE_PROJECT_DIR="$FX" python3 "$GH/hooks/stop.py" >/dev/null 2>&1
[ ! -d "$FX/llmwiki" ] && [ ! -d "$FX/harness" ] \
  && ok "(b) không đẻ llmwiki/ hay harness/ trần" \
  || bad "(b) thư mục trần xuất hiện" "$(ls -d "$FX/llmwiki" "$FX/harness" 2>/dev/null | tr '\n' ' ')"
ls "$FX/.llmwiki/wiki/sources/"*session-provenance*.md >/dev/null 2>&1 \
  && ok "(c) session-provenance ghi vào .llmwiki/wiki/sources/" \
  || bad "(c) không có session-provenance dưới .llmwiki" "stop bỏ qua vì has_stamp đọc llmwiki/ trần?"
if [ -f "$GH/fdk/tools/build-wiki-graph.py" ]; then
  [ -f "$FX/.llmwiki/html/wiki-graph.html" ] \
    && ok "(c) wiki-graph vẽ vào .llmwiki/html/" \
    || bad "(c) wiki-graph không vẽ" "wikigraph_on=False vì stamp không thấy"
fi

# (d) CI sinh ra cho downstream: đường trần chỉ được phép trong harness-src / $HOME/.claude
CI="$FX/.github/workflows/harness.yml"
BARE="$(grep -nE '(^|[ "(=])(llmwiki|harness)/' "$CI" | grep -vE 'harness-src|HOME/\.claude|\$OVERSTACK_DIR|\$HARNESS_DIR' || true)"
[ -z "$BARE" ] \
  && ok "(d) CI downstream không có đường trần" \
  || bad "(d) CI downstream còn đường trần (skip im lặng ở dự án dot)" "$(head -3 <<<"$BARE" | tr '\n' ' ')"

printf '\ndot-layout-runtime: %d PASS · %d FAIL\n' "$PASS" "$FAIL"
[ "$FAIL" = 0 ]
