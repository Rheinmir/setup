#!/usr/bin/env python3
"""UserPromptSubmit quét OKF THEO PROMPT ở prompt đầu phiên, bơm 1 lần, chỉ trang chưa in.
Vì sao: SessionStart quét trước khi user gõ gì (truy vấn = commit subject). Test dựng repo tạm có 2 trang wiki
tiếng Anh, gửi prompt TIẾNG VIỆT: (1) prompt về tên miền → gợi ý trang domains, có biên lai mang `prompt`;
(2) prompt thứ hai cùng phiên → im lặng; (3) thông báo nền → im lặng. Chạy: python3 harness/tests/test_prompt_recall.py"""
import json, os, subprocess, sys, tempfile
from pathlib import Path
HOOKS = Path(__file__).resolve().parents[1].parent / "llmwiki" / ".claude" / "hooks"
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"

def run_hook(root, session, prompt):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(root))
    payload = {"session_id": session, "hook_event_name": "UserPromptSubmit", "cwd": str(root), "prompt": prompt,
               "transcript_path": str(root / "t.jsonl")}
    p = subprocess.run([sys.executable, str(HOOKS / "user_prompt_submit.py")], input=json.dumps(payload),
                       capture_output=True, text=True, cwd=str(root), env=env, timeout=60)
    return p.stdout

def main():
    ok = True
    def chk(c, m):
        nonlocal ok; print(("  \033[1;32m✓\033[0m " if c else "  \033[1;31m✗\033[0m ") + m); ok = ok and bool(c)
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        subprocess.run(["git", "init", "-q"], cwd=t, check=True)
        (root / ".llmwiki" / "wiki" / "concepts").mkdir(parents=True)
        (root / ".llmwiki" / ".harness-stamp").write_text("1.0.0\n")
        (root / ".llmwiki" / "wiki" / "concepts" / "domains-routing-ssl.md").write_text(
            "---\ntype: concept\ntitle: \"Domains, Routing and SSL\"\ntags: [x]\nid: d\n---\n# d\n`apps/api/src/domains/routing.ts`\n")
        (root / ".llmwiki" / "wiki" / "concepts" / "backups.md").write_text(
            "---\ntype: concept\ntitle: \"Backups\"\ntags: [x]\nid: b\n---\n# b\n")
        (root / "harness" / "scripts").mkdir(parents=True)
        for n in ("okf-scan.py", "lexrank.py", "overstack_paths.py", "bnal_config.py"):
            if (SCRIPTS / n).exists():
                (root / "harness" / "scripts" / n).write_text((SCRIPTS / n).read_text(encoding="utf-8"), encoding="utf-8")
        (root / "t.jsonl").write_text("")
        out = run_hook(root, "sessP", "sửa lỗi tên miền không cấp được chứng chỉ")
        chk("recall-prompt" in out and "domains-routing-ssl" in out and "backups" not in out,
            "prompt Việt 'tên miền' → gợi ý trang domains, không gợi backups")
        rs = json.loads(subprocess.run([sys.executable, str(root / "harness/scripts/okf-scan.py"), "receipts", "--session", "sessP",
                                        "--root", t, "--json"], capture_output=True, text=True, cwd=t).stdout or "[]")
        chk(any(r.get("prompt") and r.get("prompt_terms") for r in rs), "biên lai có prompt + prompt_terms")
        out2 = run_hook(root, "sessP", "giờ làm tiếp phần sao lưu nhé")
        chk("recall-prompt" not in out2, "prompt thứ hai cùng phiên → không bơm lại")
        out3 = run_hook(root, "sessQ", "<task-notification>xong</task-notification>")
        chk("recall-prompt" not in out3, "thông báo nền → im lặng")
    print("test_prompt_recall: " + ("PASS" if ok else "FAIL")); return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
