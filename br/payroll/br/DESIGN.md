# DESIGN — Payroll CTD/Unicons

> Kế thừa `skills/br/assets/design-template.md` (§3 hệ thống thị giác dùng chung — KHÔNG sửa).
> File này chỉ CHỌN archetype + điền token cho sản phẩm. BR trỏ tới đây qua clause **C15.3**.

## 1. Bối cảnh

App nội bộ cho HR/C&B: đọc bảng lương 4.000+ dòng, soi từng con số, truy vết công thức.
Người dùng ngồi trước nó hàng giờ vào tuần chốt lương. Ưu tiên: **đọc số không mỏi mắt**,
không phải "wow". Tĩnh, sang, ít chuyển động.

## 2. Vibe + Layout (§3.2)

- **Vibe 0 — Neumorphism** (mặc định của dây chuyền; template nêu đích danh *"app nghiệp vụ/dashboard/form nội bộ như Payroll"*). **Không đổi.**
- **Layout 1 — Asymmetrical Bento**: hàng thẻ tổng quan lệch cỡ (tổng chi phí kỳ · số nhân sự · trạng thái đối chiếu ground-truth), dưới là thẻ lớn chứa bảng lương. Mobile → `grid-cols-1`.

## 3. Token (§4 — palette Neumorphism)

| Token | Light | Dark |
|---|---|---|
| `--bg` (= mặt phẳng, dùng CHUNG cho card) | `#e0e5ec` | `#2a2d32` |
| `--ink` (chữ chính, **AAA ≥ 7:1**) | `#14171c` (14,19:1) | `#e8ebf0` (11,56:1) |
| `--muted` (chữ phụ, **AAA ≥ 7:1**) | `#3a4049` (8,26:1) | `#b8bec7` (7,39:1) |
| `--accent` (CTA — **near-black, LẬT theo theme**) | `#1c1f26` | `#eef1f5` |
| `--accent-ink` (chữ TRÊN accent — lật ngược) | `#f4f6f9` | `#14171c` |
| `--sh-light` | `rgba(255,255,255,.75)` | `rgba(255,255,255,.04)` |
| `--sh-dark` | `rgba(163,177,198,.55)` | `rgba(0,0,0,.55)` |
| `--danger` (semantic — chỉ dùng cho ô LỆCH ground-truth) | `#b3261e` | `#f2b8b5` |

**Cấm:** `--card` riêng · viền `1px solid` · bóng tối gắt một hướng · hardcode `color:#fff` trên accent
(accent lật thì chữ phải lật ngược — dùng `--accent-ink`).

## 4. Công thức bắt buộc (§3.6)

```css
/* khối nổi (extrude) — ĐÚNG 2 bóng, cùng offset/blur */
box-shadow: -6px -6px 12px var(--sh-light), 6px 6px 12px var(--sh-dark);
border-radius: 16px;

/* trạng thái lõm (input, hàng đang chọn, nút đang nhấn) — ĐẢO vào trong */
box-shadow: inset -4px -4px 8px var(--sh-light), inset 4px 4px 8px var(--sh-dark);
```

## 5. Chữ & số (§3.1)

- Font: **Plus Jakarta Sans** (fallback `system-ui`). **Cấm** Inter / Roboto / Arial / Open Sans / Helvetica.
- Số tiền: `font-variant-numeric: tabular-nums`, căn phải, phân cách `.` kiểu Việt Nam.
- Bảng dữ liệu dày: row-height ~30px — HR đọc 4.000 dòng, đây không phải landing page.

## 6. Theme

Toggle `role="switch"` + `localStorage` + script chống FOUC đặt trong `<head>` **trước** khi body render.
`prefers-color-scheme` là mặc định, không ép mode. **Dark là một TRẠNG THÁI phải kiểm**, không phải phần thêm.

## 7. Cổng chốt máy-kiểm (§3.5 — "tương phản là CON SỐ, cấm ước lượng bằng mắt")

`tests/test_f15.py` assert cứng, FAIL là đỏ frame:
- Không có font cấm; có font hợp lệ.
- Không có viền `1px solid`.
- Mọi khối nổi dùng **cặp** `--sh-light` + `--sh-dark`; có ít nhất một trạng thái `inset`.
- `border-radius` ≥ 12px.
- Card **không** có màu nền riêng khác `--bg`.
- Accent **lật** giữa light và dark (hai giá trị khác nhau).
- **Tương phản tính bằng số**: `--ink` trên `--bg` và `--muted` trên `--bg` đều **≥ 7:1 (AAA)**, ở CẢ hai theme.
- Toggle + `localStorage` + chống FOUC.

> Mọi tỷ lệ tương phản trên đã TÍNH BẰNG MÁY, không ước lượng. Bản đầu tôi để `--muted` tối là
> `#aeb4bd` → chỉ 6,62:1, **trượt AAA** — đúng cái bẫy template cảnh báo. Đã thay `#b8bec7`.

## 8. Ngoài phạm vi

Không animation phức tạp (app tĩnh, đọc số). Không icon set ngoài (dùng ký tự/SVG inline nét mảnh).
