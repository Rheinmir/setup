#!/usr/bin/env bash
# install-graph-option-test — option module orca-graph của install.sh: MẶC ĐỊNH TICK, Enter là kéo; chỉ kéo khi được tick.
#   (a) --no-graph            → không kéo, bảng trạng thái ghi BỎ QUA
#   (b) không TTY (agent/CI)  → không hỏi, kéo luôn; shim ở đường dẫn cũ chạy được engine vừa kéo
#   (c) TTY + Enter           → hiện checklist `[x] 1. orca-graph`, Enter là kéo
#   (d) TTY + gõ 1 rồi Enter  → bỏ tick → không kéo
# Không đụng mạng, không đụng ~ thật: HOME cô lập, engine lấy từ bản đã cài trên máy (ORCA_GRAPH_REPO=<git dir local>).
set -uo pipefail
SRC="$(cd "$(dirname "$0")/../.." && pwd)"
OG_SRC="${ORCA_GRAPH_REPO:-$HOME/.orca-graph/repo}"; OG_SRC="$(cd "$OG_SRC" 2>/dev/null && pwd -P || true)"
[ -n "$OG_SRC" ] && [ -f "$OG_SRC/install.sh" ] && git -C "$OG_SRC" rev-parse --git-dir >/dev/null 2>&1 \
  || { echo "SKIP: không có bản orca-graph local để làm nguồn (cài: install.sh của Rheinmir/orca-graph)"; exit 0; }
OG_BR="$(git -C "$OG_SRC" rev-parse --abbrev-ref HEAD)"
# `git clone` local chỉ lấy HEAD: engine sửa mà CHƯA commit sẽ không nằm trong bản được test — nói ra, đừng im lặng xanh.
[ -z "$(git -C "$OG_SRC" status --porcelain)" ] || echo "⚠ $OG_SRC có thay đổi chưa commit — test này chỉ thấy HEAD ($(git -C "$OG_SRC" rev-parse --short HEAD)) của engine"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
PASS=0; FAIL=0
ok(){ PASS=$((PASS+1)); printf '  \033[1;32mPASS\033[0m  %s\n' "$*"; }
no(){ FAIL=$((FAIL+1)); printf '  \033[1;31mFAIL\033[0m  %s\n' "$*"; }
newproj(){ P="$T/$1"; mkdir -p "$P/proj" "$P/home"; git -C "$P/proj" init -q; }
inst(){ # inst <args...> — chạy install.sh không tty, log vào $P/log
  ( cd "$P/proj" && env -u CI HOME="$P/home" ORCA_GRAPH_REPO="$OG_SRC" ORCA_GRAPH_REF="$OG_BR" \
      bash "$SRC/harness/poc-vendor-neutral/install.sh" . --no-verify "$@" ) >"$P/log" 2>&1; }

newproj a; inst --no-graph
{ [ ! -e "$P/home/.orca-graph/repo" ] && grep -q "module orca-graph  — BỎ QUA" "$P/log"; } && ok "(a) --no-graph không kéo" || { no "(a) --no-graph"; tail -5 "$P/log"; }

newproj b; inst
if [ -f "$P/home/.orca-graph/repo/engine/orca-graph.py" ] && grep -q "module orca-graph  ✓" "$P/log" && ! grep -q "Enter = cài" "$P/log"; then
  V="$(HOME="$P/home" python3 "$SRC/harness/scripts/orca-graph.py" --version 2>&1)"
  [[ "$V" == orca-graph\ * ]] && ok "(b) không TTY → kéo luôn, không hỏi; shim chạy engine vừa kéo ($V)" || no "(b) shim không chạy được: $V"
else no "(b) không TTY phải kéo mặc định"; tail -8 "$P/log"; fi

tty_case(){ # tty_case <keys> — chạy install.sh dưới pty thật, chờ prompt rồi gõ <keys>
  python3 - "$P" "$SRC" "$OG_SRC" "$OG_BR" "$1" <<'PY'
import os, pty, select, sys, time
P, SRC, OG, BR, keys = sys.argv[1:6]
env = {k: v for k, v in os.environ.items() if k not in ("CI", "OVERSTACK_NONINTERACTIVE")}
env.update(HOME=f"{P}/home", ORCA_GRAPH_REPO=OG, ORCA_GRAPH_REF=BR)
pid, fd = pty.fork()
if pid == 0:
    os.chdir(f"{P}/proj"); os.execvpe("bash", ["bash", f"{SRC}/harness/poc-vendor-neutral/install.sh", ".", "--no-verify"], env)
buf, sent, t0 = b"", 0, time.time()
steps = keys.encode().split(b"|")
while time.time() - t0 < 180:
    r, _, _ = select.select([fd], [], [], 1)
    if r:
        try:
            d = os.read(fd, 65536)
        except OSError:
            break
        if not d:
            break
        buf += d
        if sent < len(steps) and buf.count(b"Enter = c") > sent:      # mỗi lần prompt hiện lại → gõ bước kế
            os.write(fd, steps[sent] + b"\n"); sent += 1
    elif os.waitpid(pid, os.WNOHANG)[0]:
        break
open(f"{P}/log", "wb").write(buf)
PY
}
newproj c; tty_case ""
{ grep -q "\[x\] 1. orca-graph" "$P/log" && [ -f "$P/home/.orca-graph/repo/engine/orca-graph.py" ]; } && ok "(c) TTY: checklist đã tick sẵn, Enter là kéo" || { no "(c) TTY + Enter"; tail -8 "$P/log"; }

newproj d; tty_case "1|"
{ grep -q "\[ \] 1. orca-graph" "$P/log" && [ ! -e "$P/home/.orca-graph/repo" ] && grep -q "BỎ QUA" "$P/log"; } && ok "(d) TTY: gõ 1 bỏ tick → không kéo" || { no "(d) TTY bỏ tick"; tail -8 "$P/log"; }

echo ""; echo "install-graph-option: $PASS PASS · $FAIL FAIL"; [ "$FAIL" = 0 ]
