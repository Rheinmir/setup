#!/usr/bin/env python3
"""html-font-lint — GÁC luật "mọi HTML framework sinh ra dùng font mặc định của html_font.py (Be Vietnam Pro), NHÚNG" (user chốt 20/09, đổi font 21/09/2026).

    html-font-lint.py trang.html [thư-mục …]     rc 2 + tên từng trang thiếu font · thư mục = mọi *.html ngay trong đó
    html-font-lint.py --parity                    bản sao html_font ở repo engine (orca-graph) còn khớp nguồn framework không

Một trang ĐẠT khi có đủ: khối <style id="ovs-font"> (do html_font.apply chèn) · `font-family:'<FAMILY>'` · font nhúng
`data:font/woff2;base64,` · mặc định nội dung `--fw-text:<WEIGHT_TEXT>` — FAMILY/WEIGHT_TEXT đọc từ html_font.py, không ghi cứng lần nữa · và KHÔNG gọi fonts.googleapis.com (nhúng hết = 0 request ngoài).
"""
import importlib.util, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _need() -> tuple:
    hf = _load(HERE / "html_font.py")
    return ('id="ovs-font"', hf.MARK, "data:font/woff2;base64,", f"--fw-text:{hf.WEIGHT_TEXT}")


def problems(page: Path) -> list:
    h = page.read_text(encoding="utf-8", errors="ignore")
    out = [f"thiếu `{n}`" for n in _need() if n not in h]
    if "fonts.googleapis.com" in h or "fonts.gstatic.com" in h:
        out.append("gọi Google Fonts — luật là NHÚNG, 0 request ngoài")
    return out


def _load(path: Path):
    s = importlib.util.spec_from_file_location(path.stem.replace("-", "_") + "_" + str(abs(hash(str(path)))), path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def parity() -> int:
    import os
    eng = Path(os.environ.get("ORCA_GRAPH_ENGINE_DIR") or Path(os.environ.get("ORCA_GRAPH_INSTALL_DIR") or Path.home() / ".orca-graph/repo") / "engine")
    if not (eng / "html_font.py").is_file():
        print(f"SKIP parity: chưa có engine orca-graph ≥ 3.0.3 ở {eng}"); return 4      # rc RIÊNG: caller không được đếm SKIP là PASS
    mine, theirs = _load(HERE / "html_font.py"), _load(eng / "html_font.py")
    bad = [k for k in ("FONT_TEXT", "FONT_MONO", "WEIGHT_TEXT", "WEIGHT_STRONG", "WEIGHT_HEADING", "TRACK_HEADING", "STYLE_ID") if getattr(mine, k) != getattr(theirs, k, None)]
    if mine.head_css() != theirs.head_css():         # so CSS THẬT sinh ra, không chỉ hằng số (21/09/2026: đổi letter-spacing h3 lọt qua)
        bad.append("head_css()")
    if (HERE / "html_font_data.py").read_bytes() != (eng / "html_font_data.py").read_bytes():
        bad.append("html_font_data.py (file font nhúng)")
    if (eng / "html_base.py").is_file():             # engine ≥ 3.1.0 mang cả LỚP NỀN — token sáng/tối phải khớp, không thì trang graph lệch màu với phần còn lại
        mb, tb = _load(HERE / "html_base.py"), _load(eng / "html_base.py")
        bad += [f"html_base.{k}" for k in ("LIGHT", "DARK", "KEY", "STYLE_ID") if getattr(mb, k) != getattr(tb, k, None)]
        bad += [f"html_base.base_css(family_dark={fd})" for fd in (True, False)          # CSS nền THẬT, không chỉ hằng (review t9 F4)
                if mb.base_css(family_dark=fd) != getattr(tb, "base_css", lambda **k: None)(family_dark=fd)]
    else:
        bad.append("html_base.py (engine < 3.1.0 — cập nhật engine)")
    if bad:
        print(f"✗ bản sao ở engine LỆCH nguồn framework: {bad} — chép đè fdk/tools/html_font*.py sang {eng} rồi ship repo engine"); return 2
    print(f"✓ parity: engine ({eng}) khớp nguồn framework"); return 0


def main(argv=None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    if "--parity" in a:
        return parity()
    pages = []
    for x in [Path(v) for v in a if not v.startswith("--")]:
        pages += sorted(x.glob("*.html")) if x.is_dir() else [x]
    if not pages:
        print(__doc__); return 1
    bad = 0
    for p in pages:
        if not p.is_file():
            print(f"✗ {p}: không tồn tại"); bad += 1; continue
        pr = problems(p)
        if pr:
            bad += 1; print(f"✗ {p}: " + "; ".join(pr) + f"  → python3 {HERE / 'html_font.py'} --apply {p}")
    print(f"html-font-lint: {len(pages) - bad}/{len(pages)} trang đạt")
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
