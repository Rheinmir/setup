#!/usr/bin/env python3
"""build-cheatsheet — nhồi (embed) toàn bộ SKILL.md vào trang cheatsheet để self-contained.

Đọc mọi `skills/<name>/SKILL.md`, đóng gói thành 1 block JSON
`<script id="skilldata" type="application/json">…</script>` và chèn vào trang
cheatsheet HTML (thay block cũ nếu đã có — idempotent). Sau đó mở `file://`
trang vẫn xem được full nội dung skill, KHÔNG cần server.

Escape `</` → `<\\/` để nội dung skill có chứa `</script>` (vd design-taste-frontend)
không phá thẻ script. `\\/` là escape JSON hợp lệ → JSON.parse khôi phục `/`.

Usage:
    python3 fdk/tools/build-cheatsheet.py                  # tự tìm trang trong llmwiki/html/
    python3 fdk/tools/build-cheatsheet.py <html> [skills_dir]
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def find_html() -> str:
    cands = sorted(glob.glob(os.path.join(ROOT, "llmwiki", "html", "*skills-cheatsheet.html")))
    if not cands:
        sys.exit("Không tìm thấy *skills-cheatsheet.html trong llmwiki/html/ — truyền đường dẫn làm tham số.")
    return cands[-1]


def main() -> None:
    html_path = sys.argv[1] if len(sys.argv) > 1 else find_html()
    skills_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "skills")

    data = {}
    for p in sorted(glob.glob(os.path.join(skills_dir, "*", "SKILL.md"))):
        name = os.path.basename(os.path.dirname(p))
        with open(p, encoding="utf-8") as f:
            data[name] = f.read()
    if not data:
        sys.exit(f"Không thấy SKILL.md nào trong {skills_dir}")

    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    block = '<script id="skilldata" type="application/json">' + payload + "</script>"

    with open(html_path, encoding="utf-8") as f:
        html = f.read()
    html = re.sub(r'<script id="skilldata"[^>]*>.*?</script>\n?', "", html, flags=re.S)
    idx = html.find("<script>")
    if idx == -1:
        sys.exit("Trang HTML không có <script> chính để chèn block data trước nó.")
    html = html[:idx] + block + "\n" + html[idx:]
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ embed {len(data)} skill · payload {len(payload)//1024} KB · "
          f"{os.path.relpath(html_path, ROOT)} now {len(html)//1024} KB")


if __name__ == "__main__":
    main()
