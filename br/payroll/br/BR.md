# BR — Hệ thống Payroll & Timesheet tự động (Unicons/Coteccons)

> Biên dịch từ `llmwiki/raw/PRD__Payroll_System_v2.1.docx` (PRD 2.1, phê duyệt 08/07/2026).
> Mỗi điều khoản có `clause_id` kế thừa số mục PRD. Provenance: `raw` = PRD ghi rõ ·
> `lens` = tự bù gap (verified: false, chờ HR xác nhận).

## ⚠️ GIẢ ĐỊNH ĐANG GÁNH (tự bù gap — tất cả `verified: false`)

| # | Clause | Giả định | Rủi ro nếu sai |
|---|--------|----------|----------------|
| G1 | C5.3.3 | Mức xăng 02 tài xế HN = 2.600.000 đ (PRD không ghi số, chỉ nói "duyệt riêng") | Sai tiền 2 người — thấp |
| G2 | C5.3.6 | Chingluh nội suy CHP 1.5tr, GS 1tr (PRD chỉ ghi 2 đầu mút CHT 2tr → BV 500k) | Sai tiền theo chức danh — trung bình |
| G3 | C5.3.4 | Dải 400–1000 km dùng cùng mức "trên 100 km" (PRD bảng gộp) | Thiếu bậc định mức — trung bình |
| G4 | C6.1 | Lịch chốt Mắt Bão = ngày 15 hằng tháng; grid định mức Mắt Bão tự dựng 3 dòng mẫu | Sai lịch/mức outsource — cao |
| G5 | C5.5 | Danh sách trường hợp lễ 300% = rỗng (PRD nói "theo danh sách" nhưng không kèm) | Trả thiếu OT lễ — cao |
| G6 | C5.1.4 | Thứ tự tỷ lệ trích Cty "17%/0.5%/3%/1%" = BHXH/BHYT/BHTN/TNLĐ | Hạch toán sai đầu mục — thấp (tổng đúng) |
| G7 | C6.2 | Tần suất nhắc Teams mặc định 2 lần/ngày (09:00, 15:00) | Chỉ là default — không rủi ro tiền |
| G8 | C-DATA | Thang lương cơ bản của 12 NV mẫu là số bịa để demo (PRD không kèm thang lương) | Chỉ ảnh hưởng demo |
| G9 | C5.3.1 | "Điều kiện an ninh theo quy định" của mức 2 bữa <30km: bỏ qua ở v0, coi mọi CT <30km đạt | Thừa suất ăn ở CT không đạt an ninh |
| G10 | C5.5 | OT ngày truyền thống tách thuế = non-tax toàn phần | Sai cột thuế — trung bình |
| G11 | C7.1 | Import chỉ ghi đè `nhan_vien.csv`, chưa hỗ trợ `bang_cong_tho.csv`/các CSV khác qua UI | Vẫn phải sửa tay các file còn lại — không rủi ro sai số |

## C4 — Tích hợp & chốt dữ liệu

- **C4.1** (raw) Kỳ công = 21 tháng trước → 20 tháng này. Kỳ BHXH = 01 → cuối tháng. Theo dõi SONG SONG 2 trục. Công chuẩn VP trừ CN + chiều T7; công chuẩn CT chỉ trừ CN; lưu riêng từng kỳ.
- **C4.2** (raw) Nguồn tích hợp duy nhất: API Workday (công thô theo ngày + hồ sơ + ngày kết thúc thử việc + EmployeeType + loại giờ OT). SAP cho cost allocation. Workday KHÔNG tổng hợp — Payroll tự tổng hợp toàn bộ. Ký hiệu công tối thiểu: x, x1, OL, P/F, R/Fo, L, NB, Ts/TS, TSN, ON/OD, TN, Ro, TC100/200/300, ?P.
- **C4.3** (raw) Khóa kỳ manual bởi HR: ngừng sync tháng đó; đơn muộn/sửa công sau chốt KHÔNG cập nhật/truy thu tháng sau. Trước khóa: định mức đổi hồi tố → tự tính truy thu/truy lĩnh = (mới − cũ) × ngày công tương ứng, cột riêng (3), kèm lý do.

## C5 — Tổng hợp công & tính phụ cấp

- **C5.1.1** (raw) Đếm tách ngày thử việc / sau thử việc theo "Ngày kết thúc thử việc". Lương TV = ngày TV × 85%; chính thức × 100%.
- **C5.1.2** (raw) Bổ nhiệm/điều chỉnh giữa kỳ → tách 2 giai đoạn theo ngày hiệu lực. PC trách nhiệm = ngày hưởng × (định mức / công chuẩn).
- **C5.1.3** (raw) Điều động giữa kỳ → đếm ngày công TỪNG bộ phận, tách theo loại ngày, kèm ngày điều động. PC gắn địa điểm tính + bổ chi phí theo từng bộ phận.
- **C5.1.4** (raw) Quy đổi kỳ công ↔ tháng dương lịch để xác định diện đóng BHXH. Ngày không tính đóng (TV, Ro, Ts, ốm BHXH…) đếm riêng. Trích NV 8/1.5/1; Cty 17/0.5/3/1 + 2% KPCĐ; cột Đ/C khi truy đóng/hoàn.
- **C5.1.5** (raw) Suất ăn theo bộ phận: cơm thường + TC đêm + CN/lễ (thư ký chấm bổ sung) + cơm bổ sung tháng trước. Ngày ≤4h: 0 suất.
- **C5.2** (raw) Pro-rata: (định mức / công chuẩn) × ngày hưởng. Quy tắc <14 ngày LV thực tế: ngày hưởng = LV thực tế + lễ (không phép/nghỉ hưởng lương khác/không lương); điều động chia theo bộ phận với định mức từng nơi. Tờ trình ghi đè định mức chung từ ngày hiệu lực. Mỗi PC tách Taxable/Non-tax.
- **C5.3.1** (raw) Cơm: VP 1 bữa · CT <30km 2 bữa (kèm điều kiện an ninh) · CT ≥30km 3 bữa · ≤4h 0 bữa. Đơn giá 45.000 đ cấu hình được. Miễn thuế ≤730.000 đ/tháng.
- **C5.3.2** (raw) Điện thoại theo ngạch × VP/CT (bảng 14 dòng — xem `data-draft/dinh_muc_dien_thoai.csv`). Pro-rata + <14 ngày + chia bộ phận.
- **C5.3.3** (raw+lens G1) Xăng: CT chuẩn 1.000.000 cho L2–L6. VP KHÔNG định mức chung — theo tờ trình (DVKH… 800k; GĐDA 10tr; TGĐ ô tô 25–35tr). 02 tài xế HN đích danh MSNV.
- **C5.3.4** (raw+lens G3) Đi lại: (nơi tuyển dụng × tỉnh bộ phận) → DM Khoảng cách → dải → định mức theo dải × 4 nhóm đối tượng (CHT/CHT ME · ĐH+ · CĐ/TC/Nghề · NV.02). 3 danh mục nền phải quản trị được.
- **C5.3.5** (raw) CT + công tác xa: bảng Khối (CT/VP) × dải khoảng cách × 2 đối tượng (ĐH+ / CĐ-TC-Nghề).
- **C5.3.6** (raw+lens G2) CT xa/khó khăn theo dự án đặc thù × chức danh (Quan Lạn, Chingluh, Làng Tây – Hòn Thơm 2tr theo TT).
- **C5.3.7** (raw) PC khác duyệt riêng: danh sách "Theo dõi duyệt riêng" (MSNV, bộ phận, chức danh, PC (2)–(7), ghi chú, tổng) thay định mức chung. GĐDA không hưởng PC công trường/đi lại chung.
- **C5.4** (raw) 2 ví dụ CHỐT làm acceptance: VD1 suất ăn điều động 5×1+20×3=65; VD2 <14 ngày: PC = (3+1)/chuẩn×ĐM_A + (3+2)/chuẩn×ĐM_B.
- **C5.5** (raw+lens G5,G10) OT: multiplier tách Chính thức/Mắt Bão. CN 200%; lễ luật +100% & +2 nghỉ bù/ngày (một số 300% theo danh sách); truyền thống/bổ sung +1 nghỉ bù. Tách OT thuế/không. Đăng ký đi làm lễ: NLĐ/thư ký import → trưởng BP duyệt → HR; danh mục lễ tự động hằng năm.

## C6 — Mắt Bão, phê duyệt & báo cáo

- **C6.1** (raw+lens G4) Mắt Bão: nhận diện EmployeeType từ API; lịch chốt sớm hơn; grid định mức thiết lập trên Payroll.
- **C6.2** (raw+lens G7) ?P không cộng công. Teams Bot nhắc theo cấu hình HR. HR Override duyệt thay; sync-back Workday = "Đã duyệt". Audit log bắt buộc: cũ → mới, người, thời gian, lý do.
- **C6.3** (raw) Template 0 trình ký: chung định dạng CT/Mắt Bão; điều động gộp về dự án nơi làm ngày 20. Template 2 Payroll Master: file phẳng đầy đủ (nhân sự-HĐ, các loại ngày công, lương TV/CT/PC trách nhiệm/phép tồn, PC tax/non-tax, OT, thưởng, BHXH 2 phía, giảm trừ, TNCN, sau thuế, thực nhận, chi phí Cty, Profit/Cost Center, WBS, Funds Center).
- **C6.4** (raw) Bộ báo cáo bảng công chi tiết theo file HR C&B (BẢO MẬT — chỉ HR C&B, log mọi lượt xuất): ma trận công 21–20; bảng cơm P1/P2/TC đêm/CN; bảng tổng hợp PC cột (1)–(8) + PC bộ phận trước (2) + truy thu (3); danh sách duyệt riêng & truy lĩnh có so sánh kỳ.
- **C6.5** (raw) Đơn treo: tổng hợp gửi Email/Teams cho lãnh đạo tại cut-off; dashboard realtime; HR xuất tay được.

## C3/C7/C8 — Nền tảng

- **C3** (raw) Azure AD SSO. Phân quyền granular (xem/sửa/xuất/khóa kỳ/duyệt thay). Thư ký/CHT chỉ thấy NGÀY CÔNG không thấy TIỀN. Báo cáo 6.4 giới hạn HR C&B + log xuất.
- **C7** (raw) Master data: DM Bộ phận (→tỉnh/khối/vùng, ngày hiệu lực), DM Nơi cư trú, DM Khoảng cách, bảng định mức các loại, danh sách Tờ trình, danh mục lễ (tự động hằng năm), quy định ngày nghỉ (phép 12+thâm niên, ≥50% công chuẩn, tồn đến 31/12 năm sau, ốm Cty 3 ngày…).
- **C7.1** (user, gap-mới) Import Excel/CSV qua UI: trang "Master data" có form upload thay thế 1 file dữ liệu công ty (`nhan_vien.csv`) — validate header đúng schema TRƯỚC khi ghi đè, từ chối nếu thiếu/thừa cột hoặc file rỗng; ghi đè xong redirect về Master data với thông báo số dòng đã nhập. PRD gốc KHÔNG đặc tả màn hình này (chỉ nói "dữ liệu đầu vào" ở mức luồng, không mức UI) — user yêu cầu bổ sung 2026-07-09 sau khi phát hiện UI không có chỗ nhập dữ liệu ngoài sửa CSV bằng tay.
- **C8** (raw) Phi chức năng: hàng ngàn NV xử lý <5 phút; tin Workday tuyệt đối trừ HR Override; MỌI con số truy vết được về công thức + ngày + định mức + nguồn; bảo mật báo cáo + log xem/xuất; tương thích Microsoft 365.

## Origin
Biên dịch 2026-07-09 từ `llmwiki/raw/PRD__Payroll_System_v2.1.docx` (user cung cấp 09/07). Gap tự bù theo yêu cầu user "tự bổ sung gap" — tất cả đánh dấu bảng Giả định, chờ HR xác nhận trước khi run.
