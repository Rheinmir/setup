#!/usr/bin/env python3
"""Stop-hook ghi MỘT episode cho MỖI PHIÊN, không phải mỗi lượt.

Đo 2026-10-13 (openship): 329 episode giống hệt nhau vì Stop chạy mỗi lượt → recall đầu phiên
toàn bản sao, agent mở thật 7/72 gợi ý. Test này dựng repo git tạm có stamp, gọi stop.py 3 lần
cùng session: (1) ghi, (2) không đổi → không ghi, (3) đổi file dirty → ghi đè cùng id.
Phiên khác → thêm record mới. Chạy: python3 harness/tests/test_episode_once_per_session.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1].parent / "llmwiki" / ".claude" / "hooks"
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def run_stop(root: Path, session: str):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(root), OVERSTACK_TOUCHED_PATHS="0",
               LLMWIKI_NO_DRIFT="1")
    payload = {"session_id": session, "hook_event_name": "Stop", "cwd": str(root),
               "transcript_path": str(root / "t.jsonl")}
    subprocess.run([sys.executable, str(HOOKS / "stop.py")], input=json.dumps(payload),
                   capture_output=True, text=True, cwd=str(root), env=env, timeout=120)


def episodes(root: Path):
    p = root / "harness" / "metrics" / "memory.jsonl"
    if not p.exists():
        return []
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]


def main() -> int:
    ok = True

    def chk(c, m):
        nonlocal ok
        print(("  \033[1;32m✓\033[0m " if c else "  \033[1;31m✗\033[0m ") + m)
        ok = ok and bool(c)

    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        subprocess.run(["git", "init", "-q"], cwd=t, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=t)
        subprocess.run(["git", "config", "user.name", "t"], cwd=t)
        (root / "a.txt").write_text("a\n")
        subprocess.run(["git", "add", "."], cwd=t)
        subprocess.run(["git", "commit", "-qm", "feat: khởi tạo"], cwd=t)
        (root / ".llmwiki").mkdir()
        (root / ".llmwiki" / ".harness-stamp").write_text("1.0.0\n")
        (root / "harness").mkdir()
        # engine repo-local để resolve_tool không phụ thuộc máy
        (root / "harness" / "scripts").mkdir()
        for n in ("mem-rank.py", "scratch-log.py", "lexrank.py", "bnal_config.py", "overstack_paths.py"):
            src = SCRIPTS / n
            if src.exists():
                (root / "harness" / "scripts" / n).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        (root / "harness" / "mem-rank.config.yaml").write_text("verified: false\neviction:\n  policy: none\n")
        (root / "t.jsonl").write_text("")
        (root / "a.txt").write_text("a\nb\n")           # dirty

        run_stop(root, "sessA")
        e1 = [m for m in episodes(root) if m.get("kind") == "episode"]
        chk(len(e1) == 1 and e1[0].get("session") == "sessA", f"lần 1: ghi 1 episode ({len(e1)})")

        run_stop(root, "sessA")
        e2 = [m for m in episodes(root) if m.get("kind") == "episode"]
        chk(len(e2) == 1, f"lần 2 cùng phiên, không đổi: KHÔNG ghi thêm ({len(e2)})")

        (root / "c.txt").write_text("c\n")
        subprocess.run(["git", "add", "c.txt"], cwd=t)      # thêm file dirty mới (staged)
        run_stop(root, "sessA")
        e3 = [m for m in episodes(root) if m.get("kind") == "episode"]
        chk(len(e3) == 1 and e3[0].get("id") == e1[0].get("id") and "c.txt" in (e3[0].get("files") or []),
            f"lần 3 cùng phiên, files đổi: ghi đè CÙNG id, files mới ({(e3 or [{}])[0].get('files')})")

        run_stop(root, "sessB")
        e4 = [m for m in episodes(root) if m.get("kind") == "episode"]
        chk(len(e4) == 2 and e4[-1].get("session") == "sessB" and e4[-1].get("parent") == "sessA",
            f"phiên khác: thêm record mới, parent = phiên trước ({len(e4)})")

    print("test_episode_once_per_session: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
