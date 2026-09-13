#!/usr/bin/env bash
# r3-worktree-hook-env-test.sh — R3 (index_sync) phải đúng khi chạy TRONG hook git ở linked worktree.
# Git đặt GIT_DIR=<.git/worktrees/x> (không GIT_WORK_TREE) cho hook; git con chạy cwd=wiki thì coi wiki
# là gốc work tree → mọi trang bị báo "THỪA". Test dựng repo + worktree tạm, gọi validator với ĐÚNG env đó.
set -u
SRC="$(cd "${1:-.}" && pwd)"; V="$SRC/harness/validators/index_sync.py"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
git -C "$T" init -q main && cd "$T/main" && git config user.email t@t && git config user.name t
mkdir -p wiki/concepts && printf -- '---\ntype: concept\n---\n# a\n\n## Origin\n- t\n' > wiki/concepts/a.md
printf '# Index\n\n| File | Type | Summary |\n|---|---|---|\n| [a](concepts/a.md) | concept | trang a để thử R3 trong worktree |\n' > wiki/index.md
git add -A && git -c core.hooksPath=/dev/null commit --no-verify -qm init && git worktree add -q "$T/wt" -b wt
cd "$T/wt"; GD="$(git rev-parse --absolute-git-dir)"; fail=0
python3 "$V" --wiki-dir wiki >/dev/null 2>&1 && echo "  ✓ chạy thường trong worktree: xanh" || { echo "  ✗ chạy thường đỏ"; fail=1; }
if GIT_DIR="$GD" GIT_INDEX_FILE="$GD/index" python3 "$V" --wiki-dir wiki >"$T/out" 2>&1; then echo "  ✓ env hook (GIT_DIR worktree, không GIT_WORK_TREE): xanh"
else echo "  ✗ env hook đỏ giả:"; sed 's/^/     /' "$T/out" | head -4; fail=1; fi
printf '| [ghost](concepts/ghost.md) | concept | trang ma để thử R3 còn cắn |\n' >> wiki/index.md
if GIT_DIR="$GD" GIT_INDEX_FILE="$GD/index" python3 "$V" --wiki-dir wiki >/dev/null 2>&1; then echo "  ✗ đối chứng âm: trang ma không bị bắt"; fail=1
else echo "  ✓ đối chứng âm: trang ma vẫn bị bắt dưới env hook"; fi
exit $fail
