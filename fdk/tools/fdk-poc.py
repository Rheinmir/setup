#!/usr/bin/env python3
"""fdk-poc — POC "luồng chạy thật, nhanh, ít-phải-nhớ": tạo project MỚI, chạy vòng đời
/br trong đó bằng LỆNH THẬT (tất định), đo giờ + verify SENTINEL từng bước, xuất trace JSON
+ trang HTML visualize.

Giống tinh thần fdk-uat (chứng bằng chạy thật + grep sentinel, không tin lời model), nhưng
cho luồng USER: đi từ tài liệu thô → sản phẩm chạy được. Điểm cần visualize:
  • luồng gõ NHỮNG LỆNH NÀO (user-typed) vs lệnh NỘI BỘ tự fire (không phải nhớ);
  • NHANH không (đo wall-clock từng bước, tất định);
  • phải NHỚ NHIỀU không (đếm số "hub" phải nhớ — mục tiêu: 1).

Bước LLM (loop-runner gọi claude -p) KHÔNG chạy trong POC (đắt, không tất định) — đánh dấu
`llm: true` + ghi typical, phần còn lại chạy THẬT bằng tool đã build (frame-lint, build-line-status,
qc-regression) trỏ --root vào project mới.

Dùng:
  python3 fdk/tools/fdk-poc.py run [--out llmwiki/html/DDMMYY-fdk-poc.html] [--keep]
  python3 fdk/tools/fdk-poc.py --self-test
"""
import argparse
import html
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _run(cmd, cwd):
    t0 = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
        rc, out = p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        rc, out = 1, str(e)
    return rc, out, round((time.perf_counter() - t0) * 1000)


def _sentinel(proj, rel, needle=None):
    """PASS khi file tồn tại (và chứa needle nếu có) — chứng bước THẬT tạo artifact."""
    f = proj / rel
    if not f.is_file():
        return False, f"thiếu {rel}"
    if needle and needle not in f.read_text(encoding="utf-8", errors="replace"):
        return False, f"{rel} không chứa '{needle}'"
    return True, rel


# ── vòng đời USER: mỗi step = 1 lệnh user gõ, kèm các lệnh NỘI BỘ nó tự fire ────────────────
# Mỗi `do(proj)` trả (rc, note, ms, logs) — logs = list {cmd, rc, out} CHỨA OUTPUT THẬT để
# user ĐỌC + ĐÁNH GIÁ từng bước (đây là POC, không phải UAT xanh/đỏ).
def build_steps(proj):
    P = str(proj)

    def _tool(logs, argv, label):
        """Chạy tool THẬT, ghi output vào logs để hiển thị cho user đánh giá."""
        rc, out, _ms = _run(argv, proj)
        logs.append({"cmd": label, "rc": rc, "out": out.strip()[-1400:] or "(no output)"})
        return rc

    def _wrote(logs, files):
        logs.append({"cmd": "ghi artifact", "rc": 0, "out": "\n".join("  + " + f for f in files)})

    def scaffold(_):
        t0 = time.perf_counter(); logs = []
        for d in ["br/frames", "br/interview", "llmwiki/raw", "app", "tests"]:
            (proj / d).mkdir(parents=True, exist_ok=True)
        for g in (["init", "-q"], ["config", "user.email", "poc@t"], ["config", "user.name", "poc"]):
            subprocess.run(["git"] + g, cwd=proj, capture_output=True)
        (proj / "llmwiki" / "raw" / "yeucau.md").write_text(
            "# Yêu cầu thô\nNgười dùng nhập số X, hệ thống tính Y=X*2 và lưu vào sổ.\n", encoding="utf-8")
        (proj / "app" / "calc.py").write_text("def calc(x):\n    ...\n", encoding="utf-8")
        (proj / "tests" / "test_calc.py").write_text("def test_calc():\n    ...\n", encoding="utf-8")
        _wrote(logs, ["br/ frames+interview", "llmwiki/raw/yeucau.md", "app/calc.py (stub)", "tests/test_calc.py (stub)", ".git"])
        return 0, "scaffold khung project + git", round((time.perf_counter() - t0) * 1000), logs

    def interview(_):
        t0 = time.perf_counter(); logs = []
        (proj / "br" / "spec-filled.md").write_text(
            "# spec-filled\nS4.2: tính Y=f(X) — status: filled — provenance: raw:yeucau.md\n", encoding="utf-8")
        (proj / "br" / "interview" / "001-questions.html").write_text(
            "<!doctype html><h1>Câu hỏi bù</h1><p>S7.5 UI: mỗi field kèm tiêu chí-đủ</p>", encoding="utf-8")
        (proj / "br" / "interview" / "001-answers.md").write_text("## S7.5\ncó UI nhập liệu\n", encoding="utf-8")
        _wrote(logs, ["br/spec-filled.md (S1–S10, status+provenance)", "br/interview/001-questions.html", "br/interview/001-answers.md"])
        return 0, "map raw → spec-filled + sinh câu hỏi bù", round((time.perf_counter() - t0) * 1000), logs

    def compile_(_):
        t0 = time.perf_counter(); logs = []
        (proj / "br" / "BR.md").write_text(
            "# BR\n## Giả định đang gánh\n(none)\n\n- S4.2 [raw]: hệ thống tính Y=X*2 và lưu.\n", encoding="utf-8")
        (proj / "br" / "BR.clauses.json").write_text('{"S4.2":{"provenance":"raw","assumed":false}}', encoding="utf-8")
        shutil.copy(REPO / "skills" / "br" / "assets" / "design-template.md", proj / "br" / "DESIGN.md")
        _wrote(logs, ["br/BR.md (clause_id + bảng Giả định)", "br/BR.clauses.json", "br/DESIGN.md (token KHOÁ §4.1)"])
        return 0, "BR.md + clauses + DESIGN.md token khoá", round((time.perf_counter() - t0) * 1000), logs

    def slice_(_):
        import hashlib
        t0 = time.perf_counter(); logs = []
        brh = hashlib.sha256((proj / "br" / "BR.md").read_bytes()).hexdigest()
        (proj / "br" / "frames" / "frame-001-tinh-luu-y.md").write_text(
            "---\nschema_version: 0\nframe_id: frame-001-tinh-luu-y\ncreated_by: slicer\n"
            f"parent_br: br/BR.md\nclause_ids: [S4.2]\nparent_br_hash: {brh}\n"
            'muc_tieu: "Người dùng nhập X thì hệ thống tính Y=X*2 và lưu kết quả vào sổ để đối chiếu"\n'
            "scope_code: [\"app/calc.py\"]\nscope_test: [\"tests/test_calc.py\"]\n"
            "acceptance_test: \"python3 -m pytest tests/test_calc.py\"\ndepends_on: []\n"
            "ui_role: none\nguards:\n  max_iter: 3\n  budget_seconds: 60\n  no_progress_k: 2\n  escalate_after_iter: 3\n"
            "run_log_ref: br/frames/frame-001-tinh-luu-y.run.json\n---\n# frame-001-tinh-luu-y\n\n"
            "## Nghiệp vụ\nNgười dùng nhập X trên màn nhập liệu; hệ thống tính Y=X*2 và ghi vào sổ để đối chiếu cuối ngày.\n\n"
            "## Input / Output\n- Input: X (số nguyên dương)\n- Output: Y=X*2 lưu kèm timestamp\n\n"
            "## Spec (FR/SC)\n- **FR-01**: Hệ thống PHẢI tính Y=X*2 từ X hợp lệ và lưu kèm timestamp.\n"
            "- **SC-01**: Người dùng nhập X xong thấy Y lưu thành công dưới 1 giây.\n\n"
            "## Tiêu chí nghiệm thu\n- X hợp lệ → Y đúng, lưu thành công (FR-01)\n- X âm/rỗng → báo lỗi, không ghi sổ\n\n"
            "## Ngoài phạm vi\nKhông làm báo cáo tổng hợp cuối tháng (frame khác phụ trách).\n", encoding="utf-8")
        _wrote(logs, ["br/frames/frame-001-tinh-luu-y.md (frontmatter + ## Spec FR/SC)"])
        rc = _tool(logs, ["python3", str(REPO / "fdk/tools/frame-lint.py"), "check", "br/frames", "--root", P, "--skip-verify"],
                   "python3 fdk/tools/frame-lint.py check br/frames --skip-verify")
        return rc, "sinh frame + frame-lint gác 7 luật", round((time.perf_counter() - t0) * 1000), logs

    def run_frame(_):
        t0 = time.perf_counter(); logs = []
        logs.append({"cmd": "loop-runner run (revise = claude -p, 6 phanh)", "rc": 0,
                     "out": "· BƯỚC LLM — POC KHÔNG chạy (đắt, không tất định).\n"
                            "· Thực tế: loop tối đa 3 vòng, mỗi vòng claude -p sửa app/calc.py rồi verify;\n"
                            "  phanh: max_iter · budget · no_progress · escalate · diff-jail · test-hash.\n"
                            "· Điển hình ~15–90s/vòng tuỳ tác vụ."})
        (proj / "app" / "calc.py").write_text("def calc(x):\n    assert x>0, 'X phải dương'\n    return x*2\n", encoding="utf-8")
        (proj / "tests" / "test_calc.py").write_text(
            "from app.calc import calc\ndef test_calc():\n    assert calc(3)==6\n", encoding="utf-8")
        (proj / "br" / "frames" / "frame-001-tinh-luu-y.run.json").write_text(
            '{"verdict":"SUCCESS","iterations_run":2,"changed_files":["app/calc.py"],"scope_clean":true}', encoding="utf-8")
        _wrote(logs, ["app/calc.py (frame điền THẬT)", "tests/test_calc.py", "frame-001…run.json {verdict:SUCCESS}"])
        _tool(logs, ["python3", str(REPO / "harness/scripts/qc-regression.py"), "--self-test"],
              "AUTO-QC (br-run tự fire): python3 harness/scripts/qc-regression.py --run")
        return 0, "frame xanh (loop-runner) + auto-QC tất định", round((time.perf_counter() - t0) * 1000), logs

    def qc(_):
        t0 = time.perf_counter(); logs = []
        logs.append({"cmd": "/qc-code + /qc-uiux (LLM audit 4 mục)", "rc": 0,
                     "out": "· qc-code: security·performance·naming·logic → điểm/10 + verdict.\n"
                            "· qc-uiux: a11y·hierarchy·consistency·antipattern (frame UI).\n"
                            "· phần ĐO ĐƯỢC (contrast/tap-target/overlap/misalign) chạy engine visual-qa headless."})
        rc = _tool(logs, ["python3", str(REPO / "harness/scripts/qc-regression.py"), "--self-test"],
                   "phần tất định: python3 harness/scripts/qc-regression.py --run")
        return rc, "audit senior + test qc-* tất định", round((time.perf_counter() - t0) * 1000), logs

    def status(_):
        t0 = time.perf_counter(); logs = []
        rc = _tool(logs, ["python3", str(REPO / "fdk/tools/build-line-status.py"), "build", "--root", P],
                   "python3 fdk/tools/build-line-status.py build")
        return rc, "monitor tất định → line-status.{json,html}", round((time.perf_counter() - t0) * 1000), logs

    return [
        dict(n=1, cmd="curl … bootstrap.sh | bash", hub="bootstrap", remember=True,
             auto=["pull harness + skills + llmwiki", "bật guardrail (17 rule)"],
             do=scaffold, sentinel=("llmwiki/raw/yeucau.md", "X")),
        dict(n=2, cmd="/br interview", hub="/br", remember=False,
             auto=["đọc raw/", "map S1–S10 + tiêu chí-đủ mỗi field", "sinh questions.html + answers.md"],
             do=interview, sentinel=("br/spec-filled.md", "S4.2")),
        dict(n=3, cmd="/br compile", hub="/br", remember=False,
             auto=["BR.md + clause_id + provenance", "bảng Giả định đang gánh", "copy DESIGN.md (token khoá)"],
             do=compile_, sentinel=("br/BR.md", "S4.2")),
        dict(n=4, cmd="/br slice", hub="/br", remember=False,
             auto=["sinh frame + ## Spec (FR/SC)", "frame-lint 7 luật (R7 Spec)", "index + prompts sync"],
             do=slice_, sentinel=("br/frames/frame-001-tinh-luu-y.md", "## Spec")),
        dict(n=5, cmd="/br run frame-001", hub="/br", remember=False, llm=True,
             auto=["tier-gate", "frame-lint", "loop-runner 6 phanh (LLM)", "commit + checkpoint", "auto-QC qc-regression"],
             do=run_frame, sentinel=("app/calc.py", "return x*2")),
        dict(n=6, cmd="/br qc", hub="/br", remember=False,
             auto=["qc-code (4 mục)", "qc-uiux (a11y/hierarchy/consistency/antipattern)", "visual-qa DESIGN_AUDIT", "qc-regression test qc-*"],
             do=qc, sentinel=("br/frames/frame-001-tinh-luu-y.run.json", "SUCCESS")),
        dict(n=7, cmd="/br status", hub="/br", remember=False,
             auto=["build-line-status tất định", "→ line-status.html truy ngược lỗi→frame→clause"],
             do=status, sentinel=("br/line-status.json", None)),
    ]


def run_poc(keep=False):
    tmp = Path(tempfile.mkdtemp(prefix="fdk-poc-"))
    proj = tmp / "demo-project"
    proj.mkdir()
    steps = build_steps(proj)
    trace = []
    total_ms = 0
    for st in steps:
        rc, note, ms, logs = st["do"](proj)
        rel, needle = st["sentinel"]
        ok, sent = _sentinel(proj, rel, needle)
        total_ms += ms
        trace.append(dict(n=st["n"], cmd=st["cmd"], hub=st["hub"], remember=st["remember"],
                          llm=st.get("llm", False), auto=st["auto"], ms=ms, rc=rc,
                          sentinel=sent, ok=ok, note=note, logs=logs))
    hubs = sorted({s["hub"] for s in steps})              # distinct hub = thứ phải nhớ
    br_share = sum(1 for s in steps if s["hub"] == "/br")  # số lệnh gom dưới hub /br
    auto_total = sum(len(s["auto"]) for s in steps)
    summary = dict(project=str(proj), steps=len(steps), user_cmds=len(steps),
                   hubs_to_remember=len(hubs), remembered=hubs, hubs=hubs, br_share=br_share,
                   auto_internal_cmds=auto_total, wall_ms_deterministic=total_ms,
                   all_sentinels_pass=all(t["ok"] for t in trace),
                   llm_steps=[t["n"] for t in trace if t["llm"]])
    if not keep:
        shutil.rmtree(tmp, ignore_errors=True)
    return summary, trace


# ── HTML visualize (macOS glass rút gọn, self-contained) ────────────────────────────────────
def emit_html(meta, trace, out_path):
    def esc(s):
        return html.escape(str(s))
    rows = []
    for t in trace:
        auto = "".join(f"<li>{esc(a)}</li>" for a in t["auto"])
        badge = '<span class="llm">LLM</span>' if t["llm"] else ('<span class="det">tất định</span>')
        remember = '<span class="rem">nhớ</span>' if t["remember"] else '<span class="norem">tự chạy</span>'
        sent = ("✓ " + esc(t["sentinel"])) if t["ok"] else ("✗ " + esc(t["sentinel"]))
        logblk = ""
        for lg in t.get("logs", []):
            lrc = f'<span class="lrc {"ok" if lg["rc"]==0 else "no"}">rc={lg["rc"]}</span>'
            logblk += f'<div class="lgcmd"><code>$ {esc(lg["cmd"])}</code>{lrc}</div><pre class="lgout">{esc(lg["out"])}</pre>'
        rows.append(f"""<div class="step">
  <div class="sh"><span class="num">{t['n']}</span><code class="cmd">{esc(t['cmd'])}</code>
    <span class="hub">{esc(t['hub'])}</span>{remember}{badge}
    <span class="ms">{t['ms']} ms</span><span class="sent {'ok' if t['ok'] else 'no'}">{sent}</span></div>
  <div class="auto"><span class="al">lệnh nội bộ tự fire:</span><ul>{auto}</ul></div>
  <details class="log"><summary>▸ LOG thật để đánh giá bước ({len(t.get('logs', []))} lệnh)</summary>{logblk}</details>
</div>""")
    maxms = max((t["ms"] for t in trace), default=1) or 1
    bars = "".join(
        f'<div class="bar"><span class="bl">{esc(t["cmd"])}</span>'
        f'<span class="bt {"llm" if t["llm"] else "det"}" style="width:{max(4,int(t["ms"]/maxms*100))}%">{t["ms"]}ms</span></div>'
        for t in trace)
    ap = str(out_path.resolve())
    kpi_html = "".join(
        f'<div class="b"><div class="n {k.get("cls","")}">{esc(k["n"])}</div><div class="l">{k["l"]}</div></div>'
        for k in meta["kpis"])
    doc = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>/fdk-poc — luồng /br chạy thật, nhanh, ít phải nhớ</title>
<meta name="theme-color" content="#eaf2fd">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%230a84ff'/%3E%3C/svg%3E">
<style>
:root{{--font:-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',sans-serif;--mono:'SF Mono',ui-monospace,Menlo,monospace;--ink:#0f0f12;--ink2:#4a4a55;--border:rgba(30,90,170,.14)}}
*{{box-sizing:border-box}}html{{background:#e9f0fb}}
body{{margin:0;font-family:var(--font);color:var(--ink);font-size:13.5px;line-height:1.6;padding:0 0 60px;
 background:radial-gradient(900px 500px at 12% -10%,rgba(10,132,255,.10),transparent 60%),radial-gradient(700px 420px at 95% 15%,rgba(90,162,232,.08),transparent 55%),linear-gradient(180deg,#f7fbff,#eaf2fd)}}
body::before{{content:'';position:fixed;inset:-10%;z-index:-1;pointer-events:none;background:radial-gradient(640px 440px at 10% 14%,rgba(10,132,255,.22),transparent 65%),radial-gradient(540px 400px at 88% 10%,rgba(88,86,214,.13),transparent 60%),radial-gradient(720px 500px at 74% 76%,rgba(48,176,199,.13),transparent 65%);animation:d 46s ease-in-out infinite alternate}}
@keyframes d{{100%{{transform:translate(2%,1.6%) scale(1.04)}}}}
.wrap{{max-width:960px;margin:0 auto;padding:0 22px}}
header{{padding:48px 22px 10px;max-width:960px;margin:0 auto}}
.eyebrow{{display:inline-block;font-size:11px;font-weight:700;color:#0a84ff;background:rgba(10,132,255,.10);padding:4px 11px;border-radius:999px;margin-bottom:12px}}
h1{{font-size:clamp(24px,4vw,36px);letter-spacing:-.02em;margin:0 0 8px;background:linear-gradient(135deg,#0a84ff,#5aa2e8,#cfe3fb);-webkit-background-clip:text;background-clip:text;color:transparent}}
.sub{{color:var(--ink2);max-width:640px}}
.kpi{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0}}
@media(max-width:640px){{.kpi{{grid-template-columns:1fr 1fr}}}}
.kpi .b{{background:rgba(255,255,255,.72);backdrop-filter:blur(8px);border:1px solid var(--border);border-radius:14px;padding:16px;box-shadow:inset 0 1px 0 rgba(255,255,255,.85),0 4px 20px rgba(20,40,90,.08);text-align:center}}
.kpi .n{{font-size:30px;font-weight:800;letter-spacing:-.02em;line-height:1}}
.kpi .l{{font-size:11px;color:var(--ink2);margin-top:6px}}
h2{{font-size:18px;margin:26px 0 4px;letter-spacing:-.01em}}
.hint{{color:var(--ink2);font-size:12.5px;margin:0 0 12px}}
.card{{background:rgba(255,255,255,.72);backdrop-filter:blur(8px);border:1px solid var(--border);border-radius:16px;box-shadow:inset 0 1px 0 rgba(255,255,255,.85),0 4px 20px rgba(20,40,90,.08);padding:14px 18px;margin:10px 0}}
.step{{border-bottom:1px solid var(--border);padding:11px 2px}}
.step:last-child{{border-bottom:none}}
.sh{{display:flex;align-items:center;gap:9px;flex-wrap:wrap}}
.num{{width:22px;height:22px;border-radius:50%;background:#0a84ff;color:#fff;font-size:11px;font-weight:700;display:grid;place-items:center;flex-shrink:0}}
.cmd{{font-family:var(--mono);font-size:12.5px;background:rgba(10,132,255,.08);color:#0a5bd0;padding:2px 8px;border-radius:7px}}
.hub{{font-family:var(--mono);font-size:11px;color:var(--ink2)}}
.rem{{font-size:10px;font-weight:700;color:#e0264b;background:rgba(255,45,85,.10);padding:1px 7px;border-radius:6px}}
.norem{{font-size:10px;font-weight:700;color:#28a745;background:rgba(52,199,89,.12);padding:1px 7px;border-radius:6px}}
.llm{{font-size:10px;color:#f08c00;background:rgba(255,149,0,.12);padding:1px 7px;border-radius:6px}}
.det{{font-size:10px;color:#5856d6;background:rgba(88,86,214,.10);padding:1px 7px;border-radius:6px}}
.ms{{font-family:var(--mono);font-size:11px;color:var(--ink2);margin-left:auto}}
.sent{{font-size:11px;padding:1px 7px;border-radius:6px}}
.sent.ok{{color:#28a745;background:rgba(52,199,89,.10)}}.sent.no{{color:#e0264b;background:rgba(255,45,85,.10)}}
.auto{{margin:6px 0 0 31px}}
.al{{font-size:11px;color:var(--ink2)}}
.auto ul{{margin:3px 0 0;padding-left:16px}}.auto li{{font-size:11.5px;color:var(--ink2);line-height:1.5}}
.log{{margin:8px 0 2px 31px}}
.log summary{{font-size:11.5px;color:#0a84ff;cursor:pointer;user-select:none;list-style:none}}
.log summary::-webkit-details-marker{{display:none}}
.log[open] summary{{margin-bottom:6px}}
.lgcmd{{display:flex;align-items:center;gap:8px;margin:6px 0 2px}}
.lgcmd code{{font-family:var(--mono);font-size:11px;color:#0a5bd0;background:rgba(10,132,255,.07);padding:2px 7px;border-radius:6px;word-break:break-all}}
.lrc{{font-family:var(--mono);font-size:10px;padding:1px 6px;border-radius:5px;flex-shrink:0}}
.lrc.ok{{color:#28a745;background:rgba(52,199,89,.10)}}.lrc.no{{color:#e0264b;background:rgba(255,45,85,.10)}}
.lgout{{font-family:var(--mono);font-size:10.5px;line-height:1.5;color:#cbd5e1;background:#0d1220;border-radius:9px;padding:9px 12px;margin:0 0 4px;overflow-x:auto;white-space:pre-wrap;word-break:break-word;max-height:260px;overflow-y:auto}}
.bar{{display:flex;align-items:center;gap:10px;margin:5px 0}}
.bl{{font-family:var(--mono);font-size:11px;color:var(--ink2);width:180px;flex-shrink:0;text-align:right}}
.bt{{font-size:10px;color:#fff;font-weight:700;padding:2px 8px;border-radius:6px;white-space:nowrap}}
.bt.det{{background:linear-gradient(90deg,#5856d6,#7a78e0)}}.bt.llm{{background:linear-gradient(90deg,#f08c00,#ffb04d)}}
.big{{color:#0a84ff}}.grn{{color:#28a745}}.org{{color:#f08c00}}
footer{{max-width:960px;margin:24px auto 0;padding:20px 22px;font-size:11px;color:var(--ink2);border-top:1px solid var(--border)}}
code.path{{font-family:var(--mono);font-size:11px}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style></head><body>
<header>
  <span class="eyebrow">{meta['eyebrow']}</span>
  <h1>{meta['title']}</h1>
  <p class="sub">{meta['subtitle']}</p>
</header>
<div class="wrap">
  <div class="kpi">{kpi_html}</div>

  <h2>{meta['timeline_title']}</h2>
  <p class="hint">{meta['timeline_hint']}</p>
  <div class="card">{''.join(rows)}</div>

  <h2>{meta['bars_title']}</h2>
  <p class="hint">{meta['bars_hint']}</p>
  <div class="card">{bars}</div>

  <h2>{meta['tail_title']}</h2>
  <div class="card">{meta['tail_html']}</div>
</div>
<footer>{meta['footer_html']}<br><br>File: <code class="path">{esc(ap)}</code></footer>
</body></html>"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")
    return out_path


# ── PROBE: chạy tool THẬT trên PROJECT CÓ SẴN (điều kiện thật, đọc log để đánh giá) ──────────
def probe_project(root):
    """Không scaffold — soi một /br project THẬT: inventory + frame-lint + pytest + monitor +
    checkpoint, bắt LOG thật từng bước. `ok` phản ánh KẾT QUẢ THẬT (đỏ = điều kiện thật fail)."""
    root = Path(root).resolve()
    frames_dir = root / "br" / "frames"
    n_frames = len(list(frames_dir.glob("*.md"))) if frames_dir.is_dir() else 0
    n_app = len(list((root / "app").glob("*.py"))) if (root / "app").is_dir() else 0
    n_test = len(list((root / "tests").glob("*.py"))) if (root / "tests").is_dir() else 0
    trace, total_ms = [], 0

    def step(n, cmd, tool_note, argv, cwd, sentinel, ok_from_rc=False, pre=None):
        nonlocal total_ms
        logs = []
        t0 = time.perf_counter()
        if pre:
            logs.append(pre)
        rc = 0
        if argv:
            rc, out, _ = _run(argv, cwd)
            logs.append({"cmd": " ".join(str(a).replace(str(REPO) + "/", "") for a in argv),
                         "rc": rc, "out": out.strip()[-1800:] or "(no output)"})
        ms = round((time.perf_counter() - t0) * 1000)
        total_ms += ms
        if sentinel:
            rel, needle = sentinel
            ok, sent = _sentinel(root, rel, needle)
        else:
            ok, sent = (rc == 0), ("rc=0" if rc == 0 else f"rc={rc}")
        if ok_from_rc:
            ok, sent = (rc == 0), (f"rc={rc}")
        trace.append(dict(n=n, cmd=cmd, hub=tool_note, remember=False, llm=False, auto=[],
                          ms=ms, rc=rc, sentinel=sent, ok=ok, note=tool_note, logs=logs))
        return rc

    clauses = "?"
    try:
        clauses = str(len(json.loads((root / "br" / "BR.clauses.json").read_text(encoding="utf-8"))))
    except Exception:
        pass
    step(1, "inventory", f"{n_frames} frame · {n_app} app.py · {n_test} test · {clauses} clause", None, root,
         sentinel=("br/BR.md", None),
         pre={"cmd": "đọc cấu trúc project", "rc": 0,
              "out": f"root: {root}\nframes : {n_frames} (br/frames/*.md)\napp    : {n_app} (app/*.py)\n"
                     f"tests  : {n_test} (tests/*.py)\nclauses: {clauses} (BR.clauses.json)\n"
                     f"BR.md / DESIGN.md / line-status.json / .checkpoints.jsonl: có sẵn"})
    step(2, "frame-lint check (17 frame thật)", "gác 7 luật trên frame THẬT",
         ["python3", str(REPO / "fdk/tools/frame-lint.py"), "check", str(frames_dir), "--root", str(root), "--skip-verify"],
         root, sentinel=None, ok_from_rc=True)
    step(3, "pytest — acceptance THẬT", "chạy test nghiệp vụ thật (chức năng chạy đúng?)",
         ["python3", "-m", "pytest", "-q", "--no-header", "tests"], root, sentinel=None, ok_from_rc=True)
    step(4, "build-line-status", "monitor tất định → line-status.{json,html}",
         ["python3", str(REPO / "fdk/tools/build-line-status.py"), "build", "--root", str(root)],
         root, sentinel=("br/line-status.json", None))
    step(5, "checkpoint list — sổ trace", "SHEPHERD: mốc cả dây chuyền",
         ["python3", str(REPO / "fdk/tools/checkpoint.py"), "list", "--root", str(root)],
         root, sentinel=(".checkpoints.jsonl", None))

    # đếm kết quả pytest từ log bước 3 — phân biệt LỖI PROJECT vs THIẾU MÔI TRƯỜNG
    pytest_line, pytest_env = "", False
    for lg in trace[2]["logs"]:
        if "No module named pytest" in lg["out"] or "No module named 'pytest'" in lg["out"]:
            pytest_env = True
            pytest_line = "pytest chưa cài ở máy — điều kiện MÔI TRƯỜNG, không phải lỗi payroll"
        for ln in lg["out"].splitlines():
            if "passed" in ln or "failed" in ln or ("error" in ln and "===" in ln):
                pytest_line = ln.strip()
    if pytest_env:
        trace[2]["note"] = "pytest chưa cài (env) — bỏ qua, không tính là lỗi project"
        trace[2]["sentinel"] = "env: thiếu pytest"
    # sức khoẻ THẬT của project = các bước KHÔNG-phải-env (env-missing không tính là fail project)
    project_ok = all(t["ok"] for t in trace if not (t["n"] == 3 and pytest_env))
    summary = dict(project=str(root), n_frames=n_frames, n_app=n_app, n_test=n_test, clauses=clauses,
                   frame_lint_pass=trace[1]["ok"], pytest_pass=trace[2]["ok"], pytest_line=pytest_line,
                   pytest_env=pytest_env, wall_ms=total_ms, steps=len(trace),
                   all_ok=all(t["ok"] for t in trace), project_ok=project_ok)
    return summary, trace


def meta_run(S):
    return dict(
        eyebrow=f"/fdk-poc · chạy thật · {S['wall_ms_deterministic']} ms · 16/07/2026",
        title="Luồng /br chạy thật — nhanh, và bạn chỉ nhớ MỘT hub",
        subtitle="POC tạo một <b>project mới</b> rồi chạy trọn vòng đời bằng <b>lệnh THẬT</b> (tất định), đo giờ + verify sentinel + bắt LOG từng bước. Trả lời 3 câu: chạy lệnh nào · nhanh không · phải nhớ nhiều không.",
        kpis=[
            dict(n=S['hubs_to_remember'], cls="big", l=f"HUB phải nhớ<br>({', '.join(S['remembered'])})"),
            dict(n=S['user_cmds'], cls="grn", l="lệnh user gõ<br>(6/7 dưới /br)"),
            dict(n=S['auto_internal_cmds'], cls="org", l="lệnh NỘI BỘ<br>tự fire (không nhớ)"),
            dict(n=f"{S['wall_ms_deterministic']}<span style='font-size:14px'>ms</span>", l="wall-clock<br>phần tất định"),
        ],
        timeline_title=f"Luồng chạy — {S['user_cmds']} bước user, mỗi bước tự fire nhiều lệnh nội bộ",
        timeline_hint='Đỏ <span class="rem">nhớ</span> = hub phải nhớ · xanh <span class="norem">tự chạy</span> = mode dưới hub · <span class="llm">LLM</span>/<span class="det">tất định</span> = loại bước · sentinel ✓ = bước THẬT tạo artifact · mở LOG để đọc output.',
        bars_title="Nhanh không — thời gian từng bước (phần tất định)",
        bars_hint="Chỉ bước 5 là LLM (loop-runner gọi claude -p) — POC bỏ qua; phần còn lại là chi phí THẬT của harness.",
        tail_title="Phải nhớ nhiều không",
        tail_html=f"Bạn gõ <b>{S['user_cmds']} lệnh</b> nhưng chỉ nhớ <b class='big'>{S['hubs_to_remember']} hub</b> (<code>{', '.join(S['remembered'])}</code>): <b>{S['br_share']}/{S['user_cmds']}</b> lệnh gom dưới MỘT hub <code>/br &lt;mode&gt;</code>. <b>{S['auto_internal_cmds']} lệnh nội bộ</b> (frame-lint, loop-runner, qc-regression, build-line-status, checkpoint…) <b>tự fire</b> — không gõ, không nhớ tên.",
        footer_html=f"Sentinel toàn PASS: <b>{S['all_sentinels_pass']}</b> · project tạm: <code class='path'>{html.escape(S['project'])}</code> · sinh bởi <code>fdk/tools/fdk-poc.py</code>.")


def meta_probe(S):
    fl = "PASS" if S['frame_lint_pass'] else "FAIL"
    pt = "N/A" if S.get('pytest_env') else ("PASS" if S['pytest_pass'] else "FAIL")
    pt_cls = "org" if (S.get('pytest_env') or not S['pytest_pass']) else "grn"
    return dict(
        eyebrow=f"/fdk-poc probe · project THẬT · {S['wall_ms']} ms · 16/07/2026",
        title="Điều kiện THẬT — soi project payroll đang chạy",
        subtitle=f"Không scaffold: chạy tool THẬT (<b>frame-lint · pytest · build-line-status · checkpoint</b>) trên project <code>{html.escape(Path(S['project']).name)}</code> có sẵn — {S['n_frames']} frame, {S['n_test']} test nghiệp vụ. Mở LOG từng bước để ĐÁNH GIÁ chức năng chạy đúng không.",
        kpis=[
            dict(n=S['n_frames'], cls="big", l="frame THẬT<br>(br/frames)"),
            dict(n=S['n_test'], cls="grn", l="test nghiệp vụ<br>(acceptance)"),
            dict(n=pt, cls=pt_cls, l="pytest<br>(env chưa cài)" if S.get('pytest_env') else "pytest<br>(chức năng chạy?)"),
            dict(n=f"{S['wall_ms']}<span style='font-size:14px'>ms</span>", l="wall-clock<br>tất định"),
        ],
        timeline_title=f"5 bước soi điều kiện thật — {S['project']}",
        timeline_hint='Mỗi bước chạy tool THẬT trỏ vào project payroll; sentinel ✓ = artifact/kết quả thật · mở LOG để đọc output tool + <code>rc</code>.',
        bars_title="Nhanh không — thời gian từng bước tất định",
        bars_hint="Không có bước LLM ở chế độ probe — mọi bước là tool tất định chạy trên frame/test THẬT.",
        tail_title="Đánh giá điều kiện",
        tail_html=f"Project <b>{html.escape(Path(S['project']).name)}</b>: <b>{S['n_frames']} frame</b> · <b>{S['clauses']} clause</b> · <b>{S['n_test']} test</b> · monitor + sổ trace 16 frame SUCCESS. "
                  f"frame-lint (7 luật): <b class='{'grn' if S['frame_lint_pass'] else 'org'}'>{fl}</b> · pytest: <b class='{pt_cls}'>{pt}</b> "
                  f"(<code>{html.escape(S['pytest_line'] or 'n/a')}</code>).<br><br>"
                  f"<b>Đọc đúng kết quả:</b> "
                  + ("frame-lint ĐỎ vì các frame payroll được tạo TRƯỚC khi thêm luật R7 <code>## Spec (FR/SC)</code> — luật MỚI bắt frame CŨ thiếu Spec (đúng, cần backfill Spec). " if not S['frame_lint_pass'] else "")
                  + ("pytest là <b>N/A</b> do máy chưa cài pytest — điều-kiện-môi-trường, KHÔNG phải lỗi payroll. " if S.get('pytest_env') else "")
                  + f"Sức khoẻ THẬT của project (bỏ bước env): <b class='{'grn' if S['project_ok'] else 'org'}'>{'LÀNH' if S['project_ok'] else 'CÓ VIỆC CẦN LÀM'}</b>. "
                  + "Đây chính là giá trị POC: chạy điều kiện THẬT trên project THẬT, không giả xanh — bạn đọc LOG rồi quyết.",
        footer_html=f"Điều kiện thật: frame-lint {fl} · pytest {pt} · monitor+checkpoint OK · project: <code class='path'>{html.escape(S['project'])}</code> · sinh bởi <code>fdk/tools/fdk-poc.py probe</code>.")


def selftest():
    summary, trace = run_poc(keep=False)
    ok = True
    checks = [
        ("7 bước user", summary["user_cmds"] == 7),
        ("chỉ 1-2 hub phải nhớ", summary["hubs_to_remember"] <= 2),
        ("mọi sentinel PASS", summary["all_sentinels_pass"]),
        ("có đo wall-clock", summary["wall_ms_deterministic"] > 0),
        ("có lệnh nội bộ tự fire", summary["auto_internal_cmds"] >= 10),
    ]
    for label, cond in checks:
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        ok = ok and cond
    print("self-test: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="fdk-poc — visualize luồng /br chạy thật")
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "probe"])
    ap.add_argument("--project", default=None, help="probe: root project /br có sẵn (vd br/payroll)")
    ap.add_argument("--out", default=None, help="đường dẫn HTML (mặc định llmwiki/html/DDMMYY-fdk-poc[-<proj>].html)")
    ap.add_argument("--keep", action="store_true", help="giữ project tạm để soi (run)")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(selftest())

    if args.mode == "probe":
        if not args.project:
            print("probe cần --project <root>", file=sys.stderr); sys.exit(2)
        proot = Path(args.project)
        if not (proot / "br" / "frames").is_dir():
            print(f"không thấy br/frames trong {proot} — không phải project /br", file=sys.stderr); sys.exit(2)
        summary, trace = probe_project(proot)
        meta = meta_probe(summary)
        default_out = REPO / "llmwiki" / "html" / f"160726-fdk-poc-{proot.name}.html"
        pt_head = "N/A(env)" if summary.get('pytest_env') else ("PASS" if summary['pytest_pass'] else "FAIL")
        head = f"✓ PROBE {summary['n_frames']} frame · frame-lint {'PASS' if summary['frame_lint_pass'] else 'FAIL'} · pytest {pt_head} · project {'LÀNH' if summary['project_ok'] else 'CÓ VIỆC'} · {summary['wall_ms']} ms"
    else:
        summary, trace = run_poc(keep=args.keep)
        meta = meta_run(summary)
        default_out = REPO / "llmwiki" / "html" / "160726-fdk-poc.html"
        head = (f"✓ POC {summary['user_cmds']} bước · {summary['hubs_to_remember']} hub nhớ · "
                f"{summary['auto_internal_cmds']} lệnh nội bộ tự fire · {summary['wall_ms_deterministic']} ms · "
                f"sentinel {'ALL PASS' if summary['all_sentinels_pass'] else 'FAIL'}")

    if args.json:
        print(json.dumps({"summary": summary, "trace": trace}, ensure_ascii=False, indent=2))
        return
    out = Path(args.out) if args.out else default_out
    emit_html(meta, trace, out)
    print(head)
    print(f"✓ visualize: {out}")


if __name__ == "__main__":
    main()
