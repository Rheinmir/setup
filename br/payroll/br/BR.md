# BR — Payroll CTD/Unicons

> `schema_version: 0` · compile từ `br/spec-filled.md` + `br/interview/001-answers.md` · 13/07/2026
> Mỗi điều khoản có `clause_id` (kế thừa field-id S1–S10) + provenance. Frame truy ngược về đây; code truy ngược về frame.
> Nguồn chân lý chi tiết: `br/sources/ANALYSIS-excel-params.md` · `br/sources/ANALYSIS-docx-specs.md`

---

## ⚠️ BẢNG "GIẢ ĐỊNH ĐANG GÁNH" — nhìn một phát biết đang cược gì

| # | Giả định | Nếu sai thì sao | Nguồn | Cách hạ rủi ro |
|---|---|---|---|---|
| **A1** | **Base tính bảo hiểm = `CONTRACT_TOTAL`** (lương HĐ = cơ bản + PC trách nhiệm), không phải `BASIC_SAL` | Mọi NV **có phụ cấp trách nhiệm** sẽ sai BHXH/BHYT/KPCĐ/công đoàn | as-is `U9`/`V9`. Ground-truth dòng 9 **không phân biệt được** vì `RESP_SAL = 0` → BASIC = CONTRACT | Hỏi HR. Đổi 1 dòng trong `params.json` → `ins_base` |
| **A2** | **Trần BH 46,8tr và cơm miễn thuế 730k là mức ĐANG CHẠY**; 50,6tr / 1,2tr trong sheet tham số là mức **mới chưa tới ngày hiệu lực** (chưa công thức nào tiêu thụ) | Chạy sai kỳ tương lai; hoặc đang sai kỳ hiện tại | Dòng 9 khớp 46,8tr ở **7 công thức độc lập**; payslip khớp 730k bằng số học (78×45k − 730k = 2.780.000) | `effective_from` bắt buộc trên mọi tham số. Hỏi HR: "50,6tr / 1,2tr áp từ kỳ nào?" |
| **A3** | **Hệ số OT ngày thường / ban đêm / danh sách 300% không tồn tại** → OT vào engine là **số tiền input**, không tự chế công thức giờ→tiền | Nếu HR thật ra có hệ số → engine thiếu 1 nguồn thu nhập | Excel: `OT_TAX`/`OT_NONTAX` type = `input`, "KHÔNG CÓ TRONG EXCEL công thức tính tiền OT từ giờ". Giờ OT thật (`Get_Calculated_Time_Blocks`) **đang bị chặn quyền** | `params.ot_multipliers` để sẵn (`sunday: 2.0` ✓, `weekday: null`, `night_extra: null`) + cờ `ot_from_hours: false` |
| **A4** | **"Trả thêm 100%" ngày Lễ/Tết** = cộng thêm 100%, không phải tổng 200% | Sai tiền OT ngày lễ | [HR-QT] văn bản mập mờ | Hỏi HR (câu 1 dòng) |
| **A5** | Bảng định mức phụ cấp theo **Level 1–8** trong Excel: số trần trụi (`300`, `800`) = **nghìn đồng** | Sai phụ cấp điện thoại/xăng 1000× | Excel không ghi đơn vị; `1tr`/`2tr5` thì ghi rõ | Đối chiếu với bảng ngạch QL/CV/NV của PRD v2.1 (có đơn vị đồng đầy đủ) |
| **A6** | **Tech stack Python 3 stdlib-only**, không DB, không network | Không sai nghiệp vụ; chỉ là ràng buộc thi công | Raw **MISSING** hoàn toàn phần công nghệ | Engine tách khỏi HTTP/DB → thay `_run_app.py` + `adapters.py` là chuyển stack được |
| **A7** | **Lô đầu 1 vai HR C&B, không auth, không tích hợp** (Workday/SAP/Bank/Teams/Azure AD hoãn) | Chưa dùng được ở production | 3 API Workday sống còn đang 🔴 **Blocked** (giờ OT, ngày nghỉ) | Adapter 4 hàm (`C18.1`) — nối lại không đụng engine |
| **A8** | Bộ test **SYN-1..6** (thử việc, expat, biên bậc thuế, miễn BHXH ≥14 ngày) đúng theo công thức sống — nhưng **chưa ai đối chiếu số thật** | Engine "xanh" mà vẫn sai ở nhánh không có trong dòng 9 | Chỉ có **1** dòng nhân viên thật trong toàn bộ file bàn giao | Xin HR 10–20 dòng thật đã ẩn danh phủ các nhánh này |
| **A9** | Roster 4.179 người **không có trong repo** → chạy trên 1 dòng thật + case tổng hợp | Chưa chứng minh được ở quy mô thật | `Get_Workers` = 4.179 rows ở Workday | Test `PERF` nhân bản 4.179 dòng để đo < 5 phút |

**Ba câu phải hỏi HR trước khi khoá BR:** (1) base bảo hiểm là `CONTRACT_TOTAL` hay `BASIC_SAL`? (2) 50,6tr / 1,2tr áp từ kỳ nào? (3) "trả thêm 100%" ngày lễ = tổng 200% hay +100%?

---

## C1 · Tầm nhìn & phạm vi

**C1.1** — Sản phẩm là **lõi tính lương (Payroll Engine)** cho HR/C&B Coteccons/Unicons: nhận dữ liệu nhân sự + chấm công, tính toàn bộ chuỗi lương → phụ cấp → thưởng → BHXH → thuế TNCN → **lương thực nhận**, thay các sheet Excel thủ công. `provenance: raw:PRD v2.1 §1`

**C1.2** — Tiêu chí "thành công" là **kiểm-chứng-được**, không phải cảm tính: engine chạy trên dòng dữ liệu thật của HR phải ra **đúng từng đồng** `NET_PAY = 189.930.161`. `provenance: raw:xlsx "Payroll Mar 2026" dòng 9`

**C1.3** — Nguyên tắc cắt phạm vi lô đầu: **cái gì hôm nay chứng minh được là đúng bằng máy thì làm; cái gì không chứng minh được thì hoãn**. `provenance: user (Q7)`

---

## C2 · Người dùng & quyền

**C2.1** — Lô đầu: **một vai duy nhất HR C&B**, không đăng nhập (chạy local). Model quyền đặt sẵn **một chỗ** (`app/auth.py`, enum theo PRD v2.1 §3: `view · edit · export · lock_period · approve_on_behalf · mask_money`), mọi handler đi qua `require(perm)` — nối Azure AD sau chỉ thay `current_user()`. `provenance: raw:PRD v3.0 §3 · assumed (A7)`

**C2.2** — Ràng buộc bảo mật giữ nguyên trong model quyền kể cả khi chưa bật auth: thư ký/CHT **tuyệt đối không thấy số tiền** (`mask_money`); mọi lượt xuất báo cáo nhạy cảm phải ghi log. `provenance: raw:PRD v2.1 §3, §6.4`

---

## C3 · Nguồn chân lý & lớp công thức ⭐ điều khoản gốc

**C3.1** — Excel bàn giao chứa **2 lớp công thức mâu thuẫn**: `to-be` (sheet `Payroll structure`) và `as-is` (công thức Excel **sống** trong `Payroll Mar 2026`). HR đã tự chấm **10 field lệch** (`Matched? = N`). **Engine bám lớp `as-is`** — vì đó là lớp duy nhất kiểm chứng được bằng máy hôm nay, và là số nhân viên **thực sự nhận được**. `provenance: raw:xlsx sheet "Payroll structure" cột M "Matched? (Y/N)" (10 dòng N: PAID_DAYS, CONTRACT_TOTAL, INS_SAL_BH, INS_SAL_UI, TAXABLE_GROSS, PERSONAL_DED, TAXABLE_INC, UNION_FEE, KPCD_CTY, TOTAL_CTY_COST) · user (Q1)`

**C3.2** — Mọi field lệch phải ghi vào `docs/DELTA-as-is-vs-to-be.md` để HR ký. Lớp to-be giữ sau cờ `params.formula_layer` (`"as_is"` | `"to_be"`) — đổi **một dòng** là chạy lớp kia. `provenance: user (Q1)`

**C3.3** — Chốt từng field lệch (engine dùng cột trái):

| CODE | Engine (as-is) | Bỏ (to-be) |
|---|---|---|
| `PAID_DAYS` | `IF(chính thức, OFFICIAL_DAYS, PROB_DAYS) + PAID_LEAVE + HOLIDAY + COMP + PAID_OTHER + BEREAVE` — **không** cộng `SI_DAYS`, `ADJ_DAYS` | bản cộng `SI_DAYS` + `ADJ_DAYS` |
| `CONTRACT_TOTAL` | `IF(chính thức, BASIC_SAL + RESP_SAL, PROB_SAL)` | `BASIC_SAL + [RESPONSIBILITY_ALLOW]` (mã không tồn tại) |
| `INS_SAL_BH` | `IF(chính thức, MIN(CONTRACT_TOTAL, 46.800.000), 0)` | `MIN(BASIC_SAL, 50.600.000)` |
| `EARNED_SAL` | `ROUND(PROB_EARNED + OFFICIAL_EARNED + RESP_EARNED + EARNED_PAID_LEAVE, 0)` — **4 thành phần** | 3 thành phần |
| `GROSS` | `ADJ_MINUS` được **CỘNG** (HR nhập số âm để trừ) | `… + ADJ_PLUS − ADJ_MINUS` |
| `TAXABLE_GROSS` | **có** trừ `CHARITY_DED` và `EARNED_PAID_LEAVE` | không trừ |
| `UNION_FEE` | `MIN(INS_SAL_BH × 0,5%, 253.000)` → 234.000 ✓ | `BASIC_SAL × 0,5%` → 1.000.000 ✗ |
| `KPCD_CTY` | `INS_SAL_BH × 2%` → 936.000 ✓ | `BASIC_SAL × 2%` → 4.000.000 ✗ |
| `TNLD_CTY` | `INS_SAL_BH × 0,5%` (trần **BH**, không phải trần BHTN) → 234.000 ✓ | `MIN(BASIC_SAL, 106,2tr) × 0,5%` → 531.000 ✗ |
| `TOTAL_CTY_COST` | `NET_PAY + TOTAL_INS_CTY + KPCD_CTY` → 201.522.161 ✓ | `GROSS + …` → 236.602.000 ✗ |
| `PIT` | biểu **5 bậc** (5/10/20/30/35%) | bảng 7 bậc cũ ở sheet `References` — **vứt** |

Hai thứ **to-be đúng hơn** và được giữ (ground-truth xác nhận): `PERSONAL_DED = 15.500.000`, `DEPENDENT_DED = 6.200.000`/người.

---

## C4 · Tham số hệ thống — MỘT chỗ duy nhất

**C4.1** — Toàn bộ tham số nằm ở `data/params.json`, **mỗi tham số có `effective_from`**. Đổi số không được sửa code. Lý do bắt buộc (không phải nice-to-have): payslip mẫu là kỳ cũ (giảm trừ 11tr) trong khi bảng lương hiện hành là 15,5tr → cùng một engine phải chạy đúng **cả hai kỳ**. `provenance: user (Q9/Q10/Q11)`

**C4.2** — ⚠️ **HAI TRẦN CÙNG TỒN TẠI — engine phải giữ cả hai, không được quy về một:**
- `ins_cap_bh_display = 50.600.000` — trần **hiển thị** ở cột `INS_SAL_BH` (U9 = 50.600.000).
- `ins_cap_bh = 46.800.000` — trần **tính thật**, mọi công thức BHXH/BHYT/KPCĐ/công đoàn đều ăn trần này. Khớp đồng thời **7 công thức độc lập** của dòng 9: `SI_EMP` 3.744.000 · `HI_EMP` 702.000 · `SI_CTY` 7.956.000 · `HI_CTY` 1.404.000 · `TNLD_CTY` 234.000 · `KPCD_CTY` 936.000 · `UNION_FEE` 234.000.

Chính Excel tự tố cáo mâu thuẫn này bằng ô tự-kiểm của nó: `U2 = U9 × 17% = 8.602.000`, nhưng `SI_CTY` thật `= 7.956.000`. Nếu engine quy về một trần thì **hoặc** sai cột U **hoặc** sai toàn bộ tiền bảo hiểm.
Trần **BHTN = 106.200.000** dùng chung cho cả hiển thị lẫn tính (`UI_EMP` 1.062.000 ✓). `provenance: raw:xlsx dòng 9 + ô check U2 · verified`

**C4.3** — **Cơm: đơn giá 45.000/suất; miễn thuế 730.000/tháng** (không phải 1,2tr). Bằng chứng số học từ payslip thật: 78 suất × 45.000 = 3.510.000; 3.510.000 − 730.000 = 2.780.000 = đúng cột chịu thuế. `provenance: raw:xlsx Payslip template · raw:PRD v2.1 §5.3.1 · verified`

**C4.4** — **Giảm trừ bản thân 15.500.000; NPT 6.200.000/người.** Ground-truth dòng 9 xác nhận trực tiếp cả chuỗi (`TOTAL_DED` 34.100.000 → `TAXABLE_INC` 185.392.000 → `PIT` 50.387.200 → `NET_PAY` 189.930.161). Thử việc → `PERSONAL_DED = 0`. `provenance: raw:xlsx dòng 9 · verified`

**C4.5** — Tỷ lệ đóng: **NLĐ** BHXH 8% · BHYT 1,5% · BHTN 1% (**tổng 10,5%**). **Công ty** BHXH 17% · TNLĐ-BNN 0,5% · BHYT 3% · BHTN 1% (**tổng 21,5%**) + **KPCĐ 2%**. Phí công đoàn NLĐ **0,5%, trần 253.000**. `provenance: raw:HR-QT §V.2 · raw:xlsx §5.1 · verified`

**C4.6** — **Biểu thuế TNCN 5 bậc lũy tiến** (dùng công thức sống, **vứt** bảng 7 bậc cũ ở sheet `References`):

| Bậc | Thu nhập tính thuế | Suất | Rút gọn |
|---|---|---|---|
| 1 | ≤ 10tr | 5% | `× 5%` |
| 2 | ≤ 30tr | 10% | `× 10% − 500.000` |
| 3 | ≤ 60tr | 20% | `× 20% − 3.500.000` |
| 4 | ≤ 100tr | 30% | `× 30% − 9.500.000` |
| 5 | > 100tr | 35% | `× 35% − 14.500.000` |

`provenance: raw:xlsx CK9 + ô tự-kiểm EX9 (IF ≡ SUMPRODUCT = TRUE) · verified`

---

## C5 · Lịch & kỳ

**C5.1** — **Kỳ công (kỳ lương) = 21 tháng trước → 20 tháng này.** Ví dụ kỳ 03/2026 = 21/02/2026 – 20/03/2026. `provenance: raw:PRD v2.1 §4.1 · raw:HR-QT §V.1 · raw:xlsx Time Tracking Rule · verified`

**C5.2** — **Công chuẩn**: Văn phòng = trừ Chủ nhật **và chiều thứ 7** (thứ 7 tính **½ ngày**); Công trường = **chỉ** trừ Chủ nhật. Lưu riêng từng kỳ. `provenance: raw:xlsx F1/F2 (NETWORKDAYS.INTL) · raw:PRD v2.1 §4.1 · verified`

**C5.3** — **Kỳ BHXH = 01 → cuối tháng dương lịch**, **lệch trục** với kỳ công → engine đếm **song song hai trục thời gian**. `provenance: raw:PRD v2.1 §5.1.4 · verified`

**C5.4** — Danh mục ngày lễ tự động hằng năm: `01/01` · 5 ngày Tết Âm lịch · `30/04` · `01/05` · `02/09 (+1 ngày)` · Giỗ Tổ `10/03` ÂL. HR chỉnh được. `provenance: raw:PRD v2.1 §7 · raw:xlsx Time Tracking Rule`

---

## C6 · Chấm công

**C6.1** — Bộ ký hiệu công tối thiểu: `x` (làm việc) · `x1` (lương thời gian) · `OL` (ốm hưởng lương Cty) · `P`/`F` (phép năm) · `R`/`Fo` (việc riêng có lương) · `L` (lễ) · `NB` (nghỉ bù) · `Ts`/`TSN` (thai sản) · `ON`/`OD` (ốm BHXH) · `TN` (tai nạn) · `Ro` (không lương) · `?P` (chờ duyệt). `provenance: raw:PRD v2.1 §4.2 · verified`

**C6.2** — Đơn trạng thái **`?P` (chờ duyệt) KHÔNG được cộng** vào công hưởng lương. `provenance: raw:PRD v2.1 §6.2 · verified`

**C6.3** — `PAID_DAYS` theo as-is (xem C3.3). Hai loại ngày trong bảng lương thật **chưa có mã** được cấp mã mới: `PAID_OTHER_DAYS` (nghỉ có hưởng lương), `BEREAVE_DAYS` (ma chay/hiếu hỉ). `provenance: raw:xlsx AC/AD · user (Q1)`

---

## C7 · Lương chính & pro-rata

**C7.1** — `PROB_EARNED = ROUND(PROB_SAL / STD_DAYS × PAID_DAYS, 0)` khi HĐ = thử việc, ngược lại 0. `OFFICIAL_EARNED = ROUND(BASIC_SAL / STD_DAYS × PAID_DAYS, 0)` khi HĐ = chính thức, ngược lại 0. Đơn giá thử việc = **85%** lương chính thức. `provenance: raw:xlsx AJ9/AK9 · raw:PRD v2.1 §5.1.1 · verified`

**C7.2** — `RESP_EARNED = ROUND(RESP_SAL / STD_DAYS × PAID_DAYS, 0)` — phụ cấp trách nhiệm cũng pro-rata theo ngày, tách theo ngày hiệu lực nếu bổ nhiệm giữa kỳ. `provenance: raw:xlsx AL9 · raw:PRD v2.1 §5.1.2 · verified`

**C7.3** — `EARNED_PAID_LEAVE` (lương phép tồn) = `ngày phép tồn / STD_DAYS × mức lương` — **chỉ NV chính thức**. Cộng vào `EARNED_SAL` (thành phần thứ 4). `provenance: raw:xlsx sheet "Payroll Mar 2026" AM10/AM11 (note công thức: "ngày phép tồn/ngày công chuẩn × Mức lương... chỉ áp dụng cho nhân viên chính thức") · verified`

**C7.4** — **Tách giai đoạn**: thử việc → chính thức, trước → sau bổ nhiệm, điều động giữa các bộ phận đều tính theo **ngày phát sinh thực tế**, hệ thống **tự tách dòng, không nhập tay**. `provenance: raw:HR-QT §V.4 · raw:PRD v2.1 §5.2 · verified`

---

## C8 · Phụ cấp

**C8.1** — **Suất ăn**: Văn phòng **1 bữa/ngày** · công trường/dự án **< 30 km: 2 bữa** · **≥ 30 km: 3 bữa** · ngày làm **≤ 4 tiếng: 0 bữa**. `MEAL_ALLOW = tổng_suất × 45.000`. `provenance: raw:PRD v2.1 §5.3.1 · verified`

**C8.2** — Mọi phụ cấp **tách 2 cột Taxable / Non-tax**. Cơm: `MEAL_NONTAX = MIN(MEAL_ALLOW, 730.000)`, `MEAL_TAX = MAX(0, MEAL_ALLOW − 730.000)`. `provenance: raw:PRD v2.1 §5.2 · verified`

**C8.3** — **Pro-rata chung**: `phụ_cấp = định_mức / công_chuẩn × số_ngày_hưởng`. `provenance: raw:HR-QT §V.3 · verified`

**C8.4** — ⭐ **Luật <14 ngày**: nếu **ngày làm việc thực tế** trong kỳ **< 14**, số ngày hưởng = **(ngày làm việc thực tế + ngày lễ)** — **không** tính phép, nghỉ hưởng lương khác, không lương. Áp cho: điện thoại, xăng/nhiên liệu, đi lại, công trường, và các phụ cấp cố định theo tháng. `provenance: raw:PRD v2.1 §5.2 · raw:HR-QT §V.3 · raw:xlsx note AQ10 · verified`

**C8.5** — ⭐ **Điều động**: số ngày hưởng chia **thực tế theo từng bộ phận**, áp **định mức của từng bộ phận**. Suất ăn cũng tổng hợp riêng theo bộ phận với quy tắc bữa của từng nơi. `provenance: raw:PRD v2.1 §5.2, §5.4 · verified`

**C8.6** — **Tờ trình duyệt riêng ghi đè** định mức chung kể từ **ngày hiệu lực** (từ ngày – đến ngày), **vẫn chịu** pro-rata + luật <14 ngày. Khối Văn phòng **không** áp định mức chung phụ cấp xăng (chỉ theo tờ trình). GĐDA **không** áp PC công trường/đi lại bảng chung. `provenance: raw:PRD v2.1 §5.2, §5.3.3, §5.3.7 · verified`

**C8.7** — Bảng định mức: điện thoại theo ngạch × VP/CT (QL.01 1tr … NV.03-05 200k/300k, thử việc 0/300k); đi lại theo dải khoảng cách × nhóm đối tượng; công trường + công tác xa theo khoảng cách × trình độ. `provenance: raw:PRD v2.1 §5.3.2, §5.3.4, §5.3.5 · assumed (A5: đơn vị bảng Level 1–8 trong Excel)`

**C8.8** — ⭐ **Phụ cấp truy thu/truy lĩnh (FE-06)**: khi định mức phụ cấp của nhân viên **thay đổi có hiệu lực hồi tố** (vd cập nhật trình độ học vấn, nơi tuyển dụng, chức danh theo Tờ trình), `PC_TRUY_THU = (định mức mới − định mức cũ) / công chuẩn × số ngày công tương ứng`, hiện thành **CỘT RIÊNG** trên bảng phụ cấp (không gộp vào `ADJ_PLUS`/`ADJ_MINUS` chung chung — hai cơ chế khác mục đích), **kèm lý do bắt buộc**. Không có ca truy thu → `PC_TRUY_THU = 0`. `provenance: raw:PRD v2.1 §4.3 (trích "Truy thu/Truy lĩnh trước khóa kỳ") · verified`

> ⚠️ **Giới hạn phạm vi lô đầu (ghi rõ để không giả vờ đã kiểm):** yêu cầu gốc là "**trong phạm vi kỳ CHƯA khoá**". Hệ thống **KHÔNG kiểm được** điều kiện này vì FE-15 (khoá kỳ thủ công) nằm ngoài phạm vi lô đầu (`C19`) — không có khái niệm "kỳ đã khoá" để đối chiếu. Coi như mọi kỳ đang tính đều mở; khi FE-15 được build, `PC_TRUY_THU` phải gác thêm điều kiện này.

---

## C9 · Tăng ca (OT)

**C9.1** — OT vào engine là **SỐ TIỀN INPUT** (`OT_TAX`, `OT_NONTAX`). **Không tự chế** công thức giờ → tiền: Excel khai OT `type = input`, và nguồn giờ OT thật (`Get_Calculated_Time_Blocks`) **đang bị chặn quyền**. `provenance: raw:xlsx §1.6 · verified`

**C9.2** — `params.ot_multipliers` để sẵn, **chỉ điền cái tài liệu nói thẳng**: `sunday: 2.0` ✓ · `holiday_extra: 1.0` (⚠ A4) · `holiday_300: null` (danh sách không tồn tại) · `weekday: null` · `night_extra: null`. Cờ `ot_from_hours: false` (mặc định TẮT). Nhóm Mắt Bão có nhánh hệ số riêng. `provenance: raw:PRD v2.1 §5.5 · assumed (A3)`

**C9.3** — Ghi nhận **ngày nghỉ bù** (không phải tiền kỳ này, là input `COMP_DAYS` kỳ sau): làm ngày Lễ/Tết → **+2 ngày**; Coteccons Day / nghỉ bổ sung / bù trùng ngày nghỉ tuần → **+1 ngày**. `provenance: raw:HR-QT §V.4 · verified`

---

## C10 · Thưởng & trích quỹ

**C10.1** — 13 khoản thưởng đều là **input** (`BONUS_TET`, `BONUS_13M`, `BONUS_KPI`, …); `BONUS_TOTAL` = tổng. Điều kiện loại trừ: NV nghỉ việc/có kế hoạch nghỉ; nghỉ thai sản/ốm dài/không lương **lũy kế ≥ 10 ngày** → không tính vào thời gian xét thưởng. `provenance: raw:HR-QT §V.4 · verified`

**C10.2** — **Trích thưởng hàng tháng** (có ground-truth, phải khớp): `BONUS_SAVE_TRAVEL = 6.000.000/12 = 500.000` · `BONUS_SAVE_KPI = CONTRACT_TOTAL/4` · `BONUS_SAVE_13M = CONTRACT_TOTAL/12` · `BONUS_SAVE_TET = MIN(CONTRACT_TOTAL/12, 15.000.000/12)`. Điều kiện: có ngày hưởng lương > 0 **và không có ngày nghỉ việc**. `BUDGET_SAVE = GROSS + TOTAL_INS_CTY + KPCD_CTY + các khoản trích`. `provenance: raw:xlsx §1.17 + dòng 9 (BUDGET_SAVE 305.018.667) · verified`

---

## C11 · BHXH / BHYT / BHTN

**C11.1** — `INS_SAL_BH = IF(chính thức, MIN(CONTRACT_TOTAL, 46.800.000), 0)` · `INS_SAL_UI = IF(chính thức, MIN(CONTRACT_TOTAL, 106.200.000), 0)`. Base = `CONTRACT_TOTAL` (⚠ **A1**). `provenance: raw:xlsx U9=50.600.000/V9=106.200.000 (trần HIỂN THỊ, KHÔNG phải trần dùng để tính BHXH) · sheet "Payroll structure" K19 tự ghi công thức dùng 50.600.000 (mâu thuẫn với ground-truth) · 46.800.000 là SỐ SUY NGƯỢC từ BY9/CA9/DD9/DH9/DF9/DM9/CT9 ÷ đúng tỷ lệ % (7 phép chia độc lập đều khớp) — không có ô nào chép thẳng số này · assumed (A1)`

**C11.2** — `SI_EMP/HI_EMP/SI_CTY/HI_CTY/TNLD_CTY/KPCD_CTY/UNION_FEE` **đều** ăn `INS_SAL_BH`. `UI_EMP/UI_CTY` ăn `INS_SAL_UI`. `provenance: raw:xlsx dòng 9 · verified`

**C11.3** — ⭐ **Luật 14 ngày**: trong **tháng dương lịch** (01 → cuối tháng), nếu tổng (ngày thử việc + không lương + thai sản + ốm dài) **≥ 14 ngày** → **KHÔNG trích đóng BHXH** tháng đó. `provenance: raw:HR-QT §V.2 · raw:xlsx note BY10 · verified`

**C11.4** — **Người nước ngoài**: `UI_EMP = 0` (không đóng BHTN). NV có **hợp đồng 2 nơi** → không đóng BHXH/BHYT/BHTN (cờ tay `no_insurance`, Workday chưa quản lý). `provenance: raw:xlsx sheet "Payroll structure" Q19 ("HĐ 2 nơi đang k đc quản lý trên WD") + L20 ("người nước ngoài = 0, expat không đóng BHTN") · raw:HR-QT §V.2 · verified`

---

## C12 · Thuế TNCN

**C12.1** — `TAXABLE_INC = MAX(0, TAXABLE_GROSS − TOTAL_INS − TOTAL_DED)`. `provenance: raw:xlsx CJ9 · verified`

**C12.2** — `PIT` theo biểu **5 bậc** (C4.6). **Case đặc biệt**: thử việc + Việt Nam + `TAXABLE_INC ≥ 2tr` → **10%**; `< 2tr` → **0**. Thử việc + nước ngoài → **20%**. Nước ngoài không work-permit → 20%. `provenance: raw:xlsx CK9 · verified`

**C12.3** — NPT: hồ sơ gửi **trước ngày 15** → tính kỳ đó; **sau 15** → kỳ sau. `provenance: raw:HR-QT §V.4 · verified`

---

## C13 · Tổng hợp → lương thực nhận

**C13.1** — `GROSS = EARNED_SAL + mọi phụ cấp (tax + non-tax) + OT + BONUS_TOTAL + TOTAL_SUPPORT + ADJ_PLUS + ADJ_MINUS` (⚠ `ADJ_MINUS` được **cộng** — HR nhập số âm để trừ, xem C3.3). `provenance: raw:xlsx BW9 · verified`

**C13.2** — `TAXABLE_GROSS = GROSS − (mọi khoản non-tax) − SEVER_ALLOW − SI_BENEFIT − BONUS_TRAVEL − CHARITY_DED − EARNED_PAID_LEAVE`. `provenance: raw:xlsx BX9 · verified`

**C13.3** — ⭐ `NET_PAY = GROSS − TOTAL_INS − TOTAL_PIT − TOTAL_POST_DED + TOTAL_POST_ADD` · `NET_PAY_HOME = ROUND(NET_PAY, 0)`. `provenance: raw:xlsx CZ9/DB9 · verified`

**C13.4** — `TOTAL_CTY_COST = NET_PAY + TOTAL_INS_CTY + KPCD_CTY` (as-is — **không** phải GROSS). `provenance: raw:xlsx DN9 · verified`

**C13.5** — **Tiền dùng `Decimal` + `ROUND_HALF_UP`.** Excel `ROUND(x,0)` là half-up; `round()` của Python là half-even → lệch 1 đồng và HR sẽ bắt ngay. `provenance: lens:payroll-expert · verified`

---

## C14 · Truy vết (lý do dự án tồn tại)

**C14.1** — ⭐ Mọi con số phải **truy vết được về `công thức + số ngày + định mức + nguồn định mức`**. Engine trả `trace` cho mỗi CODE: công thức nguyên văn → giá trị từng biến (đệ quy xuống được) → tham số đã dùng (kèm giá trị + `effective_from`) → `clause_id` trong BR này → dòng Excel gốc. `provenance: raw:PRD v2.1 §8 (NFR) · verified`

**C14.2** — **Audit log** (khi có sửa tay): giá-trị-cũ → giá-trị-mới · người · thời gian · **lý do bắt buộc**. Trả lời gap #9 của chính HR: *"When payroll output is wrong, how does anyone know?"* `provenance: raw:PRD v2.1 §6.2 · raw:xlsx Gap Analysis #9`

---

## C15 · Giao diện

**C15.1** — **3 màn hình xem**: `/` bảng lương (grid theo nhóm cột Excel thật, dòng TỔNG, ô lệch ground-truth tô đỏ) · `/payslip/<msnv>` phiếu lương (đúng layout thật: kỳ "Từ 21/[M-1] đến 20/[M]", khối A–E, đánh số `[0]`–`[67]`, in được) · `/trace/<msnv>/<CODE>` cây trace công thức. `provenance: raw:xlsx Payslip template · user (Q6)`

**C15.4** — **Màn hình thứ 4 — `/upload` tải Excel mass-upload**: MỘT tab tối giản duy nhất (không thêm form nhập tay từng field) — chọn kỳ lương + chọn file Excel (header hàng 1 = đúng tên field `employees.json`), tải lên thay cho việc HR phải tự tay dựng JSON. Sau khi tải: hiện số nhân sự đã nạp + link sang `/` xem ngay. Chỉ **adapt** module `app/adapters.py` sẵn có (ghi vào đúng `data/inputs/<kỳ>/employees.json` mà 4 hàm ranh giới đã đọc — không mở đường I/O song song), không sửa dữ liệu từng-field qua UI, không đăng nhập/phân quyền (kế thừa "Ngoài phạm vi" của C15.1). `provenance: user (2026-07-15, yêu cầu trực tiếp — không suy diễn từ raw)`

**C15.5** — **Màn hình `/params` — xem Master Data lương (FE-23)**: chỉ-xem toàn bộ `data/params.json` — mọi bộ tham số (kể cả bộ **chưa hiệu lực**, xem `_pending_hr`/A2), không chỉ bộ đang active. Không sửa qua UI (đổi số vẫn sửa thẳng `data/params.json`, kế thừa nguyên tắc C4.1). `provenance: user (2026-07-15) · raw:data/params.json`

**C15.6** — **Màn hình `/report/cost-by-dept` — phân bổ chi phí theo phòng ban (FE-31, phạm vi rút gọn)**: cộng dồn `TOTAL_CTY_COST` theo `phong_ban` cho một kỳ bất kỳ (`?period=`). **CHỈ** phân bổ theo phòng ban (department-level aggregation) — **KHÔNG** phải phân bổ theo dự án/doanh thu (GĐDA, PRD-3.0 §4.3: "phân bổ theo tỷ lệ dựa theo DOANH THU") hay theo tỷ lệ đề xuất trưởng phòng ban, vì **không có dữ liệu doanh thu/tỷ lệ đề xuất** trong hệ thống — hai cơ chế đó vẫn `⊘ ngoài phạm vi`, chỉ phần cộng dồn theo phòng ban (nền tảng bắt buộc trước khi phân bổ tiếp) được build. Kỳ khác kỳ ground-truth (`2026-03`) PHẢI hiện cảnh báo **"DỮ LIỆU DRAFT"** — không được lẫn với dữ liệu đã kiểm chứng. `provenance: user (2026-07-15, dữ liệu draft do user yêu cầu để test tiếp) · raw:PRD v3.0 §4.3 (giới hạn phạm vi)`

**C15.7** — **Màn hình `/report/signoff` — Báo cáo Trình ký, Template 0 (FE-19, phạm vi rút gọn)**: gộp nhân sự theo `du_an` (field trên record), mỗi nhóm là một bảng in-để-ký-tay (mã NV, họ tên, `NET_PAY_HOME` thật qua `engine.compute()`, dòng chữ ký Chỉ huy trưởng). **GIẢN LƯỢC**: PRD yêu cầu gộp theo dự án **cuối cùng nơi làm việc vào ngày 20** (cần theo dõi nhiều đoạn công tác trong tháng — dữ liệu đó không tồn tại); ở đây coi mỗi nhân viên chỉ có 1 dự án trong kỳ (field `du_an` trực tiếp). **KHÔNG** phải quy trình duyệt/ký điện tử nhiều cấp (C&B → Teamlead → TP NS-TH → GĐ QTNNL/PTGĐ VH → TGĐ+KTT) — đó là FE-16/FE-10, `⊘ ngoài phạm vi` (Teams Bot, Override, Sync-back). Kỳ khác `2026-03` PHẢI hiện "DỮ LIỆU DRAFT". `provenance: user (2026-07-15, dữ liệu draft) · raw:PRD v2.1 §6.3 + trích "Nhân sự điều động..." (giới hạn phạm vi)`

**C15.2** — Số tiền: `tabular-nums`, căn phải, phân cách kiểu VN. **Bắt buộc toggle dark/light** (`prefers-color-scheme` mặc định + nút toggle + `localStorage` + script chống FOUC trong `<head>`) — không ép mode. `provenance: user (Q6)`

**C15.3** — ⭐ **Giao diện BẮT BUỘC theo `br/DESIGN.md`** (kế thừa `skills/br/assets/design-template.md`): Vibe 0 **Neumorphism** — mặc định của cả dây chuyền, template nêu đích danh *"app nghiệp vụ/dashboard/form nội bộ như Payroll"* — cộng Layout **Asymmetrical Bento**. Bốn luật cứng: một mặt đơn sắc (card **cùng màu nền**, KHÔNG viền, không màu card riêng) · cặp bóng đối xứng sáng-trên-trái + tối-dưới-phải · trạng thái nhấn/nhập dùng `inset` · accent là **near-black LẬT theo theme** (không phải màu rực). Chữ đạt **WCAG AAA ≥ 7:1** ở CẢ hai theme — **tương phản là con số, cấm ước lượng bằng mắt**, phải có assert máy. `provenance: raw:skills/br/assets/design-template.md §3.2, §3.6, §4 (bộ specs chuẩn S7.5) · verified`

> ⚠️ **Ghi nhận thất bại (14/07/2026):** vòng slice đầu tôi BỎ QUA S7.5 và tự chế C15 chung chung ("3 màn, có toggle") → loop-runner sinh đúng cái được yêu cầu: bảng HTML trần trụi, không design system. Bài học: **spec chuẩn có gì thì BR phải mang sang, không được tóm tắt mất luật.** Và luật thị giác phải thành assert máy — hứa suông trong prompt không phải lớp gác.

---

## C16 · Snapshot & đối chiếu

**C16.1** — Mỗi lần chạy engine ghi **snapshot bất biến** `data/out/<period>/run-<ts>/`, **không ghi đè**. Chạy lại kỳ cũ với param-set cũ phải ra **đúng số cũ**. `provenance: user (Q8)`

**C16.2** — `python3 -m app.diff <run_a> <run_b>` → in NV nào lệch, CODE nào lệch, bao nhiêu đồng. Đây chính là **parallel-run so với Excel** mà tài liệu ghi là MISSING — thứ duy nhất cho phép HR dám cắt Excel. `provenance: user (Q8) · raw:S10.1 (parallel run MISSING)`

---

## C17 · Nghiệm thu

**C17.1** — ⭐ **GT-1**: dòng 9 Excel → engine ra **chính xác từng đồng** 25 cột kết quả: `GROSS 225.010.000` · `TAXABLE_GROSS 225.000.000` · `TOTAL_INS 5.508.000` · `TOTAL_DED 34.100.000` · `TAXABLE_INC 185.392.000` · `PIT 50.387.200` · `NET_INCOME 169.114.800` · **`NET_PAY 189.930.161`** · `TOTAL_INS_CTY 10.656.000` · `KPCD_CTY 936.000` · `TOTAL_CTY_COST 201.522.161` · `BUDGET_SAVE 305.018.667`. `provenance: raw:xlsx dòng 9 · verified`

**C17.2** — **GT-1b**: hai ô **tự-kiểm của chính Excel** phải xanh — `EF9`: cân sổ = 0; `EX9`: hai cách tính thuế (thang IF ≡ SUMPRODUCT) cho **cùng** kết quả. `provenance: raw:xlsx EF9/EX9 · verified`

**C17.3** — **GT-2 (effective_from)**: cùng input dòng 9, chạy với **param-set kỳ cũ** (giảm trừ bản thân 11tr, NPT 4,4tr) → `TOTAL_DED = 24.200.000` → `TAXABLE_INC = 195.292.000` → `PIT = 53.852.200`. Cùng một engine, hai bộ tham số, hai kết quả đều đúng → chứng minh `effective_from` là thật, không phải khẩu hiệu. `provenance: user (Q11) · verified`

> ⛔ **Payslip mẫu (Lê Văn Biên) KHÔNG dùng làm fixture** — đã kiểm và nó **không cân số học** ở 3 chỗ độc lập: BHXH in 3.744.000 trên lương 20tr (đúng phải là 1.600.000 — con số đó là của dòng 9, bị dán nhầm); `TAXABLE_INC` in 3.880.000 nhưng tính lại ra 8.326.000; `PIT` in 572.000 nhưng bậc 1 (5%) chỉ ra 194.000. Đó là **template trình bày**, không phải chứng từ đã tính đúng. Dùng nó làm test = ép engine sai theo. `provenance: kiểm tay 13/07/2026`

**C17.4** — **AC-1 / AC-2** (biên bản họp 23/03/2026, kiểm-chứng-được bằng máy):
- **AC-1**: VP A 5 ngày (1 bữa) + dự án B ≥30km 20 ngày (3 bữa) → **65 suất**.
- **AC-2**: BP A (3 làm việc + 1 lễ), BP B (3 làm việc + 2 lễ) → tổng làm việc 6 < 14 → `PC = (3+1)/CC × ĐM_A + (3+2)/CC × ĐM_B`.

`provenance: raw:PRD v2.1 §5.4 · verified`

**C17.5** — **SYN-1..6** (⚠ **A8**, chưa đối chiếu số thật): thử việc VN `<2tr` → PIT 0 · thử việc VN `≥2tr` → 10% · thử việc nước ngoài → 20% · expat → `UI_EMP = 0` · 5 biên bậc thuế (10/30/60/100tr) · miễn BHXH khi nghỉ ≥14 ngày. `provenance: lens:payroll-expert`

**C17.6** — **PERF**: 4.179 bản sao dòng 9 → chạy **< 5 phút** (NFR). `provenance: raw:PRD v2.1 §8 · raw:xlsx Get_Workers 4.179 rows`

---

## C18 · Ranh giới adapter (build-now-adapt-later)

**C18.1** — Mọi I/O ngoài đi qua **một file, bốn hàm** (`app/adapters.py`):
```
fetch_employees(period)   -> list[dict]   # nay: JSON | sau: Workday Get_Workers
fetch_timesheet(period)   -> list[dict]   # nay: JSON | sau: Monthly_Attendance (🟡 stale) + Calculated_Time_Blocks (🔴 blocked)
push_payslip(period, rows)-> None         # nay: ghi HTML/JSON | sau: SFTP → Workday
export_bank_file(period, rows) -> Path    # nay: CSV | sau: template HSBC/Citibank
```
Engine **không gọi gì khác**. Thứ tự nối lại khi có credential: Workday inbound → Payslip outbound → Bank → SAP. `provenance: user (Q3) · assumed (A7)`

**C18.2** — **Hàm thứ năm (adapt, không thay thế 4 hàm gốc)**: `save_uploaded_employees(period, rows: list[dict]) -> Path` — ghi `rows` (đã parse từ Excel mass-upload, xem C15.4) vào **đúng** `data/inputs/<period>/employees.json` mà `fetch_employees` đọc; không network, không schema mới — `rows` phải khớp khoá với record `fetch_employees` đã trả trước giờ (tối thiểu có `employee_id`). `provenance: user (2026-07-15)`

**C18.3** — **Hàm thứ sáu — `export_payroll_master(period, p) -> Path` (FE-20, Payroll Master Template 2)**: xuất `out/<period>/payroll_master.csv` — nhân sự + TOÀN BỘ field engine tính ra (mọi thành phần lương/phụ cấp/BHXH/thuế/thực nhận/chi phí công ty, qua `engine.bang_luong()` thật, không hard-code). **BA cột kế toán** PRD mô tả đầy đủ (`profit_cost_center`, `wbs`, `funds_center`) để **RỖNG** — không có nguồn dữ liệu nào trong hệ thống (không có Profit/Cost Center, WBS, Funds Center ở bất kỳ đâu), **không bịa số** cho ba cột này. Route `GET /export/payroll-master?period=` tải file trực tiếp (`Content-Disposition: attachment`) — đây là **file**, không phải màn hình xem. `provenance: user (2026-07-15) · raw:PRD v2.1 §6.3 (cấu trúc cột) — 3 cột kế toán MISSING theo raw`

---

## C19 · Out-of-scope lô đầu (ghi `docs/DEFERRED.md`, kèm lý do chặn)

Workday API (FE-01) · SAP (FE-27) · file ngân hàng HSBC/Citibank (FE-25) · push Payslip API (FE-26) · Teams Bot + Override + Sync-back (FE-16) · Azure AD SSO (FE-32) · multi-tenant (FE-28) · Dashboard lãnh đạo (FE-22) · Mắt Bão (FE-18) · truy thu/thoái thu BHXH + lãi nộp chậm (FE-12) · báo cáo động (FE-29) · khoá kỳ UI (FE-15) · màn nhập Tờ trình (FE-05 phần UI).

**Không** làm: truy thu **công** sau khoá kỳ · Payroll tự sinh dữ liệu gốc · tích hợp hệ HR nào ngoài Workday. `provenance: raw:PRD v2.1 §4.3, §8 · user (Q7)`
