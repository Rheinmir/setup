# QA thị giác — Lume (route-shots headless) 2026-07-12

> Sinh từ luồng `route-shots.mjs` (login + chụp 7 route) rồi agent đọc ảnh chấm.
> Mỗi finding có route + mức + cách sửa → dùng để tự bật luồng chỉnh sửa (`/br run` frame theme).

## Ảnh đã chụp
`qa-shots/{auth,home,explore,archived,attachments,inbox,setting}.png` — tất cả HTTP 200.

## Findings (ưu tiên cao→thấp)

| # | Route | Vấn đề | Mức | Cách sửa |
|---|-------|--------|-----|----------|
| F1 | auth | **Vẫn logo con vẹt + chữ "Memos"** (rebrand trượt — auth không dùng `MemosLogo`, xài `/full-logo.webp`) | CAO | Thay logo auth + gỡ mọi ref `full-logo.webp`/`logo.webp`; đổi chuỗi "Memos" còn lại |
| F2 | explore/home | **Placeholder cú/đại bàng pixel-art** (`Placeholder/pieces/*.svg`) khi rỗng — chọi premium, còn brand whimsy memos | CAO | Thay empty-state bằng khối neumorphic trung tính (icon line mảnh) |
| F3 | auth | **2 selector (English/System) màu ĐEN** không theme — chọi nền sáng | CAO | Ép chúng dùng token neumorphic (raised, `--neu-bg`) |
| F4 | home | **CTA "Save" quá nhạt** (lavender mờ, không phải accent `#4d6bfe` đặc) | TB | `.bg-primary` override bị opacity đè — ép `background:var(--neu-accent)!important; opacity:1` |
| F5 | home/explore | **List memo TRỐNG** ("No data found") — seed memo không hiện (visibility/instance) → chưa chấm được card memo | TB | Kiểm visibility seed / tạo 1 memo demo để verify card neumorphic |
| F6 | toàn cục | **Neumorphism còn nhạt/thiếu nhất quán** — search bar inset yếu, icon sidebar phẳng, spacing chưa "thở" | TB | Tăng offset shadow sidebar/search; thêm padding section; verify lại bằng chụp |

## Điểm ĐÃ đạt (giữ)
- Logo Lume (chấm sáng neumorphic) vào sidebar ✓
- Editor card + ô lịch có raised shadow đúng hướng ✓
- Nền mid-tone `#e0e5ec`, CTA phẳng (không neumorph) đúng spec ✓

## Vòng sửa kế (tự bật)
1. F1+F3 (auth rebrand + selector) → sửa `web/src/pages/SignIn.tsx` + logo.
2. F2 (placeholder) → `web/src/components/Placeholder`.
3. F4 (CTA) → neumorphism.css.
4. F5 → seed/visibility.
5. Re-run `route-shots.mjs` → so ảnh trước/sau.

## Vòng sửa #1 (2026-07-13) — verify bằng chụp lại (qa-shots2/)
- **F1 ✅ FIXED** — SignIn.tsx: logo vẹt + "Memos" → Lume mark neumorphic + tên "Lume" (verify signin-fresh.png).
- **F2 ✅ FIXED** — Placeholder sprite pixel-art → mark neumorphic trung tính.
- **F3 ⚠️ MỘT NỬA** — ThemeSelect ("System") đã neumorphic; LocaleSelect ("English") VẪN đen (component khác, chưa dùng data-slot=select-trigger) → vòng #2.
- **F4** — không phải bug: Save nhạt = disabled state (editor rỗng).
- **F5/F6** — còn: list memo trống (data), neumorphism polish tiếp.
