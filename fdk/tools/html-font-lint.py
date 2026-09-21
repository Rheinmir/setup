#!/usr/bin/env python3
"""html-font-lint — GÁC luật "mọi HTML framework sinh ra dùng font mặc định Lexend Deca Light, NHÚNG" (user chốt 20/09/2026).

    html-font-lint.py trang.html [thư-mục …]     rc 2 + tên từng trang thiếu font · thư mục = mọi *.html ngay trong đó
    html-font-lint.py --parity                    bản sao html_font ở repo engine (orca-graph) còn khớp nguồn framework không

Một trang ĐẠT khi có đủ: khối <style id="ovs-font"> (do html_font.apply chèn) · `font-family:'Lexend Deca'` · font nhúng
`data:font/woff2;base64,` · mặc định nội dung `--fw-text:300` · và KHÔNG gọi fonts.googleapis.com (nhúng hết = 0 request ngoài).
"""
import importlib.util, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NEED = ('id="ovs-font"', "font-family:'Lexend Deca'", "data:font/woff2;base64,", "--fw-text:300")


def problems(page: Path) -> list:
    h = page.read_text(encoding="utf-8", errors="ignore")
    out = [f"thiếu `{n}`" for n in NEED if n not in h]
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
    bad = [k for k in ("FONT_TEXT", "FONT_MONO", "WEIGHT_TEXT", "WEIGHT_STRONG", "STYLE_ID") if getattr(mine, k) != getattr(theirs, k, None)]
    if (HERE / "html_font_data.py").read_bytes() != (eng / "html_font_data.py").read_bytes():
        bad.append("html_font_data.py (file font nhúng)")
    if (eng / "html_base.py").is_file():             # engine ≥ 3.1.0 mang cả LỚP NỀN — token sáng/tối phải khớp, không thì trang graph lệch màu với phần còn lại
        mb, tb = _load(HERE / "html_base.py"), _load(eng / "html_base.py")
        bad += [f"html_base.{k}" for k in ("LIGHT", "DARK", "KEY", "STYLE_ID") if getattr(mb, k) != getattr(tb, k, None)]
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
