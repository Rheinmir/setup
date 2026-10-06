"""md-render — md là nguồn duy nhất, máy dựng trang người đọc (0-token). Gác: cấu trúc, an toàn, cổng R20/R7/mermaid-audit."""
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(rel, name):
    s = importlib.util.spec_from_file_location(name, ROOT / rel); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


mr = _load("fdk/tools/md-render.py", "md_render")
r20 = _load("harness/validators/html_docs_shell.py", "html_docs_shell")

MD = """---
title: Đề xuất thử
description: Trang thử md-render
---
# Tiêu đề phụ bị front matter thắng

Mở đầu có `code`, **đậm**, *nghiêng* và [link](https://example.com). <script>alert(1)</script>

## Một

```mermaid
flowchart TD
  A["Bắt đầu"] --> B["Kết thúc"]
```
Giải thích sơ đồ một.

- mục a
  - mục con
- mục b

## Hai

```archify
p-overview.html Tổng quan
```
Giải thích sơ đồ archify.

| Cột | Giá trị |
|---|---|
| x | `y` |

## Ba

> trích dẫn

```python
print("<b>")
```

## Bốn

1. bước một
2. bước hai
"""


def render(tmp):
    d = tmp / "llmwiki" / "html"; d.mkdir(parents=True)
    src = tmp / "p.md"; src.write_text(MD, encoding="utf-8")
    out = d / "p-seq.html"
    mr.build(src, out)
    return out, out.read_text(encoding="utf-8")


def test_structure_and_markers(tmp_path):
    out, h = render(tmp_path)
    assert "<title>Đề xuất thử</title>" in h and 'name="description"' in h
    assert h.count("<section") == h.count("</section>") and '<section id="một">' in h
    assert '<div class="diagram-box" data-mermaid><pre class="mermaid-src" hidden>flowchart TD' in h
    assert '<iframe class="archify-embed" src="p-overview.html" title="Tổng quan"' in h
    assert h.count('<p class="desc">') == 2                       # đoạn ngay sau MỖI sơ đồ — R7 (e)
    assert "<ul><li>mục a<ul><li>mục con</li></ul></li><li>mục b</li></ul>" in h
    assert "<ol><li>bước một</li><li>bước hai</li></ol>" in h
    assert "<table>" in h and "<code>y</code>" in h and "<blockquote>" in h
    assert str(out.resolve()) in h                                # RULE-10: trang tự in đường dẫn của nó


def test_md_is_data_not_markup(tmp_path):
    _, h = render(tmp_path)
    assert "<script>alert(1)</script>" not in h and "&lt;script&gt;alert(1)&lt;/script&gt;" in h
    assert 'print("&lt;b&gt;")' in h


def test_page_passes_framework_gates(tmp_path):
    out, h = render(tmp_path)
    assert "815 815" in h and 'id="ovs-mast"' in h               # lớp nền: favicon chữ O + ribbon
    assert "nw-tocmap" in h                                       # ≥4 mục ## → rail mục lục
    assert r20.favicon_problem(str(out), h) is None and r20.shell_problem(str(out), h) is None
    assert r20.nav_problem(h) is None


def test_idempotent(tmp_path):
    out, h1 = render(tmp_path)
    mr.build(tmp_path / "p.md", out)
    assert out.read_text(encoding="utf-8") == h1


def test_chart_block_renders_static_svg_with_values(tmp_path):
    src = tmp_path / "c.md"
    src.write_text('## A\n\n```chart\n{"title": "Model viết bao nhiêu?", "unit": "KB", "note": "đo 06/10", '
                   '"bars": [{"label": "cũ", "value": 33, "group": "trước"}, {"label": "mới", "value": 16, "group": "sau"}]}\n```\n'
                   'Giải thích chart.\n\n```chart\n{bad json\n```\n', encoding="utf-8")
    out = tmp_path / "html" / "c.html"; mr.build(src, out); h = out.read_text(encoding="utf-8")
    assert '<figure class="chart"><figcaption>Model viết bao nhiêu?</figcaption>' in h
    assert 'role="img"' in h and "cũ: 33 KB" in h and ">33 KB<" in h and ">16 KB<" in h
    assert 'class="c-bar c-alt"' in h and '<p class="desc">Giải thích chart.</p>' in h
    assert 'class="chart-err"' in h                               # JSON hỏng → báo lỗi tại chỗ, không vỡ trang
