---
name: skill-evolve
description: Đo chất lượng thực thi của TỪNG skill riêng lẻ theo thời gian (không chỉ tần suất như skill-usage) — verdict tất định từ trace-grader, tích luỹ vào ledger; khi tỷ lệ lỗi vượt ngưỡng thì tự soạn đề xuất sửa đúng SKILL.md đó kèm nhận định LLM (agent-as-judge, mặc định bật), dừng ở /propose. Gọi khi user nói "đánh giá skill", "skill nào đang tệ", "chấm chất lượng skill", "skill-evolve", hoặc định kỳ trong /lint.
---

# Skill: skill-evolve

## When to use
- Định kỳ (vd trong `/lint`) để quét N session gần nhất, cập nhật ledger chất lượng per-skill.
- Khi muốn biết skill nào đang có tỷ lệ lỗi cao (`--report`).
- Khi một skill đã `DRAFT-ELIGIBLE` và muốn soạn đề xuất sửa nó (`--draft <skill_id>`).

## Steps
1. Quét: `python3 harness/scripts/skill-evolve.py --scan [N]` — ghi verdict per-skill vào ledger cục bộ (`harness/metrics/skill-evolve-ledger.jsonl`).
2. Xem leaderboard: `python3 harness/scripts/skill-evolve.py --report` — liệt kê skill nào `DRAFT-ELIGIBLE`.
3. Với một skill eligible: `python3 harness/scripts/skill-evolve.py --draft <skill_id>` — sinh stub tại `llmwiki/wiki/sources/draft/DDMMYY-skill-evolve-<skill_id>.md`, chứa SKILL.md hiện tại + bảng bằng chứng.
4. **Bước judge (mặc định BẬT — CHỈ chạy tới đây khi bước 3 đã thật sự sinh file, tức skill đã `DRAFT-ELIGIBLE`):** đọc nguyên văn file stub vừa sinh — cả mục `## SKILL.md hiện tại` lẫn `## Bằng chứng` — rồi tự đánh giá bằng chính reasoning của bạn (KHÔNG gọi thêm API/model nào khác — bạn CHÍNH LÀ judge): tỷ lệ lỗi này có thật sự do NỘI DUNG SKILL.md gây ra (mô tả mơ hồ, thiếu bước, sai giả định), hay do NGỮ CẢNH SỬ DỤNG (skill bị gọi sai tình huống, ngoài phạm vi "When to use")? Ghi nhận định — cụ thể, trích dẫn đúng dòng bằng chứng đã đọc, không chung chung — vào một mục MỚI `## Đánh giá LLM` chèn ngay dưới mục `## Bằng chứng` của chính file stub đó.
5. Trình file đã có `## Đánh giá LLM` cho `/propose` hoàn thiện — vẫn STOP, chờ người duyệt. `skill-evolve` không bao giờ tự sửa `SKILL.md`.

## Rules
- Bước judge (Step 4) CHỈ chạy trên file `--draft` đã sinh THẬT (skill đã `DRAFT-ELIGIBLE`) — không phán đoán trên skill chưa đủ mẫu/chưa vượt ngưỡng (tốn token vô ích, và kết luận trên mẫu nhỏ không đáng tin).
- Judge là chính agent đang gọi skill này (không phải một lệnh gọi API con) — không thêm dependency hay API key nào; tái dùng reasoning đã có sẵn trong phiên.
- Never auto-promote — nhận định LLM chỉ là MỘT mục trong stub, người duyệt vẫn phải bấm chấp thuận ở `/propose`.

## Files
| File | Role |
|------|------|
| `harness/scripts/skill-evolve.py` | engine: scan (cắt lát + chấm bằng trace-grader) / report (leaderboard) / draft (soạn stub) / self-test |
| `harness/skill-evolve.config.yaml` | adapter DUY NHẤT (`verified:false`) — `min_sample`/`fail_rate_threshold` |
| `harness/metrics/skill-evolve-ledger.jsonl` | ledger cục bộ (gitignored), verdict per-skill tích luỹ qua `bnal_metrics` |
