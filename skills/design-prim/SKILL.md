---
name: design-prim
description: Dọn slop UI/UX khi onboard 1 dự án bất kỳ — quét view có sẵn, chụp playwright, trích bộ thông số thiết kế (PRODUCT.md/DESIGN.md) qua impeccable, khoá 1 hệ style xuyên suốt bằng hallmark, rồi quét lại bằng slop-test 6-trục + 58 gate cộng audit impeccable. Gọi khi user nói "dọn slop", "làm gọn UI dự án", "chuẩn hoá UI xuyên suốt", "onboard rồi làm sạch UI", "design prim", "/design-prim".
---

# Skill: design-prim

`design` (bộ thông số thiết kế: PRODUCT.md/DESIGN.md) + `prim` (chuẩn chỉnh, đúng chuẩn impeccable, không xộc xệch).

Nén 1 lần: `orca-onboard` (bỏ — quá nặng, hallmark tự quét token ở bước 4 rồi) + `playwright-verify` +
`impeccable` (bundle `doyourmagic/impeccable`) + `hallmark` (sàn design + slop-test). Không viết lại
logic của bốn skill này — chỉ gọi đúng thứ tự, đúng target.

## When to use
- Vừa nhận 1 dự án lạ (onboard) và cần đưa UI về một chuẩn nhất quán, không lộ dấu AI-slop.
- Đã có nhiều view/màn hình rời rạc, mỗi chỗ một kiểu, cần khoá lại một hệ.
- KHÔNG dùng khi chỉ sửa 1 component nhỏ (dùng thẳng `hallmark` component-scope) hoặc khi cần hiểu sâu
  kiến trúc/business logic ngoài UI (đó là `orca-onboard` đầy đủ, không phải skill này).

## Steps
0. **`impeccable` đã cài trong dự án đích chưa?** Chưa → chạy theo
   `.overstack/doyourmagic/impeccable/skills/dym-impeccable-install-into-your-project/SKILL.md`
   (nhớ bẫy: luôn `npx impeccable install -y --scope=project --providers=claude`, đừng gõ `--help`).
1. **Liệt kê view/route** — Explore agent hoặc grep thẳng router/pages config của dự án đích. Không
   cần skill riêng, không cần `orca-onboard`.
2. **Chụp hiện trạng** từng view bằng `playwright-verify`.
3. **Trích thông số** — gõ trong chat của dự án đích: `/impeccable init` rồi `/impeccable document`
   → sinh `PRODUCT.md` + `DESIGN.md` (màu, typography, spacing, radii, component, format Google Stitch).
4. **Khoá 1 hệ xuyên suốt** — `hallmark redesign <target>` cho từng view; Step 0 Pre-flight scan của
   hallmark đọc `DESIGN.md`/token vừa có ở bước 3, sinh/khoá `design.md` ở root, mọi view sau bám
   cùng token (Step 2.6 Theme route của hallmark).
5. **Quét lại** — `hallmark` slop-test.md (six-axes pre-emit self-critique + 58 gate) trên từng view đã
   redesign, cộng `/impeccable audit` (điểm P0–P3: a11y, perf, theming, responsive).

## Rules
- Thứ tự 0→5 không đảo: bước 4 phụ thuộc `DESIGN.md` của bước 3; bước 5 chấm trên kết quả bước 4.
- Bước 3–5 là lệnh **chat** (`/impeccable ...`, hallmark là skill), không phải shell — đừng gõ vào terminal.
- Không tự thêm `orca-onboard` lại trừ khi user cần hiểu kiến trúc/business logic ngoài phạm vi UI.
- Đã cài `impeccable` global rồi (không phải project) → gỡ/cài lại đúng scope trước khi chạy bước 3,
  tránh lẫn artifact của dự án khác (xem bẫy 2 trong `dym-impeccable-install-into-your-project`).
