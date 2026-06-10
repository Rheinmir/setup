#!/usr/bin/env bash
# install-harness.sh — cài llmwiki harness stack (L0–L4) vào project.
# Idempotent. Tự detect 2 trường hợp:
#   NEW     : chưa có llmwiki/  → cài đủ, bật chặn ngay
#   MIGRATE : đã có llmwiki/    → cài + baseline audit, chỉ bật chặn khi hết nợ
#
# Usage:
#   bash harness/scripts/install-harness.sh [project_root]
#   (chạy từ bất kỳ đâu; mặc định project_root = thư mục hiện tại)
#
# Nguồn file: ưu tiên bundle cạnh script; thiếu thì clone rheinmir/setup@orca.
set -euo pipefail

ROOT="$(cd "${1:-.}" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE="$(cd "$SCRIPT_DIR/../.." && pwd)"   # repo chứa harness/ + llmwiki/
TMP_CLONE=""

log()  { printf '\033[1;32m[harness]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[harness]\033[0m %s\n' "$*"; }

cleanup() { [ -n "$TMP_CLONE" ] && rm -rf "$TMP_CLONE" || true; }
trap cleanup EXIT

# ---------- 0. Xác định nguồn ----------
src_ok() { [ -d "$1/harness/validators" ] && [ -d "$1/llmwiki/.claude/hooks" ]; }
SRC="$BUNDLE"
if ! src_ok "$SRC"; then
  log "Bundle cạnh script thiếu file nguồn → clone template rheinmir/setup@orca"
  TMP_CLONE="$(mktemp -d /tmp/llmwiki-harness-src.XXXXXX)"
  git clone --depth 1 -b orca git@github.com:rheinmir/setup.git "$TMP_CLONE" >/dev/null 2>&1 \
    || git clone --depth 1 -b orca https://github.com/rheinmir/setup.git "$TMP_CLONE" >/dev/null 2>&1
  SRC="$TMP_CLONE"
  src_ok "$SRC" || { warn "Template repo chưa có harness/ — sync template trước"; exit 1; }
fi

# ---------- 1. Detect mode ----------
if [ -d "$ROOT/llmwiki" ]; then MODE="migrate"; else MODE="new"; fi
log "Project: $ROOT — mode: $MODE"

# ---------- 2. Khung llmwiki (mode new) ----------
if [ "$MODE" = "new" ]; then
  mkdir -p "$ROOT/llmwiki/wiki"/{concepts,entities,sources/draft,draft/orca} \
           "$ROOT/llmwiki"/{raw,html,skills}
  touch "$ROOT/llmwiki/raw/.gitkeep"
  [ -f "$ROOT/llmwiki/wiki/index.md" ] || printf '# Wiki Index\n\n| File | Type | Summary |\n|------|------|---------|\n' > "$ROOT/llmwiki/wiki/index.md"
  [ -f "$ROOT/llmwiki/wiki/log.md" ]   || printf '# Operation Log\n' > "$ROOT/llmwiki/wiki/log.md"
fi

# ---------- 3. L0 + validators + scripts + evals (vendor-neutral core) ----------
mkdir -p "$ROOT/harness"
cp -R "$SRC/harness/validators" "$ROOT/harness/" 2>/dev/null || true
mkdir -p "$ROOT/harness/scripts" "$ROOT/harness/evals"
cp "$SRC/harness/policy.yaml"               "$ROOT/harness/policy.yaml"
cp "$SRC/harness/recipe.md"                 "$ROOT/harness/recipe.md"
cp "$SRC/harness/scripts/wiki-health.py"    "$ROOT/harness/scripts/wiki-health.py"
cp "$SRC/harness/scripts/install-harness.sh" "$ROOT/harness/scripts/install-harness.sh" 2>/dev/null || true
[ -f "$ROOT/harness/evals/promptfooconfig.yaml" ] || cp "$SRC/harness/evals/promptfooconfig.yaml" "$ROOT/harness/evals/promptfooconfig.yaml"
log "L0 policy + validators + wiki-health + evals: OK"

# ---------- 4. L1 adapter Claude Code ----------
mkdir -p "$ROOT/llmwiki/.claude/hooks/validators"
cp "$SRC/llmwiki/.claude/hooks/"*.py "$ROOT/llmwiki/.claude/hooks/"
# copy validators vào cạnh hooks để llmwiki deploy standalone vẫn chạy (resolution tier 2)
cp "$SRC/harness/validators/"*.py "$ROOT/llmwiki/.claude/hooks/validators/"
printf '# runtime data — khong commit\naudit/\n' > "$ROOT/llmwiki/.claude/.gitignore"

SETTINGS="$ROOT/llmwiki/.claude/settings.json"
if [ -f "$SETTINGS" ]; then
  cp "$SETTINGS" "$SETTINGS.bak.$(date +%s)"
  python3 - "$SETTINGS" "$SRC/llmwiki/.claude/settings.json" <<'PY'
import json, sys
cur = json.load(open(sys.argv[1])); tpl = json.load(open(sys.argv[2]))
# merge: deny rules (union), hooks (thêm event còn thiếu — không đè hook user tự thêm)
cur.setdefault("permissions", {}).setdefault("deny", [])
for d in tpl.get("permissions", {}).get("deny", []):
    if d not in cur["permissions"]["deny"]:
        cur["permissions"]["deny"].append(d)
cur.setdefault("hooks", {})
for event, defs in tpl.get("hooks", {}).items():
    cur_defs = cur["hooks"].setdefault(event, [])
    existing = json.dumps(cur_defs)
    for d in defs:  # append hook harness nếu event đã có hook user — không đè
        cmd = (d.get("hooks") or [{}])[0].get("command", "")
        if cmd and cmd not in existing:
            cur_defs.append(d)
json.dump(cur, open(sys.argv[1], "w"), indent=2, ensure_ascii=False)
PY
  log "settings.json: MERGE (backup .bak.*)"
else
  cp "$SRC/llmwiki/.claude/settings.json" "$SETTINGS"
  log "settings.json: cài mới"
fi

# ---------- 5. L2 pre-commit ----------
if [ ! -f "$ROOT/.pre-commit-config.yaml" ]; then
  cp "$SRC/.pre-commit-config.yaml" "$ROOT/.pre-commit-config.yaml"
  log "L2 .pre-commit-config.yaml: cài mới (kiểm tra prefix path nếu wiki không nằm ở llmwiki/wiki)"
else
  warn "L2 .pre-commit-config.yaml đã tồn tại — không đè; merge tay nếu cần (mẫu: $SRC/.pre-commit-config.yaml)"
fi
if command -v pre-commit >/dev/null 2>&1 && [ -d "$ROOT/.git" ]; then
  (cd "$ROOT" && pre-commit install >/dev/null) && log "pre-commit install: OK"
else
  warn "pre-commit chưa cài hoặc không phải git repo → chạy sau: pipx install pre-commit && pre-commit install"
fi

# ---------- 6. Baseline audit (quan trọng với migrate) ----------
WIKI="$ROOT/llmwiki/wiki"
mkdir -p "$ROOT/harness/metrics"
DEBT=0
log "Baseline audit..."
CONTENT_FILES=$(find "$WIKI"/concepts "$WIKI"/entities "$WIKI"/sources "$WIKI"/draft -name '*.md' \
  ! -name 'README.md' ! -name '_template.md' 2>/dev/null || true)
if [ -n "$CONTENT_FILES" ]; then
  # shellcheck disable=SC2086
  python3 "$ROOT/harness/validators/origin_required.py" $CONTENT_FILES || DEBT=1
fi
python3 "$ROOT/harness/validators/index_sync.py" --wiki-dir "$WIKI" || DEBT=1
python3 "$ROOT/harness/scripts/wiki-health.py" --wiki-dir "$WIKI" \
  --csv "$ROOT/harness/metrics/wiki-health.csv" > "$ROOT/harness/metrics/baseline-$(date +%F).json" || true
log "Báo cáo baseline: harness/metrics/baseline-$(date +%F).json"

# ---------- 7. Kết luận ----------
{
  printf '\n## %s — install-harness — mode=%s\n' "$(date +%F)" "$MODE"
  printf -- '- Cài harness L0–L4 (validators, hooks, pre-commit, wiki-health, evals)\n'
  [ "$DEBT" = "1" ] && printf -- '- ⚠ CÓ NỢ wiki (thiếu Origin / index lệch) — backfill trước khi tin Stop hook\n'
} >> "$WIKI/log.md" 2>/dev/null || true

echo
if [ "$DEBT" = "1" ]; then
  warn "MIGRATE CÓ NỢ: sửa các vi phạm in phía trên TRƯỚC, rồi chạy lại script để xác nhận sạch."
  warn "Hooks đã cài nhưng phiên đụng wiki sẽ bị Stop hook nhắc cho tới khi index/Origin sạch."
  exit 3
fi
log "HOÀN TẤT — harness sạch, enforcement hoạt động đầy đủ. Smoke thử:"
log '  echo '"'"'{"action":"write","file_path":"llmwiki/raw/x.md"}'"'"' | python3 harness/validators/no_write_raw.py  # phải exit 2'
