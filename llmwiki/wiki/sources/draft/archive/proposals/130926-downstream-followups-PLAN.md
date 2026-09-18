---
type: draft
title: "Downstream-layout — các việc mở sau nghiệm thu 110926 (PLAN thi hành)"
status: implemented
tags: [plan, downstream, dot-layout, medic, freshinstall, wiki-sync, worktree]
timestamp: 2026-09-13
---

# Downstream-layout — việc mở sau nghiệm thu 110926 — PLAN thi hành

**Goal:** đóng các việc còn mở mà nghiệm thu PLAN `110926-downstream-layout-awareness` để lại: (A) ngữ cảnh đầu phiên nói thẳng dự án khách không chứa hook, để eval A/B lên 5/5; (B) cổng `freshinstall` của medic đo đúng code đang viết, không đụng HOME thật; (C) `wiki-sync.py` chạy được ở dự án layout dot; (E) medic không báo giả "chưa cài pre-commit" trong worktree; (G) installer in đúng đường stamp. (D) R3 không còn đỏ giả khi commit từ worktree Orca.

**Architecture:** không có module mới. Mỗi task sửa tại chỗ một file đã có, theo đúng resolver dùng chung (`overstack_paths`, `hooklib`) và khuôn fixture của `harness/tests/downstream-fixture.sh`. Các thay đổi chạm file đi xuống global (`session_start.py`, `wiki-sync.py`, `medic.py`, `install.sh`) nên cuối lượt phải tăng `template_version` rồi UAT hai pha như lượt trước.

**Tech stack:** Python 3 stdlib + bash. Không dependency mới.

**SPEC nguồn:** chỉ thị "xử lý tiếp đi" của user ngày 2026-09-13, sau báo cáo nghiệm thu liệt kê các việc mở. Nền: `llmwiki/wiki/sources/draft/110926-downstream-layout-awareness-PLAN.md` và `fdk/wiki/sources/evals/downstream-layout-awareness.md`.

## Origin
- **Chỉ thị:** user, 2026-09-13, "xử lý tiếp đi" (các việc mở trong báo cáo nghiệm thu 110926).
- **Bằng chứng từng việc (đo thật trước khi viết PLAN):**
  - (A) Eval A/B golden `downstream-layout-awareness` bản 2: agent trên `4f4db2e` FAIL 4/5, nói hook chạy từ `.llmwiki/.claude/hooks` trong dự án khách. Nó tin fixture đời cũ ở `harness/tests/dot-layout-migrate-test.sh` (dòng ghi `settings.json` trỏ `$CLAUDE_PROJECT_DIR/llmwiki/.claude/hooks/session_start.py`) hơn dòng bản đồ.
  - (B) `harness/scripts/fresh-install-smoke.sh` chế độ `--local` chỉ truyền `HARNESS_BASE`, không truyền `REPO_RAW`, nên `install.sh` tải `overstack.html`, template và `install-harness.sh` từ GitHub `orca`; bản `install-harness.sh` tải về thiếu bundle nên clone `rheinmir/setup@orca`. Kiểm engine global dùng `$HOME` thật (`GH_HOME="${OVERSTACK_HARNESS_HOME:-$HOME/.claude/harness}"`). Cùng lỗi mà fixture Task 1 của PLAN 110926 đã sửa.
  - (C) `harness/scripts/wiki-sync.py::detect_wiki_dir` chỉ dò `llmwiki/wiki` rồi `wiki`, không có `.llmwiki/wiki`, nên thoát lỗi ở dự án layout dot. Người gọi: `self-report.py`, `token-attrib.py`, `sync-template.py`, `build-overstack-docs.py`, hai test, một bước CI.
  - (E) `fdk/tools/medic.py::p_backstop` kiểm `ROOT / ".git/hooks/pre-commit"`. Trong worktree `.git` là file, nên luôn báo "pre-commit CHƯA cài". Đo trong worktree `downstream-layout`: `git rev-parse --git-path hooks/pre-commit` trả `/Users/giatran/orca/setup/setup/.git/hooks/pre-commit`, file tồn tại (git 2.50.1).
  - (G) `harness/poc-vendor-neutral/install.sh` dòng `log "  ✓ llmwiki/.harness-stamp (guarded_by: ${TV:-0})"` in cứng `llmwiki/` trong khi file ghi vào `$ROOT/$OVERSTACK_DIR/.harness-stamp`.
- **Rút lại một kết luận cũ:** "pre-commit trong worktree stash nhầm checkout chính" là SAI. Sandbox sạch cho thấy pre-commit trong linked worktree chỉ stash file của chính worktree; hai patch 11/09 là của phiên khác commit `5ad733d` trong checkout chính. Riêng R3 đỏ giả khi commit từ worktree thì tái hiện được và đã tìm ra gốc — xem Task D.
- **Commit:** _(verify-before-commit điền)_

## Global constraints

- Fail-open tuyệt đối trong hook: mọi nhánh mới trong `session_start.py` nằm trong `try/except Exception: pass` sẵn có của hàm.
- Không ghi cứng đường trần mới trong file đi xuống global: `python3 harness/validators/bare_path_lint.py --root . --check` phải xanh sau MỖI task. Không ghi lại baseline.
- Sandbox cho mọi test: `HOME` trỏ vào `mktemp -d`; không chạm `~/.claude/harness` thật.
- Không commit, không stash, không reset, không checkout trong lúc thi hành; reviewer commit sau khi review.
- Không ghi công AI trong commit (R15).
- Sau MỖI task: chạy lệnh kiểm của task đó và `bash harness/tests/dot-layout-runtime-test.sh .` (phải vẫn 5/5).

## File structure

- Sửa `llmwiki/.claude/hooks/session_start.py` — `downstream_map()` in thêm một dòng nói thẳng dự án khách không chứa hook.
- Sửa `harness/downstream-contract.yaml` — cột `downstream` của dòng hook trong `layout_map`.
- Sửa `harness/tests/dot-layout-migrate-test.sh` — chú thích fixture đời cũ.
- Sửa `harness/scripts/fresh-install-smoke.sh` — nhánh `--local` cô lập HOME, cài engine global từ working tree, `cmp` hook.
- Sửa `harness/scripts/wiki-sync.py` — `detect_wiki_dir` dò `.llmwiki/wiki` trước.
- Sửa `harness/tests/wiki-sync-test.sh` — thêm ca layout dot.
- Sửa `fdk/tools/medic.py` — `p_backstop` tìm hook qua `git rev-parse --git-path`.
- Sửa `harness/poc-vendor-neutral/install.sh` — nhãn log stamp.
- Sửa `harness/validators/index_sync.py` + bản deploy `llmwiki/.claude/hooks/validators/index_sync.py` — git con không kế thừa `GIT_DIR` của hook worktree.
- Tạo `harness/tests/r3-worktree-hook-env-test.sh` + wire vào `.github/workflows/harness.yml`.

---

### Task A — Ngữ cảnh đầu phiên nói thẳng: dự án khách không chứa hook

**Thoả:** việc mở (A) — eval A/B cho thấy agent trên bản mới vẫn tưởng hook nằm trong dự án khách.

**Files:**
- Sửa `llmwiki/.claude/hooks/session_start.py` (hàm `downstream_map`)
- Sửa `harness/downstream-contract.yaml` (dòng thứ ba của `layout_map`)
- Sửa `harness/tests/dot-layout-migrate-test.sh` (khối "1. Dự án chuẩn CŨ")

**Interfaces:**
- Consumes: `harness/downstream-contract.yaml` `layout_map` (đã có).
- Produces: thêm đúng một dòng in ra sau các dòng bản đồ; không đổi điều kiện in (chỉ repo framework có `fdk/wiki`).

```python
# session_start.py, trong downstream_map(), ngay sau:  print("\n".join(rows[:6]))
        print("  • Dự án khách KHÔNG chứa hook hay engine: hook chạy từ ~/.claude/harness/hooks "
              "(đăng ký ở ~/.claude/settings.json, chỉ bật khi thấy .llmwiki/.harness-stamp); "
              "trong dự án chỉ có .harness/poc-vendor-neutral (validator + CI).")
```

```yaml
# harness/downstream-contract.yaml — dòng thứ ba của layout_map, chỉ đổi giá trị downstream:
  - {repo: "harness/scripts, harness/validators, fdk/tools, llmwiki/.claude/hooks", downstream: "~/.claude/harness/{harness,fdk,hooks}/ — dự án khách KHÔNG chứa hook/engine", note: "engine GLOBAL dùng chung mọi dự án; hook fire từ ~/.claude/settings.json, guard theo .harness-stamp"}
```

```bash
# harness/tests/dot-layout-migrate-test.sh — thêm hai dòng chú thích ngay TRÊN dòng printf ghi settings.json của khối 1:
# settings.json ĐỜI CŨ (trước v4, hook per-project). Bản cài hiện tại KHÔNG ghi hook vào dự án khách:
# hook chạy từ ~/.claude/harness/hooks. Fixture này chỉ tồn tại để kiểm migrate viết lại con trỏ đời cũ.
```

Lệnh kiểm:

```bash
echo '{"session_id":"t"}' | CLAUDE_PROJECT_DIR=$PWD python3 llmwiki/.claude/hooks/session_start.py | grep -A8 downstream-map   # phải có dòng "Dự án khách KHÔNG chứa hook"
bash harness/tests/dot-layout-migrate-test.sh .
bash harness/tests/dot-layout-runtime-test.sh .          # 5/5
python3 harness/validators/bare_path_lint.py --root . --check
```

---

### Task B — `fresh-install-smoke --local` đo đúng code đang viết, không đụng HOME thật

**Thoả:** việc mở (B) — cổng `freshinstall` của medic (required cho mọi push) đang cài engine từ GitHub `orca` và soi `~/.claude/harness` thật của máy dev.

**Files:**
- Sửa `harness/scripts/fresh-install-smoke.sh`

**Interfaces:**
- Consumes: `harness/scripts/install-harness.sh --global` (chạy từ working tree, dùng `$HOME` đang export), khuôn trong `harness/tests/downstream-fixture.sh`.
- Produces: không đổi CLI (`--local` mặc định, `--remote`, `--keep`, `--self-test`). Chế độ `--remote` giữ nguyên hành vi.

Sửa nhánh `else` (chế độ local) của khối "cài như người mới", và hai chỗ đọc skill global:

```bash
# ngay TRƯỚC khối "── cài như người mới ──": nhớ HOME thật cho các kiểm skill (skill global
# chỉ npx cài được, fixture không có) rồi cô lập HOME cho phần harness ở chế độ local.
REAL_HOME="$HOME"
if [ "$MODE" = "local" ]; then
  export HOME="$TARGET.home"; mkdir -p "$HOME"
fi

# thay nhánh else (local) hiện tại bằng:
else
  echo "→ file:// từ working-tree (offline, tất định, HOME cô lập) — harness + llmwiki, bỏ npx skills"
  ( cd "$TARGET" && HARNESS_BASE="file://$ROOT/harness/poc-vendor-neutral" REPO_RAW="file://$ROOT" \
      bash "$ROOT/harness/poc-vendor-neutral/bootstrap.sh" --with-wiki ) >/dev/null 2>&1
  # install.sh tải install-harness.sh vào thư mục tạm → thiếu bundle → clone GitHub orca: engine global
  # sẽ là code REMOTE. Cài đè từ working tree rồi cmp (cùng lỗi fixture PLAN 110926 đã sửa).
  bash "$ROOT/harness/scripts/install-harness.sh" --global >/dev/null 2>&1 || bad "install-harness --global từ working tree lỗi"
  cmp -s "$HOME/.claude/harness/hooks/session_start.py" "$ROOT/llmwiki/.claude/hooks/session_start.py" \
    && ok "engine global = working tree (cmp hook)" || bad "engine global KHÔNG phải working tree — cổng đang đo code remote"
fi

# dọn HOME cô lập cùng TARGET: ở chỗ script đang rm -rf "$TARGET" khi không --keep, thêm:  rm -rf "$TARGET.home"

# parity hứa↔giao: skill global nằm ở HOME THẬT
SK_DIR="${AGENTS_SKILLS_DIR:-$REAL_HOME/.agents/skills}"
# mọi chỗ khác trong script đọc skill global qua $HOME/.claude/skills hoặc $HOME/.agents/skills: đổi $HOME → $REAL_HOME
```

`GH_HOME="${OVERSTACK_HARNESS_HOME:-$HOME/.claude/harness}"` giữ nguyên: ở chế độ local nó giờ trỏ HOME cô lập, tức đo đúng engine mà working tree cài ra.

Lệnh kiểm:

```bash
stat -f %m ~/.claude/harness/version.json > /tmp/gh-mtime.before
bash harness/scripts/fresh-install-smoke.sh ; echo rc=$?          # PASS, có dòng "engine global = working tree"
stat -f %m ~/.claude/harness/version.json | diff - /tmp/gh-mtime.before && echo "HOME thật không bị đụng"
python3 fdk/tools/medic.py freshinstall
```

---

### Task C — `wiki-sync.py` chạy được ở dự án layout dot

**Thoả:** việc mở (C).

**Files:**
- Sửa `harness/scripts/wiki-sync.py` (hàm `detect_wiki_dir`)
- Sửa `harness/tests/wiki-sync-test.sh` (thêm ca cuối)

**Interfaces:**
- Produces: `detect_wiki_dir(root, arg)` dò `.llmwiki/wiki` → `llmwiki/wiki` → `wiki`. Không đổi CLI. Repo framework (không có `.llmwiki`) giữ nguyên hành vi.

```python
def detect_wiki_dir(root: pathlib.Path, arg) -> pathlib.Path:
    if arg:
        return (root / arg).resolve() if not pathlib.Path(arg).is_absolute() else pathlib.Path(arg)
    # layout dot (dự án khách cài mới) trước, layout trần (repo framework / bản cài cũ) sau —
    # cùng thứ tự với overstack_paths.OVERSTACK_DIRS và session_start.wiki_drift (nơi đọc neo).
    for cand in (root / ".llmwiki" / "wiki", root / "llmwiki" / "wiki", root / "wiki"):
        if cand.is_dir():
            return cand
    sys.exit("wiki-sync: không tìm thấy thư mục wiki (.llmwiki/wiki, llmwiki/wiki hay wiki/) — chỉ định --wiki-dir")
```

Thêm vào CUỐI `harness/tests/wiki-sync-test.sh`, ngay trước dòng in tổng kết (đọc file để khớp biến `$SYNC` và cách đếm assertion sẵn có; nếu file dùng biến đếm thì tăng nó):

```bash
# 9. dự án khách layout dot: mark-synced phải neo vào .llmwiki/wiki, không thoát lỗi
D="$(mktemp -d)"; ( cd "$D" && git init -q && git config user.email t@t && git config user.name t \
  && mkdir -p .llmwiki/wiki/concepts && printf '# a\n\n## Origin\n- t\n' > .llmwiki/wiki/concepts/a.md \
  && git add -A && git commit -qm init && python3 "$SYNC" --mark-synced >/dev/null )
[ -f "$D/.llmwiki/wiki/.last-sync.json" ] && echo "  ✓ layout dot: neo nằm ở .llmwiki/wiki" \
  || { echo "  ✗ layout dot: không neo được vào .llmwiki/wiki"; exit 1; }
rm -rf "$D"
```

Lệnh kiểm:

```bash
bash harness/tests/wiki-sync-test.sh .
bash harness/tests/wiki-sync-flags-failopen-test.sh .
python3 harness/scripts/wiki-sync.py --check ; echo rc=$?     # ở repo framework: vẫn dò llmwiki/wiki như cũ
```

---

### Task E — medic tìm pre-commit hook đúng cả trong worktree

**Thoả:** việc mở (E).

**Files:**
- Sửa `fdk/tools/medic.py` (hàm `p_backstop`)

**Interfaces:**
- Produces: `p_backstop()` giữ nguyên ba giá trị trả về; chỉ đổi cách tìm file hook.

```python
    import shutil as _sh
    import subprocess as _sp
    # worktree có `.git` là FILE → ROOT/.git/hooks không tồn tại dù hook dùng chung đã cài.
    # Hỏi git: --git-path hooks/pre-commit trả đúng hook chung (và tôn trọng core.hooksPath).
    try:
        _p = _sp.run(["git", "-C", str(ROOT), "rev-parse", "--git-path", "hooks/pre-commit"],
                     capture_output=True, text=True, timeout=5).stdout.strip()
        hook_path = Path(_p) if _p and Path(_p).is_absolute() else ROOT / (_p or ".git/hooks/pre-commit")
    except Exception:
        hook_path = ROOT / ".git/hooks/pre-commit"
    hook = hook_path.exists()
    binary = _sh.which("pre-commit") is not None
```

(Nếu `medic.py` chưa `from pathlib import Path` ở đầu file thì dùng tên đang có — đọc đầu file trước.)

Lệnh kiểm:

```bash
python3 fdk/tools/medic.py backstop          # trong worktree: phải "ok", không còn "CHƯA cài"
( cd /Users/giatran/orca/setup/setup && python3 fdk/tools/medic.py backstop )   # checkout chính: vẫn ok
```

---

### Task G — installer in đúng đường stamp

**Thoả:** việc mở (G) — log UAT in `llmwiki/.harness-stamp` dù file ghi vào `.llmwiki/`.

**Files:**
- Sửa `harness/poc-vendor-neutral/install.sh`

**Interfaces:**
- Produces: chỉ đổi chuỗi log; không đổi hành vi.

```bash
    log "  ✓ $OVERSTACK_DIR/.harness-stamp (guarded_by: ${TV:-0})"
```

Lệnh kiểm:

```bash
bash harness/tests/dot-layout-runtime-test.sh .
bash harness/tests/install-seed-test.sh .
```

---

### Task D — R3 (index_sync) đúng khi chạy trong hook git của linked worktree

**Thoả:** việc mở (D) — mọi commit chạm wiki từ worktree Orca bị R3 chặn giả, buộc người dùng tắt hook.

**Files:**
- Sửa `harness/validators/index_sync.py` (hàm `gitignored` và `tracked`)
- Sửa `llmwiki/.claude/hooks/validators/index_sync.py` (bản deploy, phải giống hệt bản trên — `harness-lint --copies` gác)
- Tạo `harness/tests/r3-worktree-hook-env-test.sh`
- Sửa `.github/workflows/harness.yml` (wire test mới, ngay sau step `dot-layout-runtime`)

**Interfaces:**
- Produces: hàm nội bộ `_git_env() -> dict` trong `index_sync.py`; `gitignored()` và `tracked()` truyền `env=_git_env()` cho `subprocess.run`. Không đổi CLI.

Chẩn đoán (đo 2026-09-13, commit thật trong worktree tạm, log chèn vào `index_sync.py`): trong hook, git đặt `GIT_DIR=/…/.git/worktrees/<tên>` và `GIT_INDEX_FILE`, KHÔNG đặt `GIT_WORK_TREE`. `index_sync` gọi git con với `cwd=fdk/wiki`; có `GIT_DIR` mà không `GIT_WORK_TREE` thì git coi cwd là gốc work tree: `--show-toplevel` = `…/fdk/wiki`, `git ls-files --cached .` trả 1333 đường tính từ gốc repo, `git status concepts/R10.md` = `??`. Chạy tay (không `GIT_DIR`) thì xanh. Checkout chính không bị ảnh hưởng.

```python
def _git_env() -> dict:
    """Hook git trong linked worktree đặt GIT_DIR (không kèm GIT_WORK_TREE). Khi đó git con chạy
    với cwd khác gốc worktree sẽ coi cwd là gốc work tree → ls-files/check-ignore sai hết (đo
    2026-09-13: --show-toplevel = …/fdk/wiki, mọi trang wiki '??'). Bỏ GIT_DIR để git tự dò repo từ
    cwd; GIT_INDEX_FILE giữ nguyên vì đó là index đúng của lần commit đang chạy."""
    env = dict(os.environ)
    if "GIT_DIR" in env and "GIT_WORK_TREE" not in env:
        env.pop("GIT_DIR")
    return env
# trong gitignored():  subprocess.run(["git", "check-ignore", "-q", full], cwd=..., ..., env=_git_env())
# trong tracked():     subprocess.run(["git", "ls-files", "-z", "--cached", "."], cwd=key, ..., env=_git_env())
# thêm `import os` nếu file chưa có. Sửa xong: cp harness/validators/index_sync.py llmwiki/.claude/hooks/validators/index_sync.py
```

```bash
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
git add -A && git commit -qm init && git worktree add -q "$T/wt" -b wt
cd "$T/wt"; GD="$(git rev-parse --absolute-git-dir)"; fail=0
python3 "$V" --wiki-dir wiki >/dev/null 2>&1 && echo "  ✓ chạy thường trong worktree: xanh" || { echo "  ✗ chạy thường đỏ"; fail=1; }
if GIT_DIR="$GD" GIT_INDEX_FILE="$GD/index" python3 "$V" --wiki-dir wiki >"$T/out" 2>&1; then echo "  ✓ env hook (GIT_DIR worktree, không GIT_WORK_TREE): xanh"
else echo "  ✗ env hook đỏ giả:"; sed 's/^/     /' "$T/out" | head -4; fail=1; fi
printf '| [ghost](concepts/ghost.md) | concept | trang ma để thử R3 còn cắn |\n' >> wiki/index.md
if GIT_DIR="$GD" GIT_INDEX_FILE="$GD/index" python3 "$V" --wiki-dir wiki >/dev/null 2>&1; then echo "  ✗ đối chứng âm: trang ma không bị bắt"; fail=1
else echo "  ✓ đối chứng âm: trang ma vẫn bị bắt dưới env hook"; fi
exit $fail
```

Nếu fixture index tối giản ở trên vấp luật khác của `index_sync` (định dạng bảng, cột Summary), chỉnh FIXTURE cho hợp luật, giữ nguyên ba ý kiểm: chạy thường xanh, env hook xanh, trang ma vẫn đỏ.

```yaml
      - name: r3-worktree-hook-env — R3 đúng khi chạy trong hook git của linked worktree (GIT_DIR không GIT_WORK_TREE)
        run: bash harness/tests/r3-worktree-hook-env-test.sh .
```

Lệnh kiểm (theo thứ tự, repro-first):

```bash
bash harness/tests/r3-worktree-hook-env-test.sh .     # TRƯỚC khi sửa index_sync: phải ĐỎ ở dòng "env hook"
# … sửa index_sync.py + cp sang bản deploy …
bash harness/tests/r3-worktree-hook-env-test.sh .     # SAU: 3 ✓
python3 harness/scripts/harness-lint.py --check        # --copies: 2 bản index_sync giống hệt
python3 harness/validators/index_sync.py --wiki-dir fdk/wiki && python3 harness/validators/index_sync.py --wiki-dir llmwiki/wiki
```

---

## Định nghĩa hoàn thành

- Mọi lệnh kiểm của từng task xanh; `dot-layout-runtime-test.sh` vẫn 5/5; `bare_path_lint --check` xanh.
- `python3 fdk/tools/ci-local.py` xanh, `python3 fdk/tools/medic.py --ci` 0 fail và không còn cảnh báo `backstop` khi chạy trong worktree.
- Tăng `template_version` bằng `capability-stamp.py --update`, rồi `/fdk-uat` hai pha như lượt 110926 (checklist `uat-check.sh` + dòng mới của Task A).
- Chạy lại bên B của eval A/B trên bản mới: mục tiêu golden `downstream-layout-awareness` PASS 5/5.

## Ngoài phạm vi

- 381 chỗ nợ đường trần trong baseline: trả dần khi chạm file, lint đã chặn nợ mới.
- Chế độ `--remote` của `fresh-install-smoke.sh`: vẫn cài vào HOME thật vì đó là acceptance tay dùng npx.
