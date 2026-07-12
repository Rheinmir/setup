---
name: visual-qa
description: >-
  Luồng QA thị giác tự động cho SPA local (app do dây chuyền /br sinh ra, hoặc bất kỳ
  web app chạy localhost): login rồi chụp HEADLESS từng route tồn tại bằng playwright-core
  + Chrome hệ thống (không tải browser riêng), lưu ảnh, rồi agent ĐỌC ảnh sinh FINDINGS.md
  (fix-plan có route · mức · cách sửa) để tự bật vòng chỉnh sửa. Dùng khi extension chụp
  không được (localhost), hoặc cần kiểm giao diện theo mắt sau khi đổi theme/UI. Trigger:
  "qa thị giác", "screenshot từng route", "chụp app kiểm giao diện", "visual qa",
  "route-shots", "test giao diện headless", "tự chụp app lên plan sửa", "/visual-qa".
---

# Skill: visual-qa — luồng QA thị giác headless (screenshot → findings → fix loop)

> Vòng phản hồi thị giác (Meadows): thay vì "đoán UI đẹp/xấu" (mù), dựng đường tín hiệu
> quay về = chụp thật từng route → agent nhìn → FINDINGS.md → sửa → chụp lại so trước/sau.
> Sinh ra vì Chrome-extension MCP lỗi "error page" trên localhost; headless CLI thì chạy.

## When to use
- Vừa đổi theme/UI/rebrand một web app local và cần kiểm bằng MẮT trên nhiều route.
- Extension browser không chụp được localhost (thường gặp).
- Cần một fix-plan có cấu trúc (FINDINGS.md) để tự bật vòng sửa, không sửa mù.

## Steps
1. **App phải đang chạy** (vd memos `:5230`). Biết route list + tài khoản login (nếu app private).
2. **Chụp:** chạy driver headless (playwright-core + Chrome hệ thống — KHÔNG tải browser):
   ```bash
   # node_modules playwright-core phải resolve được từ chỗ chạy script
   node skills/visual-qa/assets/route-shots.mjs \
     --base http://localhost:5230 --out <dir>/qa-shots \
     --user demo --pass demo
   ```
   Driver: goto /auth → điền `input[type=text]`/`input[type=password]` → click "Sign in" →
   chờ rời /auth → chụp từng route với `waitUntil:"domcontentloaded"` + chờ cố định (SPA giữ
   kết nối realtime nên `networkidle` KHÔNG bao giờ đạt — đừng dùng).
3. **Đọc ảnh:** agent `Read` từng PNG trong `qa-shots/` — chấm neumorphism/brand/contrast/
   empty-state/CTA/spacing. So với ý đồ thiết kế (vd design-template §3.6 neumorphism).
4. **Sinh FINDINGS.md:** bảng `# · route · vấn đề · mức (CAO/TB/THẤP) · cách sửa` + mục
   "đã đạt (giữ)" + "vòng sửa kế". Đây là file tự-bật-luồng-sửa.
5. **Sửa → chụp lại → so** trước/sau. Lặp tới khi FINDINGS sạch mức CAO.

## Rules
- **Route list là INPUT, không đoán** — lấy từ `routes.ts`/router thật của app; route private phải login trước, không thì chụp ra trang /auth vô nghĩa.
- **`networkidle` cấm với SPA realtime** — dùng `domcontentloaded` + `waitForTimeout`.
- **playwright-core, KHÔNG playwright full** — dùng Chrome hệ thống qua `channel:"chrome"`, không tải chromium 130MB.
- **Không dẫm computer-use** (đó là desktop AX/Orca browser) — skill này là headless CLI cho SPA localhost, output là PNG + FINDINGS.md để agent tự chấm.
- **BẰNG CHỨNG > LỜI (feedback 2026-07-13, "chỉ tin file không tin think")** — pass/đẹp/fixed chỉ hợp lệ khi có FILE ẢNH thật. Driver LUÔN đẻ `MANIFEST.json` (route→file→bytes); `--assert` FAIL nếu route lỗi HOẶC không có ảnh (bytes=0). Không có file = CHƯA TỪNG CHỤP = fail, bất kể model nói gì. Sau khi sửa PHẢI chụp LẠI + đọc lại ảnh trước khi cho green.
- **FINDINGS.md phải actionable** — mỗi finding trỏ đúng file/scope để sửa, có mức ưu tiên; không mô tả chung chung.
- Ảnh + FINDINGS.md để trong thư mục dự án (vd `br/<app>/qa-shots/`), không lẫn vào repo gốc nếu là app ngoài.
