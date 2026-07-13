# AUDIT thị giác + frame — Lume (visual-qa) 2026-07-13

> Bằng chứng: `qa-audit/MANIFEST.json` — 7 route, mỗi route có ảnh thật (ASSERT OK).
> Agent ĐỌC ảnh `/`, `/attachments` rồi chấm. Không kết luận bằng suy luận.

## A. Lỗi giao diện (nhìn thấy trên ảnh)

| # | Route | Lỗi | Mức | Nguyên nhân GỐC |
|---|-------|-----|-----|-----------------|
| F7 | `/`, `/attachments` | **Bóng bị CẮT thành vệt chữ nhật xấu** — search bar, tab chips (Media/Audio/Documents), cụm lịch, editor card | CAO | Ép `box-shadow !important` lên phần tử nằm TRONG container `overflow:hidden` → bóng bị clip. Selector quá rộng (`.rounded-lg.border`) trúng cả container con. |
| F8 | mọi route | **Sidebar màu KEM ≠ nền chính xanh-xám** → vỡ luật "một mặt đơn sắc" (neumorphism move 1) | CAO | memos có token RIÊNG `--sidebar: oklch(0.9663 …)` trong `themes/default.css`; `neumorphism.css` **chưa override `--sidebar*`** nên giữ màu gốc. |
| F9 | sidebar | Icon phẳng, không có trạng thái nổi/lõm nhất quán | TB | Chưa style icon-button trong sidebar. |

## B. AUDIT FRAME — lỗ hổng khiến lỗi LỌT (quan trọng hơn A)

`frame-n03-theme-neumorphism` (frame quyết định TOÀN BỘ theme UI) đang khai:

```yaml
ui_role: none                 # ❌ SAI — frame theme ảnh hưởng toàn bộ UI
acceptance_test: "(reverse)"  # ❌ KHÔNG hit gì — chạy lại frame không kiểm được UI
```

**Hệ quả:** frame "xanh" trong khi UI vỡ. Không có gate nào cắn. Đây ĐÚNG lỗ hổng đã chỉ ra:
*sửa UI = edit frame + chạy lại, nhưng nếu acceptance không hit UI thì chạy lại vô nghĩa.*

**Vi phạm chính luật đã cắm** (skill `br` § "Vòng tự-kiểm THỊ GIÁC"): frame `ui_role≠none`
phải có `acceptance_test` = visual-qa `--assert`.

### Sửa cấu trúc (bắt buộc, làm trước CSS)
```yaml
ui_role: screen               # theme ảnh hưởng mọi màn
acceptance_test: "node skills/visual-qa/assets/route-shots.mjs --base http://localhost:5230 \
                  --route / --assert --user demo --pass demo --out br/memos/qa-gate"
```
→ chạy lại frame = tự chụp + kiểm UI. Không còn "xanh giả".

## C. Vòng sửa (fix → chụp lại → đọc lại → mới cho pass)
1. Frame n03: `ui_role` + `acceptance_test` (cấu trúc).
2. F8: override `--sidebar*` tokens trong `neumorphism.css`.
3. F7: thu hẹp selector, bỏ shadow trên child trong `overflow:hidden`.
4. Chạy lại visual-qa → ĐỌC ảnh → chỉ khi thấy sạch mới ghi FIXED (không khai pass bằng lời).
