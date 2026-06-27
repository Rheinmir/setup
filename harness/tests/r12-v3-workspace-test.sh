#!/usr/bin/env bash
# T5 — test R12 v3 multi-subrepo (fixture tmp, reversible).
#   [1] sweep phát hiện subrepo TARGET behind → exit 2
#   [2] sau khi pull synced → exit 0
#   [3] install-harness --all-subrepos → mỗi target có pre-push (gate2)
#   [4] watch (non-target) behind → KHÔNG chặn (exit 0)
set -uo pipefail

HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REAL_BIN="$HARNESS/poc-vendor-neutral/bin"
SWEEP="$REAL_BIN/pull-gate-sweep.sh"
INSTALLER="$HARNESS/scripts/install-harness.sh"

WS="$(mktemp -d)"; trap 'rm -rf "$WS"' EXIT
PASS=0; FAIL=0
chk(){ if [ "$2" = "$3" ]; then echo "  ✓ $1"; PASS=$((PASS+1)); else echo "  ✗ $1 (got '$2' want '$3')"; FAIL=$((FAIL+1)); fi; }

mkrepo(){ # mkrepo <name> <behind 0|1>
  local name="$1" behind="$2"
  local bare="$WS/$name.git" work="$WS/$name"
  git init --bare -q "$bare"
  git init -q "$work"
  ( cd "$work"
    git config user.email t@t; git config user.name t
    mkdir -p harness/poc-vendor-neutral/bin
    cp "$REAL_BIN/pull-gate.sh" harness/poc-vendor-neutral/bin/
    chmod +x harness/poc-vendor-neutral/bin/pull-gate.sh
    git add -A; git commit -qm init
    git remote add origin "$bare"
    br="$(git rev-parse --abbrev-ref HEAD)"
    git push -q origin "$br"
    git branch --set-upstream-to="origin/$br" >/dev/null 2>&1
  )
  if [ "$behind" = "1" ]; then
    local adv="$WS/$name.adv"
    git clone -q "$bare" "$adv"
    ( cd "$adv"; git config user.email t@t; git config user.name t; echo x >> f; git add -A; git commit -qm adv; git push -q )
    rm -rf "$adv"
    ( cd "$work"; git fetch -q origin )   # remote-tracking tiến → local behind 1
  fi
}

echo "== Fixture: repoA(synced,target) repoB(behind,target) repoC(behind,watch) =="
mkrepo repoA 0
mkrepo repoB 1
mkrepo repoC 1
cat > "$WS/.harness-workspace.yaml" <<YAML
subrepos: ["repoA", "repoB", "repoC"]
targets:  ["repoA", "repoB"]
YAML

echo "[1] sweep — repoB(target) behind → mong exit 2"
out="$(bash "$SWEEP" "$WS" 2>&1)"; rc=$?
echo "$out" | sed 's/^/    /'
chk "exit 2 khi target behind" "$rc" "2"

echo "[2] repoC(watch) behind nhưng repoA/B synced → KHÔNG chặn"
( cd "$WS/repoB"; git pull -q --rebase 2>/dev/null )   # repoB synced; repoC vẫn behind nhưng là watch
out="$(bash "$SWEEP" "$WS" 2>&1)"; rc=$?
echo "$out" | sed 's/^/    /'
chk "exit 0 khi chỉ watch behind" "$rc" "0"

echo "[3] install-harness --all-subrepos → pre-push mỗi target"
bash "$INSTALLER" --all-subrepos "$WS" >/dev/null 2>&1
[ -x "$WS/repoA/.git/hooks/pre-push" ] && a=1 || a=0
[ -x "$WS/repoB/.git/hooks/pre-push" ] && b=1 || b=0
chk "pre-push → repoA (target)" "$a" "1"
chk "pre-push → repoB (target)" "$b" "1"

echo "── T5: PASS=$PASS FAIL=$FAIL ──"
[ "$FAIL" = "0" ]
