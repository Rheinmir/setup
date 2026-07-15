---
type: unknown-ledger
title: "unknown — <source-slug>"
status: open
source_task: T-YYMMDD-NN
source_spec: wiki/sources/draft/DDMMYY-<source>.md
timestamp: YYYY-MM-DD
---

# Unknown ledger — <source-slug>

> **Nợ unknown** — model đã *fill-first* (điền default để không chặn việc), *find-out-later* (chờ thông tin thật để trả nợ). KHÔNG chặn cổng; hiện ra ở `/lint` để không chìm. Đóng khoảng hở giữa `(default)` và `[CẦN LÀM RÕ]`. Xem `[[150726-unknown-ledger]]`.
>
> Thêm/đóng mục bằng `python3 harness/scripts/unknown-ledger.py` — đừng sửa số U-NN bằng tay.

## U-01 — <câu hỏi / điều chưa biết>
- **Trace:** FR-<NNN> · SPEC `wiki/sources/draft/DDMMYY-<source>.md` · task `T-YYMMDD-NN`
- **Đã fill (default):** <giá trị model tự chọn để việc chạy tiếp>
- **Cần verify:** <thông tin thật phải lấy để biết default đúng hay sai>
- **Rủi ro nếu default sai:** <điều gì hỏng nếu đoán sai>
- **Status:** open
- **Resolved:** _(khi có thông tin thật: giá trị đúng · đã fix ở đâu · ngày · nếu code đã sai thì link issue)_

## Origin
- Sinh bởi `/propose` khi user chọn "fill-first, find-out-later" cho một unknown của SPEC nguồn.
- Trả nợ: `unknown-ledger.py --resolve <file> <U-id> --value … --fixed … --date …`.
- **Commit:** _(verify-before-commit điền)_
