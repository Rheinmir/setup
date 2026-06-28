#!/usr/bin/env python3
"""build-overstack-docs — sinh TÀI LIỆU USER cho framework **overstack** thành MỘT file HTML
self-contained (glass docs-site-macos), luôn-mới.

Vì sao bằng code: số skill/rule và bảng tham chiếu phải khớp đĩa, không drift. Prose (giải
thích từng phần) là chuỗi tay trong file này; bảng skill/rule + số đếm thì PULL LIVE từ đĩa.

Travel: trang sinh ra ở llmwiki/html/overstack.html — được un-gitignore + nằm trong template
manifest + install-harness copy xuống dự án downstream, nên user nào cài overstack cũng có docs.

CLI:
  build-overstack-docs.py            # ghi llmwiki/html/overstack.html từ đĩa
  build-overstack-docs.py --check    # exit 2 nếu file cũ so với bản sinh (giữ docs luôn-mới)
"""
import re
import sys
from pathlib import Path


def detect_root() -> Path:
    repo = Path(__file__).resolve().parents[2]
    if (repo / "llmwiki").is_dir():
        return repo
    return Path.cwd()


ROOT = detect_root()
OUT = ROOT / "llmwiki" / "html" / "overstack.html"

# ── live data (đếm từ đĩa) ────────────────────────────────────────────────────────────────
def _fm_desc(p: Path) -> str:
    try:
        t = p.read_text(encoding="utf-8")
    except Exception:
        return ""
    m = re.match(r"^---\n(.*?)\n---", t, re.S)
    if not m:
        return ""
    dm = re.search(r"^description:\s*(.*)$", m.group(1), re.M)
    val = (dm.group(1).strip().strip('"').strip("'")) if dm else ""
    return re.split(r"(?<=[.!?。])\s|—| - |\. |\. ", val, 1)[0].strip()


def load_loops(root: Path) -> dict:
    try:
        t = (root / "harness" / "scripts" / "sync-skills.py").read_text(encoding="utf-8")
        m = re.search(r"LOOP_MAP\s*=\s*\{(.*?)\}", t, re.S)
        return dict(re.findall(r'"([a-z0-9-]+)"\s*:\s*"([a-z-]+)"', m.group(1))) if m else {}
    except Exception:
        return {}


def skills_by_loop(root: Path):
    loops = load_loops(root)
    sk_dir = root / "skills"
    if not (sk_dir.is_dir() and any(sk_dir.glob("*/SKILL.md"))):
        sk_dir = Path.home() / ".claude" / "skills"
    by = {}
    n = 0
    for d in sorted(sk_dir.glob("*/")):
        sk = d / "SKILL.md"
        if not sk.is_file():
            continue
        n += 1
        loop = loops.get(d.name, "utils")
        by.setdefault(loop, []).append((d.name, _fm_desc(sk)))
    return by, n


def rules(root: Path):
    pol = next((p for p in (root / "harness" / "poc-vendor-neutral" / "policy.yaml",
                            root / "harness" / "policy.yaml") if p.is_file()), None)
    if not pol:
        return []
    out = []
    for rid, name in re.findall(r"id:\s*(R\d+).*?name:\s*([^\n]+)", pol.read_text(encoding="utf-8"), re.S):
        out.append((rid, name.strip().strip('"')))
    return sorted(set(out), key=lambda r: int(r[0][1:]))


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── style + script (glass docs-site-macos, đã chứng minh ở master-wiki) ───────────────────
ACCENTS = [("#0a84ff", "10,132,255"), ("#30b0c7", "48,176,199"), ("#5856d6", "88,86,214"),
           ("#28a745", "52,199,89"), ("#f08c00", "255,149,0"), ("#e0264b", "255,45,85")]

CSS_BASE = r"""
:root{--font:-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',Roboto,sans-serif;
--mono:'SF Mono',ui-monospace,Menlo,monospace;--glass2:rgba(255,255,255,.7);--glass3:rgba(255,255,255,.88);
--edge:inset 0 1px 0 rgba(255,255,255,.85);--border:rgba(30,90,170,.14);--t1:#0f0f12;--t2:#4a4a55;}
*{box-sizing:border-box}html{background:#e9f0fb;scrollbar-width:thin;scrollbar-color:transparent transparent}
html.scrolling{scrollbar-color:rgba(10,132,255,.32) transparent}
body{margin:0;padding-left:232px;font-family:var(--font);color:var(--t1);line-height:1.62;background:radial-gradient(900px 500px at 12% -10%,rgba(10,132,255,.1),transparent 60%),radial-gradient(700px 420px at 95% 12%,rgba(88,86,214,.08),transparent 55%),linear-gradient(180deg,#f7fbff,#eaf2fd);transition:padding-left .28s}
body::before{content:'';position:fixed;inset:-10%;z-index:-1;pointer-events:none;background:radial-gradient(640px 440px at 10% 14%,rgba(10,132,255,.2),transparent 65%),radial-gradient(380px 460px at 4% 52%,rgba(48,176,199,.16),transparent 65%),radial-gradient(540px 400px at 88% 10%,rgba(88,86,214,.12),transparent 60%),radial-gradient(480px 380px at 16% 86%,rgba(52,199,89,.1),transparent 60%);animation:orb 46s ease-in-out infinite alternate}
@keyframes orb{100%{transform:translate(2%,1.5%) scale(1.04)}}
body::after{content:'';position:fixed;inset:0;z-index:-1;pointer-events:none;background-image:radial-gradient(rgba(30,90,170,.1) 1px,transparent 1.3px);background-size:22px 22px;mask-image:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,.22))}
@media(prefers-reduced-motion:reduce){body::before{animation:none}}
::-webkit-scrollbar{width:11px;height:11px;background:transparent}::-webkit-scrollbar-thumb{background:transparent;border-radius:8px;border:3px solid transparent;background-clip:content-box;transition:background-color .25s}html.scrolling::-webkit-scrollbar-thumb,::-webkit-scrollbar-thumb:hover{background-color:rgba(10,132,255,.32)}
nav{position:fixed;top:0;left:0;bottom:0;width:232px;z-index:100;overflow-y:auto;display:flex;flex-direction:column;gap:1px;padding:18px 12px;background:linear-gradient(165deg,rgba(255,255,255,.46),rgba(255,255,255,.22) 48%,rgba(240,248,255,.34));backdrop-filter:blur(24px) saturate(1.7);-webkit-backdrop-filter:blur(24px) saturate(1.7);border-right:1px solid rgba(255,255,255,.55);box-shadow:inset 0 1px 0 rgba(255,255,255,.9),4px 0 24px rgba(30,90,170,.08);transition:transform .28s}
nav::before{content:'';position:absolute;inset:0;pointer-events:none;background:radial-gradient(220px 160px at 18% 4%,rgba(255,255,255,.55),transparent 70%)}nav>*{position:relative}
nav .logo{margin:0 0 8px;padding:6px 10px;font-weight:800;font-size:17px;letter-spacing:-.03em;background:linear-gradient(135deg,#0a84ff,#5856d6);-webkit-background-clip:text;background-clip:text;color:transparent}
nav .logo small{display:block;font-size:10px;font-weight:600;color:var(--t2);-webkit-text-fill-color:var(--t2);letter-spacing:0}
nav a{padding:5.5px 12px;border-radius:9px;font-size:12.5px;color:var(--t2);text-decoration:none;transition:background .15s,color .15s}nav a:hover{background:rgba(10,132,255,.06);color:#0a84ff}nav a.active{color:#0a84ff;background:rgba(10,132,255,.08);font-weight:600}
nav .grp{font-size:10px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:#9aa4b2;margin:12px 12px 2px}
.nav-close{position:absolute;top:10px;right:10px;width:26px;height:26px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:12px;color:var(--t2);cursor:pointer;background:rgba(0,0,0,.05);border:none}.nav-close:hover{color:#0a84ff;background:rgba(10,132,255,.1)}
.nav-toggle{position:fixed;top:12px;left:12px;z-index:120;width:32px;height:32px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:14px;color:var(--t2);cursor:pointer;background:linear-gradient(165deg,rgba(255,255,255,.5),rgba(255,255,255,.24));backdrop-filter:blur(24px) saturate(1.7);-webkit-backdrop-filter:blur(24px) saturate(1.7);border:1px solid transparent;box-shadow:inset 0 1px 0 rgba(255,255,255,.75),0 0 0 1px rgba(30,90,170,.08),0 2px 10px rgba(30,90,170,.12);transition:opacity .2s}body:not(.nav-collapsed) .nav-toggle{opacity:0;pointer-events:none}body.nav-collapsed nav{transform:translateX(-100%)}body.nav-collapsed{padding-left:0}@media(max-width:640px){body{padding-left:0}}
.hero{max-width:1080px;margin:0 auto;padding:74px 24px 8px}.hero .eyebrow{display:inline-block;font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:#5856d6;background:rgba(88,86,214,.1);padding:4px 12px;border-radius:999px;margin-bottom:14px}
.hero h1{font-size:clamp(30px,4.6vw,50px);line-height:1.06;letter-spacing:-.03em;margin:0 0 12px;background:linear-gradient(135deg,#0a84ff,#5856d6,#cfe3fb);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{font-size:16px;color:var(--t2);max-width:780px;margin:0}
section{position:relative}.sec::before{content:'';position:absolute;top:0;bottom:0;left:50%;width:100vw;transform:translateX(-50%);pointer-events:none}
.inner{position:relative;max-width:1080px;margin:0 auto;padding:40px 24px 44px}
.tag{display:inline-block;font-size:12px;font-weight:700;padding:4px 12px;border-radius:999px;margin-bottom:10px}
h2{font-size:25px;letter-spacing:-.02em;color:#1d1d1f;margin:0 0 6px}.lead{font-size:15px;color:var(--t2);max-width:840px;margin:0 0 8px}
h3{font-size:15.5px;margin:20px 0 6px;color:#1d1d1f}
p{margin:10px 0;max-width:860px;font-size:14.5px}
.card{background:var(--glass2);backdrop-filter:blur(8px) saturate(1.1);-webkit-backdrop-filter:blur(8px) saturate(1.1);border:1px solid var(--border);border-radius:16px;box-shadow:var(--edge),0 4px 20px rgba(0,0,0,.06);padding:18px 20px;margin-top:14px}
.card h4{margin:0 0 9px;font-size:14px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}.grid3{grid-template-columns:1fr 1fr 1fr}@media(max-width:780px){.grid,.grid3{grid-template-columns:1fr}}
code{font-family:var(--mono);font-size:.85em;background:rgba(10,132,255,.08);padding:1px 5px;border-radius:5px;color:#0a5ec7}
pre{background:rgba(13,24,40,.92);color:#e6edf6;border-radius:12px;padding:14px 16px;overflow:auto;font-family:var(--mono);font-size:12.5px;line-height:1.55;margin:12px 0;box-shadow:var(--edge),0 4px 20px rgba(0,0,0,.12)}pre code{background:none;color:inherit;padding:0}
ul.s{list-style:none;margin:10px 0 0;padding:0;display:flex;flex-direction:column;gap:6px}ul.s li{position:relative;padding-left:18px;font-size:13.5px;color:var(--t2)}ul.s li::before{content:'›';position:absolute;left:2px;font-weight:700;color:#5856d6}
ul.s li b{color:var(--t1)}
.kpi{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}.kpi .b{flex:1;min-width:92px;background:var(--glass2);backdrop-filter:blur(8px);border:1px solid var(--border);border-radius:14px;box-shadow:var(--edge),0 4px 18px rgba(0,0,0,.05);padding:13px 15px}
.kpi .n{font-size:25px;font-weight:800;letter-spacing:-.02em;line-height:1}.kpi .l{font-size:11px;color:var(--t2);margin-top:4px}
.chip{display:inline-block;font-size:11.5px;font-weight:600;font-family:var(--mono);background:rgba(10,132,255,.08);color:#0a5ec7;padding:2px 8px;border-radius:6px;margin:3px 4px 0 0}
ol.ck{margin:12px 0 0;padding-left:20px}ol.ck li{font-size:13.5px;color:var(--t2);margin:6px 0}ol.ck li b{color:var(--t1)}
table{width:100%;border-collapse:collapse;margin:14px 0;background:var(--glass3);backdrop-filter:blur(4px);border:1px solid var(--border);border-radius:12px;overflow:hidden;font-size:13px;box-shadow:var(--edge),0 4px 18px rgba(0,0,0,.05)}
th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--border);vertical-align:top}th{font-size:11px;text-transform:uppercase;letter-spacing:.03em;color:var(--t2);background:rgba(10,132,255,.05)}tr:last-child td{border-bottom:none}td code{white-space:nowrap}
.note{background:rgba(255,149,0,.08);border:1px solid rgba(255,149,0,.25);border-radius:14px;padding:16px 18px;margin-top:14px}
.note h4{margin:0 0 8px;color:#b46a00}
footer{max-width:1080px;margin:0 auto;padding:26px 24px 60px;font-size:12px;color:var(--t2);border-top:1px solid var(--border)}
.mindmap{display:flex;gap:20px;align-items:center;padding:14px 2px;overflow-x:auto}
.mm-root{flex-shrink:0;position:relative;padding:15px 20px;border-radius:16px;background:linear-gradient(135deg,#0a84ff,#5856d6);color:#fff;font-weight:800;font-size:17px;letter-spacing:-.02em;text-align:center;box-shadow:var(--edge),0 6px 22px rgba(10,132,255,.28)}
.mm-root small{display:block;font-size:10px;font-weight:600;opacity:.88;margin-top:3px}
.mm-root::after{content:'';position:absolute;right:-20px;top:50%;width:20px;height:2px;background:var(--border)}
.mm-tree{display:flex;flex-direction:column;gap:10px;position:relative;padding-left:22px}
.mm-tree::before{content:'';position:absolute;left:0;top:18px;bottom:18px;width:2px;background:var(--border);border-radius:2px}
.mm-branch{position:relative;display:flex;align-items:flex-start;gap:12px}
.mm-branch::before{content:'';position:absolute;left:-22px;top:16px;width:22px;height:2px;background:var(--c,#9aa4b2);border-radius:2px}
.mm-trunk{flex-shrink:0;display:flex;align-items:center;gap:8px;padding:7px 12px;border-radius:11px;background:var(--glass2);color:var(--c);font-weight:700;font-size:12.5px;border:1px solid var(--c);min-width:110px;box-shadow:var(--edge);backdrop-filter:blur(8px)}
.mm-trunk b{margin-left:auto;font-size:10px;background:var(--c);color:#fff;border-radius:6px;padding:1px 7px;font-weight:800}
.mm-leaves{display:flex;flex-wrap:wrap;gap:5px;align-content:flex-start;padding-top:5px;max-width:640px}
.mm-leaf{font-family:var(--mono);font-size:11px;padding:3px 8px;border-radius:7px;background:var(--glass3);border:1px solid var(--border);color:#0a5ec7;cursor:default;transition:border-color .15s,transform .1s}
.mm-leaf:hover{border-color:var(--c,#0a84ff);transform:translateY(-1px)}
@media(max-width:640px){.mindmap{flex-direction:column;align-items:stretch}.mm-root::after{display:none}.mm-leaves{max-width:none}}
"""

JS = r"""
(function(){const n=document.querySelector('nav');if(!n)return;const o=document.createElement('button');o.className='nav-toggle';o.textContent='☰';document.body.appendChild(o);const c=document.createElement('button');c.className='nav-close';c.textContent='✕';n.appendChild(c);o.onclick=function(){document.body.classList.remove('nav-collapsed')};c.onclick=function(){document.body.classList.add('nav-collapsed')};if(matchMedia('(max-width:640px)').matches)document.body.classList.add('nav-collapsed')})();
(function(){var ls=[].slice.call(document.querySelectorAll('nav a')),ss=[].slice.call(document.querySelectorAll('section[id]'));var ob=new IntersectionObserver(function(es){var a='';es.forEach(function(e){if(e.isIntersecting)a=e.target.id});if(a)ls.forEach(function(l){l.classList.toggle('active',l.getAttribute('href')==='#'+a)})},{rootMargin:'-40% 0px -55% 0px'});ss.forEach(function(s){ob.observe(s)})})();
(function(){var t;addEventListener('scroll',function(){document.documentElement.classList.add('scrolling');clearTimeout(t);t=setTimeout(function(){document.documentElement.classList.remove('scrolling')},900)},{passive:true})})();
"""


def accent_css(n: int) -> str:
    out = []
    for i in range(n):
        hexc, rgb = ACCENTS[i % len(ACCENTS)]
        out.append(f"#s{i} .tag{{background:rgba({rgb},.12);color:{hexc}}}"
                   f"#s{i} .card h4{{color:{hexc}}}#s{i} .card li::before{{color:{hexc}}}"
                   f".s{i}::before{{background:linear-gradient(180deg,rgba({rgb},.05),transparent 55%)}}")
    return "\n".join(out)


# ── sections (prose tay; bảng live tiêm vào) ──────────────────────────────────────────────
def sections(root: Path):
    by_loop, n_sk = skills_by_loop(root)
    rs = rules(root)
    n_rules = len(rs)
    n_scripts = len(list((root / "harness" / "scripts").glob("*.py"))) if (root / "harness" / "scripts").is_dir() else 0

    loop_order = ["wiki-loop", "dev-loop", "orchestrate", "utils"]
    skill_rows = []
    for loop in loop_order + [l for l in by_loop if l not in loop_order]:
        for name, desc in sorted(by_loop.get(loop, [])):
            skill_rows.append(f"<tr><td><code>/{esc(name)}</code></td><td>{esc(loop)}</td><td>{esc(desc)}</td></tr>")
    skills_table = ("<table><tr><th>Skill</th><th>Loop</th><th>Dùng khi</th></tr>"
                    + "".join(skill_rows) + "</table>")
    rule_rows = "".join(f"<tr><td><code>{rid}</code></td><td>{esc(name)}</td></tr>" for rid, name in rs)
    rules_table = f"<table><tr><th>Rule</th><th>Chặn / đảm bảo điều gì</th></tr>{rule_rows}</table>"

    # ── mind map skill+rule (sinh từ đĩa, self-contained CSS) ──
    mm_color = {"wiki-loop": ACCENTS[0][0], "dev-loop": ACCENTS[1][0],
                "orchestrate": ACCENTS[2][0], "utils": ACCENTS[3][0]}

    def _leaf(label, tip):
        t = ' title="%s"' % esc(tip) if tip else ''
        return '<span class="mm-leaf"%s>%s</span>' % (t, esc(label))

    mm = ['<div class="mindmap">',
          '<div class="mm-root">overstack<small>%d skill · %d rule</small></div>' % (n_sk, n_rules),
          '<div class="mm-tree">']
    for loop in loop_order + [l for l in by_loop if l not in loop_order]:
        items = sorted(by_loop.get(loop, []))
        if not items:
            continue
        leaves = "".join(_leaf("/" + n, d) for n, d in items)
        mm.append('<div class="mm-branch" style="--c:%s"><div class="mm-trunk">%s<b>%d</b></div>'
                  '<div class="mm-leaves">%s</div></div>'
                  % (mm_color.get(loop, ACCENTS[3][0]), esc(loop), len(items), leaves))
    rleaves = "".join(_leaf("%s · %s" % (rid, name), name) for rid, name in rs)
    mm.append('<div class="mm-branch" style="--c:%s"><div class="mm-trunk">rules<b>%d</b></div>'
              '<div class="mm-leaves">%s</div></div>' % (ACCENTS[5][0], n_rules, rleaves))
    mm.append('</div></div>')
    mindmap_html = "".join(mm)

    S = []
    S.append(("quickstart", "★ Quickstart", "00 · Bắt đầu", "Quickstart — chạy được trong 2 phút", [
        "<p class=\"lead\">Bạn chỉ cần nhớ ba thứ: <b>cài</b>, <b>để agent làm việc</b>, và <b>khi muốn tính năng mới thì /propose trước</b>. Phần còn lại overstack lo (rào chắn tất định chặn agent làm bậy, 0 token).</p>",
        "<h3>1. Cài vào dự án của bạn (một dòng)</h3>",
        "<p><b>Cách 1 — dán cho Agent</b> (agent tự cài rồi tự kiểm tra mọi thứ đã đúng chỗ):</p>",
        "<pre><code>chạy curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash và kiểm tra xem mọi thứ đã ở đúng chỗ chưa</code></pre>",
        "<p><b>Cách 2 — chạy thẳng trong terminal:</b></p>",
        "<pre><code>curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash</code></pre>",
        "<p>Lệnh này kéo cả ba trụ — <b>harness</b> (rào chắn), <b>skills</b> (kỹ năng), <b>llmwiki</b> (nền tri thức) — và bật guardrail ngay. Dự án cũ đã có wiki? Gọi <code>/harness-update</code> để migrate + tự trả nợ.</p>",
        "<h3>2. Cứ làm việc bình thường với agent</h3>",
        "<p>Agent (Claude Code, Cursor, opencode…) giờ bị overstack gác: không ghi bậy vào <code>raw/</code>, mọi trang wiki buộc có nguồn gốc (<code>## Origin</code>), index/log tự cập-nhật-bằng-code. Bạn không phải nhớ luật — hàng rào tự cắn.</p>",
        "<h3>3. Muốn một tính năng/đổi thay? gọi <code>/orca-workflow</code></h3>",
        "<p>Đây là lệnh bạn dùng nhiều nhất. <code>/orca-workflow</code> tự chạy trọn vòng <b>propose → gate → dispatch → verify</b>: vẽ kế hoạch (file ảnh hưởng, cái gì có thể vỡ, sequence diagram) + DỪNG chờ bạn duyệt, rồi giao việc cho các agent chạy song song, rồi đối chiếu kết quả. Các skill con (<code>propose</code>, <code>safe-change</code>, <code>verify-before-commit</code>…) do nó <b>điều phối</b> — bạn hiếm khi gọi tay từng cái.</p>",
        "<div class=\"note\"><h4>Lệnh bạn gọi TRỰC TIẾP nhiều nhất</h4><ul class=\"s\">"
        "<li><code>/orca-workflow</code> — dựng/đổi một tính năng (điều phối cả propose→gate→dispatch→verify).</li>"
        "<li><code>/orca-onboard</code> — onboard codebase (một hay nhiều) song song vào wiki.</li>"
        "<li><code>/harness-update</code> — tự bảo trì: cập nhật overstack + trả nợ wiki + health-check.</li>"
        "<li><code>find-skills \"&lt;việc&gt;\"</code> — không chắc có sẵn kỹ năng gì? hỏi nó.</li></ul></div>",
        "<p style=\"margin-top:14px\">Cần hiểu sâu từng phần? Các tab bên trái đi từ <b>tổng quan</b> → <b>cài đặt</b> → <b>ba trụ</b> → <b>workflow</b> → <b>tự bảo trì</b> → <b>tham chiếu đầy đủ</b>.</p>",
    ]))

    S.append(("what", "overstack là gì", "01 · Tổng quan", "overstack là gì", [
        "<p class=\"lead\">overstack <b>không phải một app</b> — nó là một lớp khung (a stack you put over your project) biến AI Agent thành một <b>cộng sự kỹ thuật tự-kỷ-luật</b>: có trí nhớ (wiki), có nguyên tắc không thể phá (harness), có tay nghề đóng gói sẵn (skills), và biết điều phối nhiều agent (Orca).</p>",
        f"<div class=\"kpi\"><div class=\"b\"><div class=\"n\" style=\"color:#0a84ff\">{n_sk}</div><div class=\"l\">skills (/…)</div></div>"
        f"<div class=\"b\"><div class=\"n\" style=\"color:#e0264b\">{n_rules}</div><div class=\"l\">rules tất định</div></div>"
        f"<div class=\"b\"><div class=\"n\" style=\"color:#5856d6\">{n_scripts}</div><div class=\"l\">harness scripts</div></div>"
        "<div class=\"b\"><div class=\"n\" style=\"color:#28a745\">0</div><div class=\"l\">token/lần gác</div></div>"
        "<div class=\"b\"><div class=\"n\" style=\"color:#30b0c7\">4</div><div class=\"l\">trụ</div></div></div>",
        "<div class=\"grid\"><div class=\"card\"><h4>Bốn trụ</h4><ul class=\"s\">"
        "<li><b>Wiki (tri thức)</b> — nơi dự án nhớ: concept, entity, nguồn, ADR, draft; mỗi trang truy được nguồn.</li>"
        "<li><b>Harness (rào chắn)</b> — luật tất định bằng code chặn agent làm bậy, không tốn token, không bypass được khi merge.</li>"
        "<li><b>Skills (kỹ năng)</b> — quy trình đóng gói, gọi bằng <code>/tên</code>, cài global dùng mọi dự án.</li>"
        "<li><b>Orca (điều phối)</b> — chạy nhiều agent song song: propose → gate → dispatch → verify.</li></ul></div>"
        "<div class=\"card\"><h4>Triết lý</h4><ul class=\"s\">"
        "<li><b>Đừng tin agent nhớ</b> — luật, log, bản đồ năng lực đều do CODE đảm bảo, không trông chờ trí nhớ LLM.</li>"
        "<li><b>Tất định &gt; xác suất</b> — rào chắn là code chạy 0-token; phần cần LLM bị nhốt sau adapter.</li>"
        "<li><b>Build-now-adapt-later</b> — dựng phần chắc chắn ngay, nhốt ẩn số sau MỘT adapter để chỉnh sau.</li>"
        "<li><b>Travel-with-project</b> — cái gì phục vụ dự án thì đi theo khi cài; đồ nghề dev framework ở lại.</li></ul></div></div>",
    ]))

    S.append(("install", "Cài đặt", "02 · Cài đặt", "Cài đặt — global vs per-project", [
        "<p class=\"lead\">overstack cài bằng một dòng bootstrap. Có hai chế độ, dùng cả hai là tốt nhất.</p>",
        "<h3>Bootstrap (mặc định — cả 3 trụ)</h3>",
        "<p><b>Cách 1 — dán cho Agent</b> (agent tự cài + tự kiểm tra):</p>",
        "<pre><code>chạy curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash và kiểm tra xem mọi thứ đã ở đúng chỗ chưa</code></pre>",
        "<p><b>Cách 2 — terminal:</b></p>",
        "<pre><code>curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash</code></pre>",
        "<p>Kéo harness + skills + llmwiki và bật chặn ngay. Opt-out: <code>--harness-only</code>.</p>",
        "<div class=\"note\"><h4>Dự án MỚI từ đầu (chưa có code)?</h4><p style=\"margin:0\">Không cần cài tay rồi feed từng file — chỉ <b>dán nội dung <code>00-New-Project.md</code></b> cho agent. Nó tự cài overstack → kickoff (hỏi 3 câu) → dựng knowledge base → scaffold MVP, dừng hỏi đúng lúc. Chi tiết: <code>setup.md</code>.</p></div>",
        "<div class=\"grid\"><div class=\"card\"><h4>Per-project (cho team)</h4><ul class=\"s\">"
        "<li>harness/ + .claude/settings.json được <b>commit vào repo</b> → đồng đội clone về là được bảo vệ.</li>"
        "<li>Có pre-commit (L2) + baseline audit cho dự án cũ.</li>"
        "<li>Đây là cách DUY NHẤT bảo vệ cả team (global chỉ bảo vệ máy bạn).</li></ul></div>"
        "<div class=\"card\"><h4>Global (cho máy bạn)</h4><ul class=\"s\">"
        "<li><code>install-harness.sh --global</code> → hooks + validators vào <code>~/.claude/harness/</code>.</li>"
        "<li>Mọi dự án có <code>llmwiki/</code> trên máy được gác; dự án khác chỉ tốn ~1ms/tool-call.</li>"
        "<li>Kèm <b>code-logger</b> + <b>build-capabilities</b> (ADR-005) → log + bản đồ năng lực xuống cùng dự án.</li></ul></div></div>",
        "<div class=\"note\"><h4>Sau khi cài</h4><ul class=\"s\">"
        "<li>Mở <b>session mới</b> thì hooks mới nạp.</li>"
        "<li>Chưa có <code>pre-commit</code>? cài <code>pipx install pre-commit</code> để bật chặn ở lớp L2.</li>"
        "<li>Tự bảo trì về sau: <code>/harness-update</code> (cập nhật + trả nợ + refresh bản đồ năng lực).</li></ul></div>",
    ]))

    S.append(("wiki", "Trụ 1 · Wiki", "03 · Tri thức", "Trụ 1 — Wiki (nền tri thức)", [
        "<p class=\"lead\">Wiki là bộ nhớ dài hạn của dự án. overstack ép nó luôn truy được nguồn và không bao giờ lệch index — bằng rào chắn, không bằng kỷ luật con người.</p>",
        "<div class=\"grid\"><div class=\"card\"><h4>Luật vàng của wiki</h4><ul class=\"s\">"
        "<li>Mọi trang phải có <code>## Origin</code> — luôn truy được nguồn gốc (R2).</li>"
        "<li>Thêm/xoá trang phải cập nhật <code>wiki/index.md</code> (R3) — overstack có <code>--fix</code> tự thêm.</li>"
        "<li>Mỗi thao tác append <code>wiki/log.md</code> — nay do <b>code-logger</b> ghi bằng code, không chờ agent.</li>"
        "<li>Không bao giờ ghi vào <code>raw/</code> — đó là inbox của con người, agent chỉ đọc (R1).</li></ul></div>"
        "<div class=\"card\"><h4>Cấu trúc thư mục</h4><ul class=\"s\">"
        "<li><code>concepts/</code> — khái niệm; <code>entities/</code> — thực thể; <code>sources/</code> — nguồn + ADR + draft.</li>"
        "<li><code>architecture/</code>, <code>tours/</code> — kiến trúc & tour. File wiki KHÔNG nằm ở gốc <code>wiki/</code> (R5).</li>"
        "<li>Frontmatter OKF v0.1 (<code>type:</code>…) — máy đọc được (R9).</li>"
        "<li>Liên kết chéo bằng <code>[[wikilink]]</code>; trang chỉ tạo SAU khi code đã commit.</li></ul></div></div>",
    ]))

    S.append(("harness", "Trụ 2 · Harness", "04 · Rào chắn", "Trụ 2 — Harness (rào chắn tất định)", [
        "<p class=\"lead\">Harness là phần làm overstack khác mọi \"prompt pack\": luật là CODE chạy ở hook/CI, chặn được agent kể cả khi nó cố tình lờ. 0 token, không bypass được khi merge.</p>",
        f"<p>Hiện có <b>{n_rules} rule</b> (R1–R{n_rules}). Mỗi rule là một validator tất định; vi phạm bị chặn ở write-time (hook), commit (pre-commit), và merge (CI) — ba lớp.</p>",
        rules_table,
        "<div class=\"grid\"><div class=\"card\"><h4>Bốn lớp gác (L0–L4)</h4><ul class=\"s\">"
        "<li><b>L0 hook</b> — chặn ngay lúc agent định ghi (PreToolUse).</li>"
        "<li><b>L1 settings</b> — wiring policy→agent.</li>"
        "<li><b>L2 pre-commit</b> — chặn lúc commit.</li>"
        "<li><b>L4 CI</b> — chặn lúc merge, nơi không agent nào bypass được.</li></ul></div>"
        "<div class=\"card\"><h4>Harness tự gác chính nó</h4><ul class=\"s\">"
        "<li><b>harness-lint</b> — bắt hằng-số-lệch giữa các script.</li>"
        "<li><b>harness-doctor</b> — chạy fixture sai/đúng qua từng validator, chứng minh rào còn cắn.</li>"
        "<li><b>fdk-gate</b> — định-nghĩa-hoàn-thành: 14 bước phải xanh mới cho push.</li></ul></div></div>",
    ]))

    S.append(("skills", "Trụ 3 · Skills", "05 · Kỹ năng", "Trụ 3 — Skills (kỹ năng đóng gói)", [
        f"<p class=\"lead\">Skill là một quy trình đóng gói thành file <code>SKILL.md</code>, gọi bằng <code>/tên</code>. Hiện có <b>{n_sk}</b> skill, chia theo \"loop\" (vòng công việc). Cài global qua <code>npx skills add</code> → dùng ở mọi dự án.</p>",
        "<div class=\"grid\"><div class=\"card\"><h4>wiki-loop</h4><ul class=\"s\"><li>nuôi tri thức: <code>/ingest</code>, <code>/query</code>, <code>/lint</code>.</li></ul></div>"
        "<div class=\"card\"><h4>dev-loop</h4><ul class=\"s\"><li>vòng phát triển: <code>/propose</code>, <code>/impact-check</code>, <code>/safe-change</code>, <code>/verify-before-commit</code>…</li></ul></div>"
        "<div class=\"card\"><h4>orchestrate (entry chính)</h4><ul class=\"s\"><li><b><code>/orca-workflow</code></b> · <b><code>/orca-onboard</code></b> — lệnh bạn gọi trực tiếp; chúng điều phối các skill dev-loop. Cùng nhóm: <code>/council</code>, <code>/trace-grader</code>.</li></ul></div>"
        "<div class=\"card\"><h4>utils</h4><ul class=\"s\"><li>tiện ích: <code>/fdk</code>, <code>/harness-update</code>, <code>/docs-site-macos</code>…</li></ul></div></div>",
        "<p>Bảng đầy đủ luôn-mới ở tab <a href=\"#reference\">Tham chiếu</a>. Không chắc dùng skill nào? <code>find-skills \"&lt;việc&gt;\"</code>.</p>",
    ]))

    S.append(("workflow", "Workflow dev", "06 · Quy trình", "Workflow — gọi /orca-workflow, nó lo 4 bước", [
        "<p class=\"lead\">Cách bạn làm việc thực tế: gọi <b><code>/orca-workflow</code></b> cho một tính năng — nó tự chạy trọn 4 bước dưới. Các skill dev-loop là <b>bước con</b> do nó điều phối, bạn không gọi tay từng cái.</p>",
        "<ol class=\"ck\">"
        "<li><b>propose</b> — restate yêu cầu, liệt kê file ảnh hưởng + cái có thể vỡ, vẽ sequence diagram, viết draft. DỪNG chờ bạn duyệt.</li>"
        "<li><b>gate</b> — validator R7 chặn proposal thiếu (đủ cặp <code>.md</code> + <code>.html</code> một-diagram-mỗi-task).</li>"
        "<li><b>dispatch</b> — giao việc cho các agent (chọn CLI theo bảng chi phí); chạy song song.</li>"
        "<li><b>verify</b> — <code>dispatch-verify</code> đối chiếu \"khai done\" với file thật; <code>/trace-grader</code> chấm cả ĐƯỜNG ĐI.</li></ol>",
        "<div class=\"note\"><h4>Hai lệnh điều phối bạn gọi trực tiếp</h4><p style=\"margin:0\"><code>/orca-workflow</code> (một tính năng) và <code>/orca-onboard</code> (onboard nhiều codebase song song). Các skill dev-loop (<code>propose</code> · <code>impact-check</code> · <code>safe-change</code> · <code>verify-before-commit</code>) là bước CON trong các flow này — gọi tay chỉ khi muốn chạy lẻ một bước.</p></div>",
    ]))

    S.append(("orca", "Orca (đa-agent)", "07 · Điều phối", "Orca — điều phối đa-agent", [
        "<p class=\"lead\">Orca là lớp điều phối: thay vì một agent làm tuần tự, nhiều agent chạy song song theo một flow có kiểm soát.</p>",
        "<div class=\"grid\"><div class=\"card\"><h4>Khi nào dùng</h4><ul class=\"s\">"
        "<li><code>/orca-workflow</code> — vòng propose→gate→dispatch hằng ngày cho một tính năng.</li>"
        "<li><code>/orca-onboard</code> — onboard nhiều codebase song song (phân tích đồng thời).</li></ul></div>"
        "<div class=\"card\"><h4>An toàn</h4><ul class=\"s\">"
        "<li>orca_guard hook canh hành vi đa-agent.</li>"
        "<li>dispatch-verify bắt \"khai done nhưng file vắng\".</li>"
        "<li>trace-grader chấm tool/thứ tự/pass^k — không chỉ kết quả.</li></ul></div></div>",
    ]))

    S.append(("bnal", "Build-now-adapt-later", "08 · Mẫu BNAL", "Build-now-adapt-later — thêm tính năng có ẩn số, không liều", [
        "<p class=\"lead\">Skill <b><code>/build-now-adapt-later</code></b> cho BẠN khi thêm vào <b>dự án của bạn</b> một tính năng còn phần chưa chắc (dùng model/API/lib nào, ngưỡng bao nhiêu, dịch vụ ngoài nào). Thay vì chờ chắc-chắn-mới-làm hay liều-đoán-rồi-khoá-mình, nó dựng phần CHẮC CHẮN ngay và nhốt phần CHƯA CHẮC sau MỘT adapter + config <code>verified:false</code> + một ADAPT-CHECKLIST — ship sớm, chỉnh sau ở đúng một chỗ.</p>",
        "<div class=\"grid\"><div class=\"card\"><h4>Build now</h4><ul class=\"s\">"
        "<li>Lõi tất định (cái bạn CHẮC) build + test ngay, không phụ thuộc ẩn số.</li>"
        "<li>Mọi ẩn số (model nào, ngưỡng bao nhiêu) sống ở ĐÚNG MỘT file config.</li>"
        "<li><code>verified:false</code> = đoán chưa xác nhận; phần gọi LLM/dịch vụ ngoài mặc định <code>enabled:false</code> (fail-safe).</li>"
        "<li><b>adapt-registry</b> gác: ẩn số không rò ra ngoài adapter (Step-7 leak-gate).</li></ul></div>"
        "<div class=\"card\"><h4>Adapt later</h4><ul class=\"s\">"
        "<li>Khi đã có dữ liệu / đã chốt lựa chọn: lõi pass self-test → <code>verified:true</code> hợp lệ.</li>"
        "<li>Phần ngoài (model/API): nối adapter + bật <code>enabled:true</code> sau khi kiểm chứng riêng.</li>"
        "<li>Chỉ sửa MỘT file adapter — không phải lục lại khắp codebase.</li></ul></div></div>",
        "<div class=\"note\"><h4>overstack tự ăn dog food</h4><p style=\"margin:0\">5 tính năng nâng cao của chính overstack (council · loop-runner · wikieval · trace-grader · failure-flywheel) đều dựng bằng BNAL — nên pattern này đã chứng minh trên thực tế, không phải lý thuyết.</p></div>",
    ]))

    S.append(("advanced", "Eval · Council · Loop", "09 · Nâng cao", "Eval · Council · Loop — 5 skill cho dự án của bạn", [
        "<p class=\"lead\">Năm skill nâng cao BẠN gọi khi dev dự án của mình (mỗi cái lõi tất định, phần LLM nhốt sau adapter). Dùng khi cần đánh giá chất lượng, quyết một vấn đề khó, hay chạy một vòng lặp tự-sửa an toàn.</p>",
        "<div class=\"grid\"><div class=\"card\"><h4>Đánh giá chất lượng</h4><ul class=\"s\">"
        "<li><b><code>/wikieval</code></b> — bộ eval hồi quy cho wiki dự án bạn (cascade assert tất định + baseline chặn merge khi tụt).</li>"
        "<li><b><code>/trace-grader</code></b> — chấm ĐƯỜNG ĐI agent đã đi (tool/thứ tự/pass^k), bắt \"đúng kết quả nhưng đi đường tệ\".</li></ul></div>"
        "<div class=\"card\"><h4>Quyết định khó & vòng lặp</h4><ul class=\"s\">"
        "<li><b><code>/council</code></b> — nhiều model trả lời độc lập → chấm chéo ẩn danh → tổng hợp, cho một vấn đề khó (Karpathy 3-stage).</li>"
        "<li><b><code>/loop-runner</code></b> — chạy vòng lặp agent CÓ chốt dừng bắt buộc (max-iter/budget/no-progress) — không sợ loop hoang.</li>"
        "<li><b><code>/failure-flywheel</code></b> — gom lỗi lặp trong dự án bạn → đề xuất rule/skill mới vào luồng /propose.</li></ul></div></div>",
    ]))

    S.append(("awareness", "Bản đồ năng lực & Logger", "10 · Tự-biết", "Bản đồ năng lực & Logger (đừng tin agent nhớ)", [
        "<p class=\"lead\">Hai cơ chế bảo đảm agent <b>biết mình có gì</b> và <b>nhớ đã làm gì</b> — bằng code, không bằng trí nhớ LLM (ADR-005).</p>",
        "<div class=\"grid\"><div class=\"card\"><h4>Bản đồ năng lực</h4><ul class=\"s\">"
        "<li><code>build-capabilities</code> sinh <code>CAPABILITIES.md</code> từ đĩa: mọi skill + rule.</li>"
        "<li>Xuống cùng dự án: downstream đọc <b>global skills + rule đã cài</b> → \"đồ nghề bạn có Ở DỰ ÁN NÀY\".</li>"
        "<li>Đủ = skill ＋ rule (harness chặn gì) ＋ state (đã làm gì).</li></ul></div>"
        "<div class=\"card\"><h4>Logger bằng code</h4><ul class=\"s\">"
        "<li><b>code-logger</b> để hook ghi <code>log.md</code> bằng CODE mỗi Write/Stop.</li>"
        "<li>Không trông chờ agent \"nhớ append log\" — máy ghi.</li>"
        "<li>Xuống cùng dự án (deploy cạnh hooks) → log wiki của chính dự án đó.</li></ul></div></div>",
    ]))

    S.append(("maintain", "Tự bảo trì", "11 · Bảo trì", "Tự bảo trì overstack trên máy bạn", [
        "<p class=\"lead\">overstack tự bảo trì được bằng một skill: cập nhật bản mới, trả nợ wiki cũ, refresh bản đồ năng lực, kiểm tra rào chắn — trong một lệnh.</p>",
        "<pre><code>/harness-update      # hoặc: bash harness/scripts/install-harness.sh . --self-heal</code></pre>",
        "<ol class=\"ck\">"
        "<li><b>Update + self-heal</b> — cài bản mới, tự backfill nợ (Origin/index/OKF) trong một process.</li>"
        "<li><b>Refresh bản đồ năng lực</b> — <code>build-capabilities --root .</code> để agent thấy đúng đồ nghề sau update.</li>"
        "<li><b>Health-check</b> — xác nhận rào chắn còn cắn (<code>/health-check</code>).</li></ol>",
        "<p>Đọc kết quả theo exit code: <code>0</code> sạch · <code>3</code> còn nợ cần xử tay một lần · khác = lỗi hạ tầng (dừng, báo nguyên văn).</p>",
    ]))

    S.append(("fdk", "FDK · dev overstack", "12 · Mở rộng", "FDK — phát triển chính overstack", [
        "<p style=\"font-size:12.5px;color:#b46a00;background:rgba(255,149,0,.1);border-radius:8px;padding:6px 12px;display:inline-block;margin:0 0 6px\">👷 Hai tab này (FDK + Dev cái mới) dành cho người <b>PHÁT TRIỂN chính overstack</b> — bỏ qua nếu bạn chỉ DÙNG overstack cho dự án của mình.</p>",
        "<p class=\"lead\">Khi bạn muốn sửa CHÍNH overstack (thêm skill/rule/validator/hook), gọi <code>/fdk</code> — front-door on-demand. KHÔNG auto-bơm mọi phiên (phần lớn phiên là dùng overstack cho DỰ ÁN KHÁC — ADR-004).</p>",
        "<div class=\"grid\"><div class=\"card\"><h4>/fdk lo gì</h4><ul class=\"s\">"
        "<li>Pre-flight: pull trước khi sửa · biết luật · đừng dẫm module cũ · propose trước.</li>"
        "<li>Inventory live (đếm skill/validator/rule từ đĩa, không hardcode).</li>"
        "<li>Self-contained: chạy được ở bất kỳ project nào.</li></ul></div>"
        "<div class=\"card\"><h4>Ranh giới (travel)</h4><ul class=\"s\">"
        "<li>Đồ nghề DEV (fdk-gate, meta-guards) ở LẠI repo overstack.</li>"
        "<li>Cái phục vụ dự án (skills, harness, code-logger, capability-map) thì TRAVEL xuống.</li></ul></div></div>",
        "<div class=\"note\"><h4>Dev framework TỪ một dự án khác → tự mở PR</h4><p style=\"margin:0\">Đang dở dự án khác mà cần chưng cất một skill vào overstack? Vì <code>fdk-gate</code>/<code>fdk/tools</code> không travel (ADR-004), <code>/fdk</code> dùng <code>fdk-kit.sh</code>: <b>pull</b> kit về sandbox <code>.overstack-kit/</code> → distill + <b>check</b> (fdk-gate) → <b>submit</b> = push branch + <code>gh pr create</code> tự mở PR vào <code>orca</code>. Một lệnh kéo về, một lệnh đẩy lên.</p></div>",
    ]))

    S.append(("newfeature", "★ Dev cái mới cần update gì", "13 · Checklist", "★ Dev một cái mới — cần update gì cho HỢP LỆ", [
        "<p class=\"lead\">👷 <i>(cho người phát triển overstack)</i> Khi thêm một tính năng/skill/rule mới cho overstack, đây là những chỗ phải đồng bộ để nó <b>hợp lệ</b> (bản máy-đọc = <code>fdk-gate</code>).</p>",
        "<ol class=\"ck\">"
        "<li><b>Code + test</b> — viết lõi tất định + self-test; ẩn số → nhốt sau MỘT adapter (<code>verified:false</code>).</li>"
        "<li><b>Rule mới?</b> → thêm vào <code>policy.yaml</code> + validator + wiring (đừng hardcode rời rạc).</li>"
        "<li><b>Skill mới?</b> → <code>skills/&lt;tên&gt;/SKILL.md</code> (canonical) + sync sang <code>llmwiki/skills/</code> (mirror) + LOOP_MAP + bảng skill trong AGENT.md ＋ CLAUDE.md (giữ parity) + CAPABILITIES.</li>"
        "<li><b>Cổng mới?</b> → cắm vào pre-commit + CI + một bước trong <code>fdk-gate</code>.</li>"
        "<li><b>Wiki \"vì sao\"</b> — viết concept giải thích lý do tồn tại (như feature-catalog).</li>"
        "<li><b>Docs người-đọc</b> — cập nhật trang này (regenerate) + README nếu đổi cách dùng.</li>"
        "<li><b>fdk-gate GREEN</b> — chạy <code>python3 harness/scripts/fdk-gate.py</code>, đủ bước mới push.</li></ol>",
        "<div class=\"note\"><h4>Vì sao cần checklist này</h4><p style=\"margin:0\">overstack lớn → thêm một thứ mà quên đồng bộ một chỗ = drift âm thầm. fdk-gate biến \"hợp lệ\" thành 14 bước máy-kiểm, không phụ thuộc trí nhớ.</p></div>",
    ]))

    S.append(("reference", "Tham chiếu (mind map)", "14 · Tham chiếu", "Tham chiếu — mind map skill & rule (đếm từ đĩa)", [
        f"<p class=\"lead\">Bản đồ tư duy toàn bộ đồ nghề, sinh từ đĩa nên luôn khớp thực tế: <b>{n_sk} skill</b> theo loop · <b>{n_rules} rule</b>. Rê chuột lên một lá để xem mô tả. Bản máy-đọc: <code>fdk/CAPABILITIES.md</code>.</p>",
        mindmap_html,
        "<h3 style=\"margin-top:26px\">Bảng chi tiết (mô tả đầy đủ)</h3>", skills_table, rules_table,
    ]))
    return S


def render(root: Path) -> str:
    S = sections(root)
    by_loop, n_sk = skills_by_loop(root)
    n_rules = len(rules(root))
    nav = ['<div class="logo">overstack<small>tài liệu chính thức · sinh từ đĩa</small></div>',
           '<div class="grp">Bắt đầu</div>']
    grouped = [("Bắt đầu", ["quickstart"]),
               ("Tổng quan", ["what", "install"]),
               ("Ba trụ", ["wiki", "harness", "skills"]),
               ("Quy trình", ["workflow", "orca"]),
               ("Nâng cao", ["bnal", "advanced", "awareness"]),
               ("Vận hành", ["maintain", "reference"]),
               ("👷 Phát triển overstack", ["fdk", "newfeature"])]
    id2nav = {sid: navlabel for sid, navlabel, *_ in S}
    idx = {sid: i for i, (sid, *_rest) in enumerate(S)}
    nav = ['<div class="logo">overstack<small>tài liệu chính thức · sinh từ đĩa</small></div>']
    for grp, ids in grouped:
        nav.append(f'<div class="grp">{grp}</div>')
        for sid in ids:
            nav.append(f'<a href="#s{idx[sid]}">{id2nav[sid]}</a>')
    body = []
    for i, (sid, navlabel, tag, title, blocks) in enumerate(S):
        inner = [f'<span class="tag">{tag}</span>', f"<h2>{title}</h2>"]
        inner.extend(blocks)
        body.append(f'<section id="s{i}" class="sec s{i}"><div class="inner">{"".join(inner)}</div></section>')
    html = [
        '<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>overstack — tài liệu chính thức</title>",
        "<style>", CSS_BASE, accent_css(len(S)), "</style></head><body>",
        "<nav>", "".join(nav), "</nav>",
        '<header class="hero"><span class="eyebrow">Tài liệu chính thức · cho người đọc</span>',
        "<h1>overstack</h1>",
        f"<p>Lớp khung biến AI Agent thành một cộng sự kỹ thuật tự-kỷ-luật: <b>tri thức</b> (wiki) · "
        f"<b>rào chắn tất định</b> (harness, {n_rules} rule, 0 token) · <b>kỹ năng</b> ({n_sk} skill) · "
        f"<b>điều phối đa-agent</b> (Orca). Bắt đầu ở Quickstart; các tab sau đi sâu từng phần.</p></header>",
        "".join(body),
        '<footer>overstack · tài liệu sinh bằng <code>fdk/tools/build-overstack-docs.py</code> (số liệu live từ đĩa) · '
        "self-contained, offline-proof · travel cùng install.</footer>",
        "<script>", JS, "</script></body></html>",
    ]
    return "".join(html)


def main():
    content = render(ROOT)
    if "--check" in sys.argv[1:]:
        cur = OUT.read_text(encoding="utf-8") if OUT.is_file() else ""
        if cur.strip() != content.strip():
            print("[build-overstack-docs] overstack.html CŨ so với đĩa — chạy lại để cập nhật.", file=sys.stderr)
            sys.exit(2)
        print("overstack.html khớp đĩa ✓")
        sys.exit(0)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(content, encoding="utf-8")
    print(f"✓ wrote {OUT.relative_to(ROOT)} ({len(content)} bytes, {content.count(chr(10)) + 1} dòng)")


if __name__ == "__main__":
    main()
