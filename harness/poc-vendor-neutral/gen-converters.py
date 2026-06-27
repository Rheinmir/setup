#!/usr/bin/env python3
"""gen-converters — đọc policy.yaml, SINH wiring cho từng vendor vào out/.

MỘT nguồn (policy.yaml) → nhiều adapter MỎNG. Mỗi file sinh ra có header GENERATED:
đừng sửa tay — sửa policy.yaml rồi chạy lại. Đây chính là "luồng cài đặt" B2/B3:
mỗi vendor được ghi WIRING native, KHÔNG vendor nào cần MCP.

Phân tầng (đã kiểm chứng 2026-06-25):
  deny-được, dùng native + CLI : claude (hook→CLI) · opencode (permission.edit:deny) · antigravity (Deny-rule)
  chỉ-nhắc (advisory text)      : cursor · codex · kiro
  phủ MỌI vendor (sàn đảm bảo)  : pre-commit + CI (gọi CLI files mode)
"""
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("gen-converters: cần pyyaml (pip install pyyaml)")

HERE = os.path.dirname(os.path.abspath(__file__))
POLICY = os.path.join(HERE, "policy.yaml")
OUT = os.path.join(HERE, "out")
# Đường gọi CLI trong các config sinh ra (chỉnh theo vị trí harness thực tế của bạn).
CLI = "harness/poc-vendor-neutral/bin/llmwiki-validate.py"
GEN = "# ⚙️  GENERATED FROM policy.yaml — đừng sửa tay; sửa policy.yaml rồi chạy gen-converters.py"


def write(rel, content):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✎ out/{rel}")


def main():
    with open(POLICY, encoding="utf-8") as f:
        policy = yaml.safe_load(f)
    rules = policy.get("rules", {})
    deny = {n: r for n, r in rules.items() if r.get("kind") == "deny_write"}
    deny_globs = [g for r in deny.values() for g in r.get("deny_write_globs", [])]
    statements = [f"- ({r.get('id')}) {r.get('statement')}" for r in rules.values()]

    print("gen-converters: sinh wiring từ policy.yaml →")

    # ---- 1. Claude — PreToolUse (lõi chặn) + 4 hook sự kiện R3/R4/R8/R10 ----
    import json
    EVT = "harness/poc-vendor-neutral/bin/harness-events.py"
    def _ev(c, t=15): return [{"type": "command", "command": c, "timeout": t}]
    # CHẶN-ĐƯỢC (PreToolUse/Stop): exec giữ exit 2 khi script chặn; file THIẾU → exit 0 (fail-open, không khoá cứng)
    def _block(f, a): return f'[ -f "$CLAUDE_PROJECT_DIR/{f}" ] && exec python3 "$CLAUDE_PROJECT_DIR/{f}" {a} || exit 0'
    # R12 gate1: bash script, chỉ chạy nếu tồn tại (repo framework); offline → fail-open trong chính script
    def _block_sh(f, a): return f'[ -f "$CLAUDE_PROJECT_DIR/{f}" ] && exec bash "$CLAUDE_PROJECT_DIR/{f}" {a} || exit 0'
    PULLGATE = "harness/poc-vendor-neutral/bin/pull-gate.sh"
    # KHÔNG-CHẶN (PostToolUse/SessionStart/UserPromptSubmit): LUÔN exit 0 — file thiếu/lỗi KHÔNG bao giờ chặn input
    def _info(f, a): return f'python3 "$CLAUDE_PROJECT_DIR/{f}" {a} 2>/dev/null || true'
    claude = {
        "_generated": GEN,
        "hooks": {
            "PreToolUse": [
                {"matcher": "Write|Edit|MultiEdit|Bash", "hooks": _ev(_block(CLI, "claude-hook"))},   # R1/R2/R5/R7/R9
                {"matcher": "Write|Edit|MultiEdit", "hooks": _ev(_block_sh(PULLGATE, "gate1"))},       # R12 gate1
            ],
            "PostToolUse": [{"matcher": "Write|Edit|MultiEdit", "hooks": _ev(_info(EVT, "audit"), 10)}],          # R4
            "Stop": [{"hooks": _ev(_block(EVT, "stop"))}],                                                        # R3
            "SessionStart": [{"hooks": _ev(_info(EVT, "session"), 10)}],                                          # R8
            "UserPromptSubmit": [{"hooks": _ev(_info(EVT, "docs"), 10)}],                                         # R10
        },
    }
    write("claude/settings.snippet.json", json.dumps(claude, ensure_ascii=False, indent=2) + "\n")

    # ---- 2. opencode (deny: permission.edit:deny NATIVE — không cần CLI lúc chạy) ----
    perm = {"*": "allow"}
    for g in deny_globs:
        perm[g] = "deny"
    opencode = {
        "$schema": "https://opencode.ai/config.json",
        "_generated": GEN,
        "permission": {"edit": perm},
    }
    write("opencode/opencode.json", json.dumps(opencode, ensure_ascii=False, indent=2) + "\n")
    # plugin gọi CLI (cho luật permission-glob không diễn tả được, vd require_origin)
    plugin = f"""// {GEN}
// opencode plugin: gọi CÙNG CLI lõi cho các luật mà permission.edit không biểu diễn được.
export const HarnessPlugin = async ({{ $ }}) => ({{
  "tool.execute.before": async (input, output) => {{
    if (!["edit", "write", "patch"].includes(input.tool)) return;
    const path = (output.args && (output.args.filePath || output.args.path)) || "";
    const res = await $`python3 {CLI} path ${{path}}`.quiet().nothrow();
    if (res.exitCode === 2) throw new Error(res.stderr.toString() || "harness deny");
  }},
}});
"""
    write("opencode/plugin/harness.js", plugin)

    # ---- 3. Antigravity (deny: Permission Deny-rule theo path) ----
    ag = [GEN.replace("# ", "# "), "# Antigravity — Permissions › Deny tier (Deny > Ask > Allow).",
          "# Dán vào cấu hình Permissions của project; chặn TRƯỚC khi ghi.", "Deny:"]
    for g in deny_globs:
        ag.append(f"  - write_file({g})")
    write("antigravity/permissions.snippet.txt", "\n".join(ag) + "\n")

    # ---- 4. advisory (chỉ-nhắc): cursor / codex / kiro ----
    body = "\n".join(statements)
    cursor = f"""---
description: llmwiki harness rules (advisory — KHÔNG enforce; sàn đảm bảo là CI)
alwaysApply: true
---
{GEN}

# Quy tắc harness (bắt buộc tuân)
{body}

> ⚠️ Cursor không có hook chặn ghi-file trực tiếp → đây chỉ là NHẮC. Đảm bảo thật ở CI + pre-commit.
"""
    write("cursor/.cursor/rules/harness.mdc", cursor)
    write("codex/AGENTS.snippet.md",
          f"<!-- {GEN} -->\n\n## Harness rules (advisory)\n{body}\n\n"
          f"> Codex: AGENTS.md hay drift giữa phiên → đây chỉ là NHẮC. Đảm bảo thật ở CI.\n")
    write("kiro/.kiro/steering/harness.md",
          f"<!-- {GEN} -->\n---\ninclusion: always\n---\n\n# Harness rules (advisory)\n{body}\n\n"
          f"> Kiro steering hay bị bỏ qua → NHẮC thôi. Đảm bảo thật ở CI.\n")

    # ---- 5. SÀN: CI (gọi CLI files mode = layer repo) ----
    ci = f"""# {GEN.lstrip('# ')}
name: harness
on: [pull_request, push]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: {{ fetch-depth: 0 }}
      - uses: actions/setup-python@v5
        with: {{ python-version: '3.x' }}
      - run: pip install pyyaml
      - name: harness validator (layer=repo) trên file .md đổi
        run: |
          base="${{{{ github.event.pull_request.base.sha || github.event.before }}}}"
          files=$(git diff --name-only "$base" HEAD 2>/dev/null | grep -E '\\.md$' || true)
          [ -z "$files" ] && {{ echo "no changed .md"; exit 0; }}
          python3 {CLI} files $files
"""
    write("ci/harness.yml", ci)

    # ---- 6. SÀN: pre-commit (gọi CLI files mode) ----
    pc = f"""# {GEN.lstrip('# ')}
# Thêm vào .pre-commit-config.yaml của project:
- repo: local
  hooks:
    - id: llmwiki-harness
      name: llmwiki harness validator (layer=repo)
      entry: python3 {CLI} files
      language: system
      files: '\\.md$'
"""
    write("pre-commit-snippet.yaml", pc)

    print("Xong. Tất cả sinh từ 1 policy.yaml. Sửa luật ở policy.yaml → chạy lại file này.")


if __name__ == "__main__":
    main()
