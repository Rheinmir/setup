#!/usr/bin/env python3
"""L1/Stop: trước khi Claude kết thúc lượt — nếu phiên có sửa wiki thì index.md phải khớp (R3).
Exit 2 = chặn dừng, Claude phải sửa index trước. Có guard chống lặp vô hạn."""
import os
import re
import subprocess
import sys

from hooklib import audit, code_log, find_validators, find_wiki_dir, project_dir, read_payload, run_validator


def regen_docs(root: str) -> None:
    """Auto-fresh derived docs (overstack.html + CAPABILITIES + skill-search) NGAY khi skill/rule/
    generator đổi — CHỈ trong repo framework (có fdk/tools), fail-open. Để overstack.html (đặc biệt
    mind map) luôn TỰ cập nhật, không phải regen tay. Gác bằng git-status nên không đụng = không tốn."""
    td = os.path.join(root, "fdk", "tools")
    if not os.path.isfile(os.path.join(td, "build-overstack-docs.py")):
        return  # không phải repo framework → bỏ (overstack.html là repo-only)
    try:
        st = subprocess.run(["git", "status", "--porcelain"], cwd=root,
                            capture_output=True, text=True, timeout=8).stdout
        if not re.search(r"(skills/.*SKILL\.md|llmwiki/skills/|policy\.yaml|"
                         r"build-overstack-docs\.py|build-capabilities\.py|sync-skills\.py)", st):
            return  # phiên không đụng skill/rule/generator → khỏi regen
        for t in ("build-capabilities.py", "build-overstack-docs.py", "build-skill-search.py"):
            subprocess.run([sys.executable, os.path.join(td, t)], capture_output=True, timeout=40)
    except Exception:
        pass


def wiki_changed(root: str) -> bool:
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root, capture_output=True, text=True, timeout=10,
        ).stdout
        return "wiki/" in out
    except Exception:
        return False


def main() -> None:
    payload = read_payload()
    audit(payload, "Stop")

    if payload.get("stop_hook_active"):
        sys.exit(0)  # đã block một lần rồi → không lặp vô hạn

    root = project_dir(payload)
    code_log(root, "--render-md")  # log.md auto-block do CODE sinh từ events.jsonl (không nhờ agent ghi)
    regen_docs(root)               # overstack.html + CAPABILITIES tự cập nhật khi skill/rule đổi (repo framework)
    if not wiki_changed(root):
        sys.exit(0)  # phiên không đụng wiki → không can thiệp

    wiki = find_wiki_dir(root)
    vdir = find_validators(root)
    if wiki is None or vdir is None:
        sys.exit(0)

    rc, err = run_validator("index_sync.py", {"action": "stop", "wiki_dir": str(wiki)}, vdir)
    if rc == 2:
        print(err, file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
