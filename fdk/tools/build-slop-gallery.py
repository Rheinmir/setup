#!/usr/bin/env python3
"""build-slop-gallery — trang nghiệm thu BẰNG MẮT cho đợt dọn slop: mỗi trang một hàng,
ảnh TRƯỚC / SAU ở cả sáng và tối, kèm số finding trước → sau.

Vì sao cần: tiêu chí "xong" của đợt này do user đặt là "nhìn ảnh thấy ổn", không phải "cổng xanh".
Cổng chỉ chứng minh luật không bị vi phạm; nó không nói trang có DỄ NHÌN hơn không.

Số liệu KHÔNG bịa:
  • cột TRƯỚC đọc từ bảng đo của trang baseline (`fdk/wiki/sources/200926-slop-baseline.md`),
  • cột SAU chạy lại chính hai cổng ngay lúc dựng trang (tĩnh + chạy-thật nếu có Playwright).
Trang nào thiếu một trong hai vế thì ghi "—", không suy đoán.

    python3 fdk/tools/build-slop-gallery.py --before scratchpad/slop-before --after scratchpad/slop-after

Exit: 0 dựng xong · 1 thiếu ảnh/đối số.
"""
import argparse
import base64
import html as H
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

# tên ảnh ↔ trang thật. Cùng danh sách với scratchpad/slop/shot.mjs (ảnh TRƯỚC) và slop-after/shot.mjs.
PAGES = {
    "overstack": "llmwiki/html/overstack.html",
    "index": "llmwiki/html/index.html",
    "cockpit": "llmwiki/html/control-room.html",
    "kanban": "llmwiki/html/control-room-kanban.html",
    "detail": "llmwiki/html/control-room-detail.html",
    "health": "llmwiki/html/280626-health-dashboard.html",
    "prd": "llmwiki/html/080926-prd-grade-fe-seq.html",
    "arch": "llmwiki/html/170926-orca-graph-gates-architecture.html",
}


def is_archify(p: Path) -> bool:
    """Artifact archify là viewer tự chứa — cổng tĩnh miễn nó (như R16/R20 và `--all`)."""
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return bool(re.search(r"\barchify \d+\.\d+", t)) and "<svg" in t


def _load(name, fname):
    s = importlib.util.spec_from_file_location(name, HERE / fname)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def before_counts(baseline: Path) -> dict:
    """Đọc bảng cổng chạy-thật của trang baseline → {đường dẫn trang: tổng số chỗ vi phạm}."""
    if not baseline.is_file():
        return {}
    out = {}
    for line in baseline.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*`([^`]+)`\s*\|(.+)\|\s*(ok|MISSING|NO-EFFECT)\s*\|\s*$", line.strip())
        if not m:
            continue
        nums = [int(x) for x in re.findall(r"\b\d+\b", m.group(2))]
        out["llmwiki/" + m.group(1)] = {"total": sum(nums), "toggle": m.group(3)}
    return out


def after_counts(rel_paths) -> dict:
    """Chạy LẠI hai cổng ngay bây giờ. Không có Playwright → phần chạy-thật trả None (ghi '—')."""
    out = {p: {"static": None, "runtime": None, "toggle": None} for p in rel_paths}
    stat = HERE / "frontend-antipattern.py"
    if stat.is_file():
        for p in rel_paths:
            if is_archify(ROOT / p):
                out[p]["static"] = "miễn"       # artifact archify — cùng cách miễn R16/R20 và `--all`
                continue
            r = subprocess.run([sys.executable, str(stat), str(ROOT / p)],
                               capture_output=True, text=True, cwd=ROOT)
            out[p]["static"] = (r.stdout + r.stderr).count("✗")
    gate = HERE / "html-visual-gate.mjs"
    node = shutil.which("node")
    if gate.is_file() and node:
        env_root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
        r = subprocess.run([node, str(gate), *[str(ROOT / p) for p in rel_paths], "--json"],
                           capture_output=True, text=True, cwd=ROOT,
                           env={**__import__("os").environ, "NODE_PATH": env_root})
        if r.returncode == 4:
            print("build-slop-gallery: bỏ cột chạy-thật — không có Playwright", file=sys.stderr)
        else:
            try:
                rows = json.loads(r.stdout)
            except ValueError:
                rows = []
                print("build-slop-gallery: cổng chạy-thật không trả JSON đọc được "
                      f"(rc {r.returncode}): {r.stderr.strip()[:160]}", file=sys.stderr)
            for row in rows:
                pg = Path(row["page"])
                rel = str(pg.relative_to(ROOT)) if pg.is_absolute() else str(pg)
                n = sum(len(row.get(m, {}).get(k, [])) for m in ("light", "dark")
                        for k in ("contrast", "tight", "overlap", "stripe"))
                out.setdefault(rel, {"static": None})
                out[rel]["runtime"] = n
                out[rel]["toggle"] = row.get("toggle")
    return out


def img(p: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def cell(before: Path, after: Path, label: str) -> str:
    def one(p, tag):
        if not p.is_file():
            return f'<figure class="shot"><div class="miss">không có ảnh {tag}</div><figcaption>{tag}</figcaption></figure>'
        return (f'<figure class="shot"><img src="{img(p)}" alt="{H.escape(label)} — {tag}" loading="lazy">'
                f'<figcaption>{tag}</figcaption></figure>')
    return one(before, "trước") + one(after, "sau")


def build(before_dir: Path, after_dir: Path, baseline: Path, out: Path) -> int:
    pairs = []
    for name, rel in PAGES.items():
        shots = {t: (before_dir / f"{name}-{t}.png", after_dir / f"{name}-{t}.png") for t in ("light", "dark")}
        if not any(b.is_file() or a.is_file() for b, a in shots.values()):
            continue
        pairs.append((name, rel, shots))
    if not pairs:
        print("build-slop-gallery: không tìm thấy cặp ảnh nào", file=sys.stderr)
        return 1

    bef = before_counts(baseline)
    aft = after_counts([rel for _, rel, _ in pairs])

    rows, secs = [], []
    for name, rel, shots in pairs:
        b = bef.get(rel)
        a = aft.get(rel, {})
        b_txt = "—" if b is None else f'{b["total"]} chỗ · toggle {b["toggle"]}'
        a_run = a.get("runtime")
        a_txt = "—" if a_run is None else f'{a_run} chỗ · toggle {a.get("toggle") or "—"}'
        a_stat = a.get("static")
        rows.append(f"<tr><td><a href=\"#{name}\">{H.escape(rel)}</a></td><td>{b_txt}</td>"
                    f"<td>{a_txt}</td><td>{'—' if a_stat is None else a_stat}</td></tr>")
        secs.append(
            f'<section id="{name}"><h2>{H.escape(rel)}</h2>'
            f'<p class="meta">cổng chạy-thật: <b>{b_txt}</b> → <b>{a_txt}</b> · cổng tĩnh sau: '
            f'<b>{"—" if a_stat is None else str(a_stat) + " finding"}</b></p>'
            f'<h3 class="sub">Chế độ sáng</h3><div class="pair">{cell(*shots["light"], rel)}</div>'
            f'<h3 class="sub">Chế độ tối</h3><div class="pair">{cell(*shots["dark"], rel)}</div></section>')

    nav = "<nav aria-label=\"Mục lục\">" + "".join(
        f'<a href="#{n}">{H.escape(Path(r).name)}</a>' for n, r, _ in pairs) + "</nav>"
    doc = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dọn slop 20/09/2026 — ảnh trước/sau</title>
<style>
  body{{margin:0;font:15px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}}
  .wrap{{max-width:1180px;margin:0 auto;padding:28px 20px 64px}}
  nav{{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 28px}}
  nav a{{padding:5px 10px;border:1px solid var(--ovs-border,#d7dee8);border-radius:8px;font-size:13px;text-decoration:none;color:var(--ovs-accent,#0059b8)}}
  td a{{color:var(--ovs-accent,#0059b8)}}
  table{{border-collapse:collapse;width:100%;margin:14px 0 34px;font-size:14px}}
  th,td{{border:1px solid var(--ovs-border,#d7dee8);padding:7px 10px;text-align:left}}
  th{{font-size:11px;letter-spacing:.06em;text-transform:uppercase}}
  section{{margin:0 0 46px;padding-top:6px}}
  h2{{font-size:19px;margin:0 0 4px}}
  h3.sub{{font-size:13px;font-weight:650;margin:18px 0 8px}}
  .meta{{margin:0;font-size:13px}}
  .pair{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
  .shot{{margin:0}}
  .shot img{{width:100%;height:auto;border:1px solid var(--ovs-border,#d7dee8);border-radius:10px;display:block}}
  .shot figcaption{{margin-top:6px;font-size:12px}}
  .miss{{display:grid;place-items:center;min-height:180px;padding:16px;border:1px dashed var(--ovs-border,#d7dee8);border-radius:10px;font-size:13px}}
  @media (max-width:760px){{.pair{{grid-template-columns:1fr}}}}
</style></head>
<body><div class="wrap">
<h1>Dọn slop — ảnh trước/sau</h1>
<p>Mỗi trang một mục: ảnh chụp cùng khung 1360×900, cùng cách ép chế độ, trước và sau đợt sửa ngày 20/09/2026.
Số ở cột "trước" lấy từ bảng đo của trang baseline; số ở cột "sau" chạy lại hai cổng ngay lúc dựng trang này.</p>
{nav}
<table><thead><tr><th>Trang</th><th>Cổng chạy-thật — trước</th><th>Cổng chạy-thật — sau</th><th>Cổng tĩnh — sau</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
{''.join(secs)}
<footer><p>File: <code>{out.resolve()}</code> · <code>{out}</code></p></footer>
</div></body></html>"""

    doc = _load("ovs_html_base", "html_base.py").apply(doc)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"→ {out.resolve()}  ({len(pairs)} trang · {out.stat().st_size // 1024} KB)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", default="scratchpad/slop-before")
    ap.add_argument("--after", default="scratchpad/slop-after")
    ap.add_argument("--baseline", default="fdk/wiki/sources/200926-slop-baseline.md")
    ap.add_argument("--out", default="llmwiki/html/200926-slop-before-after.html")
    a = ap.parse_args()
    return build(ROOT / a.before, ROOT / a.after, ROOT / a.baseline, ROOT / a.out)


if __name__ == "__main__":
    sys.exit(main())
