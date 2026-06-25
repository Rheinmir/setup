#!/usr/bin/env python3
"""llmwiki-validate — LÕI gác cổng vendor-neutral (PoC).

Một lõi duy nhất đọc policy.yaml và áp luật. Mọi vendor (Claude hook, opencode
plugin, pre-commit, CI…) chỉ là caller MỎNG gọi CLI này — không dính API riêng
vendor nào. "Não" nằm ở đây + policy.yaml; adapter chỉ là dây nối.

Modes:
  path <FILE>     kiểm 1 path ghi          (layer=session)  exit 2 = chặn
  files <F...>    kiểm nhiều file trên disk (layer=repo)     exit 1 = có vi phạm
  claude-hook     đọc PreToolUse JSON Claude từ stdin (layer=session) exit 2 = chặn

Lý do ghi ra stderr. Thiếu policy / payload hỏng => fail-open (exit 0) — đúng triết
lý harness: lỗi hạ tầng không được chặn người dùng; tầng repo (CI) vẫn đỡ.
"""
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("llmwiki-validate: thiếu pyyaml (pip install pyyaml) — fail-open\n")
    sys.exit(0)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_POLICY = os.path.normpath(os.path.join(HERE, "..", "policy.yaml"))

# bash ghi vào raw/ (mượn semantics no_write_raw.py)
BASH_WRITE = re.compile(r"(?:>>?|\btee\b(?:\s+-a)?|\btouch\b|\bsed\s+-i\S*)\s+['\"]?(?:\S*/)?raw/")
BASH_COPY = re.compile(r"\b(?:cp|mv|rsync)\b[^|;&]*\s['\"]?(?:\S*/)?raw/\S*['\"]?\s*(?:$|[|;&])")


def glob_to_regex(glob):
    """Glob → regex, hỗ trợ ** xuyên thư mục, * trong 1 segment, ?."""
    i, n, out = 0, len(glob), ["^"]
    while i < n:
        ch = glob[i]
        if ch == "*":
            if glob[i:i + 3] == "**/":
                out.append("(?:.*/)?"); i += 3; continue
            if glob[i:i + 2] == "**":
                out.append(".*"); i += 2; continue
            out.append("[^/]*"); i += 1; continue
        if ch == "?":
            out.append("[^/]"); i += 1; continue
        out.append(re.escape(ch)); i += 1
    out.append("$")
    return re.compile("".join(out))


def norm(path):
    p = (path or "").replace("\\", "/")
    return p[2:] if p.startswith("./") else p


def load_policy(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except OSError:
        return None


def rules_for_layer(policy, layer):
    out = []
    for name, r in (policy.get("rules") or {}).items():
        if layer in (r.get("enforce_at") or []):
            out.append((name, r))
    return out


def _tag(rule):
    return f"{rule.get('id', '?')} {rule.get('name', rule.get('kind', ''))}"


# ---- rule kinds ----
def check_deny_write_path(path, rule):
    p = norm(path)
    for g in rule.get("deny_write_globs", []):
        if glob_to_regex(g).match(p):
            return f"[{_tag(rule)}] chặn ghi: {p} — {rule.get('statement', '')}"
    return None


def check_deny_write_bash(command, rule):
    cmd = command or ""
    if "raw/" in cmd and (BASH_WRITE.search(cmd) or BASH_COPY.search(cmd)):
        return f"[{_tag(rule)}] chặn bash ghi raw/: {cmd[:100]}"
    return None


def check_require_section(path, content, rule):
    p = norm(path)
    if os.path.basename(p) in (rule.get("exclude_basenames") or []):
        return None
    if not any(glob_to_regex(g).match(p) for g in rule.get("target_globs", [])):
        return None
    if content is None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            return None
    sect = rule.get("require_section", "")
    # khớp linh hoạt khoảng trắng giữa token ("##  Origin" ok), chặt ở biên ("## Origins" KHÔNG tính)
    toks = [re.escape(t) for t in sect.split()]
    pat = "^" + r"\s+".join(toks) + r"(?=\s|$)" if toks else "^"
    if not re.search(pat, content, re.MULTILINE):
        return f"[{_tag(rule)}] {p} thiếu '{sect}' — {rule.get('statement', '')}"
    return None


# ---- modes ----
def mode_path(policy, filepath):
    v = []
    for _, r in rules_for_layer(policy, "session"):
        if r.get("kind") == "deny_write":
            m = check_deny_write_path(filepath, r)
            if m:
                v.append(m)
    return v


def mode_claude_hook(policy):
    try:
        data = json.load(sys.stdin)
    except Exception:
        return []  # fail-open
    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {}) or {}
    v = []
    for _, r in rules_for_layer(policy, "session"):
        kind = r.get("kind")
        if tool in ("Write", "Edit", "MultiEdit"):
            if kind == "deny_write":
                m = check_deny_write_path(ti.get("file_path", ""), r)
            elif kind == "require_section":
                m = check_require_section(ti.get("file_path", ""), ti.get("content"), r)
            else:
                m = None
        elif tool == "Bash":
            m = check_deny_write_bash(ti.get("command", ""), r) if kind == "deny_write" else None
        else:
            m = None
        if m:
            v.append(m)
    return v


def mode_files(policy, files):
    v = []
    repo = rules_for_layer(policy, "repo")
    for fp in files:
        for _, r in repo:
            kind = r.get("kind")
            if kind == "require_section":
                m = check_require_section(fp, None, r)
            elif kind == "deny_write":
                m = check_deny_write_path(fp, r)
            else:
                m = None
            if m:
                v.append(m)
    return v


def main():
    args = sys.argv[1:]
    policy_path = DEFAULT_POLICY
    if args and args[0] == "--policy":
        policy_path = args[1]
        args = args[2:]
    if not args:
        sys.stderr.write("usage: llmwiki-validate.py [--policy P] {path <FILE>|files <F...>|claude-hook}\n")
        sys.exit(0)

    policy = load_policy(policy_path)
    if policy is None:
        sys.stderr.write(f"llmwiki-validate: không đọc được policy {policy_path} — fail-open\n")
        sys.exit(0)

    mode, rest = args[0], args[1:]
    if mode == "path":
        if not rest:
            sys.exit(0)
        viol = mode_path(policy, rest[0])
        block_code = 2
    elif mode == "claude-hook":
        viol = mode_claude_hook(policy)
        block_code = 2
    elif mode == "files":
        viol = mode_files(policy, rest)
        block_code = 1
    else:
        sys.stderr.write(f"llmwiki-validate: mode lạ '{mode}' — fail-open\n")
        sys.exit(0)

    if viol:
        for m in viol:
            sys.stderr.write(m + "\n")
        sys.exit(block_code)
    sys.exit(0)


if __name__ == "__main__":
    main()
