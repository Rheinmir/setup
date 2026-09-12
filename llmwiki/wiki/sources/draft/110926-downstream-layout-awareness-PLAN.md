---
type: draft
title: "Downstream-layout awareness — chống ảo giác cấu trúc repo ↔ máy khách (PLAN thi hành)"
status: proposed
tags: [plan, downstream, dot-layout, hooks, ci, reachability, anti-hallucination]
timestamp: 2026-09-11
---

# Downstream-layout awareness — PLAN thi hành

**Goal:** mọi phiên dev trên repo framework phải (1) BIẾT cấu trúc mình đang nhìn (`llmwiki/` · `harness/` trần, engine nằm trong repo) KHÁC cấu trúc thật sự chạy ở máy khách (`.llmwiki/` · `.harness/` ẩn, engine ở `~/.claude/harness/`), (2) không thể ship code hook/engine ghi cứng đường trần mà CI vẫn xanh, và (3) có một bài test tất định chạy hook THẬT trong một dự án downstream THẬT (layout dot) ngay trong GitHub CI — thứ hôm nay hoàn toàn chưa có.

**Architecture:** không đổi layout nào cả. Ba đòn bẩy theo thang Meadows, từ cao xuống thấp: **đổi luật chơi** (T1 + T3: test runtime trong fixture dot + lint bare-path đều CẮN trong CI), **đổi luồng thông tin** (T5: bản đồ repo↔downstream in ở đầu phiên khi đang ở repo framework + ghi vào `/fdk`), rồi mới **sửa tham số** (T2 + T4: vá các chỗ ghi cứng đang làm hook câm). Mọi thứ tái dùng đồ có sẵn: `overstack_paths.py` (resolver), `hooklib.find_wiki_dir`, `bootstrap.sh` qua `file://`, cơ chế `tests-wired` của `harness.yml`, kiểu ratchet-baseline của capproof.

**Tech stack:** Python 3 stdlib + bash. Không dependency mới. Test theo convention `harness/tests/*-test.sh` (exit 0 = pass, tự wire vào CI bởi step `tests-wired`).

**SPEC nguồn:** chỉ thị `/goal` của user 2026-09-11 ("cấu trúc hiện tại của setup khá khác so với thứ thực sự được downstream xuống máy khách … cần một cách luôn aware và bơm đủ ngữ cảnh … check cả phần CI trên github … plan kỹ càng sao fresher cũng sửa được"). Nền: đề xuất `040926-downstream-dot-layout` (đã ship resolver + migrate) và các sự cố cùng lớp GH#106 · #111 · #112 · #113 · #149 · #153.

## Origin
- **Chỉ thị:** `/goal` phiên 2026-09-11 (user), repo `Rheinmir/setup` nhánh `orca` @ `90334c3`.
- **Đề xuất nền:** `llmwiki/wiki/sources/draft/040926-downstream-dot-layout.md` (resolver B + migrate tự động, status implementing).
- **Sự cố cùng lớp (bằng chứng vấn đề có thật, lặp 6 lần trong 1 tuần):** GH#106 (pre-commit trỏ `.harness/scripts` không tồn tại → chặn mọi commit), GH#111 (3 chỗ sinh dây ghi cứng đường trần → 0 luật cắn tầng phiên), GH#112 (glob R11/R14/R16/R19 ghi cứng segment `llmwiki`), GH#113 (check bash bỏ qua glob), GH#149 (seed chỉ ở MODE=new), GH#153 (scratch-log ghi cứng `llmwiki/` → đẻ thư mục lạc, tidy quét nhầm báo 0 draft).
- **Tái hiện THẬT trước khi viết PLAN (2026-09-11, fixture dot-layout dựng từ working-tree qua `bootstrap.sh` + `HARNESS_BASE=file://…`, `HOME` cô lập):**
  - `session_start.py` chạy với `CLAUDE_PROJECT_DIR=<fixture>`: **in 0 dòng** — kể cả khi hạ `template_version` global xuống `1.2.0` (lệch MAJOR so với stamp `1.3.88`). Nguyên nhân: `harness_integrity()` đọc `root/"llmwiki"/".harness-stamp"` (dòng 35) trong khi installer ghi stamp vào `.llmwiki/.harness-stamp`.
  - `stop.py` chạy trong fixture: không sinh `.llmwiki/html/wiki-graph.html`, không ghi session-provenance vào `.llmwiki/wiki/sources/`. Nguyên nhân: `has_stamp = os.path.isfile(os.path.join(root, "llmwiki", ".harness-stamp"))` (dòng 92 và 163).
  - Sau khi chạy hook, fixture mọc thêm **`harness/metrics/context-receipts.jsonl` TRẦN** cạnh `.harness/` — đúng lớp lỗi GH#153. Nguồn: `okf-scan.py` hằng `RECEIPTS = "harness/metrics/context-receipts.jsonl"` (dòng 44) và `self-report.py` (dòng 105).
  - CI downstream do `gen-converters.py` sinh (`.github/workflows/harness.yml` trong fixture) bước wikieval kiểm `harness/metrics/eval-baseline.json` và `llmwiki/wiki/sources/evals` (đường trần) → ở dự án dot **luôn "skip"** im lặng.
  - Đếm bằng script (regex đường trần dùng lúc chạy, trừ comment) trên tập file **thật sự đi xuống global** (`install-harness.sh --global` copy, trừ `STRIP_TIER3`): **55 file ghi cứng mà không đi qua resolver**, 17 file có resolver. Nặng nhất: `provenance-log.py` 11 · `code-logger.py` 8 · `demo.sh` 8 · `wiki-graph.py` 7 · `ci-fail-parse.py` 7.
  - `.github/workflows/harness.yml` của repo: **0 job** dựng dự án downstream layout dot rồi chạy hook/validator trong đó. `dot-layout-migrate-test.sh` chỉ test hàm migrate; `fresh-install-smoke.sh` (có assert `.llmwiki/`) chỉ chạy ở `medic` local, không có trong GitHub CI.
  - `skills/fdk/SKILL.md`: 0 lần nhắc `.llmwiki`/`.harness`/downstream layout. `skills/fdk-uat/SKILL.md` dòng 80-81 và 134 vẫn ghi tiêu chí nghiệm thu bằng đường trần (`harness/poc-vendor-neutral/policy.yaml`, `llmwiki/wiki/index.md`) — chính tài liệu UAT cũng ảo giác layout.
- **Commit:** _(verify-before-commit điền)_

## Global constraints

- **Repro-first, đúng thứ tự:** T1 (test) phải ĐỎ trên HEAD hiện tại trước khi sửa T2/T4; xanh mà chưa sửa gì = test sai, dừng lại. Ghi số đỏ/xanh vào commit message.
- **Fail-open tuyệt đối trong hook:** mọi nhánh mới trong `session_start.py` / `stop.py` / `hooklib.py` bọc `try/except Exception: pass`; hook không bao giờ được làm gãy phiên của người dùng.
- **Không đổi layout, không migrate repo framework:** repo framework giữ `llmwiki/` + `harness/` trần (installer đã hứa "có `fdk/wiki` thì KHÔNG BAO GIỜ migrate"). PLAN này chỉ làm code và tài liệu **nhận thức đúng** hai layout.
- **Một nguồn chân lý cho "đường dẫn ở đâu":** thứ tự ứng viên `.llmwiki` trước `llmwiki`, `.harness` trước `harness`, `fdk/wiki` thắng ở repo framework — đã khai trong `harness/scripts/overstack_paths.py`. Hook không import được file đó (nằm ở `~/.claude/harness/harness/scripts`, không chắc trên `sys.path`) nên `hooklib` được thêm hàm cùng thứ tự; T3 có self-test assert hai nơi cùng thứ tự để không drift.
- **Sandbox cho mọi test:** `HOME` trỏ vào `mktemp -d`; tuyệt đối không chạm `~/.claude/harness` thật của máy chạy test (khuôn có sẵn ở `ge-travel-test.sh`).
- **Không placeholder, không ghi công AI:** commit message không có `Co-Authored-By`/`Generated with` (ADR-016, R15 chặn cứng).
- **Mirror discipline:** sửa `skills/<x>/SKILL.md` thì chạy `python3 harness/scripts/sync-skills.py` để mirror `llmwiki/skills/…` khớp (CI `skills-sync` đỏ nếu quên).
- **Sau MỖI task:** `python3 fdk/tools/ci-local.py` xanh (chạy trọn step CI tại local) rồi mới sang task kế. Trước push: `/fdk-uat` canary.
- **Wire test vào CI là bắt buộc:** step `tests-wired` của `harness.yml` đã ép mọi `harness/tests/*-test.sh` phải có dòng `run:` trong workflow — thêm test mà quên wire thì CI đỏ.

## File structure

- Tạo `harness/tests/downstream-fixture.sh` — thư viện bash sourceable: dựng một dự án downstream layout dot từ working-tree, `HOME` cô lập; trả về `FX` và `GH`.
- Tạo `harness/tests/dot-layout-runtime-test.sh` — chạy hook THẬT (`session_start.py`, `stop.py`) trong fixture; assert hook không câm, không đẻ thư mục trần, CI sinh ra không chứa đường trần.
- Sửa `llmwiki/.claude/hooks/hooklib.py` — thêm `overstack_dir()`, `harness_dir()`, `stamp_path()`.
- Sửa `llmwiki/.claude/hooks/session_start.py` — `harness_integrity`, `wiki_drift`, `wikigraph_reminder` dùng resolver; thêm khối `downstream_map()` in khi ở repo framework.
- Sửa `llmwiki/.claude/hooks/stop.py` — hai chỗ `has_stamp` dùng `hooklib.stamp_path`.
- Sửa `harness/scripts/okf-scan.py` + `harness/scripts/self-report.py` — thư mục metrics đi qua `overstack_paths.harness_dir`.
- Sửa (Task 2b) `llmwiki/.claude/hooks/stop.py`, `harness/scripts/{scratch-log,provenance-log,mem-rank,mem-proxy,okf-scan,self-report}.py`, `fdk/tools/{memory-map,code-state}.py` — nơi ghi VÀ mọi nơi đọc 4 sổ metrics theo layout đang dùng; wiki-graph mặc định theo thư mục overstack.
- Tạo `harness/validators/bare_path_lint.py` — lint bare-path trên tập file đi xuống global, ratchet theo baseline.
- Tạo `harness/metrics/bare-path-baseline.json` — danh sách nợ hiện tại (số file do `--write-baseline` in ra) để lint chỉ đỏ khi nợ MỚI.
- Sửa `harness/poc-vendor-neutral/gen-converters.py` — bước wikieval của CI downstream dùng `$OVERSTACK_DIR`/`$HARNESS_DIR`.
- Sửa `harness/poc-vendor-neutral/install.sh` — truyền `OVERSTACK_OVERSTACK_DIR` sang gen-converters (cạnh `OVERSTACK_HARNESS_DIR` đã có).
- Sửa `harness/downstream-contract.yaml` — thêm block `layout_map:` (bản đồ repo ↔ downstream ↔ global, máy đọc).
- Sửa `skills/fdk/SKILL.md` + `llmwiki/skills/…/fdk.md` (mirror) — mục "Bản đồ downstream" + pre-flight #6.
- Sửa `skills/fdk-uat/SKILL.md` (+ mirror) — tiêu chí nghiệm thu dùng đường dot.
- Sửa `fdk/wiki/concepts/framework-dev-antipatterns.md` — thêm AP-7.
- Sửa `.github/workflows/harness.yml` — wire 2 step mới (runtime test + bare-path lint).

---

### Task 1 — Fixture downstream + test runtime chạy hook thật trong layout dot (ĐỎ trước, XANH sau)

**Mục tiêu:** một bài test tất định, sandbox, chạy được ở CI, chứng minh "hook global chạy ĐÚNG trong một dự án downstream thật". Đây là cái van phản hồi đang thiếu: mọi test hiện có đều chạy trong layout trần của repo.

**Thoả:** yêu cầu (3) của user — "audit thực sự cấu trúc ở máy khách mới là thứ thực sự hoạt động": test chạy hook THẬT trong dự án downstream THẬT, ngay trong CI GitHub.

**Files:**
- Tạo `harness/tests/downstream-fixture.sh`
- Tạo `harness/tests/dot-layout-runtime-test.sh`
- Sửa `.github/workflows/harness.yml` (thêm 1 step trong job `repo-health`, đặt ngay sau step `dot-layout-migrate`)

**Interfaces:**
- Consumes: `harness/poc-vendor-neutral/bootstrap.sh` (env `HARNESS_BASE`, `REPO_RAW`), `harness/scripts/install-harness.sh --global` (được `install.sh` tự gọi), `~/.claude/harness/hooks/session_start.py` và `stop.py` (bản global trong `HOME` sandbox).
- Produces: hàm bash `make_downstream_fixture <repo-root>` → set biến `FX` (gốc dự án fixture) và `GH` (`$HOME/.claude/harness` sandbox), `HOME` đã trỏ sandbox. Test exit 0 = pass, in `PASS/FAIL` từng assertion theo khuôn `ok()/bad()` của `ge-travel-test.sh`.

**Bước 1.1 — thư viện fixture** (`harness/tests/downstream-fixture.sh`):

```bash
#!/usr/bin/env bash
# downstream-fixture.sh — dựng MỘT dự án downstream layout dot từ working-tree, HOME cô lập.
# Source rồi gọi: make_downstream_fixture <repo-root>  → $FX (dự án) · $GH (global sandbox)
# Không curl mạng: bootstrap qua file:// (đúng khuôn fresh-install-smoke --local).
make_downstream_fixture() {
  local SRC; SRC="$(cd "${1:?repo-root}" && pwd)"
  FX_TMP="$(mktemp -d)"
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
```

**Bước 1.2 — test runtime** (`harness/tests/dot-layout-runtime-test.sh`):

```bash
#!/usr/bin/env bash
# dot-layout-runtime-test.sh — hook GLOBAL chạy trong dự án downstream layout DOT có làm đúng việc không.
# Bốn bất biến (mỗi cái từng gãy thật, đo 2026-09-11):
#   (a) session_start phải KÊU khi stamp lệch MAJOR với global (harness_integrity không được câm)
#   (b) stop KHÔNG được đẻ thư mục trần llmwiki/ hoặc harness/ cạnh .llmwiki/ .harness/ (GH#153)
#   (c) stop phải ghi session-provenance vào .llmwiki/wiki/sources/ (đúng cây), và vẽ wiki-graph nếu engine có
#   (d) CI sinh cho downstream không chứa đường trần llmwiki/ · harness/ ngoài harness-src và $HOME/.claude
set -uo pipefail
SRC="${1:?usage: dot-layout-runtime-test.sh <repo-root>}"
HERE="$(cd "$(dirname "$0")" && pwd)"; source "$HERE/downstream-fixture.sh"
PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  \033[1;32mPASS\033[0m  %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  \033[1;31mFAIL\033[0m  %s — %s\n' "$1" "$2"; }
make_downstream_fixture "$SRC" || exit 1
trap 'rm -rf "$FX_TMP"' EXIT

# (a) hạ global về 1.0.0 → stamp (1.3.x) lệch MAJOR → phải in dòng harness-integrity
python3 - "$GH/version.json" <<'PY'
import json,sys; p=sys.argv[1]; d=json.load(open(p)); d["template_version"]="1.0.0"; json.dump(d,open(p,"w"))
PY
OUT="$(echo '{"session_id":"t"}' | CLAUDE_PROJECT_DIR="$FX" python3 "$GH/hooks/session_start.py" 2>&1)"
grep -q "harness-integrity" <<<"$OUT" \
  && ok "(a) session_start kêu lệch MAJOR trong layout dot" \
  || bad "(a) session_start câm" "không có dòng harness-integrity — stamp đọc ở llmwiki/ trần?"

# (b)+(c) chạy stop với một wiki có nội dung
mkdir -p "$FX/.llmwiki/wiki/concepts"
printf -- '---\ntype: concept\ntitle: t\ntags: [t]\ntimestamp: 2026-09-11\nid: t\n---\n# t\n\n## Origin\n- test\n' > "$FX/.llmwiki/wiki/concepts/t.md"
echo '{"session_id":"t","stop_hook_active":false}' | CLAUDE_PROJECT_DIR="$FX" python3 "$GH/hooks/stop.py" >/dev/null 2>&1
[ ! -d "$FX/llmwiki" ] && [ ! -d "$FX/harness" ] \
  && ok "(b) không đẻ llmwiki/ hay harness/ trần" \
  || bad "(b) thư mục trần xuất hiện" "$(ls -d "$FX/llmwiki" "$FX/harness" 2>/dev/null | tr '\n' ' ')"
ls "$FX/.llmwiki/wiki/sources/"*session-provenance*.md >/dev/null 2>&1 \
  && ok "(c) session-provenance ghi vào .llmwiki/wiki/sources/" \
  || bad "(c) không có session-provenance dưới .llmwiki" "stop bỏ qua vì has_stamp đọc llmwiki/ trần?"
if [ -f "$GH/fdk/tools/build-wiki-graph.py" ]; then
  [ -f "$FX/.llmwiki/html/wiki-graph.html" ] \
    && ok "(c) wiki-graph vẽ vào .llmwiki/html/" \
    || bad "(c) wiki-graph không vẽ" "wikigraph_on=False vì stamp không thấy"
fi

# (d) CI sinh ra cho downstream: đường trần chỉ được phép trong harness-src / $HOME/.claude
CI="$FX/.github/workflows/harness.yml"
BARE="$(grep -nE '(^|[ "(=])(llmwiki|harness)/' "$CI" | grep -vE 'harness-src|HOME/\.claude|\$OVERSTACK_DIR|\$HARNESS_DIR' || true)"
[ -z "$BARE" ] \
  && ok "(d) CI downstream không có đường trần" \
  || bad "(d) CI downstream còn đường trần (skip im lặng ở dự án dot)" "$(head -3 <<<"$BARE" | tr '\n' ' ')"

printf '\ndot-layout-runtime: %d PASS · %d FAIL\n' "$PASS" "$FAIL"
[ "$FAIL" = 0 ]
```

**Bước 1.3 — wire vào CI** (`.github/workflows/harness.yml`, ngay sau step `dot-layout-migrate`):

```yaml
      - name: dot-layout-runtime — hook GLOBAL chạy trong dự án downstream layout DOT (a-d, GH#153 class)
        run: bash harness/tests/dot-layout-runtime-test.sh .
```

**Chạy + kết quả mong đợi TRÊN HEAD HIỆN TẠI (chưa sửa gì):**

```
$ bash harness/tests/dot-layout-runtime-test.sh .
  FAIL  (a) session_start câm — không có dòng harness-integrity …
  FAIL  (b) thư mục trần xuất hiện — …/harness
  FAIL  (c) không có session-provenance dưới .llmwiki — …
  FAIL  (d) CI downstream còn đường trần … — 46:[ -f harness/metrics/eval-baseline.json ] …
dot-layout-runtime: 0 PASS · 4 FAIL      (exit 1)
```

Nếu ra XANH ở bước này thì test sai — dừng, sửa test trước. Ước lượng: 45 phút.

---

### Task 2 — Vá các chỗ ghi cứng đang làm hook câm (đưa T1 a-b-c về XANH)

**Thoả:** hệ quả trực tiếp của tái hiện trong Origin — hook câm (harness_integrity, wiki-graph, provenance) và đẻ thư mục trần; sửa ở nguồn chung (resolver), không vá từng caller.

**Files:**
- Sửa `llmwiki/.claude/hooks/hooklib.py`
- Sửa `llmwiki/.claude/hooks/session_start.py` (hàm `harness_integrity`, `wiki_drift`, `wikigraph_reminder`)
- Sửa `llmwiki/.claude/hooks/stop.py` (hai dòng `has_stamp`, dòng 92 và 163)
- Sửa `harness/scripts/okf-scan.py` (hằng `RECEIPTS`, dòng 44) và `harness/scripts/self-report.py` (dòng 105, hằng `MET`)

**Interfaces:**
- Produces (hooklib, cùng thứ tự với `overstack_paths.py`):
  - `overstack_dir(root: str) -> pathlib.Path | None` — `.llmwiki` trước, `llmwiki` sau.
  - `harness_dir(root: str) -> pathlib.Path` — `.harness` trước, `harness` sau; không có cái nào thì trả `.harness` khi KHÔNG phải repo framework (thư mục mới phải theo chuẩn mới), `harness` khi là repo framework (`fdk/wiki` tồn tại).
  - `stamp_path(root: str) -> pathlib.Path | None` — `<overstack_dir>/.harness-stamp` nếu tồn tại.
- Consumes: `hooklib.scope_config` (đã có), `overstack_paths.harness_dir` (script engine đã nằm cạnh `overstack_paths.py` trong `harness/scripts/`).

**Bước 2.1 — hooklib** (thêm sau `find_wiki_dir`):

```python
# Cùng THỨ TỰ với harness/scripts/overstack_paths.py (chuẩn mới trước, cũ sau). Hook không chắc
# import được file đó (global: ~/.claude/harness/harness/scripts) nên chép thứ tự sang đây;
# harness/validators/bare_path_lint.py --self-test assert hai nơi khớp nhau.
OVERSTACK_DIRS = (".llmwiki", "llmwiki")
HARNESS_DIRS = (".harness", "harness")

def _first_dir(root, names):
    for n in names:
        c = pathlib.Path(root) / n
        if c.is_dir():
            return c
    return None

def overstack_dir(root: str):
    return _first_dir(root, OVERSTACK_DIRS)

def harness_dir(root: str) -> pathlib.Path:
    d = _first_dir(root, HARNESS_DIRS)
    if d:
        return d
    fw = (pathlib.Path(root) / "fdk" / "wiki").is_dir()
    return pathlib.Path(root) / ("harness" if fw else ".harness")

def stamp_path(root: str):
    d = overstack_dir(root)
    if d and (d / ".harness-stamp").is_file():
        return d / ".harness-stamp"
    return None
```

**Import (bắt buộc, đọc trước Bước 2.2):** `session_start.py` và `stop.py` import theo TÊN (`from hooklib import …`), không có tên `hooklib` trong file. Thêm `overstack_dir, stamp_path` vào dòng `from hooklib import` của `session_start.py`, và `stamp_path` vào dòng đó của `stop.py`. KHÔNG viết `hooklib.x(...)`: ở `stop.py` hai chỗ `has_stamp` nằm NGOÀI `try` và `main()` gọi chúng không bọc `try`, nên `NameError` làm sập cả hook Stop ở mọi dự án khách.

**Bước 2.2 — session_start.py:**

```python
# harness_integrity(): thay dòng  stamp_p = root / "llmwiki" / ".harness-stamp"
stamp_p = stamp_path(str(root))
if stamp_p is None:
    return
# và trong 2 chuỗi cảnh báo, thay chữ 'llmwiki/.harness-stamp' bằng f'{stamp_p.relative_to(root)}'

# wiki_drift(): thay  for wd in (root / "llmwiki" / "wiki", root / "wiki"): … continue  bằng khối dò neo
# theo thứ tự nơi GHI neo (wiki-sync.py: llmwiki/wiki rồi wiki/) + layout dot. KHÔNG dùng find_wiki_dir ở đây:
# nó trả fdk/wiki trước ở repo framework, nơi không có neo → dòng nhắc [wiki-sync] câm (đính chính 2026-09-11).
od = overstack_dir(str(root))
anchor = None
for wd in ((od / "wiki") if od else None, root / "wiki"):
    if wd is not None and (wd / ".last-sync.json").is_file():
        anchor = wd / ".last-sync.json"
        break
if anchor is None:
    return
# (phần head / rev-list / print bên dưới giữ nguyên)

# wikigraph_reminder(): thay  wiki = root / "llmwiki" / "wiki"  và  graph = root / "llmwiki" / "html" / "wiki-graph.html"
od = overstack_dir(str(root))
if od is None:
    return
wiki = od / "wiki"
graph = od / "html" / "wiki-graph.html"
# và trong lệnh gợi ý:  f"python3 {wg} {wiki.relative_to(root)} --code-root ."
```

**Bước 2.3 — stop.py** (hai chỗ giống nhau, dòng 92 và dòng 163):

```python
has_stamp = stamp_path(root) is not None
```

**Bước 2.4 — okf-scan.py / self-report.py:**

```python
# okf-scan.py dòng 44 — thay hằng chuỗi bằng hàm
from overstack_paths import harness_dir
def receipts_path(root):
    return harness_dir(root) / "metrics" / "context-receipts.jsonl"
# mọi chỗ dùng RECEIPTS → receipts_path(root); mkdir(parents=True, exist_ok=True) trước khi ghi

# self-report.py dòng 105 — MET là "harness/metrics" cứng
from overstack_paths import harness_dir
rec = _jsonl(harness_dir(root) / "metrics" / "context-receipts.jsonl")
```

Lưu ý: `overstack_paths.harness_dir()` hiện trả `None` khi chưa có thư mục nào; T2 thêm nhánh mặc định giống hooklib (dot khi không phải repo framework) để hai bên cùng hành vi:

```python
# overstack_paths.py — sửa harness_dir()
def harness_dir(root):
    d = _first_dir(root, HARNESS_DIRS)
    if d:
        return d
    return pathlib.Path(root) / ("harness" if is_framework_repo(root) else ".harness")
```

**Chạy + kết quả mong đợi:**

```
$ python3 harness/scripts/overstack_paths.py --self-test        → self-test: PASS
$ bash harness/tests/scope-config-test.sh .                    → PASS (find_wiki_dir không đổi)
$ bash harness/tests/dot-layout-runtime-test.sh .
  PASS  (a) … PASS  (b) … PASS  (c) session-provenance … PASS  (c) wiki-graph …
  FAIL  (d) CI downstream còn đường trần        ← còn lại cho Task 4
$ bash harness/tests/stop-hook-all-wikis-test.sh . ; bash harness/tests/wiki-graph-user-reachability-test.sh .   → PASS cả hai
```

Ước lượng: 60 phút.

---

### Task 2b — Dời 4 sổ metrics của chuỗi hook Stop theo layout đang dùng (phát sinh từ review)

**Thoả:** tiêu chí (b) và (c)-wiki-graph của Task 1 — hook không đẻ thư mục trần, wiki-graph vẽ được ở dự án khách. Hai lỗi này chỉ lộ ra sau khi fixture được sửa để test code local (xem "Đính chính sau review dispatch", mục 5).

**Mục tiêu:** sau Task 2, chạy hook Stop trong fixture dot vẫn đẻ `harness/metrics/{.stop-debounce.json, memory.jsonl, provenance-log.jsonl, scratch-log.jsonl}` trần (còn `.harness/metrics` trống), và wiki-graph không vẽ vì `_scope_config` mặc định `llmwiki/wiki` còn `build-wiki-graph.py` mặc định output `llmwiki/html`. Dời cả nơi GHI lẫn MỌI nơi ĐỌC của bốn sổ trong cùng một lượt: dời một nửa thì dự án khách lặng lẽ mất dữ liệu. Ở repo framework `harness_dir()` luôn trả `harness/` nên hành vi ở đó không đổi.

**Files:**
- Sửa `llmwiki/.claude/hooks/stop.py` — đường debounce, wiki mặc định của `_scope_config`, output wiki-graph.
- Sửa `harness/scripts/scratch-log.py` — hằng `LOG` (dòng `LOG = ROOT / "harness" / "metrics" / "scratch-log.jsonl"`).
- Sửa `harness/scripts/provenance-log.py` — dòng `return Path(root) / EVENTS_PATH_REL`.
- Sửa `harness/scripts/mem-rank.py` — `_store_file()` và `_ensure_gitignored()`.
- Sửa `harness/scripts/mem-proxy.py` — dòng `store = root / "harness" / "metrics" / "memory.jsonl"`.
- Sửa `harness/scripts/okf-scan.py` — mọi chỗ dựng đường từ hằng `MEMORY`.
- Sửa `harness/scripts/self-report.py` — dòng đọc `root / MET / "memory.jsonl"`.
- Sửa `fdk/tools/memory-map.py` — hai chỗ đọc `harness/metrics/scratch-log.jsonl` và `harness/metrics/memory.jsonl`.
- Sửa `fdk/tools/code-state.py` — chỗ `_lines("harness/metrics/scratch-log.jsonl")`.

**Interfaces:**
- Consumes: `hooklib.harness_dir`, `hooklib.overstack_dir` (Task 2); `overstack_paths.harness_dir` (Task 2, trả `.harness` khi chưa có thư mục nào và không phải repo framework).
- Produces: mỗi script có hàm nội bộ `_metrics_dir(root) -> Path`, fallback `root/harness/metrics` khi không import được `overstack_paths` (bản cài cũ). Không đổi CLI. Không xoá hằng đang được test hoặc `.gitattributes` tham chiếu (`EVENTS_PATH_REL`, `MEMORY` nếu còn dùng).

**Bước 2b.1 — `stop.py`:**

```python
# dòng `from hooklib import …`: thêm harness_dir, overstack_dir

# thay dòng  _DEBOUNCE_STATE = "harness/metrics/.stop-debounce.json"  bằng:
def _debounce_path(root: str) -> str:
    """.harness/metrics ở dự án khách, harness/metrics ở repo framework (hooklib.harness_dir)."""
    return os.path.join(str(harness_dir(root)), "metrics", ".stop-debounce.json")
# trong _debounce_state() và _debounce_mark(): thay  path = os.path.join(root, _DEBOUNCE_STATE)  bằng  path = _debounce_path(root)

def _scope_config(root: str):
    """GH#49 — MỘT nguồn: hooklib.scope_config(). Fallback = <thư mục overstack đang dùng>/wiki
    (.llmwiki ở dự án khách, llmwiki ở repo framework) + '.'."""
    c = scope_config(root)
    od = overstack_dir(root)
    return c["wiki_dir"] or (f"{od.name}/wiki" if od else "llmwiki/wiki"), c["code_root"] or "."

# lời gọi build-wiki-graph trong regen_docs(): engine mặc định ghi vào llmwiki/html (cứng) → truyền -o
            od = overstack_dir(root)
            out = ["-o", str(od / "html" / "wiki-graph.html")] if od else []
            subprocess.run([sys.executable, wg, wiki_dir, *also, "--code-root", code_root, *out],
                           cwd=root, capture_output=True, timeout=90)
```

**Bước 2b.2 — khuôn cho script trong `harness/scripts/`** (`overstack_paths.py` nằm cùng thư mục; ở bản global cũng vậy). Đặt ngay sau các dòng import của file; `okf-scan.py` và `self-report.py` đã có `harness_dir` từ Task 2 thì chỉ thêm `_metrics_dir`:

```python
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from overstack_paths import harness_dir as _harness_dir
except Exception:          # bản cài cũ thiếu overstack_paths → giữ hành vi cũ
    _harness_dir = None


def _metrics_dir(root) -> Path:
    return (_harness_dir(root) if _harness_dir else Path(root) / "harness") / "metrics"
```

Thay thế cụ thể:

```python
# scratch-log.py
LOG = _metrics_dir(ROOT) / "scratch-log.jsonl"
# provenance-log.py (trong hàm đang `return Path(root) / EVENTS_PATH_REL`)
    return _metrics_dir(root) / "provenance-log.jsonl"
# mem-rank.py
def _store_file(root: Path) -> Path:
    return _metrics_dir(root) / "memory.jsonl"
#   _ensure_gitignored(): mkdir  _metrics_dir(root);  rel = _store_file(root).relative_to(root).as_posix()
#   và dùng `rel` thay cho chuỗi "harness/metrics/memory.jsonl" ở cả phép kiểm lẫn dòng ghi .gitignore
# mem-proxy.py
    store = _metrics_dir(root) / "memory.jsonl"
# okf-scan.py — mọi `root / MEMORY` → `_metrics_dir(root) / "memory.jsonl"`;
#   chuỗi hiển thị f"{MEMORY}#{...}" → f"{(_metrics_dir(root) / 'memory.jsonl').relative_to(root).as_posix()}#{...}"
# self-report.py
    eps = [x for x in _jsonl(_metrics_dir(root) / "memory.jsonl") if x.get("kind") == "episode"]
```

**Bước 2b.3 — `fdk/tools/memory-map.py` và `fdk/tools/code-state.py`** (`overstack_paths.py` KHÔNG cùng thư mục: repo có `harness/scripts/`, bản global có `~/.claude/harness/harness/scripts/`). Tìm theo mốc trên đĩa, fallback hành vi cũ:

```python
import sys
from pathlib import Path
for _c in Path(__file__).resolve().parents:
    if (_c / "harness" / "scripts" / "overstack_paths.py").is_file():
        sys.path.insert(0, str(_c / "harness" / "scripts"))
        break
try:
    from overstack_paths import harness_dir as _harness_dir
except Exception:
    _harness_dir = None


def _metrics_dir(root) -> Path:
    return (_harness_dir(root) if _harness_dir else Path(root) / "harness") / "metrics"
```

Hai file này đang dựng đường TƯƠNG ĐỐI theo thư mục đang đứng, nên gốc là `Path.cwd()`: `Path("harness/metrics/memory.jsonl")` → `_metrics_dir(Path.cwd()) / "memory.jsonl"`. Với `_read("harness/metrics/scratch-log.jsonl")` và `_lines("harness/metrics/scratch-log.jsonl")`: đọc thân `_read`/`_lines` trước. Nếu hàm mở thẳng đường được truyền thì truyền `str(_metrics_dir(Path.cwd()) / "scratch-log.jsonl")`. Nếu hàm tự nối với một biến gốc thì truyền `(_metrics_dir(<gốc đó>) / "scratch-log.jsonl").relative_to(<gốc đó>).as_posix()`. Chuỗi chỉ để HIỂN THỊ (vd gợi ý `wc -l harness/metrics/…`) giữ nguyên.

**Chạy + kết quả mong đợi:**

```bash
bash harness/tests/dot-layout-runtime-test.sh .
#   PASS (a) · PASS (b) · PASS (c) session-provenance · PASS (c) wiki-graph · FAIL (d)   ← (d) thuộc Task 4
for t in $(cat <danh-sách-test-liên-quan>); do bash "$t" . >/dev/null 2>&1; echo "$t rc=$?"; done
#   rc phải BẰNG mốc đo trên HEAD; test vốn đỏ ở HEAD không tính là hồi quy
python3 harness/scripts/okf-scan.py --self-test; python3 harness/scripts/provenance-log.py --self-test
```

Ước lượng: 60 phút.

---

### Task 3 — Lint bare-path CẮN trong CI, ratchet theo baseline (nợ mới đỏ, nợ tồn đếm)

**Mục tiêu:** không ai ship thêm được một file đi-xuống-global mà ghi cứng `llmwiki/` · `harness/` lúc chạy. 55 file nợ cũ được ghi vào baseline; sửa được file nào thì baseline giảm; thêm nợ mới → CI đỏ chỉ đích danh file + dòng.

**Thoả:** yêu cầu (2) của user — "không thể ship code kiểm định dựa trên cấu trúc repo": lint đổi luật chơi, CI đỏ khi có nợ bare-path MỚI trong file đi xuống global.

**Files:**
- Tạo `harness/validators/bare_path_lint.py`
- Tạo `harness/metrics/bare-path-baseline.json` (sinh bằng `--write-baseline`)
- Sửa `.github/workflows/harness.yml` (1 step trong `repo-health`, sau step `harness-lint`)

**Interfaces:**
- CLI: `python3 harness/validators/bare_path_lint.py --root . [--check | --write-baseline | --self-test]`. Exit 0 = không nợ mới; 2 = có nợ mới (in `file:line: <dòng>`); `--self-test` không đọc repo.
- Consumes: `harness/scripts/install-harness.sh` (đọc `STRIP_TIER3="…"` bằng regex, đúng cách `ge-travel-test.sh` đã làm) để biết tập file đi xuống global; `hooklib.OVERSTACK_DIRS/HARNESS_DIRS` và `overstack_paths.OVERSTACK_DIRS/HARNESS_DIRS` để assert parity.
- Produces: baseline JSON `{"schema":1, "files": {"harness/scripts/provenance-log.py": 11, …}}`.

**Bước 3.1 — validator:**

```python
#!/usr/bin/env python3
"""bare_path_lint — file ĐI XUỐNG GLOBAL không được ghi cứng đường trần llmwiki/ · harness/ lúc chạy.

Vì sao: repo framework để llmwiki/ + harness/ trần, downstream là .llmwiki/ + .harness/ (installer
migrate, resolver overstack_paths chấp cả hai). Code viết trong repo chạy đúng ở repo, xuống máy
khách thì câm/đẻ thư mục lạc (GH#111 #112 #153, đo 2026-09-11: 55 file). Lint này là van CI:
nợ cũ nằm trong baseline (ratchet), nợ MỚI đỏ ngay.
Miễn: dòng comment; dòng đánh dấu `# bare-path: ok <lý do>` (ngoại lệ HIỆN, grep được).
KHÔNG miễn theo cả file: file đã import resolver vẫn có thể còn literal trần (đo 2026-09-11:
okf-scan.py import overstack_paths nhưng hằng MEMORY vẫn trần). Baseline ratchet đếm hết.
"""
import json, re, sys
from pathlib import Path

BARE = re.compile(r'''(?<![\w./~-])["'(]?(?:llmwiki|harness)/(?:wiki|html|raw|\.harness-stamp|\.claude|metrics|scripts|validators|poc-vendor-neutral|evals|scratch-log|personas)''')
OK_MARK = "# bare-path: ok"

def strip_tier3(root):
    s = (root / "harness/scripts/install-harness.sh").read_text(encoding="utf-8")
    m = re.search(r'STRIP_TIER3="(.*?)"', s, re.S)
    return {x.strip() for x in (m.group(1).split() if m else [])}

def shipped_files(root):
    t3 = strip_tier3(root)
    pats = ["llmwiki/.claude/hooks/*.py", "llmwiki/.claude/hooks/validators/*.py",
            "harness/validators/*.py", "harness/scripts/*.py", "fdk/tools/*.py",
            "harness/poc-vendor-neutral/bin/*.py", "harness/poc-vendor-neutral/*.sh"]
    out = []
    for p in pats:
        out += [f for f in root.glob(p) if f.relative_to(root).as_posix() not in t3]
    return sorted(set(out))

def scan_file(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    hits = []
    for i, ln in enumerate(text.splitlines(), 1):
        s = ln.strip()
        if s.startswith("#") or OK_MARK in ln:
            continue
        if BARE.search(ln):
            hits.append((i, s[:100]))
    return hits

def scan(root):
    return {f.relative_to(root).as_posix(): scan_file(f) for f in shipped_files(root)}

def parity(root):
    """Thứ tự ứng viên ở hooklib phải khớp overstack_paths — hai nguồn cùng một sự thật."""
    import importlib.util
    def load(p, n):
        spec = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
    a = load(root / "harness/scripts/overstack_paths.py", "op")
    b = load(root / "llmwiki/.claude/hooks/hooklib.py", "hl")
    # Thiếu hằng ở một bên (vd hooklib chưa có Task 2) → coi là LỆCH, báo rõ, không traceback.
    return all(getattr(a, k, None) is not None and getattr(a, k, None) == getattr(b, k, None)
               for k in ("OVERSTACK_DIRS", "HARNESS_DIRS"))

def self_test():
    import tempfile
    t = Path(tempfile.mkdtemp())
    (t / "a.py").write_text('p = "llmwiki/wiki/x.md"\n')
    (t / "b.py").write_text('from overstack_paths import wiki_dir\np = "llmwiki/wiki/x.md"\n')
    (t / "c.py").write_text('# llmwiki/wiki chỉ là comment\nq = 1\n')
    (t / "d.py").write_text('p = "llmwiki/wiki/x.md"  # bare-path: ok fixture demo\n')
    assert scan_file(t / "a.py") == [(1, 'p = "llmwiki/wiki/x.md"')], "bare literal phải bị bắt"
    assert scan_file(t / "b.py") == [(2, 'p = "llmwiki/wiki/x.md"')], "file có import resolver KHÔNG được miễn theo file"
    assert scan_file(t / "c.py") == [], "comment không tính"
    assert scan_file(t / "d.py") == [], "đánh dấu ok được miễn"
    print("self-test: PASS"); return 0

def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    root = Path(args[args.index("--root") + 1] if "--root" in args else ".").resolve()
    base_p = root / "harness/metrics/bare-path-baseline.json"
    found = {k: v for k, v in scan(root).items() if v}
    if "--write-baseline" in args:
        base_p.write_text(json.dumps({"schema": 1, "files": {k: len(v) for k, v in found.items()}}, indent=1, ensure_ascii=False) + "\n")
        print(f"baseline: {len(found)} file · {sum(len(v) for v in found.values())} chỗ"); return 0
    base = json.loads(base_p.read_text())["files"] if base_p.is_file() else {}
    new = {k: v for k, v in found.items() if len(v) > base.get(k, 0)}
    if not parity(root):
        print("✗ hooklib.OVERSTACK_DIRS/HARNESS_DIRS lệch overstack_paths — sửa cho khớp"); return 2
    if new:
        for k, v in new.items():
            for ln, s in v:
                print(f"{k}:{ln}: {s}")
        print(f"\n✗ {len(new)} file có NỢ MỚI bare-path (đi xuống global). Dùng overstack_paths.* / hooklib.*; "
              f"ngoại lệ thật thì đánh dấu `{OK_MARK} <lý do>`."); return 2
    fixed = {k: base[k] - len(found.get(k, [])) for k in base if base[k] > len(found.get(k, []))}
    if fixed:
        print(f"↓ trả nợ ở {len(fixed)} file — chạy --write-baseline để chốt: {' '.join(fixed)}")
    print(f"✓ bare-path: không nợ mới ({len(found)} file nợ tồn, baseline {len(base)})"); return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Bước 3.2 — baseline + wire:**

```bash
python3 harness/validators/bare_path_lint.py --self-test          # self-test: PASS
python3 harness/validators/bare_path_lint.py --root . --write-baseline
#  baseline: <N> file · <M> chỗ  (N, M do lệnh in ra; lớn hơn con số 55 file đo lúc lập PLAN vì không còn miễn theo file)
python3 harness/validators/bare_path_lint.py --root . --check      # exit 0
```

```yaml
      - name: bare-path-lint — file đi xuống global không ghi cứng llmwiki/ · harness/ (ratchet, nợ mới đỏ)
        run: python3 harness/validators/bare_path_lint.py --root . --check
```

**Negative control (bắt buộc làm, không commit):** thêm dòng `x = "llmwiki/wiki/z.md"` vào `harness/scripts/hub.py` → `--check` phải exit 2 và in `harness/scripts/hub.py:<n>: …`; gỡ dòng đó → exit 0. Ước lượng: 60 phút.

---

### Task 4 — CI downstream sinh ra phải theo layout (đưa T1-d về XANH)

**Thoả:** yêu cầu "check cả phần CI trên github" — CI sinh cho máy khách phải chạy theo layout dot, không skip im lặng.

**Files:**
- Sửa `harness/poc-vendor-neutral/gen-converters.py` (dòng 29 thêm `OVERSTACK_DIR`; khối wikieval dòng ~188; dòng 254 `add-paths`)
- Sửa `harness/poc-vendor-neutral/install.sh` (dòng 143: truyền thêm env)

**Interfaces:**
- Consumes: env `OVERSTACK_OVERSTACK_DIR` (mặc định `llmwiki`) cạnh `OVERSTACK_HARNESS_DIR` (đã có, mặc định `harness`).
- Produces: `out/ci/harness.yml` với `env: OVERSTACK_DIR: <.llmwiki|llmwiki>` và `HARNESS_DIR: <.harness|harness>`; mọi đường trong step `run:` dùng `$OVERSTACK_DIR` / `$HARNESS_DIR`.

**Bước 4.1 — gen-converters.py:**

```python
HARNESS_DIR = os.environ.get("OVERSTACK_HARNESS_DIR", "harness")
OVERSTACK_DIR = os.environ.get("OVERSTACK_OVERSTACK_DIR", "llmwiki")
# trong template CI, khối env: thêm hai dòng
#   OVERSTACK_DIR: {OVERSTACK_DIR}
#   HARNESS_DIR: {HARNESS_DIR}
# khối wikieval: thay từng đường trần
#   [ -f "$HARNESS_DIR/metrics/eval-baseline.json" ] || { echo "no eval baseline — skip"; exit 0; }
#   E=$(ls -d "$OVERSTACK_DIR/wiki/sources/evals" fdk/wiki/sources/evals 2>/dev/null | head -1)
#   [ -f "$HARNESS_DIR/scripts/wikieval-collect.py" ] && python3 "$HARNESS_DIR/scripts/wikieval-collect.py" > "$HARNESS_DIR/evals/wikieval-outputs.json"
#   [ -f "$HARNESS_DIR/evals/wikieval-outputs.json" ] || { echo "no candidate outputs — skip"; exit 0; }
#   … --baseline "$HARNESS_DIR/metrics/eval-baseline.json" --config "$HARNESS_DIR/wikieval.config.yaml" --outputs "$HARNESS_DIR/evals/wikieval-outputs.json" --check
# dòng 254 (add-paths: llmwiki/wiki)  →  add-paths: {OVERSTACK_DIR}/wiki
```

**Bước 4.2 — install.sh dòng 143:**

```bash
( cd "$DEST" && OVERSTACK_HARNESS_DIR="$HARNESS_DIR" OVERSTACK_OVERSTACK_DIR="$OVERSTACK_DIR" python3 gen-converters.py >/dev/null )
```

**Chạy + kết quả mong đợi:**

```
$ ( cd harness/poc-vendor-neutral && python3 gen-converters.py >/dev/null ) && bash harness/tests/downstream-firedrill-test.sh .   → PASS (repo framework: env mặc định llmwiki/harness, không đổi hành vi)
$ bash harness/tests/dot-layout-runtime-test.sh .   → 5 PASS · 0 FAIL
$ bash harness/tests/policy-converters-drift-test.sh   → PASS
```

Ước lượng: 40 phút.

---

### Task 5 — Bơm ngữ cảnh: bản đồ repo ↔ downstream ở đầu phiên (repo framework) + `/fdk` + AP-7 + fdk-uat

**Mục tiêu:** một phiên mở repo framework phải thấy ngay bản đồ 5 dòng, và `/fdk` (front-door dev framework) phải có mục bắt buộc. Nguồn chân lý máy-đọc đặt ở `harness/downstream-contract.yaml` (file đã là "sự thật downstream"), hook và tài liệu đọc từ đó.

**Thoả:** yêu cầu (1) của user — "luôn aware và bơm đủ ngữ cảnh": bản đồ repo↔downstream in đầu phiên ở repo framework, ghi vào /fdk, /fdk-uat và AP-7.

**Files:**
- Sửa `harness/downstream-contract.yaml` (thêm block `layout_map:`)
- Sửa `llmwiki/.claude/hooks/session_start.py` (thêm hàm `downstream_map`, gọi trong `main()` ngay sau `orient(root)`)
- Sửa `skills/fdk/SKILL.md` (mục mới + pre-flight #6) → `python3 harness/scripts/sync-skills.py`
- Sửa `skills/fdk-uat/SKILL.md` dòng 80, 81, 134 (đường dot) → sync-skills
- Sửa `fdk/wiki/concepts/framework-dev-antipatterns.md` (AP-7)

**Interfaces:**
- `downstream-contract.yaml` block:

```yaml
# BẢN ĐỒ LAYOUT — repo framework nhìn thấy gì ↔ máy khách thật sự có gì. session_start in khối này
# khi đang ở repo framework (nhận diện fdk/wiki); /fdk chép lại; bare_path_lint gác code.
layout_map:
  - {repo: "llmwiki/",                 downstream: ".llmwiki/",                    note: "wiki + raw + html + .harness-stamp (installer migrate, resolver chấp cả hai)"}
  - {repo: "harness/",                 downstream: ".harness/",                    note: "chỉ poc-vendor-neutral + foundation.yaml + metrics; KHÔNG có scripts/ validators/ (U10 gỡ)"}
  - {repo: "harness/scripts, harness/validators, fdk/tools, llmwiki/.claude/hooks", downstream: "~/.claude/harness/{harness,fdk,hooks}/", note: "engine GLOBAL dùng chung mọi dự án; hook fire từ ~/.claude/settings.json, guard theo .harness-stamp"}
  - {repo: "fdk/wiki/ (wiki của framework)", downstream: "(không có)",             note: "framework_only — downstream chỉ có .llmwiki/wiki của chính nó"}
  - {repo: "skills/*/SKILL.md",         downstream: "~/.claude/skills/ (npx skills add)", note: "không nằm trong repo dự án"}
  - {repo: "(không có)",                downstream: "CAPABILITIES.md · .overstack.yaml · .claude/settings.json (root)", note: "chỉ tồn tại ở downstream — code framework đọc phải chấp vắng mặt"}
```

- `session_start.downstream_map(root)`: in khi `(root/"fdk"/"wiki").is_dir()`; đọc `harness/downstream-contract.yaml` bằng parser dòng đơn giản (không pyyaml, fail-open), in tối đa 6 dòng + 1 dòng luật.

**Bước 5.1 — session_start.py:**

```python
def downstream_map(root: Path) -> None:
    """Chỉ ở REPO FRAMEWORK: nhắc layout đang nhìn KHÁC layout máy khách. Không phải context FDK
    (ADR-004) — đây là orientation 7 dòng chống ảo giác đường dẫn, đo 2026-09-11 (hook câm ở dot)."""
    try:
        if not (root / "fdk" / "wiki").is_dir():
            return
        rows = []
        for ln in (root / "harness" / "downstream-contract.yaml").read_text(encoding="utf-8").splitlines():
            m = re.match(r'\s*-\s*\{repo:\s*"([^"]*)",\s*downstream:\s*"([^"]*)"', ln)
            if m:
                rows.append(f"  {m.group(1):<52} → {m.group(2)}")
        if not rows:
            return
        print("🗺 [downstream-map] Đây là REPO FRAMEWORK — layout máy khách KHÁC cái bạn đang thấy:")
        print("\n".join(rows[:6]))
        print("  LUẬT: code/hook/CI chạm downstream KHÔNG ghi cứng llmwiki/ · harness/ — dùng overstack_paths.* / hooklib.*;"
              " test trong fixture dot: bash harness/tests/dot-layout-runtime-test.sh .")
    except Exception:
        pass
```

**Bước 5.2 — `skills/fdk/SKILL.md`**, chèn mục mới ngay sau "## Pre-flight" và thêm dòng pre-flight:

```markdown
6. **Layout máy khách ≠ layout repo** — trước khi chạm path trong hook/engine/installer/CI: đọc mục "Bản đồ downstream" bên dưới; đường trần `llmwiki/` `harness/` CHỈ đúng trong repo này.

## Bản đồ downstream — cái bạn đang thấy KHÔNG phải cái chạy ở máy khách
| Repo framework (đang mở) | Máy khách sau `curl bootstrap.sh` | Ghi chú |
|---|---|---|
| `llmwiki/` | `.llmwiki/` | wiki · raw · html · `.harness-stamp` |
| `harness/` | `.harness/` | chỉ `poc-vendor-neutral/` + `foundation.yaml` + `metrics/`; KHÔNG có `scripts/` `validators/` |
| `harness/scripts` · `harness/validators` · `fdk/tools` · `llmwiki/.claude/hooks` | `~/.claude/harness/` (global) | engine dùng chung; hook fire từ `~/.claude/settings.json` |
| `fdk/wiki/` | không có | framework_only |
| `skills/*/SKILL.md` | `~/.claude/skills/` | qua npx, không nằm trong repo dự án |
| không có | `CAPABILITIES.md` · `.overstack.yaml` · root `.claude/settings.json` | chỉ có ở downstream |

Nguồn máy-đọc: `harness/downstream-contract.yaml` → `layout_map`. Luật: path chạm downstream đi qua `harness/scripts/overstack_paths.py` (engine) hoặc `hooklib.overstack_dir/harness_dir/stamp_path` (hook); `bare_path_lint` đỏ nếu ghi cứng. Test hành vi thật: `bash harness/tests/dot-layout-runtime-test.sh .` (fixture dot, HOME cô lập). Nhớ: `rg`/Grep bỏ qua thư mục dấu chấm — dùng `--hidden` khi soi dự án downstream.
```

**Bước 5.3 — `skills/fdk-uat/SKILL.md`** (dòng 80-81, 134): thay `harness/poc-vendor-neutral/policy.yaml` → `.harness/poc-vendor-neutral/policy.yaml`, `llmwiki/wiki/index.md` → `.llmwiki/wiki/index.md`, `bash harness/poc-vendor-neutral/test-broad.sh` → `bash .harness/poc-vendor-neutral/test-broad.sh`; thêm một tiêu chí: "không tồn tại `llmwiki/` hay `harness/` trần ở gốc dự án UAT".

**Bước 5.4 — AP-7** (`fdk/wiki/concepts/framework-dev-antipatterns.md`, thêm trước `## Origin`):

```markdown
## AP-7 · "Layout hallucination" — code viết theo cây repo framework, chạy trên cây máy khách

**Triệu chứng.** Hook/engine xanh hết trong repo, xuống máy khách thì câm (không kêu lệch version, không vẽ graph, không ghi provenance) hoặc đẻ thư mục lạc `llmwiki/` `harness/` cạnh `.llmwiki/` `.harness/`. Không lỗi, không cảnh báo.

**Vì sao sập.** Repo framework KHÔNG BAO GIỜ migrate (cố ý) nên mọi phiên dev chỉ nhìn thấy layout trần; agent quét/CRUD/viết test theo cái nó thấy. Đo 2026-09-11: 55 file đi xuống global ghi cứng đường trần; `session_start.harness_integrity` + `stop.has_stamp` đọc `llmwiki/.harness-stamp` trong khi installer ghi `.llmwiki/.harness-stamp`. Sáu sự cố cùng lớp trong một tuần (GH#106 #111 #112 #113 #149 #153).

**Cách chặn.** (1) Đường dẫn qua một nguồn: `overstack_paths.*` / `hooklib.*`; `bare_path_lint` đỏ khi ghi cứng. (2) Test hành vi trong fixture dot THẬT: `dot-layout-runtime-test.sh` (CI). (3) Đầu phiên ở repo framework in `[downstream-map]`; `/fdk` có mục "Bản đồ downstream". Liên hệ [[AP-1]] (reachability) và [[AP-6]] (test tự chống đỡ tín hiệu): AP-7 là test/code tự chống đỡ *cây thư mục*.
```

**Chạy + kết quả mong đợi:**

```
$ echo '{"session_id":"t"}' | CLAUDE_PROJECT_DIR=$PWD python3 llmwiki/.claude/hooks/session_start.py | grep -A7 downstream-map
🗺 [downstream-map] Đây là REPO FRAMEWORK — layout máy khách KHÁC cái bạn đang thấy:
  llmwiki/                                             → .llmwiki/
  …
$ bash harness/tests/dot-layout-runtime-test.sh .   (fixture KHÔNG phải repo framework → không in downstream-map; grep -c downstream-map = 0)
$ python3 harness/scripts/sync-skills.py --check && python3 harness/scripts/skill-registry.py --check   → OK
$ python3 harness/validators/agent_claude_parity.py   → OK
```

Ước lượng: 60 phút.

---

### Task 6 — Nghiệm thu đầu-cuối + chốt

**Thoả:** Global constraint "sau MỖI task ci-local xanh, trước push /fdk-uat canary" + định nghĩa hoàn thành; số đỏ→xanh của T1 phải được ghi lại làm bằng chứng.

**Files:**
- Sửa `harness/metrics/bare-path-baseline.json` — chốt lại sau khi T2 trả nợ (chạy `--write-baseline` lần cuối).
- Sửa `llmwiki/wiki/sources/ISSUES.md` — thêm dòng ledger cho issue ratchet nợ tồn (qua `/raise-issue`).

**Interfaces:**
- Consumes: `fdk/tools/ci-local.py`, `fdk/tools/medic.py --ci`, skill `/fdk-uat` (canary + main-URL smoke).
- Produces: commit message có số đỏ→xanh của T1; issue GH mới (qua `/raise-issue`) "trả nợ 50 file bare-path theo ratchet" trỏ tới baseline.

**Bước 6.1:**

```bash
python3 fdk/tools/ci-local.py                    # mọi step run: của harness.yml + skills-sync.yml xanh
python3 fdk/tools/medic.py --ci                  # cổng push, gồm probe freshinstall (--local)
bash harness/tests/dot-layout-runtime-test.sh .  # 5 PASS · 0 FAIL
python3 harness/validators/bare_path_lint.py --root . --check   # ✓ không nợ mới
```

**Bước 6.2 — UAT thật:** gọi `/fdk-uat` (pha canary: đẩy nhánh `uat/<ts>`, curl bootstrap từ raw nhánh đó vào dự án trống, kiểm bằng tiêu chí ĐÃ SỬA ở T5.3 — đường dot; rồi pha main-URL smoke sau merge). Kết quả phải chép vào commit/PR body đúng số.

**Bước 6.3 — commit theo task**, ví dụ thông điệp:

```
feat(harness): dot-layout-runtime test + bare-path lint — hook global chạy đúng ở máy khách (T1 0/4 → 5/5)
```

Ước lượng: 45 phút (không tính chờ CI).

---

## Đính chính sau review dispatch (2026-09-11)

Task 1 và Task 2 đã được giao cho opencode (`opencode/mimo-v2.5-free`) và review bằng cách tự chạy lại. Review tìm ra ba lỗi của CHÍNH PLAN này. Các bước ở trên đã được sửa theo; mục này giữ lại bằng chứng.

1. **Fixture test code REMOTE.** `bootstrap.sh` chỉ tải lõi vào thư mục tạm; `install.sh` tải `install-harness.sh` qua `REPO_RAW`; bản đó thiếu bundle nên clone `rheinmir/setup@orca`. Đo: hook `session_start.py` global trong fixture có 0 lần `stamp_path`, bản worktree có 2, sha khác nhau; sau khi vá Task 2, test vẫn 0 PASS · 5 FAIL. Sửa: Bước 1.1 cài đè global từ working tree và `cmp` hook global với bản worktree. Cùng bệnh ở `harness/scripts/fresh-install-smoke.sh --local` (cổng `freshinstall` của `medic`): cài qua cùng đường, lại soi global ở `$HOME` THẬT — việc tiếp theo, ngoài PLAN này.
2. **`hooklib.x(...)` gây `NameError`.** Hai hook import theo tên; `stop.py` gọi `regen_docs`/`secondary_memory` không bọc `try`. Sửa: mục Import ở Task 2.
3. **`wiki_drift` dùng `find_wiki_dir`.** Neo `.last-sync.json` nằm ở `llmwiki/wiki/` (nơi `wiki-sync.py` ghi), còn `find_wiki_dir` trả `fdk/wiki` ở repo framework → nhắc `[wiki-sync]` câm. Sửa: dò neo theo thứ tự nơi ghi. Cùng lớp lỗi, ngoài PLAN: `wiki-sync.py::detect_wiki_dir` không biết `.llmwiki/wiki` nên thoát lỗi ở dự án layout dot.

4. **Lint Task 3 miễn trừ theo cả file thì giấu nợ.** Bản đầu bỏ qua mọi file có import resolver. Sau Task 2, `okf-scan.py` import `overstack_paths` nhưng hằng `MEMORY = "harness/metrics/memory.jsonl"` vẫn trần, và lint sẽ không bao giờ thấy nó. Sửa: bỏ miễn trừ theo file, chỉ miễn theo dòng; baseline ratchet đếm hết. `parity()` cũng được sửa để báo lệch rõ ràng thay vì traceback khi `hooklib` chưa có hằng (đo trên HEAD: `AttributeError`).

5. **Fixture đúng rồi thì lộ thêm nợ trong chuỗi hook Stop.** Sau khi fixture cài engine từ working tree, test ra 2 PASS · 3 FAIL: Stop đẻ `harness/metrics/{.stop-debounce.json, memory.jsonl, provenance-log.jsonl, scratch-log.jsonl}` trần trong khi `.harness/metrics` trống, và wiki-graph không vẽ vì `_scope_config` mặc định `llmwiki/wiki` còn `build-wiki-graph.py` mặc định output `llmwiki/html`. PLAN ban đầu không thấy vì khi đó fixture chạy code remote. Thêm Task 2b: dời nơi ghi và mọi nơi đọc (9 file).

Ngoài ra: test Task 1 có 5 assertion chứ không phải 4 (hai nhánh (c)); đo trên HEAD là 0 PASS · 5 FAIL.

## Định nghĩa hoàn thành

- `dot-layout-runtime-test.sh` có trong `harness.yml`, ĐỎ trên commit trước T2 (ghi số trong commit) và XANH sau T4.
- `bare_path_lint.py --check` xanh với baseline; negative control đã thử (thêm 1 dòng → exit 2).
- Mở repo framework thấy khối `[downstream-map]`; mở dự án downstream KHÔNG thấy khối đó.
- `/fdk` và `/fdk-uat` (canonical + mirror) không còn tiêu chí bằng đường trần.
- `/fdk-uat` canary PASS với tiêu chí đường dot; không có `llmwiki/`/`harness/` trần trong dự án UAT.
- Issue ratchet nợ tồn được mở, baseline commit.

## Ngoài phạm vi (cố ý, có lý do)

- **Không** đưa `fresh-install-smoke.sh` vào GitHub CI: nhánh parity hứa↔giao cần `~/.claude/skills` (npx, mạng) — trên runner sạch sẽ đỏ giả. `dot-layout-runtime-test.sh` phủ phần layout trong CI; smoke vẫn là cổng `medic` local + `/fdk-uat`.
- **Không** sửa 50 file nợ tồn trong PLAN này: ratchet bắt mỗi lần chạm file thì trả nợ; danh sách top-5 trong Origin để ưu tiên.
- **Không** migrate repo framework sang dot: đổi cấu trúc repo dev là quyết định kiến trúc riêng (cần ADR), và làm mất "một repo, hai layout" là chính thứ lint/test này bảo vệ.
- **Không** sửa `test-broad.sh` (76 lần nhắc `llmwiki/`): nó tự dựng fixture riêng bên trong nên không phải bare-path lúc chạy ở dự án; lint miễn qua `# bare-path: ok` một dòng đầu file kèm lý do.

## Rủi ro

- `hooklib.harness_dir()` mặc định `.harness` khi chưa có thư mục nào: dự án cũ chưa migrate nhưng cũng chưa có `harness/` sẽ được tạo `.harness/metrics` — đúng chuẩn mới, installer lần sau không phải dọn. Chấp nhận.
- Regex bare-path có thể bắt nhầm chuỗi trong thông điệp log (vd `"chạy tay: harness/scripts/x.py"`): đánh dấu `# bare-path: ok thông điệp hướng dẫn` — ngoại lệ hiện, grep được, không nới regex.
- `session_start` in thêm 7 dòng ở repo framework: chỉ ở repo framework, không ảnh hưởng dự án khách; nếu user thấy ồn thì rút còn 3 dòng (bản đồ + luật + lệnh test) — quyết ở review.
