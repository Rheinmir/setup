#!/usr/bin/env python3
"""hook-audit — đếm lỗi CỦA CHÍNH HARNESS từ transcript Claude Code (phiên chính + sub-agent).

Vì sao: hook fail-open nuốt lỗi, không sổ nào ghi (stop.py timeout 731 lần/30 ngày mà failures.jsonl
trống — xem draft 280926-harness-error-audit-30d.md trong wiki dự án, F6). Nguồn thật duy nhất là
attachment trong transcript: hook_cancelled (timeout) · hook_{blocking,non_blocking}_error · hook_success
exit≠0 · tool_result is_error có dấu vết harness.

CLI:
    hook-audit.py [--days N] [--root ~/.claude/projects] [--json OUT]   # in bảng chữ ký, mới→cũ
    hook-audit.py --self-test
Mỗi chữ ký (sig) ổn định giữa các lần chạy → dùng làm fingerprint dedupe issue.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys
import tempfile
import time

HARN = re.compile(r"harness/|llmwiki/\.claude/hooks|fdk/tools|orca-graph|\[R\d+|\[harness|egress-guard|"
                  r"hooklib|stop\.py|pre_tool_use|post_tool_use", re.I)
RULE = re.compile(r"\[(R\d+ [\w-]+|egress-guard)\]")


def _txt(c) -> str:
    if isinstance(c, list):
        return "\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in c)
    return c if isinstance(c, str) else str(c)


def _script(cmd) -> str:
    m = re.search(r"hooks/([\w\-]+\.(?:py|sh))", cmd or "")
    return m.group(1) if m else ("orca-agent-hook" if "ORCA_AGENT_HOOK" in (cmd or "") else (cmd or "?")[:40])


def _sig(kind: str, where: str, text: str) -> str:
    """Chữ ký ổn định: bỏ số, hash, path tạm — cùng lỗi gốc ra cùng sig."""
    r = RULE.search(text)
    head = r.group(1) if r else re.sub(r"[0-9a-f]{8,}|\d+|/[\w./\-]+", "#", text.strip())[:70]
    return f"{kind}|{where}|{head}"


def scan_file(path: str):
    sub = "/subagents/" in path
    tu = {}
    for line in open(path, errors="ignore"):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        ts = (e.get("timestamp") or "")[:19]
        a = e.get("attachment") or {}
        at = a.get("type")
        if at == "hook_cancelled":
            k = "hook-timeout" if a.get("timedOut") else "hook-cancelled"
            yield dict(ts=ts, sub=sub, sig=_sig(k, f"{a.get('hookName')}:{_script(a.get('command'))}", ""),
                       text=f"{a.get('durationMs')}ms/{a.get('timeoutMs')}ms")
        elif at in ("hook_non_blocking_error", "hook_blocking_error"):
            be = a.get("blockingError") if isinstance(a.get("blockingError"), dict) else {}
            t = (a.get("stderr") or "") + (be.get("blockingError") or "")
            where = f"{a.get('hookName')}:{_script(a.get('command') or be.get('command'))}"
            yield dict(ts=ts, sub=sub, sig=_sig(at[5:], where, t), text=t[:600])
        elif at == "hook_success" and a.get("exitCode") not in (0, None):
            t = (a.get("stderr") or "") + (a.get("stdout") or "")
            yield dict(ts=ts, sub=sub, sig=_sig("hook-nonzero", f"{a.get('hookName')}:{_script(a.get('command'))}", t),
                       text=t[:600])
        m = e.get("message")
        for c in (m.get("content") if isinstance(m, dict) and isinstance(m.get("content"), list) else []):
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use":
                tu[c.get("id")] = (c.get("name"), json.dumps(c.get("input"), ensure_ascii=False)[:400])
            elif c.get("type") == "tool_result" and c.get("is_error"):
                t = _txt(c.get("content"))
                name, inp = tu.get(c.get("tool_use_id"), ("?", ""))
                if HARN.search(t) or HARN.search(inp):
                    k = "hook-deny" if re.search(r"hook (error|block)|PreToolUse", t, re.I) else "tool-error"
                    yield dict(ts=ts, sub=sub, sig=_sig(k, name, t), text=t[:600], input=inp)


def audit(root: str, days: float):
    cut = time.time() - days * 86400
    groups = collections.defaultdict(list)
    for f in glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True):
        if os.path.getmtime(f) < cut:
            continue
        for ev in scan_file(f):
            if ev["ts"] and time.mktime(time.strptime(ev["ts"], "%Y-%m-%dT%H:%M:%S")) < cut - 86400:
                continue  # file mới sửa nhưng sự kiện cũ
            ev["file"] = f
            groups[ev["sig"]].append(ev)
    out = []
    for sig, evs in groups.items():
        evs.sort(key=lambda x: x["ts"])
        out.append(dict(sig=sig, count=len(evs), subagent=sum(e["sub"] for e in evs),
                        first=evs[0]["ts"], last=evs[-1]["ts"], sample=evs[-1]))
    return sorted(out, key=lambda g: -g["count"])


def self_test() -> int:
    d = tempfile.mkdtemp()
    rows = [
        {"type": "attachment", "timestamp": "2099-01-01T00:00:00Z", "attachment": {
            "type": "hook_cancelled", "hookName": "Stop", "timedOut": True, "durationMs": 30010,
            "timeoutMs": 30000, "command": "python3 $HOME/.claude/harness/hooks/stop.py"}},
        {"type": "attachment", "timestamp": "2099-01-01T00:00:01Z", "attachment": {
            "type": "hook_non_blocking_error", "hookName": "UserPromptSubmit", "stderr": "not valid JSON",
            "command": "python3 x/hooks/user_prompt_submit.py"}},
        {"type": "assistant", "timestamp": "2099-01-01T00:00:02Z", "message": {"content": [
            {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "curl localhost"}}]}},
        {"type": "user", "timestamp": "2099-01-01T00:00:03Z", "message": {"content": [
            {"type": "tool_result", "tool_use_id": "t1", "is_error": True,
             "content": "PreToolUse:Bash hook error: [egress-guard] egress to non-allow-listed host: localhost"}]}},
        {"type": "user", "timestamp": "2099-01-01T00:00:04Z", "message": {"content": [
            {"type": "tool_result", "tool_use_id": "zz", "is_error": True, "content": "unrelated failure"}]}},
    ]
    with open(os.path.join(d, "s.jsonl"), "w") as fh:
        fh.write("\n".join(json.dumps(r) for r in rows))
    g = {x["sig"]: x for x in audit(d, 1)}
    assert "hook-timeout|Stop:stop.py|" in g, g
    assert any(s.startswith("non_blocking_error|UserPromptSubmit:user_prompt_submit.py") for s in g), g
    assert "hook-deny|Bash|egress-guard" in g, g
    assert len(g) == 3, g  # lỗi không dính harness bị loại
    print("hook-audit self-test ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--days", type=float, default=1)
    ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--json", help="ghi toàn bộ nhóm ra file JSON")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    groups = audit(a.root, a.days)
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(groups, fh, ensure_ascii=False, indent=1)
    for g in groups:
        print(f"{g['count']:5d}  sub={g['subagent']:<3d} {g['first'][:10]}→{g['last'][:10]}  {g['sig']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
