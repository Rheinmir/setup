#!/usr/bin/env bash
# uninstall.sh — GỠ overstack harness khỏi 1 dự án (đảo ngược install.sh). Hiểu cả layout dot (.llmwiki/ + .harness/,
# chuẩn v4) lẫn layout cũ (llmwiki/ + harness/). Chỉ gỡ ĐÚNG phần installer đã thêm; giữ nguyên config khác của bạn.
#
#   curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash -s -- uninstall
#   bash uninstall.sh [project_root] [--keep-core] [--purge-wiki] [--purge-bak]
#
#     --keep-core   giữ thư mục <harness>/poc-vendor-neutral/ (chỉ gỡ wiring + con dấu)
#     --purge-wiki  xoá LUÔN thư mục wiki (.llmwiki/ hoặc llmwiki/) — mặc định GIỮ, vì đó là tri thức của bạn
#     --purge-bak   xoá các file .bak mà install/uninstall tạo ra
#
# Mặc định giữ wiki: gỡ con dấu .harness-stamp là đủ tắt harness — hook global (~/.claude/settings.json) chỉ chạy
# khi dự án CÓ con dấu, nên wiki còn nằm đó cũng không bị gác nữa. Bản cũ của script này không gỡ con dấu và chỉ
# biết layout harness/ → "gỡ xong" mà hook global vẫn chạy trong dự án (đo 02/10/2026).
# Engine global ~/.claude/harness KHÔNG bị gỡ: nó dùng chung cho mọi dự án khác trên máy.
set -euo pipefail
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
ROOT="."; KEEPCORE=0; PURGE=0; PURGEWIKI=0
while [ $# -gt 0 ]; do
  case "$1" in
    --keep-core) KEEPCORE=1; shift;;
    --purge-wiki) PURGEWIKI=1; shift;;
    --purge-bak) PURGE=1; shift;;
    -h|--help) sed -n '2,16p' "$0"; exit 0;;
    -*) echo "tham số lạ: $1" >&2; exit 1;;
    *) ROOT="$1"; shift;;
  esac
done
ROOT="$(cd "$ROOT" && pwd)"
log(){ printf '\033[1;32m[uninstall]\033[0m %s\n' "$*"; }
warn(){ printf '\033[1;33m[uninstall]\033[0m %s\n' "$*"; }

# 0. Không bao giờ gỡ trong REPO FRAMEWORK — cùng nhận diện với install.sh (nhãn repo_role thắng, thiếu nhãn thì fdk/wiki).
ROLE_DECL="$( { sed -nE "s/^repo_role:[[:space:]]*[\"']?([A-Za-z_-]+).*/\1/p" "$ROOT/.overstack.yaml" 2>/dev/null || true; } | head -1)"
if [ "$ROLE_DECL" = "framework" ] || { [ -z "$ROLE_DECL" ] && [ -d "$ROOT/fdk/wiki" ]; }; then
  printf '\033[1;31m[uninstall]\033[0m DỪNG — %s là REPO FRAMEWORK, không phải dự án đã cài. Chưa gỡ gì cả.\n' "$ROOT" >&2
  exit 2
fi

FOUND=0
# 1. Con dấu — công tắc của hook global. Gỡ TRƯỚC: kể cả các bước sau lỗi giữa chừng, harness đã tắt trong dự án.
for d in .llmwiki llmwiki; do
  if [ -f "$ROOT/$d/.harness-stamp" ]; then rm -f "$ROOT/$d/.harness-stamp"; FOUND=1; log "✓ gỡ con dấu $d/.harness-stamp (hook global không chạy ở dự án này nữa)"; fi
done

# Lõi theo layout: .harness/ (v4) trước, harness/ (cũ) sau.
DEST=""
for d in .harness harness; do [ -d "$ROOT/$d/poc-vendor-neutral" ] && { DEST="$ROOT/$d/poc-vendor-neutral"; break; }; done

# 2. CI workflow — chỉ xoá khi đúng là file installer sinh (nhận theo nội dung, không theo tên).
CI="$ROOT/.github/workflows/harness.yml"
if [ -f "$CI" ] && grep -qE 'llmwiki-validate|poc-vendor-neutral' "$CI"; then
  rm -f "$CI"; FOUND=1; log "✓ gỡ CI (.github/workflows/harness.yml)"
  rmdir "$ROOT/.github/workflows" "$ROOT/.github" 2>/dev/null || true
fi

# 3. pre-commit: bỏ hook id=llmwiki-harness; còn rỗng repos → xoá file.
PC="$ROOT/.pre-commit-config.yaml"
if [ -f "$PC" ] && grep -q 'llmwiki-harness' "$PC"; then
  FOUND=1
  python3 - "$PC" <<'PY' || warn "không gỡ được pre-commit tự động (thiếu pyyaml?) — xoá tay khối id=llmwiki-harness"
import sys,os
import yaml
pc=sys.argv[1]; data=yaml.safe_load(open(pc,encoding='utf-8')) or {}
repos=[]
for r in (data.get('repos') or []):
    hooks=[h for h in (r.get('hooks') or []) if h.get('id')!='llmwiki-harness']
    if hooks: r['hooks']=hooks; repos.append(r)
if repos: data['repos']=repos; yaml.safe_dump(data,open(pc,'w',encoding='utf-8'),sort_keys=False,allow_unicode=True); print('  \033[1;32m✓\033[0m gỡ hook llmwiki-harness trong .pre-commit-config.yaml')
else: os.remove(pc); print('  \033[1;32m✓\033[0m xoá .pre-commit-config.yaml (chỉ có hook harness)')
PY
fi

# 4. Claude / OpenClaude: bỏ đúng hook installer đã thêm — CÙNG dấu nhận diện với merge_claude_hooks của install.sh,
#    nên hook của chính bạn trong cùng file được giữ nguyên. Chỉ ghi (và backup) khi có thay đổi.
for sub in .claude .openclaude; do
  SP="$ROOT/$sub/settings.json"
  [ -f "$SP" ] && grep -q 'harness/poc-vendor-neutral/bin/' "$SP" || continue
  FOUND=1
  python3 - "$SP" "$sub" <<'PY'
import json,shutil,sys
sp,sub=sys.argv[1],sys.argv[2]; MARK='harness/poc-vendor-neutral/bin/'
cur=json.load(open(sp,encoding='utf-8')); hk=cur.get('hooks') or {}; n=0
for ev in list(hk):
    keep=[]
    for d in hk[ev]:
        hs=[h for h in (d.get('hooks') or []) if MARK not in (h.get('command') or '')]
        n+=len(d.get('hooks') or [])-len(hs)
        if hs: d['hooks']=hs; keep.append(d)
    if keep: hk[ev]=keep
    else: del hk[ev]
if not hk: cur.pop('hooks',None)
shutil.copy(sp,sp+'.bak'); json.dump(cur,open(sp,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print(f'  \033[1;32m✓\033[0m gỡ {n} hook harness khỏi {sub}/settings.json (backup .bak)')
PY
done

# 5. opencode: bỏ đúng các glob deny harness thêm (đọc policy.yaml TRƯỚC khi xoá lõi).
OJ="$ROOT/opencode.json"
if [ -f "$OJ" ] && grep -q '"deny"' "$OJ"; then
  python3 - "$OJ" "${DEST:+$DEST/policy.yaml}" <<'PY'
import json,shutil,sys
oj,pol=sys.argv[1],(sys.argv[2] if len(sys.argv)>2 else '')
globs=[]
try:
    import yaml; p=yaml.safe_load(open(pol,encoding='utf-8'))
    for r in (p.get('rules') or {}).values(): globs+=r.get('deny_write_globs',[]) or []
except Exception: globs=['**/raw/**','raw/**']   # lõi đã gỡ / thiếu pyyaml
cur=json.load(open(oj,encoding='utf-8')); edit=(cur.get('permission') or {}).get('edit') or {}
removed=[g for g in globs if edit.get(g)=='deny']
for g in removed: del edit[g]
if removed:
    shutil.copy(oj,oj+'.bak'); json.dump(cur,open(oj,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    print('  \033[1;32m✓\033[0m gỡ %d glob deny khỏi opencode.json (backup .bak)'%len(removed))
PY
fi

# 6. advisory
[ -f "$ROOT/.cursor/rules/harness.mdc" ] && { rm -f "$ROOT/.cursor/rules/harness.mdc"; FOUND=1; log "✓ gỡ Cursor advisory"; }
[ -f "$ROOT/.kiro/steering/harness.md" ] && { rm -f "$ROOT/.kiro/steering/harness.md"; FOUND=1; log "✓ gỡ Kiro advisory"; }
grep -ql 'llmwiki harness' "$ROOT/AGENTS.md" 2>/dev/null && warn "Codex: xoá khối 'Harness rules' trong AGENTS.md bằng tay (nếu đã thêm)"

# 7. lõi (giữ file khác trong cùng thư mục, vd .harness/foundation.yaml do bạn điền)
if [ -n "$DEST" ]; then
  FOUND=1
  if [ "$KEEPCORE" = 1 ]; then log "· giữ lõi $(basename "$(dirname "$DEST")")/poc-vendor-neutral (--keep-core)"
  else rm -rf "$DEST"; rmdir "$(dirname "$DEST")" 2>/dev/null || true; log "✓ xoá lõi $(basename "$(dirname "$DEST")")/poc-vendor-neutral/"; fi
fi

# 8. wiki — dữ liệu của bạn: chỉ xoá khi được yêu cầu rõ.
for d in .llmwiki llmwiki; do
  [ -d "$ROOT/$d" ] || continue
  if [ "$PURGEWIKI" = 1 ]; then rm -rf "${ROOT:?}/$d"; log "✓ xoá wiki $d/ (--purge-wiki)"
  else log "· giữ wiki $d/ (tri thức của bạn — xoá kèm: thêm --purge-wiki)"; fi
done

# 9. .bak
if [ "$PURGE" = 1 ]; then find "$ROOT" -maxdepth 4 -name '*.bak' -print -delete 2>/dev/null | sed 's/^/  xoá /' || true; fi

if [ "$FOUND" = 0 ]; then warn "không thấy dấu vết harness ở $ROOT — không có gì để gỡ."; exit 0; fi
log "GỠ XONG. Mở phiên agent mới để hook cũ được nạp lại. Engine global ~/.claude/harness vẫn giữ cho các dự án khác."
