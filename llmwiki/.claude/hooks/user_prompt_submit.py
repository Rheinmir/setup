#!/usr/bin/env python3
"""L1/UserPromptSubmit: R10 docs-gate — harness quản lý nhịp tài liệu.

Cứ mỗi N prompt (mặc định 5), soi N request gần nhất xem đã dùng
`/docs-site-macos` hoặc `/orca-workflow` chưa. Nếu CHƯA → inject 1 directive
vào context của chính prompt đó: hỏi user có muốn đánh giá & bổ sung tài liệu
cho 5 prompt vừa rồi không, và nếu đồng ý thì dispatch doc-agent dùng skill
`docs-site-macos` (CLI: opencode → agy → claude; subagent không gọi được
opencode thì dùng /orchestration). Nếu đã dùng rồi → im lặng (mục tiêu đã đạt).

Fail-open tuyệt đối: lỗi gì cũng exit 0, không bao giờ chặn prompt của user.
Đếm bằng state file (.claude/audit/.docs-gate.json) — bằng máy, không nhờ model nhớ.
"""
import json
import os
import sys
from pathlib import Path

from hooklib import audit, find_wiki_dir, project_dir, read_payload

EVERY = int(os.environ.get("LLMWIKI_DOCS_GATE_EVERY", "5") or "5")
TOKENS = ("docs-site-macos", "orca-workflow")


def load_count(state: Path, sid: str) -> int:
    try:
        data = json.loads(state.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    return int(data.get(sid, 0)) if isinstance(data, dict) else 0


def save_count(state: Path, sid: str, n: int) -> None:
    try:
        data = json.loads(state.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}
    data[sid] = n
    state.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def last_user_texts(transcript_path: str, k: int):
    """Lấy text của k user-message gần nhất từ transcript jsonl."""
    texts = []
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return texts
    for line in lines:
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get("type") != "user":
            continue
        msg = rec.get("message") or {}
        content = msg.get("content") if isinstance(msg, dict) else None
        texts.append(json.dumps(content, ensure_ascii=False) if content is not None else "")
    return texts[-k:]


def emit(msg: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": msg,
    }}, ensure_ascii=False))


def main() -> None:
    payload = read_payload()
    audit(payload, "UserPromptSubmit")

    root = Path(project_dir(payload))
    if find_wiki_dir(str(root)) is None:
        sys.exit(0)  # không phải project llmwiki → bỏ qua

    sid = payload.get("session_id") or "default"
    state = root / ".claude" / "audit" / ".docs-gate.json"
    state.parent.mkdir(parents=True, exist_ok=True)

    n = load_count(state, sid) + 1
    save_count(state, sid, n)
    if EVERY <= 0 or n % EVERY != 0:
        sys.exit(0)

    # Mốc N prompt: soi N request gần nhất (transcript) + prompt hiện tại.
    window = last_user_texts(payload.get("transcript_path", ""), EVERY)
    window.append(payload.get("prompt", "") or "")
    blob = "\n".join(window).lower()
    if any(t in blob for t in TOKENS):
        sys.exit(0)  # tài liệu đang được duy trì → không nhắc

    emit(
        f"⟳ [docs-gate R10] Đã {n} prompt; {EVERY} request gần nhất KHÔNG dùng "
        "`/docs-site-macos` hay `/orca-workflow` → tài liệu có thể đang tụt lại.\n"
        "HÀNH ĐỘNG (harness yêu cầu — hỏi user TRƯỚC khi chạy nặng):\n"
        f"1. Hỏi user: \"Có muốn đánh giá & bổ sung tài liệu cho {EVERY} prompt vừa rồi không?\"\n"
        "2. Nếu ĐỒNG Ý → dispatch 1 doc-agent dùng skill `docs-site-macos` để tổng hợp "
        f"những gì đã làm trong {EVERY} prompt qua thành trang tài liệu.\n"
        "   • Ưu tiên CLI: opencode → (fallback) agy → (fallback) claude, tùy CLI đang chạy.\n"
        "   • Subagent KHÔNG gọi được opencode → dùng `/orchestration` dispatch opencode chạy skill `docs-site-macos`.\n"
        "3. Nếu TỪ CHỐI → bỏ qua, không hỏi lại cho tới mốc prompt kế tiếp."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
