---
name: frontier-scan
disable-model-invocation: true
description: "Quét biên giới agent-framework 30 ngày qua và đối chiếu overstack theo 8 trục (frontier-gap-scan runbook) — gọi INSTANT, không phải cron. Chạy 5 WebSearch, chấm Ngang/Chớm/Thua, diff kỳ trước, raise-issue cho gap mới / cập nhật gap đã có, cập nhật report. Trigger: 'frontier scan', 'quét đối thủ', 'scout tuần', 'chúng ta thua gì', '/frontier-scan'."
---

# Skill: frontier-scan

Bản gọi-INSTANT của runbook trong `fdk/wiki/concepts/frontier-gap-scan.md`. Mục tiêu: overstack là frontier TOÀN DIỆN, không ngủ trên chiến thắng. Thay cho routine cloud (bị chặn vì cần kết nối GitHub) — chạy thủ công bất cứ lúc nào, người-trong-vòng-lặp.

## When to use
- "frontier scan", "quét đối thủ", "chạy scout", "scout tuần", "chúng ta thua gì so với thế giới", "/frontier-scan".
- Định kỳ (ý định hàng tuần) hoặc khi nghe tin một framework/kỹ thuật mới đáng đối chiếu.
- **KHÔNG dùng** cho: nghiên cứu chủ đề chung (đó là `/last30days`); raise một issue lẻ đã biết (đó là `/raise-issue`).

## Steps
1. **Đọc runbook + baseline**: `fdk/wiki/concepts/frontier-gap-scan.md` và report kỳ gần nhất `llmwiki/html/overstack-vs-world-30d.html`. Nạp danh sách 8 trục + verdict kỳ trước + issue đang mở (`llmwiki/wiki/sources/ISSUES.md`, GH#9-13 + Ralph #15).
2. **Quét (5 WebSearch)**: (a) Claude Code / agent framework updates tháng này; (b) AI agent memory + context engineering; (c) self-improving agents + harness eval; (d) agent skills marketplace + supply-chain security; (e) 1 truy vấn theo tin nóng tự chọn. Giữ 4 truy vấn đầu cố định để so-sánh-được qua kỳ.
3. **Đối chiếu**: chấm 8 trục (Harness, Orchestration, Memory, Self-evolving skills, Knowledge/context, Eval/observability, Skill security, Quy mô) so với `fdk/CAPABILITIES.md` → verdict Ngang/Chớm/Thua.
4. **Diff kỳ trước**: trục nào tụt hạng? trục MỚI nào xuất hiện? Đây là tín hiệu quan trọng nhất — nêu rõ.
5. **Raise / cập nhật** (R7-f query trước để không trùng):
   - Gap MỚI hoặc XẤU ĐI chưa có issue → `/raise-issue` (ledger draft + dòng ISSUES.md + `gh issue create --assignee Rheinmir`, body link ngược ledger, thêm mục "Repo/paper tham khảo").
   - Gap đã có issue → CHỈ `gh issue comment` cập nhật bằng chứng, KHÔNG raise trùng.
6. **Report + log**: cập nhật `llmwiki/html/overstack-vs-world-30d.html` (giữ baseline cũ, thêm phần diff kỳ mới) + append 1 dòng `llmwiki/wiki/log.md`.
7. **Dừng, KHÔNG code fix**: skill này chỉ trinh sát + raise. Thực thi gap là việc phiên nhận (mở bằng `/fdk`).

## Rules
- CHỈ quét + raise/cập nhật + report. Không code, không tự-merge, không tự nâng status issue quá `open`.
- Giữ 4 truy vấn quét cố định qua các kỳ để diff có nghĩa; truy vấn thứ 5 tự do.
- Query wiki + ISSUES.md trước khi raise (R7-f) — không raise trùng gap đã có issue.
- Định nghĩa "thắng": không trục nào ở **Thua** quá 2 kỳ liên tiếp mà không có issue đang chạy.
- Repo cấm AI-attribution trong commit (R15) — nếu có commit, không thêm Co-Authored-By.
- Touch only what the task requires — no opportunistic changes.
