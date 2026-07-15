#!/usr/bin/env python3
"""build-health-dashboard — sinh MỘT trang glass HTML "sức khỏe framework", tính LIVE.

Chạy từng validator/check ở chế độ kiểm (subprocess, lấy exit-code + dòng stderr
đầu) rồi vẽ đèn giao thông xanh/đỏ/hổ-phách; đếm các artifact (skill, validator,
hook, rule, draft, html, ADR) bằng cách quét file thật; và — phần đinh — dựng
BẢNG DRIFT đếm số skill theo 5 nguồn khác nhau, gắn cờ đỏ mỗi nguồn lệch khỏi
số thư mục `skills/` (nguồn chân lý).

Trang xuất ra hoàn toàn self-contained (style + script nội tuyến, 0 request
ngoài) theo đúng khuôn liquid-glass của 280626-distill-destinations.html.

Dùng:
    python3 fdk/tools/build-health-dashboard.py

KHÔNG sửa file dùng-chung: chỉ GHI đúng llmwiki/html/280626-health-dashboard.html.
Mọi check chạy ở chế độ đọc/kiểm (sync-skills --check, drift-test idempotent).
"""
import glob
import importlib.util
import json
import os
import re
import subprocess
from html import escape as esc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "llmwiki" / "html" / "280626-health-dashboard.html"
GENERATED = "2026-06-28"  # hardcode theo yêu cầu — KHÔNG gọi datetime.now()

# ─────────────────────────────────────────────────────────── traffic-light checks
CHECKS = [
    ("Index ↔ wiki sync (R3)", "Mọi file wiki có 1 dòng trong index.md",
     ["python3", "harness/validators/index_sync.py", "--wiki-dir", "fdk/wiki"], None),
    ("Wiki health — broken links", "Không có [[wikilink]] gãy",
     ["python3", "harness/scripts/wiki-health.py", "--wiki-dir", "fdk/wiki", "--fail-on", "broken"], None),
    ("Architecture scan", "Không có anti-pattern kiến trúc",
     ["python3", "harness/scripts/arch-scan.py", "--root", "."], None),
    ("OKF frontmatter (R9)", "Frontmatter chuẩn OKF v0.1",
     ["python3", "harness/scripts/okf-check.py"], "harness/scripts/okf-check.py"),
    ("Skill mirror parity", "skills/ ↔ llmwiki/skills/ khớp",
     ["python3", "harness/scripts/sync-skills.py", "--check"], None),
    ("Policy → converters drift", "gen-converters khớp policy.yaml",
     ["bash", "harness/tests/policy-converters-drift-test.sh"], "harness/tests/policy-converters-drift-test.sh"),
]


def first_line(text, skip_brace=False):
    for ln in (text or "").splitlines():
        s = ln.strip()
        if s and not (skip_brace and s[0] in "{["):
            return s
    return ""


def run_check(cmd, exists):
    """→ (status, exit_code, note). status ∈ pass|fail|err."""
    if exists is not None and not (ROOT / exists).exists():
        return ("err", None, "thiếu tool: " + exists)
    try:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=180)
    except FileNotFoundError as e:
        return ("err", None, "không chạy được: " + str(e))
    except subprocess.TimeoutExpired:
        return ("err", None, "timeout > 180s")
    except Exception as e:  # noqa: BLE001 — tolerate bất kỳ tool lỗi nào
        return ("err", None, str(e)[:140])
    status = "pass" if r.returncode == 0 else "fail"
    note = first_line(r.stderr) or first_line(r.stdout, skip_brace=True)
    return (status, r.returncode, note)


# ─────────────────────────────────────────────────────────── live counts
def count_glob(pattern):
    return len(glob.glob(str(ROOT / pattern)))


def count_dirs(pattern):
    return len([p for p in glob.glob(str(ROOT / pattern)) if os.path.isdir(p)])


def count_html_docs():
    out_name = OUT.name
    return len([p for p in glob.glob(str(ROOT / "llmwiki" / "html" / "*.html"))
                if os.path.basename(p) != out_name])  # loại trừ chính nó → ổn định qua các lần chạy


def count_rules():
    try:
        txt = (ROOT / "harness" / "poc-vendor-neutral" / "policy.yaml").read_text(encoding="utf-8")
    except OSError:
        return None
    return len(re.findall(r"id:\s*R\d+", txt))


# ─────────────────────────────────────────────────────────── drift parsers
def count_marketplace():
    try:
        data = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return sum(len(p.get("skills", [])) for p in data.get("plugins", []))


def count_skill_table(rel):
    """Đếm số dòng dữ liệu trong bảng dưới heading `## Skills`."""
    try:
        lines = (ROOT / rel).read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    in_section = in_table = False
    n = 0
    for ln in lines:
        s = ln.strip()
        if s.startswith("## "):
            in_section = s.lower().startswith("## skills")
            in_table = False
            continue
        if not in_section:
            continue
        if s.startswith("|"):
            if "Skill" in s and "Invoke" in s:           # header
                in_table = True
                continue
            if set(s) <= set("|-: "):                     # separator
                continue
            if in_table:
                n += 1
        elif in_table and not s:
            in_table = False
    return n


def count_loop_map():
    p = ROOT / "harness" / "scripts" / "sync-skills.py"
    try:
        spec = importlib.util.spec_from_file_location("_sync_skills_probe", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)            # an toàn: main() có guard __main__
        return len(mod.LOOP_MAP)
    except Exception:                            # noqa: BLE001 — fallback regex
        try:
            txt = p.read_text(encoding="utf-8")
            block = re.search(r"LOOP_MAP\s*=\s*\{(.*?)\n\}", txt, re.S)
            return len(re.findall(r'"[^"]+"\s*:\s*"[^"]+"', block.group(1))) if block else None
        except OSError:
            return None


def grep_num(rel, pattern):
    try:
        txt = (ROOT / rel).read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(pattern, txt)
    return int(m.group(1)) if m else None


# ─────────────────────────────────────────────────────────── style (copy nguyên khối từ distill-destinations)
STYLE = """:root{
  --font-text:-apple-system,BlinkMacSystemFont,'SF Pro Text','Helvetica Neue','Roboto','Segoe UI',sans-serif;
  --font-display:-apple-system,BlinkMacSystemFont,'SF Pro Display','Helvetica Neue','Roboto','Segoe UI',sans-serif;
  --font-mono:'SF Mono',ui-monospace,'SFMono-Regular',Menlo,'Roboto Mono',Consolas,monospace;
  --glass-2:rgba(255,255,255,.7);--glass-3:rgba(255,255,255,.88);--blur-2:8px;--blur-3:4px;
  --edge-hi:inset 0 1px 0 rgba(255,255,255,.85);--border:rgba(30,90,170,.14);--t1:#0f0f12;--t2:#4a4a55;
}
*{box-sizing:border-box}
html{background:#e9f0fb;scrollbar-width:thin;scrollbar-color:transparent transparent}
html.scrolling{scrollbar-color:rgba(10,132,255,.32) transparent}
body{margin:0;padding-left:210px;font-family:var(--font-text);color:var(--t1);line-height:1.6;
  background:radial-gradient(900px 500px at 12% -10%,rgba(10,132,255,.10),transparent 60%),radial-gradient(700px 420px at 95% 15%,rgba(90,162,232,.08),transparent 55%),linear-gradient(180deg,#f7fbff,#eaf2fd);
  transition:padding-left .28s cubic-bezier(.4,0,.2,1)}
body::before{content:'';position:fixed;inset:-10%;z-index:-1;pointer-events:none;
  background:radial-gradient(640px 440px at 10% 14%,rgba(10,132,255,.22),transparent 65%),radial-gradient(380px 460px at 4% 52%,rgba(48,176,199,.18),transparent 65%),radial-gradient(540px 400px at 88% 10%,rgba(88,86,214,.13),transparent 60%),radial-gradient(720px 500px at 74% 76%,rgba(48,176,199,.13),transparent 65%),radial-gradient(480px 380px at 16% 86%,rgba(255,149,0,.12),transparent 60%);
  animation:orbDrift 46s ease-in-out infinite alternate}
@keyframes orbDrift{100%{transform:translate(2.2%,1.6%) scale(1.045)}}
body::after{content:'';position:fixed;inset:0;z-index:-1;pointer-events:none;background-image:radial-gradient(rgba(30,90,170,.11) 1px,transparent 1.3px);background-size:22px 22px;mask-image:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,.22))}
@media(prefers-reduced-motion:reduce){body::before{animation:none}}
::-webkit-scrollbar{width:11px;height:11px;background:transparent}
::-webkit-scrollbar-track,::-webkit-scrollbar-track-piece,::-webkit-scrollbar-corner,::-webkit-scrollbar-button{background:transparent;border:0;box-shadow:none}
::-webkit-scrollbar-thumb{background:transparent;border-radius:8px;border:3px solid transparent;background-clip:content-box;transition:background-color .25s ease}
html.scrolling::-webkit-scrollbar-thumb,nav.scrolling::-webkit-scrollbar-thumb,::-webkit-scrollbar-thumb:hover{background-color:rgba(10,132,255,.32)}
nav{position:fixed;top:0;left:0;bottom:0;width:210px;z-index:100;overflow-y:auto;display:flex;flex-direction:column;gap:2px;padding:18px 12px;
  background:linear-gradient(165deg,rgba(255,255,255,.46),rgba(255,255,255,.22) 48%,rgba(240,248,255,.34));
  backdrop-filter:blur(24px) saturate(1.7) brightness(1.04);-webkit-backdrop-filter:blur(24px) saturate(1.7) brightness(1.04);
  border-right:1px solid rgba(255,255,255,.55);box-shadow:inset 0 1px 0 rgba(255,255,255,.9),4px 0 24px rgba(30,90,170,.08);transition:transform .28s cubic-bezier(.4,0,.2,1)}
nav::before{content:'';position:absolute;inset:0;pointer-events:none;background:radial-gradient(220px 160px at 18% 4%,rgba(255,255,255,.55),transparent 70%),linear-gradient(115deg,rgba(255,255,255,.28),transparent 28%,transparent 72%,rgba(255,255,255,.14))}
nav>*{position:relative}
nav .logo{margin:0 0 14px;padding:6px 10px;font-family:var(--font-display);font-weight:800;font-size:17px;letter-spacing:-.02em;color:#0a84ff}
nav .logo small{display:block;font-size:10px;font-weight:600;color:var(--t2);-webkit-text-fill-color:var(--t2)}
nav a{padding:8px 12px;border-radius:10px;font-size:13px;color:var(--t2);text-decoration:none;position:relative;overflow:hidden;transition:background .15s,color .15s}
nav a:hover{background:rgba(10,132,255,.06);color:#0a84ff}
nav a.active{color:#0a84ff;background:rgba(10,132,255,.08);font-weight:600}
.nav-close{position:absolute;top:10px;right:10px;width:26px;height:26px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:12px;color:var(--t2);cursor:pointer;background:rgba(0,0,0,.04);border:none}
body.nav-collapsed nav{transform:translateX(-100%)}body.nav-collapsed{padding-left:0}
.nav-toggle{position:fixed;top:12px;left:12px;z-index:120;width:32px;height:32px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:14px;color:var(--t2);cursor:pointer;background:linear-gradient(165deg,rgba(255,255,255,.5),rgba(255,255,255,.24));backdrop-filter:blur(24px) saturate(1.7);-webkit-backdrop-filter:blur(24px) saturate(1.7);border:1px solid transparent;box-shadow:inset 0 1px 0 rgba(255,255,255,.75),0 0 0 1px rgba(30,90,170,.08),0 2px 10px rgba(30,90,170,.12);transition:opacity .2s,transform .28s}
.nav-toggle:hover{color:#0a84ff}body:not(.nav-collapsed) .nav-toggle{opacity:0;pointer-events:none}
@media(max-width:640px){body{padding-left:0}}
.hero{max-width:1100px;margin:0 auto;padding:84px 24px 22px}
.hero .eyebrow{display:inline-block;font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:#0a84ff;background:rgba(10,132,255,.10);padding:4px 12px;border-radius:999px;margin-bottom:16px}
.hero h1{font-family:var(--font-display);font-size:clamp(30px,4.6vw,50px);line-height:1.06;letter-spacing:-.02em;margin:0 0 14px;color:#0a84ff}
.hero p{font-size:16.5px;color:var(--t2);max-width:720px;margin:0}
section{position:relative}
.section-bg::before{content:'';position:absolute;top:0;bottom:0;left:50%;width:100vw;transform:translateX(-50%);pointer-events:none}
.section-inner{position:relative;max-width:1100px;margin:0 auto;padding:54px 24px 58px}
.section-header .tag{display:inline-block;font-size:12px;font-weight:700;padding:4px 12px;border-radius:999px;margin-bottom:12px}
.section-header h2{font-family:var(--font-display);font-size:26px;letter-spacing:-.02em;color:#1d1d1f;margin:0 0 8px}
.section-header p{font-size:15px;color:var(--t2);max-width:780px;margin:0 0 16px}
.card{background:var(--glass-2);backdrop-filter:blur(var(--blur-2)) saturate(1.1);-webkit-backdrop-filter:blur(var(--blur-2)) saturate(1.1);border:1px solid var(--border);border-radius:16px;box-shadow:var(--edge-hi),0 4px 20px rgba(0,0,0,.06);padding:20px;margin-top:16px}
.card h4{margin:0 0 10px;font-size:15px}
.card code,td code,p code,li code{font-family:var(--font-mono);font-size:.85em;background:rgba(10,132,255,.08);padding:1px 5px;border-radius:5px;color:#0a5ec7}
.table-wrap{margin-top:16px;border-radius:14px;overflow:hidden;border:1px solid var(--border);box-shadow:var(--edge-hi),0 4px 20px rgba(0,0,0,.05)}
table{width:100%;border-collapse:collapse;background:var(--glass-3);backdrop-filter:blur(var(--blur-3));-webkit-backdrop-filter:blur(var(--blur-3));font-size:13px}
th,td{text-align:left;padding:10px 13px;border-bottom:1px solid var(--border);vertical-align:top}
th{font-weight:700;background:rgba(255,255,255,.5);font-size:12px}
tr:last-child td{border-bottom:none}
td b{color:var(--t1)}
.yes{color:#1e8e3e;font-weight:700}.no{color:#d11a3a;font-weight:700}.loc{color:#b96b00;font-weight:700}
.steps{list-style:none;margin:14px 0 0;padding:0;display:flex;flex-direction:column;gap:7px}
.steps li{position:relative;padding-left:20px;font-size:13.5px;color:var(--t2)}
.steps li::before{content:'›';position:absolute;left:3px;font-weight:700;color:#0a84ff}
footer{max-width:1100px;margin:0 auto;padding:28px 24px 60px;font-size:12.5px;color:var(--t2);border-top:1px solid var(--border)}
#sec-0 .tag{background:rgba(10,132,255,.12);color:#0a84ff}.s-bg0::before{background:linear-gradient(180deg,rgba(10,132,255,.05),transparent 60%)}
#sec-1 .tag{background:rgba(88,86,214,.12);color:#5856d6}.s-bg1::before{background:linear-gradient(180deg,rgba(88,86,214,.05),transparent 60%)}
#sec-2 .tag{background:rgba(255,45,85,.12);color:#e0264b}.s-bg2::before{background:linear-gradient(180deg,rgba(255,45,85,.05),transparent 60%)}
/* ─── dashboard additions (cùng token glass) ─── */
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(118px,1fr));gap:12px;margin-top:8px}
.metric{background:var(--glass-2);backdrop-filter:blur(var(--blur-2)) saturate(1.1);-webkit-backdrop-filter:blur(var(--blur-2)) saturate(1.1);border:1px solid var(--border);border-radius:14px;box-shadow:var(--edge-hi),0 4px 20px rgba(0,0,0,.06);padding:15px 14px;text-align:center}
.metric .n{font-family:var(--font-display);font-size:30px;font-weight:800;letter-spacing:-.02em;line-height:1;color:#0a84ff}
.metric .l{display:block;margin-top:7px;font-size:11px;color:var(--t2);font-weight:600;line-height:1.3}
.metric .src{display:block;margin-top:3px;font-family:var(--font-mono);font-size:9.5px;color:#0a5ec7;opacity:.8}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(305px,1fr));gap:14px;margin-top:16px}
.tile{position:relative;background:var(--glass-2);backdrop-filter:blur(var(--blur-2)) saturate(1.1);-webkit-backdrop-filter:blur(var(--blur-2)) saturate(1.1);border:1px solid var(--border);border-radius:14px;box-shadow:var(--edge-hi),0 4px 20px rgba(0,0,0,.06);padding:15px 16px 15px 19px;overflow:hidden}
.tile::before{content:'';position:absolute;left:0;top:0;bottom:0;width:5px}
.tile.pass::before{background:#1e8e3e}.tile.fail::before{background:#d11a3a}.tile.err::before{background:#f0a000}
.tile .top{display:flex;align-items:center;gap:9px;margin-bottom:5px}
.tile .dot{width:11px;height:11px;border-radius:50%;flex:0 0 auto}
.tile.pass .dot{background:#34c759;box-shadow:0 0 0 3px rgba(52,199,89,.16),0 0 9px rgba(52,199,89,.5)}
.tile.fail .dot{background:#ff3b30;box-shadow:0 0 0 3px rgba(255,59,48,.16),0 0 9px rgba(255,59,48,.5)}
.tile.err .dot{background:#ff9500;box-shadow:0 0 0 3px rgba(255,149,0,.16),0 0 9px rgba(255,149,0,.5)}
.tile .name{font-weight:700;font-size:14px}
.tile .verdict{margin-left:auto;font-size:11px;font-weight:800;letter-spacing:.05em}
.tile.pass .verdict{color:#1e8e3e}.tile.fail .verdict{color:#d11a3a}.tile.err .verdict{color:#b96b00}
.tile .desc{font-size:12px;color:var(--t2);margin-bottom:8px}
.tile .cmd{font-family:var(--font-mono);font-size:10.5px;color:#0a5ec7;background:rgba(10,132,255,.07);border-radius:6px;padding:4px 7px;display:block;margin-bottom:8px;word-break:break-all}
.tile .note{font-size:11.5px;color:var(--t2);line-height:1.45}
.tile .note b{color:var(--t1);font-family:var(--font-mono);font-size:11px}
.legend{display:flex;gap:18px;flex-wrap:wrap;margin-top:14px;font-size:12px;color:var(--t2)}
.legend span{display:inline-flex;align-items:center;gap:7px}
.legend i{width:11px;height:11px;border-radius:50%;display:inline-block}
.i-pass{background:#34c759}.i-fail{background:#ff3b30}.i-err{background:#ff9500}
td.num{font-family:var(--font-mono);font-weight:700;text-align:right;font-size:15px;white-space:nowrap}
.flag{display:inline-block;margin-left:7px;font-size:10px;font-weight:800;color:#d11a3a;background:rgba(255,45,85,.1);border-radius:5px;padding:1px 6px;vertical-align:middle}
.flag.ok{color:#1e8e3e;background:rgba(52,199,89,.12)}
tr.truth td{background:rgba(52,199,89,.07)}
tr.stale td{background:rgba(255,149,0,.06)}"""

SCRIPTS = """<script>
(function(){const nav=document.querySelector('nav');if(!nav)return;const b=document.createElement('button');b.className='nav-toggle';b.textContent='\\u2630';document.body.appendChild(b);const c=document.createElement('button');c.className='nav-close';c.textContent='\\u2715';nav.appendChild(c);const ap=v=>{document.body.classList.toggle('nav-collapsed',v);try{localStorage.setItem('nc',v?'1':'0')}catch(e){}};b.onclick=()=>ap(false);c.onclick=()=>ap(true);try{const s=localStorage.getItem('nc');if(s==='1'||(s!=='0'&&matchMedia('(max-width:640px)').matches))ap(true)}catch(e){}})();
(function(){const ls=[...document.querySelectorAll('nav a')],ss=[...document.querySelectorAll('section[id]')];const o=new IntersectionObserver(es=>{let a='';for(const e of es)if(e.isIntersecting)a=e.target.id;if(a)ls.forEach(l=>l.classList.toggle('active',l.getAttribute('href')==='#'+a))},{rootMargin:'-40% 0px -55% 0px'});ss.forEach(s=>o.observe(s));})();
(function(){const f=el=>{let t;return()=>{el.classList.add('scrolling');clearTimeout(t);t=setTimeout(()=>el.classList.remove('scrolling'),900)}};window.addEventListener('scroll',f(document.documentElement),{passive:true});})();
</script>"""


def tile_html(name, desc, cmd, status, code, note):
    verdict = {"pass": "PASS", "fail": "FAIL", "err": "ERROR"}[status]
    code_s = ("exit " + str(code)) if code is not None else "n/a"
    note_s = esc(note) if note else "&mdash;"
    return (f'<div class="tile {status}">'
            f'<div class="top"><span class="dot"></span><span class="name">{esc(name)}</span>'
            f'<span class="verdict">{verdict}</span></div>'
            f'<div class="desc">{esc(desc)}</div>'
            f'<code class="cmd">{esc(cmd)}</code>'
            f'<div class="note">{note_s} &middot; <b>{code_s}</b></div></div>')


def metric_html(n, label, src):
    val = "&mdash;" if n is None else str(n)
    return (f'<div class="metric"><div class="n">{val}</div>'
            f'<span class="l">{esc(label)}</span><span class="src">{esc(src)}</span></div>')


def drift_row(name, src, val, role, truth, is_truth=False, stale=False):
    val_s = "&mdash;" if val is None else str(val)
    if is_truth:
        flag = '<span class="flag ok">truth</span>'
    elif val is None:
        flag = ""
    elif val != truth:
        flag = f'<span class="flag">&ne; {truth}</span>'
    else:
        flag = '<span class="flag ok">=</span>'
    cls = " truth" if is_truth else (" stale" if stale else "")
    note = role
    if stale and val is not None and val != truth:
        note += f' &mdash; <b class="no">STALE</b>: ghi {val}, thực tế {truth}'
    return (f'<tr class="{cls.strip()}"><td><b>{esc(name)}</b><br><code>{esc(src)}</code></td>'
            f'<td class="num">{val_s}{flag}</td><td>{note}</td></tr>')


def main():
    # 1) traffic-light checks (live subprocess)
    results = [(name, desc, cmd, *run_check(cmd, ex)) for (name, desc, cmd, ex) in CHECKS]
    passed = sum(1 for r in results if r[3] == "pass")

    # 2) counts strip (live file scan)
    counts = {
        "skills": count_dirs("skills/*/"),
        "validators": count_glob("harness/validators/*.py"),
        "hooks": count_glob("llmwiki/.claude/hooks/*.py"),
        "rules": count_rules(),
        "drafts": count_glob("fdk/wiki/sources/draft/*.md") + count_glob("fdk/wiki/draft/orca/*.md"),
        "html": count_html_docs(),
        "adrs": count_glob("fdk/wiki/sources/adr/ADR-*.md"),
    }

    # 3) drift table (skill-count, 5-way + stale docs)
    truth = counts["skills"]
    drift = {
        "marketplace": count_marketplace(),
        "agent": count_skill_table("llmwiki/AGENT.md"),
        "claude": count_skill_table("llmwiki/CLAUDE.md"),
        "loop_map": count_loop_map(),
        "arch": grep_num("fdk/wiki/concepts/architecture.md", r"Published Skills\s*\((\d+)"),
        "proj": grep_num("fdk/wiki/entities/project-structure.md", r"(\d+)\s+published skills"),
    }
    disagree = sum(1 for k in ("marketplace", "agent", "claude", "loop_map", "arch", "proj")
                   if drift[k] is not None and drift[k] != truth)

    # ── render
    tiles = "\n".join(tile_html(n, d, " ".join(c), st, co, no) for (n, d, c, st, co, no) in results)
    metrics = "\n".join([
        metric_html(counts["skills"], "Skills", "skills/*/"),
        metric_html(counts["validators"], "Validators", "harness/validators"),
        metric_html(counts["hooks"], "Hooks", ".claude/hooks"),
        metric_html(counts["rules"], "Rules (R*)", "policy.yaml"),
        metric_html(counts["drafts"], "Drafts", "draft/*.md"),
        metric_html(counts["html"], "HTML docs", "llmwiki/html"),
        metric_html(counts["adrs"], "ADRs", "sources/adr"),
    ])
    drift_rows = "\n".join([
        drift_row("skills/ directories", "ls -d skills/*/", truth, "nguồn chân lý — đếm thư mục skill thật", truth, is_truth=True),
        drift_row("marketplace.json entries", ".claude-plugin/marketplace.json", drift["marketplace"], "skill được khai trong plugin npx", truth),
        drift_row("AGENT.md skill-table rows", "llmwiki/AGENT.md", drift["agent"], "bảng router cho agent", truth),
        drift_row("CLAUDE.md skill-table rows", "llmwiki/CLAUDE.md", drift["claude"], "bảng router cho Claude", truth),
        drift_row("sync-skills LOOP_MAP entries", "harness/scripts/sync-skills.py", drift["loop_map"], "map skill → loop của mirror", truth),
        drift_row("architecture.md (hardcoded)", "fdk/wiki/concepts/architecture.md", drift["arch"], "số cứng trong tài liệu", truth, stale=True),
        drift_row("project-structure.md (hardcoded)", "fdk/wiki/entities/project-structure.md", drift["proj"], "số cứng trong tài liệu", truth, stale=True),
    ])

    health_word = "khỏe" if passed == len(results) else "có vấn đề"
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Framework Health Dashboard — {GENERATED}</title>
<style>
{STYLE}
</style>
</head>
<body>
<nav>
  <div class="logo">Health<small>framework dashboard</small></div>
  <a href="#sec-0">Counts</a>
  <a href="#sec-1">Traffic lights</a>
  <a href="#sec-2">Drift table</a>
</nav>

<header class="hero">
  <span class="eyebrow">Framework Health &middot; live</span>
  <h1>Dashboard sức khỏe framework</h1>
  <p>Trang này được sinh ra bằng cách <b>chạy thật</b> từng validator/check rồi quét file để đếm artifact &mdash;
  không có số liệu chép tay. Hiện trạng: <b>{passed}/{len(results)}</b> check xanh ({health_word}),
  và <b>{disagree}</b> nguồn đang <b class="no">lệch</b> khỏi số skill chuẩn (<b>{truth}</b>).</p>
</header>

<section id="sec-0" class="section-bg s-bg0"><div class="section-inner">
  <div class="section-header"><span class="tag">00 &middot; Counts</span>
    <h2>Đếm artifact (live)</h2>
    <p>Mỗi ô đếm trực tiếp trên đĩa lúc sinh trang. Nguồn ghi dưới mỗi số.</p>
  </div>
  <div class="metrics">
{metrics}
  </div>
</div></section>

<section id="sec-1" class="section-bg s-bg1"><div class="section-inner">
  <div class="section-header"><span class="tag">01 &middot; Traffic lights</span>
    <h2>Đèn giao thông — chạy từng check</h2>
    <p>Mỗi ô chạy đúng lệnh ghi trong ô, lấy <b>exit code</b> (xanh = 0 / đỏ &ne; 0) và dòng <code>stderr</code> đầu tiên làm ghi chú. Hổ-phách = tool thiếu hoặc lỗi khi chạy.</p>
  </div>
  <div class="tiles">
{tiles}
  </div>
  <div class="legend">
    <span><i class="i-pass"></i> PASS &mdash; exit 0</span>
    <span><i class="i-fail"></i> FAIL &mdash; exit &ne; 0</span>
    <span><i class="i-err"></i> ERROR &mdash; thiếu tool / lỗi chạy</span>
  </div>
</div></section>

<section id="sec-2" class="section-bg s-bg2"><div class="section-inner">
  <div class="section-header"><span class="tag">02 &middot; Drift table</span>
    <h2>Drift số skill &mdash; 5 nguồn vs sự thật</h2>
    <p>Số thư mục trong <code>skills/</code> là <b>nguồn chân lý</b>. Mọi nơi khác khai con số skill phải bằng nó; ô nào <b class="no">lệch</b> bị gắn cờ đỏ. Hai dòng cuối là số <b>cứng</b> kẹt trong tài liệu (đã cũ).</p>
  </div>
  <div class="table-wrap"><table>
    <thead><tr><th>Nguồn đếm</th><th style="text-align:right">Số skill</th><th>Vai trò / ghi chú</th></tr></thead>
    <tbody>
{drift_rows}
    </tbody>
  </table></div>
  <div class="card"><h4>Đọc bảng thế nào</h4>
    <ul class="steps">
      <li>Dòng nền xanh = <b>truth</b> ({truth} thư mục skill). Các dòng khác so với nó.</li>
      <li>Cờ <span class="no">&ne; {truth}</span> = nguồn đó kê sai số skill &rarr; cần đồng bộ (vd chạy <code>sync-skills.py</code>, cập nhật bảng AGENT.md/CLAUDE.md, hoặc sửa số cứng trong docs).</li>
      <li>Bảng/marketplace/LOOP_MAP có thể nhỏ hơn truth vì cố ý không xuất bản hết skill; nhưng số <b>cứng trong docs</b> lệch là nợ kỹ thuật rõ ràng.</li>
    </ul>
  </div>
</div></section>

<footer>Framework Health Dashboard &middot; sinh tự động bởi <code>fdk/tools/build-health-dashboard.py</code> &middot;
self-contained, offline-proof (0 request ngoài) &middot; generated {GENERATED}.</footer>

{SCRIPTS}
</body>
</html>
"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")

    # ── console summary
    print(f"✓ wrote {OUT.relative_to(ROOT)}  ({len(html.encode('utf-8'))//1024} KB)")
    print(f"  checks: {passed}/{len(results)} pass")
    for (n, _d, _c, st, co, _no) in results:
        print(f"    [{st:4}] exit={co}  {n}")
    print(f"  counts: {counts}")
    print(f"  drift (truth={truth}): " + ", ".join(
        f"{k}={drift[k]}" for k in ("marketplace", "agent", "claude", "loop_map", "arch", "proj")))


if __name__ == "__main__":
    main()
