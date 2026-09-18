---
type: issue
kind: tech-debt
title: "orca-graph verify chạy qua `subprocess.call(..., shell=True)` = POSIX sh, cú pháp bash (process substitution) fail âm thầm rc=2"
status: done
assignee: "@Rheinmir"
dispatch: Claude
entry: /fdk
tracker: "https://github.com/Rheinmir/setup/issues/166"
priority: P2
tags: [issue, orca-graph, verify, shell, tech-debt]
timestamp: 2026-09-18
id: 180926-orca-graph-verify-shell-dialect-mismatch
source_session: bonbon-v2 mockup worktree (swordtail) — dispatch task t2/t3 của graph `bonbon-v2-dna-fix` qua orca-graph thật
---

# Issue: orca-graph verify chạy dưới `sh`, không phải `bash` — cú pháp bash trong `**Verify:**` fail âm thầm

## Vấn đề (một câu)
`harness/scripts/orca-graph.py` chạy `**Verify:**`/`**QC:**` bằng `subprocess.call(cmd, shell=True)` — trên POSIX, `shell=True` luôn dùng `/bin/sh`, không phải `bash`; khi tác giả PLAN viết cú pháp chỉ-bash (điển hình: process substitution `<(...)`), lệnh fail cú pháp rc=2 và bị hiểu nhầm là "verify thật sự thất bại" thay vì "sai shell".

## Bối cảnh & bằng chứng
Trong phiên dùng orca-graph thật cho graph `bonbon-v2-dna-fix` (worktree `redesign-bonbon-v2/swordtail`), task t2 và t3 dùng `**Verify:**`:
```
node --check /dev/stdin < <(python3 -c "...")
```
Chạy qua `orca-graph.py set/reconcile` → `subprocess.call(n["verify"], shell=True)` (4 chỗ gọi giống hệt trong bản worktree) → rc=2, node bị đẩy vào `done_unverified` dù logic sửa trong file đích đã đúng. Xác nhận gốc rễ bằng tay:
```
sh -c 'node --check /dev/stdin < <(...)'   # syntax error near unexpected token `('
```
Sau khi viết lại verify không dùng cú pháp bash-only (ghi file tạm bằng Python thay vì process substitution), lệnh chạy rc=0 bình thường. Không có dòng nào trong `skills/orca-graph/SKILL.md` cảnh báo ràng buộc "Verify chạy dưới sh, tránh cú pháp chỉ-bash" — tác giả PLAN (kể cả agent) tự nhiên viết bash vì đó là shell tương tác mặc định của môi trường dev.

## Phạm vi
- `harness/scripts/orca-graph.py` — mọi điểm gọi `subprocess.call(n["verify"]/n["qc"], shell=True)`.
- `skills/orca-graph/SKILL.md` — mục hướng dẫn viết `**Verify:**`/`**QC:**` trong PLAN.
- Universal (engine dùng chung mọi project qua orca-graph), không riêng bonbon-v2.

## Không thuộc phạm vi
- Không sửa PLAN.md cụ thể của bonbon-v2 (đã tự vá tại chỗ trong worktree đó, không cần lan ở đây).
- Không đổi cơ chế lock/dispatch/reconcile — chỉ liên quan đến shell dialect lúc chạy verify/qc.

## Hướng gợi ý (không bắt buộc)
Một trong hai, chọn một:
1. Chạy verify/qc tường minh qua bash: `subprocess.call(["/bin/bash", "-c", cmd])` thay vì `shell=True` mặc định — cho phép cú pháp bash-only hoạt động như agent kỳ vọng.
2. Giữ nguyên `sh`, nhưng thêm một dòng cảnh báo rõ trong SKILL.md ngay tại chỗ dạy viết `**Verify:**`: "chạy dưới POSIX sh, không phải bash — tránh `<(...)`, `[[ ]]`, array; dùng lệnh POSIX hoặc gọi script riêng".

Khuyến nghị hướng 1 (đổi executable) vì ít bất ngờ hơn cho agent viết PLAN — họ vốn quen viết bash.

## Tiêu chí HOÀN THÀNH
- [x] Chọn 1 trong 2 hướng trên (hoặc cả hai) và áp dụng.
- [x] Test tái hiện: PLAN có `**Verify:** node --check /dev/stdin < <(echo "1+1")` chạy qua `orca-graph.py set ... done` → rc=0 (nếu chọn hướng 1) hoặc SKILL.md có dòng cảnh báo hiển nhiên (nếu chọn hướng 2).
- [x] Không phá hành vi hiện có của các PLAN.md khác đang dùng verify POSIX thuần.

## Assign & lý do
`@Rheinmir` — chủ ledger `setup` (repo framework gốc), nơi `orca-graph.py`/skill sống. `dispatch: Claude`, `entry: /fdk` vì đây là sửa lỗi hẹp, có tái hiện rõ, không cần quyết định thiết kế lớn.

## Origin
Raise bởi phiên Claude Sonnet 5 (`swordtail`, worktree `redesign-bonbon-v2`), phát hiện khi chạy thật `reconcile` cho t2/t3 của graph `bonbon-v2-dna-fix` — không phải suy đoán, có log `sh -c` tái hiện + fix tại chỗ đã verify rc=0 (`node --check` pass) trước khi raise ngược lên đây.
