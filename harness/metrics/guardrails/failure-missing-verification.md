# Chỉ dẫn đã học — missing-verification (9×)

Lớp `missing-verification` lặp 9 lần (ngưỡng 3). Thẻ này do máy gói từ chính các lần đã ghi; đọc TRƯỚC khi làm việc cùng loại.

## Lần gần nhất
- **Triệu chứng:** vạch tiến độ absolute trong sidebar cuộn đè ngang mục nav — 57 trang docs-shell dính, không cổng nào bắt
- **Đã sửa bằng:** user chỉ bằng ảnh; sửa: fixed mép trên cửa sổ + THÊM luật line-over-text vào html-visual-gate (có fixture xấu/tốt)

## Các lần đã gặp (9)

| Khi | Triệu chứng | Cách sửa đã dùng |
|---|---|---|
| 2026-07-18 09:30 | design-variety.py: engine viết xong, concept hứa, KHÔNG gì gọi (ca thứ 4 của lớp) — capproof bêu UNPROVEN, giải phẫu 180726 phát hiện và wire vào hall | fix: hallmark SKILL.md d8 + --self-test; nợ 75→74 |
| 2026-07-20 17:04 | fnmatch glob dùng cho travel_policy_sync.py cho segment '*' vượt qua '/' — assert sai bị chính --demo self-check bắt, không phải do kiểm trước khi viế | Viết travels() dùng fnmatch.fnmatch(path, pattern) tưởng '*' không vượt '/', thực tế fnmatch coi '*' khớp mọi ký tự kể cả '/'. Không viết test trước — |
| 2026-07-20 17:04 | install-harness.sh đọc travel-policy.yaml lúc runtime từ $SRC (có thể là clone remote cũ) thay vì đóng băng cùng script — làm fresh-install-smoke từ P | Sau khi sửa installer để gỡ tầng framework_only khỏi global, không chạy fresh-install-smoke NGAY để so baseline trước/sau. User phải paste lỗi medic t |
| 2026-07-20 17:04 | kết luận 'BM25 auto-inject là ngõ cụt' được rút ra từ tập prompt lẫn 22.863 tool-result + 4.412 message subagent + 751 meta, không kiểm nguồn dữ liệu  | Lọc transcript bằng đoán chuỗi (startswith '<', chứa 'system-reminder') thay vì dùng cờ tất định isSidechain/toolUseResult/isMeta có sẵn trong schema. |
| 2026-07-20 17:05 | flywheel.py _ddmmyy() nuốt exception khi --date sai định dạng (đưa DDMMYY thay vì ISO YYYY-MM-DD theo đúng quy ước wiki của chính framework này) rồi â | Gọi --draft missing-verification --date 260720, ra file 290626-failure-missing-verification.md thay vì 200726-. except Exception: return fallback ở dò |
| 2026-07-21 11:09 | Agent Task Assignment trong propose gán mặc định Claude cho task cơ học (git push, chép khuôn có validator, chạy-diff theo verify đã viết sẵn) — lý do | Root cause 5-Why: không có gate tất định giữa 'khẳng định nghe hợp lý' và 'khẳng định được coi là xong' — cùng cấu trúc với 3 instance khác trong phiê |
| 2026-09-23 08:41 | cổng xanh nhưng user nhìn ảnh thấy lỗi: chữ 'Bấm vào khung' vô hình ở chế độ tối do mix-blend-mode+invert né được phép đo contrast | 22/09 design-showcase khối motion-circle; sửa: bỏ mẹo blend, đặt chữ trong viên nền đặc. Cổng chưa có luật cho ca này. |
| 2026-09-23 08:41 | vạch tiến độ absolute trong sidebar cuộn đè ngang mục nav — 57 trang docs-shell dính, không cổng nào bắt | user chỉ bằng ảnh; sửa: fixed mép trên cửa sổ + THÊM luật line-over-text vào html-visual-gate (có fixture xấu/tốt) |

## Trạng thái
- `đã học, CHƯA duyệt` — đây là chỉ dẫn đọc-để-nhớ, KHÔNG phải luật cắn được.
- Thành luật/skill chính thức: `flywheel.py --kind failure --draft missing-verification` rồi `/propose`.
