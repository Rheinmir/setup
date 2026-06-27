#!/usr/bin/env bash
# T5 — drift-test: gen-converters ↔ policy.yaml.
# out/ là gitignored (regenerate từ policy) → drift thật cần bắt KHÔNG phải "out lệch git"
# mà là "logic gen-converters DROP/lệch so với policy". Đảm bảo:
#   1) gen-converters chạy sạch
#   2) MỌI rule id trong policy xuất hiện ở advisory adapter (codex/cursor/kiro) — không drop
#   3) MỌI deny_write glob → opencode permission deny + antigravity deny
#   4) MỌI hook_event rule có `event` được wire trong claude settings, đúng kỳ vọng
#   5) MỌI event wire trong claude settings (trừ PreToolUse) map về 1 hook_event rule — không orphan
set -uo pipefail
HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POC="$HARNESS/poc-vendor-neutral"

echo "[regen] gen-converters từ policy.yaml"
python3 "$POC/gen-converters.py" >/dev/null || { echo "✗ gen-converters lỗi"; exit 1; }

python3 - "$POC" <<'PY'
import json, sys, pathlib, yaml
poc = pathlib.Path(sys.argv[1]); out = poc / "out"
rules = (yaml.safe_load((poc / "policy.yaml").read_text(encoding="utf-8")) or {})["rules"]
PASS, FAIL = [], []
def chk(name, cond): (PASS if cond else FAIL).append(name)

# 2) mọi rule id có trong advisory (codex + cursor + kiro)
adv = "".join((out / p).read_text(encoding="utf-8") for p in (
    "codex/AGENTS.snippet.md", "cursor/.cursor/rules/harness.mdc", "kiro/.kiro/steering/harness.md"))
for r in rules.values():
    chk(f"advisory chứa {r['id']}", f"({r['id']})" in adv)

# 3) deny_write globs → opencode + antigravity
deny = [g for r in rules.values() if r.get("kind") == "deny_write" for g in r.get("deny_write_globs", [])]
oc = json.loads((out / "opencode/opencode.json").read_text(encoding="utf-8"))
ag = (out / "antigravity/permissions.snippet.txt").read_text(encoding="utf-8")
for g in deny:
    chk(f"opencode deny {g}", oc["permission"]["edit"].get(g) == "deny")
    chk(f"antigravity deny {g}", g in ag)

# 4) hook_event → claude settings event wiring đúng kỳ vọng
claude = json.loads((out / "claude/settings.snippet.json").read_text(encoding="utf-8"))
hooks = claude["hooks"]
EXPECT = {"R3": "Stop", "R4": "PostToolUse", "R8": "SessionStart", "R10": "UserPromptSubmit"}
for r in rules.values():
    if r.get("kind") == "hook_event":
        ev = r.get("event")
        chk(f"{r['id']} event {ev} wired", ev in hooks and len(hooks[ev]) > 0)
        chk(f"{r['id']} event khớp kỳ vọng", EXPECT.get(r["id"]) == ev)
        # policy-drives-wiring: rule phải có event_action, và lệnh sinh ra phải tham chiếu nó
        act = r.get("event_action")
        chk(f"{r['id']} có event_action (policy-driven)", bool(act))
        if act and ev in hooks:
            cmd = hooks[ev][0]["hooks"][0]["command"]
            chk(f"{r['id']} lệnh hook chứa action '{act}'", act in cmd)

# 5) reverse — mọi event wire (trừ PreToolUse=content rules) phải có hook_event rule
he_events = {r.get("event") for r in rules.values() if r.get("kind") == "hook_event"}
for ev in set(hooks) - {"PreToolUse"}:
    chk(f"event {ev} có hook_event rule (không orphan)", ev in he_events)
chk("PreToolUse wired (content rules)", len(hooks.get("PreToolUse", [])) > 0)

for p in PASS: print("  ✓", p)
for f in FAIL: print("  ✗", f)
print(f"\n── drift-test: PASS={len(PASS)} FAIL={len(FAIL)} ──")
sys.exit(1 if FAIL else 0)
PY
