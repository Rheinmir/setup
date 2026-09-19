---
type: draft
title: "PLAN — chuẩn hoá 80 skill native theo SWH (solid-what-how/1), tách 23 skill ngoài vào skills/external/, hook từ khoá goal → orca-graph"
status: proposed
tags: [plan, orca-graph, swh, skills, fdk, external-skills, hook]
timestamp: 2026-09-19
---

# PLAN 190926 — SWH cho skill native + category skill ngoài + hook goal

Bối cảnh: PRD `raw/prd/Skill-Design-Standard-SOLID-WHAT-HOW-PRD.md` đã ingest thành concept [[solid-what-how]]. Repo có 103 skill trong `skills/`. Đối chiếu upstream thật (gh api, 19/09): **23 skill là bản kéo từ repo ngoài** và sẽ bị đè khi cập nhật upstream, nên KHÔNG viết lại theo SWH mà chuyển vào category `skills/external/`. **80 skill còn lại là native** (user chốt 19/09: hallmark, fable5, i-have-adhd tuy có nguồn upstream nhưng đã sửa nhiều ở local nên tính là native), phải migrate sang profile compact của SWH. Đã xác minh trong mã nguồn `skills` CLI (`dist/cli.mjs` dòng 873–910): `npx skills add` quét sâu một cấp dưới `skills/`, nên `skills/external/<tên>/SKILL.md` vẫn được cài xuống downstream.

Skill ngoài (23):
- `Leonxlnx/taste-skill` (13): brandkit, industrial-brutalist-ui, gpt-taste, image-to-code, imagegen-frontend-mobile, imagegen-frontend-web, minimalist-ui, full-output-enforcement, redesign-existing-projects, high-end-visual-design, stitch-design-taste, design-taste-frontend, design-taste-frontend-v1
- `JuliusBrussee/caveman` (7): caveman, caveman-commit, caveman-compress, caveman-help, caveman-review, caveman-stats, cavecrew
- còn lại (3): find-skills (vercel-labs/skills), last30days, agent-reach

## Global constraints
- Migrate **giữ nguyên hành vi** (PRD §15.2): chỉ sắp lại nội dung đã có vào `## WHAT` / `## HOW`, bổ sung contract/ví dụ còn thiếu; không đổi scope, không xoá lệnh, path hay luật đang có. Mọi khối code và mọi path/lệnh trong backtick của bản cũ phải còn trong bản mới (swh-lint `--preserve HEAD` kiểm).
- Frontmatter giữ `name`, `description`, `disable-model-invocation` như cũ; thêm `metadata.design-standard: "solid-what-how/1"` và `metadata.contract-version: "1.0.0"`.
- Profile claim là **documented**, không claim enforced (host chỉ đọc Markdown, PRD §14).
- Sửa SKILL.md xong: `bash fdk/tools/sync-skill.sh <tên>` (mirror + bản cài) và `python3 fdk/tools/skill-provenance.py record <tên> --source local-authored`.
- Không sửa nội dung skill ngoài; chỉ di chuyển + ghi đúng provenance (`adapt_mode: external-pull`, source thật).
- Không commit `llmwiki/raw/`, `prompt-as-site/`, scratchpad; không AI-attribution trong commit (R15). Không push trước T17.

### Task 1: ingest PRD SWH vào wiki
**Thoả:** — (PLAN vận hành; nguồn ở ## Origin)
**Kind:** wiki
**Depends:** —
**Files:**
- Tạo: `llmwiki/wiki/concepts/solid-what-how.md`
- Tạo: `llmwiki/wiki/sources/190926-skill-design-standard-swh-prd.md`
- Sửa: `llmwiki/wiki/concepts/skill-craft.md`
**Interfaces:**
- Consumes: —
- Produces: concept `solid-what-how` (chuẩn chính chủ các task sau trỏ tới)
```bash
ls llmwiki/wiki/concepts/solid-what-how.md llmwiki/wiki/sources/190926-skill-design-standard-swh-prd.md
grep -n "solid-what-how" llmwiki/wiki/index.md llmwiki/wiki/concepts/skill-craft.md
```
**Verify:** `test -f llmwiki/wiki/concepts/solid-what-how.md && test -f llmwiki/wiki/sources/190926-skill-design-standard-swh-prd.md`

### Task 2: swh-lint — lint cấu trúc SWH (profile documented) + test
**Thoả:** — (PRD §13 SWH-001/002/003/004/011 + preserve)
**Kind:** build
**Depends:** Task 1
**Files:**
- Tạo: `fdk/tools/swh-lint.py`
- Test: `harness/tests/test_swh_lint.py`
**Interfaces:**
- Consumes: `skills/<tên>/SKILL.md`
- Produces: `swh-lint.py [--skills a,b] [--ci] [--json] [--preserve REV]` → report `swh.report/1` mỗi skill (package_hash sha256 của thư mục skill, structural pass|fail, behavioral `review_required`, runtime `not_claimed`); bỏ qua `skills/external/`; rc 1 khi `--ci` và có blocking finding
Checks: SWH-001 có `## WHAT` và `## HOW` · SWH-002 WHAT có purpose/trigger + input/output contract + failure boundaries · SWH-003 HOW có bảng main workflow (step ID, cột exit/next) · SWH-004 có mục Branches (bảng có guard/rejoin hoặc câu "không có nhánh phụ") · SWH-011 có ví dụ positive + boundary/failure · SWH-META `metadata.design-standard` · `--preserve REV`: mọi khối code + path/lệnh backtick ở bản REV còn trong bản mới.
```python
BLOCKING = {
  "SWH-001": lambda b: "## WHAT" in b and "## HOW" in b,
  "SWH-002": lambda b: all(k in what(b).lower() for k in ("purpose", "contract", "failure")),
  "SWH-003": lambda b: re.search(r"^\|\s*W0?1\b", how(b), re.M) is not None,
  "SWH-004": lambda b: re.search(r"(?i)branch|nhánh", how(b)) is not None,
  "SWH-011": lambda b: re.search(r"(?i)positive|đúng", how(b)) and re.search(r"(?i)boundary|failure|biên|lỗi", how(b)),
}
def preserved(old, new):  # mọi khối code + `path/lệnh` của bản cũ phải còn
    return [t for t in fences(old) + ticks(old) if t not in new]
```
**Verify:** `python3 -m pytest -q harness/tests/test_swh_lint.py`

### Task 3: template compact SWH cho skill mới
**Thoả:** — (PRD §10.1, SS-03)
**Kind:** build
**Depends:** Task 2
**Files:**
- Sửa: `fdk/tools/new-skill.py`
- Sửa: `skills/new-skill/SKILL.md`
- Sửa: `skills/fdk/SKILL.md` (mục "Distill / author một skill" → khung WHAT/HOW, pointer tới concept)
**Interfaces:**
- Consumes: swh-lint (Task 2)
- Produces: `new-skill.py <tên>` sinh SKILL.md qua được swh-lint cấu trúc sau khi điền placeholder
```python
TEMPLATE = '''---
name: {name}
description: <Làm việc gì và khi nào áp dụng; boundary.>
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---
# {name}
## WHAT
### Purpose và context
### Mental model
### Input và output contract
### Rules và capabilities
### Failure boundaries
## HOW
### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
### Branches
### Validation và stopping
### Examples
'''
```
**Verify:** `python3 -m pytest -q harness/tests/test_swh_lint.py -k template`

### Task 4: category skills/external/ — resolver chung + di chuyển 23 skill ngoài + provenance đúng nguồn
**Thoả:** — (yêu cầu user 19/09: skill nhận update từ ngoài vào category riêng, vẫn cài downstream; user chốt layout thư mục 19/09)
**Kind:** migrate
**Depends:** Task 1
**Files:**
- Tạo: `harness/scripts/skill_dirs.py` (một hàm `iter_skill_dirs(root)` trả cả `skills/*/` và `skills/external/*/`)
- Sửa: ~33 tool đang glob `skills/*` (danh sách `grep -rlnE 'skills/\*|skills_dir|glob\([^)]*skills'` trong harness/, fdk/tools/, hooks, .github) → gọi qua resolver
- Di chuyển: 23 thư mục `skills/<tên>` → `skills/external/<tên>`
- Sửa: `fdk/skills.provenance.json` (source thật + `adapt_mode: external-pull` + `category: external`)
- Sửa: `llmwiki/wiki/concepts/adapt-modes.md` (category external ↔ KÉO NGOÀI)
**Interfaces:**
- Consumes: —
- Produces: `skill_dirs.iter_skill_dirs()`; layout `skills/external/`
Chạy `/impact-check` trên danh sách caller trước khi sửa (safe-change).
```python
# harness/scripts/skill_dirs.py
from pathlib import Path
def iter_skill_dirs(root="skills"):
    r = Path(root)
    for base in (r, r / "external"):
        for d in sorted(base.glob("*/")):
            if (d / "SKILL.md").is_file():
                yield d
```
```bash
for s in brandkit industrial-brutalist-ui gpt-taste image-to-code imagegen-frontend-mobile imagegen-frontend-web minimalist-ui full-output-enforcement redesign-existing-projects high-end-visual-design stitch-design-taste design-taste-frontend design-taste-frontend-v1 caveman caveman-commit caveman-compress caveman-help caveman-review caveman-stats cavecrew find-skills last30days agent-reach; do
  git mv skills/$s skills/external/$s
done
```
**Verify:** `python3 fdk/tools/skill-provenance.py check --ci && bash harness/tests/dot-layout-runtime-test.sh . && python3 harness/scripts/sync-skills.py --check`

### Task 5: pilot migrate 3 skill (ingest, medic, ship) — chốt văn phong trước khi fan-out
**Thoả:** — (PRD §15.2 migrate từng cohort nhỏ)
**Kind:** migrate
**Depends:** Task 2, Task 3
**Files:**
- Sửa: `skills/ingest/SKILL.md`, `skills/medic/SKILL.md`, `skills/ship/SKILL.md`
**Interfaces:**
- Consumes: swh-lint, template
- Produces: 3 skill mẫu đã duyệt — brief của Task 6–13 trỏ tới làm chuẩn
User duyệt 3 bản pilot (HITL) trước khi mở Task 6–13.
```bash
for s in ingest medic ship; do
  git show HEAD:skills/$s/SKILL.md > scratchpad/swh-baseline-$s.md   # baseline hành vi (PRD §15.2)
  # viết lại skills/$s/SKILL.md: WHAT (purpose/trigger, mental model, I/O contract, RULE-xx, failure) + HOW (bảng W01.., branches, validation, ví dụ positive + boundary)
  python3 fdk/tools/swh-lint.py --skills $s --ci --preserve HEAD
  bash fdk/tools/sync-skill.sh $s && python3 fdk/tools/skill-provenance.py record $s --source local-authored
done
```
**Verify:** `python3 fdk/tools/swh-lint.py --skills ingest,medic,ship --ci --preserve HEAD`

### Task 6: migrate lô 1 — docs-site-macos, hallmark (expanded profile: tách references/)
**Kind:** migrate
**Depends:** Task 5
**Files:**
- Sửa: `skills/docs-site-macos/SKILL.md`, `skills/hallmark/SKILL.md` (+ `references/*.md` nếu tách)
**Interfaces:**
- Consumes: `fdk/tools/swh-lint.py` (Task 2), template (Task 3), 3 bản pilot (Task 5) làm mẫu văn phong
- Produces: SKILL.md compact SWH (`## WHAT` / `## HOW`), không đổi `name`/`description`
```bash
for s in docs-site-macos hallmark; do
  git show HEAD:skills/$s/SKILL.md > scratchpad/swh-baseline-$s.md   # baseline hành vi (PRD §15.2)
  # viết lại skills/$s/SKILL.md: WHAT (purpose/trigger, mental model, I/O contract, RULE-xx, failure) + HOW (bảng W01.., branches, validation, ví dụ positive + boundary)
  python3 fdk/tools/swh-lint.py --skills $s --ci --preserve HEAD
  bash fdk/tools/sync-skill.sh $s && python3 fdk/tools/skill-provenance.py record $s --source local-authored
done
```
**Verify:** `python3 fdk/tools/swh-lint.py --skills docs-site-macos,hallmark --ci --preserve HEAD`

### Task 7: migrate lô 2 — fable5, md-to-html, orca-issue, orca-onboard, qc-uiux, threejs-particle-morph, wiki-room, wikieval
**Kind:** migrate
**Depends:** Task 5
**Files:**
- Sửa: `skills/{fable5,md-to-html,orca-issue,orca-onboard,qc-uiux,threejs-particle-morph,wiki-room,wikieval}/SKILL.md`
**Interfaces:**
- Consumes: `fdk/tools/swh-lint.py` (Task 2), template (Task 3), 3 bản pilot (Task 5) làm mẫu văn phong
- Produces: SKILL.md compact SWH (`## WHAT` / `## HOW`), không đổi `name`/`description`
```bash
for s in fable5 md-to-html orca-issue orca-onboard qc-uiux threejs-particle-morph wiki-room wikieval; do
  git show HEAD:skills/$s/SKILL.md > scratchpad/swh-baseline-$s.md   # baseline hành vi (PRD §15.2)
  # viết lại skills/$s/SKILL.md: WHAT (purpose/trigger, mental model, I/O contract, RULE-xx, failure) + HOW (bảng W01.., branches, validation, ví dụ positive + boundary)
  python3 fdk/tools/swh-lint.py --skills $s --ci --preserve HEAD
  bash fdk/tools/sync-skill.sh $s && python3 fdk/tools/skill-provenance.py record $s --source local-authored
done
```
**Verify:** `python3 fdk/tools/swh-lint.py --skills fable5,md-to-html,orca-issue,orca-onboard,qc-uiux,threejs-particle-morph,wiki-room,wikieval --ci --preserve HEAD`

### Task 8: migrate lô 3 — blur, check-approve, css-scroll-driven-native, extract-site, graph-mode, jenkins-agent-l3-deploy, orca-eval, qc-code, query, skill-provenance, tour-guide-supademo
**Kind:** migrate
**Depends:** Task 5
**Files:**
- Sửa: `skills/{blur,check-approve,css-scroll-driven-native,extract-site,graph-mode,jenkins-agent-l3-deploy,orca-eval,qc-code,query,skill-provenance,tour-guide-supademo}/SKILL.md`
**Interfaces:**
- Consumes: `fdk/tools/swh-lint.py` (Task 2), template (Task 3), 3 bản pilot (Task 5) làm mẫu văn phong
- Produces: SKILL.md compact SWH (`## WHAT` / `## HOW`), không đổi `name`/`description`
```bash
for s in blur check-approve css-scroll-driven-native extract-site graph-mode jenkins-agent-l3-deploy orca-eval qc-code query skill-provenance tour-guide-supademo; do
  git show HEAD:skills/$s/SKILL.md > scratchpad/swh-baseline-$s.md   # baseline hành vi (PRD §15.2)
  # viết lại skills/$s/SKILL.md: WHAT (purpose/trigger, mental model, I/O contract, RULE-xx, failure) + HOW (bảng W01.., branches, validation, ví dụ positive + boundary)
  python3 fdk/tools/swh-lint.py --skills $s --ci --preserve HEAD
  bash fdk/tools/sync-skill.sh $s && python3 fdk/tools/skill-provenance.py record $s --source local-authored
done
```
**Verify:** `python3 fdk/tools/swh-lint.py --skills blur,check-approve,css-scroll-driven-native,extract-site,graph-mode,jenkins-agent-l3-deploy,orca-eval,qc-code,query,skill-provenance,tour-guide-supademo --ci --preserve HEAD`

### Task 9: migrate lô 4 — i-have-adhd, failure-flywheel, fdk-uat, harness-tour, join-project, lenis-smooth-scroll, orca-workflow, playwright-verify, record-episode
**Kind:** migrate
**Depends:** Task 5
**Files:**
- Sửa: `skills/{i-have-adhd,failure-flywheel,fdk-uat,harness-tour,join-project,lenis-smooth-scroll,orca-workflow,playwright-verify,record-episode}/SKILL.md`
**Interfaces:**
- Consumes: `fdk/tools/swh-lint.py` (Task 2), template (Task 3), 3 bản pilot (Task 5) làm mẫu văn phong
- Produces: SKILL.md compact SWH (`## WHAT` / `## HOW`), không đổi `name`/`description`
```bash
for s in i-have-adhd failure-flywheel fdk-uat harness-tour join-project lenis-smooth-scroll orca-workflow playwright-verify record-episode; do
  git show HEAD:skills/$s/SKILL.md > scratchpad/swh-baseline-$s.md   # baseline hành vi (PRD §15.2)
  # viết lại skills/$s/SKILL.md: WHAT (purpose/trigger, mental model, I/O contract, RULE-xx, failure) + HOW (bảng W01.., branches, validation, ví dụ positive + boundary)
  python3 fdk/tools/swh-lint.py --skills $s --ci --preserve HEAD
  bash fdk/tools/sync-skill.sh $s && python3 fdk/tools/skill-provenance.py record $s --source local-authored
done
```
**Verify:** `python3 fdk/tools/swh-lint.py --skills i-have-adhd,failure-flywheel,fdk-uat,harness-tour,join-project,lenis-smooth-scroll,orca-workflow,playwright-verify,record-episode --ci --preserve HEAD`

### Task 10: migrate lô 5 — dark-mode-maker, doyourmagic, health-check, infinite-webgl-grid, orca-handover, ovs-notes, prd-grade-fe, propose, safe-change, tour-guide, wayfinder
**Kind:** migrate
**Depends:** Task 5
**Files:**
- Sửa: `skills/{dark-mode-maker,doyourmagic,health-check,infinite-webgl-grid,orca-handover,ovs-notes,prd-grade-fe,propose,safe-change,tour-guide,wayfinder}/SKILL.md`
**Interfaces:**
- Consumes: `fdk/tools/swh-lint.py` (Task 2), template (Task 3), 3 bản pilot (Task 5) làm mẫu văn phong
- Produces: SKILL.md compact SWH (`## WHAT` / `## HOW`), không đổi `name`/`description`
```bash
for s in dark-mode-maker doyourmagic health-check infinite-webgl-grid orca-handover ovs-notes prd-grade-fe propose safe-change tour-guide wayfinder; do
  git show HEAD:skills/$s/SKILL.md > scratchpad/swh-baseline-$s.md   # baseline hành vi (PRD §15.2)
  # viết lại skills/$s/SKILL.md: WHAT (purpose/trigger, mental model, I/O contract, RULE-xx, failure) + HOW (bảng W01.., branches, validation, ví dụ positive + boundary)
  python3 fdk/tools/swh-lint.py --skills $s --ci --preserve HEAD
  bash fdk/tools/sync-skill.sh $s && python3 fdk/tools/skill-provenance.py record $s --source local-authored
done
```
**Verify:** `python3 fdk/tools/swh-lint.py --skills dark-mode-maker,doyourmagic,health-check,infinite-webgl-grid,orca-handover,ovs-notes,prd-grade-fe,propose,safe-change,tour-guide,wayfinder --ci --preserve HEAD`

### Task 11: migrate lô 6 — diagram, impact-check, loop-runner, new-project-setup, orca-graph, orca-sec-scans, scroll-effects, sync-template, timeline, uat-nonit-testcase, web-crawl
**Kind:** migrate
**Depends:** Task 5
**Files:**
- Sửa: `skills/{diagram,impact-check,loop-runner,new-project-setup,orca-graph,orca-sec-scans,scroll-effects,sync-template,timeline,uat-nonit-testcase,web-crawl}/SKILL.md`
**Interfaces:**
- Consumes: `fdk/tools/swh-lint.py` (Task 2), template (Task 3), 3 bản pilot (Task 5) làm mẫu văn phong
- Produces: SKILL.md compact SWH (`## WHAT` / `## HOW`), không đổi `name`/`description`
```bash
for s in diagram impact-check loop-runner new-project-setup orca-graph orca-sec-scans scroll-effects sync-template timeline uat-nonit-testcase web-crawl; do
  git show HEAD:skills/$s/SKILL.md > scratchpad/swh-baseline-$s.md   # baseline hành vi (PRD §15.2)
  # viết lại skills/$s/SKILL.md: WHAT (purpose/trigger, mental model, I/O contract, RULE-xx, failure) + HOW (bảng W01.., branches, validation, ví dụ positive + boundary)
  python3 fdk/tools/swh-lint.py --skills $s --ci --preserve HEAD
  bash fdk/tools/sync-skill.sh $s && python3 fdk/tools/skill-provenance.py record $s --source local-authored
done
```
**Verify:** `python3 fdk/tools/swh-lint.py --skills diagram,impact-check,loop-runner,new-project-setup,orca-graph,orca-sec-scans,scroll-effects,sync-template,timeline,uat-nonit-testcase,web-crawl --ci --preserve HEAD`

### Task 12: migrate lô 7 — cursor-animated-sites, design-prim, fdk, frontier-scan, gsap-scrolltrigger-pin, harness-update, lint, orca-dispatch-reference, raise-issue, svg-stroke-reveal, teach-me, visual-qa
**Kind:** migrate
**Depends:** Task 5, Task 3
**Files:**
- Sửa: `skills/{cursor-animated-sites,design-prim,fdk,frontier-scan,gsap-scrolltrigger-pin,harness-update,lint,orca-dispatch-reference,raise-issue,svg-stroke-reveal,teach-me,visual-qa}/SKILL.md`
**Interfaces:**
- Consumes: `fdk/tools/swh-lint.py` (Task 2), template (Task 3), 3 bản pilot (Task 5) làm mẫu văn phong
- Produces: SKILL.md compact SWH (`## WHAT` / `## HOW`), không đổi `name`/`description`
```bash
for s in cursor-animated-sites design-prim fdk frontier-scan gsap-scrolltrigger-pin harness-update lint orca-dispatch-reference raise-issue svg-stroke-reveal teach-me visual-qa; do
  git show HEAD:skills/$s/SKILL.md > scratchpad/swh-baseline-$s.md   # baseline hành vi (PRD §15.2)
  # viết lại skills/$s/SKILL.md: WHAT (purpose/trigger, mental model, I/O contract, RULE-xx, failure) + HOW (bảng W01.., branches, validation, ví dụ positive + boundary)
  python3 fdk/tools/swh-lint.py --skills $s --ci --preserve HEAD
  bash fdk/tools/sync-skill.sh $s && python3 fdk/tools/skill-provenance.py record $s --source local-authored
done
```
**Verify:** `python3 fdk/tools/swh-lint.py --skills cursor-animated-sites,design-prim,fdk,frontier-scan,gsap-scrolltrigger-pin,harness-update,lint,orca-dispatch-reference,raise-issue,svg-stroke-reveal,teach-me,visual-qa --ci --preserve HEAD`

### Task 13: migrate lô 8 — br, build-now-adapt-later, council, mask-reveal-transition, onboard-codebase, plan, snapshot-push, tc-run, tidy, trace-grader, verify-before-commit, web-clone
**Kind:** migrate
**Depends:** Task 5
**Files:**
- Sửa: `skills/{br,build-now-adapt-later,council,mask-reveal-transition,onboard-codebase,plan,snapshot-push,tc-run,tidy,trace-grader,verify-before-commit,web-clone}/SKILL.md`
**Interfaces:**
- Consumes: `fdk/tools/swh-lint.py` (Task 2), template (Task 3), 3 bản pilot (Task 5) làm mẫu văn phong
- Produces: SKILL.md compact SWH (`## WHAT` / `## HOW`), không đổi `name`/`description`
```bash
for s in br build-now-adapt-later council mask-reveal-transition onboard-codebase plan snapshot-push tc-run tidy trace-grader verify-before-commit web-clone; do
  git show HEAD:skills/$s/SKILL.md > scratchpad/swh-baseline-$s.md   # baseline hành vi (PRD §15.2)
  # viết lại skills/$s/SKILL.md: WHAT (purpose/trigger, mental model, I/O contract, RULE-xx, failure) + HOW (bảng W01.., branches, validation, ví dụ positive + boundary)
  python3 fdk/tools/swh-lint.py --skills $s --ci --preserve HEAD
  bash fdk/tools/sync-skill.sh $s && python3 fdk/tools/skill-provenance.py record $s --source local-authored
done
```
**Verify:** `python3 fdk/tools/swh-lint.py --skills br,build-now-adapt-later,council,mask-reveal-transition,onboard-codebase,plan,snapshot-push,tc-run,tidy,trace-grader,verify-before-commit,web-clone --ci --preserve HEAD`

### Task 14: hook từ khoá "goal" → tự kèm orca-graph (visualize được, graph update bình thường)
**Thoả:** — (yêu cầu user 19/09, giữa phiên)
**Kind:** build
**Depends:** —
**Files:**
- Sửa: `llmwiki/.claude/hooks/user_prompt_submit.py`
- Test: `harness/tests/test_goal_hook.py`
**Interfaces:**
- Consumes: prompt user (UserPromptSubmit)
- Produces: khi prompt chứa từ khoá `goal` (nguyên từ, không phân biệt hoa thường, bỏ qua trong khối code) → hook inject chỉ thị: dựng/cập nhật graph cho goal qua `/orca-graph` (`build` lần đầu, `build` lại = `plan_version+1` khi goal đổi) rồi `graph-viz.py` → HTML; nếu đã có graph của goal thì in đường dẫn HTML hiện có. Hook chỉ inject, không tự chạy tác vụ nặng; tắt được bằng `OVERSTACK_GOAL_HOOK=0`.
```python
GOAL_RE = re.compile(r"(?<![\w-])goal(?![\w-])", re.I)
def goal_directive(prompt: str) -> str | None:
    if os.environ.get("OVERSTACK_GOAL_HOOK") == "0":
        return None
    text = re.sub(r"```.*?```", "", prompt, flags=re.S)   # bỏ khối code
    if not GOAL_RE.search(text):
        return None
    return ("[goal→orca-graph] Prompt có từ khoá goal: dựng/cập nhật graph qua /orca-graph "
            "(build PLAN; build lại = plan_version+1) rồi graph-viz.py → HTML cho user.")
```
**Verify:** `python3 -m pytest -q harness/tests/test_goal_hook.py`

### Task 15: cổng CI — swh-lint --ci trong harness.yml + medic
**Kind:** infra
**Depends:** Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13, Task 4
**Files:**
- Sửa: `.github/workflows/harness.yml`
- Sửa: `fdk/tools/medic.py`
**Interfaces:**
- Consumes: `swh-lint.py --ci`
- Produces: bước CI mới trong harness.yml; medic in dòng SWH
```yaml
      - name: swh-lint (skill native theo solid-what-how/1)
        run: python3 fdk/tools/swh-lint.py --ci
```
**Verify:** `python3 fdk/tools/swh-lint.py --ci`

### Task 16: đồng bộ mirror, CAPABILITIES, search index, provenance
**Kind:** cleanup
**Depends:** Task 15, Task 14
**Files:**
- Sửa: `llmwiki/skills/**` (mirror), `fdk/CAPABILITIES.md`, `fdk/skills.search.json`, `fdk/skills.provenance.json`
**Interfaces:**
- Consumes: skill đã migrate + layout `skills/external/`
- Produces: mirror/CAPABILITIES/search/provenance khớp
```bash
python3 harness/scripts/sync-skills.py
python3 fdk/tools/build-capabilities.py && python3 fdk/tools/build-skill-search.py
python3 fdk/tools/skill-provenance.py check --ci
```
**Verify:** `python3 fdk/tools/skill-provenance.py check --ci && python3 harness/scripts/sync-skills.py --check`

### Task 17: kiểm trước /ship — ci-local toàn bộ + /fdk-uat canary (HITL, user duyệt push)
**Kind:** release
**Depends:** Task 16
**Files:**
- Sửa: `harness/version.json`
**Interfaces:**
- Consumes: toàn bộ task trước
- Produces: biên lai ci-local + UAT canary; version bump
```bash
python3 fdk/tools/ci-local.py          # trọn mọi step CI tại local, phải xanh hết
python3 fdk/tools/medic.py --ci
# rồi /fdk-uat canary (nhánh uat/<ts>) — user duyệt trước khi /ship push
```
**Verify:** `python3 fdk/tools/ci-local.py`

### Task 18: R21 touched-paths — Stop hook in path file sửa/mới của phiên (trần 40 link)
**Thoả:** — (feedback user 19/09: "path đâu mà coi?", đưa vào luật framework, cap 40 link)
**Kind:** build
**Depends:** —
**Files:**
- Sửa: `llmwiki/.claude/hooks/hooklib.py`, `llmwiki/.claude/hooks/stop.py`
- Sửa: `harness/poc-vendor-neutral/policy.yaml` (R21), `harness/mechanisms.yaml`, `harness/scripts/harness-doctor.py` (build_r21)
- Test: `harness/tests/test_touched_paths.py`
**Interfaces:**
- Consumes: transcript (Write/Edit) + `git status` mtime
- Produces: `hooklib.session_touched_files(root, transcript) -> list[str]`, `hooklib.touched_message(files, cap=40) -> str`; Stop in `{"systemMessage": ...}` khi exit 0
```python
msg = touched_message(session_touched_files(project_dir(payload), payload.get("transcript_path") or ""))
if msg:
    print(json.dumps({"systemMessage": msg}, ensure_ascii=False))
```
**Verify:** `python3 -m pytest -q harness/tests/test_touched_paths.py`

## Origin
- Yêu cầu user 19/09/2026 qua `/ingest … và bắt đầu tiến hành chuẩn hóa toàn bộ skill native theo chuẩn; skill ngoài vào category riêng (vẫn cài downstream); luồng /fdk, check kỹ trước /ship; toàn bộ task bỏ vào /orca-graph`, cộng yêu cầu giữa phiên: hook từ khoá goal → orca-graph.
- Nguồn chuẩn: [[190926-skill-design-standard-swh-prd]], concept [[solid-what-how]].
