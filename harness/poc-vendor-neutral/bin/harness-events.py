#!/usr/bin/env python3
"""Hook sự kiện cho harness PoC (ngoài PreToolUse/llmwiki-validate):
  stop     R3 index-sync   — chặn kết thúc lượt nếu wiki/index.md lệch file thật (exit 2)
  audit    R4 log-append   — ghi .claude/audit/audit.jsonl (PostToolUse)
  session  R8 health       — in trạng thái harness lúc SessionStart (không chặn)
  docs     R10 docs-gate   — nhắc bổ sung docs mỗi N prompt (UserPromptSubmit)

MỌI lỗi → fail-open (exit 0), tuyệt đối không phá session.
"""
import glob
import json
import os
import sys


def root():
    return os.environ.get("CLAUDE_PROJECT_DIR", ".")


def _stdin():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def m_stop():
    r = root()
    idx = os.path.join(r, "llmwiki/wiki/index.md")
    if not os.path.exists(idx):
        return 0
    try:
        index = open(idx, encoding="utf-8").read()
    except OSError:
        return 0
    missing = []
    for d in ("concepts", "entities", "sources", "draft"):
        for f in glob.glob(os.path.join(r, "llmwiki/wiki", d, "**", "*.md"), recursive=True):
            base = os.path.basename(f)
            if base in ("README.md", "_template.md", "index.md", "log.md"):
                continue
            if base[:-3] not in index:
                missing.append(os.path.relpath(f, r))
    if missing:
        sys.stderr.write("[R3 index-sync] wiki/index.md chưa liệt kê: " + ", ".join(missing[:10]) +
                         ("…" if len(missing) > 10 else "") + " — cập nhật index trước khi kết thúc.\n")
        return 2
    return 0


def m_audit():
    data = _stdin()
    d = os.path.join(root(), ".claude/audit")
    try:
        os.makedirs(d, exist_ok=True)
        rec = {"tool": data.get("tool_name"), "path": (data.get("tool_input") or {}).get("file_path")}
        with open(os.path.join(d, "audit.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass
    return 0


def m_session():
    n = 0
    try:
        import yaml
        pol = os.path.join(root(), "harness/poc-vendor-neutral/policy.yaml")
        n = len((yaml.safe_load(open(pol, encoding="utf-8")) or {}).get("rules", {}))
    except Exception:
        pass
    print(f"[harness] {n} rule đang gác (policy.yaml) — vi phạm bị hook chặn ngay. Kiểm hook: /hooks")
    return 0


def m_docs():
    d = os.path.join(root(), ".claude/audit")
    every = int(os.environ.get("LLMWIKI_DOCS_GATE_EVERY", "5") or 5)
    try:
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, ".docs-gate.json")
        try:
            c = json.load(open(p)).get("n", 0)
        except Exception:
            c = 0
        c += 1
        json.dump({"n": c}, open(p, "w"))
        if every > 0 and c % every == 0:
            print("[harness R10] Đã qua vài lượt — cân nhắc bổ sung tài liệu (/docs-site-macos) cho phần vừa làm.")
    except OSError:
        pass
    return 0


def main():
    ev = sys.argv[1] if len(sys.argv) > 1 else ""
    fn = {"stop": m_stop, "audit": m_audit, "session": m_session, "docs": m_docs}.get(ev)
    try:
        sys.exit(fn() if fn else 0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
