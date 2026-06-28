#!/usr/bin/env python3
"""docs-curate — sắp xếp gọn kho tài liệu LOCAL (llmwiki/html/*.html + sources/draft/*.md) đang
phình to, BẰNG CODE (tất định). Triết lý 3 tầng (không chỉ "merge"):

  KEEP     canonical/active — overstack.html, index.html, cheatsheet, health-dashboard, docs mới.
  ARCHIVE  render ephemeral — cặp proposal đã xong (draft+seq), bản bị thay thế (vN cũ,
           master-wiki←overstack), report cũ → dời vào archive/ (GIỮ, không xoá).
  PROMOTE  bản chất quý → wiki — draft đứng-một-mình (không có seq) thường chứa phân tích/quyết
           định nên LÊN wiki ADR/concept (travel + sống sót clone). Tool chỉ ĐỀ XUẤT; agent (skill
           /docs-curate) đọc nội dung rồi promote bằng phán đoán — KHÔNG auto-promote.

Vì sao bằng code: phân loại + dời + re-index là tất định; phần cần đọc-hiểu (promote cái gì,
merge ra sao) để cho agent. Đây là backbone; skill là tay lái.

Subcommands:
  plan                 (mặc định) in BẢNG phân loại + kế hoạch + gợi ý promote — KHÔNG đụng file.
  apply [--keep-dates N]  dời nhóm ARCHIVE vào archive/, rồi reindex. N = số mốc-ngày gần nhất giữ active (mặc 2).
  reindex              chỉ chạy lại build-docs-index + index_sync --fix + ghi log.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "llmwiki" / "html"
DRAFT = ROOT / "llmwiki" / "wiki" / "sources" / "draft"
HTML_ARC = HTML / "archive"
DRAFT_ARC = DRAFT / "archive"

# canonical/active — không bao giờ archive (khớp theo substring)
CANONICAL = ("overstack.html", "index.html", "skills-cheatsheet", "health-dashboard")
# bản bị thay thế tường minh (file → bản thay thế nó)
SUPERSEDED = {"280626-framework-master-wiki.html": "overstack.html"}
SKIP_DRAFT = ("README.md", "_template.md")


def _date_key(name: str):
    """DDMMYY ở đầu tên → khoá sắp xếp yymmdd (mới = lớn); None nếu không có."""
    m = re.match(r"(\d{2})(\d{2})(\d{2})-", name)
    if not m:
        return None
    dd, mm, yy = m.groups()
    return int(yy) * 10000 + int(mm) * 100 + int(dd)


def _is_canonical(name: str) -> bool:
    return any(c in name for c in CANONICAL)


def classify():
    htmls = sorted(p.name for p in HTML.glob("*.html"))
    drafts = sorted(p.name for p in DRAFT.glob("*.md") if p.name not in SKIP_DRAFT)
    draft_stems = {d[:-3] for d in drafts}

    # vN superseded: gom theo base, archive mọi vN < max
    vmax = {}
    for h in htmls:
        m = re.match(r"(.*)-v(\d+)\.html$", h)
        if m:
            base, v = m.group(1), int(m.group(2))
            vmax[base] = max(vmax.get(base, 0), v)

    out = {}  # name -> (kind, action, reason)
    for h in htmls:
        if _is_canonical(h):
            out[h] = ("html", "keep", "canonical/active")
            continue
        if h in SUPERSEDED:
            out[h] = ("html", "archive", "bị thay thế bởi " + SUPERSEDED[h])
            continue
        mv = re.match(r"(.*)-v(\d+)\.html$", h)
        if mv and int(mv.group(2)) < vmax.get(mv.group(1), 0):
            out[h] = ("html", "archive", f"bản cũ (có -v{vmax[mv.group(1)]})")
            continue
        ms = re.match(r"(.*)-seq\.html$", h)
        if ms:
            base = ms.group(1)
            if base in draft_stems:
                out[h] = ("html", "archive", f"cặp proposal với {base}.md (đã xong)")
            else:
                out[h] = ("html", "archive", "seq orphan (không còn draft)")
            continue
        out[h] = ("html", "report", "report/doc một-lần")

    for d in drafts:
        stem = d[:-3]
        if (HTML / f"{stem}-seq.html").is_file():
            out[d] = ("draft", "archive", "cặp proposal (đã xong; promote bản chất trước)")
        else:
            out[d] = ("draft", "promote?", "draft đứng-một-mình → cân nhắc LÊN wiki ADR/concept")
    return out


def _resolve_reports(out, keep_dates):
    """report/promote? có ngày: giữ active nếu thuộc N mốc-ngày gần nhất; cũ hơn → archive."""
    dated = {n: _date_key(n) for n, (_k, a, _r) in out.items() if a in ("report", "promote?") and _date_key(n)}
    if not dated:
        return
    recent = sorted(set(dated.values()), reverse=True)[:max(1, keep_dates)]
    for n, dk in dated.items():
        kind, action, reason = out[n]
        if dk in recent:
            out[n] = (kind, "keep" if action == "report" else "promote?", reason + " (gần đây — giữ active)")
        else:
            out[n] = (kind, "archive", reason + " (cũ → archive)")
    for n, (kind, action, reason) in list(out.items()):   # report không-ngày → giữ active
        if action == "report":
            out[n] = (kind, "keep", reason)


def cmd_plan(keep_dates=2):
    out = classify()
    _resolve_reports(out, keep_dates)
    order = ["keep", "archive", "promote?", "report"]
    label = {"keep": "✅ GIỮ (canonical/active)", "archive": "📦 ARCHIVE (dời vào archive/)",
             "promote?": "⬆️  PROMOTE? (cân nhắc lên wiki — agent đọc rồi quyết)",
             "report": "• report"}
    print(f"docs-curate · plan — {len([1 for v in out.values()])} mục "
          f"(html {sum(1 for k,(t,*_ ) in out.items() if t=='html')} · draft {sum(1 for k,(t,*_ ) in out.items() if t=='draft')})\n")
    for act in order:
        rows = sorted((n, r) for n, (_t, a, r) in out.items() if a == act)
        if not rows:
            continue
        print(f"{label.get(act, act)}  ({len(rows)})")
        for n, r in rows:
            print(f"    {n:<46} {r}")
        print()
    nkeep = sum(1 for v in out.values() if v[1] == "keep")
    narc = sum(1 for v in out.values() if v[1] == "archive")
    nprom = sum(1 for v in out.values() if v[1] == "promote?")
    print(f"→ keep {nkeep} · archive {narc} · promote-suggest {nprom}.  Chạy: docs-curate.py apply")
    print("  PROMOTE là phán đoán của agent (đọc draft → viết ADR/concept), tool không tự làm.")
    return out


def _ensure_gitignore():
    """archive/ phải GIỮ local-only (html/draft vốn gitignored top-level; subfolder thoát pattern
    → phải ignore tường minh, kẻo file local bị track/push)."""
    gi = ROOT / ".gitignore"
    want = ["llmwiki/html/archive/", "llmwiki/wiki/sources/draft/archive/"]
    try:
        txt = gi.read_text(encoding="utf-8") if gi.is_file() else ""
        add = [w for w in want if w not in txt]
        if add:
            gi.write_text(txt.rstrip("\n") + "\n" + "\n".join(add) + "\n", encoding="utf-8")
            print("  ✓ .gitignore: thêm archive/ (giữ local-only)")
    except Exception:
        pass


def cmd_apply(keep_dates=2):
    out = classify()
    _resolve_reports(out, keep_dates)
    _ensure_gitignore()
    HTML_ARC.mkdir(parents=True, exist_ok=True)
    DRAFT_ARC.mkdir(parents=True, exist_ok=True)
    moved = 0
    for n, (kind, action, _r) in sorted(out.items()):
        if action != "archive":
            continue
        src = (HTML if kind == "html" else DRAFT) / n
        dst = (HTML_ARC if kind == "html" else DRAFT_ARC) / n
        if src.is_file():
            src.replace(dst)
            moved += 1
            print(f"  📦 {kind}/{n} → archive/")
    print(f"docs-curate · apply — dời {moved} file vào archive/. Re-index…")
    cmd_reindex()
    return moved


def cmd_reindex():
    # 1) dashboard html
    r = subprocess.run([sys.executable, str(ROOT / "fdk" / "tools" / "build-docs-index.py")],
                       capture_output=True, text=True)
    print("  " + (r.stdout or r.stderr or "").strip().splitlines()[-1] if (r.stdout or r.stderr) else "  docs-index ok")
    # 2) wiki index (R3) — archive/ là draft gitignored, index_sync git-aware bỏ qua
    subprocess.run([sys.executable, str(ROOT / "harness" / "validators" / "index_sync.py"),
                    "--wiki-dir", str(ROOT / "llmwiki" / "wiki"), "--fix"], capture_output=True, text=True)
    print("  ✓ build-docs-index + index_sync --fix")


def main():
    args = sys.argv[1:]
    keep = 2
    if "--keep-dates" in args:
        keep = int(args[args.index("--keep-dates") + 1])
    cmd = args[0] if args and not args[0].startswith("-") else "plan"
    if cmd == "apply":
        cmd_apply(keep)
    elif cmd == "reindex":
        cmd_reindex()
    else:
        cmd_plan(keep)


if __name__ == "__main__":
    main()
