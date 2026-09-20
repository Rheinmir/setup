#!/usr/bin/env bash
# downstream-fixture.sh — dựng MỘT dự án downstream layout dot từ working-tree, HOME cô lập.
# Source rồi gọi: make_downstream_fixture <repo-root>  → $FX (dự án) · $GH (global sandbox)
# Không curl mạng: bootstrap qua file:// (đúng khuôn fresh-install-smoke --local).
make_downstream_fixture() {
  local SRC; SRC="$(cd "${1:?repo-root}" && pwd)"
  FX_TMP="$(mktemp -d)"
  # Engine orca-graph sống ở repo riêng: lấy bản ĐÃ CÀI trên máy làm nguồn local (chụp TRƯỚC khi đổi HOME) để fixture
  # vẫn kín mạng; máy chưa cài thì bỏ module (shim sẽ báo rc 3 — ca (e) của dot-layout-runtime tự skip).
  local OG_REAL; OG_REAL="$(cd "${ORCA_GRAPH_REPO:-$HOME/.orca-graph/repo}" 2>/dev/null && pwd -P || true)"
  if [ -n "$OG_REAL" ] && git -C "$OG_REAL" rev-parse --git-dir >/dev/null 2>&1; then
    export ORCA_GRAPH_REPO="$OG_REAL" ORCA_GRAPH_REF="$(git -C "$OG_REAL" rev-parse --abbrev-ref HEAD)"
  else
    export ORCA_GRAPH_SKIP=1
  fi
  export HOME="$FX_TMP/home"; mkdir -p "$HOME"
  FX="$FX_TMP/proj"; GH="$HOME/.claude/harness"
  mkdir -p "$FX"; git -C "$FX" init -q
  ( cd "$FX" && HARNESS_BASE="file://$SRC/harness/poc-vendor-neutral" REPO_RAW="file://$SRC" \
      bash "$SRC/harness/poc-vendor-neutral/bootstrap.sh" --with-wiki ) >"$FX_TMP/install.log" 2>&1 \
    || { echo "bootstrap lỗi — xem $FX_TMP/install.log"; return 1; }
  # bootstrap chỉ tải LÕI vào thư mục tạm, nên install.sh không thấy install-harness.sh cạnh nó; bản tải về
  # thiếu bundle nên CLONE rheinmir/setup@orca → engine global trong fixture là code REMOTE, không phải
  # working tree (đo 2026-09-11: sha hook global ≠ worktree). Cài đè global từ working tree (khuôn ge-travel-test).
  bash "$SRC/harness/scripts/install-harness.sh" --global >>"$FX_TMP/install.log" 2>&1 \
    || { echo "install-harness --global từ working tree lỗi — xem $FX_TMP/install.log"; return 1; }
  [ -f "$FX/.llmwiki/.harness-stamp" ] || { echo "fixture không ra layout dot (thiếu .llmwiki/.harness-stamp)"; return 1; }
  [ -f "$GH/hooks/session_start.py" ]  || { echo "global sandbox thiếu hooks — install-harness --global không chạy"; return 1; }
  cmp -s "$GH/hooks/session_start.py" "$SRC/llmwiki/.claude/hooks/session_start.py" \
    || { echo "hook global KHÔNG phải bản working tree — fixture đang test code remote"; return 1; }
  export FX GH FX_TMP
}
