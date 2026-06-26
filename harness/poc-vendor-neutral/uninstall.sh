#!/usr/bin/env bash
# uninstall.sh — GỠ PoC vendor-neutral harness khỏi 1 dự án (đảo ngược install.sh).
# Chỉ gỡ ĐÚNG phần harness đã thêm; giữ nguyên config khác của bạn.
#
# Usage:
#   bash uninstall.sh [project_root] [--keep-core] [--purge-bak]
#     --keep-core   giữ thư mục harness/poc-vendor-neutral/ (chỉ gỡ wiring)
#     --purge-bak   xoá luôn các file .bak mà install tạo ra
set -euo pipefail
ROOT="."; KEEPCORE=0; PURGE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --keep-core) KEEPCORE=1; shift;;
    --purge-bak) PURGE=1; shift;;
    -*) echo "tham số lạ: $1" >&2; exit 1;;
    *) ROOT="$1"; shift;;
  esac
done
ROOT="$(cd "$ROOT" && pwd)"
DEST="$ROOT/harness/poc-vendor-neutral"
log(){ printf '\033[1;32m[uninstall]\033[0m %s\n' "$*"; }
warn(){ printf '\033[1;33m[uninstall]\033[0m %s\n' "$*"; }

# 1. CI workflow
if [ -f "$ROOT/.github/workflows/harness.yml" ]; then rm -f "$ROOT/.github/workflows/harness.yml"; log "✓ gỡ CI (.github/workflows/harness.yml)"; fi

# 2. pre-commit: bỏ hook id=llmwiki-harness; rỗng repos → xoá file
PC="$ROOT/.pre-commit-config.yaml"
if [ -f "$PC" ] && grep -q 'llmwiki-harness' "$PC"; then
  python3 - "$PC" <<'PY' || warn "không gỡ được pre-commit tự động — sửa tay"
import sys,os
try: import yaml
except ImportError: sys.exit(1)
pc=sys.argv[1]; data=yaml.safe_load(open(pc,encoding='utf-8')) or {}
repos=[r for r in (data.get('repos') or []) if not any((h.get('id')=='llmwiki-harness') for h in (r.get('hooks') or []))]
if repos: data['repos']=repos; yaml.safe_dump(data,open(pc,'w',encoding='utf-8'),sort_keys=False,allow_unicode=True); print('  \033[1;32m✓\033[0m gỡ hook trong .pre-commit-config.yaml')
else: os.remove(pc); print('  \033[1;32m✓\033[0m xoá .pre-commit-config.yaml (chỉ có hook harness)')
PY
fi

# 3. Claude: bỏ hook nào gọi llmwiki-validate
SP="$ROOT/.claude/settings.json"
if [ -f "$SP" ] && grep -q 'llmwiki-validate' "$SP"; then
  python3 - "$SP" <<'PY'
import json,os,sys,shutil
sp=sys.argv[1]; shutil.copy(sp,sp+'.bak')
cur=json.load(open(sp,encoding='utf-8')); hk=cur.get('hooks',{})
for ev in list(hk):
    defs=[d for d in hk[ev] if not any('llmwiki-validate' in (h.get('command','')) for h in (d.get('hooks') or []))]
    if defs: hk[ev]=defs
    else: del hk[ev]
if not hk: cur.pop('hooks',None)
json.dump(cur,open(sp,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('  \033[1;32m✓\033[0m gỡ hook harness khỏi .claude/settings.json (backup .bak)')
PY
fi

# 4. opencode: bỏ đúng các glob deny mà harness thêm (đọc từ policy.yaml)
OJ="$ROOT/opencode.json"
if [ -f "$OJ" ] && grep -q '"deny"' "$OJ"; then
  python3 - "$OJ" "$DEST/policy.yaml" <<'PY'
import json,os,sys,shutil
oj,pol=sys.argv[1],sys.argv[2]
globs=[]
try:
    import yaml; p=yaml.safe_load(open(pol,encoding='utf-8'))
    for r in (p.get('rules') or {}).values():
        globs+= r.get('deny_write_globs',[]) or []
except Exception: globs=['**/raw/**','raw/**']   # fallback nếu core đã gỡ
cur=json.load(open(oj,encoding='utf-8'))
edit=(cur.get('permission') or {}).get('edit') or {}
removed=[g for g in globs if edit.get(g)=='deny']
for g in removed: del edit[g]
if removed:
    shutil.copy(oj,oj+'.bak')
    json.dump(cur,open(oj,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    print('  \033[1;32m✓\033[0m gỡ %d glob deny khỏi opencode.json (backup .bak)'%len(removed))
PY
fi

# 5. advisory
[ -f "$ROOT/.cursor/rules/harness.mdc" ] && { rm -f "$ROOT/.cursor/rules/harness.mdc"; log "✓ gỡ Cursor advisory"; }
[ -f "$ROOT/.kiro/steering/harness.md" ] && { rm -f "$ROOT/.kiro/steering/harness.md"; log "✓ gỡ Kiro advisory"; }
grep -ql 'llmwiki harness' "$ROOT/AGENTS.md" 2>/dev/null && warn "Codex: xoá khối 'Harness rules' trong AGENTS.md bằng tay (nếu đã thêm)"

# 6. lõi
if [ "$KEEPCORE" = 0 ] && [ -d "$DEST" ]; then rm -rf "$DEST"; rmdir "$ROOT/harness" 2>/dev/null || true; log "✓ xoá lõi harness/poc-vendor-neutral/"; else [ "$KEEPCORE" = 1 ] && log "· giữ lõi (--keep-core)" || true; fi

# 7. .bak
if [ "$PURGE" = 1 ]; then find "$ROOT" -name '*.bak' -maxdepth 4 -print -delete 2>/dev/null | sed 's/^/  xoá /' || true; fi

log "GỠ XONG. Claude: mở session mới để hook biến mất."
