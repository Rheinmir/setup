#!/usr/bin/env python3
"""R22 html-slop: chặn NGAY LÚC GHI ba dấu hiệu AI-slop mà cổng tĩnh đã có luật, để agent không
phải chờ tới medic/CI mới biết.

(a) sọc viền MÀU một cạnh trên thẻ/nút/callout — `border-left|right: ≥3px solid <màu bão hoà>`.
(b) gradient-text — `background-clip:text` + chữ trong suốt.
(c) trang KHÔNG có chế độ tối — không `[data-theme=dark]`, không `prefers-color-scheme`.

Tại sao ghi luật ở đây thay vì chỉ dựa vào frontend-antipattern.py: cổng tĩnh chạy theo lô (medic,
CI) nên agent đã ghi xong hàng chục trang mới biết sai. Luật này chạy ở PostToolUse nhánh .html,
chặn đúng file vừa ghi (rc 2) kèm lệnh vá — cùng khuôn R16/R20.

Nguồn chân lý là frontend-antipattern.py: validator GỌI nó chứ không chép lại regex, để luật không
bao giờ lệch giữa hai cổng. Không tìm thấy tool → im lặng qua (fail-open, không phá phiên).

Miễn: artifact archify (viewer tự chứa, cùng cách miễn R16/R20) và file ngoài thư mục `html/`.

Contract: stdin JSON {"action":"write","file_path":...} hoặc argv files. Exit 0/2.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ARCHIFY_RE = re.compile(r"\barchify \d+\.\d+")
RULES = ("side-stripe", "gradient-text", "no-dark-mode")


def find_tool() -> "Path | None":
    """frontend-antipattern.py: cạnh repo (framework) → bản cài global (máy khách)."""
    here = Path(__file__).resolve()
    cands = [p / "fdk/tools/frontend-antipattern.py" for p in here.parents] + \
            [Path.home() / ".claude/harness/fdk/tools/frontend-antipattern.py"]
    return next((c for c in cands if c.is_file()), None)


def in_scope(path: str) -> bool:
    p = Path(path or "")
    return p.suffix == ".html" and p.parent.name == "html"


def problems(path: str):
    tool = find_tool()
    if tool is None:
        return []
    try:
        r = subprocess.run([sys.executable, str(tool), path], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return []
    out = r.stdout + r.stderr
    hits = []
    for line in out.splitlines():
        low = line.lower()
        if "✗" not in line:
            continue
        if "sọc viền" in line or "gradient text" in low or "gradient-text" in low or "chế độ tối" in line:
            hits.append(re.sub(r"\s+", " ", line.split(": ", 1)[-1]).strip()[:160])
    return hits


def check(path: str) -> None:
    if not in_scope(path):
        return
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    if ARCHIFY_RE.search(text) and "<svg" in text:
        return
    errs = problems(path)
    if errs:
        for e in errs:
            print(f"[R22 html-slop] {path}: {e}", file=sys.stderr)
        print(f"[R22 html-slop] vá máy-làm-được: python3 fdk/tools/html-slop-fix.py {path}", file=sys.stderr)
        sys.exit(2)


def self_test():
    import tempfile
    d = Path(tempfile.mkdtemp()) / "llmwiki" / "html"
    d.mkdir(parents=True)
    f = d / "p.html"
    ok_head = ('<html><head><style>:root{--bg:#fff}[data-theme=dark]{--bg:#000}'
               'pre,code{font-variant-ligatures:none;font-feature-settings:"liga" 0,"calt" 0}</style>'
               '</head><body><h1>x</h1>')

    def blocked(content):
        f.write_text(content, encoding="utf-8")
        try:
            check(str(f))
            return False
        except SystemExit as e:
            return e.code == 2

    if find_tool() is None:
        print("SKIP html_slop self-test: không thấy frontend-antipattern.py")
        return
    assert not blocked(ok_head + "</body></html>"), "trang sạch phải qua"
    assert blocked(ok_head.replace("--bg:#fff", "--bg:#fff}.card{border-left:3px solid #0a84ff")
                   + "<div class=card>a</div></body></html>"), "sọc viền một cạnh phải bị chặn"
    assert blocked(ok_head.replace("--bg:#fff", "--bg:#fff}h1{background:linear-gradient(90deg,#0a84ff,#5856d6);"
                                   "-webkit-background-clip:text;background-clip:text;color:transparent")
                   + "</body></html>"), "gradient-text phải bị chặn"
    # luật no-dark-mode chỉ soi trang có CSS THẬT (>400 ký tự style) — trang chuyển hướng/fixture tí hon được bỏ
    bulk = "".join(f".r{i}{{padding:{i}px;margin:{i}px;color:#111;background:#fff}}" for i in range(20))
    assert blocked(f'<html><head><style>{bulk}</style></head><body><h1>x</h1></body></html>'), \
        "trang không có chế độ tối phải bị chặn"
    arch = '<html>archify 2.17.0 <svg></svg><style>.card{border-left:3px solid #0a84ff}</style></html>'
    assert not blocked(arch), "artifact archify được miễn"
    outside = Path(tempfile.mkdtemp()) / "note.html"
    outside.write_text('<style>.card{border-left:3px solid #0a84ff}</style>', encoding="utf-8")
    try:
        check(str(outside))
    except SystemExit:
        raise AssertionError("file ngoài thư mục html/ không thuộc phạm vi")
    print("html_slop self-test OK")


def main() -> None:
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        return
    args = sys.argv[1:]
    if args:
        for p in args:
            check(p)
        sys.exit(0)
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if ev.get("action") == "write":
        check(ev.get("file_path", ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
