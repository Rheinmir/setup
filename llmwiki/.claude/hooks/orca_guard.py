#!/usr/bin/env python3
"""L1/PreToolUse guard cho orca orchestration CLI (vendor-specific — KHÔNG phải L0 policy).

Chặn cái CHẮC, inject cái KHÔNG CHẮC (bài học 230626):
  - `orca orchestration task-update --status <X>` với X ∉ enum hợp lệ → BLOCK (exit 2) + hint.
    (orca trả ok:false lặng lẽ khi status sai — guard này biến nó thành lỗi RÕ tại chỗ.)
  - `orca orchestration task-create` → INJECT nhắc dùng `result.task.id`, không phải envelope id.
  - Mọi lệnh khác (gồm non-orca) → exit 0, im. Fail-open tuyệt đối.

Chỉ soi tool Bash. Không bao giờ làm gãy phiên: lỗi gì cũng exit 0.
"""
import re
import sys

from hooklib import audit, read_payload

# Union các version CLI: bản cũ (ready|in_progress|completed|failed) + bản mới
# (pending|ready|dispatched|completed|failed|blocked). Tránh false-block khi CLI
# thật chấp nhận 'dispatched'/'pending'/'blocked' (bài học 250626 — orca-eval).
VALID_STATUS = {"pending", "ready", "dispatched", "in_progress", "completed", "failed", "blocked"}
TASK_UPDATE_RE = re.compile(r"orca\s+orchestration\s+task-update\b")
TASK_CREATE_RE = re.compile(r"orca\s+orchestration\s+task-create\b")
STATUS_RE = re.compile(r"--status[=\s]+([^\s'\"]+)")


def emit_context(msg: str) -> None:
    import json
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": msg,
    }}, ensure_ascii=False))


def main() -> None:
    payload = read_payload()
    audit(payload, "PreToolUse")

    if payload.get("tool_name") != "Bash":
        sys.exit(0)
    cmd = (payload.get("tool_input") or {}).get("command", "") or ""

    # (1) BLOCK: task-update --status sai enum
    if TASK_UPDATE_RE.search(cmd):
        m = STATUS_RE.search(cmd)
        if m and m.group(1) not in VALID_STATUS:
            print(
                f"[orca-guard] '--status {m.group(1)}' KHÔNG hợp lệ — orca sẽ trả ok:false lặng lẽ. "
                f"Status hợp lệ: {', '.join(sorted(VALID_STATUS))}. Đổi sang 'completed' nếu ý là xong. (bài học 230626)",
                file=sys.stderr,
            )
            sys.exit(2)

    # (2) INJECT: task-create → nhắc id-trap (không chặn)
    if TASK_CREATE_RE.search(cmd):
        emit_context(
            "⟳ [orca-guard] task-create trả 2 id: envelope `id` (uuid) và `result.task.id` (task_xxxx). "
            "Mọi lệnh sau (gate-create --task, dispatch --task, task-update --id) PHẢI dùng `result.task.id`, "
            "KHÔNG dùng envelope id. (bài học 230626)"
        )
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
