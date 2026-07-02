---
type: decision
title: "ADR-016: Không ghi công AI trong commit (R15 no-ai-attribution)"
status: accepted
tags: [adr, R15, no-ai-attribution, commit-msg, process-gate, harness, git-level]
timestamp: 2026-07-02
---

# ADR-016: Không ghi công AI trong commit (R15)

## Status
Accepted

## Context
Overstack được phát triển với sự hỗ trợ của AI agent (Claude Code…). Nhiều template/tool
tự chèn trailer ghi công AI vào commit message — `Co-Authored-By: Claude …`,
`🤖 Generated with Claude Code`. Trên GitHub, các trailer này biến AI thành **contributor**
hiển thị trong repo. User muốn repo **không mang dấu ghi công AI**: tác giả là con người.

Đã dọn lịch sử một lần (filter-repo + force-push, 50 trailer `Co-Authored-By` + 1
`Generated with`). Nhưng dọn thủ công không bền — lần commit sau lại dính. Cần một
**guardrail tất định** để mỗi commit tương lai không thể mang ghi công AI.

Tiêu chí (ADR-001/002):
- **Deterministic-first**: khớp regex trên commit message — luật cứng, không cần suy luận ngữ cảnh.
- **Vendor-neutral**: enforce ở tầng git (`commit-msg` hook), phủ mọi vendor/agent, không phụ thuộc lifecycle session của một tool.
- **Fail-open**: thiếu/không đọc được file message → không khoá người dùng.
- **≥2 use case**: áp cho **mọi** commit của repo.

## Decision
Thêm **R15 `no-ai-attribution`** — một `process_gate` (không phải content-check):

- **Cơ chế**: git `commit-msg` hook (pre-commit stage `commit-msg`) chạy
  `harness/validators/no_ai_attribution.py --commit-msg <MSG_FILE>`, khớp thì **exit 2** (chặn).
- **Phạm vi**: CHỈ quét **commit message** (không quét nội dung file — tránh false-positive
  với chính file/wiki đang bàn về pattern ghi công). Author/committer cũng phải là người
  (đã được lịch sử-rewrite bảo đảm, không cần validate lại từng commit).
- **Bắt**: `Co-Authored-By:` kèm tên AI (claude/anthropic/gpt/copilot/cursor/gemini/codex/llm),
  `Generated with|by <AI>`, và emoji robot 🤖.
- **Cài**: `install-harness.sh` thêm `pre-commit install --hook-type commit-msg`.
- **Khai báo**: R15 ở cả `harness/policy.yaml` (production, list) và
  `harness/poc-vendor-neutral/policy.yaml` (poc, dict) — drift-test gác parity rule-set.
- Ghi vào `/fdk` (mục Rules) như luật mềm nhắc agent; R15 là sàn cứng git-level.

## Consequences
- (+) Không commit nào lọt trailer ghi công AI về sau — guardrail thay cho dọn tay lặp lại.
- (+) Vendor-neutral: bất kỳ agent/CLI nào commit qua git đều bị gác.
- (−) `commit-msg` hook chỉ chạy ở repo đã `pre-commit install --hook-type commit-msg` — repo
  chưa cài (hoặc `git commit --no-verify`) sẽ bypass. Đây là sàn cục bộ; muốn chặt hơn cần
  thêm CI job quét commit của PR (follow-up, chưa làm).
- (−) Regex có thể miss cách diễn đạt ghi công lạ; mở rộng danh sách khi gặp thực tế.
- Fail-open theo thiết kế: lỗi hạ tầng không khoá commit.

## Origin
- **Source:** phiên 2026-07-02 — user: "thêm ràng buộc không ghi công cho AI vào /fdk … ý là nó là phần harness của framework luôn". Sau khi filter-repo dọn lịch sử + force-push toàn bộ branch/tag.
- **Liên quan:** [[rule-registry]], `ADR-001` (policy-as-source), `ADR-002` (git-level gate), `harness/validators/no_ai_attribution.py`, `policy.yaml`, `.pre-commit-config.yaml`, skill `/fdk`.
