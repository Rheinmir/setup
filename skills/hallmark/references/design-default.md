# Design — overstack default (reading theme, Vietcetera-inspired)

design.md MẪU của framework. Hallmark đọc file này ở Step 0 khi project CHƯA có
`design.md` riêng: mọi trục brief KHÔNG nhắc tới (màu, chữ, nhịp, bố cục, trạng
thái, kanban…) lấy giá trị ở đây. Thứ tự ưu tiên: lời user trong brief >
`design.md` của project > file này. User nói khác ở trục nào thì chỉ trục đó đổi.

Nguồn DNA: `vietcetera-inspired-reading-theme.html` (user giao 21/09/2026), đã
chuẩn hoá theo luật framework: khoảng cách bẻ về thang 4/8, bỏ sọc viền trái
của blockquote (slop `rounded-edge`/`stripe`), thêm chế độ tối.

Code chạy được cho từng mục dưới đây: [`design-showcase.html`](design-showcase.html) — mỗi khối có id, bản chạy thật và code; lấy code: `build-design-showcase.py --get <id>`.

## System
- Genre · editorial / reading
- Macrostructure · Long Document (topbar + mục lục trái sticky + cột đọc 720px)
- Theme · custom (vibe: "báo giấy ấm, chữ đen đặc, một điểm đỏ")
- Axes · paper ấm / display sans 800 chặt chữ / accent đỏ

## Tokens
```css
:root {
  --color-paper:   #f5f5f0;  --color-paper-2: rgba(255,255,255,.72);
  --color-ink:     #11110f;  --color-ink-2:   #6b6b63;
  --color-rule:    #d9d9d1;
  --color-accent:  #e23b2d;  /* mảng màu, chấm, progress; chữ nhấn dùng #b8281c (≥ 4.5:1) */
  --color-mark:    #f3d548;  /* nền ghi chú, avatar — không làm chữ */
  --font-text: "Be Vietnam Pro", Arial, sans-serif;      /* nội dung — nhúng qua html_font.py --apply */
  --font-display: "Newsreader", Georgia, serif;          /* tiêu đề (user chốt 22/09/2026) */
  --fw-text: 400; --fw-strong: 600; --fw-heading: 600;
  --ls-heading: -.035em;     /* h1 hero -.055em */
  --lh-body: 1.75; --lh-heading: 1.25; --measure: 35em;
  --sp: 4 8 12 16 20 24 32 40 48 64 80 96;   /* px, chỉ dùng các bậc này */
  --radius-card: 12px; --radius-pill: 999px; --radius-media: 4px;
  --ease-out: cubic-bezier(.16,1,.3,1); --dur-fast: 180ms; --dur-base: 240ms;
}
html[data-theme=dark] {
  --color-paper: #12120f; --color-paper-2: rgba(30,30,26,.72);
  --color-ink: #ecebe4;   --color-ink-2: #a9a89e; --color-rule: #34332d;
  --color-accent: #ff6a5c; --color-mark: #5a4c12;
}
```

## Type scale
- Body 16px / **1.75** (đo từ trang đọc thật 23/09/2026), đoạn tối đa `--measure` = 35em; lead/intro 18px.
- Tiêu đề: Newsreader 600, đứng thẳng, một màu đặc. h1 hero clamp(40px, 6.4vw, 78px) · h1 trang 40/1,25 · h2 28/1,42 · h3 22/1,55 · h4 18/1,5. Luôn to → nhỏ (`heading-scale`).
- Tên trang/logo ≥ 1,2 × mục nav/tab (logo 18–22px 800, nav 13px 600) — `title-scale`.
- Kicker/eyebrow: 11px 600 HOA giãn .12em, màu accent. Là chỗ DUY NHẤT được viết hoa toàn bộ.
- Tiêu đề, nhãn, nút, tab, mục nav: viết hoa chữ đầu (`sentence-case`).

## Layout
- Topbar 72px sticky, kính mờ nhẹ, một đường kẻ dưới. Progress đọc 4px accent.
- Nội dung `min(1180px, 100% - 40px)`; lưới đọc `192px | ≤720px`, gap 64px; ≤ 850px còn một cột, ẩn mục lục.
- Tiêu đề: khoảng trên ≈ 1,7 × khoảng dưới — h2 40/24, h3 32/16, h4 24/12; đoạn cách nhau 24px.

## Defaults khi user không nói (luật, không phải gợi ý)
- **Minimal, bấm mới hiện.** Màn đầu chỉ tóm tắt; chi tiết nằm sau `<details>`, popup, nút "Đầy đủ". Không đặt ngang hàng hàng chục chip/nút (`eye-rest`: mực màn đầu ≤ 55%, không dải dày liền > 520px).
- **Toggle sáng/tối** luôn có, nhớ localStorage, chống nháy khi tải.
- **Thẻ**: một style cho cả trang (nền paper-2, viền 1px rule, bo 12px, padding 16px). Không sọc màu một cạnh; phân loại bằng chấm màu hoặc nền nhạt cả thẻ.
- **Kanban**: mọi thẻ trên bảng cùng MỘT style và cùng kích thước cố định (rộng theo cột lưới đều nhau, cao cố định; tiêu đề `line-clamp:2`, dòng phụ `ellipsis`); bấm thẻ mở chi tiết, không nới thẻ ra — luật `kanban-uniform`.
- **Vùng bấm** ≥ 24×24px; chữ đạt contrast 4.5:1 ở cả hai chế độ.
- Sơ đồ/biểu đồ → skill `diagram`, chữ trong sơ đồ cùng font trang.

## CTA voice
- Primary · nền ink, chữ paper, bo pill, padding 12/20.
- Secondary · viền 1px rule, nền trong, cùng bo.

## Motion stance
- Im lặng: chỉ progress đọc, hover đổi màu, reveal khi bấm (ease-out ≤ 240ms, không ease-in).
- `prefers-reduced-motion`: chỉ crossfade opacity ≤ 150ms.

## Notes — không mang sang
- `blockquote{border-left:6px solid red}` của bản gốc → dùng trích dẫn nền paper-2 + chữ lớn, không sọc cạnh.
- Khoảng cách lẻ (25px, 70px, 58px) của bản gốc → bẻ về thang 24/64/64.

## Provenance
- Source · file HTML user giao `~/Downloads/vietcetera-inspired-reading-theme.html` · 21/09/2026 · lấy cảm hứng, không copy pixel.
