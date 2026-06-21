#!/usr/bin/env python3
"""Helpers chung cho L1 adapter (Claude Code). Vendor khác viết adapter tương đương
— xem harness/recipe.md, phần "Cook bản vendor mới".
"""
import datetime
import json
import os
import pathlib
import subprocess
import sys


def read_payload() -> dict:
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def project_dir(payload: dict) -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()


def find_validators(start: str):
    """Thứ tự: env LLMWIKI_VALIDATORS → bản copy cạnh hooks → harness/validators ở repo cha."""
    env = os.environ.get("LLMWIKI_VALIDATORS")
    if env and os.path.isdir(env):
        return pathlib.Path(env)
    here = pathlib.Path(__file__).resolve().parent
    if (here / "validators").is_dir():
        return here / "validators"
    p = pathlib.Path(start).resolve()
    for parent in [p, *p.parents]:
        cand = parent / "harness" / "validators"
        if cand.is_dir():
            return cand
    return None


def run_validator(name: str, event: dict, validators_dir: pathlib.Path):
    """Chạy validator theo contract stdin-JSON. Trả (returncode, stderr)."""
    proc = subprocess.run(
        [sys.executable, str(validators_dir / name)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        timeout=30,
    )
    return proc.returncode, proc.stderr.strip()


def find_wiki_dir(root: str):
    for cand in (pathlib.Path(root) / "wiki", pathlib.Path(root) / "llmwiki" / "wiki"):
        if cand.is_dir():
            return cand
    return None


def audit(payload: dict, event: str) -> None:
    """R4 log-append, bằng máy: mọi event append vào .claude/audit/YYYY-MM-DD.jsonl."""
    try:
        root = pathlib.Path(project_dir(payload))
        d = root / ".claude" / "audit"
        d.mkdir(parents=True, exist_ok=True)
        # audit log chứa command snippets — bảo đảm không bao giờ bị commit
        gi = root / ".claude" / ".gitignore"
        if not gi.exists() or "audit/" not in gi.read_text(encoding="utf-8", errors="ignore"):
            with open(gi, "a", encoding="utf-8") as f:
                f.write("audit/\n")
        ti = payload.get("tool_input") or {}
        rec = {
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
            "event": event,
            "session_id": payload.get("session_id"),
            "tool_name": payload.get("tool_name"),
            "file_path": ti.get("file_path"),
            "command": (ti.get("command") or "")[:200] or None,
        }
        rec = {k: v for k, v in rec.items() if v is not None}
        path = d / (datetime.date.today().isoformat() + ".jsonl")
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass  # audit không bao giờ được phép làm gãy phiên làm việc
