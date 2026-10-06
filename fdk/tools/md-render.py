#!/usr/bin/env python3
"""md-render — Markdown → trang HTML cho NGƯỜI đọc, tất định, 0-token. Model chỉ viết .md; máy dựng phần còn lại.

Vì sao (06/10/2026, user: "gen HTML tốn token gấp 3 so với chỉ file md"): phần model tự viết trong một trang HTML
≈ bằng chính file md (viết nội dung HAI lần), cộng nạp skill docs-site-macos 109KB mỗi lần làm trang. Ở đây md là
nguồn duy nhất; vỏ trang (rail mục lục, sáng/tối, font, favicon, ribbon) do lớp nền html_base.apply gắn.

Cú pháp hỗ trợ: front matter YAML (lấy `title`), heading (có id để nhảy tới), đoạn văn, list lồng (- * + 1.),
bảng `| a | b |`, trích dẫn `>`, `---`, code fence, inline `code` **đậm** *nghiêng* [link](url) ![ảnh](url).
Hai khối đặc biệt:
  ```mermaid      → <div class="diagram-box" data-mermaid> (mermaid-audit.py + R7 đọc được mã gốc; engine vẽ nhúng
                     khi trang có sơ đồ). ```archify  <file.html> [tiêu đề] → <iframe class="archify-embed"> — CHỈ trỏ
                     tới artifact archify, không chép, không sửa nó.
  Đoạn văn NGAY SAU mỗi sơ đồ nhận class="desc" (lời giải thích đi kèm sơ đồ — R7 (e)).
HTML thô trong md bị escape (md là dữ liệu, không phải markup tin được).

Usage: md-render.py <in.md> [-o out.html] [--title "…"]     → in `→ <out>`; mặc định out = cạnh file md, đuôi .html
"""
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = [HERE.parents[1] / "skills/docs-site-macos/vendor/beautiful-mermaid.min.js.gz.b64",
          Path.home() / ".claude/skills/docs-site-macos/vendor/beautiful-mermaid.min.js.gz.b64"]

CSS = """main{max-width:var(--measure,72ch);margin:0 auto;padding:var(--sp-6,32px) var(--sp-4,16px) var(--sp-8,64px);overflow-wrap:break-word}
main :not(pre)>code{overflow-wrap:anywhere}
main table{border-collapse:collapse;width:100%;margin:0 0 var(--sp-4,16px);font-size:.875rem;font-variant-numeric:tabular-nums}
main :is(h1,h2,h3,h4,section){scroll-margin-top:72px}
main th,main td{border:1px solid var(--ovs-border);padding:6px 10px;text-align:left;vertical-align:top}
main th{background:var(--ovs-surface2)}
.tbl{overflow-x:auto}
main pre{overflow-x:auto;padding:var(--sp-3,12px);border:1px solid var(--ovs-border);border-radius:8px;background:var(--ovs-surface2)}
main blockquote{margin:0 0 var(--sp-4,16px);padding-left:var(--sp-4,16px);border-left:3px solid var(--ovs-border);color:var(--ovs-ink2)}
main img{max-width:100%}
.archify-embed{width:100%;height:clamp(640px,85vh,1100px);border:1px solid var(--ovs-border);border-radius:12px;background:var(--ovs-surface)}
main .diagram-box{box-sizing:border-box;border:1px solid var(--ovs-border);border-radius:12px;padding:var(--sp-3,12px);overflow:auto;width:min(1200px,calc(100vw - 48px));max-width:none;margin:0 0 var(--sp-3,12px) calc(50% - min(600px,50vw - 24px))}  /* sơ đồ thoát cột chữ: Mermaid sinh SVG 1100–1700px, nhét vào 72ch là chữ trong nút còn 30% */
.mm-out{display:block;text-align:center}
:root{--mm-bg:transparent;--mm-fg:var(--ovs-ink);--mm-line:var(--ovs-ink2);--mm-accent:var(--ovs-accent);--mm-muted:var(--ovs-ink2);--mm-surface:var(--ovs-surface);--mm-border:var(--ovs-border)}"""

MERMAID_JS = """window.__bmReady=(typeof DecompressionStream==='undefined')?Promise.reject(new Error('no DecompressionStream')):(async function(){
var b=atob(__BM_GZ_B64),u=new Uint8Array(b.length);for(var i=0;i<b.length;i++)u[i]=b.charCodeAt(i);
(0,eval)(await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('gzip'))).text())})();
(async function(){var v=function(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()};
for(const box of document.querySelectorAll('.diagram-box[data-mermaid]')){var out=box.querySelector('.mm-out'),src=box.querySelector('.mermaid-src');
try{await window.__bmReady;var svg=BeautifulMermaid.renderMermaidSVG(src.textContent,{bg:v('--mm-bg'),fg:v('--mm-fg'),accent:v('--mm-accent'),line:v('--mm-line'),muted:v('--mm-muted'),surface:v('--mm-surface'),border:v('--mm-border')});
out.innerHTML=svg.replace(/@import url\\('https:\\/\\/fonts\\.googleapis\\.com[^;]+;/g,'');
var el=out.querySelector('svg'),vb=el&&el.viewBox&&el.viewBox.baseVal;if(vb&&vb.width){el.removeAttribute('width');el.removeAttribute('height');el.style.width=Math.max(vb.width*0.7,Math.min(vb.width,out.clientWidth))+'px';el.style.height='auto'}}catch(e){src.hidden=false}}})();"""


def slug(t, seen):
    s = re.sub(r"[^\w\s-]", "", t.lower(), flags=re.U).strip()
    s = re.sub(r"[\s_]+", "-", s) or "muc"
    base, n = s, 2
    while s in seen:
        s = f"{base}-{n}"; n += 1
    seen.add(s)
    return s


def inline(t):
    t = html.escape(t, quote=False)
    codes = []
    t = re.sub(r"`([^`]+)`", lambda m: codes.append(m.group(1)) or f"\x00{len(codes) - 1}\x00", t)
    t = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", lambda m: f'<img alt="{m.group(1)}" src="{html.escape(m.group(2))}">', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>', t)
    t = re.sub(r"&lt;(https?://[^\s&]+)&gt;", r'<a href="\1">\1</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)", r"<em>\1</em>", t)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", t)


LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")


def render_list(lines):
    """lines: [(indent, ordered, text)] → HTML list lồng theo thụt lề."""
    out, stack = [], []
    for ind, ordered, text in lines:
        while stack and ind < stack[-1][0]:
            out.append(f"</li></{stack.pop()[1]}>")
        if not stack or ind > stack[-1][0]:
            tag = "ol" if ordered else "ul"
            stack.append((ind, tag)); out.append(f"<{tag}><li>")
        else:
            out.append("</li><li>")
        out.append(inline(text))
    while stack:
        out.append(f"</li></{stack.pop()[1]}>")
    return "".join(out)


def render(md, title=None):
    meta = {}
    m = re.match(r"^---\n(.*?)\n---\n", md, re.S)
    if m:
        for ln in m.group(1).splitlines():
            k, _, v = ln.partition(":")
            meta[k.strip()] = v.strip().strip('"\'')
        md = md[m.end():]
    lines, i, body, toc, seen = md.split("\n"), 0, [], [], set()
    want_desc, has_mermaid = False, False

    def para(text):
        nonlocal want_desc
        cls = ' class="desc"' if want_desc else ""
        want_desc = False
        body.append(f"<p{cls}>{inline(text)}</p>")

    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        fm = re.match(r"^\s*(```|~~~)\s*([\w-]*)\s*(.*)$", ln)
        if fm:
            fence, lang, rest = fm.groups(); buf = []; i += 1
            while i < len(lines) and not lines[i].strip().startswith(fence):
                buf.append(lines[i]); i += 1
            i += 1
            src = "\n".join(buf)
            if lang == "mermaid":
                has_mermaid = want_desc = True
                body.append(f'<div class="diagram-box" data-mermaid><pre class="mermaid-src" hidden>{html.escape(src, quote=False)}</pre><div class="mm-out"></div></div>')
            elif lang == "archify":
                parts = (src.strip() or rest).split(None, 1)
                if parts:
                    want_desc = True
                    t = html.escape(parts[1] if len(parts) > 1 else "Sơ đồ")
                    u = html.escape(parts[0])
                    body.append(f'<iframe class="archify-embed" src="{u}" title="{t}" loading="lazy"></iframe>'
                                f'<p><a href="{u}" target="_blank" rel="noopener">Mở sơ đồ riêng ↗</a></p>')
            else:
                cls = ' class="language-%s"' % lang if lang else ""
                body.append(f"<pre><code{cls}>{html.escape(src, quote=False)}</code></pre>")
            continue
        h = re.match(r"^(#{1,6})\s+(.*?)\s*#*$", ln)
        if h:
            n, text = len(h.group(1)), h.group(2)
            if n == 1 and not title:
                title = re.sub(r"[*_`]", "", text)
            sid = slug(re.sub(r"[*_`]", "", text), seen)
            if n == 2:                                        # mỗi mục ## = một <section> (rail mục lục + mind map của lớp nền bám vào đây)
                toc.append((sid, re.sub(r"[*_`]", "", text)))
                body.append(("</section>" if toc[:-1] else "") + f'<section id="{sid}"><h2>{inline(text)}</h2>'); i += 1; continue
            body.append(f'<h{n} id="{sid}">{inline(text)}</h{n}>'); i += 1; continue
        if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", ln):
            body.append("<hr>"); i += 1; continue
        if ln.lstrip().startswith(">"):
            buf = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            body.append(f"<blockquote><p>{inline(' '.join(buf))}</p></blockquote>"); continue
        if ln.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            head = cells(ln); i += 2; rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(cells(lines[i])); i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            tr = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            body.append(f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'); continue
        if LIST_RE.match(ln):
            items = []
            while i < len(lines) and lines[i].strip():
                lm = LIST_RE.match(lines[i])
                if lm:
                    items.append((len(lm.group(1).expandtabs(4)), lm.group(2)[0].isdigit(), lm.group(3)))
                elif items:                                  # dòng nối của mục trước
                    ind, o, t = items[-1]; items[-1] = (ind, o, t + " " + lines[i].strip())
                i += 1
            body.append(render_list(items)); continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6}\s|\s*(```|~~~)|\s*>|\s*\|)", lines[i]) and not LIST_RE.match(lines[i]):
            buf.append(lines[i].strip()); i += 1
        para(" ".join(buf))

    if toc:
        body.append("</section>")
    title = meta.get("title") or title or "Tài liệu"
    nav = ""
    if len(toc) >= 4:                                         # đủ mục → nav .logo + neo; lớp nền đổi thành rail mục lục
        nav = (f'<nav><div class="logo">{html.escape(title)}</div>'
               + "".join(f'<a href="#{sid}">{html.escape(t)}</a>' for sid, t in toc) + "</nav>")
    head = (f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f"<title>{html.escape(title)}</title>"
            + (f'<meta name="description" content="{html.escape(meta["description"])}">' if meta.get("description") else "")
            + f"<style>{CSS}</style></head>")
    return head, nav, "\n".join(body), has_mermaid


def build(src: Path, out: Path, title=None) -> str:
    head, nav, body, has_mermaid = render(src.read_text(encoding="utf-8"), title)
    foot = (f'<footer><p>Sinh từ <code>{html.escape(str(src.resolve()))}</code> bởi <code>md-render.py</code> — sửa file md rồi render lại, '
            f'đừng sửa trang này · <code>{html.escape(str(out.resolve()))}</code></p></footer>')
    js = ""
    if has_mermaid:
        blob = next((p for p in VENDOR if p.is_file()), None)
        js = (f'<script>var __BM_GZ_B64="{blob.read_text().strip()}";{MERMAID_JS}</script>' if blob
              else "<script>document.querySelectorAll('.mermaid-src').forEach(function(p){p.hidden=false})</script>")
    page = f"{head}<body>{nav}<main id=\"main\">{body}{foot}</main>{js}</body></html>"
    sys.path.insert(0, str(HERE))
    try:
        import html_base
        page = html_base.apply(page)
    except Exception as e:                                    # thiếu lớp nền → trang vẫn đọc được, báo rõ
        print(f"⚠ không gắn được lớp nền html_base ({e}) — trang thiếu rail/toggle/font", file=sys.stderr)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return str(out)


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__); return 2
    src = Path(argv[0])
    if not src.is_file():
        print(f"✗ không thấy {src}"); return 1
    out = Path(argv[argv.index("-o") + 1]) if "-o" in argv else src.with_suffix(".html")
    title = argv[argv.index("--title") + 1] if "--title" in argv else None
    print(f"→ {build(src, out, title)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
