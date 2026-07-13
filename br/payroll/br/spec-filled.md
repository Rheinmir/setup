# spec-filled — Payroll CTD/Unicons (đối chiếu bộ specs chuẩn S1–S10)

> `schema_version: 0` · sinh bởi `/br interview` ngày 13/07/2026
> Nguồn thô (chỉ-đọc): `llmwiki/raw/payroll requirement/` — 3 docx + 1 xlsx bàn giao.
> Bản bóc đầy đủ (travel được, đọc kèm khi soạn frame):
> - `br/sources/ANALYSIS-docx-specs.md` — bóc từ 3 docx (quy trình HR, PRD v2.1, PRD v3.0)
> - `br/sources/ANALYSIS-excel-params.md` — bóc từ Excel bàn giao (126 field + công thức sống + ground-truth)
>
> Quy ước status: `filled` (raw có, rõ) · `missing` (raw không nói) · `conflict` (2 nguồn khác nhau) · `assumed` (điền bằng giả định, phải hiện ở bảng "Giả định đang gánh" trong BR).
>
> **Phát hiện then chốt:** Excel bàn giao chứa **2 lớp công thức mâu thuẫn nhau** —
> `Payroll structure` (to-be, cái team *định* code) và công thức Excel **sống** trong `Payroll Mar 2026`
> (as-is, cái *đang chạy thật*). Chính HR đã tự chấm cột `Matched? (Y/N)` và đánh **N (lệch)** cho 10 field.
> Đây là câu hỏi số 1 phải chốt (Q1) vì nó đổi kết quả của **mọi** con số lương.

---

## S1 · Tầm nhìn & bài toán

### S1.1 Sản phẩm giải bài toán gì
`status: filled` · `provenance: raw:PRD__Payroll_System_v2 (2).docx · raw:TÀI LIỆU YÊU CẦU SẢN PHẨM HỆ THỐNG PAYROLL_sent.docx`

Lõi tính lương (Payroll Engine) trung tâm cho HR/C&B của Coteccons/Unicons: tự tổng hợp công từ Workday (Workday **không** tự tổng hợp công) và tính toàn bộ lương / phụ cấp / thưởng / BHXH / thuế TNCN, thay cho các sheet Excel thủ công.

### S1.2 Đau hiện tại
`status: filled` · `provenance: raw:PRD v2.1 §4.2 · raw:HR-Quy trinh...docx §V.1`

- Workday chỉ trả công thô theo ngày/bộ phận → Payroll phải gánh toàn bộ logic tổng hợp.
- Bảng lương hiện chạy trên Excel thủ công; chính file bàn giao lộ **16 điểm lệch** giữa công thức "chuẩn" và công thức đang chạy (xem `ANALYSIS-excel-params.md` §10).
- Quy trình tay 6 ngày + 5 lớp ký; đơn duyệt treo làm trễ chốt lương.
- Gap Analysis của HR tự nhận: *no BA · no technical specs · **no test suite** · 1 dev bus-factor · no staging · **no audit log** ("payroll sai thì ai biết?")*.

### S1.3 "Thành công" trông thế nào (kiểm-chứng-được)
`status: filled` · `provenance: raw:PRD v2.1 §2, §8 · raw:xlsx sheet "Payroll Mar 2026"`

1. **Đối chiếu ground-truth**: engine chạy trên dòng dữ liệu thật (dòng 9 sheet `Payroll Mar 2026`) ra **đúng** `NET_PAY = 189.930.161` và toàn bộ 20+ cột kết quả trung gian (GROSS, TAXABLE_INC, PIT, TOTAL_INS…).
2. **Truy vết**: mọi con số truy được về `công thức + số ngày + định mức + nguồn định mức` (Quy định chung hay Tờ trình nào).
3. Hiệu năng: toàn bộ nhân sự (hàng ngàn người) < 5 phút.

### S1.4 Phi-mục-tiêu
`status: filled` · `provenance: raw:PRD v2.1 §2.1, §4.3, §8`

Không tích hợp hệ HR nào ngoài Workday · không truy thu **công** sau khoá kỳ · Payroll không là source-of-truth dữ liệu gốc (trừ Override).

---

## S2 · Người dùng & vai trò

### S2.1 Nhóm người dùng
`status: conflict` → **Q2**

| PRD v2.1 (nhiều nhóm) | PRD v3.0 (chỉ HR) |
|---|---|
| Admin · HR C&B · Thư ký công trường · Chỉ huy trưởng · Trưởng bộ phận (duyệt qua Teams) · Lãnh đạo (Dashboard) | "Hệ thống **chỉ** dành cho HR Admin và C&B Staff. **Không có tài khoản** cho nhân viên hay Trưởng bộ phận." |

### S2.2 Vai trò & quyền
`status: filled` · `provenance: raw:PRD v2.1 §3, §6.4`

Granular: Xem / Sửa / Xuất file / Khoá kỳ / Duyệt thay. **Field-level masking**: thư ký + CHT chỉ thấy ngày công, **tuyệt đối không thấy số tiền**. Báo cáo bảng công chi tiết chỉ HR C&B, **mọi lượt xuất phải ghi log**.

### S2.3 Quy mô
`status: filled` · `provenance: raw:xlsx sheet General`

Roster thật ở Workday: `Get_Workers` = **4.179 nhân sự**. Đa pháp nhân (multi-tenant) — chỉ PRD v3.0 nói.

---

## S3 · Luồng nghiệp vụ chính

### S3.1 / S3.2 Flow đầu-cuối
`status: filled` · `provenance: raw:HR-Quy trinh §IV.2 · raw:xlsx sheet "Sys flow_Payroll"`

Vòng đời kỳ lương (state machine từ Excel): `New → Computed → Done → Pushed` (+ `Cancel`).
Timeline tháng: chấm công 16–19 → BĐNS 18–19 → nạp bảng lương 20–21 → **tính lương 22** → teamlead rà 23 → TP kiểm 24 → **TGĐ + KTT duyệt chi ≤ 25** → hạch toán/lưu trữ 26.
Object `Allowance / Enter times / Expense`: `Draft → Approved → Archived`.

### S3.3 Luồng ngoại lệ
`status: filled` · `provenance: raw:HR-Quy trinh §V.1 · raw:PRD v2.1 §4.3, §6.2`

Rà soát sai → quay lại bước tính · đơn `?P` (chờ duyệt) **không** cộng vào công hưởng lương · đơn treo quá cut-off → HR Override (bắt buộc ghi lý do + sync-back Workday) · sửa công sau khoá kỳ → từ chối, không truy thu.

---

## S4 · Chức năng

### S4.1 Danh sách feature
`status: filled` · 32 feature (FE-01…FE-32) — xem `ANALYSIS-docx-specs.md` §S4.1.
Lõi bắt buộc: engine tổng hợp công · engine phụ cấp (7 loại + pro-rata + luật <14 ngày + điều động) · lương chính tách giai đoạn · OT · thưởng · BHXH (luật 14 ngày) · thuế TNCN · khoá kỳ · audit log · báo cáo/trình ký · UI.

### S4.2 Acceptance-criteria
`status: filled` (phần lõi) · `provenance: raw:PRD v2.1 §5.4 (biên bản họp 23/03/2026) · raw:xlsx dòng 9`

- **AC-1 (suất ăn khi điều động)**: VP A 5 ngày (1 bữa/ngày) + dự án B ≥30km 20 ngày (3 bữa/ngày) → **65 suất**. Ngày ≤ 4 tiếng → 0 suất.
- **AC-2 (luật <14 ngày + điều động)**: BP A (3 làm việc + 1 lễ), BP B (3 làm việc + 2 lễ), tổng làm việc thực tế 6 < 14 → `PC = (3+1)/công_chuẩn × định_mức_A + (3+2)/công_chuẩn × định_mức_B`. Phép / nghỉ hưởng lương khác / không lương **không** được tính.
- **AC-3 (ground-truth Excel, dòng 9)**: `BASIC_SAL 200tr · STD_DAYS 22 · PAID_DAYS 22 · 3 NPT` → `SI_EMP 3.744.000` (trần **46,8tr**) · `TAXABLE_INC 185.392.000` · `PIT 50.387.200` (bậc 35% − 14,5tr) · **`NET_PAY 189.930.161`**.
- **AC-4 (thuế thử việc)**: VN + thử việc + `TAXABLE_INC ≥ 2tr` → 10%; `< 2tr` → 0. Nước ngoài + thử việc → 20%.

### S4.3 Ưu tiên (MoSCoW)
`status: missing` → **Q7**

---

## S5 · Dữ liệu

### S5.1 / S5.2 Entity & field
`status: filled` · `provenance: raw:xlsx sheet "Payroll structure" (126 dòng)`

**Nguồn chân lý của mô hình dữ liệu là bảng 126 field có mã CODE** (`STD_DAYS`, `BASIC_SAL`, `PAID_DAYS`, `GROSS`, `TAXABLE_INC`, `PIT`, `NET_PAY`, `NET_PAY_HOME`, `TOTAL_CTY_COST`…), mỗi field có `type` (`input` | `formula` | `system`), nguồn (`WD API` | `HR input` | `excel compute`), cờ `tax`, cờ `vis` (hiện trên payslip), cờ `editable`. Chuỗi phụ thuộc đầy đủ → `NET_PAY_HOME`: xem `ANALYSIS-excel-params.md` §1.18.

Entity nghiệp vụ: Employee · Contract (Chính thức / Thử việc) · PayPeriod (21→20) · InsurancePeriod (01→cuối tháng, **lệch trục**) · TimesheetDay (ký hiệu công) · AllowanceRate (bảng định mức theo Level 1–8) · TờTrình (override có ngày hiệu lực) · Bonus · InsuranceContribution · TaxRecord · Dependent · Payslip · PayrollRun/Lock · AuditLog.

### S5.4 Ràng buộc dữ liệu
`status: filled`

- Kỳ công **21 → 20**; kỳ BHXH **01 → cuối tháng** (2 trục song song).
- Công chuẩn: **VP** trừ Chủ nhật **và chiều thứ 7** (thứ 7 = ½ ngày); **CT** chỉ trừ Chủ nhật.
- Ngày ≤ 4 tiếng → 0 suất ăn. Đơn `?P` không cộng công.
- **Luật 14 ngày BHXH**: (thử việc + không lương + thai sản + ốm dài) ≥ 14 ngày trong tháng dương lịch → **không đóng BHXH** tháng đó.
- Mọi phụ cấp phải tách 2 cột **Taxable / Non-tax**.
- Tờ trình **ghi đè** định mức chung từ ngày hiệu lực, **vẫn** chịu pro-rata + luật <14 ngày.

---

## S6 · Tích hợp ngoài

### S6.1 Bên thứ ba
`status: conflict` → **Q3**

PRD v2.1: **chỉ** Workday (+ Teams Bot, Azure AD SSO). PRD v3.0: Workday **+ SAP** (cost allocation) **+ Ngân hàng** (HSBC, Citibank).

Thực trạng API Workday (Excel sheet `General`, 21 endpoint): 🟢 `Get_Workers` (4.179) · 🟡 stale `Monthly_Attendance_Report` · 🔴 **blocked**: `Get_Calculated_Time_Blocks` (*"would give OT actual hours"*), `All_Worker_Time_Off` (*"would give leave data"*) — **nguồn giờ OT và ngày nghỉ đang bị chặn quyền**.

### S6.3 Định dạng trao đổi
`status: filled` — API (Workday, Teams) · Excel import/export · PDF payslip · SFTP đẩy Workday.

---

## S7 · Non-functional

### S7.1 Hiệu năng
`status: filled` — toàn bộ nhân sự (hàng ngàn) < **5 phút**; dashboard realtime.

### S7.2 Bảo mật & phân quyền
`status: filled` — Azure AD SSO · granular (Xem/Sửa/Xuất/Khoá kỳ/Duyệt thay) · field-masking số tiền với thư ký/CHT · **audit log bắt buộc**: giá-trị-cũ → giá-trị-mới, người, thời gian, **lý do bắt buộc** · log mọi lượt xem/xuất báo cáo nhạy cảm.

### S7.4 Khả dụng / backup
`status: missing` → **Q8** (HR tự nhận: *"no staging/UAT environment — payroll cannot be tested in production, staging là non-negotiable"*).

### S7.5 Giao diện & design system
`status: missing` → **Q6**. Raw chỉ nêu tên màn hình (dashboard lãnh đạo, khoá kỳ, cấu hình, nhập tờ trình, chấm công nhanh). Không có wireframe/style guide.

---

## S8 · Ràng buộc

### S8.1 Công nghệ
`status: missing` → **Q5**. Raw **không chỉ định** ngôn ngữ / framework / DB / hosting. Chỉ ràng buộc: Azure AD SSO, Teams Bot, tương thích Microsoft 365, (v3.0) multi-tenant.

### S8.2 Deadline
`status: filled` (bối cảnh) — Excel sheet `General`: dự án Payroll CTD, PM *Thoai, Dao Duy*, tenant **UAT**, trạng thái **🟠 AMBER**, 03/07/2026 → 19/08/2026.

---

## S9 · Out-of-scope

### S9.1 Dứt khoát không làm
`status: filled` — không tích hợp HR khác ngoài Workday · không truy thu công sau khoá kỳ · VP **không** áp định mức chung PC xăng (chỉ theo tờ trình) · GĐDA **không** áp PC công trường/đi lại bảng chung · ngày ≤ 4 tiếng không tính cơm.

---

## S10 · Acceptance tests tổng

### S10.1 Kịch bản nghiệm thu
`status: filled` — AC-1…AC-4 ở S4.2 (đều kiểm-chứng-được bằng máy). Ground-truth máy-kiểm mạnh nhất: **dòng 9 sheet `Payroll Mar 2026`** + 2 ô tự-kiểm sẵn có trong chính Excel (`EF9` = 0 và `EX9` = TRUE).

### S10.2 Dữ liệu mẫu
`status: filled` — Excel bàn giao (đã trong repo qua `br/sources/`). **Roster 4.179 người nằm ở Workday, KHÔNG có trong repo** → giả định gánh (chạy trên roster sinh giả + 1 dòng ground-truth thật).

---

## Bảng gap → câu hỏi hỏi-bù

| # | Field | Vấn đề | Hỏi ở |
|---|---|---|---|
| Q1 | S5.2 | **to-be (Payroll structure) vs as-is (công thức sống) lệch nhau ở 10 field** — chọn lớp nào làm chuẩn? | 001-questions |
| Q2 | S2.1 | Tập người dùng: PRD v2.1 (nhiều role) vs v3.0 (chỉ HR) | 001-questions |
| Q3 | S6.1 | Phạm vi tích hợp: chỉ Workday vs + SAP + Bank | 001-questions |
| Q4 | S4.1 | OT: hệ số ngày thường/đêm + công thức giờ→tiền **không có ở bất kỳ nguồn nào** | 001-questions |
| Q5 | S8.1 | Tech stack | 001-questions |
| Q6 | S7.5 | Design system / UI | 001-questions |
| Q7 | S4.3 | Ưu tiên MoSCoW / phạm vi lô đầu | 001-questions |
| Q8 | S7.4 | Môi trường + backup | 001-questions |
| Q9 | S5.4 | Trần BHXH: khai 50,6tr nhưng bảng lương thật dùng **46,8tr** | 001-questions |
| Q10 | S4.2 | Cơm miễn thuế: structure **1,2tr** vs payslip thật **730k** | 001-questions |
| Q11 | S5.2 | Giảm trừ bản thân: structure **15,5tr** vs payslip mẫu **11tr** (cũ) | 001-questions |
| Q12 | S10.2 | Roster thật 4.179 người không có trong repo — chạy engine trên dữ liệu nào? | 001-questions |
