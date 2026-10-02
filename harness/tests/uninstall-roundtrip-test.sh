#!/usr/bin/env bash
# uninstall-roundtrip-test — gỡ overstack khỏi một dự án downstream THẬT (cài bằng bootstrap qua file://) phải TẮT
# được harness, chỉ gỡ đúng phần installer thêm, và giữ dữ liệu của người dùng.
#
# Bối cảnh (đo 02/10/2026): uninstall.sh cũ chỉ biết layout harness/ và không gỡ con dấu .llmwiki/.harness-stamp —
# trong khi hook GLOBAL chạy theo con dấu → "gỡ xong" mà dự án vẫn bị gác. README hứa `bootstrap.sh … uninstall`
# nhưng bootstrap chuyển chữ đó thẳng cho install.sh.
#
# Kiểm bằng HÀNH VI chứ không chỉ bằng file: chạy chính lệnh hook PreToolUse đã đăng ký trong ~/.claude/settings.json
# (HOME sandbox) với payload ghi raw/ — trước khi gỡ phải rc=2 (chặn), sau khi gỡ phải rc=0 (không còn gác).
#
# Usage: bash harness/tests/uninstall-roundtrip-test.sh [repo-root]   (exit 0 = pass)
set -u
SRC="$(cd "${1:-.}" && pwd)"
fail=0
ok()  { printf '  \033[1;32m✓\033[0m %s\n' "$1"; }
bad() { printf '  \033[1;31m✗\033[0m %s\n' "$1"; fail=$((fail+1)); }
REAL_HOME="$HOME"
# shellcheck source=/dev/null
. "$SRC/harness/tests/downstream-fixture.sh"
make_downstream_fixture "$SRC" || { echo "fixture lỗi"; exit 1; }
trap 'export HOME="$REAL_HOME"; rm -rf "$FX_TMP"' EXIT

# Lệnh hook PreToolUse global (đã đăng ký vào $HOME sandbox) — chạy y như Claude Code gọi.
pretool_rc() {
  python3 - "$HOME/.claude/settings.json" "$FX/.claude/settings.json" <<'PY' > "$FX_TMP/pretool.cmds"
import json,os,sys
for p in sys.argv[1:]:                      # hook global + hook cấp dự án — Claude Code chạy cả hai
    if not os.path.exists(p): continue
    for g in json.load(open(p)).get("hooks",{}).get("PreToolUse",[]):
        if "Write" in (g.get("matcher") or ""):
            for h in g.get("hooks",[]): print(h["command"])
PY
  local rc=0 c
  while IFS= read -r c; do
    [ -n "$c" ] || continue
    printf '%s' '{"tool_name":"Write","tool_input":{"file_path":".llmwiki/raw/x.md","content":"x"}}' \
      | CLAUDE_PROJECT_DIR="$FX" bash -c "$c" >/dev/null 2>&1 || { r=$?; [ "$r" -gt "$rc" ] && rc=$r; }
  done < "$FX_TMP/pretool.cmds"
  echo "$rc"
}

echo "── trước khi gỡ (đã cài) ──"
[ -f "$FX/.llmwiki/.harness-stamp" ] && ok "có con dấu .llmwiki/.harness-stamp" || bad "fixture thiếu con dấu"
[ "$(pretool_rc)" = 2 ] && ok "hook global CHẶN ghi raw/ (rc=2)" || bad "hook global không chặn ghi raw/ ngay sau khi cài — fixture không đại diện"

# Dữ liệu + cấu hình của người dùng phải sống sót qua uninstall.
mkdir -p "$FX/.llmwiki/wiki/concepts"
printf -- '---\ntype: concept\n---\n# Tri thức của tôi\n## Origin\n- tôi\n' > "$FX/.llmwiki/wiki/concepts/my-note.md"
mkdir -p "$FX/.claude"
python3 - "$FX/.claude/settings.json" <<'PY'
import json,os,sys
p=sys.argv[1]; d=json.load(open(p)) if os.path.exists(p) else {}
d.setdefault("hooks",{}).setdefault("PreToolUse",[]).append({"matcher":"Bash","hooks":[{"type":"command","command":"echo user-own-hook"}]})
json.dump(d,open(p,"w"),indent=2)
PY

echo "── gỡ bằng đúng lệnh người dùng gõ (bootstrap … uninstall) ──"
( cd "$FX" && HARNESS_BASE="file://$SRC/harness/poc-vendor-neutral" bash "$SRC/harness/poc-vendor-neutral/bootstrap.sh" uninstall ) \
  >"$FX_TMP/uninstall.log" 2>&1 && ok "bootstrap uninstall rc=0" || bad "bootstrap uninstall lỗi — xem $FX_TMP/uninstall.log"
grep -q 'cài/update vào' "$FX_TMP/uninstall.log" && bad "bootstrap CÀI thay vì GỠ (chữ uninstall rơi vào install.sh)" || ok "bootstrap đi nhánh gỡ, không cài"

[ ! -f "$FX/.llmwiki/.harness-stamp" ] && ok "con dấu đã gỡ" || bad "con dấu .harness-stamp vẫn còn → hook global vẫn gác dự án"
[ "$(pretool_rc)" = 0 ] && ok "hook global KHÔNG còn chặn (rc=0) — harness đã tắt thật" || bad "sau khi gỡ hook global vẫn chặn"
[ ! -d "$FX/.harness/poc-vendor-neutral" ] && ok "lõi .harness/poc-vendor-neutral đã xoá" || bad "lõi .harness/poc-vendor-neutral còn"
if [ -f "$FX/.claude/settings.json" ]; then
  grep -q 'harness/poc-vendor-neutral/bin/' "$FX/.claude/settings.json" && bad ".claude/settings.json còn hook harness" || ok ".claude/settings.json hết hook harness"
  grep -q 'user-own-hook' "$FX/.claude/settings.json" && ok "hook của người dùng trong .claude/settings.json được giữ" || bad "uninstall xoá nhầm hook của người dùng"
fi
grep -qs 'llmwiki-validate\|poc-vendor-neutral' "$FX/.github/workflows/harness.yml" && bad "CI harness.yml còn" || ok "CI harness.yml đã gỡ"
grep -qs 'llmwiki-harness' "$FX/.pre-commit-config.yaml" && bad "pre-commit còn hook llmwiki-harness" || ok "pre-commit hết hook llmwiki-harness"
[ -f "$FX/.llmwiki/wiki/concepts/my-note.md" ] && ok "wiki của người dùng được GIỮ (mặc định)" || bad "uninstall mặc định đã xoá wiki của người dùng"

echo "── chạy lại (idempotent) ──"
bash "$SRC/harness/poc-vendor-neutral/uninstall.sh" "$FX" >"$FX_TMP/u2.log" 2>&1 && grep -q 'không có gì để gỡ' "$FX_TMP/u2.log" \
  && ok "gỡ lần hai: rc=0, báo không có gì để gỡ" || bad "gỡ lần hai lỗi hoặc không nhận ra đã sạch"

echo "── --purge-wiki ──"
bash "$SRC/harness/poc-vendor-neutral/uninstall.sh" "$FX" --purge-wiki >/dev/null 2>&1
[ ! -d "$FX/.llmwiki" ] && ok "--purge-wiki xoá .llmwiki/" || bad "--purge-wiki không xoá .llmwiki/"

echo "── chặn repo framework (trên repo GIẢ — không bao giờ chạy lên repo thật) ──"
# Bản uninstall cũ không có rào: chạy nhầm trong repo framework là xoá CI, sửa .claude/settings.json và xoá lõi
# (đo 02/10/2026 khi chạy test này với bản cũ). Nên phép thử dùng một thư mục giả dạng framework: rào hỏng thì
# chỉ thư mục giả bị phá, không phải checkout của người chạy test hay CI.
for kind in fdkwiki rolelabel; do
  DEC="$FX_TMP/decoy-$kind"; mkdir -p "$DEC/harness/poc-vendor-neutral" "$DEC/.github/workflows"
  printf 'core\n' > "$DEC/harness/poc-vendor-neutral/policy.yaml"; printf 'llmwiki-validate\n' > "$DEC/.github/workflows/harness.yml"
  if [ "$kind" = fdkwiki ]; then mkdir -p "$DEC/fdk/wiki"; else printf 'repo_role: framework\n' > "$DEC/.overstack.yaml"; fi
  bash "$SRC/harness/poc-vendor-neutral/uninstall.sh" "$DEC" >/dev/null 2>&1; rc=$?
  [ "$rc" = 2 ] && [ -f "$DEC/harness/poc-vendor-neutral/policy.yaml" ] && [ -f "$DEC/.github/workflows/harness.yml" ] \
    && ok "repo framework ($kind): từ chối (rc=2), không xoá gì" || bad "uninstall chạy được trong repo framework nhận theo $kind (rc=$rc)"
done

if [ "$fail" -eq 0 ]; then printf '\n\033[1m═══ uninstall-roundtrip: \033[1;32mPASS\033[0m\033[0m\n'; exit 0; fi
printf '\n\033[1m═══ uninstall-roundtrip: \033[1;31m%d VI PHẠM\033[0m\033[0m\n' "$fail"; exit 1
