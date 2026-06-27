# CONTRIBUTING — Thêm/sửa một rule của harness

> Lối vào tổng cho phát triển framework: `llmwiki/wiki/concepts/fdk.md` (FDK). Runbook này là nhánh "thêm/sửa rule" của bộ xương đó.

Runbook để **một người mới** thêm luật vào harness mà không cần đọc đầu tác giả. Gắn với
[[rule-registry]] (danh sách luật) + ADR-001 (policy là nguồn chân lý) + ADR-002 (tiêu chí
quyết định). Mọi đường dẫn dưới đây tương đối từ root repo.

---

## 0. Cổng quyết định — CÓ nên thêm rule không? (ADR trước, code sau)

Trả lời TRƯỚC khi viết dòng nào (tiêu chí từ ADR-001/002):

1. **Deterministic-first**: rule giải quyết được bằng luật cứng/quy ước? → harness. Nếu cần
   suy luận ngữ cảnh từng ca → KHÔNG phải rule, đừng nhét vào harness.
2. **≥ 2 use case**: chỉ phục vụ đúng 1 file/1 dự án → đừng thêm abstraction/rule. Chờ tới khi
   có ít nhất 2 nơi cần.
3. **Enforcement phủ được vendor nào?** Chỉ tin **git-level** (mọi vendor) hoặc **orchestrator**
   (làm hộ trước fan-out). Đừng dựa lifecycle session của một vendor (ADR-002).
4. **Fail-open**: lỗi hạ tầng (offline, thiếu file, parse hỏng) KHÔNG được khoá cứng người dùng.

Nếu rule là một **quyết định kiến trúc** (đánh đổi, chọn hướng) → viết kèm 1 **ADR** ở
`llmwiki/wiki/sources/adr/ADR-00N-*.md` (template: `sources/adr/README.md`).

---

## 1. Phân loại rule → chọn cơ chế

| Loại | Khi nào | Cơ chế | Đụng code lõi? |
|------|---------|--------|----------------|
| **Content-check** | Chặn/kiểm nội dung 1 file lúc ghi/commit | `kind` trong `policy.yaml` | KHÔNG, nếu `kind` đã có |
| **Hook-event** | Phản ứng theo sự kiện phiên (Stop/PostToolUse/SessionStart/UserPromptSubmit) | `kind: hook_event` (documentary) + wiring | Có — sửa `gen-converters.py` + hook script |
| **Process-gate** | Kỷ luật quy trình (vd pull-before-change) | `kind: process_gate` + script/git-hook | Có — script riêng |

`kind` content có sẵn (KHÔNG cần sửa lõi): `deny_write`, `require_section`, `forbid_root`,
`conditional_require`, `require_frontmatter`. Cần hành vi mới → mới thêm `kind` vào lõi
`harness/poc-vendor-neutral/bin/llmwiki-validate.py` (hàm `apply_rule` + 1 hàm `check_*`).

**Số hiệu**: dùng số chưa dùng kế tiếp (hiện **R13**). Tránh **R6** (đang reserved/chưa rõ) cho
tới khi điều tra. Xem [[rule-registry]].

---

## 2. Quy trình — Content-check (đường phổ biến nhất, "thick policy / thin adapter")

> Ví dụ thật: **R11 seq-html-glass-style** — thêm 0 dòng code adapter, chỉ 1 entry policy.

1. **Step 0**: `bash harness/poc-vendor-neutral/bin/pull-gate-sweep.sh` (R12 — pull trước khi sửa).
2. **Sửa `harness/poc-vendor-neutral/policy.yaml`**: thêm 1 block rule với `id`, `name`, `kind`,
   `statement`, `enforce_at` (`session` / `repo` / cả hai), và field theo `kind`
   (vd `conditional_require`: `target_globs` + `when_contains` + `need_contains`).
3. **Nếu cần `kind` mới**: thêm `check_<kind>()` + nhánh trong `apply_rule()` của
   `bin/llmwiki-validate.py`. (Hiếm — cân nhắc dùng `conditional_require` trước.)
4. **Regen adapter**: `python3 harness/poc-vendor-neutral/gen-converters.py`.
5. **Drift-test**: `bash harness/tests/policy-converters-drift-test.sh` → phải PASS (rule mới
   xuất hiện ở advisory/deny đúng kỳ vọng).
6. **Test rule cắn**: `python3 harness/poc-vendor-neutral/bin/llmwiki-validate.py path <file vi phạm>`
   → exit 2; `<file hợp lệ>` → exit 0.
7. **Cập nhật [[rule-registry]]** (1 hàng) + log/decisions nếu là quyết định.

---

## 3. Quy trình — Hook-event (R3/R4/R8/R10 kiểu này)

1–2 như trên, nhưng block policy dùng `kind: hook_event` + các **field máy**:
   `event:` (Stop/PostToolUse/SessionStart/UserPromptSubmit) · `event_action:` (arg cho
   `harness-events.py`) · `blocking:` (true→chặn exit 2 / false→báo cáo) · `matcher:?` · `timeout:?`.
3. **gen-converters TỰ SINH hook claude từ field trên** (policy-drives-wiring) — KHÔNG còn sửa dict
   hardcode. Chỉ khi `event_action` là **hành động MỚI** mới thêm nhánh trong `harness-events.py`
   (PoC) + hook production `llmwiki/.claude/hooks/<event>.py`.
4. **Regen + Drift-test BẮT BUỘC**: drift-test assert `event` khớp kỳ vọng + có `event_action` +
   lệnh hook chứa action + không orphan → chốt giữ policy↔wiring không lệch.

---

## 4. Quy trình — Process-gate (R12 kiểu này)

1. Viết script gác ở `bin/` (fail-open, exit 2 khi chặn). Block policy `kind: process_gate` +
   `*_cmd:` documentary.
2. Chọn **điểm enforce vendor-neutral** (ADR-002): git-hook (`.git/hooks/pre-push` /
   `.pre-commit` stage) cho "trước push"; orchestrator Step 0 (skill `orca-workflow`) cho
   "trước khi làm/fan-out". **KHÔNG** gắn per-edit PreToolUse (bài học R12: cost cao, lệch vendor).
3. Nhân ra workspace nhiều subrepo: `install-harness.sh --all-subrepos`.

---

## 5. Bắt buộc trước khi commit (mọi loại rule)

- [ ] `gen-converters.py` chạy sạch + `policy-converters-drift-test.sh` PASS.
- [ ] Rule cắn đúng (test dương + **test âm**: cố tình vi phạm → đỏ).
- [ ] [[rule-registry]] thêm/sửa hàng tương ứng; flag honest nếu còn caveat (đừng tô hồng).
- [ ] ADR nếu là quyết định kiến trúc; `decisions.md` + `log.md` 1 dòng.
- [ ] Commit qua gate: pre-push (R12 gate2) tự chạy. Đừng `--no-verify` trừ khi chắc.

---

## Origin
- **Source:** runbook chưng cất từ thực thi R11/R12/R12v3 + reconcile R3/R4/R8/R10 (T1–T5 của
  proposal `270626-framework-gap-backfill`), phiên 2026-06-27.
- **Liên quan:** `llmwiki/wiki/concepts/rule-registry.md`, `sources/adr/ADR-001`, `ADR-002`,
  `policy.yaml`, `gen-converters.py`, `tests/policy-converters-drift-test.sh`.
