"""showcase_dataviz — khối CHART + GRAPH của design-showcase (PLAN 220926-design-showcase t6), theo quy ước skill `diagram`:
SVG inline sinh bằng CODE từ dữ liệu (không vẽ tay toạ độ), không thư viện ngoài, chữ cùng font trang, màu từ token nên
đọc được ở cả sáng và tối, role="img" + <title> là con đầu. Số liệu thật khi có (đếm luật từ showcase_rules); số minh
hoạ thì ghi rõ trên hình. Mind map: lớp nền html_shell tự sinh từ h2/h3 cho trang docs-shell — không cần khối riêng.

proof: harness/tests/test_design_showcase.py
"""
import importlib.util
from pathlib import Path

GROUP = "Biểu đồ và sơ đồ"

_s = importlib.util.spec_from_file_location("showcase_rules", Path(__file__).resolve().parent / "showcase_rules.py")
_r = importlib.util.module_from_spec(_s); _s.loader.exec_module(_r)
RULES = _r.RULES
_by_gate = {g: sum(1 for r in RULES.values() if r["gate"] == g) for g in ("visual", "static", "doc")}
_GATE_VI = {"visual": "Cổng chạy thật", "static": "Cổng tĩnh", "doc": "Chỉ trong tài liệu"}

# token chung cho mọi hình: chữ, lưới, màu dữ liệu (một series = một màu nhấn)
_CSS_SVG = ("{r} svg{{display:block;width:100%;height:auto;font-family:inherit}}{r} .tx{{fill:var(--ovs-ink);font-size:13px}}"
            "{r} .mu{{fill:var(--ovs-ink2);font-size:12px}}{r} .gr{{stroke:var(--ovs-border);stroke-width:1}}")


def _bar() -> str:
    data = [(_GATE_VI[g], n) for g, n in _by_gate.items()]
    W, lw, bh, gap = 560, 150, 28, 16
    mx = max(n for _, n in data)
    H_ = len(data) * (bh + gap) + 8
    rows = []
    for i, (lb, n) in enumerate(data):
        y = 4 + i * (bh + gap); w = (W - lw - 48) * n / mx
        rows.append(f'<text class="tx" x="0" y="{y + bh / 2 + 5:.0f}">{lb}</text>'
                    f'<rect class="bar" x="{lw}" y="{y}" width="{w:.0f}" height="{bh}" rx="6"/>'
                    f'<text class="tx" x="{lw + w + 8:.0f}" y="{y + bh / 2 + 5:.0f}">{n}</text>')
    return (f'<svg viewBox="0 0 {W} {H_}" role="img" aria-labelledby="sc-bar-t"><title id="sc-bar-t">Số luật thiết kế theo nơi kiểm: '
            + ", ".join(f"{lb} {n}" for lb, n in data) + f'</title>{"".join(rows)}</svg>')


_LINE = [("T2", 61), ("T3", 48), ("T4", 40), ("T5", 22), ("T6", 9), ("T7", 3)]  # SỐ MINH HOẠ — ghi rõ trên hình


def _line() -> str:
    W, H_, pl, pb, pt = 560, 220, 40, 32, 16
    mx = 70
    xs = [pl + i * (W - pl - 16) / (len(_LINE) - 1) for i in range(len(_LINE))]
    ys = [pt + (H_ - pt - pb) * (1 - v / mx) for _, v in _LINE]
    grid = "".join(f'<line class="gr" x1="{pl}" x2="{W - 16}" y1="{pt + (H_ - pt - pb) * (1 - v / mx):.0f}" y2="{pt + (H_ - pt - pb) * (1 - v / mx):.0f}"/>'
                   f'<text class="mu" x="{pl - 8}" y="{pt + (H_ - pt - pb) * (1 - v / mx) + 4:.0f}" text-anchor="end">{v}</text>' for v in (0, 35, 70))
    path = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in zip(xs, ys))
    dots = "".join(f'<circle class="pt" cx="{x:.0f}" cy="{y:.0f}" r="4"/>' for x, y in zip(xs, ys))
    labels = "".join(f'<text class="mu" x="{x:.0f}" y="{H_ - 8}" text-anchor="middle">{lb}</text>' for x, (lb, _) in zip(xs, _LINE))
    return (f'<svg viewBox="0 0 {W} {H_}" role="img" aria-labelledby="sc-line-t"><title id="sc-line-t">Số liệu minh hoạ: số lỗi slop còn lại giảm từ 61 xuống 3 trong sáu ngày</title>'
            f'{grid}<path class="ln" d="{path}"/>{dots}{labels}</svg>')


_FLOW = [("PLAN.md", "việc + deps"), ("build", "graph.json"), ("next · lock", "chọn việc sẵn sàng"), ("chạy", "agent làm"), ("verify", "rc 0 mới xong")]


def _flow() -> str:
    bw, bh, gap = 132, 64, 32
    W = len(_FLOW) * bw + (len(_FLOW) - 1) * gap; H_ = bh + 8
    out = []
    for i, (t, s) in enumerate(_FLOW):
        x = i * (bw + gap)
        out.append(f'<g><rect class="box" x="{x}" y="4" width="{bw}" height="{bh}" rx="12"/>'
                   f'<text class="tx b" x="{x + bw / 2:.0f}" y="32" text-anchor="middle">{t}</text>'
                   f'<text class="mu" x="{x + bw / 2:.0f}" y="52" text-anchor="middle">{s}</text></g>')
        if i:
            ax = x - gap
            out.append(f'<path class="ar" d="M{ax + 4} {4 + bh / 2:.0f} H{x - 6}"/><path class="ah" d="M{x - 6} {bh / 2 - 1:.0f} l6 5 -6 5z"/>')
    return (f'<svg viewBox="-2 0 {W + 4} {H_}" role="img" aria-labelledby="sc-flow-t"><title id="sc-flow-t">Luồng orca-graph: '
            + " → ".join(t for t, _ in _FLOW) + f'</title>{"".join(out)}</svg>')


_n_fail = sum(1 for r in RULES.values() if r["level"] == "FAIL")
_n_warn = sum(1 for r in RULES.values() if r["level"] == "WARN")

BLOCKS = [
    dict(
        id="chart-bar", title="Biểu đồ cột ngang", rules=["svg-a11y", "font-embedded", "contrast", "no-cdn"],
        note="So sánh vài hạng mục: cột NGANG để nhãn tiếng Việt dài đọc thẳng; số in ngay cuối cột, không cần trục; một series = một màu nhấn. Số liệu thật: luật đếm từ showcase_rules.",
        html=f'<figure class="sc-chart-bar">{_bar()}<figcaption>Số luật thiết kế theo nơi kiểm (đếm từ code lúc build).</figcaption></figure>',
        css=(_CSS_SVG.format(r=".sc-chart-bar") + ".sc-chart-bar{margin:0}.sc-chart-bar .bar{fill:var(--ovs-accent)}"
             ".sc-chart-bar figcaption{margin:12px 0 0;font-size:13px;color:var(--ovs-ink2)}")),
    dict(
        id="chart-line", title="Biểu đồ đường", rules=["svg-a11y", "font-embedded", "contrast"],
        note="Xu hướng theo thời gian: ba vạch lưới mảnh, nhãn trục nhạt, đường 2px + chấm ở từng điểm. Số minh hoạ thì ghi rõ trên hình và trong chú thích (honest copy).",
        html=f'<figure class="sc-chart-line">{_line()}<figcaption>Số liệu minh hoạ, không phải số đo thật.</figcaption></figure>',
        css=(_CSS_SVG.format(r=".sc-chart-line") + ".sc-chart-line{margin:0}.sc-chart-line .ln{fill:none;stroke:var(--ovs-accent);stroke-width:2}"
             ".sc-chart-line .pt{fill:var(--ovs-bg);stroke:var(--ovs-accent);stroke-width:2}"
             ".sc-chart-line figcaption{margin:12px 0 0;font-size:13px;color:var(--ovs-ink2)}")),
    dict(
        id="stat-tile", title="Ô số liệu", rules=["contrast", "tight", "responsive-columns"],
        note="Số to (32px/800) · nhãn nhỏ phía dưới · tối đa 4 ô một hàng, tự rơi xuống khi hẹp. Chỉ số thật; không có thì để trống, không bịa.",
        html=('<div class="sc-stat-tile">'
              + "".join(f'<div class="s"><b>{v}</b><span>{lb}</span></div>'
                        for v, lb in [(len(RULES), "Luật thiết kế"), (_n_fail, "Luật chặn (FAIL)"), (_n_warn, "Luật cảnh báo (WARN)")])
              + '</div>'),
        css=(".sc-stat-tile{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(160px,100%),1fr));gap:16px}"
             ".sc-stat-tile .s{padding:16px 20px;border:1px solid var(--ovs-border);border-radius:14px;background:var(--ovs-surface2)}"
             ".sc-stat-tile b{display:block;font-family:var(--font-display);font-size:32px;font-weight:var(--fw-heading,600);line-height:1.1;font-variant-numeric:tabular-nums}"
             ".sc-stat-tile span{font-size:13px;color:var(--ovs-ink2)}")),
    dict(
        id="graph-flow", title="Sơ đồ luồng", rules=["svg-a11y", "overlap", "font-embedded", "horizontal-scroll"],
        note="Hộp + mũi tên, sinh bằng code từ danh sách bước; tên bước đậm, dòng phụ nhạt; mũi tên cùng màu chữ phụ. Sơ đồ phức tạp hơn thì gọi skill diagram, đừng vẽ tay.",
        html=f'<div class="sc-graph-flow">{_flow()}</div>',
        css=(_CSS_SVG.format(r=".sc-graph-flow") + ".sc-graph-flow{overflow-x:auto}.sc-graph-flow svg{min-width:560px}"
             ".sc-graph-flow .box{fill:var(--ovs-surface2);stroke:var(--ovs-border)}.sc-graph-flow .b{font-weight:600}"
             ".sc-graph-flow .ar{stroke:var(--ovs-ink2);stroke-width:1.5;fill:none}.sc-graph-flow .ah{fill:var(--ovs-ink2)}")),
]
