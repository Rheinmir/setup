"""test_skill_requires — hợp đồng phụ thuộc skill (PLAN 141026-skills-split T1):
parse metadata.requires (pyyaml và parser con cho cùng kết quả) · check: floor/bin/scripts/framework_scripts đúng ngữ nghĩa ·
gen: grep tất định ra scripts/bin, ghi frontmatter idempotent, giữ nguyên khoá khác.
Chạy: python3 -m pytest -q harness/tests/test_skill_requires.py  (hoặc python3 harness/tests/test_skill_requires.py)."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("skill_requires", ROOT / "harness/scripts/skill-requires.py")
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)


def test_self_test_passes():
    assert sr.self_test() == 0


def test_mini_yaml_matches_pyyaml_on_repo_skills():
    """Parser con phải đọc đúng name/description/metadata.loop của MỌI skill trên đĩa (nếu còn skills/ trong repo)."""
    sdir = sr.skills_dir(None)
    if not sdir.is_dir():
        return
    try:
        import yaml
    except ImportError:
        yaml = None
    n = 0
    for d in sr.iter_skills(sdir):
        src = sr._split_frontmatter((d / "SKILL.md").read_text(encoding="utf-8", errors="ignore"))
        if src is None:
            continue
        mini = sr._mini_yaml(src)
        assert mini.get("name"), d
        if yaml is not None:
            full = yaml.safe_load(src)
            assert " ".join(str(mini.get("description", "")).split()) == " ".join(str(full.get("description", "")).split()), d
            if isinstance(full.get("metadata"), dict) and "loop" in full["metadata"]:
                assert mini["metadata"]["loop"] == full["metadata"]["loop"], d
        n += 1
    assert n > 0


if __name__ == "__main__":
    test_self_test_passes()
    test_mini_yaml_matches_pyyaml_on_repo_skills()
    print("test_skill_requires OK")
    sys.exit(0)
