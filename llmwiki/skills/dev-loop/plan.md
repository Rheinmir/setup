---
name: plan
description: >-
  Mở rộng một draft SPEC ĐÃ ĐƯỢC DUYỆT thành kế hoạch thi hành được — file `DDMMYY-<tên>-PLAN.md`
  mà một agent KHÔNG có context nào (CLI rẻ chạy headless, không hỏi lại được) vẫn làm đúng:
  đường dẫn file chính xác, khối Interfaces (Consumes/Produces) khai chữ ký cho task hàng xóm,
  ràng buộc bao trùm chép nguyên văn, và từng bước 2-5 phút kiểu TDD có code thật + lệnh chạy +
  output mong đợi. Gọi SAU `/propose` và SAU khi user duyệt ở cổng, TRƯỚC khi dispatch task cho agent.
  Trigger - "viết plan", "mở rộng proposal thành plan", "plan thi hành", "chuẩn bị brief cho agent",
  "/plan". KHÔNG dùng để thiết kế hay để hỏi yêu cầu (đó là `/propose`), KHÔNG dùng khi chưa có SPEC duyệt.
---

# Skill: plan

## Purpose
Biến SPEC đã duyệt thành văn bản mà **một kỹ sư giỏi nhưng không biết gì về codebase này, và gu thì đáng ngờ** vẫn thi hành đúng. Trong overstack, "kỹ sư" đó thường là một CLI rẻ chạy headless (`opencode` / `agy` / `kiro`): nó **không thừa hưởng context nào** của phiên chính, **không hỏi lại được**, và khi gặp chỗ mơ hồ nó sẽ **đoán rồi im lặng**. Thực đo bài học 250626: brief mỏng → giao hàng ~1/5.

Cái gì không nằm trong PLAN thì agent không có. Đó là toàn bộ nguyên lý của skill này.

## When to use
- SPEC (`/propose`) đã được user duyệt ở cổng, và sắp dispatch task cho agent.
- Việc nhiều bước, nhiều file, hoặc chia cho ≥2 agent chạy song song.
- KHÔNG dùng khi chưa có SPEC duyệt (dùng `/propose` trước), và không dùng cho sửa một dòng.

## Steps
1. **Đọc SPEC đã duyệt** — `llmwiki/wiki/sources/draft/DDMMYY-<tên>.md`. Lấy nguyên: `## Context`, `## Global constraints`, `## Plan` (các dòng `- [ ]`), `## Agent Task Assignment`.
2. **Scope check** — SPEC ôm nhiều hệ con độc lập → tách thành nhiều PLAN, mỗi PLAN tự nó ra được phần mềm chạy được và test được. Đừng nhồi.
3. **Vẽ `## File structure` trước khi chia task** — liệt kê mọi file sẽ tạo/sửa và trách nhiệm của từng file (một file một trách nhiệm; file nào đổi cùng nhau thì ở cùng chỗ). Quyết định phân rã bị chốt ở đây, không phải trong lúc code.
4. **Chia task đúng cỡ** — một task là đơn vị **nhỏ nhất có chu kỳ test riêng và đáng một lượt review**. Setup, config, scaffolding, docs → gộp vào task cần chúng; chỉ tách khi một reviewer có thể *bác task này mà vẫn duyệt task kia*. Mỗi task kết thúc bằng một deliverable test được độc lập.
5. **Viết từng task theo khuôn dưới** (bắt buộc đủ Files + Interfaces + Steps).
6. **Self-review** (3 mắt lưới, mục 'Self-review' bên dưới), sửa tại chỗ.
7. **Ghi file** `llmwiki/wiki/sources/draft/DDMMYY-<tên>-PLAN.md`, thêm dòng vào `llmwiki/wiki/index.md`, append `llmwiki/wiki/log.md`.
8. Bàn giao: mỗi `### Task N` là một `orca orchestration task-create`; `dispatch --inject` bơm **nguyên văn** brief của task đó **kèm `## Global constraints`**. Không tóm tắt lại — tóm tắt là chỗ context rụng.

## Khuôn PLAN

Header bắt buộc (frontmatter và `## Origin` KHÔNG được bỏ — file nằm trong `wiki/sources/draft/` nên R9 chặn nếu thiếu frontmatter, R2 chặn nếu thiếu `## Origin`):

```markdown
---
type: draft
title: <tên>-PLAN
status: proposed
timestamp: YYYY-MM-DD
task: T-YYMMDD-NN        # cùng task-id với SPEC
---

# <Tên> — PLAN thi hành

**Goal:** <một câu: cái này xây ra cái gì>
**Architecture:** <2-3 câu: cách tiếp cận>
**Tech stack:** <ngôn ngữ, lib, test runner, version>
**SPEC nguồn:** `wiki/sources/draft/DDMMYY-<tên>.md` (đã duyệt <ngày>)

## Origin
- **SPEC:** `wiki/sources/draft/DDMMYY-<tên>.md`
- **Commit:** _(verify-before-commit điền)_

## Global constraints
<chép NGUYÊN VĂN từ SPEC — sàn version, giới hạn dependency, luật đặt tên, gate trước push.
 Mỗi task ngầm mang theo section này.>

## File structure
- Tạo `path/chính/xác.py` — <trách nhiệm duy nhất của file>
- Sửa `path/có/sẵn.py` — <đổi gì>
```

Mỗi task:

````markdown
### Task N: <tên>

**Files:**
- Tạo: `đường/dẫn/chính/xác.py`
- Sửa: `đường/dẫn/có/sẵn.py:123-145`
- Test: `tests/đường/dẫn/test_x.py`

**Interfaces:**
- Consumes: <dùng gì từ task trước — chữ ký chính xác>
- Produces: <task sau dựa vào cái gì — tên hàm, kiểu tham số, kiểu trả về>

- [ ] **Step 1: viết test fail**

```python
def test_hanh_vi_cu_the():
    assert ham(dau_vao) == ket_qua_mong_doi
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Chạy: `pytest tests/đường/dẫn/test_x.py::test_hanh_vi_cu_the -v`
Mong đợi: FAIL — `NameError: name 'ham' is not defined`

- [ ] **Step 3: code tối thiểu cho pass**

```python
def ham(dau_vao):
    return ket_qua_mong_doi
```

- [ ] **Step 4: chạy lại — PASS**

Chạy: `pytest tests/đường/dẫn/test_x.py::test_hanh_vi_cu_the -v`
Mong đợi: PASS

- [ ] **Step 5: commit**

```bash
git add tests/đường/dẫn/test_x.py src/đường/dẫn/x.py
git commit -m "feat: <việc cụ thể>"
```
````

**Vì sao `Interfaces` là bắt buộc khi có ≥2 agent:** agent thi hành **chỉ nhìn thấy task của chính nó**. Không khai chữ ký thì hai agent song song đặt tên hàm lệch nhau và phần ghép vỡ — đây là lỗi *chắc chắn* xảy ra, không phải rủi ro.

## Cấm placeholder — đây là plan HỎNG, không phải plan chưa xong
R7 chặn ở write-time và commit. Không bao giờ viết:
- `TBD`, `TODO`, "điền sau", "chi tiết sau"
- "xử lý lỗi phù hợp" / "thêm validation" / "handle edge cases" — nói *làm gì*, không nói "làm cho phù hợp"
- "viết test cho phần trên" mà không có code test thật
- **"tương tự Task N"** — chép lại code ra. Agent có thể đọc task không theo thứ tự, và mỗi agent chỉ được bơm task của nó.
- Bước mô tả *phải làm gì* mà không chỉ *làm thế nào* (bước đổi code thì bắt buộc có code)
- Nhắc tới hàm/kiểu/method không được định nghĩa ở bất kỳ task nào

## Self-review
Viết xong, soi lại bằng mắt mới — sửa tại chỗ, không cần vòng hai:
1. **Phủ SPEC** — lướt từng yêu cầu trong SPEC, chỉ ra được task nào thực hiện nó. Thiếu → thêm task.
2. **Quét placeholder** — dò đúng các mẫu ở mục trên.
3. **Nhất quán kiểu/tên** — tên hàm, chữ ký, tên field dùng ở task sau có khớp cái định nghĩa ở task trước không? `clearLayers()` ở Task 3 mà `clearFullLayers()` ở Task 7 là một con bug.

## Cổng ngược — `/plan` được quyền BÁC SPEC
Viết PLAN chính là cách phát hiện SPEC sai: tới lúc phải khai đường dẫn file thật và chữ ký hàm thật thì thiết kế bất khả thi mới lòi ra. Nếu cổng duyệt đã cho qua rồi mà giờ mới lòi, nghĩa là user đã duyệt một thứ không xây được — cổng đã hỏng.

**DỪNG, không viết tiếp PLAN nửa vời**, khi gặp bất kỳ điều nào:
- Một yêu cầu trong SPEC không quy được về task nào làm được.
- Hai mục trong SPEC mâu thuẫn nhau, hoặc mâu thuẫn với `## Global constraints`.
- Phương án đã chọn ở `## Approaches` hoá ra bất khả thi (file không tồn tại, API không có, ràng buộc chặn).
- Phải bịa một hàm/kiểu/file mà SPEC không hề nhắc, để cho plan "chạy được trên giấy".

Xử lý: **gom TẤT CẢ chỗ vỡ thành MỘT lần báo** (không ngắt user từng phát một), mỗi chỗ kèm đúng câu trong SPEC gây ra nó, rồi quay về `/propose` sửa SPEC và **duyệt lại**. Một PLAN viết trên nền SPEC hỏng còn tệ hơn không có PLAN: nó bơm cái sai vào agent với vẻ mặt tự tin, và agent rẻ sẽ thi hành nguyên xi.

## Rules
- PLAN **không cần** file `.html` — nó là thứ máy đọc. HTML gắn với SPEC (thứ người xem lúc duyệt), do `/propose` sinh. R7 miễn check diagram cho nhánh `-PLAN.md`.
- Đường dẫn file **luôn chính xác**, kèm dải dòng khi sửa file có sẵn.
- Bước đổi code thì **phải có code đầy đủ** — không mô tả suông.
- Lệnh chạy **chính xác**, kèm **output mong đợi** (agent cần biết thế nào là fail đúng, thế nào là pass).
- DRY, YAGNI, TDD, commit thường xuyên.
- Trong codebase có sẵn: theo pattern đang có. Đừng nhân tiện refactor thứ ngoài task.
