"""test_build_slop_gallery — trang nghiệm thu trước/sau: ghép đúng cặp ảnh, ĐỌC số từ bảng baseline
(không bịa), miễn artifact archify ở cột cổng tĩnh, và trang dựng ra tự qua cổng tĩnh."""
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(name, fname):
    s = importlib.util.spec_from_file_location(name, ROOT / f"fdk/tools/{fname}")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


bsg = _load("build_slop_gallery", "build-slop-gallery.py")

BASELINE = """| Trang | A | B | C | D | E | Toggle |
|---|---:|---:|---:|---:|---:|---|
| `html/overstack.html` | 33 | 19 | 0 | 2 | 0 | ok |
| `html/index.html` | 14 | 14 | 0 | 0 | 33 | MISSING |
"""


def test_before_counts_read_from_baseline_table(tmp_path):
    f = tmp_path / "baseline.md"
    f.write_text(BASELINE, encoding="utf-8")
    got = bsg.before_counts(f)
    assert got["llmwiki/html/overstack.html"] == {"total": 54, "toggle": "ok"}
    assert got["llmwiki/html/index.html"] == {"total": 61, "toggle": "MISSING"}


def test_missing_baseline_yields_no_numbers_instead_of_guesses(tmp_path):
    assert bsg.before_counts(tmp_path / "khong-co.md") == {}


def test_archify_artifact_is_detected_so_static_column_says_exempt(tmp_path):
    a = tmp_path / "a.html"
    a.write_text('<html><meta name="generator" content="archify 2.17.0"><svg></svg></html>', encoding="utf-8")
    b = tmp_path / "b.html"
    b.write_text("<html><body><p>thường</p></body></html>", encoding="utf-8")
    assert bsg.is_archify(a) and not bsg.is_archify(b)


def test_build_needs_at_least_one_image_pair(tmp_path):
    rc = bsg.build(tmp_path / "before", tmp_path / "after", tmp_path / "baseline.md", tmp_path / "out.html")
    assert rc == 1, "không có ảnh thì phải báo lỗi, không dựng trang rỗng"


def test_generated_page_passes_the_static_gate():
    out = ROOT / "llmwiki/html/200926-slop-before-after.html"
    if not out.is_file():
        return                      # chưa dựng trong checkout này — không phải lỗi của tool
    r = subprocess.run([sys.executable, str(ROOT / "fdk/tools/frontend-antipattern.py"), str(out)],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, (r.stdout + r.stderr)[-600:]
