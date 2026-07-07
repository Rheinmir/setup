<!--
════════════════════════════════════════════════════════════════════════════
 design-template.md — TEMPLATE THIẾT KẾ TÁI DÙNG cho dây chuyền br
 Khung: Google-style Design Doc (Context/Scope · Goals · Design · Alternatives
 · Cross-cutting). Phần §3 "Hệ thống thiết kế thị giác" nạp từ skill
 /high-end-visual-design — DÙNG CHUNG mọi project, KHÔNG sửa khi copy.
 Cách dùng: copy file này → <project>/br/DESIGN.md, điền các ô {{...}} và §1/§2/
 §4/§6/§7 cho riêng sản phẩm; giữ nguyên §3 + §5 làm chuẩn kế thừa.
 BR.md trỏ tới file này bằng một clause NFR (vd N01 giao-diện), không chép lại.
════════════════════════════════════════════════════════════════════════════
-->
# DESIGN — {{Tên sản phẩm}}

| | |
|---|---|
| **Tác giả** | {{tên}} |
| **Trạng thái** | draft · in-review · approved |
| **Ngày** | {{YYYY-MM-DD}} |
| **BR nguồn** | `br/BR.md` (clause NFR: {{N01…}}) |
| **Design system** | §3 dưới đây (kế thừa `/high-end-visual-design`) |

---

## 1. Bối cảnh & Phạm vi (Context & Scope)
{{2–4 câu: sản phẩm là gì, ai dùng, thiết kế này phủ màn hình/luồng nào. Nêu
ràng buộc nền tảng: web/mobile, framework (React/Tailwind hay stdlib HTML…),
có phải single-file không.}}

## 2. Mục tiêu / Không phải mục tiêu (Goals / Non-goals)
**Mục tiêu**
- {{vd: mọi màn hình đạt cảm giác "agency-tier", không template-generic}}
- {{vd: dark/light toggle nhớ lựa chọn, chống FOUC}}

**Không phải mục tiêu**
- {{vd: chưa làm i18n}} · {{vd: không hỗ trợ IE11}}

---

## 3. Hệ thống thiết kế thị giác (kế thừa — KHÔNG sửa khi copy)
> Distill từ skill `/high-end-visual-design` (Vanguard_UI_Architect). Đây là
> chuẩn dùng chung; mỗi sản phẩm chỉ CHỌN archetype ở §3.2, không viết lại luật.

### 3.1 "Absolute Zero" — chống mẫu (bất kỳ cái nào lọt = fail)
- **Font cấm:** Inter, Roboto, Arial, Open Sans, Helvetica. Dùng: `Geist`, `Clash Display`, `PP Editorial New`, `Plus Jakarta Sans`.
- **Icon cấm:** Lucide/FontAwesome/Material nét dày. Dùng nét siêu mảnh: Phosphor Light, Remix Line.
- **Viền/bóng cấm:** viền `1px solid gray`; bóng tối gắt (`shadow-md`, `rgba(0,0,0,.3)`).
- **Layout cấm:** navbar sticky dán sát mép trên; grid 3 cột Bootstrap đối xứng thiếu whitespace.
- **Motion cấm:** transition `linear`/`ease-in-out`; đổi trạng thái tức thì không nội suy.

### 3.2 Creative Variance Engine — chọn 1 Vibe + 1 Layout mỗi sản phẩm
**Vibe (texture)**
1. **Ethereal Glass** (SaaS/AI): OLED đen `#050505`, mesh gradient phát sáng nhẹ, card vantablack `backdrop-blur-2xl`, hairline `white/10`, chữ Grotesk hình học rộng.
2. **Editorial Luxury** (lifestyle/agency): kem ấm `#FDFBF7`, sage/espresso, serif biến thiên tương phản cao, phủ noise film-grain `opacity-[.03]`.
3. **Soft Structuralism** (consumer/health/portfolio): nền trắng/xám bạc, Grotesk đậm cỡ lớn, component nổi với bóng khuếch tán rất mềm.

**Layout**
1. **Asymmetrical Bento** — grid card kích cỡ lệch (`col-span-8 row-span-2` cạnh cột `col-span-4`). Mobile: về `grid-cols-1`, `gap-6`.
2. **Z-Axis Cascade** — card xếp chồng, lệch nhẹ `-2deg`/`3deg`. Mobile <768px: bỏ xoay + overlap, xếp dọc.
3. **Editorial Split** — chữ khổng lồ nửa trái `w-1/2`, nội dung cuộn/pill nửa phải. Mobile: `w-full` stack dọc.

**Mobile override (chung):** <768px ép `w-full`, `px-4`, `py-8`. Full-height dùng `min-h-[100dvh]` (không `h-screen` — tránh nhảy viewport iOS Safari).

### 3.3 Haptic micro-aesthetics
- **Double-Bezel (Doppelrand):** không đặt card phẳng lên nền. **Vỏ ngoài** `div` `bg-*/5` + hairline `ring-1 ring-*/5` + `p-1.5` + `rounded-[2rem]`; **Lõi trong** nền riêng + `shadow-[inset_0_1px_1px_rgba(255,255,255,.15)]` + bán kính đồng tâm `rounded-[calc(2rem-.375rem)]`.
- **Button-in-Button:** CTA là pill `rounded-full px-6 py-3`; icon `↗` nằm trong vòng tròn riêng `w-8 h-8 rounded-full bg-*/10`, sát mép phải.
- **Spatial rhythm:** section `py-24`→`py-40`. Eyebrow tag trước H1/H2: pill `text-[10px] uppercase tracking-[0.2em]`.

### 3.4 Motion choreography
- Cubic-bezier riêng: `transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)]`.
- **Fluid Island nav:** pill kính nổi `mt-6 mx-auto w-max rounded-full`; hamburger morph thành 'X' (`rotate-45`/`-rotate-45`); menu mở overlay `backdrop-blur-3xl`; link reveal so le `translate-y-12 opacity-0` → `0/100` với `delay-100/150/200`.
- **Magnetic hover:** `group`; nhấn `active:scale-[0.98]`; icon lõi `group-hover:translate-x-1 -translate-y-[1px] scale-105`.
- **Scroll entry:** `translate-y-16 blur-md opacity-0` → `0 blur-0 100` >800ms, dùng `IntersectionObserver`/`whileInView` (KHÔNG `addEventListener('scroll')`).

### 3.5 Performance guardrails
- Chỉ animate `transform` + `opacity` (không `top/left/width/height`). `will-change` dùng dè sẻn.
- `backdrop-blur` chỉ trên fixed/sticky; không trên container cuộn.
- Noise overlay: pseudo-element `position:fixed; inset:0; pointer-events-none; z-index:50`.
- Z-index kỷ luật theo tầng hệ thống (nav/modal/overlay/tooltip), không `z-[9999]` tuỳ tiện.

---

## 4. Theme & Design tokens (điền cho sản phẩm)
> Ràng buộc bắt buộc của repo: **có toggle dark/light, nhớ localStorage, chống FOUC**
> (đặt script set `data-theme` trong `<head>` TRƯỚC khi body render).

| Token | Light | Dark |
|---|---|---|
| `--bg` | {{}} | {{}} |
| `--card` | {{}} | {{}} |
| `--ink` | {{}} | {{}} |
| `--accent` | {{}} | {{}} |

- **Cơ chế:** `:root[data-theme=dark]{…}` + `@media(prefers-color-scheme:dark){:root:not([data-theme=light]){…}}`.
- **Toggle:** nút `role="switch"`, ghi `localStorage`, đọc lại lúc load.
- **Chống FOUC:** inline `<script>` đọc localStorage → set `data-theme` ngay đầu `<head>`.

## 5. Pre-output checklist (cổng chốt — copy nguyên)
- [ ] Không dính font/icon/viền/bóng/layout/motion cấm ở §3.1
- [ ] Đã chọn 1 Vibe + 1 Layout archetype (§3.2) và áp nhất quán
- [ ] Mọi card lớn dùng Double-Bezel (vỏ ngoài + lõi trong)
- [ ] CTA dùng Button-in-Button khi có icon
- [ ] Section tối thiểu `py-24` — bố cục "thở"
- [ ] Mọi transition dùng cubic-bezier riêng
- [ ] Có scroll entry animation — không phần tử nào hiện tĩnh
- [ ] <768px về 1 cột, `w-full`, `px-4`
- [ ] Animation chỉ `transform`/`opacity`
- [ ] `backdrop-blur` chỉ trên fixed/sticky
- [ ] Dark/light toggle + localStorage + chống FOUC hoạt động
- [ ] Ấn tượng tổng: "$150k agency build", không phải "template gắn font đẹp"

## 6. Phương án đã cân nhắc (Alternatives considered)
{{Nêu 1–2 hướng thiết kế khác đã loại + lý do — vd "material default: loại vì generic".}}

## 7. Vấn đề xuyên suốt (Cross-cutting)
- **A11y:** tương phản ≥ WCAG AA; focus ring rõ; `role`/`aria-*` cho toggle & nav.
- **Responsive:** breakpoint chuẩn theo §3.2 mobile override.
- **Hiệu năng:** theo §3.5; đo lại trên mobile thật nếu có blur/noise.
- **Nguồn design system:** `/high-end-visual-design` — cập nhật skill thì re-distill §3.
