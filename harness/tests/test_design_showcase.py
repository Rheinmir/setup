"""test_design_showcase — trang mẫu chuẩn tự gác (PLAN 220926-design-showcase t7).

Đỏ khi: thêm luật vào cổng mà chưa có khối mẫu · khối khai luật không tồn tại · id khối trùng · trang committed trôi
khỏi bản build lại (ai đó sửa tay hoặc quên build) · trang vi phạm chính cổng tĩnh. Cổng chạy-thật (Playwright) chạy
trong harness/tests/html-visual-gate-test.sh."""
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "fdk/tools"
PAGE = ROOT / "skills/hallmark/references/design-showcase.html"


def _load(fname):
    s = importlib.util.spec_from_file_location(fname.replace("-", "_").removesuffix(".py"), TOOLS / fname)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


ds, sr, fa = _load("build-design-showcase.py"), _load("showcase_rules.py"), _load("frontend-antipattern.py")
BLOCKS = ds.all_blocks()


def test_every_rule_has_a_showcase_block():
    covered = {r for b in BLOCKS for r in b["rules"]}
    missing = sorted(set(sr.RULES) - covered)
    assert not missing, f"luật chưa có khối mẫu (thêm vào showcase_*.py): {missing}"


def test_blocks_only_cite_real_rules_and_ids_are_unique():
    unknown = sorted({(b["id"], r) for b in BLOCKS for r in b["rules"] if r not in sr.RULES})
    assert not unknown, f"khối khai luật không có trong showcase_rules: {unknown}"
    ids = [b["id"] for b in BLOCKS]
    assert len(ids) == len(set(ids))


def test_block_css_is_scoped_to_its_root_class():
    import re
    for b in BLOCKS:
        css = re.sub(r"@keyframes[^{]+\{(?:[^{}]*\{[^}]*\})*[^}]*\}", "", b.get("css", ""))
        for sel in re.findall(r"(?:^|})\s*([^@{}][^{}]*)\{", css):
            for part in sel.split(","):
                assert part.strip().startswith(f".sc-{b['id']}"), f"{b['id']}: selector lọt phạm vi: {part.strip()}"


def test_get_prints_a_pasteable_snippet_for_every_block():
    for b in BLOCKS:
        s = ds.snippet(b)
        assert f'class="sc-{b["id"]}' in s and (not b.get("css") or "<style>" in s)
    r = subprocess.run([sys.executable, str(TOOLS / "build-design-showcase.py"), "--get", "kanban"], capture_output=True, text=True)
    assert r.returncode == 0 and "sc-kanban" in r.stdout
    r = subprocess.run([sys.executable, str(TOOLS / "build-design-showcase.py"), "--get", "khong-co"], capture_output=True, text=True)
    assert r.returncode == 1


def test_committed_page_matches_a_fresh_build():
    assert PAGE.read_text(encoding="utf-8") == ds.build(), \
        "design-showcase.html trôi khỏi bản build — chạy: python3 fdk/tools/build-design-showcase.py"


def test_page_is_clean_on_the_static_gate():
    findings = fa.scan(PAGE)
    assert not findings, [f["msg"][:80] for f in findings]
