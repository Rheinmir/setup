# Pattern: Controlled Output Renderer (COR)

Chưng từ `council.py` Stage-4. Mục tiêu: bất kỳ skill nào có **dữ liệu có cấu trúc**
cần biến thành **file HTML/md chia sẻ được** đều dùng chung 1 contract, thay vì mỗi
skill tự chế cách render (drift, injection, coupling, ghi đè mất lịch sử).

## 6 thuộc tính bất biến (contract)

| # | Thuộc tính | Vì sao | Trong council.py |
|---|-----------|--------|------------------|
| 1 | **Data/present split** | Render KHÔNG được thêm phán xét mới; mọi số liệu từ nguồn deterministic | feed thuần từ `transcript.json` |
| 2 | **Escape mọi input** | Chuỗi do người/agent nhập → chống vỡ layout & HTML-injection tại boundary | `html.escape(..., quote=True)` |
| 3 | **Offline / self-contained** | Mở được không mạng; không coupling skill/CDN ngoài | system font + inline SVG, no CDN |
| 4 | **Versioned, no-overwrite** | Mỗi lần chạy = 1 bản ghi bất biến; không diff-churn; giữ lịch sử | `name-NNN-...html` + `latest` (gitignore) |
| 5 | **Isolation (try/except)** | Lỗi renderer KHÔNG được giết lệnh core/artifact gốc (blast-radius) | core ghi TRƯỚC, render bọc try/except → WARN |
| 6 | **Deterministic** | Cùng input → cùng output (byte) để audit/regression | không Date/random trong render |

## Hình dạng API tái dùng (đề xuất — chưa chốt)

```
harness/scripts/lib/cor.py
  write_report(data, *, renderer, out_dir, stem, escape=True) -> Path
    - versioning NNN, latest pointer, try/except, mkdir
  esc(x)                      # html.escape wrapper
  render_shell(title, sections, *, offline=True) -> str   # khung glass/paper chung
```
Mỗi skill chỉ cung cấp `renderer(data) -> [sections]`; COR lo 6 bất biến.

## Ứng viên áp (điền sau khi survey xong)
- **propose** — luật repo yêu cầu cặp `.md`+`.html`; hiện render thủ công → fit cao?
- orca-eval / orca-sec-scans / wikieval / trace-grader / uat-nonit-testcase — report từ scan/eval có cấu trúc.

## Nghi vấn cần /council thẩm định
1. Generalize có over-abstract không (chỉ 1-2 skill thật sự share) — YAGNI?
2. Ranh giới: skill render-thuần (docs-site-macos) vốn ĐÃ là renderer — COR có chồng vai?
3. Chi phí maintain 1 lib dùng chung vs copy-paste 6 bất biến vào từng skill.
4. Nên là LIB (import) hay SKILL (guidance) hay RULE (harness gate kiểm 6 thuộc tính)?

## Origin
- Draft khảo sát overnight; nguồn: council.py render_report_html + _write_report.
