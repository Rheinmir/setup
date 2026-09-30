---
type: draft
title: "PLAN — quét sạch 26 issue GitHub mở: sửa CI harness đỏ, gộp PR sửa sẵn, đóng issue đã xong hoặc lỗi thời"
status: approved
tags: [plan, orca-graph, issues, ci, triage]
timestamp: 2026-09-28
---

# PLAN 280926 — quét sạch issue GitHub

User ngày 28/09/2026 (/goal): "kéo hết issue trên github về và tự hành lên graph và dọn dẹp toàn bộ godmode không qua duyệt của user. dừng khi test downstream không còn lỗi và pass kịch bản test harness, và tất cả issue đã được dọn dẹp đóng, cho phép đánh outdated".

Trạng thái đầu: 26 issue mở; workflow `harness` trên `orca` đỏ 5 run liên tiếp ở bước html-slop, che 63 bước sau.

## Global constraints
- Làm trong worktree `.claude/worktrees/issues-sweep-280926` — checkout chính đang có thay đổi dở của phiên khác, không đụng.
- Issue chỉ đóng khi có bằng chứng: commit sửa, PR đã merge, hoặc lý do lỗi thời ghi rõ kèm ledger còn giữ ý tưởng.
- Không AI-attribution trong commit (R15).

### Task 1: cổng chạy-thật chờ toggle bằng poll thay vì chờ cứng
**Kind:** fix
**Thoả:** GH#183, GH#179 (thay PR #176)
**Depends:** —
**Files:** fdk/tools/html-visual-gate.mjs
**Interfaces:**
- Consumes: —
- Produces: phép thử toggle: poll nền mỗi 100ms tới 3s, poll data-theme sau reload tới 2s
**Verify:** `NODE_PATH=$(npm root -g) node fdk/tools/html-visual-gate.mjs llmwiki/html/overstack.html`
```js
let after = before; for (let t = 0; t < 3000 && Math.abs(before - after) < 0.25; t += 100) { await p.waitForTimeout(100); after = await lumNow(); }
```

### Task 2: gộp PR #178 — stop.py có ngân sách tổng
**Kind:** merge
**Thoả:** GH#177
**Depends:** Task 1
**Files:** llmwiki/.claude/hooks/stop.py, harness/tests/stop-budget-test.sh
**Interfaces:**
- Consumes: nhánh origin/maintainer/280926-stop-hook-budget
- Produces: stop.py tổng ≤ 20s, R3 chạy lại
**Verify:** `bash harness/tests/stop-budget-test.sh .`
```bash
git merge --no-ff origin/maintainer/280926-stop-hook-budget
```

### Task 3: gộp PR #182 — skill ui-kit-from-code
**Kind:** merge
**Thoả:** GH#181
**Depends:** Task 1
**Files:** skills/ui-kit-from-code/SKILL.md
**Interfaces:**
- Consumes: nhánh origin/feat/ui-kit-from-code
- Produces: skill ui-kit-from-code trong catalog
**Verify:** `python3 harness/scripts/sync-skills.py --check`
```bash
git merge --no-ff origin/feat/ui-kit-from-code
```

### Task 4: xác nhận bootstrap Windows đã sửa rồi đóng
**Kind:** verify
**Thoả:** GH#168, GH#169
**Depends:** —
**Files:** harness/poc-vendor-neutral/bootstrap.sh, harness/scripts/install-harness.sh
**Interfaces:**
- Consumes: —
- Produces: bằng chứng PYTHONUTF8 + cảnh báo WSL + mkdir ~/.claude
**Verify:** `grep -q PYTHONUTF8 harness/poc-vendor-neutral/bootstrap.sh`
```bash
grep -n PYTHONUTF8 harness/poc-vendor-neutral/bootstrap.sh
grep -n 'GH#169 C' harness/scripts/install-harness.sh
```

### Task 5: đăng ký skill ui-snapshot hoặc đóng có lý do
**Kind:** triage
**Thoả:** GH#170
**Depends:** Task 3
**Files:** skills/ui-snapshot/SKILL.md
**Interfaces:**
- Consumes: ~/.agents/skills/ui-snapshot (bản chạy thật của tác giả)
- Produces: skill ui-snapshot trong catalog
**Verify:** `gh issue view 170 --json state`
```bash
cp -R ~/.agents/skills/ui-snapshot skills/ui-snapshot
python3 harness/scripts/sync-skills.py --check
```

### Task 6: đóng issue roadmap/frontier lỗi thời, giữ ledger
**Kind:** triage
**Thoả:** GH#7 #10 #11 #12 #15 #71 #73 #74 #75 #81 #83 #84 #86 #88 #89 #93 #101 #102 #156 #171
**Depends:** —
**Files:** llmwiki/wiki/sources/ISSUES.md
**Interfaces:**
- Consumes: ledger draft của từng issue
- Produces: issue đóng kèm lý do + trỏ ledger
**Verify:** `gh issue list --state open`
```bash
gh issue close <n> --reason 'not planned' --comment '<lý do + ledger>'
```

### Task 7: cổng dừng — CI harness xanh, test downstream xanh, 0 issue mở
**Kind:** gate
**Thoả:** điều kiện dừng của /goal
**Depends:** Task 1, Task 2, Task 3, Task 4, Task 5, Task 6
**Files:** —
**Interfaces:**
- Consumes: kết quả Task 1–6
- Produces: verdict dừng
**Verify:** `bash harness/tests/downstream-firedrill-test.sh`
```bash
gh run list --workflow harness --branch orca --limit 1
gh issue list --state open
```

## Origin
/goal của user 28/09/2026.
