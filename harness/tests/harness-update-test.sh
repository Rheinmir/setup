#!/usr/bin/env bash
# Kịch bản test cho /harness-update < 30s (T1-T4).
# Mỗi scenario chạy trong repo tạm cô lập. KHÔNG đụng repo thật.
set -uo pipefail

SRC="${1:?usage: harness-update-test.sh <repo-root>}"
INST="$SRC/harness/scripts/install-harness.sh"
AUDIT="$SRC/harness/scripts/audit.py"
PASS=0; FAIL=0; N=0
WORK="$(mktemp -d /tmp/hut.XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

ok()   { N=$((N+1)); PASS=$((PASS+1)); printf '  \033[1;32mPASS\033[0m  %s\n' "$1"; }
bad()  { N=$((N+1)); FAIL=$((FAIL+1)); printf '  \033[1;31mFAIL\033[0m  %s — %s\n' "$1" "$2"; }
hdr()  { printf '\n\033[1m── %s\033[0m\n' "$1"; }

# tạo legacy project có nợ: thiếu Origin + bold-meta (OKF) + index lệch
seed_debt() {
  local d="$1"; mkdir -p "$d/llmwiki/wiki/concepts"
  printf '# Alpha\n\nNoi dung alpha thieu Origin va OKF.\n' > "$d/llmwiki/wiki/concepts/alpha.md"
  printf '# Beta\n\n**Type:** concept\n\nNoi dung beta bold-meta.\n' > "$d/llmwiki/wiki/concepts/beta.md"
  printf '# Wiki Index\n\n| File | Type | Summary |\n|------|------|---------|\n' > "$d/llmwiki/wiki/index.md"
  printf '# Operation Log\n' > "$d/llmwiki/wiki/log.md"
  ( cd "$d" && git init -q && git config user.email t@t.t && git config user.name t && git add -A && git commit -qm seed >/dev/null )
}
timed() { python3 -c 'import subprocess,sys,time; t=time.time(); p=subprocess.run(sys.argv[1:],capture_output=True,text=True); sys.stderr.write(p.stdout+p.stderr); print("%.3f %d"%(time.time()-t,p.returncode))' "$@"; }

# ============================================================
hdr "S0 — syntax + audit.py parity"
if bash -n "$INST"; then ok "install-harness.sh cú pháp hợp lệ"; else bad "syntax" "bash -n fail"; fi

# parity: audit.py phát hiện nợ KHỚP từng validator gốc, trên 1 seed
P0="$WORK/parity"; seed_debt "$P0"
J=$(python3 "$AUDIT" --wiki-dir "$P0/llmwiki/wiki" --json 2>/dev/null)
mo=$(echo "$J" | python3 -c 'import sys,json;print(len(json.load(sys.stdin)["missing_origin"]))')
ob=$(echo "$J" | python3 -c 'import sys,json;print(len(json.load(sys.stdin)["okf_bad"]))')
im=$(echo "$J" | python3 -c 'import sys,json;print(len(json.load(sys.stdin)["index_missing"]))')
# validator gốc: origin (alpha thiếu), okf (alpha+beta), index (alpha+beta thiếu)
# alpha + beta đều thiếu '## Origin' (beta có **Type:** nhưng không có Origin) → 2
[ "$mo" = "2" ] && ok "audit missing_origin=2 khớp R2 (alpha+beta)" || bad "parity origin" "got $mo, expect 2"
[ "$ob" = "2" ] && ok "audit okf_bad=2 khớp R9" || bad "parity okf" "got $ob, expect 2"
[ "$im" = "2" ] && ok "audit index_missing=2 khớp R3" || bad "parity index" "got $im, expect 2"

# ============================================================
hdr "S1 — migrate CÓ NỢ + --self-heal (< 30s, rc=0, backfill đúng)"
D1="$WORK/s1"; seed_debt "$D1"
ALPHA_BEFORE=$(cat "$D1/llmwiki/wiki/concepts/alpha.md")
read t rc < <(timed bash "$INST" "$D1" --self-heal 2>"$D1/.out")
awk_lt() { python3 -c "import sys;sys.exit(0 if float('$1')<$2 else 1)"; }
awk_lt "$t" 30 && ok "wall-clock ${t}s < 30s" || bad "tốc độ" "${t}s >= 30s"
[ "$rc" = "0" ] && ok "exit 0 (sạch sau self-heal)" || bad "exit code" "rc=$rc, expect 0"
grep -q "backfill xong — Origin:2 index:2 OKF:2" "$D1/.out" && ok "backfill đếm đúng Origin:2 index:2 OKF:2" || bad "backfill count" "$(grep 'backfill xong' "$D1/.out" || echo 'không thấy dòng backfill')"
[ "$(grep -c 'BỊ CHẶN ✓' "$D1/.out")" = "3" ] && ok "smoke ⛔×3 sau self-heal" || bad "smoke" "không đủ 3 BỊ CHẶN"
# re-audit sạch
python3 "$AUDIT" --wiki-dir "$D1/llmwiki/wiki" >/dev/null 2>&1 && ok "audit lại = sạch (rc=0)" || bad "residual" "vẫn còn nợ"

# ============================================================
hdr "S2 — backfill là THÊM, KHÔNG sửa nội dung cũ"
ALPHA_AFTER=$(cat "$D1/llmwiki/wiki/concepts/alpha.md")
# nội dung gốc 'Noi dung alpha...' phải còn nguyên; chỉ thêm frontmatter + Origin
echo "$ALPHA_AFTER" | grep -q "Noi dung alpha thieu Origin va OKF." && ok "body gốc còn nguyên" || bad "body" "nội dung cũ bị đổi"
echo "$ALPHA_AFTER" | grep -q "^## Origin" && ok "Origin được THÊM" || bad "origin" "không thêm Origin"
echo "$ALPHA_AFTER" | grep -qE "commit gần nhất: [0-9a-f]{7,} 20" && ok "Origin có hash+date git thật (batched git log)" || bad "git hash" "không có hash thật"
echo "$ALPHA_AFTER" | head -1 | grep -q "^---$" && ok "OKF frontmatter được THÊM ở đầu" || bad "okf" "không có frontmatter"

# ============================================================
hdr "S3 — idempotent: re-run sạch < 5s + skip pre-commit"
read t2 rc2 < <(timed bash "$INST" "$D1" --self-heal 2>"$D1/.out2")
awk_lt "$t2" 5 && ok "re-run ${t2}s < 5s" || bad "idempotent tốc độ" "${t2}s >= 5s"
[ "$rc2" = "0" ] && ok "re-run rc=0" || bad "re-run exit" "rc=$rc2"
if command -v pre-commit >/dev/null 2>&1; then
  grep -q "pre-commit: đã cài (skip)" "$D1/.out2" && ok "skip pre-commit install lần 2" || bad "pre-commit skip" "vẫn install lại"
else
  ok "pre-commit chưa cài trên máy → bỏ qua test skip (n/a)"
fi
# self-heal lần 2 không backfill gì thêm (đã sạch)
grep -q "wiki sạch (Origin + index + OKF) sau backfill" "$D1/.out2" && ok "re-run: báo wiki sạch, không backfill thừa" || ok "re-run: không có nợ để backfill"

# ============================================================
hdr "S4 — backward-compat: KHÔNG cờ --self-heal trên repo có nợ → rc=3 (hành vi cũ)"
D4="$WORK/s4"; seed_debt "$D4"
read t4 rc4 < <(timed bash "$INST" "$D4" 2>"$D4/.out")
[ "$rc4" = "3" ] && ok "không cờ → exit 3 (giữ hành vi cũ)" || bad "backward-compat" "rc=$rc4, expect 3"
! grep -q "backfill xong" "$D4/.out" && ok "không cờ → KHÔNG tự backfill (đúng)" || bad "no-flag backfill" "tự backfill khi không có cờ"

# ============================================================
hdr "S5 — --no-clone fast-fail (không treo mạng)"
ISO="$WORK/iso"; mkdir -p "$ISO/harness/scripts"; cp "$INST" "$ISO/harness/scripts/"
TGT="$WORK/s5"; mkdir -p "$TGT/llmwiki/wiki/concepts"
read t5 rc5 < <(timed bash "$ISO/harness/scripts/install-harness.sh" "$TGT" --no-clone 2>"$TGT/.out")
[ "$rc5" = "1" ] && ok "--no-clone bundle thiếu → exit 1" || bad "no-clone rc" "rc=$rc5, expect 1"
awk_lt "$t5" 3 && ok "fast-fail ${t5}s < 3s (không treo)" || bad "no-clone tốc độ" "${t5}s — có vẻ treo"
grep -q "fast-fail (không treo mạng)" "$TGT/.out" && ok "có thông báo fast-fail rõ ràng" || bad "no-clone msg" "thiếu thông báo"

# ============================================================
hdr "S6 — OKF-only debt: self-heal vẫn bắt (không phụ thuộc DEBG mục 6)"
D6="$WORK/s6"; mkdir -p "$D6/llmwiki/wiki/concepts"
# file CÓ Origin + CÓ trong index nhưng THIẾU OKF frontmatter (bold) → chỉ nợ OKF
printf '# Gamma\n\n**Type:** concept\n\nBody gamma.\n\n## Origin\n- seed\n' > "$D6/llmwiki/wiki/concepts/gamma.md"
printf '# Wiki Index\n\n| File | Type | Summary |\n|------|------|---------|\n| [gamma](concepts/gamma.md) | concept | Gamma |\n' > "$D6/llmwiki/wiki/index.md"
printf '# Operation Log\n' > "$D6/llmwiki/wiki/log.md"
( cd "$D6" && git init -q && git config user.email t@t.t && git config user.name t && git add -A && git commit -qm seed >/dev/null )
read t6 rc6 < <(timed bash "$INST" "$D6" --self-heal 2>"$D6/.out")
[ "$rc6" = "0" ] && ok "OKF-only: self-heal → rc=0 sạch" || bad "okf-only rc" "rc=$rc6"
grep -q "Origin:0 index:0 OKF:1" "$D6/.out" && ok "OKF-only: chỉ migrate OKF (Origin:0 index:0 OKF:1)" || bad "okf-only count" "$(grep 'backfill xong' "$D6/.out")"
head -1 "$D6/llmwiki/wiki/concepts/gamma.md" | grep -q "^---$" && ok "gamma.md có OKF frontmatter sau migrate" || bad "okf migrate" "không migrate"
grep -q "^## Origin" "$D6/llmwiki/wiki/concepts/gamma.md" && ok "Origin gốc còn nguyên (không nhân đôi)" || bad "origin preserve" "mất Origin"

# ============================================================
hdr "S7 — index STALE (file bị xoá) — detect (self-heal không tự xoá row)"
D7="$WORK/s7"; seed_debt "$D7"
# thêm row index trỏ file không tồn tại
printf '| [ghost](concepts/ghost.md) | concept | Ghost |\n' >> "$D7/llmwiki/wiki/index.md"
JS=$(python3 "$AUDIT" --wiki-dir "$D7/llmwiki/wiki" --json 2>/dev/null)
st=$(echo "$JS" | python3 -c 'import sys,json;print(len(json.load(sys.stdin)["index_stale"]))')
[ "$st" = "1" ] && ok "audit phát hiện index_stale=1 (ghost.md)" || bad "stale detect" "got $st"

# ============================================================
hdr "S8 — file CHƯA commit → Origin ghi 'chưa commit' (không vỡ)"
D8="$WORK/s8"; seed_debt "$D8"
printf '# Delta\n\nBody delta chua commit.\n' > "$D8/llmwiki/wiki/concepts/delta.md"  # KHÔNG add/commit
read t8 rc8 < <(timed bash "$INST" "$D8" --self-heal 2>"$D8/.out")
[ "$rc8" = "0" ] && ok "có file uncommitted → vẫn rc=0" || bad "uncommitted rc" "rc=$rc8"
grep -q "commit gần nhất: chưa commit" "$D8/llmwiki/wiki/concepts/delta.md" && ok "file chưa commit → Origin 'chưa commit'" || bad "uncommitted origin" "$(grep -A1 Origin "$D8/llmwiki/wiki/concepts/delta.md" | tail -1)"

# ============================================================
hdr "S9 — combo --self-heal --no-clone (bundle CÓ → vẫn chạy đủ)"
D9="$WORK/s9"; seed_debt "$D9"
read t9 rc9 < <(timed bash "$INST" "$D9" --self-heal --no-clone 2>"$D9/.out")
[ "$rc9" = "0" ] && ok "combo 2 cờ + bundle có → rc=0" || bad "combo rc" "rc=$rc9"
grep -q "backfill xong" "$D9/.out" && ok "combo: self-heal vẫn backfill" || bad "combo backfill" "không backfill"

# ============================================================
printf '\n\033[1m═══ TỔNG: %d test — \033[1;32m%d PASS\033[0m / \033[1;31m%d FAIL\033[0m\n' "$N" "$PASS" "$FAIL"
[ "$FAIL" = "0" ] && exit 0 || exit 1
