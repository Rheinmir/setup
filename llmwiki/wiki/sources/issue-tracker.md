---
type: reference
title: "Issue tracker — hợp đồng theo repo (adapter boundary)"
status: living
tags: [issue, tracker, adapter, ledger, wayfinder]
timestamp: 2026-07-15
---

# Issue tracker — hợp đồng của repo này

Đây là **ranh giới adapter**: skill (`/raise-issue`, `/orca-issue`, `/wayfinder`) chỉ nói *"publish to the issue tracker"*, *"fetch the ticket"*, *"claim it"* — còn **cách làm ở repo này** thì nằm ở đây. Muốn đổi tracker (thêm Jira, đổi sang GitLab) là sửa **một file này**, không mổ ruột skill nào. Đây là thứ mattpocock làm đúng mà `/raise-issue` cũ làm sai (hardcode `gh`/`glab` trong thân skill).

## Tracker của repo này

**Nguồn chân lý: local-markdown** — ledger `llmwiki/wiki/sources/ISSUES.md`. Luôn chạy được, không cần mạng, đi theo repo khi clone. Đây là gốc, không phải bản sao.

**Mirror (tuỳ chọn): GitHub** — repo có remote `github.com/Rheinmir/setup`. Mirror lên để hiện ở tab Issues, assign người thật, có notification. Ledger vẫn là gốc; GitHub là bản sao để phối hợp. Không có mạng / không có `gh` → bỏ qua mirror, ledger-only vẫn đủ.

## Năm nhãn chuẩn (triage roles)

Mọi issue mang đúng một nhãn vòng đời. Nhãn nói *issue đang ở đâu*, và quan trọng nhất: **việc nào một agent được tự lấy chạy**.

| Nhãn | Nghĩa | Agent tự lấy được? |
|------|-------|--------------------|
| `needs-triage` | Cần người đánh giá (mặc định của issue mới) | Không |
| `needs-info` | Chờ người báo thêm thông tin | Không |
| **`ready-for-agent`** | Đã đặc tả đủ, một agent AFK làm được | **CÓ** — đây là nhãn frontier lọc |
| **`ready-for-human`** | Cần người thi hành: quyết định thiết kế, đánh đổi, truy cập ngoài, kiểm thủ công | Không — **cấm dispatch cho CLI headless** |
| `wontfix` | Sẽ không làm | — |

`ready-for-agent` / `ready-for-human` là ranh giới **HITL/AFK**: nó là thứ duy nhất trong hệ nói được "việc này giao máy được hay phải người". Việc `ready-for-human` mà bị giao cho một CLI headless không hỏi lại được thì nó chỉ còn cách **đoán thay người dùng rồi im lặng** — đúng gốc của con số giao-hàng ~1/5.

## Thao tác — cách diễn đạt ở repo này

Skill gọi bằng *ý định*; cột phải của bảng này là *cách làm*. Chạy cả hai vế (ledger + mirror) khi có mạng; chỉ vế ledger khi offline.

| Ý định skill nói | Local-markdown (gốc) | GitHub (mirror, nếu có) |
|------------------|----------------------|-------------------------|
| **publish an issue** | Thêm một dòng vào `ISSUES.md` + file draft chi tiết | `gh issue create --title … --body …` |
| **fetch the ticket** | Đọc dòng + file draft theo `id` | `gh issue view <n> --comments` |
| **apply a label** | Sửa ô `labels` của dòng | `gh issue edit <n> --add-label …` |
| **close** | Đổi `status` → `done` | `gh issue close <n> --comment …` |
| **list open** | Lọc dòng `status: open` | `gh issue list --state open` |
| **add a blocking edge** | Thêm id vào ô `blocked_by` của issue bị chặn | `gh api …/dependencies/blocked_by` (dependency native, UI hiện) |
| **claim it** | Ghi `<phiên>@<ts>` vào ô `claim` — **thao tác GHI ĐẦU TIÊN** của phiên | `gh issue edit <n> --add-assignee @me` |

## Frontier — việc nào lấy được BÂY GIỜ

`python3 harness/scripts/frontier.py` (tất định, 0 token) in ra **frontier** = issue *open* ∧ *mọi blocker đã đóng* ∧ *chưa ai claim*. Thêm `--agent` để chỉ lấy `ready-for-agent` (bỏ `ready-for-human`). Đây là câu trả lời cho *"giờ lấy việc gì là hợp lệ"* — trước đây hệ không trả lời được.

## Wayfinding operations (dùng bởi `/wayfinder`)

Bản đồ là một issue nhãn `wayfinder:map`; ticket là issue **con** của nó.
- **Map**: một dòng `ISSUES.md` nhãn `wayfinder:map`, thân ở file draft (Destination / Decisions-so-far / Not-yet-specified / Out-of-scope). Mirror: `gh issue create --label wayfinder:map`.
- **Ticket con**: dòng issue nhãn `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`), `blocked_by` trỏ ticket chặn nó. Mirror: GitHub sub-issue.
- **Frontier query**: `frontier.py` lọc theo nhãn `wayfinder:map` cha.
- **Claim / Resolve**: claim = ghi ô `claim`; resolve = `status: done` + append một dòng vào Decisions-so-far của map.

## Origin
- Adapter boundary chưng cất từ `mattpocock/skills` — `setup-matt-pocock-skills/issue-tracker-github.md` + `triage-labels.md` (clone `scratchpad/mattpocock-skills/`, 2026-07-15).
- Absorb qua `/propose` → `150726-mattpocock-absorb` (T6/T7), task `T-260715-01`.
- **Commit:** _(verify-before-commit điền)_
