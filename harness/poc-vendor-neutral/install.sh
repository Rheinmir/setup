#!/usr/bin/env bash
# install.sh — cài PoC vendor-neutral harness vào 1 dự án bằng MỘT lệnh (luồng B0–B4).
#
# Usage:
#   bash install.sh [project_root] [--vendor claude,opencode,cursor,codex,kiro] [--no-verify]
#
#   project_root  thư mục dự án đích (mặc định: thư mục hiện tại)
#   --vendor      ép danh sách vendor; bỏ qua → tự DÒ (.claude/ · opencode.json · .cursor/ · .kiro/ · .codex)
#   --no-verify   bỏ bước chạy demo.sh + test-broad.sh
#
# Idempotent. CI + pre-commit luôn cài (sàn đảm bảo); adapter chỉ cài cho vendor có mặt.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # nguồn = poc-vendor-neutral/
ROOT="."; VENDORS=""; VERIFY=1; CLEAN=0; WITH_SKILLS=0
while [ $# -gt 0 ]; do
  case "$1" in
    --vendor) VENDORS="${2:-}"; shift 2;;
    --no-verify) VERIFY=0; shift;;
    --clean) CLEAN=1; shift;;
    --with-skills) WITH_SKILLS=1; shift;;
    -*) echo "tham số lạ: $1" >&2; exit 1;;
    *) ROOT="$1"; shift;;
  esac
done
ROOT="$(cd "$ROOT" && pwd)"
DEST="$ROOT/harness/poc-vendor-neutral"; OUT="$DEST/out"
log(){ printf '\033[1;32m[install]\033[0m %s\n' "$*"; }
warn(){ printf '\033[1;33m[install]\033[0m %s\n' "$*"; }
has(){ case ",$VENDORS," in *",$1,"*) return 0;; *) return 1;; esac; }

# --clean: gỡ bản cũ trước khi cài (cài mới sạch). Cần uninstall.sh cạnh script.
if [ "$CLEAN" = 1 ] && [ -f "$SRC/uninstall.sh" ]; then
  log "--clean → gỡ bản cũ trước"
  bash "$SRC/uninstall.sh" "$ROOT" || warn "uninstall gặp lỗi, vẫn cài tiếp"
fi

# ── B0. Copy lõi vào dự án ──
log "B0 · copy lõi → $DEST"
mkdir -p "$DEST/bin"
if [ "$(cd "$SRC" && pwd -P)" != "$(cd "$DEST" && pwd -P)" ]; then
  cp "$SRC/policy.yaml" "$SRC/gen-converters.py" "$SRC/demo.sh" "$SRC/test-broad.sh" "$DEST/"
  cp "$SRC/bin/"*.py "$DEST/bin/"
  for f in install.sh uninstall.sh bootstrap.sh README.md DOCS.md; do [ -f "$SRC/$f" ] && cp "$SRC/$f" "$DEST/"; done
else
  log "  · lõi đã ở đúng chỗ (SRC=DEST), bỏ qua copy"
fi
printf 'out/\n' > "$DEST/.gitignore"
chmod +x "$DEST/bin/"*.py "$DEST/gen-converters.py" "$DEST"/*.sh 2>/dev/null || true
python3 -c 'import yaml' 2>/dev/null || { warn "thiếu pyyaml → thử pip install"; pip3 install --quiet pyyaml 2>/dev/null || warn "không cài được pyyaml — lõi sẽ fail-open tới khi có pyyaml"; }

# ── B1. Dò vendor ──
if [ -z "$VENDORS" ]; then
  det=""
  [ -d "$ROOT/.claude" ] && det="${det}claude,"
  { [ -f "$ROOT/opencode.json" ] || [ -d "$ROOT/.opencode" ]; } && det="${det}opencode,"
  [ -d "$ROOT/.cursor" ] && det="${det}cursor,"
  { [ -f "$ROOT/AGENTS.md" ] || [ -d "$ROOT/.codex" ]; } && det="${det}codex,"
  [ -d "$ROOT/.kiro" ] && det="${det}kiro,"
  VENDORS="${det%,}"
fi
log "B1 · vendor: ${VENDORS:-(không thấy — chỉ cài CI + pre-commit)}"

# ── B2. Sinh wiring từ policy ──
log "B2 · gen-converters → out/"
( cd "$DEST" && python3 gen-converters.py >/dev/null )

# ── B3. Cắm wiring ──
log "B3 · cắm wiring"
# CI (sàn, luôn cài)
mkdir -p "$ROOT/.github/workflows"
cp "$OUT/ci/harness.yml" "$ROOT/.github/workflows/harness.yml"
log "  ✓ CI       → .github/workflows/harness.yml"
# pre-commit (sàn)
PC="$ROOT/.pre-commit-config.yaml"
if [ ! -f "$PC" ]; then
  cat > "$PC" <<'YML'
repos:
  - repo: local
    hooks:
      - id: llmwiki-harness
        name: llmwiki harness validator (layer=repo)
        entry: python3 harness/poc-vendor-neutral/bin/llmwiki-validate.py files
        language: system
        files: '\.md$'
YML
  log "  ✓ pre-commit → .pre-commit-config.yaml (tạo mới)"
elif grep -q 'llmwiki-harness' "$PC"; then
  log "  · pre-commit → đã có hook llmwiki-harness, bỏ qua"
else
  warn "  pre-commit đã tồn tại → thêm tay khối repo:local id=llmwiki-harness (xem out/pre-commit-snippet.yaml)"
fi
# Claude (merge hooks vào settings.json)
if has claude; then
  python3 - "$ROOT" "$OUT/claude/settings.snippet.json" <<'PY'
import json,os,sys,shutil
root,snip=sys.argv[1],sys.argv[2]
sp=os.path.join(root,'.claude','settings.json')
os.makedirs(os.path.dirname(sp),exist_ok=True)
cur=json.load(open(sp,encoding='utf-8')) if os.path.exists(sp) else {}
if os.path.exists(sp): shutil.copy(sp, sp+'.bak')
add=json.load(open(snip,encoding='utf-8'))
cur.setdefault('hooks',{})
for ev,entries in add.get('hooks',{}).items():
    defs=cur['hooks'].setdefault(ev,[])
    existing={h.get('command') for d in defs for h in (d.get('hooks') or [])}
    for d in entries:
        cmds={h.get('command') for h in (d.get('hooks') or [])}
        if cmds & existing: continue
        defs.append(d)
json.dump(cur,open(sp,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('  \033[1;32m✓\033[0m Claude   → .claude/settings.json (merged, backup .bak)')
PY
fi
# opencode (permission.edit native — merge tự động)
if has opencode; then
  python3 - "$ROOT" "$OUT/opencode/opencode.json" <<'PY'
import json,os,sys,shutil
root,snip=sys.argv[1],sys.argv[2]
op=os.path.join(root,'opencode.json')
cur=json.load(open(op,encoding='utf-8')) if os.path.exists(op) else {}
if os.path.exists(op): shutil.copy(op,op+'.bak')
add=json.load(open(snip,encoding='utf-8'))
perm=cur.get('permission')
if not isinstance(perm,dict): perm={}
edit=perm.get('edit')
if not isinstance(edit,dict): edit={}
for k,v in add.get('permission',{}).get('edit',{}).items():
    if k=='*': edit.setdefault(k,v)     # giữ default của user nếu đã có
    else: edit[k]=v                      # luôn áp glob deny của harness
perm['edit']=edit; cur['permission']=perm
cur.setdefault('$schema', add.get('$schema','https://opencode.ai/config.json'))
json.dump(cur,open(op,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('  \033[1;32m✓\033[0m opencode → opencode.json (merged permission.edit, backup .bak)')
PY
fi
# advisory (nhắc — dựa CI là chính)
if has cursor; then mkdir -p "$ROOT/.cursor/rules"; cp "$OUT/cursor/.cursor/rules/harness.mdc" "$ROOT/.cursor/rules/"; log "  ✓ Cursor   → .cursor/rules/harness.mdc (advisory)"; fi
if has kiro;   then mkdir -p "$ROOT/.kiro/steering"; cp "$OUT/kiro/.kiro/steering/harness.md" "$ROOT/.kiro/steering/"; log "  ✓ Kiro     → .kiro/steering/harness.md (advisory)"; fi
if has codex;  then warn "  Codex → thêm nội dung out/codex/AGENTS.snippet.md vào AGENTS.md (advisory)"; fi

# ── B4. Verify ──
if [ "$VERIFY" = 1 ]; then
  log "B4 · verify"
  if bash "$DEST/demo.sh" >/dev/null 2>&1; then log "  ✓ demo.sh (13)"; else warn "  demo.sh FAIL — kiểm pyyaml"; fi
  if bash "$DEST/test-broad.sh" >/dev/null 2>&1; then log "  ✓ test-broad.sh (54)"; else warn "  test-broad.sh FAIL"; fi
fi

# ── (tùy chọn) cài skill llmwiki (GLOBAL — khác phạm vi với harness theo-project) ──
if [ "$WITH_SKILLS" = 1 ]; then
  log "+ cài bộ skill llmwiki (global, qua npx skills)"
  if command -v npx >/dev/null; then
    npx -y skills add rheinmir/setup#orca --global --all 2>&1 | tail -4 | sed 's/^/    /' \
      || warn "  cài skill lỗi — chạy tay: npx skills add rheinmir/setup#orca --global --all"
  else
    warn "  không có npx — cài skill tay: npx skills add rheinmir/setup#orca --global --all"
  fi
fi

log "HOÀN TẤT."
[ "$WITH_SKILLS" = 1 ] && echo "   • Skill cài GLOBAL (~/.claude/skills) — dùng cho mọi project, khác với harness (theo từng project)."
echo "   • Claude: mở session mới (hoặc /hooks reload) để hook có hiệu lực."
echo "   • CI chạy khi push lên GitHub. Sửa luật: harness/poc-vendor-neutral/policy.yaml → chạy lại install.sh (hoặc gen-converters.py)."
