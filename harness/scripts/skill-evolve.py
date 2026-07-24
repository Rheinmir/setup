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


def main() -> int:
    ap = argparse.ArgumentParser(description="skill-evolve — per-skill quality ledger")
    ap.add_argument("--scan", nargs="?", const=1, type=int, metavar="N",
                    help="quét N session gần nhất (mặc định 1 = session hiện tại)")
    args = ap.parse_args()
    if args.scan is not None:
        n = args.scan
        written = scan(ROOT, n)
        print(f"· scan {n} session → {written} verdict mới ghi vào harness/metrics/{LEDGER}")
        return 0
    ap.error("chưa có subcommand — dùng --scan (thêm --report/--draft/--self-test ở task sau)")
    return 2


if __name__ == "__main__":
    sys.exit(main())
