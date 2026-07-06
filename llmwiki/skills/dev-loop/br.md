---
name: br
description: >-
  Hub MỘT TÊN cho dây chuyền sản xuất kiểu Ralph (GH#15): biến tài liệu thô của
  user thành sản phẩm qua 5 mode — `/br interview` (đọc folder raw/ → đối chiếu bộ
  specs chuẩn S1–S10 → sinh bộ câu hỏi hỏi-bù dạng HTML xem trước + MD điền, cho
  phép lens chuyên gia điền thay mục chưa chắc), `/br compile` (answers → BR.md có
  clause_id + bảng "Giả định đang gánh"), `/br slice` (BR → frames nhỏ gắn chặt code,
  gác bằng frame-lint), `/br run <frame>` (mỗi frame chạy loop-runner có 6 phanh +
  dry-run + người gác), `/br status` (trang line-status.html tất định: frame nào
  chạy/kẹt/xong + truy ngược lỗi→frame→clause). Gọi khi user nói "br", "interview",
  "phỏng vấn yêu cầu", "soạn BR", "slice frame", "chạy frame", "trạng thái dây chuyền",
  "ralph pipeline", hoặc invoke /br. User chỉ mô tả PHẠM VI, không cần nhớ lệnh con.
---

# Skill: br — dây chuyền sản xuất Ralph (BR-kỹ → frames → loop có harness)

> Hub 1-tên: user mô tả *phạm vi* (interview / compile / slice / run / status), KHÔNG
> phải nhớ nhiều lệnh. Nền tảng: council 028 (thin-slice, người-trong-vòng-lặp) +
> council 031/032 (loop v1 với 6 điều kiện bắt buộc — winner Taleb mean-rank 1.0).

## When to use
- User có tài liệu yêu cầu (thô/không cấu trúc) và muốn biến thành sản phẩm có kỷ luật.
- User nói: interview / phỏng vấn yêu cầu / soạn BR / slice frame / chạy frame / trạng thái dây chuyền / ralph.

## Đồ nghề tất định (đã build + selftest — KHÔNG viết lại)
| Tool | Việc | selftest |
|------|------|----------|
| `skills/br/assets/spec-template.md` | bộ specs chuẩn S1–S10 (khung tham chiếu mọi project) | — |
| `fdk/tools/frame-lint.py` | gác frame 6 luật (schema · scope · test-first · freshness · DAG · exclusive-scope) | `frame-lint.py selftest` |
| `harness/scripts/loop-runner.py` | loop 6 phanh (max_iter·budget·no_progress·escalate·**diff-jail**·**test-hash**) | `loop-runner.py selftest` |
| `fdk/tools/build-line-status.py` | monitor tất định (frame·run-log·BR → json+html, `--check`) | `build-line-status.py selftest` |

Runtime artifacts sống ở `br/` tại gốc project (không phải trong skill): `br/spec-filled.md`,
`br/interview/NNN-{questions.html,answers.md}`, `br/BR.md`, `br/BR.clauses.json`, `br/frames/*.md`,
`br/frames/index.md`, `br/frames/<id>.run.json`, `br/line-status.{json,html}`.

## Mode 1 — `/br interview`
1. Đọc TẤT CẢ file trong `llmwiki/raw/` (chỉ đọc — luật cấm ghi raw/). Nếu trống → hỏi user bỏ tài liệu vào.
2. Đối chiếu bộ specs chuẩn `skills/br/assets/spec-template.md`: bóc thông tin từ raw map vào từng field S1–S10 → ghi `br/spec-filled.md`. MỖI field ghi `status` (`filled|missing|conflict|assumed`) + `provenance` (`raw:<file>`).
3. Gap-diff: field `missing`/`conflict` → sinh bộ câu hỏi. Ghi 2 file (cùng số thứ tự NNN):
   - `br/interview/NNN-questions.html` — xem theo section, có giải nghĩa thuật ngữ, in full-path (R16), dark-mode. CHỈ hỏi phần thiếu.
   - `br/interview/NNN-answers.md` — block điền theo field-id (vd `## S4.2` … khoảng trống), để user gõ câu trả lời.
4. **STOP** — báo user mở HTML xem + điền answers.md.
5. Nếu user bật `--lens-fill` (hoặc nói "cho chuyên gia điền mục chưa chắc"): bốc lens bằng `python3 harness/scripts/council.py roster --case product --json`, điền các field `missing` mà user đánh dấu "không chắc" → mỗi field đóng dấu `filled_by: lens:<tên>` + `verified: false`. KHÔNG trộn với câu trả lời thật của user.

## Mode 2 — `/br compile`
1. Đọc `br/spec-filled.md` + `br/interview/*-answers.md` đã điền.
2. Sinh `br/BR.md`: mỗi điều khoản có `clause_id` (kế thừa field-id, vd `S4.2`) + provenance (`raw|user|lens:<tên>`). Đầu file là bảng **"Giả định đang gánh"** liệt kê mọi clause `lens`/`assumed` (fail-fast: nhìn một phát biết đang cược gì).
3. Sinh `br/BR.clauses.json`: `{clause_id: {provenance, assumed: bool}}` — monitor (`/br status`) đọc file này để tô cam clause assumed.

## Mode 3 — `/br slice`
1. Đọc `br/BR.md`. ĐỀ XUẤT danh sách lát cắt: mỗi lát = {clause_ids, scope_code dự kiến (≤3 file), scope_test, acceptance_test}. **STOP cho user duyệt/sửa/gộp/tách TỪNG lát** (người-trong-vòng-lặp — chốt chặn lỗi tương quan slicer). Lô đầu ≤ 3–5 frame.
2. Ghi `br/frames/frame-NNN-<slug>.md` (schema v0 — xem frame-lint REQUIRED_FIELDS) + `parent_br_hash = sha256(br/BR.md)`.
3. Sinh registry `br/frames/index.md` (bảng frame_id · clause_ids · scope_code · status · run_log_ref) từ frontmatter các frame.
4. Gác: `python3 fdk/tools/frame-lint.py check br/frames --root . ` — xanh hết mới coi là slice xong (gồm R6 exclusive-scope: 2 frame không được giẫm cùng file).
5. `python3 fdk/tools/br-prompts.py sync` — bổ sung mục prompt cho các frame mới vào sổ `br/prompts.md` (user sửa tay được ngay).

## Mode 4 — `/br run <frame>`
**Cách gọi tất định (đã wire — mặc định IN-PLACE, MỘT cây làm việc duy nhất):**
```
python3 fdk/tools/br-run.py run br/frames/<frame>.md --root .
# xem prompt sẽ gửi mà không chạy: thêm --print-prompt
# chạy cả hàng đợi resumable: python3 fdk/tools/br-queue.py run --queue br/queue.yaml
# cần cô lập thư mục thật sự (hiếm): thêm --worktree
```
`br-run.py` tự: (0) **TIER-GATE** — frame khai `tier: compensable|irreversible` trong frontmatter (effect không-đảo: gọi API ngoài/gửi mail/ghi DB) bị CHẶN cho tới khi người chạy lại với `--ack-tier` (SHEPHERD gate-before-materialize), (1) frame-lint, (2) kiểm working-tree sạch, (3) chạy loop-runner **NGAY TRONG cây hiện tại** với revise **đã trỏ tới `fdk/tools/br-revise.py`** (render `skills/br/assets/revise-prompt.md` → `claude -p` tools bó hẹp), (4) frame xanh → commit vào nhánh hiện tại, message gắn frame_id (mốc revert/blame), (5) in tóm tắt 1 dòng, (6) ghi `run_log_ref` vào frame, (7) **ghi mốc vào SỔ TRACE** `.checkpoints.jsonl` (checkpoint-trace/SHEPHERD — record trỏ commit sẵn, không double-commit) → xem cả dây chuyền: `python3 fdk/tools/checkpoint.py list`; **rollback cả pipeline về frame bất kỳ theo TÊN**: `checkpoint.py rollback <frame_id>` (giữ lịch sử, cảnh báo effect tier không-đảo sau mốc).
**Vì sao in-place là mặc định (feedback user 05/07):** N frame = N worktree = N folder ma không ai lục; luồng người thường là *bật app lên xem*, sửa phải hiện ngay trong cây đang chạy app. **Kiểm soát không-phạm-scope nằm ở HARNESS** (diff-jail revert mỗi vòng + FINAL SCOPE SWEEP + test-hash + scope_clean + R6 exclusive-scope), không nằm ở cô lập thư mục. Không ưng kết quả → `git revert <commit frame>`.

Bước thủ công tương đương (nếu cần tinh chỉnh tay):
1. `frame-lint check` frame đó xanh. Kiểm **working-tree SẠCH** (`git status --porcelain` rỗng) — bẩn thì từ chối.
2. Tạo **git worktree riêng** từ `baseline_ref` của frame (jail filesystem — frame đầu KHÔNG đụng harness/hook/CI).
3. Chạy loop — commit per-frame VÀO WORKTREE BRANCH (không phải main); người vẫn merge tay:
   ```
   python3 harness/scripts/loop-runner.py run \
     --verify "<acceptance_test>" --revise "<adapter claude -p>" \
     --state "<scope_code>" --scope "<scope_code>" --protect "<scope_test>" \
     --baseline "<baseline_ref>" --commit-on-success \
     --commit-message "frame(<frame_id>): <muc_tieu> [<clause_ids>]" \
     --max-iter <g> --budget-seconds <g> --no-progress-k <g> --escalate-after <g> \
     --log br/frames/<id>.run.json --cwd <worktree>
   ```
   Adapter revise = `claude -p` với tools bó hẹp (`--allowedTools Edit,Write,Read,Grep,Glob` — KHÔNG Bash tự do, không network), prompt dựng từ `muc_tieu` + `scope_code` + output verify fail gần nhất.
   **Truy vết frame→code (điều kiện tiên quyết — chắc frame tạo code nào + không phạm scope):**
   - Run-log ghi `changed_files` = file THẬT frame đã đổi (≠ scope dự định); `scope_clean`=true khi mọi file ⊆ `scope_code`; `attempted_out_of_scope` = file frame ĐỊNH ghi ngoài scope nhưng đã bị revert.
   - **FINAL SCOPE SWEEP**: mọi lần loop dừng (kể cả PROTECT_VIOLATION), loop-runner revert sạch mọi file ngoài `scope_code` → worktree LUÔN scope-clean, `changed_files` LUÔN ⊆ `scope_code`. Kiểm soát hoàn toàn, không chỉ dựa lời dặn prompt.
   - `--commit-on-success` chỉ commit khi verdict=SUCCESS VÀ scope_clean; message gắn `frame_id` → `git blame` truy đúng frame. `--baseline` = commit gốc để tính diff (thường HEAD của worktree lúc bắt đầu).

### Prompt & queue (chạy nhiều frame, resume được)
- **📒 SỔ PROMPT TỔNG (nguồn ƯU TIÊN #1, user sửa tay không cần model)**: `br/prompts.md` — MỘT file, mỗi frame một mục `## <frame_id>`. Mở ra, tìm frame, sửa/THÊM nội dung thoải mái (placeholder `{{...}}` giữ nguyên để máy điền lúc chạy). `python3 fdk/tools/br-prompts.py sync` tự thêm mục cho frame mới, KHÔNG BAO GIỜ đè mục đã sửa tay (chạy sau mỗi `/br slice`); `list`/`get <frame_id>` để tra. Thứ tự ưu tiên khi run: **sổ prompt > queue inline > prompt_file > template mặc định**.
- **Template gốc (seed cho sổ)**: `skills/br/assets/revise-prompt.md`. Adapter `fdk/tools/br-revise.py` render nguồn thắng cuộc → gọi `claude -p` (tools bó hẹp). Xem prompt sẽ gửi: `br-revise.py run --frame <f> --verify "<cmd>" --print`.
- **File QUEUE** (`br/queue.yaml`, mẫu `skills/br/assets/queue.example.yaml`): DANH SÁCH frame để chạy tuần tự; mỗi mục hoặc `prompt_file:` (trỏ file template) HOẶC `prompt:` (ghi text trực tiếp, vẫn hỗ trợ placeholder). Driver `fdk/tools/br-queue.py run --queue br/queue.yaml` chạy từng mục, ghi `status` back sau MỖI mục → **chạy lại queue = bỏ qua `done`, chạy tiếp** (resume). `--dry-run` xem mỗi mục dùng prompt nào; `list` xem trạng thái.
- Adapter `claude -p` là ranh giới `verified:false` (BNAL) — template + queue + render đều tất định + selftest (`br-revise.py selftest`, `br-queue.py selftest`).
4. **Điều kiện KILL viết TRƯỚC** (via negativa): vd diff-jail cắn ≥2 lần / test-hash cắn 1 lần → vứt cả run, không cứu, không nâng phanh.
5. Loop dừng → in **tóm tắt MỘT DÒNG** (verdict · số vòng · diffstat · lệnh verify cuối) + chạy `python3 fdk/tools/medic.py --ci`. **STOP** — người đọc diff trong worktree, tự quyết merge/chạy-tiếp/vứt.
6. Điền `run_log_ref` + `outcome` vào frame + registry. Ghi lesson (kể cả điều KHÔNG xảy ra — phanh nào chưa từng cắn).

## Mode 4b — `/br find <file-hoặc-từ-khoá>` — trỏ vào chỗ lỗi, ra frame/prompt phụ trách
Luồng người thường: bật app → thấy lỗi → trỏ vào khúc đó:
```
python3 fdk/tools/br-find.py "src/auth/login.py"     # theo file
python3 fdk/tools/br-find.py "đăng nhập"              # theo từ khoá / clause
```
In ra: frame phụ trách (khớp theo file THẬT đã đổi > scope_code > từ khoá) · điều khoản BR · **prompt nằm ở đâu** (inline trong queue.yaml / prompt_file / template mặc định) · lệnh chạy lại ĐÚNG frame đó sau khi sửa prompt. Hoạt động được vì R6 exclusive-scope (frame-lint) ép mỗi file chỉ thuộc MỘT frame.

## Mode 5 — `/br status`
1. `python3 fdk/tools/build-line-status.py build --root .` → `br/line-status.json` + `llmwiki/html/line-status.html`.
2. In tóm tắt 3 dòng (tổng quan trạng thái · frame đáng chú ý nhất · đường dẫn HTML). Trang cho truy ngược lỗi→frame→clause; clause assumed tô cam → quay `/br interview` vòng sau nếu lỗi rơi vào assumed.

## Rules
- **Người là cổng cuối** — KHÔNG tự commit/merge output frame; dry-run + người duyệt (council 028).
- **Phanh bất khả xâm phạm** — không bao giờ nâng max_iter hay tắt guard "để nó xong". Thừa phanh rẻ hơn thiếu phanh (council 031/032).
- **Prompt-dặn KHÔNG phải lớp an toàn** — scope-jail/test-hash là code tất định (loop-runner guard 5/6), không phải lời dặn trong prompt (council 5/5 ghế).
- **Lens-fill luôn `verified: false`** — không trộn với câu trả lời thật; luôn hiện ở bảng "Giả định đang gánh".
- **Slicer người-trong-vòng-lặp** ở đợt đầu — chưa full-auto (lỗi slicer là lỗi tương quan, blast-radius = toàn BR).
- **File-first, on-demand** — mọi artifact là file travel-được; skill gọi tay, KHÔNG hook auto-fire (ADR-004).
- HTML sinh ra cho người xem phải giải nghĩa thuật ngữ + in full-path (R16).
