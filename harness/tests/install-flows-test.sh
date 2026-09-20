#!/usr/bin/env bash
# install-flows-test — MỖI Ô của bảng luồng cài/cập nhật (fdk/wiki/concepts/install-update-flows.md) là một ca chạy được.
# Sinh ra vì 20/09/2026 tôi chỉ test đường `curl bootstrap` rồi báo xong, trong khi các đường khác hỏng mà không cổng nào thấy.
#   A3  bootstrap --harness-only      → module vẫn được kéo, launcher chạy
#   A7  install-harness.sh --global   → shim VÀ engine tới cùng chuyến;  A7s: ORCA_GRAPH_SKIP=1 → shim báo lệnh cài (rc 3)
#   B1  máy còn engine v2 (trước khi tách repo) chạy lại bootstrap → shim + engine v3, graph đang dở vẫn đọc được
#   B3  /harness-update kiểu cũ (`install-harness.sh . --self-heal`) trên dự án dot-layout → DỪNG rc 5, không chép engine vào dự án
#   C1  chạy installer trong REPO FRAMEWORK (khai nhãn / suy theo fdk/wiki) → DỪNG rc 3, 0 file đổi; ép cờ thì chạy
# Gọi từng ca: install-flows-test.sh B3 C1 · không tham số = mọi ca. Kín mạng (engine lấy từ bản cài local), HOME cô lập, không daemon.
set -uo pipefail
SRC="$(cd "$(dirname "$0")/../.." && pwd)"
OG_SRC="$(cd "${ORCA_GRAPH_REPO:-$HOME/.orca-graph/repo}" 2>/dev/null && pwd -P || true)"
[ -n "$OG_SRC" ] && [ -f "$OG_SRC/install.sh" ] && git -C "$OG_SRC" rev-parse --git-dir >/dev/null 2>&1 \
  || { echo "SKIP: không có bản orca-graph local làm nguồn (cài: install.sh của Rheinmir/orca-graph)"; exit 0; }
[ -z "$(git -C "$OG_SRC" status --porcelain)" ] || echo "⚠ $OG_SRC có thay đổi chưa commit — các ca chỉ thấy HEAD của engine"
export ORCA_GRAPH_REPO="$OG_SRC" ORCA_GRAPH_REF="$(git -C "$OG_SRC" rev-parse --abbrev-ref HEAD)" ORCA_GRAPH_NO_DAEMON=1 ORCA_GRAPH_NO_ROOM=1
unset CI ORCA_GRAPH_SKIP ORCA_GRAPH_INSTALL_DIR 2>/dev/null || true
T="$(mktemp -d)"; trap 'git -C "$SRC" worktree remove --force "$T/old" >/dev/null 2>&1; rm -rf "$T"' EXIT
PASS=0; FAIL=0; SKIP=0
ok(){ PASS=$((PASS+1)); printf '  \033[1;32mPASS\033[0m  %s\n' "$*"; }
no(){ FAIL=$((FAIL+1)); printf '  \033[1;31mFAIL\033[0m  %s\n' "$*"; [ -f "${LOG:-}" ] && sed 's/\x1b\[[0-9;]*m//g' "$LOG" | tail -6 | sed 's/^/        /'; }
sk(){ SKIP=$((SKIP+1)); printf '  SKIP  %s\n' "$*"; }
box(){ B="$T/$1"; mkdir -p "$B/home" "$B/proj"; git -C "$B/proj" init -q; LOG="$B/log"; GH="$B/home/.claude/harness"; }
boot(){ ( cd "$B/proj" && HOME="$B/home" HARNESS_BASE="file://$SRC/harness/poc-vendor-neutral" REPO_RAW="file://$SRC" bash "$SRC/harness/poc-vendor-neutral/bootstrap.sh" --no-verify "$@" ) >"$LOG" 2>&1; }
ver(){ HOME="$B/home" python3 "$GH/harness/scripts/orca-graph.py" --version 2>&1 | head -1; }

case_A3(){ box a3; boot --harness-only; rc=$?
  V="$("$B/home/.orca-graph/bin/orca-graph" --version 2>&1)"
  { [ $rc = 0 ] && [[ "$V" == orca-graph\ [0-9]* ]]; } && ok "A3 --harness-only: module vẫn được kéo ($V)" || no "A3 rc=$rc V=$V"; }

case_A7(){ box a7; ( HOME="$B/home" bash "$SRC/harness/scripts/install-harness.sh" --global ) >"$LOG" 2>&1; rc=$?; V="$(ver)"
  { [ $rc = 0 ] && [[ "$V" == orca-graph\ [0-9]* ]]; } && ok "A7 install-harness --global: shim + engine cùng chuyến ($V)" || no "A7 rc=$rc V=$V"
  box a7s; ( HOME="$B/home" ORCA_GRAPH_SKIP=1 bash "$SRC/harness/scripts/install-harness.sh" --global ) >"$LOG" 2>&1
  HOME="$B/home" python3 "$GH/harness/scripts/orca-graph.py" --version >"$B/v" 2>&1; rc=$?
  { [ $rc = 3 ] && grep -q "orca-graph/main/install.sh" "$B/v" && [ ! -e "$B/home/.orca-graph/repo" ]; } && ok "A7s ORCA_GRAPH_SKIP: không kéo; shim rc 3 + in lệnh cài" || no "A7s rc=$rc"; }

case_B1(){ OLD=70ecb22
  git -C "$SRC" cat-file -e "$OLD^{commit}" 2>/dev/null || { sk "B1 cần commit $OLD (trước khi tách repo) — checkout nông của CI không có"; return; }
  box b1; git -C "$SRC" worktree add -q --detach "$T/old" "$OLD" || { sk "B1 không dựng được worktree"; return; }
  ( HOME="$B/home" bash "$T/old/harness/scripts/install-harness.sh" --global ) >"$LOG" 2>&1
  OG="$GH/harness/scripts/orca-graph.py"; L0=$(wc -l < "$OG" | tr -d ' ')
  mkdir -p "$B/proj/.llmwiki/graph"; printf '# t\n\n### Task 1: A\n**Files:**\n- Tạo: `a`\n**Verify:** `true`\n### Task 2: B\n**Files:**\n- Tạo: `b`\n**Depends:** Task 1\n**Verify:** `true`\n' > "$B/proj/PLAN.md"
  ( cd "$B/proj" && export HOME="$B/home" && python3 "$OG" --dir .llmwiki/graph build PLAN.md --id old && python3 "$OG" --dir .llmwiki/graph lock old t1 \
      && python3 "$OG" --dir .llmwiki/graph set old t1 dispatched && python3 "$OG" --dir .llmwiki/graph set old t1 done --gen 1 ) >/dev/null 2>&1
  boot; rc=$?; V="$(ver)"; L1=$(wc -l < "$OG" | tr -d ' ')
  ST="$(cd "$B/proj" && HOME="$B/home" python3 "$OG" --dir .llmwiki/graph show old 2>/dev/null | awk '/^  t/{printf "%s=%s ",$1,$2}')"
  { [ $rc = 0 ] && [ "$L0" -gt 500 ] && [ "$L1" -lt 100 ] && [[ "$V" == orca-graph\ 3* ]] && [ "$ST" = "t1=done t2=ready " ]; } \
    && ok "B1 engine v2 ($L0 dòng) → shim ($L1 dòng) + $V; graph dở đọc nguyên: $ST" || no "B1 rc=$rc L0=$L0 L1=$L1 V=$V ST=$ST"
  git -C "$SRC" worktree remove --force "$T/old" >/dev/null 2>&1; }

case_B3(){ box b3; boot --with-wiki || true
  [ -f "$B/proj/.llmwiki/.harness-stamp" ] || { no "B3 fixture không ra layout dot"; return; }
  ( cd "$B/proj" && HOME="$B/home" bash "$SRC/harness/scripts/install-harness.sh" . --self-heal ) >"$LOG" 2>&1; rc=$?
  { [ $rc = 5 ] && grep -q "bootstrap.sh" "$LOG" && [ ! -d "$B/proj/harness/scripts" ] && [ ! -d "$B/proj/llmwiki" ]; } \
    && ok "B3 /harness-update kiểu cũ trên dot-layout: DỪNG rc 5, chỉ lệnh bootstrap, không chép engine / không mọc llmwiki/ trần" || no "B3 rc=$rc"; }

case_C1(){ for how in declared inferred; do box "c1$how"; P="$B/proj"; mkdir -p "$P/fdk/wiki" "$P/.github/workflows" "$P/.claude"
    echo "name: REAL-CI" > "$P/.github/workflows/harness.yml"; echo '{"mine":1}' > "$P/.claude/settings.json"
    [ $how = declared ] && echo "repo_role: framework" > "$P/.overstack.yaml"
    git -C "$P" add -A >/dev/null 2>&1; git -C "$P" -c user.name=t -c user.email=t@t commit -qm base
    ( cd "$P" && HOME="$B/home" bash "$SRC/harness/poc-vendor-neutral/install.sh" . --no-verify ) >"$LOG" 2>&1; rc=$?
    { [ $rc = 3 ] && [ -z "$(git -C "$P" status --porcelain)" ] && grep -q "REPO FRAMEWORK" "$LOG"; } && ok "C1 ($how): installer từ chối repo framework, 0 file đổi" || no "C1 ($how) rc=$rc đổi: $(git -C "$P" status --porcelain | head -3 | tr '\n' ' ')"
  done; }

CASES=("$@"); [ ${#CASES[@]} -gt 0 ] || CASES=(A3 A7 B1 B3 C1)
for c in "${CASES[@]}"; do if declare -F "case_$c" >/dev/null; then "case_$c"; else echo "ca lạ: $c (có: A3 A7 B1 B3 C1)"; FAIL=$((FAIL+1)); fi; done
LEAK="$(pgrep -f "$T" | wc -l | tr -d ' ')"; [ "$LEAK" = 0 ] || { echo "  ⚠ còn $LEAK process chạy từ thư mục tạm của test"; FAIL=$((FAIL+1)); }
echo ""; echo "install-flows: $PASS PASS · $FAIL FAIL · $SKIP SKIP"; [ "$FAIL" = 0 ]
