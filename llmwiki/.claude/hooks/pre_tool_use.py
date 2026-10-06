#!/usr/bin/env python3
"""L1/PreToolUse: chặn trước khi tool chạy. Exit 2 = block, stderr được đưa lại cho Claude.

Mỗi cú chặn cũng là một failure ĐÃ gán nhãn sẵn (taxonomy `spec-violation` = "ignored an
explicit rule") → ghi thẳng vào flywheel ledger. Tất định, 0 token, fail-open: capture không
còn chờ ai nhớ gõ `flywheel record`."""
import sys

import json
import os
import re
import subprocess
import tempfile

from hooklib import find_validators, project_dir, read_payload, resolve_tool, run_validator

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


def record_bite(root: str, rule: str, tool: str, target: str, err: str) -> None:
    """Rule cắn → 1 dòng ledger CỦA DỰ ÁN ĐÓ. Fail-open tuyệt đối: không thấy engine → no-op.
    resolve_tool = repo-local → global (~/.claude/harness): downstream chỉ có engine global,
    tự nối root/harness/scripts sẽ trượt và capture chết im (bắt được ở fresh-install)."""
    try:
        engine = resolve_tool(root, "harness/scripts/flywheel.py")
        if not engine:
            return
        sys.path.insert(0, os.path.dirname(engine))
        import flywheel
        flywheel.record(root, flywheel.KINDS["failure"], "spec-violation",
                        f"{rule} chặn {tool} {target}".strip(),
                        detail=(err or "").strip()[:300] or None)
    except Exception:
        pass


def run_egress_guard(root: str, event: dict, tool: str, target: str) -> None:
    """Chặn network-egress ngoài allow-list qua harness/scripts/egress-guard.py (bnal quarantine,
    xem harness/egress-guard.config.yaml). Trước bản vá này script chỉ chạy --self-test trong
    medic/fdk-gate — KHÔNG chặn Bash thật lúc runtime. Mặc định mode:warn nên vẫn fail-open cho
    tới khi allow_domains được calib + lật mode:block. Fail-open nếu không tìm thấy script."""
    guard = resolve_tool(root, "harness/scripts/egress-guard.py")
    if not guard:
        return
    try:
        r = subprocess.run([sys.executable, guard], input=json.dumps(event),
                           capture_output=True, text=True, timeout=15)
    except Exception:
        return  # fail-open tuyệt đối
    if r.returncode == 2:
        err = r.stderr.strip()
        record_bite(root, "egress-guard", tool, target, err)
        print(err, file=sys.stderr)
        sys.exit(2)


def run_local(root: str, event: dict, tool: str, target: str) -> None:
    """Chạy rule RIÊNG của dự án (harness-local/run.py) SONG SONG framework. Block (exit 2) nếu vi phạm.
    Fail-open: dự án không có harness-local/ hoặc lỗi → no-op (không đụng framework)."""
    runner = os.path.join(root, "harness-local", "run.py")
    if not os.path.isfile(runner):
        return
    try:
        r = subprocess.run([sys.executable, runner, "hook"], input=json.dumps(event),
                           capture_output=True, text=True, timeout=25)
    except Exception:
        return  # fail-open tuyệt đối
    if r.returncode == 2:
        err = r.stderr.strip()
        record_bite(root, "harness-local", tool, target, err)
        print(err, file=sys.stderr)
        sys.exit(2)


# Việc ỒN (dựng/kiểm HTML, chạy cổng) nên giao agent con để log + ảnh chụp không đổ vào context chính (user 07/10: phiên
# 7ed5600e tự md-render + sửa lớp nền + loay hoay Playwright ngay trong phiên chính). NHẮC, không chặn: hook nhận nhầm lệnh
# cũng không kẹt việc. Mỗi loại nhắc một lần mỗi phiên; agent con (có agent_type) không bao giờ bị nhắc.
DELEGATE = (
    ("html-builder", re.compile(r"md-render|html-visual-gate|html-slop-fix|playwright|chromium"),
     "dựng/kiểm trang HTML (render, gate, chụp ảnh, sửa tới xanh)"),
    ("gate-runner", re.compile(r"ci-local|medic\.py|\bpytest\b|swh-lint|harness-doctor"),
     "chạy cổng kiểm/test rồi sửa tới xanh"),
)


def delegate_nudge(payload: dict, tool: str, ti: dict) -> str:
    if payload.get("agent_type"):
        return ""
    text = ti.get("command", "") if tool == "Bash" else (ti.get("file_path", "") if tool in WRITE_TOOLS else "")
    for agent, rx, job in DELEGATE:
        hit = (tool in WRITE_TOOLS and agent == "html-builder" and text.lower().endswith(".html")) or (tool == "Bash" and rx.search(text))
        if not hit or not os.path.isfile(os.path.expanduser(f"~/.claude/agents/{agent}.md")):
            continue
        mark = os.path.join(tempfile.gettempdir(), f"ovs-nudge-{payload.get('session_id', '')}-{agent}")
        if os.path.exists(mark):
            return ""
        try:
            open(mark, "w").close()
        except OSError:
            pass
        return (f"[delegate] Việc này ({job}) nên giao agent `{agent}` (Agent tool, subagent_type={agent}) — log, diff, ảnh "
                f"chụp ở lại context của agent, phiên chính chỉ nhận khối Trạng thái. Lệnh hiện tại vẫn chạy; nhắc 1 lần/phiên.")
    return ""


def main() -> None:
    payload = read_payload()
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input") or {}
    vdir = find_validators(project_dir(payload))
    if vdir is None:
        sys.exit(0)  # không tìm thấy validators → fail-open, còn L2 đỡ

    if tool in WRITE_TOOLS:
        event = {
            "action": "write",
            "file_path": ti.get("file_path", ""),
            "content": ti.get("content") or ti.get("new_string") or "",
            "agent_type": payload.get("agent_type", ""),
        }
        checks = ["no_write_raw.py", "folder_structure.py", "patterns_guard.py"] + (["agent_scope_guard.py"] if event["agent_type"] else [])
    elif tool == "Bash":
        # session + root: rule dự án cần biết phiên nào đang chạy (P1 no-bulk-stage — commit file của phiên khác)
        event = {"action": "bash", "command": ti.get("command", ""), "session": payload.get("session_id", ""),
                 "root": project_dir(payload), "transcript_path": payload.get("transcript_path", ""),
                 "agent_type": payload.get("agent_type", "")}
        checks = (["no_write_raw.py", "patterns_guard.py"] + (["html_read_guard.py"] if ".html" in event["command"] else [])
                  + (["agent_scope_guard.py"] if event["agent_type"] else []))   # R24: chỉ agent con
    elif tool == "Read":
        # R23: chỉ .html mới tốn công gọi validator — mọi Read khác thoát ngay (Read chạy rất nhiều lần mỗi phiên)
        if not str(ti.get("file_path", "")).lower().endswith(".html"):
            sys.exit(0)
        event = {"action": "read", "file_path": ti.get("file_path", ""), "transcript_path": payload.get("transcript_path", "")}
        checks = ["html_read_guard.py"]
    else:
        sys.exit(0)

    root = project_dir(payload)
    target = event.get("file_path") or event.get("command", "")[:80]
    for name in checks:
        rc, err = run_validator(name, event, vdir)
        if rc == 2:
            record_bite(root, name[:-3] if name.endswith(".py") else name, tool, target, err)
            print(err, file=sys.stderr)
            sys.exit(2)
    if tool == "Bash":
        run_egress_guard(root, event, tool, target)
    run_local(root, event, tool, target)  # rule RIÊNG của dự án (harness-local) — sau framework
    msg = delegate_nudge(payload, tool, ti)
    if msg:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": msg}}, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
