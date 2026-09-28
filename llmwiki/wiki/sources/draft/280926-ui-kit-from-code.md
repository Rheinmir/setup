---
type: issue
kind: feature-gap
title: "Chưa có skill rút UI kit HTML (kiểu Figma UI kit) từ token + component thật của một codebase"
status: open
assignee: "@Rheinmir"
dispatch: Claude
entry: /fdk
priority: P2
labels: ready-for-agent
tags: [issue, skill, ui-kit, design-system, tokens, dev-loop]
timestamp: 2026-09-28
id: 280926-ui-kit-from-code
source_session: "m3e-canvas — dựng docs/ui-kit.html từ lib/tokens.ts, rồi yêu cầu rút cách làm thành skill"
---

# Issue: Chưa có skill rút UI kit HTML từ token + component thật của một codebase

## Vấn đề (một câu)
Khi một dự án đã có hệ thiết kế nằm trong code (token màu, thang kích thước, bộ component), overstack chưa có đường nào dựng lại nó thành MỘT trang HTML tham chiếu kiểu "Figma UI kit": đổi được theme, copy được token và markup, đối chiếu được với tên component trong code.

## Bối cảnh & bằng chứng
- Phiên m3e-canvas (28/09/2026) làm tay `docs/ui-kit.html` (khoảng 72 KB) cho editor Material 3 Expressive. Cách làm lặp lại được:
  1. Chạy chính hàm token của app qua test runner để lấy giá trị THẬT: `paletteOf()` cho 7 palette × sáng/tối, không gõ tay hex.
  2. Dựng foundations: 25 vai trò màu, thang chữ, thang shape (`--k` = `scaleR`), bảng kích thước.
  3. Vẽ khoảng 30 component bằng class `.m3-*`, chỉ dựa vào token `--m3-*` và `--k`.
  4. Ghép màn mẫu điện thoại 412×892 và desktop 1280×800 (rail + list-detail).
  5. Kiểm bằng Playwright: 0 lỗi JS, mobile không tràn ngang, chụp sáng/tối.
- Skill gần nhất là `[[hallmark]]`, nhưng `references/design-showcase.html` của nó là bộ mẫu design MẶC ĐỊNH của overstack (build/redesign), không phải kit rút từ code của dự án đích. Còn `extract-site`/`web-clone` rút từ URL đang chạy, không từ nguồn token.
- Skill anh em vừa có: `[[live-mcp-bridge]]` (PR #180). Kit là tài liệu tham chiếu cho định dạng mà agent ghi qua MCP (mỗi thẻ ghi tên `kind`).

## Phạm vi
- Skill mới `skills/ui-kit-from-code/` (loop `dev-loop`, nhóm build) + mirror llmwiki + đăng ký đủ các bề mặt curated.
- `references/ui-kit-reference.html` = chính file m3e-canvas làm mẫu output chuẩn, kèm checklist cấu trúc BẮT BUỘC cho từng phần.
- Universal: áp cho mọi codebase có token (TS/JS, CSS vars, Tailwind config, Style Dictionary, Android/Compose theme…).

## Không thuộc phạm vi
- Sinh design system MỚI khi dự án chưa có (đó là `hallmark`).
- Export sang Figma thật (.fig / plugin), Storybook, hay package npm component.
- Đồng bộ ngược kit → code.

## Hướng gợi ý (không bắt buộc)
Khung 7 phần cố định: thanh điều khiển theme · intro + facts · foundations (màu, chữ, shape, layout/kích thước) · component theo nhóm của app · màn mẫu (mobile + desktop) · nút copy (token, HTML từng thẻ, hex từng ô) · kiểm chứng Playwright.

## Tiêu chí HOÀN THÀNH
- `swh-lint --skills ui-kit-from-code --ci`, `sync-skills.py --check`, `skill-registry.py --check`, `skill-provenance.py check --ci` đều rc 0.
- Skill nêu rõ cấu trúc bắt buộc của từng phần và trỏ tới file mẫu tham chiếu.
- File mẫu mở được độc lập (file://), 0 lỗi JS, không tràn ngang ở 390px.

## Assign & lý do
@Rheinmir, dispatch Claude qua `/fdk`: đã có bản mẫu chạy thật nên việc chủ yếu là chưng cất quy trình, agent làm được (`ready-for-agent`).

## Origin
Raise từ phiên Claude Code ở `~/orca/m3e-canvas` ngày 2026-09-28, sau khi dựng `docs/ui-kit.html` và thêm màn desktop theo yêu cầu người dùng. Bằng chứng: file mẫu đính kèm trong PR của skill, ảnh chụp Playwright trong phiên.
