#!/usr/bin/env python3
"""arch-scan: quét xung đột "văn bản vs luật" trong skill/doc — 0 token, chạy pre-commit/cron.

4 check (đúc từ audit 2026-06-12 bắt được 3 lỗi thật):
  C1  flag --dangerously-skip-permissions trong lệnh (classifier sẽ deny) — bỏ qua dòng cảnh báo
  C2  đường dẫn wiki/<dir>/ ngoài allowlist R5 (lookbehind chống false-positive llmwiki/)
  C3  path llmwiki/skills/... được tham chiếu nhưng không tồn tại (stale)
  C4  file wiki/<x>.md ở root ngoài allowlist

Usage: arch-scan.py [--root DIR] [--scan-global] [--warn-only] [files...]
  mặc định quét <root>/llmwiki/{skills,CLAUDE.md,AGENT.md}; --scan-global thêm ~/.agents/skills
Exit 0 = sạch · 2 = có finding (0 nếu --warn-only)
"""
import re
import sys
from pathlib import Path

R5_DIRS = {"concepts", "entities", "sources", "draft"}
ROOT_MD = {"index.md", "log.md", "README.md", "active-context.md", "decisions.md", "_template.md"}
FLAG = "--dangerously-skip-permissions"
WIKI_DIR_RE = re.compile(r"(?<![a-zA-Z])wiki/([a-z][a-z0-9-]*)/")
WIKI_ROOTMD_RE = re.compile(r"(?<![a-zA-Z])wiki/([A-Za-z][\w-]*\.md)")
SKILL_PATH_RE = re.compile(r"llmwiki/skills/[\w./-]+\.md")


def scan_file(p, repo_root, findings):
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for i, line in enumerate(text.splitlines(), 1):
        if FLAG in line and "KHÔNG" not in line and "⚠" not in line and "DENY" not in line:
            findings.append(f"C1 {p}:{i} — flag bị classifier chặn: dispatch sẽ không bao giờ chạy được")
        for m in WIKI_DIR_RE.finditer(line):
            if m.group(1) not in R5_DIRS:
                findings.append(f"C2 {p}:{i} — 'wiki/{m.group(1)}/' vi phạm R5 (chỉ {sorted(R5_DIRS)})")
        for m in WIKI_ROOTMD_RE.finditer(line):
            if m.group(1) not in ROOT_MD and "/" not in m.group(1):
                findings.append(f"C4 {p}:{i} — 'wiki/{m.group(1)}' ở wiki root ngoài allowlist")
        for m in SKILL_PATH_RE.finditer(line):
            rel = m.group(0)
            if repo_root and not (repo_root / rel).exists() and "<" not in rel:
                findings.append(f"C3 {p}:{i} — path stale: {rel} không tồn tại")


def main():
    args = sys.argv[1:]
    warn = "--warn-only" in args
    scan_global = "--scan-global" in args
    root = Path(".")
    if "--root" in args:
        root = Path(args[args.index("--root") + 1])
    files = [Path(a) for a in args if not a.startswith("--") and a != str(root) and Path(a).is_file()]
    if not files:
        for pat in ("llmwiki/skills/**/*.md", "llmwiki/CLAUDE.md", "llmwiki/AGENT.md"):
            files += list(root.glob(pat))
        if scan_global:
            files += list(Path.home().glob(".agents/skills/*/SKILL.md"))
    repo_root = root if (root / "llmwiki" / "skills").is_dir() else None
    findings = []
    for f in files:
        scan_file(f, repo_root, findings)
    if findings:
        print(f"[arch-scan] {len(findings)} xung đột văn-bản-vs-luật:", file=sys.stderr)
        for x in findings:
            print("  " + x, file=sys.stderr)
        sys.exit(0 if warn else 2)
    sys.stdout.buffer.write(f"[arch-scan] sach ({len(files)} files)\n".encode("utf-8"))


if __name__ == "__main__":
    main()
