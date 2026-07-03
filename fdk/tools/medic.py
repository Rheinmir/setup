#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""medic — CỔNG SỨC KHOẺ TỔNG / tuyến phòng thủ cuối của framework overstack.

Gõ `medic`, xanh = hệ khoẻ. MỘT lệnh gom mọi kiểm tra tất định (compose tool đã có,
KHÔNG đẻ tool trùng). Không phải nhớ 7 lệnh — mô tả phạm vi là đủ.

Dùng:
  medic                 # tất cả (all)
  medic rules           # chỉ nhóm khớp 'rules' (mô tả phạm vi, không nhớ subcommand)
  medic docs eval       # nhiều phạm vi
  medic --ci            # exit≠0 nếu có mục FAIL (để chốt pre-commit/CI)
  medic --list          # liệt kê các probe + tag

Triết lý: Meadows (vòng phản hồi trên tầng enforcement) + hub-1-tên/transparent (kim chỉ nam fdk).
Tự-mở-coverage: đọc policy.yaml/validator/generator LIVE → thêm chức năng mà quên hàng rào → medic tự báo.
Self-contained: chỉ stdlib. Fail-open từng probe: probe lỗi → SKIP, không giết cả cổng.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable
G, Y, R, B, X = "\033[32m", "\033[33m", "\033[31m", "\033[34m", "\033[0m"


def sh(args, timeout=120):
    try:
        r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return 127, str(e)


# ── PROBES ─────────────────────────────────────────────────────────────────────────────────
# Mỗi probe trả (state, detail, fix): state ∈ 'ok'|'fail'|'warn'|'skip'.
def p_rules():
    """Luật có CẮN không — harness-doctor fire-drill (BAD phải bị chặn)."""
    doc = ROOT / "harness/scripts/harness-doctor.py"
    if not doc.exists():
        return "skip", "harness-doctor.py không có", ""
    rc, out = sh([PY, str(doc), "--ci"])
    m = re.search(r"(\d+)/(\d+) rails bite", out)
    bite = m.group(0) if m else "?"
    drift = "✗ validator drift" in out
    if rc != 0:
        return "fail", f"có rail ĐEN (BAD không bị chặn) — {bite}", "python3 harness/scripts/harness-doctor.py --ci"
    if drift:
        dl = next((l.strip() for l in out.splitlines() if "validator drift" in l), "drift")
        return "warn", f"{bite} cắn, NHƯNG {dl}", "sync validator: bản hooks-copy khác src"
    return "ok", f"{bite} rail đều cắn", ""


def p_coverage():
    """Tự-mở-coverage: rule trong policy.yaml có bite-test chưa (debt hiện tại)."""
    pol = ROOT / "harness/poc-vendor-neutral/policy.yaml"
    doc = ROOT / "harness/scripts/harness-doctor.py"
    if not (pol.exists() and doc.exists()):
        return "skip", "thiếu policy.yaml/harness-doctor", ""
    rules = set(re.findall(r"id:\s*(R\d+)", pol.read_text(encoding="utf-8")))
    tested = set(re.findall(r"def build_(r\d+)", doc.read_text(encoding="utf-8")))
    tested = {t.upper() for t in tested}
    missing = sorted(rules - tested, key=lambda r: int(r[1:]))
    if not missing:
        return "ok", f"{len(rules)}/{len(rules)} rule có bite-test", ""
    return "warn", (f"{len(tested)}/{len(rules)} rule có bite-test — {len(missing)} chưa chứng minh: "
                    + ",".join(missing)), "mở rộng harness-doctor build_rN cho rule còn thiếu (proposal medic)"


def p_backstop():
    """Backstop L2 git còn sống không (pre-commit)."""
    if (ROOT / ".git/hooks/pre-commit").exists():
        return "ok", "pre-commit đã cài (.git/hooks)", ""
    return "warn", "pre-commit CHƯA cài — backstop L2 tắt", "pre-commit install"


def p_docs():
    """Docs/CAPABILITIES khớp đĩa không (anti-drift) — mọi build-*.py --check LIVE."""
    # chỉ generator KHAI có --check (khớp bản 'luôn-mới' wired ở stop.py) — tránh false-positive
    KNOWN = ("build-overstack-docs.py", "build-capabilities.py")   # generator có --check THẬT (anti-drift)
    checks = []
    for fn in KNOWN:
        gen = ROOT / "fdk/tools" / fn
        if not gen.exists():
            continue
        rc, out = sh([PY, str(gen), "--check"], timeout=60)
        if "required" in out and "argument" in out:      # thiếu positional → không phải --check thật
            continue
        checks.append((gen.stem, rc == 0))
    if not checks:
        return "skip", "không generator nào có --check", ""
    stale = [n for n, ok in checks if not ok]
    if stale:
        return "fail", f"{len(stale)} docs CŨ so đĩa: {','.join(stale)}", "python3 fdk/tools/<gen>.py  # regen"
    return "ok", f"{len(checks)} generator khớp đĩa", ""


def p_narrative():
    """Narrative overstack có TRUNG THỰC không (council-025) — KHÁC docs-probe (chỉ so
    html==generator-output = tính TRUNG THÀNH bản sao). Probe này gác tính TRUNG THỰC bản gốc:
      (b) mọi live_probe trong mechanisms.yaml phải TỒN TẠI (manifest không nói dối);
      (a) mọi cơ-chế LIVE phải XUẤT HIỆN trong overstack.html (không narrative drift);
      (c) canary: skill mô tả tuyến-phòng-thủ mà chưa vào manifest → warn.
    Parse manifest bằng regex → medic vẫn stdlib-only; fail-open nếu không parse được."""
    man = ROOT / "harness/mechanisms.yaml"
    page = ROOT / "llmwiki/html/overstack.html"
    if not (man.exists() and page.exists()):
        return "skip", "thiếu mechanisms.yaml/overstack.html", ""
    text = man.read_text(encoding="utf-8")
    names = re.findall(r'^\s*name:\s*"?(.+?)"?\s*$', text, re.M)
    probes = re.findall(r'^\s*live_probe:\s*(.+?)\s*$', text, re.M)
    if not names or len(names) != len(probes):
        return "skip", "manifest cơ-chế không parse được (regex)", ""
    html = page.read_text(encoding="utf-8", errors="ignore")
    lying = [p for p in probes if not (ROOT / p).exists()]
    if lying:
        return ("fail", f"manifest NÓI DỐI: {len(lying)} live_probe không tồn tại: {','.join(lying[:3])}",
                "sửa harness/mechanisms.yaml — live_probe phải trỏ file/dir thật")
    missing = [n for n, p in zip(names, probes) if n not in html]
    if missing:
        return ("fail", f"NARRATIVE DRIFT: {len(missing)} cơ-chế LIVE vắng overstack.html: {','.join(missing[:3])}",
                "python3 fdk/tools/build-overstack-docs.py  # regen trang từ manifest")
    KW = ("self-heal", "gương-soi", "tuyến phòng thủ", "narrative drift", "rào chắn còn cắn")
    known = " ".join(names + probes).lower()
    canary = []
    skdir = ROOT / "skills"
    if skdir.is_dir():
        for sk in sorted(skdir.glob("*/SKILL.md")):
            head = sk.read_text(encoding="utf-8", errors="ignore")[:600].lower()
            nm = sk.parent.name
            if any(k in head for k in KW) and nm not in known:
                canary.append(nm)
    if canary:
        return ("warn", f"{len(names)} cơ-chế khớp trang; canary: skill phòng-thủ chưa vào manifest: {','.join(canary[:3])}",
                "nếu là tuyến phòng thủ, thêm vào harness/mechanisms.yaml")
    return "ok", f"{len(names)} cơ-chế LIVE đều có mặt + đúng bản gốc", ""


def p_selfstate():
    """code-state self-narration (Phase 2) còn TRUNG THỰC không (council-advisory):
      - reproducibility (Feynman): code-state.py --check phải xanh (render 2 lần byte-identical);
      - presence: overstack.html phải có section 'Trạng thái hiện thời'.
    (Staleness của FACT ổn định do docs-probe lo — regen đổi html → docs FAIL nếu quên.)"""
    cs = ROOT / "fdk/tools/code-state.py"
    page = ROOT / "llmwiki/html/overstack.html"
    if not cs.exists():
        return "skip", "code-state.py chưa có", ""
    rc, out = sh([PY, str(cs), "--check"], timeout=200)
    if rc != 0:
        return "fail", "code-state KHÔNG tái tạo được (render 2 lần lệch — nondeterminism)", \
               "python3 fdk/tools/code-state.py --check"
    if page.exists() and "Trạng thái hiện thời" not in page.read_text(encoding="utf-8", errors="ignore"):
        return "fail", "overstack.html THIẾU section 'Trạng thái hiện thời'", \
               "python3 fdk/tools/build-overstack-docs.py  # regen"
    return "ok", "code-state tái tạo được + section có mặt", ""


def p_code():
    """Code lành — mọi .py trong harness/ + fdk/tools compile sạch (không rail gãy cú pháp)."""
    import py_compile
    bad = []
    for d in ("harness/scripts", "harness/validators", "fdk/tools", "llmwiki/.claude/hooks"):
        base = ROOT / d
        if not base.is_dir():
            continue
        for f in base.rglob("*.py"):
            try:
                py_compile.compile(str(f), doraise=True)
            except Exception:
                bad.append(f.relative_to(ROOT).as_posix())
    if bad:
        return "fail", f"{len(bad)} file .py GÃY: {', '.join(bad[:3])}", "sửa lỗi cú pháp"
    return "ok", "mọi .py compile sạch", ""


def p_eval():
    """Eval lõi không regress — self-index gate + episodic retrieval hit@k (nếu có baseline)."""
    gate = ROOT / "harness/evals/self-index/check.py"
    if gate.exists():
        rc, out = sh([PY, str(gate)])
        if rc != 0:
            return "fail", "eval self-index REGRESS", "xem harness/evals/self-index"
    # episodic retrieval (tầng nhớ episodic, issue #9): sinh output tất định rồi --check hit@k
    ep_base = ROOT / "harness/metrics/episodic-baseline.json"
    ep_dir = ROOT / "llmwiki/wiki/sources/evals/episodic"
    if ep_base.exists() and ep_dir.is_dir():
        import tempfile as _tf
        out_f = Path(_tf.gettempdir()) / "medic-ep-out.json"
        rc, _ = sh([PY, str(ROOT / "harness/scripts/mem-proxy.py"), "--out", str(out_f)])
        if rc != 0:
            return "fail", "episodic mem-proxy GÃY", "python3 harness/scripts/mem-proxy.py --self-test"
        rc, _ = sh([PY, str(ROOT / "harness/scripts/retrieval-eval.py"),
                    "--evals-dir", str(ep_dir), "--outputs", str(out_f),
                    "--baseline", str(ep_base), "--check"])
        if rc != 0:
            return "fail", "episodic retrieval hit@k REGRESS", "xem harness/metrics/episodic-baseline.json"
        return "ok", "eval không regress (self-index + episodic hit@k)", ""
    if not gate.exists():
        return "skip", "self-index eval chưa promote; chưa có episodic baseline", ""
    return "ok", "eval self-index không regress", ""


PROBES = [
    ("rules",    ["rules", "luật", "bite"],      p_rules),
    ("coverage", ["rules", "coverage", "luật"],  p_coverage),
    ("drift",    ["drift", "rules"],             lambda: p_rules()),  # drift lộ trong p_rules
    ("backstop", ["backstop", "git", "commit"],  p_backstop),
    ("docs",     ["docs", "capabilities"],       p_docs),
    ("narrative", ["narrative", "docs", "drift"], p_narrative),
    ("selfstate", ["selfstate", "state", "narrative"], p_selfstate),
    ("code",     ["code", "health"],             p_code),
    ("eval",     ["eval", "baseline"],           p_eval),
]
# bỏ 'drift' probe trùng — drift đã báo trong rules:
PROBES = [p for p in PROBES if p[0] != "drift"]

ICON = {"ok": f"{G}✓{X}", "fail": f"{R}✗{X}", "warn": f"{Y}⚠{X}", "skip": f"{B}·{X}"}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    flags = {a for a in sys.argv[1:] if a.startswith("-")}
    if "--list" in flags:
        print("medic probes:")
        for name, tags, _ in PROBES:
            print(f"  {name:10} tags: {', '.join(tags)}")
        return 0
    scope = args
    chosen = [p for p in PROBES if not scope or any(s in p[0] or s in p[1] for s in scope)]

    print(f"{B}medic{X} — cổng sức khoẻ framework  ·  {ROOT}")
    print(f"phạm vi: {' '.join(scope) if scope else 'all'}  ·  {len(chosen)}/{len(PROBES)} probe\n")
    results = []
    for name, _tags, fn in chosen:
        try:
            state, detail, fix = fn()
        except Exception as e:
            state, detail, fix = "skip", f"probe lỗi: {e}", ""
        results.append((name, state, detail, fix))
        line = f"  {ICON[state]} {name:10} {detail}"
        print(line)
        if fix and state in ("fail", "warn"):
            print(f"       {B}↳ sửa:{X} {fix}")

    fails = [r for r in results if r[1] == "fail"]
    warns = [r for r in results if r[1] == "warn"]
    verdict = "FAIL" if fails else ("KHOẺ (có cảnh báo)" if warns else "HỆ KHOẺ")
    vcol = R if fails else (Y if warns else G)
    print(f"\n{vcol}▉ {verdict}{X} — {len(fails)} fail · {len(warns)} warn · "
          f"{sum(1 for r in results if r[1]=='ok')} ok · {sum(1 for r in results if r[1]=='skip')} skip")

    # ── recap + dạy dùng thụ động (kim chỉ nam fdk: cuối output nhắc lại + use-case) ──
    print(f"""
{B}medic là gì:{X} một lệnh = tuyến phòng thủ cuối. Nó KHÔNG sửa gì — chỉ CHỨNG MINH hệ còn
khoẻ: luật còn cắn, validator không lệch bản, docs khớp đĩa, code compile, eval không tụt.
Xanh = yên tâm; đỏ = in đúng chỗ hở + 1 dòng lệnh sửa.

{B}dùng khi (kể cả lúc không ngờ):{X}
  • trước khi commit/PR — `medic --ci` chốt, đỏ thì đừng đẩy.
  • sau khi kéo bản mới / đổi máy — `medic` xem overstack có nguyên vẹn.
  • nghi một rule "có vẻ không chặn nữa" — `medic rules` rà riêng tầng luật.
  • vừa thêm skill/rule/generator — `medic` tự báo nếu quên hàng rào cho nó.
  • chỉ muốn coi cấu trúc phòng thủ — `medic --list`.

{B}cấu trúc (transparent — biết đồ nằm đâu mà mở):{X}
  fdk/tools/medic.py            ← bạn đang chạy cái này (hub)
  fdk/tools/build-*.py --check  ← probe docs/capabilities gọi tới
  harness/scripts/harness-doctor.py  ← probe rules gọi tới (fire-drill BAD/GOOD)
  harness/poc-vendor-neutral/policy.yaml  ← nguồn 'có bao nhiêu luật' (đếm LIVE)
  harness/validators/*.py       ← các validator được rà 'còn cắn không'""")
    return 1 if (fails and "--ci" in flags) else 0


if __name__ == "__main__":
    sys.exit(main())
