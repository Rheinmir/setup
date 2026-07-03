---
type: plan
status: done
issue: GH#4
date: 2026-07-04
---

# Plan — Issue GH#4: hoàn thiện trace-grading xuyên phiên (phần B sau review Fable)

> **ĐÃ HOÀN THÀNH** trong nhánh `Rheinmir/issue-4-logger-c` (phiên orca-fdk issue-4, 2026-07-04): B1 + B2 + B3 xong, self-test 5/5, verify trên 5 phiên 2026-07-02. Xem checklist cuối file.
> **Trạng thái nền**: phần A (parser transcript) đã xong trước; plan này thêm 3 fix do review chỉ ra.

## Bối cảnh 30 giây

- Issue GH#4 hỏi: logger (`code-logger` → `events.jsonl`) có đủ thông tin để **trace-grade xuyên phiên** không? → **Không**: chỉ ghi `file.write`, thiếu retrieval / grounding / outcome.
- Chẩn đoán: dữ liệu đầy đủ nhất nằm ở **transcript phiên** (`~/.claude/projects/<proj>/<session>.jsonl`), chỉ là `trace-grader.py` chưa đọc được.
- **Đã làm (phần A, đã verify)**: `harness/scripts/trace-grader.py` có `runs_from_transcript()` + CLI `--transcript` + self-test case (d). Chạy được trên 5 phiên 2026-07-02 (recover 42/295/162 steps).
- Council 2026-07-03: **đừng** đo query-rate (Goodhart). Đo reinvent-rate / cross-break / harm-when-missing. Deliberation phải để lại dấu vết.

## 4 lỗ hổng review chỉ ra (thứ tự ưu tiên = thứ tự làm)

### Bước 1 — Sửa cách suy `run.ok` cho transcript (bug thực, làm trước)

**Vấn đề**: `runs_from_transcript()` trả `ok = all(s.ok for s in steps)`. Trace dài (295 steps) gần như chắc chắn có ≥1 tool_result `is_error` (Grep không match, Bash exit≠0 vô hại…) → **mọi phiên thật luôn bị chấm FAIL** → metric `delivered` vô dụng.

**Việc làm** (chỉ trong `harness/scripts/trace-grader.py`):
- Task-level success KHÔNG phải AND của step-level. Với run từ transcript, KHÔNG suy `ok` từ steps — transcript không nói task có deliver hay không.
- Cách sửa gọn nhất: `Run.ok` giữ nguyên kiểu bool (đừng đổi schema), nhưng `runs_from_transcript` đặt `ok=True` mặc định (như `runs_from_audit` đã làm với step ok) **và** ghi rõ LIMITATION trong docstring: "transcript không carry task-level verdict; delivered luôn True — chỉ tin flags, đừng tin verdict pass/fail". Đây là đúng tinh thần `runs_from_audit` hiện tại (dòng ~149: "LIMITATION (honest)").
- KHÔNG thêm trạng thái `unknown` vào schema (đụng `grade_run`, `render_report`, self-test — quá phạm vi).

**Verify**: `python3 harness/scripts/trace-grader.py --self-test` ALL PASS; chạy lại 3 phiên lớn → không còn FAIL oan, flags vẫn hiện (`excessive_steps` v.v.).

### Bước 2 — Lọc sidechain/subagent khỏi run chính

**Vấn đề**: transcript chứa cả tool_use của agent con (`isSidechain: true` trên dòng, hoặc `parentUuid` trỏ vào nhánh sidechain). Trộn vào làm sai `step_budget`, `order_constraints`.

**Việc làm**:
- Trong vòng lặp parse của `runs_from_transcript`: `if o.get("isSidechain"): continue` (fail-open — thiếu field coi như main chain).
- KIỂM TRA THẬT trước khi tin: mở 1 transcript có Agent call (phiên `c0fd85d2`, 295 steps) xem field tên gì (`isSidechain` / `is_sidechain` / khác) — **đừng code theo giả định**, grep thử:
  ```bash
  grep -o '"isSidechain":[a-z]*' ~/.claude/projects/-Users-giatran-orca-setup-setup/c0fd85d2-*.jsonl | sort | uniq -c
  ```
- Thêm 1 assert vào self-test case (d): dòng có `isSidechain: true` bị bỏ qua.

**Verify**: số steps phiên `c0fd85d2` giảm (subagent bị loại) hoặc xác nhận phiên đó vốn không có sidechain; self-test ALL PASS.

### Bước 3 — Check grounding `edited_without_read` (tim của câu hỏi #2 trong issue)

**Vấn đề**: parser giữ args nhưng chưa có check nào nối Read(X) → Edit(X). "Agent có nhìn trước khi làm không?" hiện vẫn chưa chấm được.

**Việc làm**:
- Thêm pure function `check_edited_without_read(run, cfg)` cạnh các check hiện có (khoảng dòng 193+), cùng shape flag `{check, severity, step, tool, detail}`:
  - Duyệt steps theo thứ tự, gom tập `seen_paths` = mọi `file_path`/`path` xuất hiện trong args của tool đọc (`Read`, `Grep`, `Glob`) **và** file agent vừa Write (tự viết ra thì coi như đã biết nội dung).
  - Gặp `Edit`/`MultiEdit` với `file_path` chưa có trong `seen_paths` → flag `severity: "medium"`, check `edited_without_read`.
  - `Write` KHÔNG flag (tạo file mới không cần đọc trước).
  - So path bằng bản chuẩn hoá (`os.path.normpath`), đừng so string thô.
- Đăng ký vào tuple `PATH_CHECKS`.
- Config adapter: thêm `grounding: {enabled: true}` vào `DEFAULT_CONFIG` + đọc trong check (tôn trọng ranh giới adapter của file — mọi tham số rule nằm ở `harness/trace-grader.config.yaml`, đánh dấu `# ASSUMPTION`).
- Thêm self-test case (e): trace có Edit không Read trước → flag; trace Read rồi Edit → không flag.

**Verify**: self-test ALL PASS; chạy trên 5 phiên 2026-07-02, đọc flags bằng mắt xem có false-positive kiểu "Edit file vừa Write" không.

### Bước 4 — Đóng vòng: ledger + wiki + issue

- Cập nhật node `p-17` trong `llmwiki/html/fdk-problem-tree.html` (data trong `<script id="tree-data">`, chỉ sửa JSON): mô tả thêm 3 fix, cân nhắc scope. **Lưu ý màu/scope**: chỉ `solved` + scope full khi cả 3 trụ xong — phần đo reinvent-rate (mục C, chưa làm) vẫn giữ node ở `partial`.
- Nếu commit code: sau commit mới được viết wiki entry (rule "wiki sau commit"); entry vào `sources/` hoặc cập nhật draft này, nhớ `## Origin` + update `wiki/index.md`.
- Comment lên GH#4 tóm tắt: chẩn đoán + phần đã làm + phần C còn mở (reinvent-rate cần định nghĩa "reinvent" — chưa chốt, ĐỪNG tự chế metric).

## KHÔNG làm trong nhánh này (chống phình phạm vi)

- **B cũ (mở `hooklib.audit()` ghi retrieval args)**: giá trị biên nhỏ một khi grader đọc transcript trực tiếp. Chỉ làm nếu có nhu cầu thật (vd. transcript bị xoá theo retention). Đừng làm "cho đủ 3 trụ".
- **C (reinvent-rate / cross-break / harm-when-missing)**: cần định nghĩa metric qua council/propose riêng. Bước 3 (grounding check) là proxy đầu tiên, đủ cho issue này.
- Đừng phình `events.jsonl` thêm loại event mới — council đã cảnh báo Goodhart.

## Checklist tổng (tick khi xong)

- [x] B1: `run.ok` transcript không còn AND-steps (`ok=True` forced); docstring LIMITATION; self-test pass
- [x] B2: sidechain lọc (`isSidechain` — verified field name trên transcript thật); assert trong self-test (d)
- [x] B3: `check_edited_without_read` + config `grounding.enabled` (adapter) + self-test case (e)
- [x] Chạy cả 5 phiên 2026-07-02: hết FAIL oan, grounding flag ≤1/phiên (không false-positive thô)
- [x] B4: p-17 cập nhật (partial, trụ harness); comment GH#4 + đóng issue; plan này là wiki record
- [x] Commit KHÔNG có AI-attribution (R15 chặn); mở PR vào `orca` + merge

## Origin

- Issue: https://github.com/Rheinmir/setup/issues/4 (rà 5 phiên 2026-07-02)
- Council: `llmwiki/wiki/draft/orca/030726-eval-report.md`, `council-report-022-seed42.html`
- Phần A + review 4 lỗ hổng: phiên orca-fdk issue-4, 2026-07-04 (nhánh `Rheinmir/issue-4-logger-c`, file `harness/scripts/trace-grader.py`)
- Ledger: node `p-17` trong `llmwiki/html/fdk-problem-tree.html`
