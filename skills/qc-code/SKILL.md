---
name: qc-code
description: >-
  Review code phong cách SENIOR 10 năm — bốn mục security · performance · naming · logic, mỗi mục cho
  ĐIỂM/10 + LỖI NẶNG NHẤT + CÁCH SỬA, rồi một kết luận PASS-sang-bước-kế hay CẦN-SỬA. Mục logic tìm bug
  (null/rỗng/âm/overflow, off-by-one, race) và SINH một test-case tái hiện cho mỗi bug (đặt tên qc-*),
  các test đó auto-chạy qua hook tất định (0-token, không LLM). Gọi khi user nói "qc code", "review code",
  "soi code", "chấm điểm code", "kiểm tra chất lượng code", "/qc-code". KHÁC /orca-sec-scans (Trivy quét
  TĨNH — vuln/misconfig/secret) và /code-review built-in (review tổng quát): qc-code là format senior
  bốn-mục-chấm-điểm-verdict + sinh test tái hiện. Mặc định review DIFF hiện tại; chỉ định file khi cần.
---

# Skill: qc-code

## When to use
- User muốn một cặp mắt senior soi code trước khi chốt: "review code", "soi code", "chấm điểm code".
- Trước commit một thay đổi đáng kể — cắm tùy chọn vào `/orca-workflow` trước `verify-before-commit`.
- KHÔNG dùng cho: quét bảo mật tĩnh (đó là `/orca-sec-scans` — Trivy) hay xử lý một sự cố đã xảy ra (đó là `/orca-issue` — repro-first).

## Phạm vi review (mặc định = diff hiện tại)
Mặc định soi **thay đổi kể từ base** (`git diff` từ commit/branch gốc) — đúng lúc trước commit, nhanh, đúng thứ vừa viết. User chỉ định file/thư mục thì soi cái đó. KHÔNG mặc định toàn codebase (chậm, tốn token, phần lớn không đổi).

## Steps
1. **Xác định phạm vi** — `git diff <base>..HEAD --stat` (hoặc file user nêu). Đọc code trong phạm vi đó.
2. **Chấm bốn mục** (mục dưới). Mỗi mục: **điểm/10 · lỗi nặng nhất · cách sửa**. → Xong khi cả bốn mục đều có đủ ba phần.
3. **Mục logic: sinh test tái hiện** cho mỗi bug (mục "logic & bug" bên dưới). → Xong khi mỗi bug có một test đỏ chạy được.
4. **Kết luận** — `PASS` (sang bước kế) hay `CẦN SỬA` (liệt kê phải sửa gì trước khi pass). → Xong khi verdict rõ + danh sách phải-sửa nếu CẦN SỬA.
5. **Ghi test vào dự án** (mục "Ghi test" dưới) + nhắc `qc-regression.py --run` auto-chạy chúng.

## Bốn mục

### 1. Security — điểm/10 · lỗi nặng nhất · cách sửa
Soi: **SQL injection** (chuỗi nối vào query, thiếu parameterize) · **XSS** (output không escape, `innerHTML`/`dangerouslySetInnerHTML`) · **lộ API key / secrets** (hardcode key, secret trong log/repo) · **validate input** (nhận dữ liệu ngoài không kiểm) · **phân quyền** (thiếu check ai-được-làm-gì, IDOR). Đây là ranh giới tin cậy — không lười ở đây (carve-out CLAUDE.md).

### 2. Performance — điểm/10 · lỗi nặng nhất · cách sửa · 3 điểm chậm nhất
Soi: **query N+1** (vòng lặp gọi DB từng phần tử thay vì một query) · **vòng lặp lồng vô ích** (O(n²) khi O(n) đủ) · **memory leak âm thầm** (listener/timer không gỡ, ref giữ mãi, cache không giới hạn). **Chỉ ra 3 điểm chậm nhất** và cách tối ưu từng cái (với ước lượng độ lớn: O(?), số round-trip).

### 3. Naming & readability — điểm/10 · lỗi nặng nhất · bảng đổi tên
Soi: **tên có nói đúng việc nó làm** không (hàm `getUser` mà ghi DB, biến `data` vô nghĩa) · **convention nhất quán** (camelCase/snake_case lẫn lộn, số nhiều/ít lộn). **Trả về bảng:**

| Tên cũ | Tên mới | Lý do |
|--------|---------|-------|
| `d` | `dueDate` | tên một chữ không nói được gì |

### 4. Logic & bug — điểm/10 · lỗi nặng nhất · TEST tái hiện mỗi bug
Soi: **edge case** (null · rỗng · số âm · overflow) · **off-by-one** (`<` vs `<=`, index cuối) · **race condition** (state chia sẻ, await xen kẽ, đọc-rồi-ghi không atomic). Mỗi bug tìm được → **viết một test-case ĐỎ tái hiện lỗi** (chứng minh bug có thật, không phải nghi ngờ). Test đỏ là dữ kiện; verdict là ý kiến.

## Kết luận (verdict)
Một trong hai, kèm lý do:
- **PASS** — không lỗi nặng ở mục nào, sang bước kế được.
- **CẦN SỬA** — liệt kê **cụ thể** phải sửa gì trước khi pass (ưu tiên security + logic-có-test-đỏ trước naming).

> **Verdict là ADVISORY — người quyết, không chặn commit.** Thứ gác cứng là các test tái hiện (đỏ→xanh). Đừng để user tưởng "qc-code PASS = an toàn tuyệt đối"; nó là một cặp mắt senior, không phải bằng chứng.

## Ghi test tái hiện vào dự án
Mỗi test ở mục logic:
- **Đặt vào thư mục test chuẩn của dự án** — tự phát hiện: `tests/` · `test/` · `__tests__/` · file `*_test.py` · `*.spec.ts` · `*.test.js` cạnh nguồn. Không có → báo rõ và để test cạnh file nguồn, KHÔNG đoán bừa cấu trúc.
- **Tên `qc-<slug-bug>`** (vd `qc-off-by-one-pagination`) — phân biệt test do qc-code sinh, để `qc-regression.py` gom được.
- **Chạy bằng runner có sẵn** của dự án (pytest/vitest/jest) — không đẻ framework test mới.
- Test PHẢI đỏ trước khi fix (tái hiện), xanh sau khi fix (bằng chứng). Nếu bug quay lại → test đỏ lại (chống tái phát).

## Auto-chạy test (tất định, 0-token)
`python3 harness/scripts/qc-regression.py --run` chạy đúng các test `qc-*` và báo đỏ/xanh — **không gọi LLM**. Nó auto-chạy ở `verify-before-commit` (trước commit); bật thêm PostToolUse cho phản hồi tức thì nếu muốn. Fail-open nếu chưa có test `qc-*` nào. Đây là phần "tự động hook khi sửa code" — chỉ hook phần rẻ tất định, LLM review (skill này) giữ gọi tay.

## Rules
- **Tách đắt/rẻ:** LLM review (skill này) = gọi tay / bước workflow tùy chọn. Test tự-sinh = auto-chạy qua hook tất định. KHÔNG bao giờ gọi LLM trong hook (nguyên tắc hook-0-token của overstack).
- **Verdict advisory, test tất định gác cứng** — không để LLM verdict chặn commit.
- **Không dẫm:** `/orca-sec-scans` = Trivy tĩnh · `/code-review` built-in = tổng quát · `/orca-issue` = sự cố repro-first. `/qc-code` = senior 4-mục-chấm-điểm + sinh test.
- **Review có unknown?** Nếu một nhận định phụ thuộc thứ chưa chắc (config prod, hành vi runtime chưa thấy) → ghi nợ `[[150726-unknown-ledger]]` thay vì khẳng định bừa.

## Origin
- Distill từ yêu cầu user 2026-07-15 (qc-code 4 mục + sinh test + auto-hook). Quyết định "nối vào đâu" đã hỏi user → option 3 (LLM thủ công, test auto-hook tất định), phạm vi diff hiện tại.
- Absorb qua `/propose` → `150726-qc-code-skill`, task `T-260715-04`.
- **Commit:** _(verify-before-commit điền)_
