---
name: timeline
description: Component timeline dọc (mốc theo ngày, cuộn-hiện dần bằng IntersectionObserver, tự chuyển layout mobile→desktop ở 768px) cho trang changelog/lịch sử/roadmap/writing-archive. Gọi khi user nói "làm timeline", "dòng thời gian", "lịch sử phiên bản dạng timeline", "changelog timeline", "roadmap timeline", hoặc /timeline. KHÁC /diagram (sơ đồ luồng/kiến trúc) — đây là danh sách MỐC THEO THỜI GIAN của MỘT trục, không phải quan hệ nhiều node.
---

# Skill: timeline

Component HTML/CSS/JS thuần (không framework) — danh sách mốc dọc, mỗi mốc có ngày + tiêu đề + nguồn, cuộn tới đâu hiện tới đó.

## When to use
- Trang cần liệt kê MỐC THEO THỜI GIAN: changelog, lịch sử dự án, roadmap, writing archive, timeline sự kiện.
- User nói "làm timeline", "dòng thời gian", "lịch sử dạng timeline".
- KHÔNG dùng cho sơ đồ quan hệ/luồng (đó là `/diagram`) hay biểu đồ dữ liệu số (đó là `dataviz`) — đây chỉ là MỘT trục thời gian tuyến tính.

## Assets
`assets/timeline.html` + `assets/timeline.css` + `assets/timeline.js` — đọc rồi ADAPT vào trang đích (đổi class/token theo hệ design của dự án nếu đã có `design.md`), không copy máy móc y nguyên.

## Cơ chế
- Mỗi mốc là `<li class="timeline__item">` chứa `<time>` (ngày, `datetime` attr chuẩn ISO) + `<a>` tiêu đề + `<small>` nguồn.
- `IntersectionObserver` gắn class `timeline__item--in` khi mốc cuộn vào khung nhìn → CSS transition làm nó "hiện dần" (opacity + translateX), KHÔNG animate bằng JS trực tiếp.
- Responsive: mobile — chấm mốc + đường nối bên trái, ngày nằm trong dòng. `≥768px` — ngày tách ra cột riêng bên trái (`position: absolute`).
- Dark theme qua `@media (prefers-color-scheme: dark)` — đổi 3 biến `--bg/--fg/--primary`; nếu dự án đã có `dark-mode-maker` (toggle chủ động, không chỉ theo OS) thì thay khối này bằng biến token của `dark-mode-maker`, đừng để hai cơ chế dark-mode chỏi nhau.

## Rules
- **`assets/timeline.js` dòng 1 import `faker` từ `esm.sh` chỉ để SINH DỮ LIỆU GIẢ cho demo** (`generateArticles()`) — khi wire vào dự án thật, XOÁ import đó + `generateArticles()`, thay `this.articles` bằng dữ liệu THẬT (API/markdown/CMS) trước khi build(). Để nguyên import faker trong production là phụ thuộc thừa + lộ dữ liệu giả.
- Class đặt tên theo BEM (`timeline__item-time`...) — đổi tên class thì đổi cả CSS lẫn JS `querySelector`, đừng đổi một bên.
- Ngưỡng `threshold: 1` của `IntersectionObserver` nghĩa là mốc phải vào khung nhìn TOÀN BỘ mới hiện — mốc cao hơn viewport (nội dung dài) sẽ không bao giờ đạt threshold 1, hạ xuống `0.5` nếu mốc có nội dung dài.
- Verify bằng `playwright-verify` (chụp + cuộn thử) sau khi wire dữ liệu thật, không tự khen "chạy được" chỉ vì không lỗi console.

## Origin
- Nén từ `llmwiki/patterns/timeline/` (snippet tham khảo chưa gắn skill nào, chưa từng track git) thành skill thật theo yêu cầu user 2026-09-17 — cùng đợt với `blur`.
