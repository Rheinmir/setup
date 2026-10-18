#!/usr/bin/env python3
"""R24 agent-scope-guard: AGENT CON không được làm cổng xanh bằng cách nới cổng.

Đo 06/10/2026: hook PreToolUse chạy cả trong agent con (payload mang agent_id + agent_type, CÙNG session_id/transcript
với phiên chính) — nên R2/R23… vẫn cắn. Lỗ còn lại: bị chặn thì agent con tự quyết cách xử lý, có thể sửa chính
validator/test/policy hoặc bỏ cổng (`--no-verify`, `SKIP=`). Lời dặn trong định nghĩa agent không đủ — cổng này chặn cứng.
Phiên chính (không có agent_type) không bị đụng: người/agent chính sửa harness là việc bình thường của /fdk.
Thoát: OVERSTACK_AGENT_HARNESS_EDIT=1 (khi CHÍNH user giao agent con sửa harness).

Contract: stdin JSON {"action":"write"|"bash","file_path"|"command","agent_type"}. Exit 0/2. Fail-open khi parse lỗi.
"""
import json
import os
import re
import sys

# Mẫu KHỚP (không phải path để mở) — phủ cả 3 layout: repo framework (harness/…), dự án khách (.harness/…, .llmwiki/…),
# engine global (~/.claude/harness/hooks/validators/…). Bản đầu chỉ phủ layout repo → agent con ở dự án khách sửa validator global lọt.
PROTECTED = re.compile(r"(^|/)\.?(harness/(validators|tests|hooks/validators|poc-vendor-neutral)/"   # bare-path: ok mẫu khớp, phủ mọi layout
                       r"|harness/(poc-vendor-neutral/)?policy\.yaml|harness/scripts/harness-doctor\.py"         # bare-path: ok mẫu khớp
                       r"|llmwiki/\.claude/hooks/validators/|llmwiki/wiki/sources/evals/|wiki/sources/evals/"   # bare-path: ok mẫu khớp
                       r"|\.pre-commit-config\.yaml|test_[\w-]+\.py$|[\w-]+-test\.sh$)")
MUTATORS = {"sed", "tee", "rm", "mv", "cp", "truncate", "perl", "chmod", "ln"}   # lệnh mà ĐỐI SỐ là đích ghi
REDIRECT = re.compile(r">{1,2}\s*(\S+)")                                            # `> file` / `>> file`: đích ghi là file sau dấu >
BYPASS = re.compile(r"--no-verify\b|\bSKIP=|\bPRE_COMMIT_ALLOW_NO_CONFIG\b|\bHUSKY=0\b")


def problem(ev: dict):
    if not ev.get("agent_type") or os.environ.get("OVERSTACK_AGENT_HARNESS_EDIT") == "1":
        return None
    if ev.get("action") == "write" and PROTECTED.search(ev.get("file_path", "")):
        return f"agent con ({ev['agent_type']}) không được sửa file cổng kiểm {ev['file_path']}"
    cmd = ev.get("command", "")
    if ev.get("action") == "bash":
        if BYPASS.search(cmd):
            return f"agent con ({ev['agent_type']}) không được bỏ qua cổng ({BYPASS.search(cmd).group(0)})"
        # Chỉ chặn khi ĐÍCH GHI của chính đoạn lệnh là file cổng kiểm. Bản đầu chặn khi "có thao tác ghi" và "có path cổng"
        # ở BẤT KỲ đâu trong lệnh → `pytest harness/tests/x.py | tee /scratch/log` bị chặn nhầm (gate-runner bắt được 06/10/2026).
        for seg in re.split(r"[|;&]+|&&", cmd):
            words = seg.split()
            if any(PROTECTED.search("/" + t) for t in REDIRECT.findall(seg)):
                return f"agent con ({ev['agent_type']}) không được ghi đè file cổng kiểm qua Bash (redirect)"
            head = os.path.basename(words[0]) if words else ""
            git_mut = head == "git" and len(words) > 1 and words[1] in ("checkout", "restore", "rm")
            if (head in MUTATORS or git_mut) and any(PROTECTED.search("/" + w) for w in words[1:]):
                return f"agent con ({ev['agent_type']}) không được sửa file cổng kiểm qua Bash ({head})"
    return None


def main():
    if sys.argv[1:] == ["--self-test"]:
        return self_test()
    try:
        ev = json.load(sys.stdin)
    except ValueError:
        return
    p = problem(ev)
    if p:
        print(f"[R24 agent-scope-guard] {p}. Cổng đỏ mà nghi cổng gác sai → DỪNG, báo lại phiên chính kèm lệnh tái hiện; "
              f"không nới cổng. (User giao sửa harness → OVERSTACK_AGENT_HARNESS_EDIT=1.)", file=sys.stderr)
        sys.exit(2)


def self_test():
    a = {"agent_type": "gate-runner"}
    assert problem({**a, "action": "write", "file_path": "/r/harness/validators/html_slop.py"})  # bare-path: ok fixture self-test
    assert problem({**a, "action": "write", "file_path": "/r/harness/tests/test_md_render.py"})
    assert problem({**a, "action": "write", "file_path": "/r/harness/policy.yaml"})
    assert problem({**a, "action": "write", "file_path": "/r/fdk/wiki/sources/evals/teach-me-x.md"}), "golden eval là dữ liệu kiểm"
    assert not problem({**a, "action": "write", "file_path": "/r/fdk/tools/md-render.py"}), "code thường được sửa"
    assert not problem({"action": "write", "file_path": "/r/harness/validators/x.py"}), "phiên chính không bị đụng"  # bare-path: ok fixture self-test
    assert problem({**a, "action": "bash", "command": "git commit --no-verify -m x"})
    assert problem({**a, "action": "bash", "command": "SKIP=r20 git commit -m x"})
    assert problem({**a, "action": "bash", "command": "sed -i 's/2/0/' harness/validators/html_slop.py"})  # bare-path: ok fixture self-test
    assert not problem({**a, "action": "bash", "command": "python3 harness/validators/html_slop.py x.html"}), "chạy validator được"  # bare-path: ok fixture self-test
    assert not problem({**a, "action": "bash", "command": "python3 -m pytest -q harness/tests/test_md_render.py"}), "chạy test được"
    assert not problem({**a, "action": "bash", "command": "python3 -m pytest -q harness/tests/test_md_render.py 2>&1 | tee /tmp/s/gate-1.log"}), \
        "dương tính giả 06/10: chạy test rồi tee log RA NGOÀI phải được"
    assert not problem({**a, "action": "bash", "command": "python3 harness/scripts/harness-doctor.py > /tmp/s/doctor.log"})  # bare-path: ok fixture self-test
    assert problem({**a, "action": "bash", "command": "echo x > harness/validators/html_slop.py"}), "redirect vào validator phải chặn"  # bare-path: ok fixture self-test
    assert problem({**a, "action": "bash", "command": "git checkout -- harness/tests/test_md_render.py"})
    assert problem({**a, "action": "write", "file_path": "/Users/u/.claude/harness/hooks/validators/html_slop.py"}), "engine global (máy khách)"
    assert problem({**a, "action": "write", "file_path": "/proj/.harness/poc-vendor-neutral/policy.yaml"}), "dự án khách layout dot"
    assert problem({**a, "action": "write", "file_path": "/proj/.llmwiki/wiki/sources/evals/x.md"}), "golden eval layout dot"
    os.environ["OVERSTACK_AGENT_HARNESS_EDIT"] = "1"
    assert not problem({**a, "action": "write", "file_path": "/r/harness/validators/x.py"}); del os.environ["OVERSTACK_AGENT_HARNESS_EDIT"]  # bare-path: ok fixture self-test
    print("agent_scope_guard --self-test: 19/19 ok")


if __name__ == "__main__":
    main()
