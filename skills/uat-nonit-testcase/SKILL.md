---
name: uat-nonit-testcase
description: >-
  Tạo bộ test case / checklist UAT cho người dùng nghiệp vụ NON-IT (C&B, kế toán, vận hành) — 1
  file HTML offline-proof gồm bảng kịch bản tuần tự có mã Ctrl+F, phạm vi check/không-check theo
  nguồn dữ liệu, step-by-step kèm ảnh màn hình thật đã blur PII, Đạt/Không đạt + xuất
  Excel/CSV/PDF. Trigger: "tạo test case cho non-IT", "checklist UAT cho nghiệp vụ", "kịch bản
  kiểm thử cho C&B", "/uat-nonit-testcase".
---

# UAT Test-case Builder cho người dùng NON-IT

Sinh **1 file HTML tự chứa** (không CDN, không build, mở `file://` vẫn chạy) làm tài liệu UAT
cho business user. Đúc kết từ dự án Payroll Coteccons — các quy tắc dưới đây là bài học đã trả giá,
KHÔNG bỏ bước.

## Nguyên tắc cốt lõi (học từ phản hồi người dùng thật)

1. **Ngôn ngữ phi kỹ thuật, giọng formal doanh nghiệp.** Không emoji, không codename, không file path,
   không tên API. "Danh mục kiểm thử", "Đạt / Không đạt" (không Pass/Fail trên UI), "hệ thống tự tính"
   (không "engine"). Nguồn dữ liệu **chỉ gọi tên**: `từ HRIS` / `import Excel` / `người dùng nhập` /
   `hệ thống tự tính` — không giải thích cơ chế.
2. **Phạm vi check / không-check tách bạch ngay đầu trang.** 2 card ✓/✗: cái app tự tính + người dùng
   nhập thì CHECK; dữ liệu hệ thống nguồn (HRIS/ERP) mang sang thì KHÔNG — "nếu y như nguồn thì xuất
   nguồn ra dùng, kiểm lại làm gì". Sai lệch dữ liệu nguồn ghi nhận riêng, không tính bug.
3. **Số kỳ vọng phải TÍNH SẴN từ code/config thật.** Đọc backend/config lấy công thức + hằng số thật
   (vd trần BHXH 46,8tr → lương 50tr ra đúng 3.744.000). Một con số cụ thể đáng giá hơn mười dòng mô tả.
   Đối chiếu chéo với màn hình cấu hình thật trước khi ghi.
4. **Bảng kịch bản tuần tự là deliverable chính** — business user muốn "list dạng bảng", không muốn
   trang web đẹp. Cột chuẩn: `Mã (Ctrl+F) | Kịch bản | Màn hình | Bước thực hiện | Kết quả mong đợi |
   KQ | Ghi chú`. Thứ tự kịch bản = thứ tự làm thật: setup → dữ liệu vào → tính → từng nghiệp vụ → tổng → khóa sổ.
5. **Mã kịch bản Ctrl+F được**: `NHÓM-NN` monospace (`LUONG-01`, `TRICH-02`, `CHOT-01`). Dùng làm ngôn
   ngữ chung khi báo bug ("TRICH-02 fail + ảnh chụp").
6. **Mặc định chỉ 5–6 kịch bản trọng yếu** phủ đủ các nhóm nghiệp vụ, nút "Hiển thị đầy đủ N kịch bản"
   để mở rộng. Khi mở rộng, case trọng yếu phân biệt bằng **màu nền nhạt + thanh trái accent** —
   KHÔNG dùng ⭐/badge/emoji (môi trường doanh nghiệp legacy).
7. **Disclaimer ghi đè (highlight amber, đặt trên bảng):** công thức phức tạp ngoài chuẩn → tính ngoài
   Excel rồi **ghi đè trực tiếp giá trị vào ô tương ứng** (nhấp đúp → nhập → lưu kèm lý do); hệ thống lưu
   vết trước/sau + hoàn tác — tham chiếu kịch bản OVR.
8. **Ảnh màn hình THẬT, không mockup, không iframe.**
   - Mockup số giả → user hỏi "không giống thật thì lấy ra làm gì". Bỏ.
   - Iframe app thật → chết vì SSO (Microsoft chặn login trong frame) + cookie partitioning. Bỏ.
   - Chốt: **ảnh chụp thật** (Playwright + dev-token bypass), panel ảnh sticky bên phải, nút tại mỗi
     mục đổi ảnh sang đúng màn hình; nút "Mở ứng dụng (cửa sổ mới)" cho thao tác thật.
9. **Layout chuẩn:** hero ngắn → 2 card phạm vi → disclaimer → bảng kịch bản (+nút Sao chép Excel /
   Tải CSV / Xuất PDF) → split 2 cột: trái panel step-by-step theo nhóm nghiệp vụ (bước đánh số,
   ô "Giá trị kỳ vọng", checkbox), phải ảnh sticky.

## Kỹ thuật bắt buộc (đã vấp đủ)

- **Offline-proof tuyệt đối**: CSS thuần trong file, KHÔNG Tailwind CDN (mạng chặn = trang trắng).
  Google Fonts cho phép nhưng phải có fallback stack.
- **`<head>` đủ:** `<meta charset="utf-8">` + `<meta name="viewport" content="width=device-width, initial-scale=1">`
  + `<title>` thật. Thiếu viewport → bảng tràn ngang trên laptop nhỏ/máy tính bảng của nghiệp vụ.
- **Cột số căn theo `tabular-nums`** (`td.num, .exp-val{font-variant-numeric:tabular-nums}`) — số kỳ vọng
  (lương, trần BHXH…) phải thẳng cột để soi nhanh; font tỉ lệ làm số nhảy cột, sai lệch khó thấy.
- **Focus ring bàn phím:** mọi nút (Sao chép Excel / Tải CSV / Xuất PDF / "Hiển thị đầy đủ") + ô chọn
  Đạt/Không đạt cần `:focus-visible{outline:2px solid var(--accent);outline-offset:2px}` — nghiệp vụ
  hay thao tác bằng Tab/Enter, mất ring là lạc chỗ. (Bỏ ring chuột bằng `:focus:not(:focus-visible){outline:none}`.)
- **`localStorage` bọc try/catch** — `file://` có thể chặn storage, để hở là chết toàn bộ script:
  ```js
  const store={get(k){try{return localStorage.getItem(k)}catch(_){return null}},
               set(k,v){try{localStorage.setItem(k,v)}catch(_){}}};
  ```
- **Trạng thái Đạt/Không đạt + ghi chú** lưu store, dòng đổi màu (Đạt = accent nhạt, Không đạt = amber),
  badge đếm `Đạt x · Không đạt y / N`.
- **Xuất 3 kiểu**: Copy TSV (dán thẳng Excel, fallback execCommand), CSV có BOM `﻿` (Excel VN đọc
  đúng UTF-8), PDF = tự expand đủ bộ → `window.print()` + `@media print` (ẩn nút/ảnh/split, **ép nền
  trắng chữ đen** — nền dark in giấy là hỏng).
- **Blur PII trước khi đưa ảnh ra khỏi mạng nội bộ** (PIL GaussianBlur ≥18 trên ảnh gốc 2400px):
  cột mã NV + họ tên (cả chip code trong cột tên), cột người nhập/duyệt/sửa, chip tài khoản góc sidebar.
  Sau blur PHẢI crop-soi lại từng vùng — tail tên tràn cột và dòng đầu trên mép blur là 2 lỗi kinh điển.
  Chỉ deploy ảnh đã blur + đã được trang tham chiếu; ảnh thừa xóa khỏi gói.
- **Agent không tự deploy ra hosting công khai** — classifier chặn đúng. Quy trình: agent blur + đóng gói
  (`/tmp/<deploy-dir>` với index.html), đưa user 1 lệnh `! vercel deploy --prod --yes` tự chạy.
- Chụp màn hình bằng Playwright: set localStorage (accessToken/user/expiry) + cookie authed qua
  `addInitScript`/`addCookies`; API nào 401 với dev-token thì `ctx.route` trả `[]` (KHÔNG `{}` —
  page gọi `.forEach` là vỡ).

## Quy trình 6 bước

1. **Lấy lời business user nguyên văn** → rút ra: nhóm nghiệp vụ họ check, cái họ từ chối check,
   định dạng họ muốn (bảng!).
2. **Quét code/config thật** (Explore agent): màn hình + route, công thức, hằng số, nguồn từng cột dữ liệu.
3. **Chụp màn hình thật** các màn liên quan (Playwright, auth bypass) → blur PII nếu sẽ share ngoài.
4. **Soạn kịch bản tuần tự** theo template bảng, tính sẵn số kỳ vọng, chọn 5–6 case trọng yếu.
5. **Build HTML** theo layout chuẩn + kỹ thuật bắt buộc ở trên. Brand theo brand-kit dự án nếu có
   (tokens: bg/accent/amber-cảnh-báo qua CSS vars — đổi brand chỉ sửa `:root`).
6. **Test bằng Playwright trước khi giao**: mở `file://` + chặn 100% mạng ngoài → 0 JS error, toggle
   5↔N dòng, select Đạt/Không đạt, print-to-pdf ra file.

## Output

- `llmwiki/html/DDMMYY-uat-checklist-<nhóm>.html` (+ `assets/uat-shots/*.png` đã blur nếu share ngoài)
- Ghi wiki theo loop của dự án (draft + index + log) nếu có llmwiki.

## Output Report

Sau khi xong, ghi draft `llmwiki/wiki/sources/draft/DDMMYY-<ten>.md` (Type: draft, Status: proposed,
Tags: uat-nonit-testcase, output-report) + cập nhật `wiki/index.md` và `wiki/log.md` — theo chuẩn
output-report của các skill khác trong bộ này.
