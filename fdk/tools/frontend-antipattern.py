#!/usr/bin/env python3
"""frontend-antipattern — soi anti-pattern FRONTEND ở HTML sinh (0 token, no-LLM).

Cổng chất-lượng-HTML mà p_docs (medic) KHÔNG bắt: p_docs chỉ so generator↔đĩa (anti-drift),
không nhìn NỘI DUNG lỗi. Bắt các bẫy rẻ-tiền, tất định làm hỏng copy-paste / gây hiểu nhầm:

  [FAIL] ligature chưa tắt: file có <pre>/<code> mà thiếu `font-variant-ligatures:none`
         → mono-font ligate '--'/'-' thành em-dash: người đọc gõ sai lệnh (bug đã gặp 07/2026).
  [WARN] prose lọt code block: <pre>…</pre> chứa chữ tiếng Việt có dấu ở dòng KHÔNG phải
         comment (#) → câu văn lẫn vào lệnh, copy ra chạy lỗi. Heuristic → warn, người soi lại.

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


def main() -> None:
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
