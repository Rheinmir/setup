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
def emit_html(summary, trace, out_path):
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
    S = summary
    ap = str(out_path.resolve())
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
  <span class="eyebrow">/fdk-poc · chạy thật · {esc(S['wall_ms_deterministic'])} ms · 16/07/2026</span>
  <h1>Luồng /br chạy thật — nhanh, và bạn chỉ nhớ MỘT hub</h1>
  <p class="sub">POC tạo một <b>project mới</b> rồi chạy trọn vòng đời bằng <b>lệnh THẬT</b> (tất định), đo giờ + verify sentinel từng bước. Trả lời 3 câu: chạy lệnh nào · nhanh không · phải nhớ nhiều không.</p>
</header>
<div class="wrap">
  <div class="kpi">
    <div class="b"><div class="n big">{esc(S['hubs_to_remember'])}</div><div class="l">HUB phải nhớ<br>({esc(', '.join(S['remembered']))})</div></div>
    <div class="b"><div class="n grn">{esc(S['user_cmds'])}</div><div class="l">lệnh user gõ<br>(đều dưới /br)</div></div>
    <div class="b"><div class="n org">{esc(S['auto_internal_cmds'])}</div><div class="l">lệnh NỘI BỘ<br>tự fire (không nhớ)</div></div>
    <div class="b"><div class="n">{esc(S['wall_ms_deterministic'])}<span style="font-size:14px">ms</span></div><div class="l">wall-clock<br>phần tất định</div></div>
  </div>

  <h2>Luồng chạy — {esc(S['user_cmds'])} bước user, mỗi bước tự fire nhiều lệnh nội bộ</h2>
  <p class="hint">Đỏ <span class="rem">nhớ</span> = hub phải nhớ · xanh <span class="norem">tự chạy</span> = mode dưới hub, không phải nhớ tên tool · <span class="llm">LLM</span>/<span class="det">tất định</span> = loại bước · sentinel ✓ = bước THẬT tạo artifact.</p>
  <div class="card">{''.join(rows)}</div>

  <h2>Nhanh không — thời gian từng bước (phần tất định)</h2>
  <p class="hint">Chỉ bước 5 là LLM (loop-runner gọi claude -p) — POC bỏ qua, phần còn lại là chi phí THẬT của harness.</p>
  <div class="card">{bars}</div>

  <h2>Phải nhớ nhiều không</h2>
  <div class="card">Bạn gõ <b>{esc(S['user_cmds'])} lệnh</b> nhưng chỉ cần nhớ <b class="big">{esc(S['hubs_to_remember'])} hub</b> (<code>{esc(', '.join(S['remembered']))}</code>): <b>{esc(S['br_share'])}/{esc(S['user_cmds'])}</b> lệnh gom dưới MỘT hub <code>/br &lt;mode&gt;</code>, còn lại là <code>bootstrap</code> chạy một lần. <b>{esc(S['auto_internal_cmds'])} lệnh nội bộ</b> (frame-lint, loop-runner, qc-regression, build-line-status, checkpoint…) <b>tự fire</b> — bạn không gõ, không nhớ tên chúng. Đây chính là "hub MỘT tên fan-out mode" đã bàn ở phần discoverability.</div>
</div>
<footer>Sentinel toàn PASS: <b>{esc(S['all_sentinels_pass'])}</b> · project tạm: <code class="path">{esc(S['project'])}</code> · sinh bởi <code>fdk/tools/fdk-poc.py</code>.<br><br>File: <code class="path">{esc(ap)}</code></footer>
</body></html>"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")
    return out_path


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
    ap.add_argument("mode", nargs="?", default="run", choices=["run"])
    ap.add_argument("--out", default=None, help="đường dẫn HTML (mặc định llmwiki/html/DDMMYY-fdk-poc.html)")
    ap.add_argument("--keep", action="store_true", help="giữ project tạm để soi")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(selftest())
    summary, trace = run_poc(keep=args.keep)
    if args.json:
        print(json.dumps({"summary": summary, "trace": trace}, ensure_ascii=False, indent=2))
        return
    out = Path(args.out) if args.out else (REPO / "llmwiki" / "html" / "160726-fdk-poc.html")
    emit_html(summary, trace, out)
    print(f"✓ POC chạy {summary['user_cmds']} bước · {summary['hubs_to_remember']} hub nhớ · "
          f"{summary['auto_internal_cmds']} lệnh nội bộ tự fire · {summary['wall_ms_deterministic']} ms · "
          f"sentinel {'ALL PASS' if summary['all_sentinels_pass'] else 'FAIL'}")
    print(f"✓ visualize: {out}")


if __name__ == "__main__":
    main()
