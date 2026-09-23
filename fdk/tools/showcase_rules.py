#!/usr/bin/env python3
"""showcase_rules — danh sách MÁY ĐỌC ĐƯỢC mọi luật thiết kế của framework (PLAN 220926-design-showcase t1).

Trang showcase (`build-design-showcase.py`) phải có ≥ 1 khối minh hoạ cho MỖI luật ở đây; test
`harness/tests/test_design_showcase.py` đỏ khi luật mới thêm vào cổng mà chưa có khối mẫu.

Nguồn (đọc từ code, không chép tay — cổng đổi thì danh sách đổi theo):
  visual  fdk/tools/html-visual-gate.mjs — id ở phần chú thích đầu file; mức = WARN nếu code `warns.push(\\`<id>:`, còn lại FAIL
  static  fdk/tools/frontend-antipattern.py — `add("FAIL|WARN", "<id>"` + nhóm luật cũ chưa có id (khai ở STATIC_LEGACY)
  doc     luật chỉ có trong tài liệu (skills/hallmark/references/design-default.md, docs-site-macos) — khai ở DOC

    python3 fdk/tools/showcase_rules.py          # bảng id · cổng · mức
    python3 fdk/tools/showcase_rules.py --json


proof: harness/tests/test_design_showcase.py
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# frontend-antipattern.py có các luật trước khi có trường "rule" — id đặt ở đây, mô tả theo docstring của nó
STATIC_LEGACY = {
    "ligature-off": ("FAIL", "code/pre phải tắt ligature (font-variant-ligatures:none) — '--' không thành em-dash"),
    "gradient-text": ("FAIL", "cấm chữ tô gradient (background-clip:text); gradient NỀN hợp lệ"),
    "italic-header": ("FAIL", "tiêu đề không in nghiêng, kể cả <em>/<i> bên trong"),
    "svg-a11y": ("WARN", "sơ đồ SVG có role=img + <title> là con đầu; không tham chiếu http ngoài"),
}
DOC = {
    "eight-states": ("MUST", "nút/input đủ 8 trạng thái: default · hover · focus-visible · active · disabled · loading · error · success"),
    "motion-ease-out": ("MUST", "phản hồi bấm dùng ease-out ≤ 240ms, không ease-in"),
    "reduced-motion": ("MUST", "prefers-reduced-motion: chỉ crossfade opacity ≤ 150ms"),
    "font-embedded": ("MUST", "Be Vietnam Pro nhúng 400/600/800, chữ trong sơ đồ cùng font trang"),
    "minimal-disclosure": ("MUST", "màn đầu chỉ tóm tắt, chi tiết bấm mới hiện (<details>, dialog)"),
    "responsive-columns": ("MUST", "lưới 1–4 cột rơi dần về 1 cột theo điểm gãy, không cuộn ngang ở 320px"),
    "no-cdn": ("MUST", "trang tự chứa, mở offline: không script/font/CSS từ CDN ngoài"),
}


def visual_rules(src: str) -> dict:
    head = src.split("\nimport ", 1)[0]
    ids = re.findall(r"^//   ([a-z][a-z-]+[a-z])\s{2,}(?:FAIL|WARN)?\s*(.+)$", head, re.M)
    warn = set(re.findall(r"warns\.push\(`([a-z-]+):", src))
    return {i: {"gate": "visual", "level": "WARN" if i in warn else "FAIL", "text": t.strip()} for i, t in ids}


def static_rules(src: str) -> dict:
    out = {i: {"gate": "static", "level": lv, "text": t} for i, (lv, t) in STATIC_LEGACY.items()}
    for lv, i in re.findall(r'add\("(FAIL|WARN)",\s*"([a-z0-9-]+)"', src):
        out.setdefault(i, {"gate": "static", "level": lv, "text": "frontend-antipattern.py"})
    return out


def load() -> dict:
    rules = {}
    rules.update(static_rules((HERE / "frontend-antipattern.py").read_text(encoding="utf-8")))
    rules.update(visual_rules((HERE / "html-visual-gate.mjs").read_text(encoding="utf-8")))  # trùng id (rounded-edge) → cổng chạy-thật thắng
    rules.update({i: {"gate": "doc", "level": lv, "text": t} for i, (lv, t) in DOC.items()})
    return rules


RULES = load()

if __name__ == "__main__":
    if "--json" in sys.argv:
        print(json.dumps(RULES, ensure_ascii=False, indent=1))
    else:
        for i, r in sorted(RULES.items(), key=lambda kv: (kv[1]["gate"], kv[0])):
            print(f"{i:<26} {r['gate']:<7} {r['level']:<5} {r['text'][:90]}")
