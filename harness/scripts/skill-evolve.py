#!/usr/bin/env python3
"""skill-evolve — per-skill quality ledger + auto-draft revision proposal.

BUILD-NOW / ADAPTER BOUNDARY (see /build-now-adapt-later)
----------------------------------------------------------
Correlator mỏng nối 3 module đã có, KHÔNG viết lại engine chấm điểm nào:
  * fdk/tools/skill-usage.py::collect()   — biết lúc nào gọi skill nào (line_idx/file)
  * harness/scripts/trace-grader.py       — chấm đường đi tất định (runs_from_transcript/grade_run)
  * harness/scripts/bnal_metrics.py + bnal_config.py — ghi ledger JSONL fail-open + load config

Ngưỡng số (min_sample, fail_rate_threshold) sống trong harness/skill-evolve.config.yaml,
verified:false — adapter DUY NHẤT, xem /build-now-adapt-later.

Never auto-promote: --draft chỉ SOẠN đề xuất, dừng ở /propose. Không tự ghi SKILL.md.

Usage
-----
  python3 harness/scripts/skill-evolve.py --scan [N]
  python3 harness/scripts/skill-evolve.py --report
  python3 harness/scripts/skill-evolve.py --draft <skill_id>
  python3 harness/scripts/skill-evolve.py --self-test
"""
import argparse
import datetime as _dt
import glob
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # harness/scripts
HARNESS = HERE.parent                            # harness
ROOT = HARNESS.parent                             # repo root
FDK_TOOLS = ROOT / "fdk" / "tools"

LEDGER = "skill-evolve-ledger.jsonl"
STATE_REL = "skill-evolve.state.json"
CONFIG_NAME = "skill-evolve"
DEFAULT_CFG = {"verified": False, "min_sample": 5, "fail_rate_threshold": 0.4}

sys.path.insert(0, str(HERE))
import bnal_config      # noqa: E402  (cùng thư mục, import thường — không dấu gạch ngang)
import bnal_metrics     # noqa: E402


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # trace-grader.py dùng @dataclass + postponed annotations —
    spec.loader.exec_module(mod)  # cần đăng ký trước exec để dataclasses._is_type resolve được
    return mod


_su = None


def skill_usage():
    global _su
    if _su is None:
        _su = _load_module("skill_usage", FDK_TOOLS / "skill-usage.py")
    return _su


_tg = None


def trace_grader():
    global _tg
    if _tg is None:
        _tg = _load_module("trace_grader", HERE / "trace-grader.py")
    return _tg


def _state_path() -> Path:
    return HARNESS / "metrics" / STATE_REL


def _load_state() -> dict:
    try:
        import json
        return json.loads(_state_path().read_text(encoding="utf-8"))
    except Exception:
        return {"processed": []}


def _save_state(state: dict) -> None:
    try:
        import json
        bnal_metrics.ensure_gitignored(ROOT, STATE_REL, comment="skill-evolve watermark (local)")
        _state_path().parent.mkdir(parents=True, exist_ok=True)
        _state_path().write_text(json.dumps(state), encoding="utf-8")
    except Exception:
        pass


def scan(root=ROOT, n=1) -> int:
    """Cắt lát N session gần nhất theo từng lần gọi Skill-tool, chấm bằng trace-grader,
    ghi verdict vào ledger. Idempotent (watermark theo session::line_idx). Fail-open per lần gọi."""
    su = skill_usage()
    tg = trace_grader()
    dirs = su.discover_transcript_dirs(root)
    all_files = sorted(
        (Path(f) for d in dirs for f in glob.glob(str(Path(d) / "*.jsonl"))),
        key=lambda p: p.stat().st_mtime, reverse=True,
    )
    target = {str(p) for p in all_files[:n]}
    if not target:
        return 0

    events = su.collect(dirs)
    by_file = {}
    for e in events:
        if e["file"] in target:
            by_file.setdefault(e["file"], []).append(e)

    cfg = tg.load_config(str(tg.DEFAULT_CONFIG_PATH))
    state = _load_state()
    processed = set(state.get("processed", []))
    written = 0

    for fpath, evs in by_file.items():
        evs.sort(key=lambda e: e["line_idx"])
        try:
            all_lines = Path(fpath).read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for i, e in enumerate(evs):
            key = f"{e['session']}::{e['line_idx']}"
            if key in processed:
                continue
            start = e["line_idx"]
            end = evs[i + 1]["line_idx"] if i + 1 < len(evs) else len(all_lines)
            slice_lines = all_lines[start:end]
            try:
                runs = tg.runs_from_transcript(slice_lines, task_hint=e["skill"])
                if not runs:
                    processed.add(key)
                    continue
                verdict = tg.grade_run(runs[0], cfg)
            except Exception:
                continue
            rec = {
                "skill": e["skill"], "session": e["session"], "ts": e["ts"].isoformat(),
                "verdict": verdict["verdict"], "flags": verdict["flags"],
            }
            bnal_metrics.append(root, LEDGER, rec, comment="skill-evolve per-skill quality ledger (local)")
            processed.add(key)
            written += 1

    _save_state({"processed": sorted(processed)})
    return written


def _leaderboard(root=ROOT) -> dict:
    """{skill_id: {count, bad}} — bad = số verdict corrupt-success (verdict 'fail' cũng
    tính nếu có, nhưng KHÔNG BAO GIỜ xảy ra với run xuất phát từ transcript — xem
    trace-grader.py docstring runs_from_transcript: Run.ok bị ép True nên grade_run không
    bao giờ trả 'fail' cho nguồn dữ liệu này; giữ cả hai nhánh để không vỡ nếu sau này
    thêm nguồn khác (traces.json/audit) có Run.ok thật)."""
    groups = {}
    for r in bnal_metrics.read(root, LEDGER):
        g = groups.setdefault(r["skill"], {"count": 0, "bad": 0})
        g["count"] += 1
        if r["verdict"] in ("corrupt-success", "fail"):
            g["bad"] += 1
    return groups


def report(root=ROOT) -> str:
    cfg = bnal_config.load(root, CONFIG_NAME, DEFAULT_CFG)
    min_sample = int(cfg.get("min_sample", 5))
    thr = float(cfg.get("fail_rate_threshold", 0.4))
    groups = _leaderboard(root)
    lines = [
        f"skill-evolve — {len(groups)} skill(s) tracked",
        f"min_sample={min_sample}  fail_rate_threshold={thr}  "
        f"(adapter: harness/{CONFIG_NAME}.config.yaml, verified={cfg.get('verified')})",
        "",
    ]
    if not groups:
        lines.append("(chưa có dữ liệu — chạy --scan trước)")
        return "\n".join(lines)
    ordered = sorted(groups.items(), key=lambda kv: (-kv[1]["bad"], kv[0]))
    eligible = []
    for skill, g in ordered:
        rate = g["bad"] / g["count"] if g["count"] else 0.0
        elig = g["count"] >= min_sample and rate >= thr
        if elig:
            eligible.append(skill)
        tag = "DRAFT-ELIGIBLE" if elig else "-"
        lines.append(f"  {g['count']:>4}  fail_rate={rate:.2f}  {tag:<15}  {skill}")
    lines.append("")
    lines.append("Eligible for --draft:" if eligible else "Chưa skill nào đủ mẫu + vượt ngưỡng.")
    lines += [f"  skill-evolve.py --draft {s}" for s in eligible]
    return "\n".join(lines)


def _skill_md_path(root, skill_id):
    """FR-008: định vị qua registry canonical (glob skills/*/SKILL.md dùng bởi
    fdk/tools/build-capabilities.py::skills_dir), KHÔNG đoán bằng convention tên file khác."""
    p = Path(root) / "skills" / skill_id / "SKILL.md"
    return p if p.is_file() else None


def _ddmmyy(date_str: str) -> str:
    y, m, d = date_str.split("-")
    return f"{d}{m}{y[2:]}"


def draft(root=ROOT, skill_id=None, date_str=None):
    cfg = bnal_config.load(root, CONFIG_NAME, DEFAULT_CFG)
    min_sample = int(cfg.get("min_sample", 5))
    thr = float(cfg.get("fail_rate_threshold", 0.4))
    groups = _leaderboard(root)
    g = groups.get(skill_id)
    if not g or not (g["count"] >= min_sample and (g["bad"] / g["count"]) >= thr):
        return None, f"'{skill_id}' chưa đủ mẫu (>= {min_sample}) hoặc chưa vượt ngưỡng ({thr}) — không eligible."

    skill_md = _skill_md_path(root, skill_id)
    if not skill_md:
        return None, f"Không tìm thấy skills/{skill_id}/SKILL.md — không thể soạn draft."

    rows = [r for r in bnal_metrics.read(root, LEDGER)
            if r["skill"] == skill_id and r["verdict"] in ("corrupt-success", "fail")]
    date_str = date_str or _dt.date.today().isoformat()
    ddmmyy = _ddmmyy(date_str)
    out_dir = Path(root) / "llmwiki" / "wiki" / "sources" / "draft"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{ddmmyy}-skill-evolve-{skill_id}.md"

    rate = g["bad"] / g["count"]
    md = [
        "---", "type: draft",
        f'title: "Đề xuất sửa SKILL.md — {skill_id} (skill-evolve)"',
        "status: proposed", f"tags: [skill-evolve, {skill_id}, quality-regression]",
        f"timestamp: {date_str}", "---", "",
        f"# {ddmmyy}-skill-evolve-{skill_id}", "",
        f"Tỷ lệ lỗi (`corrupt-success`/`fail`) của skill `{skill_id}` = "
        f"{g['bad']}/{g['count']} ({rate:.0%}), vượt ngưỡng {thr:.0%} "
        f"(cấu hình `harness/{CONFIG_NAME}.config.yaml`). Nội dung `SKILL.md` hiện tại và "
        f"bằng chứng cụ thể ở dưới — bản này là SEED cho `/propose`, KHÔNG tự ghi đè.", "",
        "## SKILL.md hiện tại (nguyên văn)", "```markdown",
        skill_md.read_text(encoding="utf-8"), "```", "",
        f"## Bằng chứng ({len(rows)} lần gọi lỗi)", "",
        "| Session | Verdict | Flags |", "|---|---|---|",
    ]
    for r in rows[-20:]:
        flags_s = "; ".join(f.get("detail") or f.get("check", "?") for f in r.get("flags", [])) or "-"
        md.append(f"| {r['session']} | {r['verdict']} | {flags_s} |")
    md += [
        "", "## Origin",
        f"- **Source:** `skill-evolve.py --draft {skill_id}` từ `harness/metrics/{LEDGER}` "
        f"({g['count']} lần gọi, {g['bad']} lỗi).",
        f"- **Adapter:** `harness/{CONFIG_NAME}.config.yaml` (verified={cfg.get('verified')}).",
        f"- **Date:** {date_str}", "",
    ]
    out.write_text("\n".join(md), encoding="utf-8")
    return out, f"Đã soạn {out} — STOP, chờ /propose hoàn thiện + người duyệt."


def self_test() -> int:
    import json as _json
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "harness").mkdir()
        (root / "harness" / f"{CONFIG_NAME}.config.yaml").write_text(
            "verified: false\nmin_sample: 1\nfail_rate_threshold: 0.4\n", encoding="utf-8"
        )
        skills_dir = root / "skills" / "demo-bad"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("---\nname: demo-bad\n---\n# demo-bad\n", encoding="utf-8")

        proj = root / "proj"
        proj.mkdir()
        lines = [
            {"type": "assistant", "timestamp": "2026-07-24T10:00:00.000Z", "sessionId": "st-se",
             "message": {"content": [{"type": "tool_use", "id": "c1", "name": "Skill",
                                       "input": {"skill": "demo-clean"}}]}},
            {"type": "assistant", "timestamp": "2026-07-24T10:00:01.000Z", "sessionId": "st-se",
             "message": {"content": [{"type": "tool_use", "id": "c2", "name": "Read",
                                       "input": {"file_path": "x.py"}}]}},
            {"type": "user", "timestamp": "2026-07-24T10:00:02.000Z", "sessionId": "st-se",
             "message": {"content": [{"type": "tool_result", "tool_use_id": "c2",
                                       "content": "ok", "is_error": False}]}},
            {"type": "assistant", "timestamp": "2026-07-24T10:00:03.000Z", "sessionId": "st-se",
             "message": {"content": [{"type": "tool_use", "id": "c3", "name": "Skill",
                                       "input": {"skill": "demo-bad"}}]}},
            {"type": "assistant", "timestamp": "2026-07-24T10:00:04.000Z", "sessionId": "st-se",
             "message": {"content": [{"type": "tool_use", "id": "c4", "name": "force_push",
                                       "input": {}}]}},
            {"type": "user", "timestamp": "2026-07-24T10:00:05.000Z", "sessionId": "st-se",
             "message": {"content": [{"type": "tool_result", "tool_use_id": "c4",
                                       "content": "done", "is_error": False}]}},
        ]
        (proj / "st-se.jsonl").write_text(
            "\n".join(_json.dumps(l) for l in lines) + "\n", encoding="utf-8"
        )

        su = skill_usage()
        events = su.collect([proj])
        by_file = {}
        for e in events:
            by_file.setdefault(e["file"], []).append(e)
        tg = trace_grader()
        cfg = tg.load_config(str(tg.DEFAULT_CONFIG_PATH))
        written = 0
        for fpath, evs in by_file.items():
            evs.sort(key=lambda e: e["line_idx"])
            all_lines = Path(fpath).read_text(encoding="utf-8").splitlines()
            for i, e in enumerate(evs):
                start = e["line_idx"]
                end = evs[i + 1]["line_idx"] if i + 1 < len(evs) else len(all_lines)
                runs = tg.runs_from_transcript(all_lines[start:end], task_hint=e["skill"])
                if not runs:
                    continue
                verdict = tg.grade_run(runs[0], cfg)
                rec = {"skill": e["skill"], "session": e["session"], "ts": e["ts"].isoformat(),
                       "verdict": verdict["verdict"], "flags": verdict["flags"]}
                bnal_metrics.append(root, LEDGER, rec, comment="self-test")
                written += 1

        rep = report(root)
        out, _msg = draft(root, "demo-bad", date_str="2026-07-24")

        ok = (
            written == 2
            and "demo-clean" in rep and "demo-bad" in rep
            and "DRAFT-ELIGIBLE" in rep
            and out is not None and out.exists()
            and "force_push" in out.read_text(encoding="utf-8")
        )

    print("skill-evolve self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="skill-evolve — per-skill quality ledger")
    ap.add_argument("--scan", nargs="?", const=1, type=int, metavar="N",
                    help="quét N session gần nhất (mặc định 1 = session hiện tại)")
    ap.add_argument("--report", action="store_true", help="leaderboard per-skill")
    ap.add_argument("--draft", metavar="SKILL_ID", help="soạn đề xuất sửa SKILL.md nếu eligible")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.scan is not None:
        n = args.scan
        written = scan(ROOT, n)
        print(f"· scan {n} session → {written} verdict mới ghi vào harness/metrics/{LEDGER}")
        return 0
    if args.report:
        print(report(ROOT))
        return 0
    if args.draft:
        out, msg = draft(ROOT, args.draft)
        print(msg)
        return 0 if out else 1
    ap.error("chưa có subcommand — dùng --scan/--report/--draft/--self-test")
    return 2


if __name__ == "__main__":
    sys.exit(main())
