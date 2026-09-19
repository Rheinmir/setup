---
type: draft
title: "PLAN — SWH v1.1 Reuse Layer mức local MVP: catalog pattern/template, recipe pin hash, reuse_decision, lint placeholder/lock, ledger authoring"
status: proposed
tags: [plan, orca-graph, swh, reuse-layer, skills, fdk]
timestamp: 2026-09-19
---

# PLAN 190926 — SWH Reuse Layer (PRD v1.1 §22–29), lát cắt local MVP

Bối cảnh: PRD v1.1 thêm lớp tái sử dụng để skill kế tiếp kế thừa phần đã chuẩn hoá (concept [[solid-what-how]] mục Reuse Layer). Backlog đầy đủ là 12 ticket RU (25 ngày công). PLAN này chỉ làm mức **manual seed + local authoring MVP** (§29.1): chạy local, file-based, không service, không vector DB, không auto-upgrade. Tái dùng thứ đã có: `new-skill.py` (template compact + BM25 SkillResolve), `skill-provenance.py` (sha256), `swh-lint.py` (package_hash). Catalog đặt ở `fdk/skill-catalog/` (framework_only như `fdk/`, không ship xuống dự án khách). KHÔNG đụng `llmwiki/patterns/` (kho pattern vai trò dự án, luật R14).

Ngoài phạm vi (nói thẳng): promotion workflow tự động (RU-09), upgrade/quarantine propagation (RU-10), pilot đo chi phí có baseline (RU-12), P02 external-effect active. Seed chỉ mang nhãn `limited_evidence`; không tuyên bố tiết kiệm.

## Global constraints
- Mọi skill sinh từ template vẫn phải qua `swh-lint --ci` như skill viết tay; reuse không miễn cổng nào.
- `${...}` là placeholder văn bản typed, render bằng thay chuỗi có schema; KHÔNG eval, KHÔNG shell; giá trị chứa xuống dòng, `---` hoặc `${` bị từ chối.
- Recipe pin sha256 thật; thiếu hash hoặc `lock_status: unresolved` thì không release.
- Mỗi lần `new-skill.py` chạy phải ghi `reuse_decision` (reuse · compose · scratch · catalog_unavailable) + lý do; scratch là đường hợp lệ.
- Không AI-attribution trong commit (R15); không commit `llmwiki/raw/`.

### Task 1: catalog + seed pattern/template (swh.reuse/1)
**Kind:** build
**Depends:** —
**Files:**
- Tạo: `fdk/skill-catalog/catalog.json`
- Tạo: `fdk/skill-catalog/patterns/P01-evidence-to-artifact.md`, `P02-verified-external-effect.md`, `P03-pure-transform.md`
- Tạo: `fdk/skill-catalog/templates/T00-compact.md` (khung compact hiện có của new-skill.py), `T01-evidence-to-artifact.md`, `T02-pure-transform.md`
**Interfaces:**
- Consumes: —
- Produces: `catalog.json` = `{"schema_version":"swh.reuse/1","assets":[{asset_id,kind,version,status,path,effect_class,problem_tags,applicable_when,not_applicable_when,params:{name:{type,required,enum?,min?,max?}},evidence:"limited_evidence"}]}`
```json
{"asset_id": "evidence-to-artifact", "kind": "template", "version": "1.0.0", "status": "active",
 "path": "templates/T01-evidence-to-artifact.md", "effect_class": "file_only",
 "problem_tags": ["evidence", "artifact", "draft", "report"], "evidence": "limited_evidence",
 "params": {"repair_limit": {"type": "int", "required": true, "min": 0, "max": 2}}}
```
**Verify:** `python3 -c "import json;d=json.load(open('fdk/skill-catalog/catalog.json'));assert d['schema_version']=='swh.reuse/1' and len(d['assets'])>=6"`

### Task 2: skill-reuse.py — search · decide · resolve · render
**Kind:** build
**Depends:** Task 1
**Files:**
- Tạo: `fdk/tools/skill-reuse.py`
- Test: `harness/tests/test_skill_reuse.py`
**Interfaces:**
- Consumes: `fdk/skill-catalog/catalog.json`
- Produces: `search(contract) -> list[dict]` (lọc cứng status∈{active} + effect_class khớp TRƯỚC, rồi xếp hạng theo tag, tối đa 3) · `resolve(recipe) -> lock` (sha256 từng asset, cycle/độ sâu ≤ 3 → `DEPENDENCY_CYCLE`/`DEPTH_LIMIT`) · `render(template_text, params, schema) -> str` (lỗi `INVALID_PARAMETER`/`UNRESOLVED_SLOT`) · CLI `search|decide|resolve|render`
```python
def render(text, params, schema):
    for k, spec in schema.items():
        v = params.get(k)
        if v is None and spec.get("required"):
            raise ReuseError("INVALID_PARAMETER", k)
        if isinstance(v, str) and ("\n" in v or "${" in v or v.strip() == "---"):
            raise ReuseError("INVALID_PARAMETER", k)
    out = re.sub(r"\$\{(\w+)\}", lambda m: str(params[m.group(1)]) if m.group(1) in params else m.group(0), text)
    left = re.findall(r"\$\{\w+\}", out)
    if left:
        raise ReuseError("UNRESOLVED_SLOT", left)
    return out
```
**Verify:** `python3 -m pytest -q harness/tests/test_skill_reuse.py`

### Task 3: new-skill.py dùng catalog + ghi reuse_decision + recipe
**Kind:** build
**Depends:** Task 2
**Files:**
- Sửa: `fdk/tools/new-skill.py`
- Sửa: `skills/new-skill/SKILL.md`
- Tạo: `fdk/skill-catalog/recipes/.keep`
**Interfaces:**
- Consumes: `skill-reuse.search/resolve/render`
- Produces: `new-skill.py <name> --loop L --desc D [--from <asset_id> --params p.json]`; không `--from` → in top-3 gợi ý từ catalog, ghi decision `scratch` (hoặc `catalog_unavailable` nếu không đọc được catalog); `--from` → render + ghi `fdk/skill-catalog/recipes/<name>.recipe.json` (lock_status resolved, sha256 base)
```python
decision = {"schema_version": "swh.reuse/1", "skill": name, "decision": "reuse" if args.from_ else "scratch",
            "candidates": [h["asset_id"] for h in hits], "reason": args.reason or ""}
```
**Verify:** `python3 -m pytest -q harness/tests/test_skill_reuse.py -k new_skill`

### Task 4: swh-lint — SWH-PLACEHOLDER + SWH-LOCK
**Kind:** build
**Depends:** Task 2
**Files:**
- Sửa: `fdk/tools/swh-lint.py`
- Sửa: `harness/tests/test_swh_lint.py`
**Interfaces:**
- Consumes: `fdk/skill-catalog/recipes/<skill>.recipe.json` (nếu có)
- Produces: finding `SWH-PLACEHOLDER` (còn `${...}` hoặc marker việc-chưa-điền của template T00 ngoài khối code) và `SWH-LOCK` (recipe unresolved hoặc sha256 base ≠ file hiện tại — RE-04)
```python
UNFILLED = re.compile(r"\$\{\w+\}|\bTO" r"DO\b")   # marker chưa điền của T00
if UNFILLED.search(bare):
    out.append(("SWH-PLACEHOLDER", "còn placeholder chưa điền"))
```
**Verify:** `python3 -m pytest -q harness/tests/test_swh_lint.py && python3 fdk/tools/swh-lint.py --ci`

### Task 5: ledger chi phí authoring (mức manual)
**Kind:** build
**Depends:** Task 3
**Files:**
- Sửa: `fdk/tools/skill-reuse.py` (lệnh `episode start|end|report`)
- Test: `harness/tests/test_skill_reuse.py`
**Interfaces:**
- Consumes: —
- Produces: `harness/metrics/skill-authoring.jsonl` (event_id idempotent, skill, decision, minutes, outcome); `report` in median/p75/n theo decision, `benefit_unproven` khi thiếu baseline scratch cùng cohort; ví dụ hòa vốn F=12, scratch=8, reuse=3 → 3 lần (RU-08 QA)
```python
def breakeven(F, scratch, reuse, maint=0):
    return None if reuse >= scratch else math.ceil((F + maint) / (scratch - reuse))
```
**Verify:** `python3 -m pytest -q harness/tests/test_skill_reuse.py -k ledger`

### Task 6: nối cổng + tài liệu (CI, medic, concept, fdk skill)
**Kind:** infra
**Depends:** Task 4, Task 5
**Files:**
- Sửa: `.github/workflows/harness.yml`, `fdk/tools/medic.py`, `harness/mechanisms.yaml`
- Sửa: `skills/fdk/SKILL.md` (bước author: tìm mẫu trước, ghi decision)
- Sửa: `llmwiki/wiki/concepts/solid-what-how.md`
**Interfaces:**
- Consumes: Task 2–5
- Produces: CI chạy `test_skill_reuse.py`; mechanism `skill-reuse`; hướng dẫn author trỏ tới catalog
```yaml
      - name: skill-reuse — catalog/recipe/render/ledger (SWH v1.1 Reuse Layer)
        run: python3 -m pytest -q harness/tests/test_skill_reuse.py
```
**Verify:** `python3 fdk/tools/ci-local.py`

### Task 7: kiểm trước /ship — ci-local + /fdk-uat canary (HITL)
**Kind:** release
**Depends:** Task 6
**Files:**
- Sửa: `harness/version.json`
**Interfaces:**
- Consumes: toàn bộ task trước
- Produces: biên lai ci-local + UAT canary/main-URL
```bash
python3 fdk/tools/ci-local.py && python3 fdk/tools/medic.py --ci
```
**Verify:** `python3 fdk/tools/ci-local.py`

## Origin
- Yêu cầu user 19/09/2026: "đọc tiếp phần cải thiện này và đem nó vào harness" — nguồn `raw/prd/Skill-Design-Standard-SOLID-WHAT-HOW-PRD (1).md` §22–29, tóm tắt [[190926-skill-design-standard-swh-prd]].
