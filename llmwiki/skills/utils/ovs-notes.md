---
name: ovs-notes
description: "Viewer release-notes overstack TỨC THÌ (kiểu /release-notes của Claude CLI). Gõ /ovs-notes → liệt kê NGAY changelog OVERSTACK framework (newest-first) để chọn & đọc; /ovs-notes <version|latest> in đầy đủ; /ovs-notes --here = release của PROJECT hiện tại. READ-ONLY, KHÔNG side-effect — KHÁC /ship (quy trình CẮT release). Trigger: /ovs-notes, 'xem release notes', 'release notes bản nào', 'changelog', 'các bản đã ra', 'bản mới nhất có gì'."
---

# Skill: ovs-notes

> Xem release notes tức thì — gõ phát hiện danh sách các bản để chọn & đọc. Read-only viewer, không cắt release (đó là `/ship`).

## When to use
- User muốn XEM lịch sử phát hành: "release notes", "changelog", "các bản đã ra", "bản mới nhất có gì", "/ovs-notes".
- KHÔNG dùng để cắt/đẩy release — đó là `/ship`.

## Nguồn: framework mặc định, project qua --here (council-advisory 030726)
Tên `ovs-` = lời hứa "của overstack" → **mặc định xem changelog FRAMEWORK** (`Rheinmir/setup`, qua `gh`), dù bạn đứng ở project nào — KHÔNG suy nguồn từ CWD (chống mạo danh: release framework tưởng của project). Mỗi lần in đều **dán nhãn nguồn** ở header.
- `--here` → release của PROJECT hiện tại (git tag local, offline-ok).
- `--repo owner/name` → repo GitHub khác.
- `gh` vắng/offline/chưa login → in rõ *"không xác nhận được — rỗng KHÔNG nghĩa là không có bản"*, exit≠0 (không giả rỗng).

## Zero-model: chạy thẳng, không tốn token
Toàn bộ LOGIC ở `harness/scripts/ovs-notes.py` (sống ở harness/scripts nên **TRAVEL** xuống mọi project cài overstack — path không gãy downstream). Muốn giống hệt `/release-notes` client-side của Claude CLI (tức thì, 0 token), gõ thẳng bằng bang-prefix:

```
!python3 harness/scripts/ovs-notes.py            # changelog framework (list)
!python3 harness/scripts/ovs-notes.py latest     # bản framework mới nhất
!python3 harness/scripts/ovs-notes.py --here     # release project hiện tại
```

Skill này là lối vào NGÔN-NGỮ-TỰ-NHIÊN (khi user nói "xem release notes") — CÓ qua model một nhịp để gọi script; muốn 0-token thì dùng `!` ở trên.

## Steps
1. **List (mặc định):** chạy `python3 harness/scripts/ovs-notes.py` → changelog framework newest-first (`vX.Y.Z  <ngày>  <tiêu đề>`), có nhãn nguồn. User muốn release project → thêm `--here`.
2. **Chọn để đọc:** user nêu bản ("v1.0.5"/"mới nhất") → `python3 harness/scripts/ovs-notes.py <version|latest>` (+ `--here` nếu là project). Chưa nêu → hiện danh sách rồi hỏi user chọn.
3. Chỉ IN cho user đọc. Không sửa, không tag, không push.

## Rules
- **Read-only tuyệt đối** — KHÔNG bao giờ tạo/sửa tag, release, hay file. Cắt release là việc của `/ship`.
- **Nhãn nguồn bắt buộc** — mỗi output nói rõ đang xem framework hay project nào (chống mạo danh — Taleb).
- **Fail to lớn, không giả rỗng** — gh vắng/offline → nói "không xác nhận được" + exit≠0, đừng in danh sách rỗng như thể không có bản.
- Compose, đừng đẻ lại: mọi logic ở `harness/scripts/ovs-notes.py` (self-contained stdlib, travel downstream) — skill chỉ điều phối gọi.
