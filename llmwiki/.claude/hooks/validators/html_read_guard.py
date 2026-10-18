#!/usr/bin/env python3
"""R23 html-read-guard: đừng đọc lại trang HTML MÁY SINH — đọc nguồn của nó. Nguồn là đủ (user 06/10/2026: "đọc md là đủ rồi").

Trang máy sinh nặng 270KB–1MB (font nhúng, engine sơ đồ, viewer) mà nội dung thật nằm ở nguồn nhỏ hơn hàng chục lần; đọc trang
= tốn lượt (Read từ chối > 25k token rồi agent đọc từng mảnh) hoặc đổ cả khối vào context qua cat/sed. Chỉ chặn trang CÓ nguồn
khác để đọc — trang mà HTML chính là nguồn (landing hallmark, UI kit, trang viết tay) vẫn đọc/sửa bình thường:
  • trang md-render  (chân trang ghi `bởi <code>md-render.py</code>`)  → đọc file .md ghi ở chân trang
  • artifact archify (chữ ký `archify <ver>` + <svg>)                 → đọc spec `<tên>.<loại>.json` cạnh nó
  • trang generator  (overstack, wiki-graph, control-room*, *.graph.html, memory-map, skill-whiteboard, atlas)
                                                                       → đọc dữ liệu/generator, hoặc chụp ảnh nếu cần nhìn
Ngoại lệ: lượt hiện tại do user gọi SLASH một skill audit (/qc-uiux, /visual-qa, /design-prim, /hallmark, /impeccable,
/redesign-existing-projects, hoặc tên có "audit") — audit cần soi chính trang. Thoát tay: OVERSTACK_READ_HTML=1.
Bash: chỉ chặn lệnh ĐỔ nội dung (cat/less/more/bat/head/tail/sed/awk) lên trang máy sinh; grep/wc (đếm, tìm) vẫn được.

Contract: stdin JSON {"action":"read"|"bash","file_path"|"command":…,"transcript_path":…} hoặc argv <file.html>. Exit 0/2.
Fail-open: lỗi đọc file/transcript → cho qua.
"""
import json
import os
import re
import shlex
import sys
from pathlib import Path

GEN_NAMES = re.compile(r"^(overstack|wiki-graph|memory-map|skill-whiteboard|atlas|control-room(-[\w-]+)?)\.html$|\.graph\.html$")
MD_RENDER = re.compile(r"Sinh từ <code>([^<]+\.md)</code> bởi <code>md-render\.py</code>")
ARCHIFY = re.compile(r"\barchify \d+\.\d+")
AUDIT_SKILLS = {"qc-uiux", "visual-qa", "design-prim", "hallmark", "impeccable", "redesign-existing-projects", "qc-code"}
DUMP_CMDS = {"cat", "less", "more", "bat", "head", "tail", "sed", "awk"}


def source_of(path: Path):
    """→ (loại, gợi ý nguồn) nếu là trang máy sinh, None nếu HTML chính là nguồn."""
    if path.suffix.lower() != ".html" or not path.is_file():
        return None
    try:
        with path.open("rb") as f:
            head = f.read(400_000).decode("utf-8", "ignore")
            f.seek(max(0, path.stat().st_size - 8_000))
            tail = f.read().decode("utf-8", "ignore")
    except OSError:
        return None
    m = MD_RENDER.search(tail) or MD_RENDER.search(head)
    if m:
        return "trang md-render", f"đọc nguồn: {m.group(1)} (sửa md rồi chạy lại md-render.py)"
    if ARCHIFY.search(head) and "<svg" in head:
        specs = sorted(str(p) for p in path.parent.glob(path.stem + ".*.json"))
        return "artifact archify", ("đọc spec: " + ", ".join(specs)) if specs else "đọc spec .json đã dùng để deliver (cùng tên, cạnh file)"
    if GEN_NAMES.search(path.name):
        return "trang generator", "trang này máy sinh từ dữ liệu/code — đọc dữ liệu nguồn hoặc generator; cần NHÌN thì chụp ảnh (playwright-verify)"
    return None


def audit_turn(transcript_path: str) -> bool:
    """Lượt hiện tại bắt đầu bằng slash command của một skill audit? (tin nhắn user gần nhất không phải tool_result)."""
    try:
        p = Path(transcript_path)
        with p.open("rb") as f:
            f.seek(max(0, p.stat().st_size - 3_000_000))
            lines = f.read().decode("utf-8", "ignore").splitlines()
    except (OSError, TypeError):
        return False
    for ln in reversed(lines):
        if '"type":"user"' not in ln.replace(" ", ""):
            continue
        try:
            msg = (json.loads(ln).get("message") or {}).get("content")
        except ValueError:
            continue
        text = msg if isinstance(msg, str) else " ".join(c.get("text", "") for c in msg or [] if isinstance(c, dict) and c.get("type") == "text")
        if not text.strip():
            continue                                   # tool_result → đi tiếp về tin nhắn user thật
        names = re.findall(r"<command-name>/?([\w:-]+)</command-name>", text)
        return any(n.split(":")[-1] in AUDIT_SKILLS or "audit" in n for n in names)
    return False


def targets(event: dict):
    if event.get("action") == "read":
        return [event.get("file_path", "")]
    cmd = event.get("command", "")
    out = []
    for seg in re.split(r"[|;&]+", cmd):
        try:
            words = shlex.split(seg)
        except ValueError:
            words = seg.split()
        if words and os.path.basename(words[0]) in DUMP_CMDS:
            out += [w for w in words[1:] if w.lower().endswith(".html")]
    return out


def check(event: dict) -> None:
    if os.environ.get("OVERSTACK_READ_HTML") == "1":
        return
    hits = []
    for t in targets(event):
        src = source_of(Path(os.path.expanduser(t)))
        if src:
            hits.append((t, *src))
    if not hits or audit_turn(event.get("transcript_path", "")):
        return
    for t, kind, hint in hits:
        print(f"[R23 html-read-guard] {t}: {kind} — đừng đọc lại trang máy sinh (nặng, nội dung nằm ở nguồn). {hint}. "
              f"Cần soi chính trang (audit) → user gọi /qc-uiux hoặc skill audit bằng slash; thoát tay OVERSTACK_READ_HTML=1.",
              file=sys.stderr)
    sys.exit(2)


def main():
    if sys.argv[1:] and sys.argv[1] != "--self-test":
        for p in sys.argv[1:]:
            check({"action": "read", "file_path": p})
        return
    if sys.argv[1:] == ["--self-test"]:
        return self_test()
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    check(event)


def self_test():
    import tempfile
    d = Path(tempfile.mkdtemp())
    md = d / "p-seq.html"; md.write_text("<html><body><footer><p>Sinh từ <code>/x/p.md</code> bởi <code>md-render.py</code></p></footer></body></html>")
    hand = d / "landing.html"; hand.write_text("<html><head><style id=\"ovs-font\"></style></head><body>landing</body></html>")
    arch = d / "o.html"; arch.write_text("<html>archify 2.17.0 <svg></svg></html>"); (d / "o.sequence.json").write_text("{}")
    gen = d / "wiki-graph.html"; gen.write_text("<html></html>")

    def blocked(ev):
        try:
            check(ev); return False
        except SystemExit as e:
            return e.code == 2
    assert blocked({"action": "read", "file_path": str(md)}), "trang md-render phải bị chặn"
    assert blocked({"action": "read", "file_path": str(arch)}) and blocked({"action": "read", "file_path": str(gen)})
    assert not blocked({"action": "read", "file_path": str(hand)}), "HTML là nguồn (landing) phải đọc được"
    assert not blocked({"action": "read", "file_path": str(d / "a.md")})
    assert blocked({"action": "bash", "command": f"cat {md} | head"}), "cat trang máy sinh phải bị chặn"
    assert not blocked({"action": "bash", "command": f"grep -c desc {md}"}), "grep đếm vẫn được"
    tr = d / "t.jsonl"
    tr.write_text(json.dumps({"type": "user", "message": {"content": "<command-name>/qc-uiux</command-name> soi"}}) + "\n"
                  + json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": "x"}]}}) + "\n")
    assert not blocked({"action": "read", "file_path": str(md), "transcript_path": str(tr)}), "lượt /qc-uiux được đọc"
    tr.write_text(json.dumps({"type": "user", "message": {"content": "sửa trang giúp tôi"}}) + "\n")
    assert blocked({"action": "read", "file_path": str(md), "transcript_path": str(tr)}), "lượt thường vẫn chặn"
    os.environ["OVERSTACK_READ_HTML"] = "1"
    assert not blocked({"action": "read", "file_path": str(md)}); del os.environ["OVERSTACK_READ_HTML"]
    print("html_read_guard --self-test: 10/10 ok")


if __name__ == "__main__":
    main()
