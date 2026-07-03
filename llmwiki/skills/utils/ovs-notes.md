---
name: ovs-notes
description: "Viewer release-notes overstack TỨC THÌ (kiểu /release-notes của Claude CLI). Gõ /ovs-notes → liệt kê NGAY các bản (git tag + GH release) newest-first để chọn & đọc; /ovs-notes <version|latest> in đầy đủ notes một bản. READ-ONLY, KHÔNG side-effect — KHÁC /ship (quy trình CẮT release). Trigger: /ovs-notes, 'xem release notes', 'release notes bản nào', 'changelog', 'các bản đã ra', 'bản mới nhất có gì'."
---

# Skill: ovs-notes

> Xem release notes overstack tức thì — gõ phát hiện danh sách các bản để chọn & đọc. Read-only viewer, không cắt release (đó là `/ship`).

## When to use
- User muốn XEM lịch sử phát hành: "release notes", "changelog", "các bản đã ra", "bản mới nhất có gì", "/ovs-notes".
- KHÔNG dùng để cắt/đẩy release — đó là `/ship`.

## Zero-model: chạy thẳng, không tốn token
Toàn bộ LOGIC ở `fdk/tools/ovs-notes.py` là **code thuần, không qua model**. Muốn giống hệt `/release-notes` client-side của Claude CLI (tức thì, 0 token), user gõ thẳng trong phiên bằng bang-prefix:

```
!python3 fdk/tools/ovs-notes.py            # list
!python3 fdk/tools/ovs-notes.py latest     # đọc bản mới nhất
```

Skill này là lối vào NGÔN-NGỮ-TỰ-NHIÊN (khi user nói "xem release notes") — nó CÓ qua model một nhịp để gọi script; còn muốn 0-token thì dùng `!` ở trên.

## Steps
1. **List (mặc định):** chạy `python3 fdk/tools/ovs-notes.py` → in danh sách các bản newest-first (`vX.Y.Z  <ngày>  <tiêu đề>`). Nguồn: GH release (giàu) → fallback annotated git tag.
2. **Chọn để đọc:** user đã nêu bản (vd "v1.0.5", "mới nhất") → `python3 fdk/tools/ovs-notes.py <version|latest>` in đầy đủ. Chưa nêu → hiện danh sách rồi hỏi user chọn (có thể dùng picker).
3. Chỉ IN cho user đọc. Không sửa, không tag, không push.

## Rules
- **Read-only tuyệt đối** — KHÔNG bao giờ tạo/sửa tag, release, hay file. Cắt release là việc của `/ship`.
- **Nguồn sự thật = git tag + GH release**, không bịa. `gh` thiếu/không login → viewer tự lùi về annotated git tag (không chết).
- **Instant** — ưu tiên hiện danh sách ngay, đừng bắt user nhớ cú pháp; `latest` = bản mới nhất.
- Compose, đừng đẻ lại: mọi logic ở `fdk/tools/ovs-notes.py` (self-contained stdlib) — skill chỉ điều phối gọi.
