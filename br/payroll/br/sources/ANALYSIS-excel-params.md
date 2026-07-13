# TRÍCH XUẤT ĐẦY ĐỦ — `[Confidential] Payroll Handover Assessment - param.xlsx`

Nguồn: `/Users/giatran/orca/workspaces/setup/issue-15-br-k/scratchpad/raw-extract/confidential-payroll-handover-assessment-1-param.txt` (610 dòng, 12 sheet — đã đọc hết).

Quy ước: `KHÔNG CÓ TRONG EXCEL` = trường/tham số không tồn tại trong file. Mọi con số dưới đây đều trích nguyên văn.

---

## 0. Hai nguồn công thức — PHẢI phân biệt

File có **2 lớp công thức khác nhau và MÂU THUẪN NHAU**:

| Lớp | Ở đâu | Ý nghĩa |
|---|---|---|
| **Structure (to-be)** | Sheet `Payroll structure`, cột **I** (`công thức hiện tại`) và cột **J** | Công thức chuẩn hoá theo mã CODE — cái team định code |
| **Sample (as-is)** | Sheet `Payroll Mar 2026`, công thức Excel SỐNG ở dòng 9 | Công thức bảng lương thật đang chạy |
| **Đối chiếu** | Cột `M` = `Matched? (Y/N)` | HR/IT đã tự chấm: **Y** = 2 lớp khớp, **N** = LỆCH, **?** = chưa rõ |

Các field bị chấm **N (lệch)**: `PAID_DAYS`, `CONTRACT_TOTAL`, `INS_SAL_BH`, `INS_SAL_UI`, `TAXABLE_GROSS`, `PERSONAL_DED`, `TAXABLE_INC`, `UNION_FEE`, `KPCD_CTY`, `TOTAL_CTY_COST`. Field `PIT` và `NET_PAY_2` = `?`.

---

## 1. PAYROLL STRUCTURE — 126 dòng, đầy đủ theo thứ tự `seq`

Cột `C` = cột Excel trong sheet `Payroll Mar 2026` (`#N/A` = **field CHƯA có cột trong bảng lương thật**).
Cột `F` (tax) = `T` → khoản chịu thuế. Cột `G` = nguồn dữ liệu.

### 1.1 Ngày công (TIME_TRACKING)

| CODE | Tên tiếng Việt | Cột | seq | type | Nguồn | Công thức (dịch sang CODE) |
|---|---|---|---|---|---|---|
| `STD_DAYS` | Công chuẩn | W | 100 | input | — | — |
| `PROB_DAYS` | Ngày công thử việc | X | 110 | input | WD API | — |
| `OFFICIAL_DAYS` | Ngày công chính thức | Y | 120 | input | WD API | — |
| `ACTUAL_DAYS` | Tổng ngày công thực tế | **#N/A** | 125 | formula | — | **KHÔNG CÓ TRONG EXCEL** (khai là formula nhưng cột I trống) |
| `PAID_LEAVE_DAYS` | Nghỉ phép năm | Z | 130 | input | WD API | — |
| `HOLIDAY_DAYS` | Nghỉ lễ, tết | AA | 135 | input | WD API | — |
| `COMP_DAYS` | Nghỉ bù | AB | 137 | input | WD API | — |
| `REGIME_DAYS` | Nghỉ chế độ & có hưởng lương | **#N/A** | 140 | input | WD API | — |
| `UNPAID_DAYS` | Nghỉ không hưởng lương | AE | 145 | input | WD API | — |
| `SI_DAYS` | Nghỉ chế độ BHXH | AF | 150 | input | WD API | — |
| `ADJ_DAYS` | Ngày công điều chỉnh | AG | 155 | input | WD API | — |
| `CONS_ALLOW` | Phụ cấp công trình | **#N/A** | 158 | input | — | — |
| `PAID_DAYS` | **Tổng ngày làm việc hưởng lương** | AI | 190 | formula | — | `ACTUAL_DAYS + HOLIDAY_DAYS + PAID_LEAVE_DAYS + COMP_DAYS + REGIME_DAYS + SI_DAYS + ADJ_DAYS` |

**Công thức SỐNG (AI9) — khác với trên:**
```
IF(LOẠI_HĐ="Chính thức", SUM(Y:AD), X + SUM(Z:AD))
= Chính thức: OFFICIAL_DAYS + PAID_LEAVE + HOLIDAY + COMP + AC + AD
= Thử việc : PROB_DAYS   + PAID_LEAVE + HOLIDAY + COMP + AC + AD
```
→ **LỆCH (M=N)**: bản sống KHÔNG cộng `SI_DAYS` và `ADJ_DAYS`; và có 2 cột AC/AD (`Nghỉ có hưởng lương`, `Ngày nghỉ chế độ ma chay/hiếu hỉ`) **chưa được gán CODE nào**.

Các cột bảng lương thật KHÔNG có CODE: `AC` (Nghỉ có hưởng lương), `AD` (Nghỉ chế độ ma chay/hiếu hỉ), `AH` (Ngày phép tồn), `BS` (Các khoản hỗ trợ BHSK), `DA` (USD), `DC` (Ghi chú).

### 1.2 Lương hợp đồng (SAL_CONTRACT_BASE)

| CODE | Tên | Cột | seq | type | Nguồn | Công thức |
|---|---|---|---|---|---|---|
| `PROB_SAL` | Lương thử việc (85%) | Q | — | input | WD | — |
| `BASIC_SAL` | Lương chính thức (100%) | R | 200 | input | WD | — |
| `RESP_SAL` | Phụ cấp trách nhiệm | S | 210 | input | WD API - CTD Payroll | — |
| `CONTRACT_TOTAL` | Tổng lương trên HĐLĐ | T | 220 | formula | — | `BASIC_SAL + [RESPONSIBILITY_ALLOW]` ⚠️ mã `RESPONSIBILITY_ALLOW` **không tồn tại** trong danh mục CODE — thực chất là `RESP_SAL` |
| `INS_SAL_BH` | Mức lương đóng BHXH, BHYT | U | 300 | formula | — | `MIN(BASIC_SAL, 50 600 000)` |
| `INS_SAL_UI` | Mức lương đóng BHTN | V | 310 | formula | — | `MIN(BASIC_SAL, 106 200 000)` |

**Công thức SỐNG:**
```
T9 = IF(M9="Chính thức", R9+S9, Q9)      → Chính thức: BASIC_SAL+RESP_SAL ; Thử việc: PROB_SAL
U9 = IF(M9="Chính thức", MIN(T9, 50 600 000), 0)   ← dùng CONTRACT_TOTAL, KHÔNG phải BASIC_SAL
V9 = IF(M9="Chính thức", MIN(T9, 106 200 000), 0)
```
Ghi chú HR (Q19/Q20): **NV có hợp đồng 2 nơi → KHÔNG đóng BHXH/BHYT/BHTN**; expat → `INS_SAL_UI = 0`. Lưu ý: *"th HĐ 2 nơi đang k đc quản lý trên WD, cần lưu master data"*.

### 1.3 Lương thực tế (SAL_ACTUAL)

| CODE | Tên | Cột | seq | type | Công thức Structure | Công thức SỐNG |
|---|---|---|---|---|---|---|
| `PROB_EARNED` | Lương thử việc | AJ | 400 | formula | `PROB_DAYS * PROB_SAL / STD_DAYS` | `IF(HĐ="Thử việc", ROUND(PROB_SAL/STD_DAYS*PAID_DAYS,0), 0)` |
| `OFFICIAL_EARNED` | Lương chính thức | AK | 410 | formula | `(PAID_DAYS - PROB_DAYS) * BASIC_SAL / STD_DAYS` | `IF(HĐ="Chính thức", ROUND(BASIC_SAL/STD_DAYS*PAID_DAYS,0), 0)` |
| `RESP_EARNED` | Phụ cấp trách nhiệm (thực tế) | AL | 420 | formula | `PAID_DAYS * [RESPONSIBILITY_ALLOW] / STD_DAYS` | `IFERROR(ROUND(RESP_SAL/STD_DAYS*PAID_DAYS,0),0)` |
| `EARNED_PAID_LEAVE` | **Lương phép tồn** | AM | — | formula | *(cột I trống)* — K25: `= ngày phép tồn / STD_DAYS * Mức lương`, **chỉ áp dụng NV chính thức** | input tay trong sample |
| `EARNED_SAL` | Tổng lương thực tế trong tháng | AN | 490 | formula | `PROB_EARNED + OFFICIAL_EARNED + RESP_EARNED` | `ROUND(SUM(AJ:AM),0)` = **có cộng thêm `EARNED_PAID_LEAVE`** |

Ghi chú AK10: *"Bổ nhiệm: nếu có 2 mức lương khác nhau trong kỳ lương thì tính theo 2 giai đoạn"*.
Ghi chú Q21: *"general check: rounding method"*. Q22: `TIỀN: XX.00`. Q23: `day/other: xx.5, yy.0`.

### 1.4 Cơm & phụ cấp chịu thuế (PC_TAX)

| CODE | Tên | Cột | seq | type | Nguồn | Công thức |
|---|---|---|---|---|---|---|
| `MEALS_BASE` | Cơm phụ cấp (bữa) | **#N/A** | 500 | input | excel compute | K26: WD không trả cơm bữa → đếm số bữa = tổng ngày có `Regular time tracking = 1` |
| `MEALS_OT` | Cơm tăng ca (bữa) | **#N/A** | 501 | input | WD API - CTD Payroll | Q27: `= cơm đêm + cơm CN + tăng ca lễ` |
| `MEALS_TOTAL` | Tổng bữa cơm | **#N/A** | 502 | formula | — | *(cột I trống — suy ra `MEALS_BASE + MEALS_OT`)* |
| `MEAL_ALLOW` | PC cơm (tổng) | **#N/A** | 505 | formula | — | `MEALS_TOTAL * 45 000` |
| `MEAL_TAX` | PC cơm (chịu thuế) | AO | 510 | formula (T) | — | `MAX(0, MEAL_ALLOW - 1 200 000)` |
| `PHONE_ALLOW` | PC điện thoại (tổng) | AP | 520 | input | WD API - CTD Payroll | — |
| `PHONE_TAX` | PC điện thoại (chịu thuế) | **#N/A** | 525 | formula (T) | — | `0` |
| `FUEL_ALLOW` | PC NL/Xăng | AQ | 530 | input (T) | WD API - CTD Payroll | — |
| `TRANSPORT_ALLOW` | PC đi lại (chuẩn) | **#N/A** | 535 | input | WD API - CTD Payroll | — |
| `TRIP_OVERRIDE` | PC đi lại duyệt riêng | **#N/A** | 537 | input | HR input | — |
| `TRANSPORT_TAX` | PC đi lại (chịu thuế) | AR | 540 | formula (T) | — | `TRANSPORT_ALLOW + TRIP_OVERRIDE` (Q36: *"ưu tiên PC override nếu có"*) |
| `LIVING_ALLOW` | PC nhà ở | AS | 545 | input (T) | HR input | — |
| `OTHER_ALLOW_TAX` | PC Khác (chịu thuế) | AT | 550 | input (T) | HR input | — |

Trong bảng lương thật, **AO/AR/AU/AV là input tay** (dòng 11 ghi rõ: *"Không có công thức trong sample — nhập trực tiếp"*).

### 1.5 Phụ cấp không chịu thuế (PC_NOTAX)

| CODE | Tên | Cột | seq | type | Công thức |
|---|---|---|---|---|---|
| `MEAL_NONTAX` | PC cơm (không chịu thuế) | AU | 600 | formula | `MIN(MEAL_ALLOW, 1 200 000)` |
| `PHONE_NONTAX` | PC điện thoại (không chịu thuế) | AV | 605 | formula | `[PHONE_ALLOW` ⚠️ **công thức bị cụt trong Excel** (thiếu `]`) — hiểu là `= PHONE_ALLOW` |
| `FUEL_NONTAX` | PC NL/Xăng (không chịu thuế) | AW | 610 | input | — |
| `TRANSPORT_NONTAX` | PC đi lại (không chịu thuế) | AX | 615 | input | — |
| `LIVING_NONTAX` | PC nhà ở (không chịu thuế) | AY | 620 | input | — |
| `OTHER_ALLOW_NONTAX` | PC Khác (không chịu thuế) | AZ | 625 | input | — |

### 1.6 Tăng ca

| CODE | Tên | Cột | seq | type | tax |
|---|---|---|---|---|---|
| `OT_TAX` | Tăng ca (chịu thuế) | BA | 700 | input | T |
| `OT_NONTAX` | Tăng ca (không chịu thuế) | BB | 705 | input | — |

**KHÔNG CÓ TRONG EXCEL**: công thức tính tiền OT từ số giờ. OT vào hệ thống dưới dạng **số tiền input**.

### 1.7 Thưởng (BONUS) — tất cả `input`, `tax=T`, nguồn `WD API`

| CODE | Tên | Cột | seq |
|---|---|---|---|
| `BONUS_TET` | Thưởng tết âm lịch | BC | 800 |
| `BONUS_30_04` | Thưởng 30/04 | BD | 810 |
| `BONUS_CTD_DAY` | Thưởng Coteccons Day | BE | 820 |
| `BONUS_02_09` | Thưởng 02/09 | BF | 830 |
| `BONUS_KPI` | Thưởng KPIs / Văn phòng | BG | 840 |
| `BONUS_13M` | Lương tháng 13 | BH | 850 |
| `BONUS_NEW_YEAR` | Thưởng tết dương lịch 1/1 | BI | 860 |
| `BONUS_PROJECT` | Thưởng dự án | BJ | 870 |
| `BONUS_EXCELLENCE` | Thưởng cá nhân xuất sắc | BK | 880 |
| `BONUS_LOC` | Lộc đầu năm | BL | 885 |
| `BONUS_OTHER` | Thưởng khác | BM | 888 |
| `BONUS_TRAVEL` | Du lịch (**không** chịu thuế, OTHER_INCOME) | BN | 890 |
| `BONUS_REFERRAL` | Thưởng giới thiệu ứng viên nội bộ (T) | BO | 892 |
| `BONUS_TOTAL` | **Tổng thưởng** (formula) | #N/A | 895 |

```
BONUS_TOTAL = BONUS_TET + BONUS_30_04 + BONUS_CTD_DAY + BONUS_02_09 + BONUS_KPI
            + BONUS_13M + BONUS_NEW_YEAR + BONUS_PROJECT + BONUS_EXCELLENCE
            + BONUS_LOC + BONUS_OTHER + BONUS_TRAVEL + BONUS_REFERRAL
```
(Sample **không có cột tổng riêng** — chỉ cộng gộp ẩn trong GROSS.)

Định mức thưởng (ghi chú BC10/BH10):
- `BONUS_TET`: Lương bình quân 12 tháng liền kề, **không quá 15 triệu**. Mức hưởng = `thời gian tính thưởng / 365 × định mức`.
- `BONUS_13M`: Lương bình quân 12 tháng liền kề. Mức hưởng = `thời gian tính thưởng / 365 × định mức`.

### 1.8 Trợ cấp (OTHER_ALLOW) — tất cả `input`, không chịu thuế

| CODE | Tên | Cột | seq |
|---|---|---|---|
| `SEVER_ALLOW` | Trợ cấp nghỉ việc | BP | 900 |
| `SI_BENEFIT` | BHXH chi vào lương | BQ | 905 |
| `OTHER_SUPPORT` | Trợ cấp khác | BR | 910 |
| `FAMILY_SUPPORT` | Các khoản hỗ trợ | **#N/A** | 915 |
| `TOTAL_SUPPORT` | Tổng trợ cấp (formula) | #N/A | 990 |

`TOTAL_SUPPORT = SEVER_ALLOW + SI_BENEFIT + OTHER_SUPPORT + FAMILY_SUPPORT`

### 1.9 Điều chỉnh trước thuế

| CODE | Tên | Cột | seq | type | tax |
|---|---|---|---|---|---|
| `ADJ_PLUS` | Điều chỉnh cộng (+) | BT | 1000 | input | T |
| `ADJ_MINUS` | Điều chỉnh trừ (−) | BU | 1005 | input | — |
| `CHARITY_DED` | Từ thiện / Quỹ PCTT | BV | 1010 | input | — |

### 1.10 Tổng thu nhập

| CODE | Tên | Cột | seq | type |
|---|---|---|---|---|
| `GROSS` | Tổng thu nhập trong tháng | BW | 1100 | formula |
| `TAXABLE_GROSS` | Tổng thu nhập chịu thuế | BX | 1110 | formula |

```
GROSS = EARNED_SAL + MEAL_TAX + MEAL_NONTAX + PHONE_TAX + PHONE_NONTAX
      + FUEL_ALLOW + FUEL_NONTAX + TRANSPORT_TAX + TRANSPORT_NONTAX
      + LIVING_ALLOW + LIVING_NONTAX + OTHER_ALLOW_TAX + OTHER_ALLOW_NONTAX
      + OT_TAX + OT_NONTAX + BONUS_TOTAL + TOTAL_SUPPORT + ADJ_PLUS − ADJ_MINUS

TAXABLE_GROSS = GROSS − MEAL_NONTAX − PHONE_NONTAX − FUEL_NONTAX − TRANSPORT_NONTAX
              − LIVING_NONTAX − OTHER_ALLOW_NONTAX − OT_NONTAX
              − SEVER_ALLOW − SI_BENEFIT − BONUS_TRAVEL
```

**Công thức SỐNG (M=N, LỆCH):**
```
BW9 = SUM(AN9:BU9)                                   ← "Điều chỉnh trừ" (BU) đang bị CỘNG, không TRỪ
BX9 = SUM(AN9:AT9) + BA9 + SUM(BC9:BU9) − BV9 − AM9  ← có trừ CHARITY_DED và EARNED_PAID_LEAVE
```
→ Structure **không** trừ `CHARITY_DED` ở TAXABLE_GROSS, sample **có** trừ. Sample **không** trừ `ADJ_MINUS` ở GROSS.

### 1.11 BHXH nhân viên (IS_EMP)

| CODE | Tên | Cột | seq | type | Công thức Structure (cột I) | Ghi chú sample (cột K) |
|---|---|---|---|---|---|---|
| `SI_EMP` | BHXH NV 8% | BY | 1200 | formula | `MIN(BASIC_SAL, 46 800 000) * 0.08` | `MIN(CONTRACT_TOTAL, 50 600 000) × 8%` |
| `SI_ADJ` | Điều chỉnh BHXH NV | BZ | 1205 | input | — | — |
| `HI_EMP` | BHYT NV 1.5% | CA | 1210 | formula | `MIN(BASIC_SAL, 46 800 000) * 0.015` | `MIN(CONTRACT_TOTAL, 46 800 000) × 1.5%` |
| `HI_ADJ` | Điều chỉnh BHYT NV | CB | 1215 | input | — | — |
| `UI_EMP` | BHTN NV 1% | CC | 1220 | formula | `MIN(BASIC_SAL, 106 200 000) * 0.01` | `MIN(CONTRACT_TOTAL, 106 200 000) × 1%` (expat = 0) |
| `UI_ADJ` | Điều chỉnh BHTN NV | CD | 1225 | input | — | — |
| `TOTAL_INS` | Tổng BHXH nhân viên | CE | 1290 | formula | `SI_EMP + SI_ADJ + HI_EMP + HI_ADJ + UI_EMP + UI_ADJ` | — |

⚠️ **MÂU THUẪN TRẦN LƯƠNG** (rất quan trọng để code):
- `INS_SAL_BH` khai trần **50.600.000**, nhưng công thức `SI_EMP`/`HI_EMP` (cột I) lại dùng trần **46.800.000**.
- Giá trị THẬT trong bảng Mar 2026 dòng 9: `BY9 = 3.744.000 = 46.800.000 × 8%`, `CA9 = 702.000 = 46.800.000 × 1.5%`, `DD9 = 7.956.000 = 46.800.000 × 17%`, `DH9 = 1.404.000 = 46.800.000 × 3%`, `DM9 = 936.000 = 46.800.000 × 2%` → **bảng lương thật đang dùng trần 46.800.000**, trong khi `U9` = 50.600.000. Cell kiểm tra `U2 = U9*0.17 = 8.602.000` ≠ `DD9 = 7.956.000` → chính Excel cũng lộ lệch này.
- BHTN dùng trần **106.200.000** ở cả 2 nơi (`CC9 = 1.062.000 = 106.200.000 × 1%` ✓).

### 1.12 Giảm trừ & thuế TNCN

| CODE | Tên | Cột | seq | type | Công thức |
|---|---|---|---|---|---|
| `PERSONAL_DED` | Giảm trừ bản thân | CF | 1300 | formula | `15 500 000` — sample: `IF(HĐ="Chính thức", 15 500 000, IF(HĐ="Thử việc", 0, 0))` |
| `DEPENDENT_CNT` | Số người phụ thuộc | CG | 1310 | input | — |
| `DEPENDENT_DED` | Giảm trừ gia cảnh NPT | CH | 1320 | formula | `DEPENDENT_CNT * 6 200 000` |
| `TOTAL_DED` | Tổng khoản giảm trừ | CI | 1390 | formula | `PERSONAL_DED + DEPENDENT_DED` |
| `TAXABLE_INC` | Thu nhập tính thuế | CJ | 1400 | formula | `MAX(0, TAXABLE_GROSS − TOTAL_INS − TOTAL_DED)` |
| `PIT` | Thuế TNCN | CK | 1410 | **system** | xem §5.2 |
| `PIT_ADJ` | Điều chỉnh thuế TNCN | CL | 1415 | input | — |
| `TOTAL_PIT` | Tổng thuế TNCN đã khấu trừ | CM | 1420 | formula | `PIT + PIT_ADJ` |
| `NET_INCOME` | Thu nhập thuần | CN | 1490 | formula | `GROSS − TOTAL_INS − PIT − PIT_ADJ` |

⚠️ `TAXABLE_INC` bị chấm **N**: sample `CJ9` **không trừ Từ thiện**, còn Structure ghi chú là có. (Thực tế Từ thiện đã bị trừ ngay ở `BX9`.)

### 1.13 Cộng sau thuế (ADD_EXCL_TAX) — tất cả `input`

| CODE | Tên | Cột | seq |
|---|---|---|---|
| `PIT_SETTLE` | Quyết toán thuế | CO | 1500 |
| `SI_REGIME` | Chế độ BHXH | CP | 1510 |
| `SEVER_FUND` | Trợ cấp thôi việc (trích quỹ) | CQ | 1515 |
| `SEVER_PAY` | Trợ cấp thôi việc NĐ 145/2020 | CR | 1520 |
| `OTHER_POST_ADD` | Cộng sau thuế khác | CS | 1525 |
| `TOTAL_POST_ADD` | Tổng cộng sau thuế (formula) | #N/A | 1590 |

`TOTAL_POST_ADD = PIT_SETTLE + SI_REGIME + SEVER_FUND + SEVER_PAY + OTHER_POST_ADD`

### 1.14 Trừ sau thuế (DED_EXCL_TAX)

| CODE | Tên | Cột | seq | type | Công thức |
|---|---|---|---|---|---|
| `UNION_FEE` | Phí công đoàn (0.5%) | CT | 1600 | formula | Structure: `BASIC_SAL * 0.005` — Sample (K93): `INS_SAL_BH × 0.5%`, **MAX = 253.000** ⚠️ M=N |
| `BAOVET_INS` | Thu hộ BH Bảo Việt | CU | 1605 | input | — |
| `DEDUCT_LOC` | Trừ lộc đầu năm | CV | 1610 | input | sample: `CV9 = BL9` (= `BONUS_LOC`) |
| `PIT_SETTLE_DED` | Quyết toán thuế (trừ) | CW | 1615 | input | — |
| `OTHER_POST_DED` | Trừ sau thuế khác | CX | 1620 | input | — |
| `FAMILY_HEALTH_INS` | BHSK người thân (cty tài trợ) | CY | 1625 | input | sample: `CY9 = BS9` |
| `TOTAL_POST_DED` | Tổng trừ sau thuế | #N/A | 1690 | formula | `UNION_FEE + BAOVET_INS + DEDUCT_LOC + PIT_SETTLE_DED + OTHER_POST_DED + FAMILY_HEALTH_INS` |

### 1.15 Lương thực nhận — ĐÍCH CUỐI

| CODE | Tên | Cột | seq | type | Công thức |
|---|---|---|---|---|---|
| `NET_PAY` | **Lương thực nhận (VND)** | CZ | 1700 | formula | `GROSS − TOTAL_INS − TOTAL_PIT − TOTAL_POST_DED + TOTAL_POST_ADD` |
| `NET_PAY_HOME` | **Lương thực chi (VND)** | DB | 1701 | formula | `ROUND(NET_PAY, 0)` |
| `ADVANCE_1` | Tạm ứng / Lương thực chi đợt 1 | #N/A | 1710 | input | — |
| `NET_PAY_2` | Lương thực chi đợt 2 | #N/A | 1720 | formula | `NET_PAY − ADVANCE_1` (M=?) |

Công thức SỐNG: `CZ9 = ROUND(CN9 + SUM(CO9:CS9) − SUM(CT9:CY9), 0)` → tương đương.

### 1.16 Chi phí công ty (IS_COMP)

| CODE | Tên | Cột | seq | type | Công thức Structure | Ghi chú sample |
|---|---|---|---|---|---|---|
| `SI_CTY` | BHXH Cty 17% | DD | 1800 | formula | `MIN(BASIC_SAL, 46 800 000) * 0.17` | `MIN(CONTRACT_TOTAL, 46 800 000) × 17%` |
| `SI_CTY_ADJ` | Điều chỉnh BHXH Cty | DE | 1805 | input | — | — |
| `TNLD_CTY` | BHTNLĐ-BNN Cty 0.5% | DF | 1810 | formula | `MIN(BASIC_SAL, 106 200 000) * 0.005` | K106: `MIN(…, 46 800 000) × 0.5%` ⚠️ lệch trần ngay trong 1 dòng |
| `TNLD_CTY_ADJ` | Điều chỉnh BHTNLĐ Cty | DG | 1815 | input | — | — |
| `HI_CTY` | BHYT Cty 3% | DH | 1820 | formula | `MIN(BASIC_SAL, 46 800 000) * 0.03` | — |
| `HI_CTY_ADJ` | Điều chỉnh BHYT Cty | DI | 1825 | input | — | — |
| `UI_CTY` | BHTN Cty 1% | DJ | 1830 | formula | `MIN(BASIC_SAL, 106 200 000) * 0.01` | — |
| `UI_CTY_ADJ` | Điều chỉnh BHTN Cty | DK | 1835 | input | — | — |
| `TOTAL_INS_CTY` | Tổng BHXH Cty đóng | DL | 1890 | formula | `SI_CTY + SI_CTY_ADJ + TNLD_CTY + TNLD_CTY_ADJ + HI_CTY + HI_CTY_ADJ + UI_CTY + UI_CTY_ADJ` | — |
| `KPCD_CTY` | 2% KPCĐ Cty | DM | 1895 | formula | `BASIC_SAL * 0.02` | K113: `INS_SAL_BH × 2%` (**không** phải CONTRACT_TOTAL); *"Thử việc = 0?"* ⚠️ M=N |
| `TOTAL_CTY_COST` | Tổng chi phí công ty | DN | 1999 | formula | `GROSS + TOTAL_INS_CTY + KPCD_CTY` | Sample `DN9 = SUM(DL:DM) + CZ9` → dùng **NET_PAY**, không phải GROSS ⚠️ M=N |

Không có CODE (chỉ tên): `MST` (input), `THU NHẬP THÁNG` (formula).

### 1.17 Trích thưởng hàng tháng (SAVE_BONUS) — dự phòng quỹ

| CODE | Tên | Cột | type | Công thức (K) | Công thức SỐNG |
|---|---|---|---|---|---|
| `BONUS_SAVE_NEW_YEAR` | Tết dương lịch 1/1 | DQ | formula | **missing fomula** | — |
| `BONUS_SAVE_30_04` | 30/4 | DR | formula | **missing fomula** | — |
| `BONUS_SAVE_TRAVEL` | Du lịch | DS | formula | Nếu không có termination: `10tr/12` | `IF(NGÀY_NGHỈ_VIỆC<>"", 0, ROUND(6 000 000/12,0))` = **500.000** ⚠️ 6tr ≠ 10tr |
| `BONUS_SAVE_CTD_DAY` | Coteccons day | DT | formula | **missing fomula** | — |
| `BONUS_SAVE_02_09` | 2/9 | DU | formula | **missing fomula** | — |
| `BONUS_SAVE_ADD_2` | Bổ sung đợt 2 | DV | formula | **missing fomula** | — |
| `BONUS_SAVE_KPI` | Thưởng KPIs | DW | formula | `CONTRACT_TOTAL / 4` | `IF(term<>"",0, ROUND(T9/4,0))` |
| `BONUS_SAVE_13M` | Lương tháng 13 | DX | formula | `CONTRACT_TOTAL / 12` | `IF(term<>"",0, ROUND(T9/12,0))` |
| `BONUS_SAVE_TET` | Thưởng Âm lịch | DY | formula | `MIN(CONTRACT_TOTAL, 15 000 000) / 12` | `IF(term<>"",0, MIN(ROUND(T9/12,0), ROUND(15 000 000/12,0)))` |
| `BUDGET_SAVE` | Check budget | EE | formula | `TOTAL_CTY_COST + BONUS_SAVE_TRAVEL + BONUS_SAVE_KPI + BONUS_SAVE_13M + BONUS_SAVE_TET` | `BW9 + DL9 + DM9 + DS9 + DW9 + DX9 + DY9` (dùng **GROSS**, không phải TOTAL_CTY_COST) |

Điều kiện chung (DS10/DW10/DX10/DY10): *"Ngày hưởng lương > 0"* và **không có ngày nghỉ việc**. Q123-Q125: *"lấy lương chính thức luôn"*.

### 1.18 CHUỖI PHỤ THUỘC → LƯƠNG THỰC NHẬN

```
STD_DAYS, PROB_DAYS, OFFICIAL_DAYS, PAID_LEAVE_DAYS, HOLIDAY_DAYS,
COMP_DAYS, REGIME_DAYS, SI_DAYS, ADJ_DAYS
        └─> PAID_DAYS ─┐
                       │
PROB_SAL, BASIC_SAL, RESP_SAL ─> CONTRACT_TOTAL
                       │            ├─> INS_SAL_BH  (MIN, trần 50.6tr)
                       │            └─> INS_SAL_UI  (MIN, trần 106.2tr)
                       ↓
        PROB_EARNED + OFFICIAL_EARNED + RESP_EARNED (+ EARNED_PAID_LEAVE)
                       └─> EARNED_SAL
                                │
   MEALS_BASE + MEALS_OT ─> MEALS_TOTAL ─> MEAL_ALLOW ─> MEAL_TAX / MEAL_NONTAX
   PHONE_*, FUEL_*, TRANSPORT_ALLOW+TRIP_OVERRIDE ─> TRANSPORT_TAX, LIVING_*, OTHER_*
   OT_TAX / OT_NONTAX
   BONUS_* ─> BONUS_TOTAL
   SEVER_ALLOW + SI_BENEFIT + OTHER_SUPPORT + FAMILY_SUPPORT ─> TOTAL_SUPPORT
   ADJ_PLUS, ADJ_MINUS, CHARITY_DED
                                ↓
                             GROSS ─────────> TAXABLE_GROSS
                                │                   │
   INS_SAL_BH/UI ─> SI_EMP, HI_EMP, UI_EMP (+ADJ) ─> TOTAL_INS
   PERSONAL_DED + DEPENDENT_CNT×6.2tr ─────────────> TOTAL_DED
                                │                   │
                                │              TAXABLE_INC = MAX(0, TAXABLE_GROSS − TOTAL_INS − TOTAL_DED)
                                │                   ↓
                                │                 PIT (biểu lũy tiến / 10% / 20%)
                                │                   ↓  + PIT_ADJ
                                │              TOTAL_PIT
                                ↓
   NET_INCOME = GROSS − TOTAL_INS − PIT − PIT_ADJ
                                ↓
   TOTAL_POST_ADD (+) ─┐                 ┌─ TOTAL_POST_DED (−)  [UNION_FEE = INS_SAL_BH×0.5%, max 253k]
                       ↓                 ↓
   ★ NET_PAY = GROSS − TOTAL_INS − TOTAL_PIT − TOTAL_POST_DED + TOTAL_POST_ADD
                       ↓
   ★ NET_PAY_HOME = ROUND(NET_PAY, 0)          ← LƯƠNG THỰC CHI
                       ↓
     NET_PAY_2 = NET_PAY − ADVANCE_1           ← đợt 2
```

---

## 2. TIME TRACKING RULE (sheet `Time Tracking Rule`)

| Loại | Quy tắc (nguyên văn) |
|---|---|
| **Kỳ công** | Từ ngày **21 tháng này đến 20 tháng sau**. VD kỳ công 03/2026: 21/02/2026 – 20/03/2026 |
| **Ngày công chuẩn** | **Văn phòng**: 21→20, trừ Chủ nhật **và chiều thứ 7**. **Công trường**: 21→20, trừ Chủ nhật |
| **Nghỉ phép năm** | 12 ngày/năm; mỗi đủ 05 năm làm việc liên tục +1 ngày phép (**bao gồm thời gian thử việc**). Mỗi tháng làm việc = 1 ngày phép. Chưa đủ tháng: nếu (ngày làm việc + ngày nghỉ có hưởng lương) ≥ **50% công chuẩn tháng** → tính 01 ngày phép. Book vượt định mức → cảnh báo, yêu cầu book trong định mức. NLĐ được tự hủy phép đã duyệt trên hệ thống + mail cho quản lý |
| **Phép tồn** | Chuyển tiếp đến hết **31/12 năm liền kề**, sau đó hủy, **không thanh toán bằng tiền**. Chưa đủ 12 tháng: `(phép năm + phép thâm niên) / 12 × số tháng làm việc thực tế`. **Đã ký HĐLĐ**: nghỉ việc → tổng hợp phép tồn để tính lương phép. **Đang thử việc**: nghỉ việc → clear phép tồn, KHÔNG tính lương phép tồn |
| **Nghỉ không hưởng lương** | Phải có đơn + phê duyệt của Quản lý theo phân quyền **và** Phòng Nhân sự-Tổng hợp |
| **Nghỉ ốm (BHXH)** | Lương hưởng: **75% lương bình quân đóng BHXH 6 tháng liền kề**. Con ốm: ≤20 ngày làm việc/năm nếu con <3 tuổi; ≤15 ngày/năm nếu con 3–<7 tuổi. Bản thân ốm: ≤30 ngày/năm (đóng BHXH <15 năm); ≤40 ngày/năm (15–<30 năm); ≤60 ngày/năm (≥30 năm). Hồ sơ: nội trú → Giấy ra viện; ngoại trú → Giấy nghỉ hưởng BHXH |
| **Nghỉ ốm (Công ty)** | Định mức **03 ngày/năm dương lịch**, mỗi lần tối đa 01 ngày. Hết năm hệ thống **tự clear, không cộng dồn** |
| **Nghỉ thai sản** | **100% lương bình quân đóng BHXH 6 tháng liền kề**. Nam (nghỉ trong 60 ngày đầu từ ngày vợ sinh): 05 ngày (sinh thường 1 con); 07 ngày (phẫu thuật / con <32 tuần); sinh đôi 10 ngày, từ sinh ba trở lên +03 ngày/con; sinh đôi trở lên phải phẫu thuật: 14 ngày. Nữ sinh con: **6 tháng** (nộp đơn trước 1 tháng). Nữ khám thai: ≤02 ngày/lần, ≤10 ngày/thai kỳ |
| **Nghỉ việc riêng có hưởng lương** | Bản thân kết hôn: 03 ngày. Con đẻ/con nuôi kết hôn: 01 ngày. Tang chế (cha/mẹ đẻ, nuôi; cha/mẹ vợ-chồng; vợ/chồng; con đẻ/con nuôi chết): 03 ngày |
| **Nghỉ bù** | Đi làm ngày lễ → theo dõi & trừ dần. **Ngày Lễ/Tết theo luật: trả thêm 100% tiền lương + bố trí 02 ngày nghỉ bù hưởng nguyên lương cho MỖI ngày làm việc.** Coteccons Day / ngày nghỉ bổ sung do Cty quyết định / nghỉ bù do Lễ-Tết trùng ngày nghỉ tuần: **01 ngày nghỉ bù** hưởng nguyên lương cho mỗi ngày làm việc |
| **Nghỉ lễ (1)** — set tự động | 01/01 dương lịch · **05 ngày** 29 – 4/1 âm lịch (hoặc 1/1–5/1 âm) · 30/04 (01 ngày) · 01/05 (01 ngày) · 02/09 (01 ngày, **thêm 1 ngày 01/09 hoặc 03/09**) · Giỗ Tổ 10/03 âm lịch (01 ngày). Nếu cần chỉnh → chỉnh TRs |
| **Đăng ký đi làm lễ** | NLĐ đăng ký / Thư ký import file → Trưởng bộ phận duyệt → gửi về HR |

**Hệ số tăng ca** (rải rác ở note `BB10` sheet Payroll Mar 2026):
- **Chủ nhật: 200%**
- **Ngày nghỉ Lễ/Tết: trả thêm 100% tiền lương** + ghi nhận **2 ngày nghỉ bù** cho mỗi ngày đi làm
- Ngày truyền thống / bổ sung / bù: ghi nhận **1 ngày nghỉ bù** cho mỗi ngày đi làm

⚠️ **KHÔNG CÓ TRONG EXCEL**: hệ số OT ngày thường (thường 150%), hệ số OT ban đêm (thường 30%/20% cộng thêm), công thức quy đổi giờ OT → tiền. Payslip có 6 dòng OT (thường/nghỉ/lễ × ngày/đêm) nhưng **không có hệ số nào**.

**Quy tắc chốt công**: ngày **20** hàng tháng (Sys flow A4). Payroll period mặc định **25 tháng trước → 25 tháng hiện tại** (Sys flow A15) — ⚠️ mâu thuẫn với kỳ công 21→20 và với Payslip (21 tháng trước → 20 tháng này).

**Miễn đóng BHXH** (note BY10): *"số ngày thử việc, không lương, thai sản… ≥ 14 ngày tính từ ngày 1 đến cuối tháng → KHÔNG đóng BHXH"*.

---

## 3. ALLOWANCE RULE + EXCEPT

### 3.1 Bảng mức phụ cấp theo Level (đơn vị nguyên văn — `1tr` = 1.000.000; các số trần trụi như `300`, `800` là **nghìn đồng**, Excel không ghi rõ đơn vị)

| # | Compensation plan | Điều kiện | L1 | L2-3 | L4 | L5 | L6 | L7 | L8 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Tel** (điện thoại) | — | 300 | 400 | 400 | 600 | 800 | 1tr | 1tr |
| 2 | **Car** | Not BOD | — | — | — | — | — | **10tr** | **25tr** |
| 2 | **Car** | BOD | — | — | — | — | — | — | **35tr** |
| 3 | **Petro** (xăng) | Not site | **800 with approval** (cột L1) | — | — | — | — | — | — |
| 3 | **Petro** | Site | — | 1tr | 1tr | 1tr | 1tr | — | — |
| 4 | **Responsibility** | Security Team Leader | **1tr2** | | | | | | |
| 4 | | Deputy Security Team Leader | **800k** | | | | | | |
| 4 | | Acting Deputy Site Manager | **5tr** | | | | | | |
| 4 | | Acting Site Manager | **8tr** | | | | | | |
| 4 | | Acting Project Director | **15tr** | | | | | | |
| 5 | **Transportation** | 30-100 km, central | — | 1tr2 | 1tr5 | 1tr5 | 1tr9 | — | — |
| 5 | | 100-400 km, central | — | 2tr1 | 2tr6 | 2tr6 | 2tr9 | — | — |
| 5 | | 400-1k km, central | — | 4tr | 4tr5 | 4tr5 | 5tr | — | — |
| 5 | | 30-100 km, not central | — | 1tr2 | 1tr5 | 1tr5 | 1tr9 | — | — |
| 5 | | 100-400 km, not central | — | 2tr1 | 2tr6 | 2tr6 | 2tr9 | — | — |
| 5 | | 400-1k km, not central | — | 4tr8 | 5tr3 | 5tr3 | 8tr6 | — | — |
| 5 | | > 1k km, not central | — | 5tr7 | 7tr6 | 7tr6 | 13tr2 | — | — |
| 6 | **Meal** | Security staff | **2 × 45k** | | | | | | |
| 6 | | Non-project | **1 × 45k** | | | | | | |
| 6 | | Project < 30km | **2 × 45k** | | | | | | |
| 6 | | Project >= 30km | **3 × 45k** | | | | | | |

(Cột `D`=Level 1, `E`=Level 2-3, `F`=Level 4, `G`=Level 5, `H`=Level 6, `I`=Level 7, `J`=Level 8. Ô trống = không hưởng / không quy định.)

### 3.2 Quy tắc prorata (từ note dòng 10 sheet `Payroll Mar 2026`)

- **PC cơm** (AO10/AU10): `vp: 1 bữa/ngày · site <30km: 2 bữa/ngày · site ≥30km: 3 bữa/ngày`. Miễn thuế **730k** (sample) → phần vượt là chịu thuế. ⚠️ Structure lại dùng **1.200.000** (`MEAL_TAX = MAX(0, MEAL_ALLOW − 1.200.000)`).
- **PC Xăng** (AQ10): `VP: up duyệt riêng theo tờ trình` · `CT: L2–L6: 1tr/tháng`.
- **PRORATA CHUNG** (lặp lại ở AQ10/AR10/AV10/AX10): *"Số ngày đi làm thực tế **dưới 14 (mười bốn) ngày** → phụ cấp được tính theo tỷ lệ **ngày làm việc thực tế và ngày nghỉ lễ** trong tháng"*. Ghi chú thêm ở mọi dòng: *"lưu ý nhân sự điều động"*.
- **PC điện thoại** (AV10): theo Level, cùng quy tắc <14 ngày.
- **PC Khác** (AT10): *"Phụ cấp duyệt riêng theo tờ trình"*.

### 3.3 Exception (chỉ có **1** case được điền — 5 dòng còn lại TRỐNG)

| # | Compensation plan | Exception | Handle | Compute |
|---|---|---|---|---|
| 1 | Transportation | New Hire employee has the same permanent residence province as their working location | **WD** | **Amount = 0** |
| 2–6 | *(trống)* | *(trống)* | *(trống)* | *(trống)* |

---

## 4. MASTER DATA

Sheet `Master data` chỉ có **1 danh mục duy nhất**:

| Contract type | # | Name |
|---|---|---|
| | 1 | **Chính thức** |
| | 2 | **Thử việc** |
| | 3 | *(trống)* |

**KHÔNG CÓ TRONG EXCEL** (không có sheet/danh mục): phòng ban, chức danh, ngạch-bậc, cost center, WBS. Chúng chỉ tồn tại dưới dạng **cột** trong bảng lương thật:
- `C` = VP/CT · `D` = MÃ KIỂM TOÁN · `E` = MÃ SỐ NHÂN VIÊN · `F` = TÊN NHÂN VIÊN · `G` = **Quốc tịch** (giá trị dùng trong công thức: `"Việt Nam"` / `"Nước ngoài"`) · `H` = MÃ WSB PHÒNG BAN BỔ CHI PHÍ · `I` = TÊN PHÒNG BAN BỔ CHI PHÍ · `J` = BỘ PHẬN · `K` = CHỨC DANH · `L` = **NGẠCH - BẬC** · `M` = **LOẠI HỢP ĐỒNG** (`Chính thức`/`Thử việc`) · `N` = NGÀY VÀO LÀM · `O` = NGÀY KẾT THÚC THỬ VIỆC · `P` = NGÀY NGHỈ VIỆC · `DZ` = Nhóm chức danh · `EA` = Profits Center · `EB` = Cost Center · `EC` = WBS · `ED` = Funds Center · `EY` = Level Payroll 01/2026 · `EZ` = Level sau MYR.
- **Level**: `Level 1` … `Level 8` (từ sheet Allowance Rule + giá trị mẫu `EY9 = Level 8`). Payslip dùng ký hiệu `L6`.

---

## 5. THAM SỐ HỆ THỐNG

### 5.1 Bảng tham số (cột `V` sheet `Payroll structure` — legend cột Q–S)

| Tham số | Giá trị | Dùng ở đâu |
|---|---|---|
| Trần lương đóng **BHXH/BHYT** | **50.600.000** | `INS_SAL_BH` (V3) |
| Trần lương đóng **BHTN** | **106.200.000** | `INS_SAL_UI` (V5) |
| Đơn giá 1 bữa cơm | **45.000** | `MEAL_ALLOW` (V6) |
| Mức miễn thuế PC cơm | **1.200.000** | `MEAL_TAX`/`MEAL_NONTAX` (V7) ⚠️ sample dùng **730.000** |
| Giảm trừ bản thân | **15.500.000** | `PERSONAL_DED` (V8) ⚠️ Payslip mẫu ghi **11.000.000** (cũ) |
| Giảm trừ người phụ thuộc | **6.200.000** /người | `DEPENDENT_DED` (V9) |
| Phí công đoàn | **0,5%** (V10 = 0.005) | `UNION_FEE` |
| **Trần phí công đoàn** | **253.000** (V11) | `UNION_FEE` max |
| BHXH NLĐ | **8%** (V12 = 0.08) | `SI_EMP` |
| BHYT NLĐ | **1,5%** (V13 = 0.015) | `HI_EMP` |
| BHTN NLĐ | **1%** (V14 = 0.01) | `UI_EMP` |
| BHXH Công ty | **17%** (V15 = 0.17) | `SI_CTY` |
| BHTNLĐ-BNN Công ty | **0,5%** (V16 = 0.005) | `TNLD_CTY` |
| BHYT Công ty | **3%** (V17 = 0.03) | `HI_CTY` |
| BHTN Công ty | **1%** (V18 = 0.01) | `UI_CTY` |
| KPCĐ Công ty | **2%** (V19 = 0.02) | `KPCD_CTY` |
| Trích thưởng Du lịch (mốc) | **10.000.000** (V22) ⚠️ công thức sống dùng **6.000.000** | `BONUS_SAVE_TRAVEL` |
| Trần thưởng Tết (trích quỹ) | **15.000.000** (V23) | `BONUS_SAVE_TET` |
| Trần lương ĐANG DÙNG THẬT (BHXH/BHYT/KPCĐ/CĐ) | **46.800.000** | suy ra từ giá trị thật dòng 9 |

**Tổng gánh nặng bảo hiểm**: NLĐ = 8 + 1,5 + 1 = **10,5%**; Công ty = 17 + 0,5 + 3 + 1 = **21,5%** (+ 2% KPCĐ).

**Legend meta (cột Q–S)**:
- `type`: `input` (Excel compute) · `formula` (Compute from formula) · `system`
- Nguồn: `WD API` · `WD API - CTD Payroll` · `CTD HRIS` · `HR input` · `excel compute`
- `tax`: `1` = Include tax · `0` = No-include tax
- `vis`: `#N/A` = Hide in Payslip · `other` = Show in Payslip
- `editable`: `1` = Allow edit after compute · `0` = Can not edit

### 5.2 Thuế TNCN

**Công thức SỐNG (`CK9`)** — đây là ground truth:
```excel
ROUND(
  IF(AND(Quốc tịch="Việt Nam", HĐ="Thử việc", TAXABLE_INC >= 2 000 000), TAXABLE_INC * 10%,
  IF(AND(Quốc tịch="Việt Nam", HĐ="Thử việc", TAXABLE_INC <  2 000 000), 0,
  IF(AND(Quốc tịch="Nước ngoài", HĐ="Thử việc"), TAXABLE_INC * 20%,
     SUMPRODUCT( (TAXABLE_INC > {0;10;30;60;100}*10^6)
               * (TAXABLE_INC - {0;10;30;60;100}*10^6)
               * {0.05;0.05;0.1;0.1;0.05} )
  ))), 0)
```

**Biểu lũy tiến 5 bậc** (dạng IF tương đương ở cột `EW9`, đã được ô `EX9` xác nhận bằng `EW9 = CK9` → **TRUE**):

| Bậc | Thu nhập tính thuế | Thuế suất | Công thức rút gọn |
|---|---|---|---|
| 1 | ≤ 10.000.000 | **5%** | `TAXABLE_INC × 5%` |
| 2 | ≤ 30.000.000 | **10%** | `TAXABLE_INC × 10% − 500.000` |
| 3 | ≤ 60.000.000 | **20%** | `TAXABLE_INC × 20% − 3.500.000` |
| 4 | ≤ 100.000.000 | **30%** | `TAXABLE_INC × 30% − 9.500.000` |
| 5 | > 100.000.000 | **35%** | `TAXABLE_INC × 35% − 14.500.000` |

**Các trường hợp đặc biệt** (`K83` sheet Payroll structure + `CK10`):
- **Thử việc, Việt Nam**: `TAXABLE_INC ≥ 2tr → 10%`; `< 2tr → 0`
- **Thử việc, Nước ngoài**: `20%`
- **Nước ngoài + không có work permit**: `tax = 20%` thu nhập tính thuế
- **Intern**: `> 5tr → tax = 10%`; **nếu có giấy cam kết thuế → tax = 0**
- Ghi chú Q83: *"uyên check lại với Mắt Bão"* → chưa chốt.

⚠️ **Bảng thuế ở sheet `References` MÂU THUẪN & KHÔNG ĐẦY ĐỦ** (chỉ 3/7 dòng có dữ liệu — đây là biểu **7 bậc CŨ**, đừng dùng):

| Tax rate | From | To | Diff_Amount |
|---|---|---|---|
| 0.05 | 0 | 5.000.000 | 0 |
| 0.1 | 5.000.000 | 10.000.000 | 250.000 |
| *(trống)* | | | |
| 0.3 | 52.000.000 | 80.000.000 | 5.850.000 |
| *(trống ×3)* | | | |

Sheet References cũng có 1 dòng **code Python** (A22) — khớp với biểu 5 bậc mới:
```python
result = int((cat['ACCESSIBLE_INCOME']>100000000 and cat['ACCESSIBLE_INCOME']*0.35-14500000
          or cat['ACCESSIBLE_INCOME']>60000000  and cat['ACCESSIBLE_INCOME']*0.3-9500000
          or cat['ACCESSIBLE_INCOME']>30000000  and cat['ACCESSIBLE_INCOME']*0.2-3500000
          or cat['ACCESSIBLE_INCOME']>10000000  and cat['ACCESSIBLE_INCOME']*0.1-500000
          or cat['ACCESSIBLE_INCOME']>0         and cat['ACCESSIBLE_INCOME']*0.05
          or 0) + 0.5000001)
```
(Text mô tả ở `K83` ghi *"5%/10%/15%/20%/25%"* — **SAI**, mâu thuẫn với chính công thức của nó. Tin công thức, không tin text.)

### 5.3 Lương tối thiểu vùng
**KHÔNG CÓ TRONG EXCEL.**

---

## 6. PAYSLIP TEMPLATE

Tiêu đề: `PHIẾU LƯƠNG THÁNG MM/yyyy / PAYSLIP MM/yyyy` — kỳ: **`(Từ ngày 21/[M-1] đến ngày 20/[M])`** (công thức: `DATE(YEAR(J1),MONTH(J1)-1,21)` → `DATE(YEAR(J1),MONTH(J1),20)`).

**A. THÔNG TIN NHÂN VIÊN**: Tên nhân viên · Mã số nhân viên · Chức danh · Phòng ban · Số người phụ thuộc · Loại HĐ · **Cấp bậc** (note J6: *"chỉnh ngạch thành cấp bậc"*, mẫu `L6`)

**B. THÔNG TIN NGÀY CÔNG** (11 dòng, đánh số `[0]`–`[10]`):
`[0]` Ngày công chuẩn · `[1]` Ngày làm việc thực tế · `[2]` **Ngày làm việc hưởng 70% lương** ⚠️ (KHÔNG có CODE tương ứng trong Payroll structure) · `[3]` Ngày nghỉ lễ, tết · `[4]` Ngày nghỉ phép · `[5]` Ngày nghỉ bù · `[6]` Ngày nghỉ chế độ (ma chay, hiếu hỉ) · `[7]` **Ngày nghỉ ốm Công ty** (note: *"thêm"*) · `[8]` Ngày nghỉ không hưởng lương · `[9]` Ngày chế độ BHXH · Ngày công điều chỉnh · Ngày phép tồn · `[10]` **Tổng số ngày làm việc hưởng lương** = `G13+G14+G15+G16+G17+G19+G18`

**C. LƯƠNG, PHỤ CẤP & TRỢ CẤP**:
- Lương thử việc · Lương chính thức · **Lương bình quân ngày** = `ROUND(Lương chính thức / Ngày công chuẩn, 0)` (note J30: *"hour nhưng cthuc đang là day"*) · Phụ cấp trách nhiệm · `[11]` Tổng lương thực tế trong tháng
- **Phụ cấp** (2 cột: Không chịu thuế / Chịu thuế): `[12]` Cơm · `[13]` Điện thoại · `[14]` NL/Xăng · `[15]` Đi lại · `[16]` Nhà ở · `[17]` Khác → `[18]` **Tổng tiền phụ cấp = [12+13+14+15+16+17]**
- **Tăng ca** (3 cột: Số giờ / Không chịu thuế / Chịu thuế): `[19]` ngày thường · `[20]` ngày nghỉ · `[21]` ngày lễ · `[22]` đêm ngày thường · `[23]` đêm ngày nghỉ · `[24]` đêm ngày lễ → `[25]` **Tổng tiền tăng ca = [19+20+21+22+23+24]**
- **Thưởng**: `[26]` Lương tháng 13 · `[27]` Thưởng KPIs · `[28]` Thưởng Lễ/Tết · `[29]` Thưởng văn phòng · `[30]` Thưởng công trình · `[31]` Thưởng khác → `[32]` **Tổng tiền thưởng**
- **Trợ cấp**: `[33]` Trợ cấp nghỉ việc · `[34]` Trợ cấp khác · `[35]` Teambuilding (note: *"Nhuận bút (nếu có)"*) · `[36]` Thưởng giới thiệu ứng viên · `[37]` Hỗ trợ khác (BHSK người thân cty tài trợ) → `[38]` **Tổng trợ cấp/hỗ trợ**
- **Điều chỉnh trước thuế**: `[39]` Điều chỉnh cộng · `[40]` Điều chỉnh trừ
- `[41]` **Tổng thu nhập = [11+18+25+32+38+39+40]** (chia 2 cột: không chịu thuế / chịu thuế)

**D. CÁC KHOẢN KHẤU TRỪ**:
- `[42]` BHXH-NV 8% · `[43]` BHYT-NV 1.5% · `[44]` BHTN-NV 1% · `[45]` Điều chỉnh BHXH → `[46]` **Tổng trích đóng BHXH-NV = [42+43+44+45]**
- `[47]` Giảm trừ bản thân · `[48]` Giảm trừ gia cảnh → `[49]` **Tổng các khoản khấu trừ = [46+47+48]**
- **PIT**: `[50]` Thu nhập tính thuế · `[51]` Thuế TNCN · `[52]` Điều chỉnh Thuế TNCN · `[53]` Tổng thuế TNCN đã khấu trừ
- **Giảm trừ sau thuế**: `[54]` **Phí công đoàn (1%)** ⚠️ (Structure & sample đều ghi **0,5%**) · `[55]` Thu hộ BH Bảo Việt · `[56]` Quyết toán thuế TNCN năm trước · `[57]` Khoản trừ sau thuế khác · `[58]` Khoản trừ sau thuế khác (BHSK người thân) `= [37]` → `[59]` **Tổng các khoản trừ sau thuế = [54+55+56+57+58]**

**E. THU NHẬP THỰC NHẬN & ĐIỀU CHỈNH SAU THUẾ**:
- `[60]` Chế độ BHXH · `[61]` Quyết toán thuế TNCN năm trước · `[62]` Trợ cấp thôi việc · `[63]` Các khoản cộng sau thuế khác → `[64]` **Tổng các khoản cộng sau thuế = [60+61+62+63]**
- `[65]` ★ **Tiền lương thực nhận / Net salary = [41 − 46 − 53 − 59 + 64]**
- `[66]` Lương tạm ứng Đợt 1 · `[67]` Lương thưởng Đợt 2
- Footer: *"Cảm ơn những đóng góp và nỗ lực của Anh/Chị vào sự phát triển của Công ty."*

**Số liệu mẫu payslip** (Lê Văn Biên, mã 006720, L6, Chính thức, 0 NPT): Công chuẩn 26 · Ngày làm việc thực tế 26 · Lương chính thức 20.000.000 · Lương bình quân ngày 769.231 · PC cơm non-tax **730.000** / taxable **2.780.000** · PC điện thoại non-tax 800.000 · Trợ cấp khác 992.000 · Tổng thu nhập 25.302.000 (non-tax 1.530.000 + chịu thuế 23.772.000) · BHXH 3.744.000 · BHYT 702.000 · BHTN **0** · Giảm trừ bản thân **11.000.000** · Thu nhập tính thuế 3.880.000 · PIT 572.000 · **Net = 20.284.000**.
⚠️ Payslip mẫu đang dùng tham số **CŨ** (giảm trừ 11tr, cơm miễn 730k) — không khớp Payroll structure (15,5tr / 1,2tr).

---

## 7. SYS FLOW_PAYROLL — "LUỒNG TẠO VÀ XỬ LÝ PAYSLIP (recommendation)"

**Bước 1 — Kéo dữ liệu mỗi tháng từ Workday & CTD HRIS**
- Định kỳ mỗi tháng **ngày chốt công (20)** / thủ công kéo dữ liệu từ Workday và CTD HRIS về **CTD Payroll Engine**:
  - CTD HRIS: `Employees' expenses`
  - Workday: `Employee information`, `Compensation plans`, `Time Tracking and Absences`
- Tại Payroll Engine: tính Allowance dựa theo Onboard, Offboard, Enter times…
- ➜ **Cần HR cung cấp các trường hợp loại trừ, phát sinh** (VD: Tiền cơm OT, trường hợp không được hưởng phụ cấp dựa trên Onboard/Offboard…)

**Bước 2 — Kiểm tra thông tin và tính Payslip cho toàn bộ NV**
- HR review Allowance, Enter times, Expenses → `Download <Allowances/Enter times/Expense> report` (Excel) để kiểm tra
- ➜ **(1) Cần HR cung cấp/xác nhận template report tương ứng từng object**
- `Mass approve` sau khi review chính xác
- Tạo **Payroll period**, mặc định **25 tháng trước → 25 tháng hiện tại**
- `Generate Payslips` trong Payroll period view
- ➜ **Cần HR cung cấp/xác nhận cấu trúc lương và các công thức lương**

**Bước 3 — Upload để chỉnh các ad-hoc cases**
- `Download payroll report` ➜ **(2) Cần HR cung cấp/xác nhận Payroll template**
- `Update payslip` → pop-up cho HR upload file Payroll với các mục cần thay đổi
- `Re-compute payslips` → reset payslip theo cấu trúc lương hệ thống

**Bước 4 — Xác nhận và gửi payslip**
- `Approved` → xác nhận và **khoá thay đổi** toàn bộ Payslip
- `Push to WD` → đẩy Payslip vào **SFTP** để đưa lên Workday
- ➜ **(3) Cần HR cung cấp/xác nhận Payslip template**
- Các template cần đẩy lên WD: **(1), (2), (3)**

**Bước 5 — Lưu ý (state machine)**
- **Payroll period**: `New → Computed → Done → Pushed → Cancel`
  - `New`: nút `Compute Payslip`
  - `Computed`: nút `Download payroll`, `Update payslip`, `Re-compute payslips`, `Approved`
  - `Done`: nút `Push to WD`
  - Nút `Cancel` ở các trạng thái `New` / `Computed` / `Done`
- **Object Allowance / Enter times / Expense**: `Draft → Approved → Archived`
  - `Draft`: nút `Approved`, `Archived`
  - `Archived`: nút `Unarchived`
  - Nút `Print report` ở trạng thái `Draft` / `Approved`

---

## 8. PAYROLL MAR 2026 — bảng lương thật

### 8.1 Cấu trúc header (bắt buộc phải parse đúng)

| Dòng | Nội dung |
|---|---|
| **1–2** | Công chuẩn VP `F1 = NETWORKDAYS.INTL(H1,H2,1) + NETWORKDAYS.INTL(H1,H2,"1111101")/2` (ngày thường + **thứ 7 tính nửa ngày**) · Công chuẩn CT `F2 = NETWORKDAYS.INTL(H1,H2,11)` (**chỉ trừ Chủ nhật**) · `H1`=Ngày bắt đầu, `H2`=Ngày kết thúc (`DD/MM/YYYY`, đang để placeholder) · `U2 = U9*0.17 = 8.602.000` (ô check) |
| **3** | Tiêu đề `CTD BẢNG LƯƠNG THÁNG MM/YYYY` + vài ô check tổng |
| **4** | **Dòng TỔNG** (`SUBTOTAL(9, …)` / giá trị tổng cột) — KHÔNG phải dữ liệu nhân viên |
| **5** | **Header nhóm cấp 1** (merged): STT · VP/CT · MÃ KIỂM TOÁN · MÃ SỐ NHÂN VIÊN · TÊN NHÂN VIÊN · Quốc tịch · MÃ WSB PHÒNG BAN · TÊN PHÒNG BAN · BỘ PHẬN · CHỨC DANH · NGẠCH-BẬC · LOẠI HỢP ĐỒNG · NGÀY VÀO LÀM · NGÀY KẾT THÚC THỬ VIỆC · NGÀY NGHỈ VIỆC · MỨC LƯƠNG HỢP ĐỒNG · MỨC LƯƠNG ĐÓNG BHXH/BHYT · MỨC LƯƠNG ĐÓNG BHTN · CÔNG CHUẨN · CÁC NGÀY CÔNG TRONG THÁNG · LƯƠNG THỰC TẾ · PHỤ CẤP TÍNH THUẾ · PHỤ CẤP KHÔNG TÍNH THUẾ · TĂNG CA · CÁC LOẠI THƯỞNG · … · LƯƠNG THỰC NHẬN · LƯƠNG THỰC CHI · CHI PHÍ CÔNG TY · TRÍCH THƯỞNG HÀNG THÁNG · Check budget |
| **6** | **Header nhóm cấp 2** (tên cột chi tiết tiếng Việt): `Q6`=Lương thử việc, `R6`=Lương chính thức, `S6`=Phụ cấp Trách nhiệm, `T6`=Tổng lương trên HĐLĐ, `X6`=Ngày làm việc thực tế-Thử việc, `Y6`=Ngày làm việc thực tế-Sau thử việc, `Z6`=Nghỉ phép năm, `AA6`=Ngày nghỉ lễ tết, `AB6`=Ngày nghỉ bù, `AC6`=Nghỉ có hưởng lương, `AD6`=Ngày nghỉ chế độ (ma chay, hiếu hỉ), `AE6`=Ngày nghỉ không lương, `AF6`=Ngày chế độ BHXH, `AG6`=Ngày công bổ sung, `AH6`=Ngày phép tồn, `AI6`=Tổng số ngày làm việc hưởng lương, … `CZ6`=VND, `DA6`=USD, `DB6`=VND |
| **7** | **`type`** — `=VLOOKUP(<CODE dòng 8>, 'Payroll structure'!A:E, 5, FALSE)` → trả `input` / `formula` / `system` |
| **8** | ★ **DÒNG MÃ CODE** — `Q8=PROB_SAL`, `R8=BASIC_SAL`, … `CZ8=NET_PAY`, `DB8=NET_PAY_HOME`, `EE8=BUDGET_SAVE` |
| **9** | ★ **DỮ LIỆU BẮT ĐẦU** — dòng nhân viên đầu tiên (chứa công thức Excel sống) |
| **10** | Dòng **ghi chú/diễn giải business rule** cho từng cột (nguồn vàng: OT 200% CN, prorata <14 ngày, quy tắc cơm, miễn BHXH ≥14 ngày…) |
| **11** | Dòng đối chiếu — `=IF(<type>="formula", VLOOKUP(<CODE>, 'Payroll structure'!A:K, 11, FALSE), "")` → in ra mô tả công thức bằng chữ |

### 8.2 Số dòng nhân viên thật

**Trong file dump này chỉ có ĐÚNG 1 dòng nhân viên: dòng 9.** (Đã kiểm bằng scan toàn bộ section — không có dòng 12+ nào chứa dữ liệu; chỉ còn 1 ô rác `C143`.) Đây là **dòng mẫu đã ẩn danh** (cột `F` TÊN NHÂN VIÊN trống, `E` MÃ SỐ NV trống, `M9="Chính thức"`, `C9="VP301"`).

⚠️ Kết luận: **file này KHÔNG chứa 4.000+ dòng bảng lương thật** — nó là **template + 1 dòng mẫu ground-truth**. (Sheet `General` cho biết roster thật ở Workday: `Get_Workers` = 4.179 rows.)

### 8.3 Ground-truth dòng 9 — dùng để test engine (đã verify tay, khớp 100%)

| CODE | Cột | Giá trị |
|---|---|---|
| LOẠI HĐ | M9 | `Chính thức` |
| NGÀY VÀO LÀM | N9 | `37646` (serial) |
| `PROB_SAL` | Q9 | 0 |
| `BASIC_SAL` | R9 | **200.000.000** |
| `RESP_SAL` | S9 | *(trống → 0)* |
| `CONTRACT_TOTAL` | T9 | **200.000.000** |
| `INS_SAL_BH` | U9 | **50.600.000** |
| `INS_SAL_UI` | V9 | **106.200.000** |
| `STD_DAYS` | W9 | **22** |
| `PROB_DAYS` | X9 | 0 |
| `OFFICIAL_DAYS` | Y9 | **19,5** |
| `HOLIDAY_DAYS` | AA9 | **2,5** |
| `PAID_DAYS` | AI9 | **22** |
| `OFFICIAL_EARNED` | AK9 | **200.000.000** |
| `EARNED_SAL` | AN9 | **200.000.000** |
| `FUEL_ALLOW` | AQ9 | 25.000.000 |
| `MEAL_NONTAX` | AU9 | **−990.000** (âm!) |
| `PHONE_NONTAX` | AV9 | 1.000.000 |
| `GROSS` | BW9 | **225.010.000** |
| `TAXABLE_GROSS` | BX9 | **225.000.000** |
| `SI_EMP` | BY9 | **3.744.000** (= 46,8tr × 8%) |
| `HI_EMP` | CA9 | **702.000** (= 46,8tr × 1,5%) |
| `UI_EMP` | CC9 | **1.062.000** (= 106,2tr × 1%) |
| `TOTAL_INS` | CE9 | **5.508.000** |
| `PERSONAL_DED` | CF9 | **15.500.000** |
| `DEPENDENT_CNT` | CG9 | **3** |
| `DEPENDENT_DED` | CH9 | **18.600.000** |
| `TOTAL_DED` | CI9 | **34.100.000** |
| `TAXABLE_INC` | CJ9 | **185.392.000** |
| `PIT` | CK9 | **50.387.200** (= 185.392.000 × 35% − 14.500.000) |
| `TOTAL_PIT` | CM9 | **50.387.200** |
| `NET_INCOME` | CN9 | **169.114.800** |
| `PIT_SETTLE` | CO9 | 21.049.361 |
| `UNION_FEE` | CT9 | **234.000** (= 46,8tr × 0,5%) |
| ★ `NET_PAY` | CZ9 | **189.930.161** |
| ★ `NET_PAY_HOME` | DB9 | **189.930.161** |
| `SI_CTY` | DD9 | 7.956.000 |
| `TNLD_CTY` | DF9 | 234.000 |
| `HI_CTY` | DH9 | 1.404.000 |
| `UI_CTY` | DJ9 | 1.062.000 |
| `TOTAL_INS_CTY` | DL9 | **10.656.000** |
| `KPCD_CTY` | DM9 | **936.000** |
| `TOTAL_CTY_COST` | DN9 | **201.522.161** |
| `BONUS_SAVE_TRAVEL` | DS9 | 500.000 |
| `BONUS_SAVE_KPI` | DW9 | 50.000.000 |
| `BONUS_SAVE_13M` | DX9 | 16.666.667 |
| `BONUS_SAVE_TET` | DY9 | 1.250.000 |
| `BUDGET_SAVE` | EE9 | **305.018.667** |
| Check (`EF9`) | EF9 | **0** ✓ (cân) |
| Level | EY9/EZ9 | `Level 8` |

**Cột kết quả (ground-truth để đối chiếu engine)**: `BW` (GROSS) · `BX` (TAXABLE_GROSS) · `CE` (TOTAL_INS) · `CJ` (TAXABLE_INC) · `CK`/`CM` (PIT) · `CN` (NET_INCOME) · **`CZ` (NET_PAY)** · **`DB` (NET_PAY_HOME)** · `DL`/`DM`/`DN` (chi phí công ty) · `EE` (BUDGET_SAVE).
**Cột tự-kiểm sẵn có trong Excel**: `EF9` (`SUM(AN:BV) − CE − CM + SUM(CO:CS) − SUM(CT:CY) − CZ` phải = 0) và `EX9` (`EW9 = CK9` — kiểm biểu thuế IF vs SUMPRODUCT).

---

## 9. HANDOVER PREREQUISITES

### 9.1 Knowledge Capture — 14 item HR/IT yêu cầu dev hiện tại bàn giao

| # | Item | Why | Priority | Weight |
|---|---|---|---|---|
| 1 | Codebase walkthrough (recorded) / tech stack / FE / BE | Only source of truth right now | 🔴 High | 3 |
| 2 | Data model / DB schema | Core of any payroll engine | 🔴 High | 3 |
| 3 | Infrastructure (DB/App/Source code storage mỗi env) | — | 🔴 High | 3 |
| 4 | As-is / To-be flow | To define what is a need and the ultimate goal | 🔴 High | 3 |
| 5 | **Business logic mapping (Excel → code)** | **Most critical, hardest to reverse-engineer** | 🔴 High | 3 |
| 6 | Edge cases & known bugs | Hidden landmines | 🟡 Medium | 2 |
| 7 | **Assumption Log** | Rules assumed during build, để review & làm chuẩn test/GTM | 🔴 High | 3 |
| 8 | Current deployment setup | Avoid "works on my machine" | 🟡 Medium | 2 |
| 9 | Any hardcoded CTD-specific configs | Must be separated before Phase 2 | 🟡 Medium | 2 |
| 10 | **Payroll calculation formula walkthrough (step by step, not just code)** | Code alone doesn't tell the intent — **especially for PIT & BHXH** | 🔴 High | 3 |
| 11 | External dependencies / 3rd party integrations | Must know before handover | 🔴 High | 3 |
| 12 | Access & credentials handover (DB, server, env files) | Often forgotten until it blocks the new team | 🟡 Medium | 2 |
| 13 | User manual / how CTD currently uses the system | — | 🟡 Medium | 2 |
| 14 | Environment setup guide | — | 🟡 Medium | 2 |

`Avg score = avg(assessment point × weight of priority)`. **Toàn bộ cột Score đang `#VALUE!` → CHƯA CHẤM ĐIỂM.**

### 9.2 Gap Analysis — 9 gap HR/IT tự nhận

| # | Gap | Impact | Action | PIC |
|---|---|---|---|---|
| 1 | **No BA** | Requirements unclear | Assign 1 BA to reverse-document Phase 1 | — |
| 2 | **No technical specs** | Hard to handover and maintain | (a) document current tech stack, (b) Tech Lead reviews & decides what stays vs gets replaced | — |
| 3 | **No test suite** | Can't safely refactor | **Write regression tests before touching code** | — |
| 4 | No product spec for Phase 2 | Can't scope GTM | Run a discovery sprint with stakeholders | — |
| 5 | **1 dev bus factor** | Immediate risk | Parallel onboard a 2nd dev during knowledge transfer | — |
| 6 | No separation of CTD-specific logic | Blocks Phase 2 | Identify & modularize configs | — |
| 7 | No version control discipline | Không có branching strategy / commit standards → dev thứ 2 onboard sẽ conflict ngay | *(chưa có action)* — *"my assumption so far, can confirm w Hau"* | — |
| 8 | **No staging/UAT environment** | Payroll **cannot** be tested in production — staging là **non-negotiable** | Tech lead works w Devs to prep testing env | — |
| 9 | **No error handling / audit log** | *"When payroll output is wrong, how does anyone know?"* — cần logging trước Phase 2 | *(chưa có action)* | — |

**Cột PIC (E) và timeline: TRỐNG HOÀN TOÀN** — mà chính `Assessment guide` yêu cầu *"Every gap must have a named owner and timeline"* để pass Section 3.

### 9.3 Bối cảnh dự án (sheet `General`)
- Project: **Payroll CTD** · Sponsor: CTD · PM: **Thoai, Dao Duy** · Tenant hiện tại: **UAT** · Trạng thái: **🟠 AMBER**
- Start `46204` / End `46251` (Excel serial ≈ 03/07/2026 → 19/08/2026)
- **STREAM-WISE STATUS SUMMARY: 4 dòng (Functional/Data/Integrations/Infrastructure) — TẤT CẢ ĐỀU `#DIV/0!` (chưa điền)**
- **RISK & ISSUES LOG: TRỐNG**
- **SFTP / UAT / PROD URL + access info: TRỐNG**
- **Workday APIs & RaaS — 21 endpoint**, trong đó:
  - 🟢 Synced: `Get_Workers` (bulk 4.179 rows / +comp 8.581 / +dependents 9.154 / +events 390.880), `Get_Organizations` (1.975), `Get_Holiday_Calendars` (20), `Get_Time_Requests` (106), `CTD_-_Compensation_Changes_Report` (10.692), `Compensation_Profile_-_Allowances` (4.157)
  - 🟡 Stale: `CTD_-_Monthly_Attendance_Report_-_Copy` (6.935 rows, timed out on wide-range re-sync) — **nguồn Attendance/OT hours/leave days**
  - 🔴 **Blocked**: `Get_Calculated_Time_Blocks` (security domain not granted — *"Would give OT actual hours"*) · `CTD_-_List_Detail_of_Work_History` (tenant report permission) · `All_Worker_Time_Off` (every param rejected — *"Would give time-off/leave data"*)
  - 🟠 Waiting: `CTD_-_Time_Off_Balance_For_Payout_-_Copy` (needs Business_Object value from user)
  - 🔍 Verified to exist, not implemented: `Get_Time_Off_Plan_Balances` (SOAP Absence_Management v44.1/v46.1)
  - ⚫ Not found: `CTD - Night/Sunday Meal & Regular Audit`, `CTD - Absence Report`
  - 📝 `14× write operations` (HireEmployee, ChangeJob… `internal/workday/write.go`) — coded, chưa wire vào REST endpoint

---

## 10. TỔNG HỢP MÂU THUẪN / THIẾU — phải chốt với HR trước khi code

| # | Vấn đề | Structure (to-be) | Sample/Thực tế (as-is) |
|---|---|---|---|
| 1 | **Trần lương đóng BHXH/BHYT** | `INS_SAL_BH` khai 50.600.000 nhưng công thức `SI_EMP`/`HI_EMP`/`SI_CTY`/`HI_CTY` dùng **46.800.000** | Giá trị thật dòng 9 = **46.800.000** |
| 2 | **Base tính bảo hiểm** | `MIN(BASIC_SAL, trần)` | `MIN(CONTRACT_TOTAL, trần)` |
| 3 | **Mức miễn thuế PC cơm** | **1.200.000** | **730.000** (payslip + note) |
| 4 | **Giảm trừ bản thân** | **15.500.000** | Payslip mẫu **11.000.000** |
| 5 | **Phí công đoàn** | `BASIC_SAL × 0,5%`, không trần | `INS_SAL_BH × 0,5%`, **max 253.000**; Payslip ghi **1%** |
| 6 | **KPCĐ 2%** | `BASIC_SAL × 2%` | `INS_SAL_BH × 2%`; *"Thử việc = 0?"* chưa chốt |
| 7 | **TOTAL_CTY_COST** | `GROSS + TOTAL_INS_CTY + KPCD_CTY` | `NET_PAY + TOTAL_INS_CTY + KPCD_CTY` |
| 8 | **PAID_DAYS** | có cộng `SI_DAYS` + `ADJ_DAYS` | **không** cộng; nhưng có `AC`/`AD` chưa có CODE |
| 9 | **GROSS** | `… + ADJ_PLUS − ADJ_MINUS` | `SUM(AN:BU)` → **ADJ_MINUS bị CỘNG** |
| 10 | **TAXABLE_GROSS / TAXABLE_INC** | không trừ `CHARITY_DED` | `BX9` **có** trừ `CHARITY_DED` và `EARNED_PAID_LEAVE` |
| 11 | **EARNED_SAL** | 3 thành phần | 4 thành phần (**+ `EARNED_PAID_LEAVE`**) |
| 12 | **BONUS_SAVE_TRAVEL** | `10tr/12` | `6.000.000/12 = 500.000` |
| 13 | **Kỳ lương** | Sys flow: **25 → 25** | Time Tracking Rule + Payslip: **21 → 20** |
| 14 | **Biểu thuế** | References: bảng 7 bậc **cũ, thiếu 4 dòng** | Công thức sống: **5 bậc (5/10/20/30/35%)** — dùng cái này |
| 15 | Mã CODE lỗi | `CONTRACT_TOTAL` & `RESP_EARNED` tham chiếu `[RESPONSIBILITY_ALLOW]` — **CODE không tồn tại** (đúng ra là `RESP_SAL`); `PHONE_NONTAX` = `[PHONE_ALLOW` — **thiếu dấu `]`** | |
| 16 | Thiếu hoàn toàn | Hệ số OT (ngày thường/đêm), công thức giờ→tiền OT · `ACTUAL_DAYS` formula · `MEALS_TOTAL` formula · 5 công thức `BONUS_SAVE_*` ghi *"missing fomula"* · Lương tối thiểu vùng · Danh mục phòng ban/chức danh/ngạch-bậc · 5/6 dòng Exception phụ cấp · Dòng payslip *"Ngày làm việc hưởng 70% lương"* không có CODE | |
agentId: aebea3e3aad391828 (use SendMessage with to: 'aebea3e3aad391828', summary: '<5-10 word recap>' to continue this agent)
<usage>subagent_tokens: 143147
tool_uses: 8
duration_ms: 472810</usage>