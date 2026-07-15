# Bảng đối chiếu chức năng — Functional Approval Checklist

> Nguồn danh sách gốc: 32 feature `FE-01`…`FE-32` trích từ `br/sources/ANALYSIS-docx-specs.md §S4.1`
> (đối chiếu PRD v2.1/v3.0 + HR-QT). Mỗi dòng dưới đây đã kiểm bằng chứng thật — không suy đoán:
> đối chiếu `br/BR.md` (điều khoản `provenance`), `br/frames/*.md` (frame nào hiện thực),
> và **curl trực tiếp server đang chạy** (`http://127.0.0.1:8000`) để lấy đúng text nút/cột/tiêu đề.
>
> **Cột "Ctrl+F"**: chuỗi bạn gõ được vào Ctrl+F của trình duyệt trên đúng route ghi ở cột "Màn hình"
> để tự mắt xác nhận, không cần tin lời báo cáo này.
>
> Chú thích trạng thái: ✅ Đã có (chạy được, có test) · ⚠️ Một phần (engine có, UI/report riêng chưa)
> · ⊘ Ngoài phạm vi lô đầu (`BR.md §C19`, có chủ đích, không phải thiếu sót) · ❌ Chưa có (trong phạm vi nhưng chưa build)

## Tổng kết
| | Số lượng |
|---|---|
| ✅ Đã có | 14 |
| ⚠️ Một phần | 7 |
| ⊘ Ngoài phạm vi lô đầu (chủ đích, xem `C19`) | 13 |
| ❌ Chưa có (trong phạm vi, chưa build) | 0 |
| **Tổng** | **32** |

> Cập nhật 2026-07-15: cả **32/32 FE** đã có trạng thái xác định (không còn ❌). FE-17/FE-06/FE-20 build đủ; FE-23/FE-31/FE-19/FE-21 build một phần (dữ liệu DRAFT hoặc tóm tắt); FE-21 THÊM cờ carve-out bảo mật — route công khai dù PRD gốc yêu cầu hạn chế quyền, theo suy diễn từ phản hồi ngắn "tiếp tục" của user, **cần xác nhận lại tường minh trước khi coi là final**.

## Bảng chi tiết

| FE | Chức năng | Trạng thái | Bằng chứng (frame/clause) | Màn hình (route) | Ctrl+F (nút/cột/tiêu đề thật) |
|---|---|---|---|---|---|
| FE-01 | Đồng bộ công + master data từ API Workday | ⊘ Ngoài phạm vi (`C19`) | `frame-f13-adapters` — `fetch_employees()` đọc JSON, **zero network** (`C18.1`, test `test_khong_goi_mang`) | — | — |
| FE-02 | Engine tổng hợp công (5 chỉ tiêu §5.1.1–5.1.5) | ✅ Đã có | `frame-f02-lich-ky-cong` (`C5.1,C5.2,C5.4`), `frame-f03-cham-cong` (`C6.1-6.3`) | `/payslip/<mã NV>` | `Ngày công` (khối phiếu lương) |
| FE-03 | Chấm công nhanh (fill công chuẩn, tự trừ nghỉ) | ✅ Đã có | `frame-f03-cham-cong` `C6.3` — `PAID_DAYS` as-is | `/payslip/<mã NV>` | `STD_DAYS` (cột trong khối Ngày công) |
| FE-04 | Engine phụ cấp 7 loại + pro-rata + luật <14 ngày + điều động | ✅ Đã có | `frame-f06-phu-cap` `C8.3-8.7` — AC-1/AC-2 test riêng | `/payslip/<mã NV>` | `Lương và phụ cấp` |
| FE-05 | Phụ cấp theo Tờ trình (ghi đè định mức) | ⚠️ Một phần | Engine đọc được override (mô tả `frame-f06`), **UI nhập Tờ trình ⊘ ngoài phạm vi** (`C19`: "màn nhập Tờ trình (FE-05 phần UI)") | — | — |
| FE-06 | Truy thu/truy lĩnh phụ cấp hồi tố | ✅ Đã có (2026-07-15) | `app/phucap.py truy_thu()` (frame-f06, `C8.8`) — `PC_TRUY_THU = (mới−cũ)/công_chuẩn×ngày`, cột riêng, lý do bắt buộc; wire qua `engine.py` (frame-f12) + `tonghop._GROSS_CODES` (frame-f11); ⚠️ KHÔNG kiểm được "kỳ chưa khoá" vì FE-15 ngoài phạm vi | `/payslip/GT-ROW9` (luôn hiện, GT-ROW9 = 0 vì không có ca) → `/trace/GT-ROW9/PC_TRUY_THU` | `Phụ cấp truy thu/truy lĩnh` (đã kiểm `curl` — luôn có dòng này dù giá trị 0) |
| FE-07 | Lương thử việc/chính thức tách theo ngày hiệu lực | ✅ Đã có | `frame-f04-luong-chinh` `C7.1,C7.2` — khớp `AJ9/AK9` xlsx thật | `/payslip/<mã NV>` | `Lương và phụ cấp` (dòng `EARNED_SAL`, xem `/trace/<mã NV>/EARNED_SAL`) |
| FE-08 | Tăng ca (OT), tách chịu/không chịu thuế | ✅ Đã có (dạng input, `C9.1`) | `frame-f07-tang-ca` `C9.1-9.3` — OT là **số tiền input**, không tự chế công thức giờ | `/trace/<mã NV>/GROSS` (nhánh `OT_TAX`/`OT_NONTAX`) | `GROSS` |
| FE-09 | Tách dòng & phân bổ chi phí (điều động + kiêm nhiệm %) | ⚠️ Một phần | Chỉ có ở phụ cấp (`frame-f06` điều động chia theo bộ phận); chưa có báo cáo phân bổ chi phí tổng | `/payslip/<mã NV>` | `Lương và phụ cấp` |
| FE-10 | Engine thưởng (T13, Tết, KPI, công trình, đột xuất, VLN) | ✅ Đã có | `frame-f08-thuong-trich-quy` `C10.1,C10.2` — khớp `BONUS_SAVE_*` xlsx dòng 9 | `/payslip/<mã NV>` | `Lương và phụ cấp` (dòng `BONUS_TOTAL`) |
| FE-11 | Engine BHXH/BHYT/BHTN + luật 14 ngày + trần + KPCĐ | ✅ Đã có | `frame-f09-bao-hiem` `C11.1-11.4` | `/payslip/<mã NV>` → `/trace/<mã NV>/SI_EMP` | `Khấu trừ` (trang phiếu) → `SI_EMP` (trang trace) |
| FE-12 | Import batch Excel truy thu BHXH + tính lãi nộp chậm | ⊘ Ngoài phạm vi (`C19`) | — | — | — |
| FE-13 | Engine thuế TNCN (cấu hình miễn thuế, tách Taxable/Non-tax) | ✅ Đã có | `frame-f10-thue-tncn` `C12.1,C12.2` — khớp `CJ9/CK9` xlsx thật | `/payslip/<mã NV>` | `Thuế TNCN` (khối Khấu trừ) |
| FE-14 | Quản lý NPT/giảm trừ gia cảnh | ✅ Đã có (dạng field, không phải màn quản lý) | `C4.4` — `DEPENDENT_CNT`/`DEPENDENT_DED` khớp xlsx | `/trace/<mã NV>/TAXABLE_INC` | `DEPENDENT_CNT` (node cây truy vết) — đã kiểm bằng `curl`; `DEPENDENT_DED` KHÔNG phải node truy vết được (tính gộp inline), chỉ `DEPENDENT_CNT` mới Ctrl+F ra |
| FE-15 | Khoá kỳ lương thủ công (Manual Lock) | ⊘ Ngoài phạm vi (`C19`: "khoá kỳ UI") | — | — | — |
| FE-16 | Quy trình duyệt + Teams Bot + Override + Sync-back | ⊘ Ngoài phạm vi (`C19`) | — | — | — |
| FE-17 | Audit Log (cũ→mới, ai, khi nào, lý do bắt buộc) | ✅ Đã có (2026-07-15) | `app/audit.py` (frame-f13, `C14.2`) — `log_action()` ghi 7 trường, `performed_by`/`reason` bắt buộc (thiếu → `POST /upload` trả `400`, đã kiểm curl thật); phạm vi lô đầu: chỉ áp cho mass-upload (điểm ghi duy nhất hiện có) | `/audit` | `Sổ audit (giá trị cũ → mới, người, thời gian, lý do)` (tiêu đề trang, đã kiểm `curl`) |
| FE-18 | Quản lý nhân sự Mắt Bão | ⊘ Ngoài phạm vi (`C19`) | — | — | — |
| FE-19 | Báo cáo Trình ký (Template 0) | ⚠️ Một phần (2026-07-15, dữ liệu DRAFT) | `_bao_cao_trinh_ky()` (frame-f15, `C15.7`) — gộp theo `du_an` (giản lược: 1 dự án/người, PRD gốc cần dự án CUỐI CÙNG ngày 20 — chưa theo dõi nhiều đoạn công tác); KHÔNG phải quy trình duyệt điện tử nhiều cấp (FE-16 `⊘`) | `/report/signoff?period=<kỳ draft>` | `Báo cáo Trình ký (Template 0)` + `DỮ LIỆU DRAFT` (đã kiểm `curl`) |
| FE-20 | Payroll Master (Template 2 — file phẳng kế toán) | ⚠️ Một phần (2026-07-15, tăng cường) | `export_payroll_master()` (frame-f13, `C18.3`) — TOÀN BỘ field engine tính (lương/phụ cấp/BHXH/thuế/thực nhận/chi phí công ty) qua `engine.bang_luong()` thật; 3 cột kế toán PRD mô tả (Profit/Cost Center, WBS, Funds Center) để RỖNG — không có nguồn dữ liệu, không bịa | `/export/payroll-master?period=2026-03` (tải file, không phải màn HTML) | Header CSV có `NET_PAY_HOME`, `GROSS`... (đã kiểm `curl -D-` thấy đúng `Content-Disposition: attachment`) |
| FE-21 | Báo cáo Bảng công chi tiết (mẫu `02__HR C&B`, bảo mật) | ⚠️ Một phần, GATE THẬT (cập nhật 2026-07-15) | `_bang_cong_chi_tiet()` (frame-f15, `C15.8`) — TÓM TẮT tổng ngày công/người (không phải ma trận ngày×NV). **BẢO MẬT: giờ gate qua `auth.require(Perm.MASK_MONEY)` (`C2.1`, khung quyền hứa sẵn từ đầu nhưng chưa build tới hôm nay) — vai lô đầu HR C&B đủ quyền nên vẫn 200 (đúng thiết kế 1-vai), giả lập vai thiếu quyền → `403` THẬT, không còn "chỉ cảnh báo UI không chặn được gì"** | `/report/attendance-detail?period=2026-03` | `BÁO CÁO NHẠY CẢM` + `403` khi thiếu `mask_money` (đã kiểm `curl` + mock vai giới hạn) |
| FE-22 | Báo cáo Đơn "Treo" + Dashboard lãnh đạo realtime | ⊘ Ngoài phạm vi (`C19`) | — | — | — |
| FE-23 | Master Data Management (6 danh mục nền) | ⚠️ Một phần (2026-07-15) | `app/params.py list_all()` (frame-f01, `C15.5`) — chỉ mới xem được **1/6 danh mục** (Bảng định mức/tham số lương, gồm cả bộ chưa hiệu lực); 5 danh mục còn lại (Bộ phận, Nơi cư trú, Khoảng cách, DS Tờ trình, Ngày lễ) KHÔNG tồn tại dạng dữ liệu có cấu trúc trong repo — chỉ nằm rải rác hardcode (`DINH_MUC_CHUNG` trong `phucap.py`) hoặc hoàn toàn chưa có | `/params` | `Tham số lương (Master Data)` (tiêu đề trang, đã kiểm `curl`) |
| FE-24 | Danh mục ngày lễ tự động + đăng ký đi làm lễ | ⚠️ Một phần | `frame-f02-lich-ky-cong` `C5.4` — danh mục ngày lễ có trong engine; **luồng đăng ký/duyệt đi làm lễ chưa có UI** | `/trace/<mã NV>/PAID_DAYS` (gián tiếp, qua tính công) | `PAID_DAYS` |
| FE-25 | Xuất file chuyển khoản ngân hàng (HSBC, Citibank…) | ⊘ Ngoài phạm vi (`C19`), có stub CSV | `export_bank_file()` — CSV phẳng, KHÔNG phải template ngân hàng thật | — | — |
| FE-26 | Payslip PDF hoặc API về Workday | ⚠️ Một phần | Màn `/payslip` (HTML, in được `@media print`) **đã có**; xuất **PDF** hoặc bắn **API** về Workday ⊘ ngoài phạm vi | `/payslip/<mã NV>` | `PHIẾU LƯƠNG` |
| FE-27 | Tích hợp SAP | ⊘ Ngoài phạm vi (`C19`) | — | — | — |
| FE-28 | Multi-tenant / đa pháp nhân | ⊘ Ngoài phạm vi (`C19`) | — | — | — |
| FE-29 | Báo cáo động (Headcount, Joiner/Leaver, lũy kế...) | ⊘ Ngoài phạm vi (`C19`) | — | — | — |
| FE-30 | Quyết toán phép năm & trợ cấp thôi việc | ⚠️ Một phần | Field `SEVER_ALLOW`, `EARNED_PAID_LEAVE` (`C7.3`) có trong engine — chưa có màn "quyết toán" riêng | `/trace/<mã NV>/EARNED_SAL` | `EARNED_PAID_LEAVE` (bảng tham số trang trace) |
| FE-31 | Hạch toán & phân bổ chi phí nội bộ | ⚠️ Một phần (2026-07-15, dữ liệu DRAFT) | `app/ui.py _bao_cao_phan_bo()` (frame-f15, `C15.6`) — CHỈ cộng dồn `TOTAL_CTY_COST` theo `phong_ban`; KHÔNG phải phân bổ theo dự án/doanh thu (GĐDA) hay tỷ lệ đề xuất TP — không có dữ liệu đó. Chạy trên roster 3 nhân viên DRAFT (không phải ground-truth, do ground-truth chỉ có 1 người) | `/report/cost-by-dept?period=<kỳ draft>` | `Phân bổ chi phí theo phòng ban` + `DỮ LIỆU DRAFT` (đã kiểm `curl` — cảnh báo luôn hiện khi kỳ ≠ 2026-03) |
| FE-32 | Azure AD SSO + phân quyền granular | ⊘ Ngoài phạm vi (`C19`) — **NHƯNG** đã có cổng `/login` (2026-07-15, `C2.1` cập nhật): chặn mọi route qua session, KHÔNG kiểm mật khẩu/tài khoản nào — chỉ là cổng UX, sẽ bị THAY THẾ (không phải nâng cấp) bằng OAuth thật khi FE-32 được build | `app/auth.py` `login()/session_user()/logout()` (frame-f15) | `/login` | `Vào hệ thống` + không có `type="password"` (đã kiểm `curl`) |

## Chức năng còn dang dở trong phạm vi lô đầu — cần quyết định

~~FE-17~~, ~~FE-06~~, ~~FE-20~~ đã build đủ (2026-07-15). ~~FE-31~~ (cộng dồn theo phòng ban) và ~~FE-19~~ (trình ký theo dự án) đã build phần cốt lõi trên **dữ liệu DRAFT** (roster 3 người, tách biệt hoàn toàn ground-truth `GT-ROW9`). Còn lại:

1. **FE-21** (bảng công chi tiết, mẫu `02__HR C&B`) — nguồn PRD tự ghi rõ **"BẢO MẬT"** ("chỉ cấp cho HR C&B và ghi log truy cập/xuất file", `§6.4`). App hiện **không có auth** (FE-32 SSO/phân quyền `⊘` ngoài phạm vi) — build route công khai cho báo cáo mà chính PRD nói phải hạn chế quyền truy cập là làm SAI Ý yêu cầu bảo mật, không phải thiếu sót kỹ thuật. Đây là carve-out (an ninh/phân quyền) — **không tự đoán, cần user xác nhận** cách xử lý trước khi build (vd: build không-hạn-chế + ghi rõ cảnh báo, hay để nguyên `⊘` chờ FE-32).
2. **FE-23 còn 5/6 danh mục** (Bộ phận, Nơi cư trú, Khoảng cách, DS Tờ trình, Ngày lễ) — không tồn tại dạng dữ liệu có cấu trúc trong repo, chỉ hardcode rải rác hoặc hoàn toàn chưa có; cần quyết định nguồn dữ liệu trước khi build màn xem.
3. **FE-31 phần GĐDA/doanh thu** — cần dữ liệu doanh thu theo dự án + tỷ lệ đề xuất trưởng phòng ban, hiện không tồn tại ở bất kỳ đâu trong repo.
4. **FE-19 phần "dự án cuối cùng ngày 20"** — hiện giản lược thành 1 dự án/người; cần theo dõi nhiều đoạn công tác trong tháng để đúng PRD.

**Đề xuất:** nếu các mục trên thực sự cần cho lô đầu, phải quay lại `/br interview` bổ sung field còn thiếu ở S9 (Out-of-scope) — hiện BR không nói rõ các mục này được LOẠI hay chỉ ĐANG THIẾU. Nếu chủ đích hoãn, nên thêm vào bảng `C19` cho nhất quán (tránh mập mờ như hiện tại).

## Cách tự kiểm lại (không tin báo cáo này, tự tay verify)

```bash
cd br/payroll && python3 -m app.ui   # server tại http://127.0.0.1:8000
```
Mở từng route ở cột "Màn hình", Ctrl+F đúng chuỗi ở cột "Ctrl+F" — ra thì ✅ đúng, không ra thì báo lại để tôi kiểm lại.

## Origin
Rà bằng: `grep` toàn bộ `app/*.py`, đối chiếu `br/frames/*.md` + `br/BR.md` (điều khoản `C19` out-of-scope), và `curl` trực tiếp server sống (`http://127.0.0.1:8000`) lấy đúng text đang hiển thị. Danh sách gốc 32 FE: `br/sources/ANALYSIS-docx-specs.md §S4.1`. Phiên 2026-07-15.
