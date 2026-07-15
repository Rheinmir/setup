#!/usr/bin/env python3
"""frontend-antipattern — soi anti-pattern FRONTEND ở HTML sinh (0 token, no-LLM).

Cổng chất-lượng-HTML mà p_docs (medic) KHÔNG bắt: p_docs chỉ so generator↔đĩa (anti-drift),
không nhìn NỘI DUNG lỗi. Bắt các bẫy rẻ-tiền, tất định làm hỏng copy-paste / gây hiểu nhầm:

  [FAIL] ligature chưa tắt: file có <pre>/<code> mà thiếu `font-variant-ligatures:none`
         → mono-font ligate '--'/'-' thành em-dash: người đọc gõ sai lệnh (bug đã gặp 07/2026).
  [WARN] prose lọt code block: <pre>…</pre> chứa chữ tiếng Việt có dấu ở dòng KHÔNG phải
         comment (#) → câu văn lẫn vào lệnh, copy ra chạy lỗi. Heuristic → warn, người soi lại.

  Cổng slop-test hallmark, nhóm UNIVERSAL (chưng cất design-foundation, hấp thụ 07/2026):
  [FAIL] gradient TEXT (background-clip:text) — dấu hiệu AI kinh điển. Gradient NỀN vẫn hợp lệ.
  [FAIL] italic header (<h_> chứa <em>/<i>, hoặc h_{font-style:italic}) — AI-tell đáng tin nhất.
  [WARN] fake browser chrome vẽ tay (≥3 màu traffic-light) — cấm re-drawn chrome.
  [WARN] số liệu marketing bịa (`Nx faster`, `+NN% conversion`, `trusted by N,000+`) — honest-copy.
  Nhóm genre-scoped (Inter/system làm display, pure đen-trắng) KHÔNG ở đây — false-positive trên
  chính seq.html của ta. Để model xử lúc dựng UI sản phẩm qua skills/hallmark.

Exit: 0 sạch · 1 có FAIL · 2 chỉ WARN (medic map: 1→fail, 2→warn, 0→ok). Fail-open:
thiếu file → sạch (không chặn). Mặc định quét llmwiki/html/overstack.html; nhận path khác qua arg.

Usage:
  frontend-antipattern.py [file.html ...]   # mặc định overstack.html
  frontend-antipattern.py --json
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = [ROOT / "llmwiki" / "html" / "overstack.html"]
# chữ Việt có dấu (precomposed) — tín hiệu chắc: lệnh shell ASCII thuần không khớp
VN = re.compile(
    r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    r"ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]"
)
PRE = re.compile(r"<pre\b[^>]*>(.*?)</pre>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")

# ── Cổng slop-test hallmark, nhóm UNIVERSAL (chưng cất design-foundation) ──
# CHỈ những dấu hiệu KHÔNG BAO GIỜ hợp lệ, kể cả ở artifact kỹ thuật (seq/report).
# Nhóm genre-scoped (Inter/system làm display, pure đen-trắng, 3-cột-icon-tile) KHÔNG ở đây —
# chúng false-positive trên chính seq.html của ta (dùng system font + gradient NỀN). Để model
# xử lúc dựng UI sản phẩm qua skills/hallmark. Xem [[design-foundation]] § phạm vi.

# gradient TEXT (background-clip:text + gradient) — dấu hiệu AI kinh điển; gradient NỀN thì hợp lệ.
GRAD_TEXT = re.compile(
    r"(background-clip\s*:\s*text|-webkit-background-clip\s*:\s*text)", re.I)
# italic header: <h1..h6> chứa <em>/<i>, hoặc rule CSS cho heading + font-style:italic
ITALIC_H_EM = re.compile(r"<h[1-6]\b[^>]*>[^<]*<(?:em|i)\b", re.I)
ITALIC_H_CSS = re.compile(r"\bh[1-6]\b[^{}]*\{[^}]*font-style\s*:\s*italic", re.I)
# fake browser chrome: 3 chấm traffic-light vẽ tay (đỏ/vàng/lục cạnh nhau) — cấm re-drawn chrome
TRAFFIC = re.compile(
    r"(#ff5f5[06]|#febc2e|#28c840|#ff605c|#ffbd44|#00ca4e)", re.I)
# số liệu MARKETING bịa (honest-copy). Khớp mẫu quảng cáo, KHÔNG khớp số kỹ thuật (74/74, ~2.3k token).
FAKE_METRIC = re.compile(
    r"(\b\d+\s*[x×]\s*(?:faster|better|more)\b"
    r"|\+\s*\d+\s*%\s*(?:conversion|growth|faster|revenue|increase)"
    r"|\btrusted by\s+[\d,]+\+?\b"
    r"|\b[\d,]+\+\s*(?:teams|companies|customers|users)\s+(?:trust|use|love)\b)", re.I)


def _unesc(s: str) -> str:
    return (s.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
             .replace("&#39;", "'").replace("&amp;", "&"))


def scan(path: Path) -> list:
    """Trả list finding dict: {level, file, msg, snippet}."""
    out = []
    try:
        html = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return out  # fail-open: đọc không được → coi như sạch
    rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    has_code = ("<pre" in html) or ("<code" in html)
    # [FAIL] ligature — chỉ bắt khi CÓ code block
    if has_code and "font-variant-ligatures:none" not in html:
        out.append({"level": "FAIL", "file": str(rel),
                    "msg": "có <pre>/<code> nhưng thiếu `font-variant-ligatures:none` "
                           "(mono ligate '-' thành em-dash → gõ sai lệnh)",
                    "snippet": "pre,code{font-variant-ligatures:none;font-feature-settings:\"liga\" 0,\"calt\" 0}"})
    # ── Cổng slop-test hallmark (UNIVERSAL) — dấu hiệu AI không bao giờ hợp lệ ──
    # CHỈ quét trong <style> (+ inline style=""), KHÔNG quét cả trang: văn xuôi nhắc
    # `background-clip:text` để GIẢI THÍCH cổng thì không phải vi phạm (bài học R7-d, p-32).
    styles = "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", html, re.S | re.I))
    styles += "\n".join(re.findall(r'style\s*=\s*"([^"]*)"', html, re.I))
    if GRAD_TEXT.search(styles):
        out.append({"level": "FAIL", "file": str(rel),
                    "msg": "gradient TEXT (background-clip:text) — dấu hiệu AI kinh điển (slop-test #2). "
                           "Gradient NỀN thì hợp lệ; nhấn chữ bằng weight/màu đặc, không gradient.",
                    "snippet": "background-clip:text  ← bỏ"})
    if ITALIC_H_EM.search(html) or ITALIC_H_CSS.search(styles):
        out.append({"level": "FAIL", "file": str(rel),
                    "msg": "italic header — một trong những AI-tell đáng tin nhất (slop-test #38a). "
                           "Heading luôn roman; nhấn bằng weight/màu/underline, italic chỉ trong body.",
                    "snippet": "<h_>…<em> hoặc h_{font-style:italic}  ← bỏ"})
    if len(set(TRAFFIC.findall(styles))) >= 3:
        out.append({"level": "WARN", "file": str(rel),
                    "msg": "nghi fake browser chrome vẽ tay (≥3 màu traffic-light) — cấm re-drawn chrome "
                           "(discipline #4). Dùng screenshot thật trong <figure>, hoặc bỏ chrome.",
                    "snippet": "3 chấm đỏ/vàng/lục cạnh nhau"})
    for m in FAKE_METRIC.finditer(TAG.sub(" ", html)):
        out.append({"level": "WARN", "file": str(rel),
                    "msg": "nghi số liệu marketing BỊA (honest-copy, slop-test #46) — nếu không có nguồn thật, "
                           "dùng placeholder có nhãn hoặc đổi macrostructure.",
                    "snippet": m.group(0)[:60]})
        break
    # [WARN] prose lọt <pre> — chữ Việt có dấu ở dòng không-comment
    for block in PRE.findall(html):
        text = _unesc(TAG.sub("", block))
        for ln in text.splitlines():
            s = ln.strip()
            if not s or s.startswith("#"):
                continue  # dòng trống / comment shell → cho phép
            code_part = s.split("#", 1)[0]  # bỏ comment inline (`lệnh  # chú thích VN` hợp lệ)
            if VN.search(code_part):
                out.append({"level": "WARN", "file": str(rel),
                            "msg": "prose tiếng Việt lọt code block (copy ra chạy lỗi)",
                            "snippet": s[:80]})
                break  # 1 cảnh báo / block là đủ
    return out


def _scan_text(html: str) -> list:
    """scan() nhưng trên chuỗi (cho self-test, không cần file thật)."""
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        tmp = Path(f.name)
    try:
        return scan(tmp)
    finally:
        tmp.unlink()


def self_test() -> int:
    """Bite-test: cổng slop hallmark phải BẮT bản BAD và THA bản GOOD. Exit 0 pass / 1 fail."""
    BAD = ("<html><head><style>.h1{background:linear-gradient(135deg,#0a84ff,#5856d6);"
           "-webkit-background-clip:text;color:transparent} h2{font-style:italic}</style></head>"
           "<body><h1>x</h1><h2>Built to <em>think</em></h2>"
           "<p>10x faster than the competition, trusted by 50,000+ teams</p></body></html>")
    GOOD = ("<html><head><style>.h1{color:#0a2540;font-weight:800}"
            "code{font-variant-ligatures:none}</style></head>"
            "<body><h1>x</h1><p>đo thật: 74/74 test PASS, cắt ~2.307 token</p></body></html>")
    bad = _scan_text(BAD)
    good = _scan_text(GOOD)
    bad_kinds = {f["msg"][:20] for f in bad}
    ok = True
    checks = [
        ("BAD bắt gradient-text", any("gradient TEXT" in f["msg"] for f in bad)),
        ("BAD bắt italic-header (em)", any("italic header" in f["msg"] for f in bad)),
        ("BAD bắt số liệu marketing", any("marketing" in f["msg"] for f in bad)),
        ("GOOD sạch (0 finding)", len(good) == 0),
    ]
    for label, passed in checks:
        print(f"  {'✓' if passed else '✗'} {label}")
        ok = ok and passed
    print("self-test: PASS" if ok else "self-test: FAIL")
    return 0 if ok else 1


def main() -> None:
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv
    targets = [Path(a) for a in args] if args else DEFAULT
    findings = []
    for t in targets:
        findings += scan(t)
    fails = [f for f in findings if f["level"] == "FAIL"]
    warns = [f for f in findings if f["level"] == "WARN"]
    if as_json:
        import json
        print(json.dumps({"fail": len(fails), "warn": len(warns), "findings": findings},
                         ensure_ascii=False))
    else:
        for f in findings:
            mark = "\033[1;31m✗\033[0m" if f["level"] == "FAIL" else "\033[1;33m⚠\033[0m"
            print(f"  {mark} {f['file']}: {f['msg']}\n      → {f['snippet']}")
        n = len([t for t in targets if t.exists()])
        if not findings:
            print(f"  \033[1;32m✓\033[0m {n} file HTML sạch anti-pattern frontend")
        else:
            print(f"\n  {len(fails)} FAIL · {len(warns)} WARN trên {n} file")
    sys.exit(1 if fails else (2 if warns else 0))


if __name__ == "__main__":
    main()
