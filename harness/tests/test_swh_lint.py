"""test_swh_lint — lint cấu trúc SWH: skill đủ WHAT/HOW pass; thiếu HOW/ví dụ/metadata fail đúng rule;
--preserve bắt lệnh bị mất khi migrate; skills/external/ không bị lint; --ci ra rc 1."""
import importlib.util, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("swh", ROOT / "fdk/tools/swh-lint.py")
swh = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(swh)

GOOD = """---
name: demo
description: Demo skill.
metadata:
  design-standard: "solid-what-how/1"
---
# demo
## WHAT
### Purpose và context
Làm X khi Y.
### Input và output contract
In: a. Out: b.
### Failure boundaries
Thiếu a → blocked.
## HOW
### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | a | chạy `python3 tools/x.py` | b | lỗi → blocked |
### Branches
Không có nhánh phụ trong version này.
### Examples
- Positive: a hợp lệ → b.
- Boundary: thiếu a → blocked.
"""


def rules(text):
    return {r for r, _ in swh.check(text)}


def test_good_skill_passes():
    assert rules(GOOD) == set()


def test_missing_how_is_swh001():
    assert "SWH-001" in rules(GOOD.split("## HOW")[0])


def test_missing_examples_and_branches():
    t = GOOD.replace("### Branches\nKhông có nhánh phụ trong version này.\n", "")
    t = t.split("### Examples")[0]
    assert {"SWH-004", "SWH-011"} <= rules(t)


def test_missing_metadata():
    assert "SWH-META" in rules(GOOD.replace('  design-standard: "solid-what-how/1"\n', ""))


def test_legacy_skill_fails_structure():
    legacy = "---\nname: x\ndescription: y\n---\n# x\n## When to use\n- a\n## Steps\n1. b\n## Rules\n- c\n"
    assert "SWH-001" in rules(legacy)


def test_preserve_detects_lost_command():
    old = "## Steps\n```bash\npython3 fdk/tools/foo.py --all\n```\nxem `harness/x.yaml`\n"
    assert swh.lost_tokens(old, GOOD) == ["harness/x.yaml", "python3 fdk/tools/foo.py --all"]
    assert swh.lost_tokens(old, GOOD + old) == []


def _mk(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_external_skipped_and_ci_rc(tmp_path):
    _mk(tmp_path, "skills/good/SKILL.md", GOOD)
    _mk(tmp_path, "skills/external/upstream/SKILL.md", "---\nname: u\n---\nlegacy\n")
    assert [d.name for d in swh.skill_dirs(tmp_path)] == ["good"]
    assert swh.main(["--root", str(tmp_path), "--ci"]) == 0
    _mk(tmp_path, "skills/bad/SKILL.md", "---\nname: bad\n---\n# bad\n")
    assert swh.main(["--root", str(tmp_path), "--ci"]) == 1
    assert swh.main(["--root", str(tmp_path)]) == 0          # không --ci thì chỉ báo


def test_report_contract(tmp_path):
    _mk(tmp_path, "skills/good/SKILL.md", GOOD)
    r = swh.report(tmp_path / "skills/good")
    assert r["schema_version"] == "swh.report/1" and r["structural"] == "pass"
    assert r["behavioral"] == "review_required" and r["release_eligible"] is False
    assert len(r["package_hash"]) == 64


def test_template_new_skill_passes_structure():
    spec = importlib.util.spec_from_file_location("newskill", ROOT / "fdk/tools/new-skill.py")
    ns = importlib.util.module_from_spec(spec); spec.loader.exec_module(ns)
    body = ns.render("demo-x", "Demo: làm X khi Y")
    assert rules(body) == {"SWH-PLACEHOLDER"}, rules(body)            # khung đúng hình, chỉ còn chờ điền
    assert rules(body.replace("⟨TODO⟩", "x")) == set()


def test_placeholder_slot_and_inline_code_exempt():
    assert "SWH-PLACEHOLDER" in rules(GOOD.replace("Làm X khi Y.", "Làm ${outcome}."))
    assert rules(GOOD.replace("Làm X khi Y.", "Làm X khi `${VAR}` có.")) == set()


def test_heading_inside_code_fence_does_not_cut_section():
    t = GOOD.replace("### Examples", "### Output report\n````\n## What\n## Output\n````\n### Examples")
    assert rules(t) == set(), rules(t)


def test_inline_triple_backtick_is_not_a_fence():
    old = "| a | ```css :root{}``` |\n## Steps\n1. chạy `fdk/tools/x.py`\n"
    assert swh.preserve_tokens(old) == {"fdk/tools/x.py"}
