# 001-answers — Payroll CTD/Unicons

> Bộ trả lời cho `001-questions.html`. Mỗi block = 1 field-id, mang sang BR thành clause cùng id.
> `provenance` hợp lệ: `raw:<file>` (rút được từ tài liệu) · `user` (người chốt) · `lens:<tên>` (chuyên gia điền thay).
> `verified: false` = **giả định đang gánh** → phải hiện ở bảng đầu `br/BR.md`.

---

## Q1 — S5.2 · Lớp công thức nào là chuẩn: "to-be" (Payroll structure) hay "as-is" (công thức Excel sống)?

**Bối cảnh:** Excel bàn giao có 2 lớp công thức và **chính HR đã chấm lệch (`Matched? = N`) ở 10 field**: `PAID_DAYS`, `CONTRACT_TOTAL`, `INS_SAL_BH`, `INS_SAL_UI`, `TAXABLE_GROSS`, `PERSONAL_DED`, `TAXABLE_INC`, `UNION_FEE`, `KPCD_CTY`, `TOTAL_CTY_COST`.

answer: **CHỌN LỚP "AS-IS" (công thức Excel sống dòng 9) làm chuẩn cho engine lô đầu.** Lý do dứt khoát: as-is là lớp DUY NHẤT kiểm chứng được bằng máy ngay hôm nay — tôi đã tái lập tay toàn bộ chuỗi dòng 9 và nó khớp 100%, kể cả 2 ô tự-kiểm mà chính Excel mang sẵn (`EF9 = 0` cân sổ, `EX9 = TRUE` biểu thuế IF ≡ SUMPRODUCT). Lớp to-be không có một con số kết quả nào để đối chiếu, và ở 4/10 field lệch nó cho ra số SAI so với bảng lương thật (vd `SI_EMP` to-be = `MIN(BASIC_SAL, 46,8tr)×8%` với `TNLD_CTY` to-be = `MIN(BASIC_SAL, 106,2tr)×0,5%` → 531.000, trong khi thật là 234.000). HR sẽ không tin engine nào không ra đúng bảng lương họ đang trả.
Chốt từng field lệch — engine code theo cột phải:
| Field | Engine dùng (as-is) | Bỏ (to-be) |
|---|---|---|
| `PAID_DAYS` | `IF(HĐ=Chính thức, OFFICIAL_DAYS, PROB_DAYS) + PAID_LEAVE + HOLIDAY + COMP + AC + AD` (AC = nghỉ có hưởng lương, AD = ma chay/hiếu hỉ — **cấp CODE mới `PAID_OTHER_DAYS`, `BEREAVE_DAYS`**); KHÔNG cộng `SI_DAYS`, `ADJ_DAYS` | bản cộng SI_DAYS + ADJ_DAYS |
| `CONTRACT_TOTAL` | `IF(Chính thức, BASIC_SAL + RESP_SAL, PROB_SAL)` | `BASIC_SAL + [RESPONSIBILITY_ALLOW]` (mã không tồn tại) |
| `INS_SAL_BH` | `IF(Chính thức, MIN(CONTRACT_TOTAL, **46.800.000**), 0)` — xem Q9 | `MIN(BASIC_SAL, 50.600.000)` |
| `INS_SAL_UI` | `IF(Chính thức, MIN(CONTRACT_TOTAL, 106.200.000), 0)`; expat → 0 | `MIN(BASIC_SAL, 106.200.000)` |
| `EARNED_SAL` | `ROUND(PROB_EARNED + OFFICIAL_EARNED + RESP_EARNED + EARNED_PAID_LEAVE, 0)` — **4 thành phần** | 3 thành phần |
| `GROSS` | `SUM(EARNED_SAL … ADJ_MINUS)` → **`ADJ_MINUS` được CỘNG** (tức HR nhập số ÂM khi muốn trừ; giữ nguyên, ghi rõ trong UI: "nhập số âm để trừ") | `… + ADJ_PLUS − ADJ_MINUS` |
| `TAXABLE_GROSS` | `= GROSS − (mọi khoản non-tax) − SEVER_ALLOW − SI_BENEFIT − BONUS_TRAVEL − CHARITY_DED − EARNED_PAID_LEAVE` (**có** trừ từ thiện và lương phép tồn) | bản không trừ 2 khoản đó |
| `TAXABLE_INC` | `MAX(0, TAXABLE_GROSS − TOTAL_INS − TOTAL_DED)` (từ thiện đã bị trừ ở TAXABLE_GROSS rồi → **không trừ lần 2**) | bản trừ từ thiện lần nữa |
| `UNION_FEE` | `MIN(INS_SAL_BH × 0,5%, 253.000)` — dòng 9 ra 234.000 = 46,8tr × 0,5% ✓ | `BASIC_SAL × 0,5%` không trần (= 1.000.000 ✗) |
| `KPCD_CTY` | `INS_SAL_BH × 2%` → 936.000 ✓ | `BASIC_SAL × 2%` = 4.000.000 ✗ |
| `TNLD_CTY` | `INS_SAL_BH × 0,5%` (trần 46,8tr!) → 234.000 ✓ | `MIN(BASIC_SAL, 106,2tr) × 0,5%` = 531.000 ✗ |
| `TOTAL_CTY_COST` | `NET_PAY + TOTAL_INS_CTY + KPCD_CTY` → 201.522.161 ✓ | `GROSS + …` = 236.602.000 ✗ |
| `BONUS_SAVE_TRAVEL` | `6.000.000/12 = 500.000` ✓ | `10.000.000/12` ✗ |
| `PIT` | biểu **5 bậc** 5/10/20/30/35% + case thử việc (VN ≥2tr → 10%, <2tr → 0; expat → 20%) | bảng 7 bậc cũ ở sheet References — **vứt** |
Hai thứ to-be ĐÚNG hơn as-is và giữ lại (vì dòng 9 xác nhận): `PERSONAL_DED = 15.500.000` (CF9) và `DEPENDENT_DED = 6.200.000/người` (CH9 = 3 × 6,2tr = 18.600.000). To-be còn lại được lưu trong `params.json` dưới flag `formula_layer: "as_is" | "to_be"` — **một chỗ duy nhất**, đổi 1 dòng là chạy lớp kia khi HR chốt ngược lại. Mọi field to-be lệch được ghi vào `docs/DELTA-as-is-vs-to-be.md` để HR ký.
provenance: raw:ANALYSIS-excel-params.md (§0 bảng Matched?, §1.18 chuỗi phụ thuộc, §8.3 ground-truth dòng 9, §10 bảng 16 mâu thuẫn) · lens:payroll-expert (nguyên tắc "engine mới phải re-produce bảng lương đang chạy trước khi được phép sửa nó")
verified: true

---

## Q2 — S2.1 · Tập người dùng lô đầu

PRD v2.1 có 6 nhóm (Admin, HR C&B, thư ký công trường, CHT, trưởng bộ phận, lãnh đạo). PRD v3.0 nói **chỉ** HR Admin + C&B, không có tài khoản cho nhân viên/trưởng bộ phận.

answer: **Lô đầu: MỘT vai duy nhất — HR C&B (full quyền), KHÔNG có đăng nhập.** Theo PRD v3.0 §3 ("Hệ thống chỉ dành cho HR Admin và C&B Staff"), vì (a) v3.0 là bản mới hơn và là bản duy nhất mô tả đúng phạm vi lõi tính lương, (b) toàn bộ 6 nhóm của v2.1 chỉ có nghĩa khi đã có Azure AD SSO + Teams Bot + workflow duyệt — cả 3 đều bị hoãn ở lô đầu (Q3), (c) nhóm thư ký/CHT/lãnh đạo tiêu thụ ngày công và dashboard, không tiêu thụ engine — không chặn lô đầu.
Cụ thể: app local chạy `http://localhost:8000`, không auth, không session, không user table. Nhưng **model quyền được đặt sẵn 1 chỗ**: mọi handler đi qua `require(perm)` với `CURRENT_ROLE = "hr_cb"` hardcode trong `app/auth.py` (~15 dòng) và enum quyền theo đúng v2.1 §3: `view · edit · export · lock_period · approve_on_behalf`, cộng `mask_money` (thư ký/CHT tuyệt đối không thấy tiền). Khi nối Azure AD, chỉ thay hàm `current_user()` — không đụng handler. Không build màn quản trị user, không build RBAC DB ở lô đầu.
provenance: raw:ANALYSIS-docx-specs.md (S2.1 CONFLICT, S2.2, S9.1 item 2) · assumed (bỏ auth ở lô đầu là ràng buộc thi công local, không có trong docs)
verified: false

---

## Q3 — S6.1 · Phạm vi tích hợp lô đầu

v2.1: chỉ Workday. v3.0: Workday + SAP + Ngân hàng (HSBC/Citibank). Thực trạng: 3 API Workday quan trọng nhất (`Get_Calculated_Time_Blocks` = giờ OT thật, `All_Worker_Time_Off` = ngày nghỉ) **đang bị chặn quyền**.

answer: **Lô đầu: KHÔNG tích hợp gì cả. Zero network call.** Engine đọc dữ liệu vào từ **file trong repo** (`data/inputs/<period>/employees.json` — 1 record = 1 dòng bảng lương, đúng 126 CODE). Đây không phải né tránh: `Get_Calculated_Time_Blocks` (giờ OT thật) và `All_Worker_Time_Off` (ngày nghỉ) đang 🔴 **Blocked** vì chưa cấp security domain — tức 2 input sống còn của engine hiện KHÔNG lấy được qua API dù có code. Viết client Workday bây giờ = code chết không test được.
Ranh giới adapter — **1 file, 1 interface, 4 hàm**, `app/adapters.py`:
```
fetch_employees(period) -> list[dict]     # lô đầu: đọc JSON | sau: Workday Get_Workers
fetch_timesheet(period) -> list[dict]     # lô đầu: đọc JSON | sau: CTD_-_Monthly_Attendance_Report (🟡 stale) + Get_Calculated_Time_Blocks (🔴 blocked)
push_payslip(period, rows) -> None        # lô đầu: ghi PDF-less HTML + JSON vào out/ | sau: SFTP → Workday
export_bank_file(period, rows) -> Path    # lô đầu: ghi CSV | sau: template HSBC/Citibank
```
Mọi thứ khác của engine gọi 4 hàm này, không gọi gì khác. Thứ tự nối lại về sau (khi có credential): **Workday inbound → Payslip outbound → Bank file → SAP**. SAP/Bank/Teams/Azure AD/multi-tenant = **hoãn**, không viết stub rỗng cho chúng (YAGNI) — chỉ ghi vào `docs/DEFERRED.md` kèm lý do chặn.
provenance: raw:ANALYSIS-excel-params.md (§9.3 — 3 API blocked, 1 stale) · raw:ANALYSIS-docx-specs.md (S6.1 CONFLICT v2.1 vs v3.0) · assumed (ranh giới 4-hàm là quyết định thi công)
verified: false

---

## Q4 — S4.1 · Hệ số OT và công thức quy giờ OT → tiền

**Không nguồn nào có**: hệ số OT ngày thường (luật VN 150%), OT ban đêm (+30%), công thức từ số giờ ra tiền. Chỉ có: Chủ nhật 200%, Lễ/Tết "trả thêm 100% + 2 ngày nghỉ bù", "một số trường hợp 300% theo danh sách" (không có danh sách). Excel để OT là **số tiền input**, không tính từ giờ.

answer: **GIỮ ĐÚNG NGUỒN: OT vào engine là SỐ TIỀN INPUT (`OT_TAX`, `OT_NONTAX`), KHÔNG tự chế công thức giờ → tiền.** Tuyệt đối không bịa hệ số 150%/300%/+30% — tự chế nghĩa là engine sẽ ra số KHÁC bảng lương thật ngay ở nhân viên đầu tiên có OT, và sai số đó lẫn vào PIT + BHXH + NET_PAY khiến không ai truy được lỗi ở đâu. Excel nói thẳng: `OT_TAX`/`OT_NONTAX` type = `input`, không có công thức, và giờ OT thật (`Get_Calculated_Time_Blocks`) hiện còn bị chặn quyền → kể cả muốn tính từ giờ cũng không có giờ mà tính.
Thi công:
1. `OT_TAX`, `OT_NONTAX` = input tiền (đơn vị VND), như dòng 9. Engine chỉ cộng vào GROSS/TAXABLE_GROSS.
2. Mở sẵn **bảng hệ số cấu hình** trong `params.json` → `ot_multipliers`, đã điền những gì tài liệu NÓI THẲNG, để `null` những gì không có, kèm cờ `ot_from_hours: false` (mặc định TẮT):
   `sunday: 2.0` (raw ✓) · `holiday_extra: 1.0` (raw: "trả thêm 100%" — ⚠ chưa rõ tổng 200% hay chỉ +100%, xem dưới) · `holiday_300: null` (raw có nhắc "một số trường hợp 300% theo danh sách" nhưng **danh sách không tồn tại**) · `weekday: null` · `night_extra: null` · Mắt Bão: nhánh hệ số riêng `ot_multipliers_matbao` (v2.1 §5.5 yêu cầu tách).
3. Payslip có 6 dòng OT (thường/nghỉ/lễ × ngày/đêm) + cột "Số giờ" → **lô đầu để cột Số giờ trống, chỉ hiện tiền**. Không fake giờ.
4. Kèm theo, hai thứ OT tài liệu nói rõ mà engine PHẢI ghi nhận (không phải tiền, là NGÀY): làm ngày Lễ/Tết → **+2 ngày nghỉ bù**; Coteccons Day/nghỉ bổ sung/bù trùng ngày nghỉ tuần → **+1 ngày nghỉ bù**. Đây là input cho `COMP_DAYS` kỳ sau, không phải tiền kỳ này.
**3 câu phải hỏi HR trước khi bật `ot_from_hours`**: (a) "trả thêm 100%" = tổng 200% hay chỉ +100% cộng trên công đã hưởng? (b) danh sách 300% gồm ai? (c) chính sách OT cho Level ≥ 7 (HR-QT chỉ quy định Level ≤ 6)?
provenance: raw:ANALYSIS-excel-params.md (§1.6 — OT type=input, "KHÔNG CÓ TRONG EXCEL: công thức tính tiền OT từ số giờ"; §2 hệ số; §9.3 Get_Calculated_Time_Blocks blocked) · raw:ANALYSIS-docx-specs.md (A4 — CONFLICT/GAP về 300% và Level ≥7)
verified: true

---

## Q5 — S8.1 · Tech stack

Raw không chỉ định ngôn ngữ/framework/DB/hosting.

answer: **Python 3 stdlib-only. Không package ngoài, không DB, không network.**
- **Engine**: Python thuần. `app/engine.py` = 126 CODE thành 1 DAG tất định, mỗi CODE 1 hàm `f(ctx) -> Decimal`, topo-sort theo `seq`. Tiền dùng `decimal.Decimal` + `ROUND_HALF_UP` (Excel `ROUND(x,0)` là half-up, **không** dùng `float`/`round()` của Python vì round-half-even sẽ lệch 1 đồng và HR sẽ bắt ngay).
- **Tham số**: `data/params.json` — MỘT chỗ duy nhất chứa 46.800.000 / 106.200.000 / 45.000 / 730.000 / 15.500.000 / 6.200.000 / 0,5% / 253.000 / 8-1,5-1% / 17-0,5-3-1% / 2% / biểu thuế 5 bậc / `formula_layer` / `ot_multipliers`. Có `effective_from` → 1 kỳ = 1 param-set (payslip mẫu dùng 11tr là kỳ cũ, phải chạy lại được — xem Q12).
- **Dữ liệu**: JSON/CSV trong repo. `data/inputs/<period>/*.json` (vào) · `data/out/<period>/*.json|csv|html` (ra). Git = version control = backup.
- **UI**: `http.server.ThreadingHTTPServer` + `string.Template` render HTML server-side. 1 file `_run_app.py` → `python3 _run_app.py` → mở `localhost:8000`. Không Flask/Django/FastAPI, không npm, không build step, không CDN (mọi CSS/JS inline).
- **Test**: `unittest` stdlib, `python3 -m unittest` — fixture chính là ground-truth dòng 9 (Q12).
Lý do: yêu cầu tối cao là "chạy được ngay trên máy local, không cài thêm package". Payroll lô đầu không có gì cần một framework: không concurrency, không auth, không migration, ~4.200 record/kỳ (dưới 5 phút cho hàng ngàn người là thừa sức với Python thuần — `Decimal` chậm ~10× float nhưng 4.200 × 126 field ≈ 530k phép tính, dưới 5 giây). Khi lên server thật: giữ nguyên `engine.py`, chỉ thay `_run_app.py` + `adapters.py` — engine không biết gì về HTTP hay DB.
provenance: assumed (ràng buộc thi công của dự án; `raw:ANALYSIS-docx-specs.md` S8.1 ghi rõ **MISSING** ngôn ngữ/framework/DB/hosting) · lens:payroll-expert (Decimal + ROUND_HALF_UP là bắt buộc với tiền, không thương lượng)
verified: false

---

## Q6 — S7.5 · Giao diện & design system

Raw chỉ nêu tên màn hình, không có wireframe/style guide/theme.

answer: **3 màn hình, không hơn** — đủ để HR nghiệm thu engine, không gold-plate:
1. **`/` Bảng lương** — grid 1 dòng/NV, cột theo nhóm đúng header cấp-1 của Excel thật (Thông tin NV · Lương HĐ · Ngày công · Lương thực tế · PC chịu thuế · PC không chịu thuế · Tăng ca · Thưởng · BHXH · Thuế · **Lương thực nhận** · Chi phí công ty). Dòng đầu = dòng TỔNG (như `SUBTOTAL` dòng 4). Sticky header + sticky 3 cột đầu. Ô lệch so với ground-truth (nếu có) tô đỏ.
2. **`/payslip/<msnv>` Phiếu lương** — dựng đúng layout payslip thật: header kỳ **"Từ ngày 21/[M-1] đến ngày 20/[M]"**, khối A–E, đánh số `[0]`…`[67]`, 2 cột Không-chịu-thuế / Chịu-thuế cho phụ cấp, in được (`@media print`).
3. **`/trace/<msnv>/<CODE>` Trace công thức** — đây là màn ĐẮT NHẤT và là lý do dự án tồn tại (NFR v2.1 §8: "mọi con số phải truy vết được về công thức + số ngày + định mức + nguồn định mức"). Mỗi CODE hiện: công thức nguyên văn → giá trị từng biến đầu vào (click được, đệ quy xuống) → tham số dùng (kèm giá trị + `effective_from` + nguồn: `params.json` hay Tờ trình nào) → clause_id trong BR → dòng Excel gốc. Cây trace = duyệt ngược DAG, ~40 dòng code, tái dùng luôn cho debug engine.
**Design system**: không dùng framework. 1 file `app/static/style.css` inline: hệ 8px spacing, `system-ui` font, số tiền `font-variant-numeric: tabular-nums` + căn phải + phân cách `.` kiểu VN. Bảng dày (row-height 28px) vì HR đọc 4.000 dòng, không phải landing page. **Bắt buộc có toggle dark/light**: `prefers-color-scheme` làm mặc định + nút toggle ghi `localStorage` + script chống FOUC đặt trong `<head>` — không ép mode.
Không làm ở lô đầu: dashboard lãnh đạo, màn khóa kỳ, màn nhập Tờ trình, chấm công nhanh (đều thuộc lô 2, xem Q7).
provenance: raw:ANALYSIS-excel-params.md (§6 payslip 67 dòng, §8.1 header) · raw:ANALYSIS-docx-specs.md (S7.5, S1.3 KPI#4 truy vết) · assumed (design system, dark/light, chọn đúng 3 màn)
verified: false

---

## Q7 — S4.3 · Ưu tiên: lô đầu làm gì, hoãn gì

32 feature, không có MoSCoW.

answer: Cắt theo tiêu chí duy nhất: **cái gì hôm nay chứng minh được là ĐÚNG bằng máy thì làm; cái gì không chứng minh được thì hoãn.**
**MUST — lô đầu (5 mục, tất cả có test):**
| # | Việc | Nghiệm thu |
|---|---|---|
| M1 | `params.json` — 20 tham số ở MỘT chỗ, có `effective_from` | đổi 1 số → engine đổi, không sửa code |
| M2 | `engine.py` — 126 CODE, DAG theo `seq`, lớp as-is (Q1), `Decimal`+`ROUND_HALF_UP` | chạy hết không lỗi |
| M3 | **Đối chiếu ground-truth dòng 9** — 25 cột kết quả + 2 ô tự-kiểm (`EF9=0`, `EW9=CK9`) | `python3 -m unittest` XANH, sai 1 đồng = đỏ |
| M4 | UI 3 màn (Q6) | mở localhost thấy đúng số dòng 9 |
| M5 | Trace công thức đến tận `params.json` + clause BR | click `NET_PAY` → xuống được tới `BASIC_SAL` |
**SHOULD — lô 2 (có AC sẵn trong tài liệu, nhưng ground-truth dòng 9 KHÔNG kiểm được vì trong Excel thật các cột này là input tay):** engine phụ cấp (FE-04): suất ăn 1/2/3 bữa + luật >4 tiếng, pro-rata, **quy tắc <14 ngày**, tách theo bộ phận khi điều động — nghiệm thu bằng **AC-1 (65 suất)** và **AC-2 (đi lại = (3+1)/CC × ĐM_A + (3+2)/CC × ĐM_B)** chốt tại họp 23/03/2026; Tờ trình duyệt riêng (FE-05); engine thưởng (FE-10); khóa kỳ (FE-15); audit log (FE-17).
**HOÃN — không có credential / API bị chặn / không kiểm được (ghi `docs/DEFERRED.md`):** Workday API (FE-01), SAP (FE-27), file ngân hàng HSBC/Citibank (FE-25), Payslip push API (FE-26), Teams Bot + Override + Sync-back (FE-16), Azure AD SSO (FE-32), multi-tenant/data-masking (FE-28), Dashboard lãnh đạo (FE-22), Mắt Bão (FE-18), truy thu/thoái thu BHXH + lãi nộp chậm (FE-12), báo cáo động (FE-29).
**Lý do cắt phụ cấp khỏi lô đầu (dù nó là "linh hồn" của PRD):** trong bảng lương thật, `AO`/`AR`/`AU`/`AV` (cơm, đi lại, PC) là **input tay — không có công thức**. Nghĩa là engine phụ cấp không có ground-truth để đối chiếu; nó chỉ có 2 ví dụ từ biên bản họp. Làm nó ở lô 2, sau khi lõi tiền đã đúng — nếu làm chung lô đầu và số lệch, không ai biết lệch do engine lương hay engine phụ cấp.
provenance: raw:ANALYSIS-docx-specs.md (S4.3 = **MISSING** MoSCoW → đây là suy luận; S10.1 AC-1/AC-2; S4.1 32 feature) · raw:ANALYSIS-excel-params.md (§1.4 dòng 11: "AO/AR/AU/AV là input tay") · lens:payroll-expert (thứ tự "lõi tiền đúng trước, phụ cấp sau")
verified: false

---

## Q8 — S7.4 · Môi trường & backup

HR tự nhận: *"No staging/UAT environment — payroll cannot be tested in production; staging là non-negotiable"*.

answer: **Lô đầu KHÔNG deploy → không có prod → chưa phát sinh vấn đề staging.** Toàn bộ chạy local, không server, không DB, không secret. Nhưng KHÔNG bỏ qua yêu cầu — cài sẵn 3 thứ để lời hứa "staging non-negotiable" thành sự thật ngay khi có server:
1. **Kỳ = thư mục, bất biến**: `data/out/<period>/run-<YYYYMMDDHHMM>/` — mỗi lần chạy engine ghi 1 snapshot JSON MỚI, **không ghi đè**. `runs/latest` là symlink. Đây là "môi trường" của payroll: chạy lại tháng cũ với param cũ phải ra đúng số cũ.
2. **Diff 2 lần chạy**: `python3 -m app.diff <run_a> <run_b>` → in ra NV nào lệch, CODE nào lệch, bao nhiêu đồng. Đây chính là **parallel-run so với Excel** mà mục S10.1 ghi là MISSING, và là thứ duy nhất cho phép HR dám cắt Excel. Rẻ (~60 dòng), phải có từ lô đầu.
3. **Backup = git**. Repo chứa cả input, params, output snapshot → mọi con số payroll đã từng phát ra đều truy được về 1 commit. Không cần backup strategy nào khác cho tới khi có DB.
Khi lên server (lô 3, kèm điều kiện bắt buộc trước go-live): dev → **staging bắt buộc, có bản copy dữ liệu 1 kỳ thật đã ẩn danh** → prod; cấm chạy payroll test trên prod; RTO/RPO + lịch backup DB **MISSING trong mọi tài liệu → phải hỏi IT**. Cũng chưa ai trả lời gap #9 của chính HR: *"When payroll output is wrong, how does anyone know?"* → snapshot + diff ở trên là câu trả lời tối thiểu cho lô đầu.
provenance: raw:ANALYSIS-excel-params.md (§9.2 gap #3 "no test suite", #8 "no staging", #9 "no error handling/audit log") · raw:ANALYSIS-docx-specs.md (S7.4 = MISSING, S10.1 "parallel run: MISSING") · assumed (snapshot/diff/git là quyết định thi công)
verified: false

---

## Q9 — S5.4 · Trần lương đóng BHXH/BHYT: 50,6tr hay 46,8tr?

Bảng tham số khai `INS_SAL_BH = MIN(BASIC_SAL, 50.600.000)`, nhưng công thức `SI_EMP`/`HI_EMP` lại dùng trần **46.800.000**, và **giá trị thật dòng 9 dùng 46,8tr** (`SI_EMP = 3.744.000 = 46,8tr × 8%`). Chính Excel cũng lộ lệch: ô check `U2 = 8.602.000` ≠ `DD9 = 7.956.000`.

answer: **DÙNG 46.800.000.** Đây là con số bảng lương thật đang chạy, và nó khớp ĐỒNG THỜI ở 6 chỗ độc lập của dòng 9 — không thể là trùng hợp:
`SI_EMP` 3.744.000 = 46,8tr × 8% ✓ · `HI_EMP` 702.000 = 46,8tr × 1,5% ✓ · `SI_CTY` 7.956.000 = 46,8tr × 17% ✓ · `HI_CTY` 1.404.000 = 46,8tr × 3% ✓ · `TNLD_CTY` 234.000 = 46,8tr × 0,5% ✓ · `KPCD_CTY` 936.000 = 46,8tr × 2% ✓ · `UNION_FEE` 234.000 = 46,8tr × 0,5% ✓.
Con số 50.600.000 chỉ xuất hiện ở ô hiển thị `U9` và **không được công thức nào tiêu thụ** — chính Excel tự tố cáo bằng ô check `U2 = U9 × 17% = 8.602.000 ≠ DD9 = 7.956.000`. Tức 50,6tr là giá trị đã cập nhật vào bảng tham số nhưng **CHƯA được áp vào công thức** — một cây kim chờ nổ.
Thi công — quy về MỘT tham số duy nhất, mọi công thức BH/KPCĐ/công đoàn ăn chung:
```
INS_SAL_BH = IF(Chính thức, MIN(CONTRACT_TOTAL, params.ins_cap_bh), 0)   # ins_cap_bh = 46_800_000
INS_SAL_UI = IF(Chính thức, MIN(CONTRACT_TOTAL, params.ins_cap_ui), 0)   # ins_cap_ui = 106_200_000; expat → 0
SI/HI/SI_CTY/HI_CTY/TNLD_CTY/KPCD_CTY/UNION_FEE  ← ĐỀU dùng INS_SAL_BH   (TNLD dùng cap BH, KHÔNG dùng cap UI)
UI_EMP/UI_CTY                                     ← dùng INS_SAL_UI       (1.062.000 = 106,2tr × 1% ✓)
```
Base là **`CONTRACT_TOTAL`** (lương HĐ = BASIC + RESP), không phải `BASIC_SAL` — theo công thức sống `U9`/`V9`. ⚠ Dòng 9 KHÔNG phân biệt được 2 base này (vì `RESP_SAL = 0` nên BASIC = CONTRACT = 200tr) → chọn CONTRACT_TOTAL theo as-is nhưng **đây là giả định phải hỏi HR** (ảnh hưởng mọi NV có phụ cấp trách nhiệm).
Đổi trần khi Nhà nước tăng lương cơ sở: sửa `params.json` → `ins_cap_bh`, thêm `effective_from`. **Phải hỏi HR: 50,6tr là trần MỚI sắp áp từ kỳ nào?** — nếu đúng, đây không phải bug mà là param chưa tới ngày hiệu lực.
Miễn đóng BHXH (note BY10, engine phải có): số ngày thử việc/không lương/thai sản **≥ 14 ngày** trong tháng dương lịch → KHÔNG đóng BHXH tháng đó. NV có HĐ 2 nơi → không đóng BHXH/BHYT/BHTN (⚠ "chưa quản lý trên WD, cần master data" → cờ tay `no_insurance: true`).
provenance: raw:ANALYSIS-excel-params.md (§1.11 ⚠MÂU THUẪN TRẦN LƯƠNG, §5.1 bảng tham số, §8.3 ground-truth dòng 9, §2 miễn đóng ≥14 ngày, §1.2 ghi chú Q19/Q20)
verified: true

---

## Q10 — S4.2 · Cơm miễn thuế: 1.200.000 hay 730.000?

Bảng tham số Payroll structure: **1.200.000**. Payslip thật + note bảng lương: **730.000**. PRD v2.1 §5.3.1 cũng ghi **730.000**.

answer: **DÙNG 730.000.** Ba nguồn độc lập chỉ về 730k, và một trong ba là **số học đóng được**: payslip thật (Lê Văn Biên) có PC cơm non-tax **730.000** + taxable **2.780.000** → `MEAL_ALLOW = 3.510.000 = 78 suất × 45.000` ✓, và `3.510.000 − 730.000 = 2.780.000` ✓ khớp chính xác. Đó là bằng chứng công thức `MEAL_NONTAX = MIN(MEAL_ALLOW, 730.000)` / `MEAL_TAX = MAX(0, MEAL_ALLOW − 730.000)` đang chạy thật ngoài đời. Con số 1.200.000 chỉ nằm ở ô tham số `V7` của sheet structure, không có một kết quả thật nào chứng minh.
(Ghi chú: dòng 9 KHÔNG kiểm được điều này — `AU9 = −990.000` là **số âm**, tức HR nhập tay để bù trừ, không phải công thức. `AO/AR/AU/AV` trong bảng lương thật đều là input tay. Nên bằng chứng phải lấy từ payslip, không lấy từ dòng 9.)
Thi công: `params.meal_tax_free = 730_000` + `params.meal_unit_price = 45_000`, cả hai có `effective_from`. Cùng một chỗ đó chứa `formula_layer` — khi HR chốt 1,2tr (rất có thể đây là mức MỚI, giống chuyện 50,6tr ở Q9), sửa 1 dòng + thêm ngày hiệu lực, không đụng code, và mọi kỳ cũ vẫn chạy lại ra đúng số cũ.
**Phải hỏi HR đúng 1 câu**: "1.200.000 là mức miễn thuế MỚI (áp từ kỳ nào), hay là ô tham số điền nhầm?" — vì cả 50,6tr (Q9) lẫn 1,2tr (Q10) lẫn 15,5tr (Q11) đều là "số mới ở sheet structure" trong khi 46,8tr / 730k là "số cũ đang chạy". Nhưng 15,5tr thì ĐÃ vào ground-truth (Q11) → chứng tỏ họ đang cập nhật DẦN. Đây là tín hiệu mạnh: 46,8tr và 730k sẽ sớm bị thay. Engine phải cấu hình được là bắt buộc, không phải nice-to-have.
provenance: raw:ANALYSIS-excel-params.md (§6 số liệu mẫu payslip: non-tax 730.000 / taxable 2.780.000; §3.2 note AO10/AU10 "Miễn thuế 730k"; §5.1 tham số V7 = 1.200.000; §1.4 dòng 11 "AO/AR/AU/AV input tay") · raw:ANALYSIS-docx-specs.md (A7 + FE-13: "Phần ≤ 730.000 đ/tháng ghi cột Non-tax")
verified: true

---

## Q11 — S5.2 · Giảm trừ bản thân: 15,5tr hay 11tr?

Payroll structure: **15.500.000** (đúng NQ 954 sửa đổi mới). Payslip mẫu: **11.000.000** (mức cũ). Giảm trừ NPT: **6.200.000**/người (structure) — payslip mẫu dùng 4,4tr cũ.

answer: **DÙNG 15.500.000 (bản thân) + 6.200.000/người (NPT).** Khác Q9/Q10, ở đây **ground-truth dòng 9 xác nhận trực tiếp** con số mới, không phải suy đoán:
`PERSONAL_DED` (CF9) = **15.500.000** ✓ · `DEPENDENT_CNT` (CG9) = 3 · `DEPENDENT_DED` (CH9) = **18.600.000 = 3 × 6.200.000** ✓ · `TOTAL_DED` (CI9) = **34.100.000** ✓ → và chuỗi này chảy đúng xuống tận cuối: `TAXABLE_INC` = 225.000.000 − 5.508.000 − 34.100.000 = **185.392.000** ✓ → `PIT` = 185.392.000 × 35% − 14.500.000 = **50.387.200** ✓ → `NET_PAY` = **189.930.161** ✓.
Payslip mẫu (11tr + 4,4tr) là chứng từ của một **KỲ CŨ** — payslip đó cũng dùng 730k cơm và BHTN = 0. Nó không phải "lớp as-is đang chạy", nó là ảnh chụp quá khứ. Không được lấy nó ghi đè bảng tham số hiện hành.
Thi công: `params.personal_ded = 15_500_000`, `params.dependent_ded = 6_200_000`, kèm `effective_from`. **Chính vì payslip cũ tồn tại nên param BẮT BUỘC phải có ngày hiệu lực** — engine phải chạy lại được kỳ cũ với param-set cũ (11tr/4,4tr) và ra đúng `NET = 20.284.000` của Lê Văn Biên. Đó là fixture số 2 của bộ test (xem Q12) và là bài kiểm tra rằng "cấu hình được" là thật chứ không phải khẩu hiệu.
Áp dụng thêm (as-is `CF9`): thử việc → `PERSONAL_DED = 0` (`IF(HĐ="Chính thức", 15.500.000, 0)`) — nhất quán với luật thuế 10%/20% cho thử việc ở §5.2.
provenance: raw:ANALYSIS-excel-params.md (§8.3 ground-truth dòng 9: CF9/CG9/CH9/CI9/CJ9/CK9/CZ9; §1.12 công thức PERSONAL_DED; §5.1 tham số V8/V9; §6 payslip mẫu dùng 11.000.000)
verified: true

---

## Q12 — S10.2 · Engine chạy nghiệm thu trên dữ liệu nào?

Roster thật 4.179 người nằm ở Workday, **không có trong repo**. Excel bàn giao chỉ có **1 dòng nhân viên thật đã ẩn danh (dòng 9)** kèm đầy đủ cột kết quả.

answer: **Nghiệm thu trên 1 dòng thật + 1 payslip thật + N case tổng hợp. Không cần roster.** Một dòng ĐÚNG TOÀN CHUỖI có giá trị chứng minh cao hơn 4.179 dòng không có đáp án — dòng 9 chạy qua đủ 126 CODE, tất cả 5 tầng (ngày công → lương → thu nhập → BH/thuế → thực nhận → chi phí công ty), và Excel còn tặng kèm 2 ô tự-kiểm.
**Bộ nghiệm thu — `tests/`:**
| # | Fixture | Nguồn | Assert |
|---|---|---|---|
| **GT-1** | `ground-truth-row9.json` — input (M9, Q9…AI9) + **25 cột kết quả** | dòng 9 Excel bàn giao (đã ẩn danh) | Engine phải ra **CHÍNH XÁC từng đồng**: GROSS 225.010.000 · TAXABLE_GROSS 225.000.000 · TOTAL_INS 5.508.000 · TOTAL_DED 34.100.000 · TAXABLE_INC 185.392.000 · PIT 50.387.200 · NET_INCOME 169.114.800 · **NET_PAY 189.930.161** · TOTAL_INS_CTY 10.656.000 · KPCD 936.000 · TOTAL_CTY_COST 201.522.161 · BUDGET_SAVE 305.018.667 |
| **GT-1b** | 2 ô tự-kiểm của chính Excel | `EF9`, `EX9` | `SUM(AN:BV) − TOTAL_INS − TOTAL_PIT + SUM(CO:CS) − SUM(CT:CY) − NET_PAY == 0` (cân sổ) và `PIT_if_ladder == PIT_sumproduct` (2 cách tính thuế trùng nhau) |
| **GT-2** | `payslip-2024-legacy.json` — payslip Lê Văn Biên (006720, L6, 0 NPT) chạy với **param-set CŨ** (personal_ded 11tr, dependent 4,4tr, cơm 730k, BHTN 0) | payslip mẫu trong Excel | `NET == 20.284.000` · cơm non-tax 730.000 / taxable 2.780.000 · BHXH 3.744.000 · BHYT 702.000 · PIT 572.000. **Đây là test chứng minh `params.effective_from` hoạt động thật** — cùng 1 engine, 2 bộ tham số, 2 kết quả đúng. |
| **SYN-1..6** | Case tổng hợp cho nhánh dòng 9 KHÔNG chạm | `lens:payroll-expert`, dựng từ công thức sống | thử việc VN `TAXABLE_INC < 2tr` → PIT = 0 · thử việc VN `≥ 2tr` → 10% · thử việc **nước ngoài** → 20% · expat → `UI_EMP = 0` · 5 bậc thuế lũy tiến (biên 10/30/60/100tr) · miễn đóng BHXH khi nghỉ ≥14 ngày · `MAX(0, …)` khi TAXABLE_INC âm |
| **PERF** | 4.179 bản sao dòng 9 (nhân bản, đổi MSNV) | sinh bằng script | chạy < 5 phút (NFR v2.1 §8). Cho phép đo sớm, không chờ Workday. |
**Ranh giới rõ:** GT-1/GT-1b/GT-2 = **thật, verified**. SYN-* = **giả định** (đúng theo công thức sống nhưng chưa ai đối chiếu số thật) → vào bảng "Giả định đang gánh". Khi Workday mở quyền: thay `fetch_employees()` (Q3), chạy engine trên roster thật, dùng `app/diff` (Q8) so với bảng lương Excel của cùng kỳ → **parallel run**. Đó mới là nghiệm thu cuối; bộ test này là điều kiện CẦN để được phép chạy tới đó.
**Hỏi HR 1 câu**: xin thêm **10–20 dòng thật đã ẩn danh** phủ các nhánh SYN (thử việc, expat, có phụ cấp trách nhiệm, nghỉ ≥14 ngày, có phép tồn) — đây là thứ rẻ nhất họ có thể cho và có giá trị cao nhất cho chất lượng engine.
provenance: raw:ANALYSIS-excel-params.md (§8.2 "chỉ có ĐÚNG 1 dòng nhân viên: dòng 9", §8.3 bảng ground-truth + 2 ô tự-kiểm EF9/EX9, §6 số liệu mẫu payslip, §5.2 case thử việc/expat, §9.3 Get_Workers = 4.179 rows) · raw:ANALYSIS-docx-specs.md (S7.1 NFR < 5 phút; S10.1 "parallel run: MISSING") · lens:payroll-expert (bộ SYN-*)
verified: true
