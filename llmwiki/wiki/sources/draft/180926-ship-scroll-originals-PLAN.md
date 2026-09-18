---
type: draft
title: "PLAN — ship scroll-effects bản gốc (uiux-asset) + dọn CI đỏ + issue orca-graph còn mở"
status: in-progress
tags: [plan, orca-graph, ship, scroll-effects]
timestamp: 2026-09-18
---

# PLAN 180926 — ship scroll-originals + issue mở

Bối cảnh: 8 skill scroll-effects đã trỏ về code gốc nguyên văn ở repo ngoài `Rheinmir/uiux-asset` (Pages live, 61/64 pen sạch). Framework chưa commit: `ci-local` 65/67 — 2 đỏ do việc dọn draft dở của phiên khác (PLAN graph-engineering bị dời vào `archive/proposals/`, `skills/tidy/SKILL.md` sửa 1 dòng). Kéo thêm issue GitHub đang mở làm được ngay; epic frontier (#7–#15, #71–#102) ngoài phạm vi graph này (≤ 20 node).

## Global constraints
- Không commit `llmwiki/raw/`, `prompt-as-site/`, file nháp scratchpad; không AI-attribution trong commit (R15).
- Mọi push chỉ sau khi `ci-local` 67/67 xanh; đóng issue GitHub chỉ khi có bằng chứng (test/CI xanh).
- Việc dở của phiên khác: tách commit riêng, không trộn vào commit tính năng.

### Task 1: ge-acceptance trỏ đúng đường dẫn PLAN đã archive
**Thoả:** — (PLAN vận hành, không có SPEC FR-xxx; nguồn yêu cầu ở ## Origin)
**Kind:** fix
**Depends:** —
**Files:**
- Sửa: `harness/tests/ge-acceptance-test.sh`
**Interfaces:**
- Consumes: —
- Produces: —
```bash
SPEC="$(find llmwiki/wiki/sources/draft -name 290726-graph-engineering-PLAN.md 2>/dev/null | head -1)"
```
**Verify:** `bash harness/tests/ge-acceptance-test.sh .`

### Task 2: ghi lại provenance cho skill tidy (thay đổi 1 dòng doc của phiên dọn draft)
**Thoả:** — (PLAN vận hành, không có SPEC FR-xxx; nguồn yêu cầu ở ## Origin)
**Kind:** fix
**Depends:** —
**Files:**
- Sửa: `fdk/skills.provenance.json`
**Interfaces:**
- Consumes: —
- Produces: —
```bash
python3 fdk/tools/skill-provenance.py record tidy --source local-authored
```
**Verify:** `python3 fdk/tools/skill-provenance.py check --ci`

### Task 3: GH#166 — verify/QC của orca-graph chạy dưới bash, không phải sh
**Thoả:** — (PLAN vận hành, không có SPEC FR-xxx; nguồn yêu cầu ở ## Origin)
**Kind:** fix
**Depends:** —
**Files:**
- Sửa: `harness/scripts/orca-graph.py`
- Test: `harness/tests/test_orca_graph.py`
**Interfaces:**
- Consumes: —
- Produces: —
```bash
SHELL = shutil.which("bash")
rc = subprocess.call(n["verify"], shell=True, executable=SHELL)
```
**Verify:** `python3 -m pytest -q harness/tests/test_orca_graph.py`

### Task 4: GH#162 + GH#163 — xác nhận đã implement (run --strict allow-list, trường **QC:**) rồi đóng issue
**Thoả:** — (PLAN vận hành, không có SPEC FR-xxx; nguồn yêu cầu ở ## Origin)
**Kind:** review
**Depends:** —
**Files:**
- Sửa: `llmwiki/wiki/sources/draft/170926-orca-graph-no-write-sandbox.md`
**Interfaces:**
- Consumes: —
- Produces: —
```bash
python3 -m pytest -q harness/tests/test_orca_graph.py -k "qc or strict"
gh issue close 162 163 --comment "Đã implement: run --strict allow-list (GH#162), trường **QC:** (GH#163) — test_orca_graph.py xanh"
```
**Verify:** `grep -q -- '--strict' harness/scripts/orca-graph.py && grep -q '"qc"' harness/scripts/orca-graph.py`

### Task 5: ci-local xanh trọn 67/67
**Thoả:** — (PLAN vận hành, không có SPEC FR-xxx; nguồn yêu cầu ở ## Origin)
**Kind:** test
**Depends:** Task 1, Task 2, Task 3
**Files:**
- Test: `fdk/tools/ci-local.py`
**Interfaces:**
- Consumes: —
- Produces: —
```bash
python3 fdk/tools/ci-local.py
```
**Verify:** `python3 fdk/tools/ci-local.py 2>&1 | tail -1 | grep -q '67/67'`

### Task 6: commit A — scroll-effects bản gốc + query-proxy + egress + GH#166 + fix CI
**Thoả:** — (PLAN vận hành, không có SPEC FR-xxx; nguồn yêu cầu ở ## Origin)
**Kind:** release
**Depends:** Task 5
**Files:**
- Sửa: `skills/scroll-effects/SKILL.md`
**Interfaces:**
- Consumes: —
- Produces: —
```bash
git commit --only -- <danh sách path scroll-effects + fix CI>
```
**Verify:** `git log -1 --format=%s | grep -q scroll`

### Task 7: commit B — dọn draft sprawl của phiên tidy (archive/need-review/provenance)
**Thoả:** — (PLAN vận hành, không có SPEC FR-xxx; nguồn yêu cầu ở ## Origin)
**Kind:** cleanup
**Depends:** Task 6
**Files:**
- Sửa: `llmwiki/wiki/index.md`
**Interfaces:**
- Consumes: —
- Produces: —
```bash
git add -A llmwiki/wiki fdk/wiki harness/scripts/tidy.py harness/tests/tidy-test.sh && git commit
```
**Verify:** `test -z "$(git status --short -- llmwiki/wiki/sources/draft llmwiki/wiki/draft)"`

### Task 8: push lên origin/orca
**Thoả:** — (PLAN vận hành, không có SPEC FR-xxx; nguồn yêu cầu ở ## Origin)
**Kind:** deploy
**Mode:** hitl
**Depends:** Task 7
**Files:**
- Test: `fdk/tools/ci-local.py`
**Interfaces:**
- Consumes: —
- Produces: —
```bash
git push origin orca
```
**Verify:** `test "$(git rev-parse HEAD)" = "$(git rev-parse origin/orca)"`

### Task 9: GH#165 + GH#161 — CI remote xanh sau push thì đóng 2 issue ci-fail cũ
**Thoả:** — (PLAN vận hành, không có SPEC FR-xxx; nguồn yêu cầu ở ## Origin)
**Kind:** review
**Mode:** hitl
**Depends:** Task 8
**Files:**
- Sửa: `llmwiki/wiki/sources/ISSUES.md`
**Interfaces:**
- Consumes: —
- Produces: —
```bash
gh run list --branch orca --limit 3
gh issue close 161 165 --comment "CI xanh lại sau push"
```
**Verify:** `gh run list --branch orca --limit 3 --json conclusion --jq '.[].conclusion' | grep -qv failure`

### Task 10: GH#160 — land skill br + 12 tool về canonical (cần file từ global harness máy gốc)
**Thoả:** — (PLAN vận hành, không có SPEC FR-xxx; nguồn yêu cầu ở ## Origin)
**Kind:** migrate
**Mode:** hitl
**Depends:** —
**Files:**
- Tạo: `skills/br/SKILL.md`
- Tạo: `fdk/tools/br-run.py`
**Interfaces:**
- Consumes: —
- Produces: —
```bash
# cần máy gốc có global harness chứa skill br — copy về canonical rồi record provenance
```
**Verify:** `test -f skills/br/SKILL.md && test -f fdk/tools/br-run.py`

## Origin
- Phiên 0d1b17dc (18/09/2026) nối tiếp handover 43638fd4; user: "lưu mấy task này vào /orca-graph và kéo issue về bổ sung vào graph".
- Issue nguồn: `gh issue list --state open` (Rheinmir/setup) — #160 #161 #162 #163 #165 #166.
- Repo ngoài: https://github.com/Rheinmir/uiux-asset
