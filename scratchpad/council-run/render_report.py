#!/usr/bin/env python3
"""Stage-4 HTML report — STRUCTURED. Feeds from council.transcript.json for the
deterministic voting math; seat opinions are held as structured objects (verdict/
risks/fixes) so the page renders as tidy cards, not a wall of text. All strings
are HTML-escaped (Taleb fix #1)."""
import json, html, pathlib, sys
run = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
T = json.load(open(run / "council.transcript.json"))
def e(x): return html.escape(str(x), quote=True)

# ---- structured seat content (distilled from Stage-1 answers) ----
SEATS = {
 "taleb": dict(name="Nassim Taleb", lens="Phản mong manh & rủi ro đuôi",
   sig="Thiết kế cho cái ĐUÔI, không phải trung bình.", accent="#7a5c86", init="T",
   verdict="GIỮ opt-in — nhưng lũy kế fragility ở ranh giới.",
   risks=[("Coupling không phase-locked","Template /docs-site-macos đổi → HTML vỡ, user không biết lỗi ở council.py hay skill kia → chạy lại cả council."),
          ("HTML injection","author/text không sanitize trong council.py, chỉ dặn layer khác escape → ngã lúc integration."),
          ("Scope chat-room thừa","bubble/avatar/timeline thêm kỳ vọng hành vi mà docs-site-macos không cam kết; đổi template phải port cả 3.")],
   fixes=["Sanitize HTML entities NGAY trong council.py","Bỏ chat-room debate, giữ blind-vote + dashboard","Fail-safe: render fail vẫn emit transcript, --report trả lỗi tường minh"]),
 "munger": dict(name="Charlie Munger", lens="Đa mô hình & nghịch đảo",
   sig="Cái gì ĐẢM BẢO thất bại? (invert, rồi tránh).", accent="#3f7d74", init="M",
   verdict="GIỮ — lõi deterministic isolation tốt, opt-in sound.",
   risks=[("Không self-contained","phụ thuộc skill ngoài → skill unavailable = dependent-failure trong khi core vẫn tốt."),
          ("Trigger #2 mơ hồ","'chia sẻ ra ngoài người vận hành' cần context-detection phức tạp hơn 1 cờ."),
          ("Chairman delay","render --report trước khi chairman_synthesis fill → HTML incomplete/misleading.")],
   fixes=["Bỏ heuristic trigger #2 → chỉ explicit --report","Chain-guard: chặn --report nếu chairman_synthesis==None","Graceful fallback về markdown nếu docs-site-macos unavailable"]),
 "kahneman": dict(name="Daniel Kahneman", lens="Thiên kiến nhận thức",
   sig="Chính suy nghĩ của ta là lỗi đầu tiên.", accent="#b06a2c", init="K",
   verdict="GIỮ opt-in — nhưng HTML là công cụ tâm lý, không trung lập.",
   risks=[("WYSIATI","HTML bóng bẩy làm người đọc TIN kết quả hơn thực chất → authority illusion kể cả khi verified:false."),
          ("Cognitive fatigue","'one big page' → non-IT skip debate, nhìn thẳng dashboard, nhầm consensus là chân lý."),
          ("Novelty + sunk-cost","bật --report lần đầu → xu hướng render liên tục → coupling thành non-negotiable.")],
   fixes=["Warning box rõ khi verified:false","Tách Findings vs Caveats","Defer visual refinement — transcript.md đủ 95% internal"]),
}

agg = T["aggregate"]; jr = T["judge_rankings"]; anchor = T["anchor_guard"]
pres = anchor.get("presentation_order", {})
order = [(r["author"], r["label"], r["mean_rank"], r["ranks"], r["consensus_rank"]) for r in agg]
label_of = {a:l for a,l,_,_,_ in order}
winner, contested = T["winner"], T["most_contested"]
seed, verified = T.get("seed"), T.get("verified", False)
synth = T.get("chairman_synthesis","")

MEDAL = {1:"🥇",2:"🥈",3:"🌱"}

# ---- Section 1: structured opinion cards ----
cards = ""
for author, label, mean, ranks, crank in order:
    s = SEATS[author]; ac = s["accent"]
    risks = "".join(f'<li><span class="rk" style="background:{ac}">{i+1}</span><div><b>{e(t)}</b><p>{e(d)}</p></div></li>' for i,(t,d) in enumerate(s["risks"]))
    fixes = "".join(f'<li>{e(f)}</li>' for f in s["fixes"])
    cards += f'''
    <div class="pcard" style="--ac:{ac}">
      <div class="phead">
        <div class="pav" style="background:{ac}">{e(s["init"])}</div>
        <div><div class="pname">{e(s["name"])} <span class="rankpill">{MEDAL[crank]} #{crank} · mean {e(mean)}</span></div>
        <div class="plens">{e(s["lens"])} · <i>{e(s["sig"])}</i></div></div>
        <div class="blindtag">blind {e(label)}</div>
      </div>
      <div class="verdict-line">⚖️ {e(s["verdict"])}</div>
      <div class="cols">
        <div><h4>Rủi ro</h4><ul class="risks">{risks}</ul></div>
        <div><h4>Đề xuất sửa</h4><ul class="fixes">{fixes}</ul></div>
      </div>
    </div>'''

# ---- Section 2: blind vote ----
vote_rows = "".join(
    f'<tr><td>{e(j["judge"])}</td><td class="mono">{" › ".join(e(x) for x in j["ranking_labels"])}</td>'
    f'<td class="mono dim">{" → ".join(e(x) for x in pres.get(j["judge"],[]))}</td></tr>' for j in jr)
reveal = "".join(f'<span class="chip" style="--c:{SEATS[a]["accent"]}">{e(l)} = {e(SEATS[a]["name"])}</span>' for a,l,_,_,_ in order)

# ---- Section 3: dashboard ----
dash = "".join(
    f'<tr><td class="mono"><b>{e(l)}</b></td><td>{MEDAL[cr]} {e(SEATS[a]["name"])}</td><td class="mono">{e(m)}</td><td class="mono dim">{e(rk)}</td></tr>'
    for a,l,m,rk,cr in order)
unan = all(j["ranking_labels"]==jr[0]["ranking_labels"] for j in jr)

# chairman synthesis → split into lines/bullets
syn_html=""
for ln in synth.split("\n"):
    ln=ln.strip()
    if not ln: continue
    if ln[0:2] in ("1.","2.","3.","4."):
        syn_html+=f'<li>{e(ln[2:].strip())}</li>'
    elif ln.startswith(("PHÁN QUYẾT","4 SỬA","Dissent","Nền đúng")):
        if "<ul" in syn_html and "</ul>" not in syn_html[-6:]: syn_html+="</ul>"
        syn_html+=f'<p class="synhead">{e(ln)}</p><ul class="synlist">'
    else:
        syn_html+=f'<p>{e(ln)}</p>'
syn_html+="</ul>"

warn = "" if verified else ('<div class="warn"><b>⚠️ verified: false</b> — model identities đã quarantine trong council.config.yaml. '
 'Đây là <b>consensus mean-rank</b>, không phải chân lý. Đọc Đề-xuất-sửa của từng ghế trước khi trích.</div>')

FAV = ("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
       "<rect width='32' height='32' rx='7' fill='%23232028'/>"
       "<path d='M8 22h16M16 7l7 5H9z' stroke='%23c9a24b' stroke-width='2' fill='none' stroke-linejoin='round'/></svg>")

PAGE = f'''<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Council Stage-4 report — blind peer-rank của hội đồng persona đánh giá skill council. Deterministic từ council.transcript.json.">
<title>Council · báo cáo Stage-4</title>
<link rel="icon" href="{FAV}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Outfit:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root{{
 --paper:#f4f1ea;--ink:#26221c;--dim:#7a7266;--faint:#a79e90;
 --line:rgba(60,52,40,.13);--card:rgba(255,253,249,.72);--stroke:rgba(255,255,255,.9);
 --accent:#8a6d2f;              /* single global accent — muted brass */
 --shadow:24px 40px 24px rgba(60,48,28,.10);
 --plum:#7a5c86;--teal:#3f7d74;--amber:#b06a2c;   /* desaturated persona data-hues */
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;font:15px/1.6 "Outfit",system-ui,sans-serif;color:var(--ink);background:var(--paper);
 background-image:radial-gradient(120% 80% at 15% -5%,rgba(214,198,160,.35),transparent 55%),
   radial-gradient(90% 70% at 100% 0%,rgba(150,168,178,.22),transparent 50%);
 min-height:100dvh;-webkit-font-smoothing:antialiased}}
body::after{{content:"";position:fixed;inset:0;pointer-events:none;z-index:99;opacity:.5;mix-blend-mode:multiply;
 background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.045'/%3E%3C/svg%3E")}}
.wrap{{max-width:940px;margin:0 auto;padding:56px 22px 96px}}
.tabnum{{font-variant-numeric:tabular-nums}}
header.hero{{margin-bottom:30px}}
.eyebrow{{font:600 12px/1 "JetBrains Mono",monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}}
h1{{font-family:"Fraunces",serif;font-weight:600;font-size:clamp(30px,5vw,46px);line-height:1.02;letter-spacing:-.02em;margin:12px 0 10px;text-wrap:balance;max-width:22ch}}
.q{{color:var(--dim);font-size:16px;max-width:60ch;text-wrap:pretty}}
.meta{{margin-top:14px;font:500 12.5px/1 "JetBrains Mono",monospace;color:var(--faint);letter-spacing:.02em}}
.warn{{display:flex;gap:11px;background:rgba(176,106,44,.09);border:1px solid rgba(176,106,44,.32);border-left:3px solid var(--amber);
 border-radius:13px;padding:14px 16px;margin:26px 0 8px;font-size:13.5px;color:#5f4a2e}}
.sect{{margin:46px 0 18px;display:flex;align-items:baseline;gap:14px}}
.sect .n{{font-family:"Fraunces",serif;font-size:26px;color:var(--accent);line-height:1}}
.sect h2{{font-family:"Fraunces",serif;font-weight:500;font-size:21px;margin:0;letter-spacing:-.01em}}
.sect .rule{{flex:1;height:1px;background:var(--line)}}
.pcard{{background:var(--card);backdrop-filter:blur(14px) saturate(1.3);-webkit-backdrop-filter:blur(14px) saturate(1.3);
 border:1px solid var(--stroke);border-radius:20px;padding:22px 24px;margin:18px 0;position:relative;overflow:hidden;
 box-shadow:0 1px 0 rgba(255,255,255,.7) inset,var(--shadow);transition:transform .28s cubic-bezier(.2,.7,.2,1),box-shadow .28s}}
.pcard::before{{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--ac)}}
.pcard:hover{{transform:translateY(-3px);box-shadow:0 1px 0 rgba(255,255,255,.8) inset,32px 54px 30px rgba(60,48,28,.14)}}
.phead{{display:flex;align-items:center;gap:14px;margin-bottom:14px}}
.pav{{width:46px;height:46px;border-radius:14px;color:#fff;font-family:"Fraunces",serif;font-weight:600;font-size:20px;display:grid;place-items:center;flex:0 0 46px;box-shadow:0 6px 14px -4px var(--ac)}}
.pname{{font-family:"Fraunces",serif;font-size:19px;font-weight:600;letter-spacing:-.01em}}
.rankpill{{font:600 11.5px/1 "JetBrains Mono",monospace;color:var(--dim);margin-left:6px}}
.plens{{font-size:12.5px;color:var(--dim);margin-top:2px}}
.blindtag{{margin-left:auto;align-self:flex-start;font:600 11px/1 "JetBrains Mono",monospace;color:var(--ac);
 border:1px solid var(--ac);border-radius:7px;padding:5px 9px;letter-spacing:.03em}}
.verdict-line{{background:rgba(255,255,255,.55);border:1px solid var(--line);border-radius:12px;padding:11px 14px;font-size:14px;font-weight:600;margin-bottom:16px}}
.cols{{display:grid;grid-template-columns:1.15fr .85fr;gap:26px}}
@media(max-width:640px){{.cols{{grid-template-columns:1fr;gap:18px}}}}
h4{{margin:0 0 10px;font:600 11px/1 "JetBrains Mono",monospace;text-transform:uppercase;letter-spacing:.09em;color:var(--faint)}}
ul.risks{{list-style:none;margin:0;padding:0}}
ul.risks li{{display:flex;gap:11px;margin-bottom:13px}}
.rk{{width:21px;height:21px;border-radius:7px;color:#fff;font:700 11.5px/1 "JetBrains Mono",monospace;display:grid;place-items:center;flex:0 0 21px;margin-top:1px;background:var(--ac)}}
ul.risks b{{font-size:13.5px}} ul.risks p{{margin:3px 0 0;font-size:12.5px;color:var(--dim);line-height:1.5}}
ul.fixes{{margin:0;padding:0;list-style:none;counter-reset:f}}
ul.fixes li{{position:relative;padding-left:22px;margin-bottom:10px;font-size:13px;line-height:1.5}}
ul.fixes li::before{{counter-increment:f;content:"→";position:absolute;left:0;color:var(--ac);font-weight:700}}
.tblwrap{{border:1px solid var(--line);border-radius:16px;overflow:hidden;background:rgba(255,253,249,.6);box-shadow:var(--shadow)}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}
th,td{{text-align:left;padding:12px 15px;border-bottom:1px solid var(--line)}}
tbody tr:last-child td{{border-bottom:0}}
tbody tr{{transition:background .18s}} tbody tr:hover{{background:rgba(138,109,47,.06)}}
th{{color:var(--faint);font:600 11px/1 "JetBrains Mono",monospace;text-transform:uppercase;letter-spacing:.06em;background:rgba(60,52,40,.03)}}
.mono{{font-family:"JetBrains Mono",monospace;font-variant-numeric:tabular-nums}} .dim{{color:var(--dim)}}
.chip{{display:inline-flex;align-items:center;gap:6px;background:color-mix(in srgb,var(--c) 12%,var(--paper));border:1px solid color-mix(in srgb,var(--c) 55%,transparent);
 color:var(--c);border-radius:9px;padding:5px 11px;margin:9px 8px 0 0;font-size:12.5px;font-weight:600;transition:transform .2s}}
.chip:hover{{transform:translateY(-2px)}}
.chip::before{{content:"";width:8px;height:8px;border-radius:50%;background:var(--c)}}
.kpi{{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin:0 0 18px}}
@media(max-width:640px){{.kpi{{grid-template-columns:1fr}}}}
.kpi div{{background:var(--card);border:1px solid var(--stroke);border-radius:16px;padding:16px 18px;box-shadow:var(--shadow);transition:transform .26s}}
.kpi div:hover{{transform:translateY(-3px)}}
.kpi b{{display:block;font-family:"Fraunces",serif;font-size:22px;font-weight:600;margin:5px 0 3px;letter-spacing:-.01em}}
.kpi span{{color:var(--faint);font:600 10.5px/1 "JetBrains Mono",monospace;text-transform:uppercase;letter-spacing:.07em}}
.kpi em{{font-style:normal;color:var(--dim);font-size:12px}}
.synth{{background:linear-gradient(158deg,rgba(138,109,47,.10),rgba(63,125,116,.06));border:1px solid rgba(138,109,47,.26);
 border-radius:20px;padding:24px 26px;margin-top:16px;box-shadow:var(--shadow)}}
.synth .lbl{{font:600 11px/1 "JetBrains Mono",monospace;text-transform:uppercase;letter-spacing:.09em;color:var(--accent)}}
.synhead{{font-family:"Fraunces",serif;font-weight:600;margin:16px 0 6px;font-size:15px}} .synth p{{margin:7px 0;font-size:13.5px;line-height:1.6}}
ul.synlist{{margin:6px 0 10px;padding:0;list-style:none;counter-reset:s}}
ul.synlist li{{position:relative;padding-left:26px;margin-bottom:8px;font-size:13.5px;line-height:1.55}}
ul.synlist li::before{{counter-increment:s;content:counter(s);position:absolute;left:0;top:0;width:18px;height:18px;border-radius:6px;
 background:var(--accent);color:#fff;font:700 11px/18px "JetBrains Mono",monospace;text-align:center}}
.reveal{{margin-top:16px}} .reveal .lbl{{font:600 11px/1 "JetBrains Mono",monospace;text-transform:uppercase;letter-spacing:.06em;color:var(--faint)}}
footer{{margin-top:40px;padding-top:20px;border-top:1px solid var(--line);color:var(--faint);font-size:12.5px;text-align:center}}
a:focus-visible,tr:focus-visible{{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}}
</style></head><body><div class="wrap">

<header class="hero">
  <div class="eyebrow">🏛 Council · Stage-4</div>
  <h1>Hội đồng chấm mù skill council</h1>
  <p class="q">{e(T.get("question") or "Đánh giá tính năng Stage-4 HTML report của skill council — thiết kế, opt-in, rủi ro, giữ/sửa/bỏ.")}</p>
  <div class="meta tabnum">seed {e(seed)} · council.py/1.0 · {len(jr)} giám khảo · {len(order)} ghế</div>
</header>
{warn}

<section><div class="sect"><span class="n tabnum">1</span><h2>Ý kiến hội đồng</h2><span class="rule"></span></div>
{cards}
</section>

<section><div class="sect"><span class="n tabnum">2</span><h2>Bỏ phiếu kín</h2><span class="rule"></span></div>
<div class="tblwrap"><table><thead><tr><th>Giám khảo</th><th>Ranking (nhãn ẩn)</th><th>Thứ tự trình bày · anchor guard</th></tr></thead><tbody>{vote_rows}</tbody></table></div>
<div class="reveal"><span class="lbl">Reveal map — chỉ lộ ở cuối</span><br>{reveal}</div>
</section>

<section><div class="sect"><span class="n tabnum">3</span><h2>Dashboard chốt</h2><span class="rule"></span></div>
<div class="kpi">
 <div><span>Winner</span><b>{MEDAL[1]} {e(SEATS[winner["author"]]["name"])}</b><em class="tabnum">blind {e(winner["label"])} · mean {e(winner["mean_rank"])}</em></div>
 <div><span>Most contested</span><b>{e(SEATS[contested["author"]]["name"])}</b><em class="tabnum">blind {e(contested["label"])} · var {e(contested["variance"])}</em></div>
 <div><span>Đồng thuận</span><b class="tabnum">{len(jr)} giám khảo</b><em>{"nhất trí tuyệt đối ✓" if unan else "phân hoá ✗"}</em></div>
</div>
<div class="tblwrap"><table><thead><tr><th>Blind</th><th>Ghế</th><th>Mean rank</th><th>Judge ranks</th></tr></thead><tbody>{dash}</tbody></table></div>
<div class="synth"><span class="lbl">Chairman synthesis — câu trả lời chốt</span>{syn_html}</div>
</section>

<footer>Mọi số liệu lấy từ <span class="mono">council.transcript.json</span> — report chỉ là lớp trình bày, không thêm phán xét mới.</footer>
</div></body></html>'''
out = run / "council.report.html"
out.write_text(PAGE, encoding="utf-8")
print(f"wrote {out} ({len(PAGE)} bytes)")
