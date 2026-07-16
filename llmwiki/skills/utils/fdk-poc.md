---
name: fdk-poc
description: >-
  POC "luồng chạy THẬT, nhanh, ít-phải-nhớ": tạo một PROJECT MỚI rồi chạy trọn vòng đời /br
  trong đó bằng LỆNH THẬT tất định (frame-lint, build-line-status, qc-regression trỏ --root vào
  project mới), đo giờ + verify SENTINEL từng bước, xuất trang HTML visualize. Trả lời 3 câu:
  luồng gõ NHỮNG LỆNH NÀO · NHANH không (wall-clock từng bước) · phải NHỚ NHIỀU không (đếm hub,
  mục tiêu 1 — mọi thứ dưới /br, tool phụ tự fire). Cùng tinh thần fdk-uat (chứng bằng chạy thật
  + grep sentinel, không tin lời model). Gọi khi user nói "fdk-poc", "poc luồng", "visualize luồng
  br chạy", "chạy thử project mới", "/fdk-poc".
---

# Skill: fdk-poc — POC luồng /br chạy thật + visualize

## When to use
- Muốn THẤY (không chỉ nghe) rằng luồng overstack/br chạy được, nhanh, và ít phải nhớ.
- Trước khi giới thiệu /br cho người mới: một trang visualize "gõ lệnh nào → tự fire lệnh nào → mất bao lâu".
- KHÔNG dùng để: chạy sản phẩm thật (đó là `/br run`) hay UAT một tính năng (đó là fdk-uat thủ tục verify).

## Cách chạy (một lệnh)
```
python3 fdk/tools/fdk-poc.py run [--out llmwiki/html/DDMMYY-fdk-poc.html] [--keep] [--json]
```
- Tạo project tạm mới (`/tmp/fdk-poc-*`), chạy 7 bước vòng đời (bootstrap → interview → compile → slice → run → qc → status).
- Mỗi bước chạy **lệnh THẬT** của tool tất định trỏ `--root` vào project mới, đo `ms`, verify **sentinel** (file artifact tồn tại + chứa needle) → chứng bước THẬT xảy ra, không phải khai.
- Bước LLM duy nhất (`/br run` → loop-runner gọi `claude -p`) KHÔNG chạy (đắt, không tất định) — đánh dấu `llm:true`, phần còn lại là chi phí THẬT của harness.
- Xuất `llmwiki/html/DDMMYY-fdk-poc.html` (macOS glass, self-contained): KPI (hub-phải-nhớ · lệnh-user · lệnh-nội-bộ · wall-clock) + timeline từng bước (auto-substeps) + biểu đồ thời gian + kết luận "phải nhớ nhiều không".
- `--keep` giữ project tạm để soi; `--json` in trace; `--self-test` kiểm bất biến.

## Đọc kết quả
- **hub phải nhớ** → mục tiêu ≈ **1** (`/br`) + `bootstrap` chạy một lần. 6/7 lệnh gom dưới `/br <mode>` (hub MỘT tên fan-out — xem discoverability).
- **lệnh nội bộ tự fire** (frame-lint · loop-runner · qc-regression · build-line-status · checkpoint…) → user KHÔNG gõ, KHÔNG nhớ tên chúng.
- **wall-clock tất định** → phần harness (không tính bước LLM) là mili-giây.
- **sentinel ALL PASS** → luồng THẬT tạo đủ artifact.

## Rules
- **Chứng bằng chạy thật + sentinel** (tinh thần fdk-uat) — không "cho pass" bằng suy luận; file artifact phải tồn tại thật.
- **Bước LLM đánh dấu trung thực** — không giả vờ chạy loop-runner; ghi `llm:true` + để phần tất định nói lên tốc độ.
- **Tất định, offline** — POC không gọi mạng/LLM; chạy lại cho cùng kết quả (trừ mili-giây).
- HTML self-contained + in full-path (R16), có toggle sáng/tối nếu mở rộng.

## Related
- `fdk/tools/fdk-poc.py` — runner + emit HTML.
- `fdk/tools/frame-lint.py` · `fdk/tools/build-line-status.py` · `harness/scripts/qc-regression.py` — tool THẬT mà POC chạy.
- `skills/br/SKILL.md` — vòng đời được demo.
