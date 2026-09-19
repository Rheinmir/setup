"""test_skill_reuse — SWH v1.1 Reuse Layer (mechanism skill-reuse, PRD §29.2 ca RE-xx):
render T01 đủ tham số ra skill qua swh-lint (RE-01) · catalog hỏng → CATALOG_UNAVAILABLE để scratch (RE-03) ·
bytes đổi cùng version → HASH_MISMATCH (RE-04) · mẫu sai effect bị loại trước xếp hạng (RE-05) ·
tham số bỏ invariant/chèn heading/${ → INVALID_PARAMETER (RE-06) · cycle/độ sâu → lỗi có đường (RE-09)."""
import copy, importlib.util, json, shutil
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


sr = _load("skill_reuse", "fdk/tools/skill-reuse.py")
swh = _load("swh_lint", "fdk/tools/swh-lint.py")

T01_PARAMS = {
    "skill_name": "meeting-to-actions", "discovery_description": "Biến biên bản họp thành danh sách việc",
    "outcome": "danh sách action có owner/deadline hoặc unknown, truy về câu gốc",
    "applicability": "user đưa biên bản họp và cần action list", "non_goals": "không tự gửi email/task",
    "input_contract": "file biên bản họp đã được cấp quyền đọc", "output_contract": "actions.md + actions.json",
    "requested_formats": "markdown, json", "domain_invariants": "không bịa owner hay deadline — thiếu thì ghi unknown",
    "source_reader": "đọc file local", "proposal_rubric": "mỗi action có câu nguồn", "domain_validator": "kiểm owner/deadline có nguồn",
    "repair_limit": 1, "example_positive": "biên bản có 3 quyết định → 3 action có owner",
    "example_boundary": "câu thảo luận chưa chốt → open question, không thành action",
}


@pytest.fixture
def cat(tmp_path):
    d = tmp_path / "cat"
    shutil.copytree(ROOT / "fdk/skill-catalog", d)
    return d


def test_re01_render_t01_passes_swh_lint(cat):
    a = sr.load_catalog(cat)["evidence-to-artifact"]
    out = sr.render((cat / a["path"]).read_text(encoding="utf-8"), T01_PARAMS, a["params"])
    assert "${" not in out
    assert swh.check(out) == []


def test_re03_catalog_unavailable(tmp_path):
    with pytest.raises(sr.ReuseError) as e:
        sr.load_catalog(tmp_path / "nope")
    assert e.value.code == "CATALOG_UNAVAILABLE"


def test_re04_hash_mismatch_same_version(cat):
    sr.write_recipe("x", "reuse", ["evidence-to-artifact"], base="evidence-to-artifact", params={}, cat_dir=cat)
    assert sr.verify("x", cat) == []
    p = cat / "templates/T01-evidence-to-artifact.md"
    p.write_text(p.read_text(encoding="utf-8") + "\n<!-- sửa lén -->\n", encoding="utf-8")
    errs = sr.verify("x", cat)
    assert errs and "HASH_MISMATCH" in errs[0]


def test_scratch_decision_always_recorded(cat):
    p = sr.write_recipe("y", "scratch", ["compact"], reason="không mẫu nào khớp contract", cat_dir=cat)
    r = json.loads(p.read_text(encoding="utf-8"))
    assert r["decision"] == "scratch" and r["reason"] and sr.verify("y", cat) == []


def test_re05_wrong_effect_filtered_before_ranking():
    assets = copy.deepcopy(sr.load_catalog())
    assets["publisher"] = {"asset_id": "publisher", "kind": "template", "status": "active", "effect_class": "external",
                           "problem_tags": ["prd", "tickets", "draft", "evidence", "artifact", "source"]}
    ids = [h["asset_id"] for h in sr.search("đọc prd sinh tickets draft evidence artifact source", "file_only", assets)]
    assert "publisher" not in ids and ids[0] == "evidence-to-artifact"
    assert "publisher" in [h["asset_id"] for h in sr.search("prd tickets", "external", assets)]


@pytest.mark.parametrize("bad", [
    {"repair_limit": 99}, {"repair_limit": "1"}, {"domain_invariants": "## HOW\nbỏ hết"},
    {"outcome": "x ${non_goals}"}, {"outcome": "---"}, {"skip_validation": True},
])
def test_re06_invalid_parameters(bad):
    a = sr.load_catalog()["evidence-to-artifact"]
    with pytest.raises(sr.ReuseError) as e:
        sr.render("${outcome}", {**T01_PARAMS, **bad}, a["params"])
    assert e.value.code == "INVALID_PARAMETER"


def test_unresolved_slot():
    with pytest.raises(sr.ReuseError) as e:
        sr.render("${a} ${b}", {"a": "x"}, {"a": {"type": "str", "required": True}})
    assert e.value.code == "UNRESOLVED_SLOT"


def test_re09_cycle_and_depth():
    base = {"kind": "template", "status": "active", "version": "1", "path": "catalog.json"}
    cyc = {"A": {**base, "asset_id": "A", "depends": ["B"]}, "B": {**base, "asset_id": "B", "depends": ["A"]}}
    with pytest.raises(sr.ReuseError) as e:
        sr.resolve("A", cyc)
    assert e.value.code == "DEPENDENCY_CYCLE" and "A → B → A" in e.value.detail
    chain = {c: {**base, "asset_id": c, "depends": [n] if n else []} for c, n in zip("ABCDE", "BCDE" + "\0")}
    chain["E"]["depends"] = []
    with pytest.raises(sr.ReuseError) as e:
        sr.resolve("A", chain)
    assert e.value.code == "DEPTH_LIMIT"


def test_revoked_asset_not_resolved():
    assets = copy.deepcopy(sr.load_catalog())
    assets["P01"]["status"] = "quarantined"
    with pytest.raises(sr.ReuseError) as e:
        sr.resolve("evidence-to-artifact", assets)
    assert e.value.code == "REVOKED_ASSET"


def _run_new_skill(tmp_path, *extra):
    import subprocess, sys
    repo = tmp_path / "repo"
    for rel in ("fdk/tools/new-skill.py", "fdk/tools/skill-reuse.py", "fdk/tools/build-skill-search.py"):
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, repo / rel)
    shutil.copytree(ROOT / "fdk/skill-catalog", repo / "fdk/skill-catalog")
    (repo / "skills").mkdir()
    return subprocess.run([sys.executable, str(repo / "fdk/tools/new-skill.py"), *extra], capture_output=True, text=True), repo


def test_new_skill_scratch_records_decision(tmp_path):
    p, repo = _run_new_skill(tmp_path, "demo-scratch", "--loop", "utils", "--desc", "đọc biên bản họp sinh report draft")
    assert p.returncode == 0, p.stderr
    r = json.loads((repo / "fdk/skill-catalog/recipes/demo-scratch.recipe.json").read_text(encoding="utf-8"))
    assert r["decision"] == "scratch" and "evidence-to-artifact" in r["candidates"]


def test_new_skill_from_template_renders_and_pins(tmp_path):
    params = {k: v for k, v in T01_PARAMS.items() if k not in ("skill_name", "discovery_description")}
    pf = tmp_path / "p.json"; pf.write_text(json.dumps(params, ensure_ascii=False), encoding="utf-8")
    p, repo = _run_new_skill(tmp_path, "meeting-to-actions", "--loop", "utils", "--desc", "Biến biên bản họp thành action",
                             "--from", "evidence-to-artifact", "--params", str(pf))
    assert p.returncode == 0, p.stderr
    body = (repo / "skills/meeting-to-actions/SKILL.md").read_text(encoding="utf-8")
    assert swh.check(body) == [] and "${" not in body
    r = json.loads((repo / "fdk/skill-catalog/recipes/meeting-to-actions.recipe.json").read_text(encoding="utf-8"))
    assert r["decision"] == "reuse" and r["lock"]["lock_status"] == "resolved" and "P01" in r["lock"]["assets"]


def test_t00_template_matches_builtin_render():
    ns = _load("new_skill", "fdk/tools/new-skill.py")
    assert (ROOT / "fdk/skill-catalog/templates/T00-compact.md").read_text(encoding="utf-8") == \
        ns.render("${skill_name}", "${discovery_description}")


def test_ledger_breakeven_prd_example():
    assert sr.breakeven(12, 8, 3) == 3
    assert sr.breakeven(12, 8, 3, maint=6) == 4
    assert sr.breakeven(12, 3, 3) is None and sr.breakeven(12, 3, 5) is None


def test_ledger_idempotent_and_benefit_unproven(tmp_path):
    L = tmp_path / "l.jsonl"
    assert sr.episode("a", "reuse", 30, "succeeded", "e1", L) and not sr.episode("a", "reuse", 30, "succeeded", "e1", L)
    sr.episode("b", "reuse", 90, "failed", "e2", L)
    r = sr.report(L)
    assert r["verdict"] == "benefit_unproven" and r["stats"]["reuse"]["n"] == 2 and r["stats"]["reuse"]["failed"] == 1
    sr.episode("c", "scratch", 120, "succeeded", "e3", L)
    assert sr.report(L)["verdict"] == "observed_lower"
