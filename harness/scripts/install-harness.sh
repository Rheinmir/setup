#!/usr/bin/env bash
# install-harness.sh — cài llmwiki harness stack (L0–L4) vào project.
# Idempotent. Tự detect 2 trường hợp:
#   NEW     : chưa có llmwiki/  → cài đủ, bật chặn ngay
#   MIGRATE : đã có llmwiki/    → cài + baseline audit, chỉ bật chặn khi hết nợ
#
# Usage:
#   bash harness/scripts/install-harness.sh [project_root]   # per-project (mặc định)
#   bash harness/scripts/install-harness.sh --global         # global: hooks vào ~/.claude (mọi project llmwiki trên máy)
#
# GLOBAL mode: copy hooks+validators vào ~/.claude/harness/hooks/, đăng ký 4 hooks
# vào ~/.claude/settings.json với shell guard `[ -d "$CLAUDE_PROJECT_DIR/llmwiki" ]`
# — project không có llmwiki chỉ tốn ~1ms/tool-call, không python, không audit,
# không false-positive (raw/ của data project, wiki/ của project ngoài).
# Global KHÔNG thay thế per-project cho team: teammate clone repo chỉ được bảo vệ
# khi harness/ + .claude/settings.json được commit vào repo (mode per-project).
# Global cũng KHÔNG cài pre-commit (L2) và không chạy baseline audit.
#
# Nguồn file: ưu tiên bundle cạnh script; thiếu thì clone rheinmir/setup@orca.
set -euo pipefail

# ---------- Flag scan (tách --self-heal khỏi positional) ----------
# --self-heal: sau audit, installer TỰ backfill nợ (Origin+index+OKF) trong 1 process
# rồi re-audit 1 lần — gộp vòng lặp 3-reinstall của agent thành 1 lệnh bash.
SELF_HEAL=0
NO_CLONE=0
ARGS=()
for a in "$@"; do
  case "$a" in
    --self-heal) SELF_HEAL=1 ;;
    --no-clone)  NO_CLONE=1 ;;
    *) ARGS+=("$a") ;;
  esac
done
set -- ${ARGS[@]+"${ARGS[@]}"}   # bash 3.2-safe khi mảng rỗng + set -u

if [ "${1:-}" = "--global" ]; then ROOT="$HOME"; else ROOT="$(cd "${1:-.}" && pwd)"; fi
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
  if [ "$NO_CLONE" = "1" ]; then
    warn "Bundle nguồn thiếu và --no-clone bật → fast-fail (không treo mạng). Cung cấp bundle rồi chạy lại."
    exit 1
  fi
  log "Bundle cạnh script thiếu file nguồn → clone template rheinmir/setup@orca"
  TMP_CLONE="$(mktemp -d /tmp/llmwiki-harness-src.XXXXXX)"
  git clone --depth 1 -b orca git@github.com:rheinmir/setup.git "$TMP_CLONE" >/dev/null 2>&1 \
    || git clone --depth 1 -b orca https://github.com/rheinmir/setup.git "$TMP_CLONE" >/dev/null 2>&1
  SRC="$TMP_CLONE"
  src_ok "$SRC" || { warn "Template repo chưa có harness/ — sync template trước"; exit 1; }
fi

# ---------- 0.5. GLOBAL mode ----------
if [ "${1:-}" = "--global" ]; then
  GH="$HOME/.claude/harness"
  mkdir -p "$GH/hooks/validators"
  cp "$SRC/llmwiki/.claude/hooks/"*.py "$GH/hooks/"
  cp "$SRC/harness/validators/"*.py "$GH/hooks/validators/"
  cp "$SRC/harness/scripts/health-check.py" "$GH/hooks/health-check.py"   # session_start.py tìm cạnh hooks
  log "GLOBAL: hooks + validators + health-check → $GH/hooks/"

  SETTINGS="$HOME/.claude/settings.json"
  [ -f "$SETTINGS" ] && cp "$SETTINGS" "$SETTINGS.bak.$(date +%s)" || echo '{}' > "$SETTINGS"
  python3 - << 'PYEOF'
import json, os, re
path = os.path.expanduser("~/.claude/settings.json")
cur = json.load(open(path))
HOOKS_DIR = '$HOME/.claude/harness/hooks'
def script_of(command):
    m = re.search(r'([A-Za-z0-9_./-]+\.py)', command or "")
    return os.path.basename(m.group(1)) if m else None
def cmd(script):
    # if-guard (KHÔNG dùng `&& ... || true` — nó nuốt exit 2, mất khả năng chặn).
    # `-f` fail-open: hook THIẾU file → bỏ qua, KHÔNG brick tool (sự cố cozyroom).
    p = f'{HOOKS_DIR}/{script}'
    return f'if [ -d "${{CLAUDE_PROJECT_DIR:-.}}/llmwiki" ] && [ -f "{p}" ]; then python3 "{p}"; fi'
tpl = {
    "PreToolUse":  [{"matcher": "Write|Edit|MultiEdit|NotebookEdit|Bash", "script": "pre_tool_use.py"},
                    {"matcher": "Bash", "script": "orca_guard.py"}],
    "PostToolUse": {"matcher": "Write|Edit|MultiEdit", "script": "post_tool_use.py"},
    "Stop":        {"matcher": None, "script": "stop.py"},
    "SessionEnd":  {"matcher": None, "script": "session_end.py"},
    "SessionStart": {"matcher": None, "script": "session_start.py"},
    "UserPromptSubmit": {"matcher": None, "script": "user_prompt_submit.py"},
}
cur.setdefault("permissions", {}).setdefault("deny", [])
for d in ["Write(./llmwiki/raw/**)", "Edit(./llmwiki/raw/**)", "MultiEdit(./llmwiki/raw/**)"]:
    if d not in cur["permissions"]["deny"]:
        cur["permissions"]["deny"].append(d)
cur.setdefault("hooks", {})
# idempotent re-merge: dedup theo BASENAME script → chạy lại NÂNG CẤP lệnh trần cũ thành có guard.
for event, spec in tpl.items():
    defs = cur["hooks"].setdefault(event, [])
    specs = spec if isinstance(spec, list) else [spec]
    tpl_scripts = {s["script"] for s in specs}
    defs[:] = [d for d in defs
               if not any(script_of(hh.get("command")) in tpl_scripts for hh in (d.get("hooks") or []))]
    for s in specs:
        entry = {"hooks": [{"type": "command", "command": cmd(s["script"]), "timeout": 30}]}
        if s["matcher"]:
            entry["matcher"] = s["matcher"]
        defs.append(entry)
json.dump(cur, open(path, "w"), indent=2, ensure_ascii=False)
print("[harness] GLOBAL: settings.json merged (backup .bak.*)")
PYEOF

  python3 -c "import json; json.load(open(\"$SETTINGS\"))" || { warn "settings.json hỏng — khôi phục từ backup!"; exit 1; }
  # Smoke: validator phải chặn được
  RC=0; echo '{"action":"write","file_path":"llmwiki/raw/x.md"}' | python3 "$GH/hooks/validators/no_write_raw.py" 2>/dev/null || RC=$?
  [ "$RC" = "2" ] && log "GLOBAL smoke OK: no_write_raw chặn đúng (rc=2)" || { warn "GLOBAL smoke FAIL (rc=$RC)"; exit 4; }
  log "GLOBAL HOÀN TẤT — restart session hoặc mở /hooks để reload. Per-project vẫn cần cho team (commit harness/ vào repo)."
  exit 0
fi

# ---------- 1. Detect mode ----------
if [ -d "$ROOT/llmwiki" ]; then MODE="migrate"; else MODE="new"; fi
SAME_BUNDLE=0; [ "$SRC" = "$ROOT" ] && SAME_BUNDLE=1
log "Project: $ROOT — mode: $MODE$([ $SAME_BUNDLE = 1 ] && echo ' (project chính là bundle — bỏ qua copy core)')"

# ---------- 2. Khung llmwiki (mode new) ----------
if [ "$MODE" = "new" ]; then
  mkdir -p "$ROOT/llmwiki/wiki"/{concepts,entities,sources/draft,draft/orca} \
           "$ROOT/llmwiki"/{raw,html,skills}
  touch "$ROOT/llmwiki/raw/.gitkeep"
  [ -f "$ROOT/llmwiki/wiki/index.md" ] || printf '# Wiki Index\n\n| File | Type | Summary |\n|------|------|---------|\n' > "$ROOT/llmwiki/wiki/index.md"
  [ -f "$ROOT/llmwiki/wiki/log.md" ]   || printf '# Operation Log\n' > "$ROOT/llmwiki/wiki/log.md"
fi

# ---------- 3. L0 + validators + scripts + evals (vendor-neutral core) ----------
if [ "$SAME_BUNDLE" = "0" ]; then
  mkdir -p "$ROOT/harness"
  cp -R "$SRC/harness/validators" "$ROOT/harness/" 2>/dev/null || true
  mkdir -p "$ROOT/harness/scripts" "$ROOT/harness/evals"
  cp "$SRC/harness/policy.yaml"               "$ROOT/harness/policy.yaml"
  cp "$SRC/harness/recipe.md"                 "$ROOT/harness/recipe.md"
  cp "$SRC/harness/scripts/"*.py              "$ROOT/harness/scripts/" 2>/dev/null || true
  [ -f "$ROOT/harness/version.json" ] || cp "$SRC/harness/version.json" "$ROOT/harness/version.json" 2>/dev/null || true
  cp "$SRC/harness/scripts/install-harness.sh" "$ROOT/harness/scripts/install-harness.sh" 2>/dev/null || true
  [ -f "$ROOT/harness/evals/promptfooconfig.yaml" ] || cp "$SRC/harness/evals/promptfooconfig.yaml" "$ROOT/harness/evals/promptfooconfig.yaml"
fi
log "L0 policy + validators + wiki-health + evals: OK"

# ---------- 4. L1 adapter Claude Code ----------
mkdir -p "$ROOT/llmwiki/.claude/hooks/validators"
[ "$SAME_BUNDLE" = "0" ] && cp "$SRC/llmwiki/.claude/hooks/"*.py "$ROOT/llmwiki/.claude/hooks/"
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
    # so sánh trên command THÔ — json.dumps escape quote nên substring-check sẽ luôn miss
    existing_cmds = {h.get("command") for d in cur_defs for h in (d.get("hooks") or [])}
    for d in defs:  # append hook harness nếu event đã có hook user — không đè
        cmd = (d.get("hooks") or [{}])[0].get("command", "")
        if cmd and cmd not in existing_cmds:
            cur_defs.append(d)
json.dump(cur, open(sys.argv[1], "w"), indent=2, ensure_ascii=False)
PY
  log "settings.json: MERGE (backup .bak.*)"
else
  cp "$SRC/llmwiki/.claude/settings.json" "$SETTINGS"
  log "settings.json: cài mới"
fi

# ---------- 4b. Settings ở ROOT — session mở tại root mới load hooks ----------
# (llmwiki/.claude/settings.json chỉ tác dụng khi session mở ngay tại llmwiki/)
ROOT_SETTINGS="$ROOT/.claude/settings.json"
mkdir -p "$ROOT/.claude"
[ -f "$ROOT_SETTINGS" ] && cp "$ROOT_SETTINGS" "$ROOT_SETTINGS.bak.$(date +%s)"
python3 - "$ROOT_SETTINGS" <<'PY'
import json, os, sys
path = sys.argv[1]
prefix = "llmwiki/"
hooks_dir = '$CLAUDE_PROJECT_DIR/llmwiki/.claude/hooks'
deny = [f"Write(./{prefix}raw/**)", f"Edit(./{prefix}raw/**)", f"MultiEdit(./{prefix}raw/**)"]
def h(script, matcher=None):
    # `-f` fail-open: hook THIẾU file → bỏ qua, KHÔNG brick tool (sự cố cozyroom).
    p = f'{hooks_dir}/{script}'
    d = {"hooks": [{"type": "command", "command": f'if [ -f "{p}" ]; then python3 "{p}"; fi'}]}
    if matcher: d["matcher"] = matcher
    return d
tpl = {"permissions": {"deny": deny}, "hooks": {
    "PreToolUse":  [h("pre_tool_use.py",  "Write|Edit|MultiEdit|NotebookEdit|Bash"), h("orca_guard.py", "Bash")],
    "PostToolUse": [h("post_tool_use.py", "Write|Edit|MultiEdit")],
    "Stop":        [h("stop.py")],
    "SessionEnd":  [h("session_end.py")],
    "SessionStart":[h("session_start.py")],
    "UserPromptSubmit":[h("user_prompt_submit.py")],
}}
cur = {}
if os.path.exists(path):
    try: cur = json.load(open(path))
    except Exception: cur = {}
cur.setdefault("permissions", {}).setdefault("deny", [])
for d in tpl["permissions"]["deny"]:
    if d not in cur["permissions"]["deny"]:
        cur["permissions"]["deny"].append(d)
cur.setdefault("hooks", {})
# idempotent re-merge: dedup theo BASENAME script (vd orca_guard.py), không theo chuỗi lệnh thô,
# để chạy lại NÂNG CẤP lệnh trần cũ thành lệnh có guard thay vì sinh hook trùng.
def script_of(command):
    m = re.search(r'([A-Za-z0-9_./-]+\.py)', command or "")
    return os.path.basename(m.group(1)) if m else None
for event, defs in tpl["hooks"].items():
    cur_defs = cur["hooks"].setdefault(event, [])
    tpl_scripts = {script_of(d["hooks"][0]["command"]) for d in defs}
    # bỏ entry cũ trỏ cùng script (lệnh trần) — sẽ thay bằng bản guard mới
    cur_defs[:] = [d for d in cur_defs
                   if not any(script_of(hh.get("command")) in tpl_scripts for hh in (d.get("hooks") or []))]
    cur_defs.extend(defs)
json.dump(cur, open(path, "w"), indent=2, ensure_ascii=False)
PY
grep -q "audit/" "$ROOT/.claude/.gitignore" 2>/dev/null || printf 'audit/\nsettings.json.bak.*\n' >> "$ROOT/.claude/.gitignore"
log "settings.json ở ROOT: OK (session mở tại root sẽ load hooks)"

# Presence-check: hook đã đăng ký nhưng THIẾU file → WARN (không fatal; lệnh đã fail-open guard).
for hook_py in pre_tool_use.py orca_guard.py post_tool_use.py stop.py session_end.py session_start.py user_prompt_submit.py; do
  [ -f "$ROOT/llmwiki/.claude/hooks/$hook_py" ] || warn "hook '$hook_py' đã đăng ký trong settings nhưng THIẾU file (fail-open: bỏ qua) — chạy '/sync-template --full' để tải về."
done

# ---------- 5. L2 pre-commit ----------
if [ ! -f "$ROOT/.pre-commit-config.yaml" ]; then
  cp "$SRC/.pre-commit-config.yaml" "$ROOT/.pre-commit-config.yaml"
  log "L2 .pre-commit-config.yaml: cài mới (kiểm tra prefix path nếu wiki không nằm ở llmwiki/wiki)"
else
  warn "L2 .pre-commit-config.yaml đã tồn tại — không đè; merge tay nếu cần (mẫu: $SRC/.pre-commit-config.yaml)"
fi
# [ -e ] chứ không phải [ -d ]: trong git worktree, .git là FILE trỏ về gitdir chính
if command -v pre-commit >/dev/null 2>&1 && [ -e "$ROOT/.git" ]; then
  # idempotent: hook đã trỏ pre-commit rồi thì khỏi install lại (re-run nhanh hơn)
  HOOK="$ROOT/.git/hooks/pre-commit"
  if [ -f "$HOOK" ] && grep -q "pre-commit" "$HOOK" 2>/dev/null; then
    log "pre-commit: đã cài (skip)"
  else
    (cd "$ROOT" && pre-commit install >/dev/null) && log "pre-commit install: OK"
  fi
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

# 6b. Pattern-sync health: sinh version.json nếu thiếu, rồi báo cáo (không chặn)
if [ -f "$ROOT/.template-manifest.json" ] && [ -f "$ROOT/harness/scripts/health-check.py" ]; then
  [ -f "$ROOT/harness/version.json" ] \
    || python3 "$ROOT/harness/scripts/health-check.py" --root "$ROOT" --update >/dev/null 2>&1 || true
  python3 "$ROOT/harness/scripts/health-check.py" --root "$ROOT" --branch orca || true
fi

# ---------- 6c. Self-heal (chỉ khi --self-heal) — installer tự trả nợ trong 1 process ----------
# Trigger dựa trên audit.py (gồm cả OKF), KHÔNG chỉ DEBT của mục 6 (origin+index).
# Nhờ vậy nợ OKF-only cũng được bắt. Backfill là THÊM, không sửa/xóa nội dung cũ.
if [ "$SELF_HEAL" = "1" ] && [ -f "$ROOT/harness/scripts/audit.py" ]; then
  if ! python3 "$ROOT/harness/scripts/audit.py" --wiki-dir "$WIKI" --root "$ROOT" >/dev/null 2>&1; then
    log "Self-heal: phát hiện nợ (Origin/index/OKF) → tự backfill trong 1 process..."
    python3 "$ROOT/harness/scripts/audit.py" --wiki-dir "$WIKI" --root "$ROOT" --fix || true
  fi
  if python3 "$ROOT/harness/scripts/audit.py" --wiki-dir "$WIKI" --root "$ROOT" >/dev/null 2>&1; then
    DEBT=0; log "Self-heal: wiki sạch (Origin + index + OKF) sau backfill."
  else
    DEBT=1; warn "Self-heal: còn nợ KHÔNG tự sửa được (cần user quyết):"
    python3 "$ROOT/harness/scripts/audit.py" --wiki-dir "$WIKI" --root "$ROOT" || true
  fi
fi

# ---------- 7. Kết luận ----------
{
  printf '\n## %s — install-harness — mode=%s\n' "$(date +%F)" "$MODE"
  printf -- '- Cài harness L0–L4 (validators, hooks, pre-commit, wiki-health, health-check, evals)\n'
  [ "$DEBT" = "1" ] && printf -- '- ⚠ CÓ NỢ wiki (thiếu Origin / index lệch) — backfill trước khi tin Stop hook\n'
} >> "$WIKI/log.md" 2>/dev/null || true

echo
if [ "$DEBT" = "1" ]; then
  warn "MIGRATE CÓ NỢ: sửa các vi phạm in phía trên TRƯỚC, rồi chạy lại script để xác nhận sạch."
  warn "Hooks đã cài nhưng phiên đụng wiki sẽ bị Stop hook nhắc cho tới khi index/Origin sạch."
  exit 3
fi
log "HOÀN TẤT — harness sạch. Tự kiểm hàng rào:"

# ---------- 8. Auto-smoke: 3 rule phải CHẶN được (exit 2 = PASS) ----------
V="$ROOT/harness/validators"
smoke() { # smoke <label> <validator> <json> — exit 2 là KỲ VỌNG, không để errexit giết
  local out rc=0
  out=$(printf '%s' "$3" | python3 "$V/$2" 2>&1) || rc=$?
  if [ "$rc" = "2" ]; then printf '  ⛔ %-38s → BỊ CHẶN ✓\n' "$1"
  else printf '  ✗ %-38s → KHÔNG CHẶN (rc=%s) — KIỂM TRA LẠI!\n' "$1" "$rc"; SMOKE_FAIL=1; fi
}
SMOKE_FAIL=0
echo "── Harness tự kiểm ─────────────────────────────────────"
smoke "Thử ghi llmwiki/raw/x.md (R1)"        no_write_raw.py     '{"action":"write","file_path":"llmwiki/raw/x.md"}'
smoke "Thử wiki file thiếu ## Origin (R2)"   origin_required.py  '{"action":"write","file_path":"llmwiki/wiki/concepts/x.md","content":"# x"}'
smoke "Thử file lạc wiki/ root (R5)"         folder_structure.py '{"action":"write","file_path":"llmwiki/wiki/rogue.md"}'
echo "────────────────────────────────────────────────────────"
if [ "$SMOKE_FAIL" = "0" ]; then
  log "Hệ thống đang cắn. Xem nó cắn trong PHIÊN THẬT: gọi skill /harness-tour (3 phút)"
  log "Hoặc xem máy diễn đủ 5 cảnh: bash harness/scripts/tour.sh"
else
  warn "Có rule không chặn được — kiểm tra python3 + harness/validators/"
  exit 4
fi
