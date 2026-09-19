---
name: ovs-notes
disable-model-invocation: true
description: "Viewer release-notes overstack TỨC THÌ (kiểu /release-notes của Claude CLI). Gõ /ovs-notes → liệt kê NGAY changelog OVERSTACK framework (newest-first) để chọn & đọc; /ovs-notes <version|latest> in đầy đủ; /ovs-notes --here = release của PROJECT hiện tại. READ-ONLY, KHÔNG side-effect — KHÁC /ship (quy trình CẮT release). Trigger: /ovs-notes, 'xem release notes', 'release notes bản nào', 'changelog', 'các bản đã ra', 'bản mới nhất có gì'."
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: ovs-notes

> Xem release notes tức thì — gõ phát hiện danh sách các bản để chọn & đọc. Read-only viewer, không cắt release (đó là `/ship`).

## WHAT

### Purpose và context
- **Purpose:** cho user XEM release notes (framework overstack mặc định, hoặc project hiện tại) tức thì, chỉ đọc.
- **Trigger (when to use):**
  - User muốn XEM lịch sử phát hành: "release notes", "changelog", "các bản đã ra", "bản mới nhất có gì", "/ovs-notes".
- **Non-goals:** KHÔNG dùng để cắt/đẩy release — đó là `/ship`. Không suy nguồn từ CWD.

### Mental model
`nguồn (framework mặc định · --here project · --repo khác) → danh sách vX.Y.Z newest-first có nhãn nguồn → user chọn bản → in đầy đủ`.

Tên `ovs-` = lời hứa "của overstack" → **mặc định xem changelog FRAMEWORK** (`Rheinmir/setup`, qua `gh`), dù bạn đứng ở project nào — KHÔNG suy nguồn từ CWD (chống mạo danh: release framework tưởng của project). Mỗi lần in đều **dán nhãn nguồn** ở header (council-advisory 030726).

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | version \| `latest` | không | không có → in danh sách rồi hỏi chọn |
| In | `--here` / `--repo owner/name` | không | release project hiện tại (git tag local, offline-ok) / repo GitHub khác |
| Out | danh sách `vX.Y.Z  <ngày>  <tiêu đề>` hoặc nội dung một bản | có | luôn có nhãn nguồn ở header |
| Out | exit≠0 + "không xác nhận được" | khi gh vắng/offline | không giả rỗng |

### Rules và capabilities
- RULE-01 (MUST): **Read-only tuyệt đối** — KHÔNG bao giờ tạo/sửa tag, release, hay file. Cắt release là việc của `/ship`.
- RULE-02 (MUST): **Nhãn nguồn bắt buộc** — mỗi output nói rõ đang xem framework hay project nào (chống mạo danh — Taleb).
- RULE-03 (MUST): **Fail to lớn, không giả rỗng** — gh vắng/offline → nói "không xác nhận được" + exit≠0, đừng in danh sách rỗng như thể không có bản.
- RULE-04 (MUST): Compose, đừng đẻ lại: mọi logic ở `harness/scripts/ovs-notes.py` (self-contained stdlib, travel downstream) — skill chỉ điều phối gọi.
- Capabilities: đọc release của repo remote (qua công cụ GitHub đã auth) hoặc tag git local; không ghi gì.

### Failure boundaries
- `gh` vắng/offline/chưa login → **blocked**: in rõ *"không xác nhận được — rỗng KHÔNG nghĩa là không có bản"*, exit≠0.
- User chưa nêu bản → **clarify**: hiện danh sách rồi hỏi chọn.
- User thật ra muốn cắt release → chuyển `/ship`, không làm ở đây.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | nguồn | List: chạy `python3 harness/scripts/ovs-notes.py` (+ `--here` nếu project) | changelog newest-first có nhãn nguồn | gh vắng → blocked, exit≠0 |
| W02 | judgment | lời user | Chọn bản: user nêu → chạy với `<version|latest>`; chưa nêu → hỏi | nội dung bản | chưa chọn → clarify |
| W03 | deterministic | output | Chỉ IN cho user đọc | user đọc được | — |

Chi tiết từng bước (nguồn chân lý cho W01–W03):

1. **List (mặc định):** chạy `python3 harness/scripts/ovs-notes.py` → changelog framework newest-first (`vX.Y.Z  <ngày>  <tiêu đề>`), có nhãn nguồn. User muốn release project → thêm `--here`.
2. **Chọn để đọc:** user nêu bản ("v1.0.5"/"mới nhất") → `python3 harness/scripts/ovs-notes.py <version|latest>` (+ `--here` nếu là project). Chưa nêu → hiện danh sách rồi hỏi user chọn.
3. Chỉ IN cho user đọc. Không sửa, không tag, không push.

#### Nguồn: framework mặc định, project qua --here (council-advisory 030726)
- `--here` → release của PROJECT hiện tại (git tag local, offline-ok).
- `--repo owner/name` → repo GitHub khác.
- `gh` vắng/offline/chưa login → in rõ *"không xác nhận được — rỗng KHÔNG nghĩa là không có bản"*, exit≠0 (không giả rỗng).

#### Zero-model: chạy thẳng, không tốn token
Toàn bộ LOGIC ở `harness/scripts/ovs-notes.py` (sống ở harness/scripts nên **TRAVEL** xuống mọi project cài overstack — path không gãy downstream). Muốn giống hệt `/release-notes` client-side của Claude CLI (tức thì, 0 token), gõ thẳng bằng bang-prefix:

```
!python3 harness/scripts/ovs-notes.py            # changelog framework (list)
!python3 harness/scripts/ovs-notes.py latest     # bản framework mới nhất
!python3 harness/scripts/ovs-notes.py --here     # release project hiện tại
```

Skill này là lối vào NGÔN-NGỮ-TỰ-NHIÊN (khi user nói "xem release notes") — CÓ qua model một nhịp để gọi script; muốn 0-token thì dùng `!` ở trên.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | user_optional | user muốn release của PROJECT hiện tại | thêm `--here` (git tag local, offline-ok) | — | W02 |
| B02 | user_optional | user chỉ định repo GitHub khác | thêm `--repo owner/name` | gh vắng → blocked | W02 |
| B03 | user_optional | user muốn 0 token | gõ thẳng `!python3 harness/scripts/ovs-notes.py …` | — | kết thúc (không qua model) |

### Validation và stopping
Nội dung do `ovs-notes.py` in (tất định); model chỉ chuyển cho user. Dừng sau khi in; không có bước ghi nào.

### Examples
- **Positive:** "bản mới nhất có gì" → `python3 harness/scripts/ovs-notes.py latest` → in đầy đủ notes bản framework mới nhất, header ghi nguồn `Rheinmir/setup`.
- **Boundary/failure:** máy chưa `gh auth login` → script in "không xác nhận được — rỗng KHÔNG nghĩa là không có bản", exit≠0; không in danh sách rỗng.
