---
name: orca-workflow
description: Daily propose → gate → dispatch workflow with Orca
---

# Skill: orca-workflow

## Triggers

- User nói "propose <tính năng>", "feature request", "implement <tên>"
- User nói "chạy lint", "verify wiki"
- User nói "sync template", "upstream"

## ⚠️ QUY TẮC BẤT BIẾN — KHÔNG ĐƯỢC BỎ QUA

### Trước khi đụng container (docker compose / docker run)

```bash
# BẮT BUỘC chạy trước bất kỳ --force-recreate, down, recreate nào:
docker inspect <container_name> --format '{{json .Mounts}}' | python3 -m json.tool
```

So sánh `Source` path với volume trong compose file sắp dùng. Nếu khác → DỪNG, hỏi user.

**Production DB của Cozyroom:** `/mnt/c/Users/olive/orca/workspaces/home-spotify/m/data/metadata.db`
Không bao giờ đổi volume mount mà không backup + xác nhận user.

> Bài học 2026-05-29: recreate container với compose sai path → mất toàn bộ DB người dùng.

---

## Workflow: propose

> ⛔ **HARD RULE — ĐỌC TRƯỚC KHI LÀM BẤT KỲ THỨ GÌ:**
> Không được tạo file, chạy lệnh, hay thay đổi code **trước khi có file propose được USER XÁC NHẬN**.
> Propose phải mô tả **KẾ HOẠCH** (sẽ làm gì), KHÔNG phải kết quả (đã làm gì).
> Sau khi tạo propose → **DỪNG NGAY, hiển thị nội dung propose, hỏi user "Duyệt không?"**

### Bước 1 — query (read-only)
Đọc wiki, đọc code liên quan. **KHÔNG tạo file, KHÔNG sửa gì.**

### Bước 2 — propose (**TẠO FILE + DỪNG**)
Tạo `llmwiki/wiki/draft/orca/DDMMYY-tên.md` với nội dung:
```
## Plan
- [ ] Task 1: mô tả cụ thể
- [ ] Task 2: ...

## Agent Task Assignment (KẾ HOẠCH dispatch — bắt buộc nếu có dùng agent khác)
| Task | Agent | Model | Status |
|------|-------|-------|--------|
| <task 1> | Claude main / agy / opencode / kiro | <model> | pending |

## Files sẽ tạo/sửa
| File | Action | Lý do |
|------|--------|-------|

## Risks
- ...
```
Tạo kèm **sequence diagram hoạt họa** `llmwiki/html/DDMMYY-tên-seq.html` — luồng code đi qua các component của plan (mỗi flow một diagram: happy path, fail/block path). Quy ước: lifeline indigo = component có sẵn, emerald = component proposal thêm/sửa; message hiện từng bước, auto-loop, click để pause. Link 2 chiều md ↔ html. **Propose = CẶP md + html — thiếu một là chưa hoàn chỉnh.**

Sau khi tạo cặp file → **⛔ DỪNG LẠI.**

**In DISPATCH BOARD ra terminal bằng bash (BẮT BUỘC — viết trong chat hoặc chỉ trong file propose là KHÔNG ĐỦ):**
```bash
echo ""
echo "==================== ORCA-WORKFLOW DISPATCH BOARD ===================="
printf " %-30s %-22s %-20s %s\n" "TASK" "AGENT" "MODEL" "STATUS"
# một dòng printf cho mỗi task trong Agent Task Assignment, ví dụ:
printf " %-30s %-22s %-20s %s\n" "Build landing page" "opencode" "DeepSeek Flash v4" "pending"
echo "======================================================================="
```
User gate dựa trên board này — không có board hiện trong terminal thì không được hỏi duyệt.

In nội dung propose + preview URL của html ra màn hình. Hỏi user: **"Duyệt proposal này không?"**
**KHÔNG làm gì thêm** cho đến khi user nói OK / duyệt / yes / proceed.

### Bước 3 — gate (**CHỜ USER**)
Chờ user approve. Nếu user yêu cầu thay đổi → sửa propose, hỏi lại.
**Chỉ tiếp tục khi user nói OK rõ ràng.**

### Bước 4 — implement (**CHỈ SAU KHI ĐƯỢC DUYỆT**)
Thực hiện theo đúng plan trong propose. Không làm ngoài scope đã duyệt.
Phân rã tasks → `orca orchestration task-create` mỗi task (nếu cần dispatch).

### Bước 5 — dispatch (nếu cần agent khác)
Chỉ dispatch đúng theo **Agent Task Assignment** đã duyệt ở gate. Muốn đổi agent/model → cập nhật board, in lại, hỏi lại user.
`orca orchestration dispatch --task <id> --to <agent> --inject`; nếu fail → `orca terminal send`
Chờ: `orca terminal wait --for tui-idle` → `orca terminal read`
Sau mỗi task xong → cập nhật cột Status trong file propose NGAY (pending → in-progress → done), không dồn về cuối.

### Bước 6 — verify
Invoke `verify-before-commit` trước mỗi commit.

## Dispatch nhanh

```bash
# Check terminals
orca terminal list

# Tạo Antigravity terminal (nếu chưa có)
orca terminal create --worktree active --title "Antigravity" --command "agy"

# Tạo OpenCode terminal
orca terminal create --worktree active --title "OpenCode" --command "opencode"

# Gửi task
orca terminal send --title "Antigravity" --text "<task description>"

# Đọc kết quả
orca terminal wait --for tui-idle && orca terminal read --title "Antigravity"
```

## Agent binaries

| Agent | Binary | CHECK |
|-------|--------|-------|
| Antigravity | `agy` | `agy --version` |
| OpenCode | `opencode` | `opencode --version` |
| Kiro | `kiro-cli` | `kiro-cli --version` |
| Orca | GUI only — dùng qua `orca terminal *` commands | `orca terminal list` |

## Caveman Mode

Dùng `caveman` (plugin `/caveman`) cho hầu hết tình huống để tiết kiệm ~75% token. Không dùng khi viết proposal, tài liệu, hoặc xuất HTML.

> Để biết dispatch, skill install, AgentMemory — xem `llmwiki/skills/setup/orca-dispatch-reference.md`


---

## Output Report (sau khi implement xong)

> Đây là **báo cáo kết quả** sau khi implement, KHÔNG phải propose plan.
> Propose plan phải được tạo ở Bước 2 TRƯỚC khi làm bất kỳ thứ gì.

After all implementation tasks complete, write an output report to the wiki.

### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/draft/orca/DDMMYY-<ten>.md`:

```
# DDMMYY-<ten>
**Type:** draft
**Status:** proposed
**Tags:** <skill-name>, output-report
**Proposed:** YYYY-MM-DD

## Agent Task Assignment
| Task | Agent | Status |
|------|-------|--------|
| <mô tả task 1> | <tên agent> | pending / in-progress / done |
| <mô tả task 2> | <tên agent> | pending / in-progress / done |

## What
<One sentence — what this skill invocation produced or decided>

## Output
<Key artefacts, files created/modified, or decisions made>

## Files
| File | Action |
|------|--------|
| `path/to/file` | created / modified |

## Notes
- Invoked via: `/<skill-name>` skill

## Origin
- **Draft:** `wiki/draft/orca/DDMMYY-<ten>.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
```

**3. Update wiki index & log:**
- `llmwiki/wiki/index.md` — append one row: `| [DDMMYY-<ten>](draft/orca/DDMMYY-<ten>.md) | draft | YYYY-MM-DD |`
- `llmwiki/wiki/log.md` — append: `## YYYY-MM-DD — <skill-name> — <ten>`

**4. Update agent statuses & sync push — BẮT BUỘC, không bỏ qua:**
- Mở lại file `llmwiki/wiki/draft/orca/DDMMYY-<ten>.md`
- Cập nhật cột **Status** trong bảng `## Agent Task Assignment` theo trạng thái thực tế của từng agent (pending → in-progress → done)
- Clone `rheinmir/setup` nhánh `orca`, copy các skill file đã sửa, rồi push ngược lên:
  ```bash
  git clone git@github.com:rheinmir/setup.git /tmp/rheinmir-setup-sync -b orca --depth 1
  cp /path/to/skill.md /tmp/rheinmir-setup-sync/skills/<skill-name>/SKILL.md
  cd /tmp/rheinmir-setup-sync
  git add .
  git commit -m "skill: sync update — DDMMYY-<ten>"
  git push origin orca
  rm -rf /tmp/rheinmir-setup-sync
  ```

> Skip chỉ khi skill không tạo ra artifact hoặc quyết định nào.