#!/usr/bin/env python3
"""mermaid-audit — soi mọi sơ đồ Mermaid theo MẪU CHUẨN, tất định, 0-token.

Mẫu chuẩn (user chọn 02/10/2026): sơ đồ "Vẽ sơ đồ harness agent" — flowchart dọc 14 nút, một tông tím, nút bo góc 16px
(nền #EFE5FE, viền rgba(0,0,0,.1)), nút QUYẾT ĐỊNH cũng là hộp bo góc nhưng nền nhạt #F9F5FE + viền nét đứt #D7CEE5 và câu
hỏi kết thúc bằng "?", chữ #6B3AB4 đậm 600 căn giữa, tối đa hai dòng (dòng chính + dòng chi tiết), mũi tên xám #8F8F8F 1px
nét liền đi vuông góc, nhãn mũi tên là viên thuốc ngắn ("Có", "Không", "Đạt", "Cần sửa, còn ngân sách").

Luật kiểm (mỗi luật là thứ đọc được thẳng từ mã Mermaid, không cần render):
  M1 flowchart/graph phải đọc từ trên xuống (TD/TB) như mẫu                          — WARN
  M2 không dùng hình thoi {…} cho quyết định — dùng hộp bo góc + class decision       — FAIL
  M3 nút quyết định (hình thoi hoặc class decision) phải là câu hỏi kết thúc bằng "?"  — FAIL
  M4 nhãn nút tối đa 2 dòng gõ tay, mỗi dòng ≤ 40 ký tự (dòng dài nhất của mẫu, để renderer tự ngắt) — FAIL
  M5 nhãn mũi tên ≤ 5 từ                                                                — FAIL
  M6 tối đa 15 nút một sơ đồ (mẫu 14) — nhiều hơn thì tách                             — FAIL
  M7 một tông màu: không quá 2 màu nền khai bằng style/classDef                         — FAIL
  M8 không emoji, không nhãn VIẾT HOA toàn bộ (≥ 3 từ chữ; mã/viết tắt như "M11 CLI" không tính) — FAIL
  M9 chỉ mũi tên thường (-->, ---): không trộn nét đậm ==> hay nét chấm -.->           — WARN

Dùng: mermaid-audit.py [file|thư mục ...]   (không đối số = quét cả repo, bỏ external/vendor/archive/scratchpad)
Exit: 0 sạch · 2 có FAIL.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP = ("/.git/", "/node_modules/", "/scratchpad/", "/worktrees/", "/external/", "/vendor/", "/archive/", "/llmwiki/raw/")   # raw/ = tài liệu gốc user đưa vào, không phải sơ đồ mình vẽ — truyền đường dẫn để quét
MAX_NODES, MAX_LINES, MAX_LINE_CHARS, MAX_EDGE_WORDS, MAX_FILLS = 15, 2, 40, 5, 2

MD_BLOCK = re.compile(r"```mermaid\s*\n(.*?)```", re.S)
HTML_BLOCK = re.compile(r'<(pre|div)\b[^>]*class="[^"]*\bmermaid(?:-src)?\b[^"]*"[^>]*>(.*?)</\1>', re.S | re.I)
# nút: id + hình. Thứ tự quan trọng: {{…}} trước {…}, ([…]) trước […]
NODE = re.compile(r"\b([A-Za-z_][\w-]*)\s*(\(\[|\[\[|\[\(|\(\(|\{\{|\[/|\[\\|\[|\(|\{|>)(.*?)(\]\)|\]\]|\)\]|\)\)|\}\}|/\]|\\\]|\]|\)|\})")
EDGE_LABEL = re.compile(r"(?:--|==|-\.)\s*\|?([^|>\n-][^|\n]*?)\|?\s*(?:-->|==>|\.->|---)|(?:-->|==>|-\.->|---)\s*\|([^|\n]+)\|")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
FILL = re.compile(r"fill\s*:\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|[a-z]+)")


def _lines(label: str) -> list:
    label = re.sub(r"^[\"']|[\"']$", "", label.strip())
    return [x.strip() for x in re.split(r"<br\s*/?>|\\n", label) if x.strip()]


def audit(dsl: str) -> list:
    """Trả về [(mức, luật, thông điệp)] cho MỘT sơ đồ."""
    out = []
    head = dsl.strip().splitlines()[0].strip() if dsl.strip() else ""
    kind = head.split()[0] if head else ""
    body = "\n".join(l for l in dsl.splitlines()[1:] if not l.strip().startswith("%%"))
    if kind in ("flowchart", "graph") and not re.match(r"(flowchart|graph)\s+(TD|TB)\b", head):
        out.append(("WARN", "M1", f"'{head}' — mẫu đọc từ trên xuống (TD)"))

    decision_ids = set(re.findall(r"\b([A-Za-z_][\w-]*):::decision\b", body))
    for m in re.finditer(r"^\s*class\s+([\w,\s-]+?)\s+decision\b", body, re.M):
        decision_ids |= {x.strip() for x in m.group(1).split(",")}
    nodes = {}
    if kind in ("flowchart", "graph"):
        for m in NODE.finditer(body):
            nid, opn, label = m.group(1), m.group(2), m.group(3)
            if nid in ("class", "classDef", "style", "click", "linkStyle", "subgraph", "end", "direction"):
                continue
            nodes.setdefault(nid, (opn, label))
    elif kind == "sequenceDiagram":
        for m in re.finditer(r"^\s*(?:participant|actor)\s+(\S+)(?:\s+as\s+(.+))?$", body, re.M):
            nodes.setdefault(m.group(1), ("[", m.group(2) or m.group(1)))

    if len(nodes) > MAX_NODES:
        out.append(("FAIL", "M6", f"{len(nodes)} nút > {MAX_NODES} — tách thành hai sơ đồ"))
    for nid, (opn, label) in nodes.items():
        lines = _lines(label)
        text = " ".join(lines)
        if opn == "{":
            out.append(("FAIL", "M2", f"{nid}{{{text[:30]}}} — hình thoi; dùng hộp bo góc + :::decision"))
        if (opn == "{" or nid in decision_ids) and not text.rstrip().endswith("?"):
            out.append(("FAIL", "M3", f"{nid} '{text[:40]}' — nút quyết định phải là câu hỏi kết thúc bằng '?'"))
        if len(lines) > MAX_LINES or any(len(x) > MAX_LINE_CHARS for x in lines):
            longest = max((len(x) for x in lines), default=0)
            out.append(("FAIL", "M4", f"{nid} '{text[:40]}…' — {len(lines)} dòng, dòng dài nhất {longest} ký tự "
                                      f"(tối đa {MAX_LINES} dòng × {MAX_LINE_CHARS})"))
        words = [w for w in re.findall(r"[^\W\d_]+", text) if len(w) > 1]
        if EMOJI.search(text) or (len(words) >= 3 and all(w.isupper() for w in words)):
            out.append(("FAIL", "M8", f"{nid} '{text[:40]}' — emoji hoặc VIẾT HOA toàn bộ"))

    if kind in ("flowchart", "graph"):
        for m in EDGE_LABEL.finditer(body):
            lab = (m.group(1) or m.group(2) or "").strip().strip('"')
            if lab and len(lab.split()) > MAX_EDGE_WORDS:
                out.append(("FAIL", "M5", f"nhãn mũi tên '{lab[:40]}' — {len(lab.split())} từ > {MAX_EDGE_WORDS}"))
        if re.search(r"==>|-\.->|-\.-", body):
            out.append(("WARN", "M9", "trộn nét đậm (==>) hoặc nét chấm (-.->) — mẫu chỉ dùng --> nét liền"))
    fills = {f.lower() for f in FILL.findall(body)}
    if len(fills) > MAX_FILLS:
        out.append(("FAIL", "M7", f"{len(fills)} màu nền ({', '.join(sorted(fills)[:5])}) — mẫu chỉ một tông"))
    return out


def blocks(path: Path) -> list:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".md":
        return [(text[:m.start()].count("\n") + 2, m.group(1)) for m in MD_BLOCK.finditer(text)]
    import html as h
    return [(text[:m.start()].count("\n") + 1, h.unescape(re.sub(r"<[^>]+>", "", m.group(2)))) for m in HTML_BLOCK.finditer(text)]


def targets(args: list) -> list:
    roots = [Path(a) for a in args] or [ROOT]
    files = []
    for r in roots:
        cand = [r] if r.is_file() else [*r.rglob("*.md"), *r.rglob("*.html")]
        base = r.resolve() if r.is_dir() else r.resolve().parent       # bỏ qua chỉ xét phần đường dẫn DƯỚI gốc được truyền vào
        files += [p for p in cand if not any(s in f"/{p.resolve().relative_to(base).as_posix()}/" for s in SKIP)]
    return sorted(set(files))


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    n_diag = n_fail = n_warn = 0
    for f in targets(args):
        for line, dsl in blocks(f):
            n_diag += 1
            rel = f.resolve().relative_to(ROOT) if f.resolve().is_relative_to(ROOT) else f
            for lvl, rule, msg in audit(dsl):
                n_fail += lvl == "FAIL"; n_warn += lvl == "WARN"
                print(f"  {'✗' if lvl == 'FAIL' else '⚠'} {rel}:{line} {rule} {msg}")
    print(f"mermaid-audit: {n_diag} sơ đồ · {n_fail} FAIL · {n_warn} WARN")
    return 2 if n_fail else 0


def _selftest():
    ok = 'flowchart TD\n  A["Người dùng giao nhiệm vụ"] --> B(["Còn trong giới hạn?"]):::decision\n  B -->|Có| A\n  B -->|Không| C["Dừng"]'
    assert audit(ok) == [], audit(ok)
    bad = audit('graph LR\n  A{Kiểm tra} -->|một hai ba bốn năm sáu| B["' + "x" * 41 + '"]\n  A ==> C\n'
                '  style A fill:#f00\n  style B fill:#0f0\n  style C fill:#00f')
    rules = {r for _, r, _ in bad}
    assert {"M1", "M2", "M3", "M4", "M5", "M7", "M9"} <= rules, rules
    assert audit('flowchart TD\n  A["M11 CLI"] --> B["LOG"]') == []
    assert {r for _, r, _ in audit('flowchart TD\n  A["CHẠY NGAY BÂY GIỜ"]')} == {"M8"}
    seq = audit("sequenceDiagram\n  participant A as Người viết\n  A->>B: ghi Tier")
    assert seq == [], seq
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        _selftest()
    else:
        sys.exit(main())
