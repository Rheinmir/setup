#!/usr/bin/env bash
# fdk-gate-git-env-test — bước của fdk-gate KHÔNG được thừa hưởng GIT_DIR/GIT_INDEX_FILE của git hook.
#
# Bối cảnh (đo 27/09/2026): git export GIT_DIR, GIT_INDEX_FILE… vào hook pre-push. fdk-gate truyền nguyên môi
# trường cho từng bước, nên self-test dựng repo tạm (`git -C /tmp/x init/commit`) thực ra thao tác trên repo
# THẬT: harness-doctor, graph-engineering, BNAL đỏ chỉ khi push (chạy tay thì xanh), index bị xoá sạch,
# phát sinh nhánh rác, và một commit sau đó đã xoá 1641 file. Sửa: run() gỡ GIT_* trừ 4 biến danh tính.
#
# Kiểm bằng HÀNH VI: gọi đúng run() của fdk-gate dưới môi trường giả hook (GIT_DIR trỏ repo ngoài), cho bước
# con dựng repo tạm rồi commit. Repo ngoài phải KHÔNG nhận thêm commit nào. GATE=… để chạy với bản khác (bite test).
# Usage: bash harness/tests/fdk-gate-git-env-test.sh [repo-root]   (exit 0 = pass)
set -u
SRC="$(cd "${1:-.}" && pwd)"
GATE="${GATE:-$SRC/harness/scripts/fdk-gate.py}"
fail=0
ok()  { printf '  \033[1;32m✓\033[0m %s\n' "$1"; }
bad() { printf '  \033[1;31m✗\033[0m %s\n' "$1"; fail=$((fail+1)); }
SB="$(mktemp -d)"; trap 'rm -rf "$SB"' EXIT
OUT="$SB/outer"
git init -q "$OUT" && git -C "$OUT" -c user.name=t -c user.email=t@t commit -q --allow-empty -m seed
before="$(git -C "$OUT" rev-list --count HEAD)"

# GIT_DIR/GIT_INDEX_FILE chỉ đặt cho tiến trình python (y như hook), không rò sang các lệnh git của chính test.
res="$(GIT_DIR="$OUT/.git" GIT_INDEX_FILE="$OUT/.git/index" python3 - "$GATE" "$SRC" <<'PY'
import importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("fdk_gate", sys.argv[1]); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
step = 'd=$(mktemp -d) && git -C "$d" init -q && git -C "$d" -c user.name=t -c user.email=t@t commit -q --allow-empty -m inner && echo "GIT_DIR=${GIT_DIR:-unset}"'
rc, msg = g.run(Path(sys.argv[2]), ["bash", "-c", step])
print(f"{rc}|{msg}")
PY
)"
rc="${res%%|*}"; msg="${res#*|}"
after="$(git -C "$OUT" rev-list --count HEAD)"

[ "$rc" = 0 ] && ok "bước con chạy xong (rc=0)" || bad "bước con lỗi rc=$rc — $msg"
[ "$msg" = "GIT_DIR=unset" ] && ok "bước con KHÔNG thấy GIT_DIR của hook" || bad "GIT_DIR rò vào bước con: $msg"
[ "$after" = "$before" ] && ok "repo ngoài không bị commit lén (vẫn $before commit)" || bad "repo ngoài nhận thêm commit ($before → $after): self-test ghi nhầm repo thật"

if [ "$fail" -eq 0 ]; then printf '\n\033[1m═══ fdk-gate-git-env: \033[1;32mPASS\033[0m\033[0m\n'; exit 0; fi
printf '\n\033[1m═══ fdk-gate-git-env: \033[1;31m%d VI PHẠM\033[0m\033[0m\n' "$fail"; exit 1
