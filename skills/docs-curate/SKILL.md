---
name: docs-curate
description: Sắp xếp gọn kho tài liệu LOCAL (llmwiki/html/ + wiki/sources/draft/) khi phình to. Ba tầng — PROMOTE bản chất quý lên wiki ADR/concept (travel, sống sót clone), ARCHIVE render ephemeral (cặp proposal đã xong, bản bị thay thế, report cũ → archive/), KEEP canonical — rồi RE-INDEX đầy đủ. Trigger khi "dọn docs", "sắp xếp/merge tài liệu", "tidy docs", "html/draft quá nhiều", "/docs-curate".
---

# Skill: docs-curate

## When to use
- `llmwiki/html/` hoặc `wiki/sources/draft/` tích luỹ quá nhiều file local (sau một đợt làm việc dài sinh nhiều report/proposal).
- Cảm thấy "tài liệu quý nhưng lộn xộn / khó tìm / có thể mất khi clone".

## Vì sao 3 tầng (không chỉ "merge")
Merge HTML local lại vẫn LOCAL → vẫn mất khi kéo repo ở máy khác (file html/draft là gitignored). Cái "quý" thật sự là **quyết định thiết kế / bài học / pattern** — nó phải lên **wiki** (travel + được commit). Còn render (html, draft report) là ephemeral → archive. Tool tất định lo phân loại + dời + index; phần đọc-hiểu để promote là việc của bạn (agent).

## Steps
1. **Plan (dry-run, không đụng file):**
   ```bash
   python3 fdk/tools/docs-curate.py plan        # in 3 tầng KEEP / ARCHIVE / PROMOTE?
   ```
2. **PROMOTE bản chất QUÝ vào wiki — LÀM TRƯỚC khi archive** (phán đoán của agent):
   - Với mỗi mục `PROMOTE?` và mỗi draft trong cặp proposal `ARCHIVE`: **đọc nội dung**. Nếu chứa quyết định/bài học/pattern **chưa có** trong wiki → viết thành:
     - `llmwiki/wiki/sources/adr/ADR-NNN-<slug>.md` cho một QUYẾT ĐỊNH, hoặc
     - `llmwiki/wiki/concepts/<slug>.md` cho một KHÁI NIỆM/pattern.
     Đúng frontmatter YAML (`type:`…) + `## Origin` (trỏ draft/commit nguồn). Cập nhật `wiki/index.md` + `wiki/log.md`.
   - Đã có trong wiki/git rồi → bỏ qua, chỉ để archive.
   - KHÔNG promote thứ tầm thường (report tiến độ, render trùng). Chỉ cái "đáng cho máy/người khác đọc".
3. **Apply (dời ARCHIVE + tự re-index):**
   ```bash
   python3 fdk/tools/docs-curate.py apply        # dời vào archive/, chạy build-docs-index + index_sync --fix
   ```
   Tuỳ chỉnh số mốc-ngày giữ active: `apply --keep-dates 3`.
4. **Verify + commit:** xác nhận `llmwiki/html/index.html` (dashboard) mới + `wiki/index.md` không lệch R3 (đang dev framework → chạy `fdk-gate`). Commit gồm: ADR/concept mới promote + `archive/` + index. Append `log.md`.

## Rules
- **PROMOTE trước ARCHIVE** — tuyệt đối đừng archive một draft chứa bản chất quý mà chưa kịp lên wiki (local gitignored → mất là mất thật).
- **Archive = DỜI, KHÔNG XOÁ** — file vào `archive/`, giữ nguyên (vẫn là tài liệu quý, chỉ ra khỏi workspace active).
- Canonical (`overstack.html`, `index.html`, `*-cheatsheet`, `*-health-dashboard`) KHÔNG bao giờ archive.
- Phân vai rõ: **tool** = phân loại/dời/re-index (tất định); **agent** = promote (đọc-hiểu). Không lẫn.
- Mọi wiki entry mới có `## Origin`; cập nhật `wiki/index.md` + `wiki/log.md` (rule R2/R3).
