# BÓC TÁCH YÊU CẦU — HỆ THỐNG PAYROLL (Unicons/Coteccons)

> Nguồn (3 file, đã đọc hết):
> - `raw:hr-quy-trinh-tinh-luong-va-thanh-toan-luong_so-luoc-1.txt` → viết tắt **[HR-QT]** (quy trình nội bộ Unicons, 427 dòng)
> - `raw:prd__payroll_system_v2-2.txt` → **[PRD-2.1]** (PRD v2.1, 08/07/2026, "chỉ kết nối Workday", 334 dòng)
> - `raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt` → **[PRD-3.0]** (PRD v3.0, "Workday + SAP + Bank", 85 dòng)
>
> Lưu ý toàn cục: **[PRD-2.1] và [PRD-3.0] là 2 phiên bản PRD KHÁC NHAU, mâu thuẫn nhau ở phạm vi tích hợp và tập người dùng.** v3.0 có số hiệu cao hơn nhưng v2.1 có ngày cập nhật rõ (08/07/2026) và trạng thái "Approved for Dev"; v3.0 không ghi ngày. Đây là xung đột PHẢI chốt trước khi soạn BR.

---

## S1 — Vấn đề & Mục tiêu

### S1.1 — Sản phẩm giải bài toán gì (1 câu)
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt`

Xây một **lõi tính lương (Payroll Engine) trung tâm cho HR/C&B**, tự động tổng hợp công từ Workday (Workday KHÔNG tự tổng hợp công) và tính toàn bộ lương/phụ cấp/thưởng/BHXH/thuế phức tạp của Unicons/Coteccons, thay cho các sheet Excel thủ công.

Trích [PRD-2.1] §1: "xây dựng một hệ thống Payroll trung tâm nhằm tự động hóa quy trình tổng hợp công và tính toán phụ cấp từ một nguồn tích hợp duy nhất là Workday… Do Workday hiện không thực hiện tổng hợp công, hệ thống Payroll phải đảm nhận toàn bộ việc tổng hợp".

Trích [PRD-3.0] §1: "Xây dựng một lõi tính lương (Payroll Engine) độc lập, chuyên biệt dành riêng cho phòng HR/C&B. Hệ thống đóng vai trò trung gian: Nhận dữ liệu nhân sự/chấm công từ Workday và tỷ lệ phân bổ chi phí từ SAP, Tính toán… và Xuất dữ liệu trả về Workday (Payslip), Ngân hàng (File thanh toán), và SAP (Chi phí kế toán)."

### S1.2 — Đau hiện tại / bằng chứng
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:hr-quy-trinh-tinh-luong-va-thanh-toan-luong_so-luoc-1.txt`

- "Workday hiện KHÔNG tổng hợp công. Payroll chỉ nhận dữ liệu công thô theo từng ngày/từng bộ phận và phải tự thực hiện toàn bộ logic tổng hợp" — [PRD-2.1] §4.2.
- "Hệ thống giải quyết bài toán **xử lý thủ công**, tách biệt logic giữa nhân sự chính thức và nhân sự Mắt Bão" — [PRD-2.1] §1.
- "thay thế các **sheet Excel tổng hợp thủ công hiện tại**" — [PRD-2.1] §2.
- Bằng chứng vật lý (căn cứ PRD): "File tổng hợp phụ cấp tháng 02/2026; Bảng công hiện hành; Bảng lương mẫu (Payroll 0904); Các Tờ trình phụ cấp duyệt riêng" — [PRD-2.1] header; file HR hiện hành tên `02__HR C&B` — [PRD-2.1] §6.4.
- Đau về kỷ luật duyệt: cần "nhắc duyệt đơn" qua Teams + báo cáo "Đơn Treo" cho lãnh đạo → hiện có tình trạng quản lý duyệt chậm làm trễ chốt lương — [PRD-2.1] §2, §6.2, §6.5.
- Đau về thủ công trong quy trình: chấm công do thư ký từng Phòng ban/Công trường làm rời rạc, C&B phải "làm việc trực tiếp với CBNV và yêu cầu thư ký điều chỉnh lại cho chính xác" khi phát hiện sai — [HR-QT] §V.1.
- Quy trình hiện tại phải chạy tay trong 6 ngày + chuỗi review/ký nhiều lớp (xem S3) — [HR-QT] §IV.

### S1.3 — "Thành công" trông thế nào (kiểm chứng được)
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt`

KPI ghi rõ tại [PRD-2.1] §2:
1. **Chính xác 100%**: "Triệt tiêu sai sót thủ công trong tính toán phụ cấp (cơm, điện thoại, nhiên liệu/xăng xe, đi lại, công trường xa...) và trong việc chia tách giai đoạn điều động/thử việc/bổ nhiệm."
2. **Tiết kiệm 80% thời gian**: "Tự động hóa tổng hợp công từ Workday, nhắc duyệt đơn và xuất file trình ký/báo cáo đúng định dạng."
3. **Tính nhất quán**: "Dữ liệu giữa Payroll và Workday luôn đồng bộ thông qua cơ chế Sync-back; một nguồn định mức duy nhất được quản trị tập trung."
4. **Kiểm chứng được (NFR)**: "mọi con số phụ cấp trên báo cáo phải truy vết được về công thức + số ngày + định mức + nguồn định mức (Quy định chung hay Tờ trình nào)" — [PRD-2.1] §8.
5. **Hiệu năng**: toàn bộ nhân sự (hàng ngàn người) < 5 phút — [PRD-2.1] §8.

### S1.4 — Phi-mục-tiêu
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt`

- KHÔNG tích hợp hệ thống HR nào ngoài Workday: "hệ thống Payroll chỉ kết nối và tích hợp với duy nhất hệ thống Workday. Không tích hợp với bất kỳ hệ thống HR nào khác" (loại bỏ tham chiếu HRM/HRE) — [PRD-2.1] §2.1 changelog + §4.2.
- KHÔNG làm cổng self-service cho nhân viên: "Hệ thống chỉ dành cho HR Admin và C&B Staff. Không có tài khoản dành cho nhân viên (Regular Employee) hay Trưởng bộ phận trên hệ thống này." — [PRD-3.0] §3. **(⚠ mâu thuẫn trực tiếp với [PRD-2.1] — xem S2.1 CONFLICT)**
- KHÔNG truy thu công sau khi khóa kỳ: "mọi đơn duyệt muộn/sửa công trên hệ thống gốc sau ngày chốt sẽ không được cập nhật hay truy thu vào tháng sau" — [PRD-2.1] §4.3.
- Payroll KHÔNG là source-of-truth dữ liệu gốc: "hệ thống Payroll tin tưởng tuyệt đối dữ liệu nguồn (Source of Truth) từ Workday trừ trường hợp HR can thiệp Override" — [PRD-2.1] §8.
- GĐDA: "không áp dụng phụ cấp công trường/đi lại theo bảng chung (chỉ hưởng theo Tờ trình riêng nếu có)" — [PRD-2.1] §5.3.7.

---

## S2 — Người dùng

### S2.1 — Nhóm người dùng
`status: conflict`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt · raw:hr-quy-trinh-tinh-luong-va-thanh-toan-luong_so-luoc-1.txt`

**CONFLICT — phải chốt trước khi thiết kế:**

| Phiên bản A — [PRD-2.1] (nhiều nhóm) | Phiên bản B — [PRD-3.0] (chỉ HR) |
|---|---|
| Admin; HR C&B; **Thư ký công trường**; **Chỉ huy trưởng**; **Trưởng bộ phận (duyệt qua Teams)**; **Lãnh đạo (Dashboard riêng)**. Trích §3: "Thư ký công trường/Chỉ huy trưởng chỉ thấy dữ liệu ngày công, tuyệt đối không thấy thông tin về số tiền"; §6.5: "Trang Dashboard dành riêng cho lãnh đạo theo dõi thời gian thực." | Trích §3: "**Hệ thống chỉ dành cho HR Admin và C&B Staff. Không có tài khoản dành cho nhân viên (Regular Employee) hay Trưởng bộ phận trên hệ thống này.**" |

Nhóm actor xuất hiện trong quy trình gốc [HR-QT] (bối cảnh, không phải user hệ thống một cách hiển nhiên): CBNV; Thư ký Phòng ban/Công trường; Trưởng Phòng ban/Công trường/GĐDA; NV/CV C&B (phụ trách chấm công / phụ trách tính lương); Teamlead C&B; Trưởng P.NS-TH; Giám đốc Quản trị Nguồn nhân lực / Phó TGĐ Vận hành; Tổng giám đốc/Lãnh đạo ủy quyền; Kế toán trưởng; P.TCKT; **Mắt Bão** (nhà cung cấp dịch vụ tính lương/outsource).

### S2.2 — Vai trò & quyền mỗi nhóm
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt · raw:hr-quy-trinh-tinh-luong-va-thanh-toan-luong_so-luoc-1.txt`

- **Phân quyền chi tiết (Granular)**: "Admin có quyền thiết lập vai trò chi tiết cho từng nhóm người dùng (**Xem / Sửa / Xuất file / Khóa kỳ / Duyệt thay**)" — [PRD-2.1] §3.
- **Thư ký công trường / Chỉ huy trưởng**: chỉ thấy ngày công, **tuyệt đối không thấy số tiền** (lương/phụ cấp) — [PRD-2.1] §3. Thư ký còn có quyền: chấm bổ sung cơm CN/ca đêm/lễ ([PRD-2.1] §5.3.1), import file đăng ký đi làm lễ ([PRD-2.1] §5.5).
- **HR C&B**: quyền **Override (duyệt thay)** để chốt lương kịp tiến độ; quyền **khóa kỳ thủ công**; quyền nhập danh sách Tờ trình duyệt riêng; nhóm DUY NHẤT được nhận báo cáo bảng công chi tiết (§6.4 — "chỉ cấp cho HR C&B và ghi log truy cập/xuất file") — [PRD-2.1] §3, §4.3, §5.2, §6.2, §6.4.
- **Trưởng bộ phận**: duyệt đơn (công/OT/đi làm lễ), nhận nhắc duyệt qua **Microsoft Teams Bot** — [PRD-2.1] §5.5, §6.2.
- **Lãnh đạo**: Dashboard realtime + nhận báo cáo "Đơn Treo" tự động ngày Cut-off — [PRD-2.1] §6.5.
- **Data Masking theo pháp nhân**: "Hỗ trợ phân quyền xem dữ liệu theo từng Pháp nhân (Công ty con)" — [PRD-3.0] §3.
- Quyền phê duyệt bảng lương ngoài hệ thống ([HR-QT] §IV): Teamlead C&B rà soát → Trưởng P.NS-TH kiểm tra → **Giám đốc QTNNL / Phó TGĐ Vận hành phê duyệt** → Tổng giám đốc/Lãnh đạo ủy quyền + Kế toán trưởng duyệt chi.

### S2.3 — Quy mô
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt`

- "toàn bộ nhân sự (**hàng ngàn người**)" — [PRD-2.1] §8.
- Đa pháp nhân: "Hệ thống hỗ trợ kiến trúc **Đa công ty (multi-tenant)**, cho phép quản lý nhiều pháp nhân với các chính sách riêng biệt trên cùng một nền tảng." — [PRD-3.0] §1.
- Phạm vi tổ chức: "Tất cả Phòng ban/Công trường… tất cả CBNV Công ty" — [HR-QT] §II.
- Con số headcount chính xác: **MISSING**.

---

## S3 — Flow đầu-cuối

### S3.1 — Danh sách flow (đặt tên)
`status: filled`
`provenance: raw:hr-quy-trinh-tinh-luong-va-thanh-toan-luong_so-luoc-1.txt · raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt`

- **F1. Chấm công kỳ 21→20** (thư ký chấm → TP duyệt → C&B tổng hợp)
- **F2. Đồng bộ Biến động nhân sự (BĐNS) từ Workday**
- **F3. Tổng hợp công tự động** (thử việc/chính thức, trước/sau bổ nhiệm, theo bộ phận khi điều động, ngày tính/không tính BHXH, suất ăn)
- **F4. Tính phụ cấp** (7 loại + truy thu/truy lĩnh)
- **F5. Tính lương chính** (thử việc + chính thức + PC trách nhiệm + OT)
- **F6. Tính thưởng** (T13, Tết âm, KPI, thưởng công trình, đột xuất, VLN)
- **F7. Tính BHXH/BHYT/BHTN + KPCĐ/CĐP**
- **F8. Tính thuế TNCN tạm trích + đăng ký NPT/giảm trừ gia cảnh**
- **F9. Phê duyệt & trình ký** (C&B → Teamlead C&B → TP NS-TH → GĐ QTNNL/PTGĐ VH → TGĐ + KTT)
- **F10. Nhắc duyệt & Override qua MS Teams + Sync-back Workday**
- **F11. Khóa kỳ lương (Manual Lock)**
- **F12. Xuất báo cáo & file** (Trình ký T0, Payroll Master T2, bảng công chi tiết, file ngân hàng, file SAP, Payslip)
- **F13. Hạch toán & phân bổ chi phí** (bộ phận/công trường/GĐDA/kiêm nhiệm → SAP)
- **F14. Quyết toán phép năm & trợ cấp thôi việc khi nghỉ việc**
- **F15. Quyết toán thuế TNCN cuối năm**
- **F16. Luồng Mắt Bão (outsource)** — lịch chốt công sớm hơn, định mức riêng, timeline riêng
- **F17. Điều chỉnh BHXH truy thu/thoái thu theo lô (batch import Excel)** — [PRD-3.0] §4.6

### S3.2 — Mỗi flow: bước đầu → bước cuối → điều kiện thành công
`status: filled`
`provenance: raw:hr-quy-trinh-tinh-luong-va-thanh-toan-luong_so-luoc-1.txt · raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt`

**F1–F9 — Quy trình lương tháng (timeline chuẩn, [HR-QT] §IV.2):**

| Bước | Việc | Trách nhiệm | Deadline | Kết quả / điều kiện thành công |
|---|---|---|---|---|
| 1a | Chấm công cho CBNV (cập nhật phép, ốm BHXH/ốm công ty, thai sản lên hệ thống) | Phòng ban/Công trường/CBNV + NV/CV C&B phụ trách chấm công | **Ngày 16–19 hàng tháng** | "Bảng chấm công của Phòng ban/Công trường chính xác và đầy đủ; Bảng tổng hợp chấm công toàn Công ty". Phòng ban/Công trường "chịu trách nhiệm về tính chính xác và đầy đủ của BCC" |
| 1b | Thông tin biến động nhân sự | NV/CV phụ trách tính lương + Bộ phận Tuyển dụng/điều động | **Ngày 18–19** | "Thông tin CBNV phải được cập nhật đầy đủ và chính xác" |
| 1c | Cập nhật đầy đủ dữ liệu vào bảng lương | NV/CV tính lương | **Ngày 20–21** | "Dữ liệu liên quan đến thu nhập CBNV được tổng hợp đầy đủ" |
| 2 | Tính lương và các khoản liên quan | NV/CV tính lương | **Ngày 22** | Bảng tổng hợp + bảng chi tiết chi lương + bảng so sánh lương so tháng trước → chuyển teamlead |
| 3 | Trưởng bộ phận C&B kiểm tra / rà soát | Teamlead C&B (phối hợp Trưởng P.NS-TH) | **Chậm nhất ngày 23** | Bảng đã rà soát; **phát hiện sai sót → quay về bước 2** |
| 4a | Trưởng phòng kiểm tra | Trưởng P.NS-TH; TGĐ/Lãnh đạo ủy quyền | **Chậm nhất ngày 24** | Bảng đã phê duyệt; **không phê duyệt → quay về bước 2** |
| 4b | Bảng thanh toán lương được phê duyệt (thủ tục **online**) | NV/CV tính lương + TGĐ/Lãnh đạo ủy quyền + Kế toán trưởng | **Chậm nhất ngày 25** | "Bảng chi tiết chi lương đến từng CBNV, chi phí BHXH, BHYT, BHTN, KPCĐ, CĐP… được cập nhật và phê duyệt trên hệ thống" |
| 5 | Báo cáo lương và lưu trữ hồ sơ | NV/CV tính lương + Teamlead C&B | **Chậm nhất ngày 26** | Bảng hạch toán lương; báo cáo số lượng nhân sự; báo cáo tổng hợp chi phí nhân sự hàng tháng. "Hồ sơ scan và hồ sơ gốc được lưu trữ theo quy định" |

Lưu đồ tổng (thời lượng): 06 ngày (chấm công/BĐNS/phụ cấp) → 01 ngày (tính lương) → 0.5 ngày (bảng tổng hợp+chi tiết) → 01 ngày (Teamlead C&B) → 01 ngày (TP kiểm tra + GĐ QTNNL/PTGĐ VH phê duyệt) → **chậm nhất ngày 25** (CTQ phê duyệt) → 02 ngày (hạch toán, báo cáo, lưu trữ) — [HR-QT] §IV.1.

Ghi chú thời gian: "Trường hợp thanh toán lương sớm hơn dự kiến thì thời gian trình tự liên quan sẽ được lùi tương ứng" — [HR-QT] bước 1c.

**F16 — TIMELINE ĐI LƯƠNG MẮT BÃO** ([HR-QT], bảng cuối file):

| STT | Bước | Phụ trách | Ngày hoàn tất |
|---|---|---|---|
| 1 | Thư ký chấm công | Thư ký/CBNV phụ trách chấm công | **16–17** (rơi vào T7, CN thì lùi tương ứng) |
| 2 | Công ty gửi bản chấm công cho Mắt Bão | CTD/UNI | **18** |
| 3 | Mắt Bão lên bảng lương, đối soát | Mắt Bão | **19** |
| 4 | Công ty và Mắt Bão review và chốt bảng lương | CTD/UNI/Mắt Bão | **20, 21** |
| 5 | Mắt Bão gửi hồ sơ thanh toán | Mắt Bão | **21** |
| 6 | CTD/UNI thanh toán cho Mắt Bão | CTD/UNI | **23, 24** |
| 7 | **Mắt Bão thanh toán lương cho CBNV** | Mắt Bão | **Trước 15h ngày 25** (rơi vào T7, CN lùi tương ứng) |

**F3 — Tổng hợp công tự động** ([PRD-2.1] §5.1): Bắt đầu = pull công thô theo ngày/bộ phận từ API Workday → Payroll tự đếm 5 chỉ tiêu (5.1.1 → 5.1.5) → Kết thúc = bộ số ngày đã tách giai đoạn/bộ phận sẵn sàng cho tính phụ cấp. Điều kiện thành công: mọi con số truy vết được về công thức + số ngày + định mức + nguồn định mức.

**F11 — Khóa kỳ (Manual Lock)** ([PRD-2.1] §4.3): HR kiểm soát xong → bấm khóa thủ công → **hệ thống ngừng đồng bộ API tháng đó** → không phát sinh biến động.

**F10 — Nhắc duyệt & Override** ([PRD-2.1] §6.2): Đơn ở trạng thái **Chờ duyệt (?P) → KHÔNG cộng vào công hưởng lương** → Teams Bot nhắc quản lý (HR cấu hình giờ gửi + số lần nhắc) → nếu vẫn treo, HR **Override** → **Sync-back về Workday trạng thái "Đã duyệt"** → Audit log bắt buộc (Giá trị cũ → Giá trị mới, Người thực hiện, Thời gian, **Lý do bắt buộc**).

**F14 — Quyết toán phép năm & trợ cấp thôi việc** ([HR-QT] §V.4): xem S4/S5 để biết công thức. Điều kiện thời điểm: "Nếu CBNV nghỉ việc **trước ngày 20** thì được thanh toán trong kỳ lương tháng đó, nếu nghỉ việc **sau ngày 20** thì thanh toán trong kỳ lương tháng sau hoặc kỳ lương gần nhất sau khi hoàn tất thủ tục nghỉ việc."

**F15 — Quyết toán thuế TNCN** ([HR-QT] §V.5): "Hàng tháng C&B tạm trích thuế TNCN của CBNV. Hàng năm C&B sẽ thực hiện quyết toán thuế TNCN thay đối với CBNV đủ điều kiện ủy quyền và có gửi **bản gốc giấy ủy quyền** quyết toán thuế TNCN về Công ty **hoặc** xuất chứng từ khấu trừ thuế và xác nhận thu nhập để CBNV tự quyết toán."

### S3.3 — Luồng ngoại lệ / lỗi
`status: filled`
`provenance: raw:hr-quy-trinh-tinh-luong-va-thanh-toan-luong_so-luoc-1.txt · raw:prd__payroll_system_v2-2.txt`

- **Rà soát phát hiện sai** (bước 3) → "quay về bước 2" — [HR-QT].
- **Không phê duyệt** (bước 4) → "quay về bước 2" — [HR-QT].
- **Ngày công sai quy định**: "C&B làm việc trực tiếp với CBNV và yêu cầu thư ký điều chỉnh lại cho chính xác. Trưởng Phòng ban/Công trường xác nhận trên bảng chấm công." — [HR-QT] §V.1.
- **Phép năm âm vượt tiêu chuẩn**: "C&B yêu cầu thư ký điều chỉnh lại ngày công **ngay trong tháng**." — [HR-QT] §V.1.
- **Tăng ca chênh lệch so với đăng ký**: "C&B đối chiếu lại ngày công chấm thực tế so với danh sách đăng ký nếu chênh lệch yêu cầu thư ký **điều chỉnh/giải trình**." — [HR-QT] §V.1.
- **Hồ sơ NPT đăng ký thất bại**: "Những hồ sơ đăng ký không thành công C&B sẽ phản hồi lại cho CBNV đăng ký." — [HR-QT] §V.4.
- **Đơn treo quá Cut-off** → HR Override + báo cáo lãnh đạo — [PRD-2.1] §6.2, §6.5.
- **Sửa công sau khóa kỳ** → bị từ chối, không truy thu — [PRD-2.1] §4.3.
- **Nộp chậm BHXH**: "Hệ thống cần có thể **tự tính tiền lãi nộp chậm bảo hiểm**." — [PRD-3.0] §4.6.
- **Ngày hoàn tất rơi vào T7/CN** (Mắt Bão): "lùi tương ứng" — [HR-QT].

---

## S4 — Feature

### S4.1 — Danh sách feature
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt · raw:hr-quy-trinh-tinh-luong-va-thanh-toan-luong_so-luoc-1.txt`

| # | Feature | Nguồn |
|---|---|---|
| FE-01 | Đồng bộ dữ liệu công thô + master data từ **API Workday** | PRD-2.1 §4.2, PRD-3.0 §2 |
| FE-02 | **Engine tổng hợp công** (5 chỉ tiêu §5.1.1–5.1.5) | PRD-2.1 §5.1 |
| FE-03 | **Chấm công nhanh**: mặc định fill đủ công chuẩn, tự trừ nghỉ phép/không lương/nghỉ việc/ốm từ Workday | PRD-3.0 §4.2 |
| FE-04 | **Engine phụ cấp** 7 loại + pro-rata + quy tắc <14 ngày + tách theo bộ phận | PRD-2.1 §5.2–5.3 |
| FE-05 | **Phụ cấp theo Tờ trình (duyệt riêng)** có ngày hiệu lực, ghi đè định mức chung | PRD-2.1 §5.2, PRD-3.0 §4.3 |
| FE-06 | **Truy thu / truy lĩnh phụ cấp** (hồi tố trong kỳ chưa khóa) | PRD-2.1 §4.3 |
| FE-07 | **Tính lương thử việc / chính thức / PC trách nhiệm** tách theo ngày hiệu lực | PRD-2.1 §5.1.1–5.1.2, HR-QT §V.4 |
| FE-08 | **Tăng ca (OT)** — hệ số cấu hình được, tách nhóm Chính thức vs Mắt Bão, tách OT chịu/không chịu thuế | PRD-2.1 §5.5 |
| FE-09 | **Tách dòng & Phân bổ chi phí** (điều động theo thời gian + kiêm nhiệm % dự án) | PRD-3.0 §4.3 |
| FE-10 | **Engine thưởng** (T13, Tết âm, KPI, thưởng công trình, đột xuất, VLN) | PRD-3.0 §4.4, HR-QT §V.4 |
| FE-11 | **Engine BHXH/BHYT/BHTN** + luật 14 ngày + trần đóng + KPCĐ/CĐP | HR-QT §V.2, PRD-2.1 §5.1.4, PRD-3.0 §4.6 |
| FE-12 | **Import batch Excel truy thu/thoái thu BHXH** + tự tính lãi nộp chậm | PRD-3.0 §4.6 |
| FE-13 | **Engine thuế TNCN** — cấu hình linh hoạt khoản miễn thuế; tách Taxable/Non-tax | PRD-2.1 §5.2, PRD-3.0 §4.6 |
| FE-14 | **Quản lý NPT / giảm trừ gia cảnh** (cut-off ngày 15) | HR-QT §V.4 |
| FE-15 | **Khóa kỳ lương thủ công (Manual Lock)** | PRD-2.1 §4.3, PRD-3.0 §4.1 |
| FE-16 | **Quy trình duyệt + MS Teams Bot nhắc duyệt + Override + Sync-back** | PRD-2.1 §6.2 |
| FE-17 | **Audit Log** (cũ→mới, ai, khi nào, lý do bắt buộc) + log xem/xuất file | PRD-2.1 §6.2, §8 |
| FE-18 | **Quản lý nhân sự Mắt Bão** (nhận diện qua EmployeeType, lịch chốt sớm, grid định mức riêng trên Payroll) | PRD-2.1 §6.1 |
| FE-19 | **Báo cáo Trình ký (Template 0)** | PRD-2.1 §6.3 |
| FE-20 | **Payroll Master (Template 2)** — file phẳng cho kế toán | PRD-2.1 §6.3, PRD-3.0 §5 |
| FE-21 | **Báo cáo Bảng công chi tiết (mẫu file HR `02__HR C&B`) — bảo mật** | PRD-2.1 §6.4 |
| FE-22 | **Báo cáo Đơn "Treo" + Dashboard lãnh đạo realtime** | PRD-2.1 §6.5 |
| FE-23 | **Master Data Management** (6 danh mục nền) | PRD-2.1 §7 |
| FE-24 | **Danh mục ngày lễ tự động hằng năm** + đăng ký đi làm lễ (NLĐ đăng ký/thư ký import → TP duyệt → HR) | PRD-2.1 §5.5, §7 |
| FE-25 | **Xuất file chuyển khoản ngân hàng** (HSBC, Citibank…, NH nội địa & quốc tế) | PRD-3.0 §2, §5 |
| FE-26 | **Payslip** — PDF hoặc bắn API về Workday | PRD-3.0 §5 |
| FE-27 | **Tích hợp SAP** (inbound cost allocation, outbound chi phí hạch toán) | PRD-3.0 §2 |
| FE-28 | **Multi-tenant / đa pháp nhân** + data masking theo pháp nhân | PRD-3.0 §1, §3 |
| FE-29 | **Báo cáo động** (Headcount, Joiner/Leaver, so sánh chênh lệch công/lương giữa các tháng, lũy kế thu nhập, trích nộp BHXH, quyết toán thuế cuối năm, Cost Allocation Report) | PRD-3.0 §5 |
| FE-30 | **Quyết toán phép năm & trợ cấp thôi việc** | HR-QT §V.4 |
| FE-31 | **Hạch toán & phân bổ chi phí nội bộ** (GĐDA theo doanh thu, phòng ban hỗ trợ công trường theo tỷ lệ TP đề xuất) | HR-QT §V.4 |
| FE-32 | **Azure AD SSO + phân quyền granular** | PRD-2.1 §3, PRD-3.0 §3 |

### S4.2 — Acceptance-criteria kiểm-chứng-được cho MỖI feature
`status: filled` (một phần suy từ ví dụ chốt tại họp; các AC không có trong tài liệu ghi rõ MISSING)
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt · raw:hr-quy-trinh-tinh-luong-va-thanh-toan-luong_so-luoc-1.txt`

- **FE-01**: Payroll lấy được: bảng công theo ngày với ký hiệu công, công chuẩn, loại giờ tăng ca, định mức phụ cấp chính thức, "Ngày kết thúc thử việc", EmployeeType từ API Workday. Không gọi bất kỳ hệ thống HR nào khác.
- **FE-02**: Với 1 NV bất kỳ trong kỳ, hệ thống xuất đúng: (a) ngày thử việc/sau thử việc, (b) ngày trước/sau bổ nhiệm, (c) ngày công tại từng bộ phận (bộ phận 1/2/3) tách theo loại ngày, (d) số ngày tính/không tính BHXH theo tháng dương lịch, (e) tổng suất ăn — **không nhập tay** ("Hệ thống Payroll phải tự tổng hợp các số ngày này theo từng bộ phận, không nhập tay" — §5.4).
- **FE-04 (AC chốt tại họp 23/03/2026 — dùng làm test case)**:
  - *Ví dụ 1*: NV X làm VP A 5 ngày (>4h/ngày → 1 bữa) + dự án B 20 ngày (>30km, >4h/ngày → 3 bữa) → **Tổng suất ăn = 5×1 + 20×3 = 65 suất**.
  - *Ví dụ 2*: NV X có 10 ngày công ở BP A (3 làm việc, 1 lễ, 6 phép) + 15 ngày công ở BP B (3 làm việc, 7 phép, 2 việc riêng hưởng lương, 1 không lương, 2 lễ). Tổng ngày làm việc thực tế = 3+3 = 6 < 14 → áp quy tắc <14 ngày → **PC đi lại = (3+1)/Công chuẩn × Định mức BP A + (3+2)/Công chuẩn × Định mức BP B**. Tính tương tự cho nhiên liệu/xăng xe và điện thoại.
- **FE-13**: Mỗi loại phụ cấp phải có 2 cột Taxable/Non-tax; cơm: "Phần ≤ 730.000 đ/tháng ghi cột Non-tax; phần vượt ghi cột Taxable".
- **FE-15**: Sau khi khóa: (a) hệ thống ngừng đồng bộ API tháng đó; (b) đơn duyệt muộn/sửa công sau ngày chốt KHÔNG được cập nhật và KHÔNG truy thu sang tháng sau.
- **FE-16**: Đơn ở trạng thái `?P` (Chờ duyệt) KHÔNG được cộng vào công hưởng lương. Sau HR Override, trạng thái sync-back về Workday = "Đã duyệt".
- **FE-17**: Mỗi thao tác lưu: Giá trị cũ → Giá trị mới, Người thực hiện, Thời gian, **Lý do (bắt buộc)**. Mọi lượt xuất file báo cáo nhạy cảm đều có log.
- **FE-19**: "Nhân sự điều động: toàn bộ công trong tháng được gộp vào bảng trình ký của **dự án cuối cùng (nơi nhân viên làm việc vào ngày 20)** để Chỉ huy trưởng tại đó ký xác nhận." Template dùng chung cho Chính thức và Mắt Bão.
- **FE-21**: Chỉ HR C&B được cấp quyền xem/xuất; mọi truy cập/xuất bị ghi log.
- **NFR-AC (áp cho toàn engine)**: "mọi con số phụ cấp trên báo cáo phải **truy vết được về công thức + số ngày + định mức + nguồn định mức** (Quy định chung hay Tờ trình nào)"; toàn bộ nhân sự (hàng ngàn người) xử lý **< 5 phút**.
- **AC cho các feature còn lại (FE-03, 05–12, 14, 18, 20, 22–32)**: tài liệu mô tả hành vi nhưng **KHÔNG có acceptance-criteria dạng kiểm-chứng-được** → `MISSING` (phải soạn khi làm BR).

### S4.3 — Ưu tiên must/should/could
`status: missing`
`provenance: —`

**MISSING.** Không tài liệu nào gán MoSCoW/priority cho feature. Suy luận gián tiếp duy nhất: [PRD-2.1] tự nhận là "Approved for Dev" cho toàn bộ nội dung của nó, và changelog v2.1 loại HRM/HRE ra khỏi phạm vi. Ưu tiên phải chốt với khách hàng.

---

## S5 — Dữ liệu

### S5.1 — Entity nghiệp vụ
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt · raw:hr-quy-trinh-tinh-luong-va-thanh-toan-luong_so-luoc-1.txt`

Employee (CBNV) · EmploymentContract (thử việc / HĐCT) · Company/Pháp nhân (multi-tenant) · Department/Bộ phận · Project/Công trường · JobGrade (Ngạch chức danh QL.01–NV.05, TV; Level L1–L8) · PayPeriod (kỳ công 21→20) · InsurancePeriod (kỳ BHXH 01→cuối tháng) · TimesheetDay (chấm công theo ngày × ký hiệu) · TimesheetAggregate (bản tổng hợp §5.1) · LeaveRequest/Đơn (phép, ốm, không lương, hiếu hỉ, thai sản, nghỉ bù) · OTRegistration/OTRecord · MealCount (suất ăn) · AllowanceType (7 loại) · AllowanceRate/Định mức · TờTrình (duyệt riêng, có ngày hiệu lực) · AllowanceCalcLine (theo bộ phận/giai đoạn) · Retro/Truy thu-truy lĩnh · SalaryLine (thử việc/chính thức/PC trách nhiệm/lương phép tồn) · Bonus (T13, Tết âm, KPI, công trình, đột xuất, VLN, lì xì) · InsuranceContribution (NV + Cty) · UnionFee (KPCĐ 2%, CĐP 0.5%) · TaxRecord (tạm trích + quyết toán) · Dependent/NPT · SeverancePay (trợ cấp thôi việc) · AnnualLeaveBalance (phép năm, phép tồn) · CostAllocation (kiêm nhiệm % dự án) · Payslip · PayrollRun/Lock · BankTransferFile · AuditLog · MasterData (DM Bộ phận, DM Nơi cư trú, DM Khoảng cách, Bảng định mức, DS Tờ trình, DM Ngày lễ, Quy định ngày nghỉ) · EmployeeType (Chính thức / **Mắt Bão**) · Nationality (VN / nước ngoài — khác tỷ lệ BH).

### S5.2 — Field chính mỗi entity
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt · raw:hr-quy-trinh-tinh-luong-va-thanh-toan-luong_so-luoc-1.txt`

**Employee** (từ [PRD-2.1] §6.4 bảng tổng hợp phụ cấp + [HR-QT] §V.3):
MSNV · Họ tên · **Đối tượng** (VP/CT, Chính thức/Mắt Bão/Nước ngoài) · **Chức danh** · **Cấp bậc/Ngạch (level)** · **Trình độ** (ĐH trở lên / CĐ-TC-Nghề) · **Nơi tuyển dụng** · **Nơi cư trú** · **Khu vực xét phụ cấp** · **Khoảng cách** · Bộ phận hiện tại · Bộ phận trước (khi điều động) · Ngày điều động · Ngày kết thúc thử việc (từ Workday) · EmployeeType · Số tài khoản ngân hàng · Ngày vào/ngày nghỉ việc.
> "Điều chỉnh thông tin cá nhân: **Nơi tuyển dụng, nơi cư trú, bằng cấp**. Những thông tin này **có ảnh hưởng đến mức phụ cấp** cần được cập nhật đúng, đầy đủ và chính xác ngay tại thời điểm điều chỉnh." — [HR-QT] §V.3.

**TimesheetDay — ký hiệu công tối thiểu phải hỗ trợ** ([PRD-2.1] §4.2, đồng bộ bảng công hiện hành):

| Ký hiệu | Ý nghĩa |
|---|---|
| `x` | công làm việc |
| `x1` | lương thời gian |
| `OL` | nghỉ ốm hưởng lương (Cty) |
| `P` / `F` | nghỉ phép năm |
| `R` / `Fo` | nghỉ việc riêng có lương (hiếu, hỉ) |
| `L` | nghỉ lễ, tết |
| `NB` | nghỉ bù |
| `Ts` / `TS` | thai sản |
| `TSN` | thai sản nam |
| `ON` / `OD` | ốm BHXH ngắn / dài ngày |
| `TN` | tai nạn |
| `Ro` | nghỉ không lương |
| (đi làm ngày Lễ) | TC **100% / 300%** |
| (đi làm ngày CN) | TC **200%** |
| `?P` | **Chờ duyệt — KHÔNG cộng vào công hưởng lương** ([PRD-2.1] §6.2) |

**Payroll Master (Template 2) — cấu trúc file phẳng** ([PRD-2.1] §6.3): thông tin nhân sự & hợp đồng; công chuẩn; các ngày công trong tháng (thử việc, sau thử việc, phép năm, lễ tết, nghỉ bù, nghỉ hưởng lương, hiếu hỉ, không lương, BHXH, công bổ sung, phép tồn); lương thực tế (thử việc / chính thức / PC trách nhiệm / lương phép tồn); phụ cấp **Taxable** và **Non-tax** (cơm, điện thoại, NL/xăng, đi lại, **nhà ở**, khác); OT; các loại thưởng; BHXH NV & công ty; giảm trừ; thuế TNCN; các khoản cộng/trừ sau thuế; **lương thực nhận / thực chi**; chi phí công ty; **Profit/Cost Center, WBS, Funds Center**.

**Bảng tổng hợp phụ cấp tháng — 8 cột phụ cấp** ([PRD-2.1] §6.4):
PC Cơm **(1)** · Điện thoại **(2)** · Xăng xe/ô tô **(3)** · CT + Công tác xa **(4)** · Đi lại **(5)** · Công trường xa **(6)** · Khác **(7)** · **Tổng (8)**.
Cùng 3 cột ngữ cảnh: phụ cấp bộ phận hiện tại **(1)**, phụ cấp bộ phận trước **(2)** khi điều động, **phụ cấp truy thu/truy lĩnh (3)**.

**Bảng chấm công kỳ 21–20 (báo cáo §6.4)**: ma trận ngày × nhân viên; ký hiệu công từng ngày; loại ngày (thường/CN/lễ); quy ra công theo từng loại (x, OL, x1, NB, P, R, L, Ts, Ro, O, đi làm lễ/CN các mức TC); **tổng số công được hưởng**; **số ngày công chuẩn**; **số ngày công truy thu/truy lĩnh**; **số phép năm hiện tại và phép còn lại**.

**Bảng tính phụ cấp cơm (§6.4)**: số suất cơm **P1 (không điều động)**, **P2 (điều động trong tháng)**, **cơm tăng ca đêm**, **cơm Chủ nhật (thư ký gửi về)**, tổng số phần cơm, ghi chú; kèm ghi chú trường hợp điều động từ VP (ngày đi, ngày đến, đơn vị 1/đơn vị 2, số ngày công tại mỗi đơn vị, số ngày hưởng tiền cơm).

**Tờ trình duyệt riêng**: MSNV · bộ phận · chức danh · loại phụ cấp (2)→(7) · định mức · **số Tờ trình** · **ngày hiệu lực (từ ngày – đến ngày)** · ghi chú · tổng phụ cấp — [PRD-2.1] §5.2/§5.3.7/§7, [PRD-3.0] §4.3.

**Master Data — 6 danh mục** ([PRD-2.1] §7):
- **DM Bộ phận**: Bộ phận → Tỉnh, Khối (VP/CT), Vùng miền; **có ngày hiệu lực khi thay đổi** (ví dụ: "Kho miền Nam đổi về Bình Dương từ 06/2025").
- **DM Nơi cư trú**: Tỉnh/Thành → Khu vực → Miền.
- **DM Khoảng cách**: cặp (Nơi tuyển dụng/Khu vực xét PC × Tỉnh bộ phận) → số km → dải khoảng cách (**<30, 30–100, 100–400, 400–1000, >1000, khu vực miền**).
- **Bảng định mức phụ cấp**: Điện thoại theo ngạch/level (VP-CT); NL/Xăng theo khối; Đi lại và CT+CTX theo dải khoảng cách × đối tượng; CT xa theo dự án × chức danh.
- **DS Tờ trình duyệt riêng**.
- **DM Ngày lễ**: "Thiết lập tự động hằng năm (**01/01; 5 ngày Tết Âm lịch; 30/04; 01/05; 02/09 +1 ngày; 10/03 ÂL**); HR chỉnh được khi cần."
- **Quy định ngày nghỉ**: "**Phép năm 12 ngày (+1/5 năm thâm niên)**, quy tắc tính phép theo tháng (**≥50% công chuẩn**), **phép tồn dùng đến 31/12 năm kế tiếp**, **nghỉ ốm Cty 3 ngày/năm**, nghỉ hiếu hỉ, thai sản, nghỉ bù… theo sheet Quy định ngày."

### S5.3 — Quan hệ
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt`

- Employee **1–N** TimesheetDay (theo kỳ công) · Employee **1–N** AllowanceCalcLine (**1 dòng / bộ phận / giai đoạn** — do điều động và bổ nhiệm giữa kỳ).
- Employee **N–N** Department qua điều động (kèm ngày điều động; đếm ngày công tại từng bộ phận 1/2/3…).
- Employee **N–N** Project qua CostAllocation (kiêm nhiệm: "VD: 30% Dự án A, 70% Dự án B" — [PRD-3.0] §4.3).
- (Nơi tuyển dụng/Khu vực xét PC) **×** (Tỉnh của bộ phận) → **DM Khoảng cách** → dải km → **×** nhóm đối tượng → định mức PC đi lại — [PRD-2.1] §5.3.4.
- (Dự án đặc thù) **×** (Chức danh) → định mức PC công trường xa — [PRD-2.1] §5.3.6.
- Tờ trình **ghi đè** định mức từ Bảng định mức chung kể từ ngày hiệu lực (1 Employee có thể có N Tờ trình theo loại phụ cấp).
- PayPeriod (21→20) **lệch** InsurancePeriod (01→cuối tháng) → **2 trục thời gian song song** ([PRD-2.1] §4.1, §5.1.4; [PRD-3.0] §4.1).
- Payroll ⇄ Workday (inbound công/master, outbound payslip + sync-back trạng thái duyệt); Payroll ⇄ SAP (inbound cost allocation, outbound chi phí); Payroll → Bank (file chuyển khoản).

### S5.4 — Ràng buộc dữ liệu
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:hr-quy-trinh-tinh-luong-va-thanh-toan-luong_so-luoc-1.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt`

- **Kỳ công**: 21 tháng trước → 20 tháng này. "Ví dụ: kỳ công tháng 03/2026 = 21/02/2026 – 20/03/2026." — [PRD-2.1] §4.1; [HR-QT] §V.1: "Kỳ chấm công tại Công ty được áp dụng từ ngày 21 tháng này đến ngày 20 tháng sau."
- **Kỳ BHXH**: 01 → ngày cuối tháng dương lịch.
- **Ngày công chuẩn**: "Văn phòng: từ 21 – 20, **trừ Chủ nhật và chiều thứ 7**. Công trường: từ 21 – 20, **trừ Chủ nhật**. Công chuẩn VP và CT được lưu riêng cho từng kỳ." — [PRD-2.1] §4.1. **⚠ CONFLICT nhẹ**: [PRD-3.0] §4.2 nói "Công chuẩn: **lấy từ Workday**" (không tự tính).
- **Trạng thái `?P` (Chờ duyệt) KHÔNG cộng vào công hưởng lương** — [PRD-2.1] §6.2.
- **Ngày làm việc ≤ 4 tiếng → 0 suất ăn** — [PRD-2.1] §5.1.5, §5.3.1; [HR-QT] §V.3 ("CBNV làm việc **trên 4 tiếng/ngày** sẽ được tính bữa ăn").
- **Sau khóa kỳ**: ngừng đồng bộ API, không nhận sửa công/duyệt muộn, không truy thu sang tháng sau — [PRD-2.1] §4.3.
- **Bảng chấm công phải có xác nhận phê duyệt của Trưởng Phòng ban/Công trường** — [HR-QT] §V.1.
- **Hồ sơ NPT gửi trước ngày 15 → tính kỳ đó; sau ngày 15 → kỳ sau** — [HR-QT] §V.4.
- **Phụ cấp phải tách 2 cột Taxable / Non-tax** trước khi đưa vào bảng lương — [HR-QT] §V.3, [PRD-2.1] §5.2.
- **Định mức Tờ trình ghi đè định mức chung** kể từ ngày hiệu lực, "và vẫn chịu quy tắc pro-rata/dưới 14 ngày như trên" — [PRD-2.1] §5.2.
- **Đối tượng thưởng bị loại**: CBNV nghỉ việc/có kế hoạch nghỉ việc đã được Trưởng PB/CT xác nhận; thời gian nghỉ thai sản/ốm dài hạn/không lương **lũy kế ≥ 10 ngày** trong kỳ xét **không tính vào thời gian tính thưởng** — [HR-QT] §V.4; [PRD-3.0] §4.4.

---

## S6 — Tích hợp

### S6.1 — API / hệ thống bên thứ ba
`status: conflict`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt`

**CONFLICT LỚN — phạm vi tích hợp:**

**Phiên bản A — [PRD-2.1] v2.1 (§ changelog 2.1 + §4.2):** CHỈ Workday.
> "Chuẩn hóa phạm vi tích hợp: hệ thống Payroll **chỉ kết nối và tích hợp với DUY NHẤT hệ thống Workday** (loại bỏ các tham chiếu HRM/HRE). Mọi dữ liệu đầu vào (chấm công, hồ sơ nhân sự, ngày kết thúc thử việc, EmployeeType, loại giờ tăng ca) lấy từ API Workday; **Sync-back trạng thái duyệt cũng chỉ về Workday**."
> "Không tích hợp với bất kỳ hệ thống HR nào khác; các dữ liệu không có trên Workday (định mức Mắt Bão, danh sách Tờ trình duyệt riêng, danh mục master data) được quản trị trực tiếp trên Payroll."
> Ngoài ra vẫn có: **Microsoft Teams Bot** (nhắc duyệt), **Email** (báo cáo Đơn Treo), **Azure AD SSO**.

**Phiên bản B — [PRD-3.0] (§2):** Workday **+ SAP + Ngân hàng**.
> "**Workday (Inbound & Outbound API)**: Inbound: Nhận Master data, Lịch sử tăng lương, Người phụ thuộc, Quyết định nghỉ việc, Dữ liệu chấm công (Nghỉ phép, OT...). Outbound: Đẩy Phiếu lương (Payslip) về lại Workday."
> "**Kế toán & SAP**: Inbound: Nhận file phân bổ chi phí (Cost Allocation) của nhân sự kiêm nhiệm dự án (VD: 30% Dự án A, 70% Dự án B) hoặc lấy từ Workday. Outbound: Trả file kết quả lương/chi phí đã hạch toán cho SAP."
> "**Hệ thống Ngân hàng (Export)**: Xuất template chuyển khoản tự động chuẩn định dạng của các ngân hàng nội địa và quốc tế" — nêu đích danh **HSBC, Citibank** (§5).

Bên thứ ba khác cả 2 bản đồng thuận: **Azure Active Directory (SSO)**; **Microsoft Teams**.

### S6.2 — Hệ thống nội bộ phải tương thích
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt · raw:hr-quy-trinh-tinh-luong-va-thanh-toan-luong_so-luoc-1.txt`

- **Workday** (hệ thống chấm công/nhân sự gốc — Source of Truth).
- **Microsoft 365 / Azure AD / Teams**: "Tương thích: tích hợp sâu với hạ tầng **Microsoft 365 của Coteccons/Unicons**" — [PRD-2.1] §8.
- **SAP** (kế toán) — chỉ [PRD-3.0].
- **Mắt Bão** — đối tác outsource tính/chi lương: cần trao đổi bảng chấm công + hồ sơ thanh toán theo timeline riêng ([HR-QT]); nhận diện qua **EmployeeType từ API** ([PRD-2.1] §6.1).
- Định dạng file kế toán hiện hành: "Báo cáo Phân bổ chi phí (Cost Allocation Report) **theo chuẩn excel kế toán cần**" — [PRD-3.0] §5.
- Trường hạch toán phải khớp SAP: **Profit/Cost Center, WBS, Funds Center** — [PRD-2.1] §6.3.

### S6.3 — Định dạng trao đổi
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt`

- **API** (Workday inbound/outbound; Teams Bot; Payslip "bắn qua API về Workday").
- **Excel import**: file phân bổ chi phí kế toán ([PRD-3.0] §4.3); batch truy thu/thoái thu BHXH ([PRD-3.0] §4.6); "Bữa ăn chấm đêm **import theo mẫu**" ([HR-QT] §V.3); thư ký import file đăng ký đi làm lễ ([PRD-2.1] §5.5).
- **Excel/file phẳng export**: Payroll Master (Template 2); Trình ký (Template 0); Bảng công chi tiết theo mẫu `02__HR C&B`; Cost Allocation Report.
- **PDF**: Payslip ("xuất PDF hoặc bắn qua API về Workday" — [PRD-3.0] §5).
- **Template ngân hàng**: "chuẩn định dạng của các ngân hàng nội địa và quốc tế" (HSBC, Citibank…). **Đặc tả layout cụ thể: MISSING.**
- **Email / Teams message**: báo cáo Đơn Treo cho lãnh đạo.

---

## S7 — Phi chức năng

### S7.1 — Hiệu năng
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt`

"Hiệu năng: xử lý tổng hợp công, tính toán và xuất báo cáo cho **toàn bộ nhân sự (hàng ngàn người) trong vòng dưới 5 phút**." — [PRD-2.1] §8.
Dashboard lãnh đạo: theo dõi **thời gian thực** — [PRD-2.1] §6.5.

### S7.2 — Bảo mật & phân quyền
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt`

- **Xác thực**: Azure AD SSO (tài khoản Office 365 công ty) — cả 2 PRD.
- **Granular Permissions**: Xem / Sửa / Xuất file / Khóa kỳ / Duyệt thay — [PRD-2.1] §3.
- **Field-level masking**: "Thư ký công trường/Chỉ huy trưởng chỉ thấy dữ liệu ngày công, **tuyệt đối không thấy thông tin về số tiền** (lương/phụ cấp)."
- **Report-level restriction**: báo cáo bảng công chi tiết (§6.4) "chứa dữ liệu nhạy cảm về định mức phụ cấp và ghi chú cá nhân, **chỉ phân phối cho nhóm HR C&B được cấp quyền**; **mọi lượt xuất file phải được ghi log**."
- **NFR bảo mật**: "báo cáo bảng công chi tiết và các bảng định mức chỉ mở cho nhóm được phân quyền; **log toàn bộ thao tác xem/xuất**." — [PRD-2.1] §8.
- **Data Masking theo pháp nhân** — [PRD-3.0] §3.
- **Audit Log bắt buộc**: "Giá trị cũ → Giá trị mới, Người thực hiện, Thời gian và **Lý do bắt buộc**." — [PRD-2.1] §6.2.

### S7.3 — Khối lượng dữ liệu
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt`

"hàng ngàn người" mỗi kỳ; ma trận chấm công ngày × nhân viên cho kỳ 21–20; nhiều pháp nhân (multi-tenant). Con số cụ thể (số bản ghi, số công trường, dung lượng): **MISSING**.

### S7.4 — Khả dụng / backup
`status: missing`
`provenance: —`

**MISSING.** Không tài liệu nào nêu SLA uptime, RTO/RPO, chiến lược backup, DR. Điều gần nhất là yêu cầu **lưu trữ hồ sơ**: "Tất cả các hồ sơ liên quan đến kỳ lương sẽ được NV/CV C&B **scan và lưu hồ sơ gốc, file mềm đầy đủ theo từng tháng**"; "Hồ sơ scan và hồ sơ gốc được lưu trữ theo quy định" — [HR-QT] §IV.2 (bước 4, bước 5). Đây là lưu trữ nghiệp vụ, KHÔNG phải backup hệ thống.

### S7.5 — Yêu cầu giao diện / UI
`status: filled` (mỏng)
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt`

- **Trang Dashboard riêng cho lãnh đạo** theo dõi thời gian thực (đơn treo) — [PRD-2.1] §6.5.
- **Màn hình khóa kỳ thủ công** cho HR — [PRD-2.1] §4.3.
- **Màn hình cấu hình**: tần suất/giờ gửi/số lần nhắc Teams; hệ số OT (tách Chính thức vs Mắt Bão); đơn giá suất ăn; grid định mức Mắt Bão; danh mục ngày lễ.
- **Màn hình nhập Tờ trình duyệt riêng**: MSNV – loại phụ cấp – định mức – số Tờ trình – ngày hiệu lực.
- **Màn hình "Chấm công nhanh"**: mặc định fill đủ công chuẩn, tự trừ ngày nghỉ — [PRD-3.0] §4.2.
- **Chức năng xuất báo cáo thủ công** cho HR — [PRD-2.1] §6.5.
- Wireframe/mockup/style guide/responsive/dark-light: **MISSING**.

---

## S8 — Ràng buộc

### S8.1 — Công nghệ bắt buộc / cấm
`status: filled` (một phần)
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt`

**Bắt buộc:**
- Azure Active Directory SSO (không dùng auth riêng).
- Microsoft Teams Bot (kênh nhắc duyệt) + Email.
- "tích hợp sâu với hạ tầng **Microsoft 365** của Coteccons/Unicons".
- Kiến trúc **multi-tenant** (đa pháp nhân) — [PRD-3.0].

**Cấm / loại trừ:**
- "**Không tích hợp với bất kỳ hệ thống HR nào khác**" ngoài Workday (loại bỏ HRM/HRE) — [PRD-2.1] v2.1.
- Không tạo tài khoản cho nhân viên / trưởng bộ phận — [PRD-3.0] §3 (⚠ conflict).

**MISSING:** ngôn ngữ/framework/DB/hosting (cloud vs on-prem) — không tài liệu nào chỉ định.

### S8.2 — Deadline
`status: missing`
`provenance: raw:prd__payroll_system_v2-2.txt`

**MISSING** (không có deadline dự án / go-live). Mốc thời gian duy nhất ghi được:
- [PRD-2.1] v1.0: 07/02/2026 — "Bản Final ban đầu – Phê duyệt cho phát triển."
- [PRD-2.1] v2.0 & v2.1: 08/07/2026 — trạng thái **"Phê duyệt cho Phát triển (Approved for Dev)"**.
- Biên bản họp chốt logic: **23/03/2026**.
- [PRD-3.0]: trạng thái "Sẵn sàng phát triển (Ready for Dev)" — **không ghi ngày**.

(Các deadline vận hành hàng tháng — ngày 16/18/19/20/21/22/23/24/25/26 — xem S3.2, đó là ràng buộc nghiệp vụ, không phải deadline dự án.)

### S8.3 — Ngân sách / nguồn lực
`status: missing`
`provenance: —`

**MISSING.** Không tài liệu nào nói ngân sách, size team, vendor, hay chi phí.

---

## S9 — Phạm vi loại trừ

### S9.1 — Dứt khoát KHÔNG làm
`status: filled`
`provenance: raw:prd__payroll_system_v2-2.txt · raw:tài-liệu-yêu-cầu-sản-phẩm-hệ-thống-payroll_sent.txt`

1. **Không tích hợp hệ thống HR nào khác ngoài Workday** ("loại bỏ các tham chiếu HRM/HRE") — [PRD-2.1] v2.1.
2. **Không có tài khoản cho nhân viên thường / trưởng bộ phận** trên hệ thống — [PRD-3.0] §3. ⚠ *(mâu thuẫn [PRD-2.1] vốn có role thư ký/CHT/quản lý duyệt/lãnh đạo)*.
3. **Không truy thu công sau khóa kỳ** — "mọi đơn duyệt muộn/sửa công trên hệ thống gốc sau ngày chốt sẽ **không được cập nhật hay truy thu vào tháng sau**" — [PRD-2.1] §4.3.
4. **Sau khóa kỳ: ngừng đồng bộ API tháng đó** — [PRD-2.1] §4.3.
5. **Payroll không tự sinh dữ liệu gốc** — "tin tưởng tuyệt đối dữ liệu nguồn từ Workday trừ trường hợp HR Override" — [PRD-2.1] §8.
6. **Khối Văn phòng KHÔNG áp định mức chung phụ cấp nhiên liệu** — chỉ theo Tờ trình — [PRD-2.1] §5.3.3.
7. **GĐDA không áp phụ cấp công trường/đi lại theo bảng chung** — [PRD-2.1] §5.3.7.
8. **Định mức phụ cấp Mắt Bão KHÔNG lấy từ Workday** — quản trị trực tiếp trên Payroll — [PRD-2.1] §6.1.
9. **Ngày làm ≤ 4 tiếng: không tính suất ăn** — [PRD-2.1] §5.3.1.
10. **Ngày phép / nghỉ hưởng lương khác / nghỉ không lương KHÔNG tính vào "ngày hưởng" khi áp quy tắc <14 ngày** — [PRD-2.1] §5.2.

### S9.2 — Hoãn sang sau
`status: missing`
`provenance: —`

**MISSING.** Không tài liệu nào có mục "Phase 2 / Future / Backlog / Deferred". Ứng viên hiển nhiên cần chốt (do 2 PRD lệch nhau): **SAP integration**, **file ngân hàng (HSBC/Citibank)**, **Payslip PDF/API**, **multi-tenant**, **portal cho trưởng bộ phận/lãnh đạo** — [PRD-3.0] có, [PRD-2.1] không.

---

## S10 — Nghiệm thu

### S10.1 — Kịch bản nghiệm thu toàn hệ
`status: filled` (một phần — chỉ có 2 ví dụ chốt tại họp; không có UAT plan)
`provenance: raw:prd__payroll_system_v2-2.txt`

Không có "kịch bản nghiệm thu toàn hệ" chính thức. Tài liệu duy nhất mang tính test case là **§5.4 Ví dụ minh họa (chốt tại họp 23/03/2026)** — đây là 2 case bắt buộc PASS:

**AC-1 (Ví dụ 1 — Tổng hợp suất ăn khi điều động):**
> "Nhân viên X làm tại văn phòng A trong 5 ngày (mỗi ngày trên 4 tiếng → 1 bữa/ngày). Làm dự án B trong 20 ngày, khoảng cách trên 30 km (mỗi ngày trên 4 tiếng → 3 bữa/ngày). → Hệ thống tự tổng hợp: **Tổng số suất ăn = 5 × 1 + 20 × 3 = 65 suất**. Nếu có ngày làm việc ≤ 4 tiếng thì ngày đó không tính suất ăn."

**AC-2 (Ví dụ 2 — Phụ cấp khi điều động và dưới 14 ngày làm việc):**
> "Nhân viên X có 10 ngày công ở bộ phận A (3 ngày làm việc, 1 ngày lễ, 6 ngày phép) và 15 ngày công ở bộ phận B (3 ngày làm việc, 7 ngày phép, 2 ngày nghỉ việc riêng hưởng lương, 1 ngày không lương, 2 ngày lễ). Tổng ngày làm việc thực tế = 3 + 3 = 6 ngày < 14 ngày → áp dụng quy tắc tỷ lệ (chỉ tính ngày làm việc thực tế + ngày lễ): **Phụ cấp đi lại X = (3 + 1)/Ngày công chuẩn × Định mức bộ phận A + (3 + 2)/Ngày công chuẩn × Định mức bộ phận B.** Tính tương tự cho phụ cấp nhiên liệu/xăng xe và điện thoại. Hệ thống Payroll phải tự tổng hợp các số ngày này theo từng bộ phận, **không nhập tay**."

Ràng buộc nghiệm thu ngầm khác (NFR, [PRD-2.1] §8): mọi con số phụ cấp trên báo cáo phải truy vết được về **công thức + số ngày + định mức + nguồn định mức**; xử lý toàn bộ nhân sự < 5 phút.

**MISSING**: UAT plan, danh sách test case đầy đủ, tiêu chí Go/No-Go, đối chiếu song song (parallel run) với Excel hiện tại.

### S10.2 — Dữ liệu mẫu / môi trường
`status: filled` (chỉ có tên file, không có file)
`provenance: raw:prd__payroll_system_v2-2.txt`

Dữ liệu mẫu do khách hàng cung cấp (nêu tên trong "Căn cứ" + §6.4):
- **File tổng hợp phụ cấp tháng 02/2026** — file HR `02__HR C&B` (chứa các sheet: bảng chấm công 21–20, bảng tính phụ cấp cơm, bảng tổng hợp phụ cấp tháng, sheet **"Truy lãnh"**, sheet **"Quy định ngày"**, danh sách theo dõi duyệt riêng).
- **Bảng lương mẫu (Payroll 0904)** — cấu trúc chuẩn cho Payroll Master (Template 2).
- **Bảng công hiện hành** — nguồn bộ ký hiệu công.
- **Quy định về Hệ thống cấp bậc chức danh và chế độ phúc lợi** — nguồn bảng định mức.
- **Các Tờ trình phụ cấp duyệt riêng** (khối văn phòng, 02 tài xế Hà Nội, Làng Tây – Hòn Thơm, Thủ kho, GĐDA, Ban TGĐ).
- **Biên bản họp ngày 23/03/2026**.

Môi trường (dev/staging/prod, Workday sandbox, SAP test): **MISSING**.

---
---

# PHỤ LỤC A — TOÀN BỘ QUY TẮC TÍNH (bóc đầy đủ, không tóm tắt)

## A1. Ngày công chuẩn & kỳ

| Hạng mục | Giá trị | Nguồn |
|---|---|---|
| Kỳ công (kỳ lương) | **21 tháng trước → 20 tháng này** (VD kỳ T03/2026 = 21/02/2026 – 20/03/2026) | [PRD-2.1] §4.1; [HR-QT] §V.1; [PRD-3.0] §4.1 |
| Kỳ BHXH | **01 → ngày cuối tháng dương lịch** | cả 3 file |
| Công chuẩn **Văn phòng** | 21→20, **trừ Chủ nhật và chiều thứ 7** | [PRD-2.1] §4.1 |
| Công chuẩn **Công trường** | 21→20, **trừ Chủ nhật** | [PRD-2.1] §4.1 |
| Lưu trữ | "Công chuẩn VP và CT được lưu **riêng cho từng kỳ**" | [PRD-2.1] §4.1 |
| ⚠ CONFLICT | [PRD-3.0] §4.2: "**Công chuẩn: lấy từ Workday**" (không tự tính) | [PRD-3.0] |

## A2. Chấm công — nguyên tắc ([HR-QT] §V.1)

- "Ngày công của CBNV được xác định dựa theo bảng chấm công từ hệ thống phần mềm nhân sự do **thư ký từng Phòng ban/Công trường** theo dõi ngày làm việc thực tế và tổng hợp chấm công vào **ngày 13-19 hàng tháng**, bảng chấm công phải có **xác nhận phê duyệt của Trưởng Phòng ban/Công trường**."
  > ⚠ **CONFLICT NỘI BỘ trong cùng file [HR-QT]**: §V.1 nói tổng hợp chấm công **ngày 13–19**, nhưng bảng diễn giải §IV.2 bước 1 nói **"Ngày 16-19 hàng tháng"**, còn timeline Mắt Bão nói thư ký chấm công **16–17**. Ba mốc khác nhau → phải hỏi lại.
- Nghỉ phép/ốm/chế độ: "CBNV **chủ động đăng ký** phép năm/nghỉ ốm… trên hệ thống phần mềm nhân sự và **được phê duyệt từ Trưởng Phòng ban/Công trường**."
- Nghỉ hưởng lương BHXH: "phải đảm bảo ngày công được chấm đúng với quy định và **chứng từ CBNV gửi về P.NS-TH** làm hồ sơ hưởng chế độ từ cơ quan BHXH."
- Ngày công sai → C&B làm việc trực tiếp với CBNV, yêu cầu thư ký điều chỉnh, TP xác nhận trên BCC.
- Đi làm ngày nghỉ tuần/lễ tết: "thư ký tổng hợp **đăng ký kế hoạch tăng ca** từ CBNV và phải được sự đồng ý **phê duyệt của Trưởng Phòng ban/Công trường/GĐDA trước mỗi kỳ nghỉ lễ, tết**. Khi chấm công C&B đối chiếu lại ngày công chấm thực tế so với danh sách đăng ký nếu chênh lệch yêu cầu thư ký điều chỉnh/giải trình."
- Phép năm: "C&B tổng hợp ngày công vào **danh sách theo dõi phép năm** để rà soát lại việc sử dụng phép và tồn phép của từng CBNV. Trường hợp **phép năm bị âm vượt tiêu chuẩn**, C&B yêu cầu thư ký **điều chỉnh lại ngày công ngay trong tháng**."
- **Ốm công ty**: "**03 ngày/năm dương lịch – nghỉ không liên tục, đăng ký tối đa 1 ngày/lần nghỉ**" — [HR-QT] §IV.2 bước 1.

## A3. Quy định ngày nghỉ ([PRD-2.1] §7 — sheet "Quy định ngày")

- **Phép năm 12 ngày** (**+1 ngày / 5 năm thâm niên**).
- **Quy tắc tính phép theo tháng: ≥ 50% công chuẩn**.
- **Phép tồn dùng đến 31/12 năm kế tiếp**.
- **Nghỉ ốm Cty: 3 ngày/năm**.
- Nghỉ hiếu hỉ, thai sản, nghỉ bù… theo sheet Quy định ngày.
- **Danh mục ngày lễ (tự động hằng năm)**: `01/01` · `5 ngày Tết Âm lịch` · `30/04` · `01/05` · `02/09 + 1 ngày` · `10/03 ÂL`. HR chỉnh được khi cần.

## A4. Tăng ca (OT)

**[HR-QT] §V.4 — Tổng hợp lương tăng ca** (áp cho **Người lao động từ Level 6 trở xuống**, khi làm theo yêu cầu Công ty hoặc theo đăng ký của PB/CT **đã được Ban Lãnh đạo / Phó TGĐ Vận hành / Giám đốc QTNNL phê duyệt TRƯỚC khi thực hiện**):

| Loại ngày | Chế độ |
|---|---|
| **Ngày nghỉ Lễ, Tết theo quy định pháp luật** | "Được **trả thêm 100% tiền lương** cho ngày làm Lễ, Tết. Đồng thời được bố trí **02 ngày nghỉ bù hưởng nguyên lương** cho mỗi ngày làm việc." |
| **Ngày truyền thống Công ty (Coteccons Day), ngày nghỉ bổ sung do Công ty quyết định, ngày nghỉ bù do Lễ/Tết trùng vào ngày nghỉ hằng tuần** | "Được bố trí **01 ngày nghỉ bù hưởng nguyên lương** cho mỗi ngày làm việc." |
| Phương án chi trả khác | "phải được **Phó TGĐ Vận hành và/hoặc Giám đốc QTNNL phê duyệt trước khi thực hiện**, đồng thời bảo đảm tuân thủ quy định pháp luật hiện hành." |

"Ngày công tăng ca sẽ căn cứ vào **bảng tổng hợp tăng ca được đối chiếu giữa bảng đăng ký tăng ca và thực tế chấm tăng ca** do Trưởng Phòng ban/Công trình ký xác nhận."

**[PRD-2.1] §5.5 — Tăng ca (OT):**
- "Nhận **loại giờ** từ hệ thống gốc. Payroll cho phép **cấu hình hệ số nhân (multiplier) tách biệt cho nhóm Chính thức và Mắt Bão**."
- "Mặc định theo quy định hiện hành: **Chủ nhật 200%**; ngày Lễ/Tết theo luật: **trả thêm 100% tiền lương và ghi nhận 2 ngày nghỉ bù** cho mỗi ngày đi làm (**một số trường hợp 300% theo danh sách**); ngày truyền thống/bổ sung/nghỉ bù: ghi nhận **1 ngày nghỉ bù** cho mỗi ngày đi làm. **Tách OT chịu thuế/không chịu thuế**."
- Ký hiệu công: đi làm ngày Lễ (**TC 100%/300%**); đi làm ngày CN (**TC 200%**) — §4.2.
- "Đăng ký đi làm lễ: NLĐ đăng ký hoặc **Thư ký import file** → **trưởng bộ phận duyệt** → gửi về HR; ngày lễ cho phép thiết lập tự động theo danh mục ngày lễ hằng năm."

> ⚠ **CONFLICT / GAP**: [HR-QT] **KHÔNG nói gì về hệ số Chủ nhật 200%** và không nói mức 300%. [PRD-2.1] bổ sung 200%/300%. Cần chốt: 300% áp cho ai ("theo danh sách" nào)? "Trả thêm 100%" nghĩa là tổng 200% hay chỉ thêm 100% trên nền công đã hưởng?
> ⚠ **GAP**: OT cho Level 7 trở lên — [HR-QT] chỉ quy định "Level 6 trở xuống" → chính sách cho Level ≥7 = **MISSING**.

## A5. Công thức lương chính ([HR-QT] §V.4 + [PRD-2.1] §5.1.1–5.1.2)

```
Tổng lương trong tháng = Lương thử việc + Lương chính thức

Lương thử việc   = mức lương thử việc   × số ngày công thử việc   / số ngày công tiêu chuẩn trong tháng
Lương chính thức = mức lương chính thức × số ngày công chính thức / số ngày công tiêu chuẩn trong tháng
```
- "Đối với **điều chỉnh lương, bổ nhiệm giữa kỳ công**, lương cũng được tính theo **ngày phát sinh thực tế**." — [HR-QT].
- **Đơn giá thử việc = 85%**, chính thức = 100%: "Lương thử việc = số ngày giai đoạn thử việc × đơn giá lương thử việc (**85%**); Lương chính thức = số ngày giai đoạn chính thức × đơn giá lương chính thức (**100%**)." — [PRD-2.1] §5.1.1. *(Con số 85% chỉ có ở PRD-2.1, [HR-QT] không nêu %.)*
- **Phụ cấp trách nhiệm** = `số ngày hưởng phụ cấp × (định mức phụ cấp / ngày công chuẩn)`, "tách theo ngày hiệu lực nếu thay đổi giữa kỳ" — [PRD-2.1] §5.1.2. [PRD-3.0] §4.3: "Phụ cấp trách nhiệm: **lấy ngày hiệu lực để apply, nếu bổ nhiệm giữa kỳ công**".

## A6. Phụ cấp — nguyên tắc chung

**[HR-QT] §V.3 — công thức gốc:**
```
Phụ cấp được hưởng = Định mức phụ cấp được hưởng theo quy định của tháng
                     × Ngày công hưởng lương Công ty chi trả
                     ÷ Công chuẩn của tháng
```

**[PRD-2.1] §5.2 — Pro-rata:**
> "Mọi phụ cấp cố định theo tháng (Điện thoại, Nhiên liệu/Xăng xe, Đi lại, Công trường + Công tác xa, Công trường xa, Khác…) đều tính: **(Định mức phụ cấp / Ngày công chuẩn) × Số ngày hưởng phụ cấp**."

**QUY TẮC DƯỚI 14 NGÀY** (3 file đều nói, gần trùng khớp):
- [PRD-2.1] §5.2: "Nếu **tổng số ngày làm việc thực tế trong kỳ dưới 14 ngày**, phụ cấp được tính theo tỷ lệ: **Số ngày hưởng = ngày làm việc thực tế + ngày nghỉ lễ trong tháng** (**không tính phép, nghỉ hưởng lương khác, không lương**). Khi có điều động, số ngày hưởng được chia thực tế theo từng bộ phận và áp định mức của từng bộ phận. Quy tắc này áp dụng cho các phụ cấp **Nhiên liệu/Xăng xe, Đi lại, Điện thoại** và các phụ cấp cố định tháng tương tự."
- [HR-QT] §V.3: "Trường hợp số ngày đi làm thực tế **dưới 14 (mười bốn) ngày**, phụ cấp được tính theo tỷ lệ **ngày làm việc thực tế và ngày nghỉ lễ trong tháng**." (áp cho: điện thoại, đi lại, nhiên liệu/xăng xe, ô tô, trách nhiệm…)
- [PRD-3.0] §4.3: "Phụ cấp điện thoại, nhiên liệu, đi lại, **trách nhiệm, ô tô, phụ cấp duyệt riêng** được tính theo ngày hưởng lương thực tế trong tháng dựa theo định mức. Trường hợp số ngày đi làm thực tế dưới 14 ngày, phụ cấp được tính theo tỷ lệ ngày làm việc thực tế và ngày nghỉ lễ trong tháng."

**ĐIỀU ĐỘNG**: "Tất cả các loại phụ cấp khi có điều động sẽ được tính **pro-rata theo ngày thực tế từng bộ phận**" — [PRD-3.0] §4.3. "hệ thống **tự động tách dòng dữ liệu, không xử lý thủ công**" — [PRD-2.1] §5.2.

**TỜ TRÌNH (duyệt riêng)**: "Admin/HR nhập danh sách **MSNV – loại phụ cấp – định mức – số Tờ trình – ngày hiệu lực áp dụng**. Định mức Tờ trình **ghi đè định mức theo Quy định chung** kể từ ngày hiệu lực, và **vẫn chịu quy tắc pro-rata/dưới 14 ngày**." — [PRD-2.1] §5.2. [PRD-3.0]: "Cho up định mức phụ cấp duyệt riêng có ngày hiệu lực: **từ ngày, đến ngày**…"

**THUẾ**: "mỗi loại phụ cấp phải **tách phần tính thuế (Taxable) và không tính thuế (Non-tax)**" — [PRD-2.1] §5.2. [HR-QT] §V.3: "C&B **tách riêng khoản phụ cấp tính thuế và không tính thuế** đưa vào bảng lương."

**Các case đặc biệt phải xử lý ([HR-QT] §V.3):**
- **CBNV tăng mới trong tháng**: cập nhật **nơi tuyển dụng, nơi công tác, nơi cư trú**; "Xác định số công thực tế làm trong tháng để được hưởng phụ cấp so với công chuẩn của tháng đó."
- **CBNV điều động trong tháng**: "cần xác định rõ số công thực tế làm việc của từng Phòng ban/Công trường và áp dụng theo đúng định mức phụ cấp quy định."
- **CBNV ký HĐCT sau thử việc**: "trong tổng công thực tế làm việc trong tháng cần **tách công thử việc và công sau khi ký HĐCT** để áp dụng mức phụ cấp đúng quy định."
- **Điều chỉnh thông tin cá nhân** (nơi tuyển dụng, nơi cư trú, bằng cấp) → ảnh hưởng mức phụ cấp → cập nhật ngay tại thời điểm điều chỉnh.
- **Hưởng theo tờ trình riêng**: "Cần kiểm tra **điều kiện được hưởng, thời điểm được hưởng** theo tờ trình được ký duyệt đầy đủ… Nếu có thay đổi cần có **xác nhận từ Trưởng Phòng ban/Công trường và thông báo đến CBNV trước khi thanh toán lương**."
- Nhóm đặc thù: "ngoài áp dụng theo chính sách chung của công ty, nhóm đối tượng này được áp dụng thêm **chính sách riêng theo tờ trình được đề xuất từ Trưởng PB/CT và phê duyệt của BTGĐ**."

## A7. Phụ cấp (1) — CƠM / SUẤT ĂN

**Số bữa/ngày** ([PRD-2.1] §5.3.1):

| Đối tượng / điều kiện | Số bữa |
|---|---|
| **Văn phòng** | **1 bữa/ngày** |
| **Công trường/dự án khoảng cách < 30 km** (kèm điều kiện an ninh theo quy định) | **2 bữa/ngày** |
| **Công trường/dự án khoảng cách ≥ 30 km** | **3 bữa/ngày** |
| **Làm việc ≤ 4 tiếng/ngày (mọi đối tượng)** | **0 bữa** (không tính suất ăn) |

- **Đơn giá suất ăn: cấu hình được, mặc định 45.000 đ/bữa** — [PRD-2.1] §5.3.1; [PRD-3.0] §4.3 ("set định mức 1-2-3 bữa/ngày, **45k/bữa**. Trên 4 tiếng mới dc tính cơm").
- **Phụ cấp cơm = Tổng số suất ăn × đơn giá.**
- **Miễn thuế**: "Phần **≤ 730.000 đ/tháng** ghi cột **Non-tax**; phần vượt ghi cột **Taxable**." — [PRD-2.1] §5.2, §5.3.1.
- **Cơm ngoài quy định** ([HR-QT] §V.3): "Bữa ăn **ngày Chủ nhật** được chấm nếu CBNV có đi làm ngày chủ nhật (**Áp dụng cho Công trường**). Thư ký chấm bữa ăn và có xác nhận của Trưởng Phòng ban/Công trường." · "**Bữa ăn chấm đêm import theo mẫu**."
- "Suất cơm đi làm **Chủ nhật/ca đêm/lễ** do thư ký công trường chấm và gửi về, hệ thống **cộng thêm** vào tổng suất ăn của bộ phận tương ứng." — [PRD-2.1] §5.3.1.
- **Điều động**: "số suất ăn được tổng hợp **riêng theo từng bộ phận** (bộ phận 1/2/3) với quy tắc bữa ăn của từng nơi."
- Chỉ tiêu tổng hợp suất ăn ([PRD-2.1] §5.1.5): suất cơm ngày thường · suất cơm **tăng ca đêm** · cơm **ngày Chủ nhật/lễ** · **cơm bổ sung của tháng trước (nếu có)**.
- Báo cáo §6.4 tách: **P1 (không điều động)**, **P2 (điều động trong tháng)**, cơm tăng ca đêm, cơm Chủ nhật.

## A8. Phụ cấp (2) — ĐIỆN THOẠI

**Định mức theo ngạch chức danh × VP/CT** ([PRD-2.1] §5.3.2 — theo Quy định cấp bậc chức danh hiện hành):

| Ngạch chức danh | Văn phòng (đ/tháng) | Công trường (đ/tháng) |
|---|---|---|
| QL.01 | 1.000.000 | 1.000.000 |
| QL.02 | 800.000 | 1.000.000 |
| QL.03 – QL.04 | 800.000 | 800.000 |
| QL.05 – QL.06 | 600.000 | 600.000 |
| CV.01 – CV.02 | 300.000 | 400.000 |
| NV.01 – NV.02 | 300.000 | 400.000 |
| NV.03 – NV.05 | 200.000 | 300.000 |
| **Thử việc (TV)** | **0** | **300.000** |

- "Áp dụng **pro-rata theo ngày công và quy tắc dưới 14 ngày**; khi **điều động, tính theo định mức của từng bộ phận theo số ngày tại mỗi nơi**."
- [PRD-3.0] §4.3 chỉ nói: "Phụ cấp điện thoại: **theo level**" (không có bảng).

## A9. Phụ cấp (3) — NHIÊN LIỆU / XĂNG XE / Ô TÔ

**[PRD-2.1] §5.3.3:**
- **Khối Công trường**: "định mức chuẩn **1.000.000 đ/tháng** cho các **level L2 – L6** (theo Quy định chung)."
- **Khối Văn phòng**: "**KHÔNG áp định mức chung** – chi trả **theo Tờ trình** do phòng ban đề xuất, được duyệt riêng. Hệ thống quản lý danh sách này gồm MSNV, bộ phận, định mức và ngày hiệu lực (ví dụ theo Tờ trình hiện hành: **DVKH / QL ĐT Thiết bị / An toàn / QL Kỹ thuật Thi công: 800.000 đ**; **GĐDA: 10.000.000 đ**; **Ban TGĐ: 25.000.000 – 35.000.000 đ định mức ô tô**)."
- **02 tài xế Hà Nội**: "có mức phụ cấp **duyệt riêng theo Tờ trình, cấu hình đích danh theo MSNV**, không theo bảng định mức chung."
- "Áp dụng **pro-rata và quy tắc dưới 14 ngày** (ngày làm việc thực tế + ngày lễ); **điều động chia theo bộ phận**."

**[PRD-3.0] §4.3:**
> "Công trg: **level 2 trở lên**: định mức **1tr/tháng**
> Văn phòng: theo phê duyệt: up duyệt riêng, định mức **800k/tháng**
> Ô tô cấp quản lý: cho up cố định hàng tháng: **L7: 10tr, L8: 25TR, TGĐ: 35 TR**"

> ⚠ **CONFLICT #1**: công trường — [PRD-2.1] "**L2 – L6**" (có trần trên) vs [PRD-3.0] "**level 2 trở lên**" (không trần).
> ⚠ **CONFLICT #2**: ô tô cấp quản lý — [PRD-2.1] gán theo chức danh (**GĐDA 10tr; Ban TGĐ 25–35tr**) vs [PRD-3.0] gán theo level (**L7 10tr; L8 25tr; TGĐ 35tr**). Cần map GĐDA↔L7, Ban TGĐ↔L8.

## A10. Phụ cấp (5) — ĐI LẠI

**Cách xác định** ([PRD-2.1] §5.3.4):
> "Xác định theo: **Nơi tuyển dụng / Khu vực xét phụ cấp × Tỉnh của bộ phận làm việc** → tra bảng **Danh mục khoảng cách (DM Khoảng cách)** để ra **dải khoảng cách**; sau đó tra định mức theo **dải khoảng cách × nhóm đối tượng**."

**Nhóm đối tượng (theo Quy định)**: (1) **CHT / CHT ME**; (2) CBNV ngạch từ **NV.01 trình độ Đại học trở lên** (không gồm CHT); (3) CBNV ngạch từ **NV.01 trình độ Cao đẳng / Trung cấp / Nghề**; (4) **NV.02**.

| Khoảng cách / Khu vực | CHT, CHT ME | ĐH trở lên | CĐ/TC/Nghề | NV.02 |
|---|---|---|---|---|
| Dưới 30 km | 0 | 0 | 0 | 0 |
| 30 – 100 km | 900.000 | 500.000 | 350.000 | 250.000 |
| Trên 100 km | 1.400.000 | 1.100.000 | 850.000 | 550.000 |
| Miền Trung (từ HN/HCM) | 7.200.000 | 3.600.000 | 2.700.000 | 1.800.000 |
| Nam Trung Bộ (từ HCM) | 6.000.000 | 3.000.000 | 2.200.000 | 1.500.000 |
| Phú Quốc (từ HCM) | 6.000.000 | 3.000.000 | 2.200.000 | 1.500.000 |
| Miền Nam (từ HN) / Miền Bắc (từ HCM) | 11.200.000 | 5.600.000 | 4.200.000 | 2.800.000 |

- "Áp dụng **pro-rata, quy tắc dưới 14 ngày và chia theo bộ phận khi điều động** (Ví dụ 2)."
- [PRD-3.0] §4.3: "Phụ cấp đi lại phức tạp: Tự động tính dựa trên **Mức lương cơ bản cấp bậc, Nơi làm việc, Nơi cư trú, và Nơi tuyển dụng**."
  > ⚠ **GAP/CONFLICT nhẹ**: [PRD-3.0] thêm biến "**Mức lương cơ bản cấp bậc**" vào công thức đi lại — [PRD-2.1] KHÔNG dùng biến này (chỉ dùng khoảng cách × nhóm đối tượng theo trình độ/chức danh). Cần chốt.

## A11. Phụ cấp (4) — CÔNG TRƯỜNG + CÔNG TÁC XA

([PRD-2.1] §5.3.5)

| Khối | Khoảng cách / Khu vực | Đối tượng 1 (ĐH trở lên) | Đối tượng 2 (CĐ/TC/Nghề) |
|---|---|---|---|
| Công trường | Dưới 30 km | 1.000.000 | 500.000 |
| Công trường | 30 – 100 km | 2.000.000 | 1.200.000 |
| Công trường | Trên 100 km / Phú Quốc | 2.500.000 | 1.500.000 |
| Công trường | Miền Trung / Nam Trung Bộ / khác miền | 3.000.000 | 2.000.000 |
| Văn phòng | Dưới 30 km | 0 | 0 |
| Văn phòng | 30 – 100 km | 1.000.000 | 700.000 |
| Văn phòng | Trên 100 km / Phú Quốc | 1.500.000 | 1.000.000 |
| Văn phòng | Miền Trung / Nam Trung Bộ / khác miền | 2.000.000 | 1.500.000 |

## A12. Phụ cấp (6) — CÔNG TRƯỜNG XA / KHÓ KHĂN (dự án đặc thù)

([PRD-2.1] §5.3.6) — "định mức theo chức danh tại dự án, quản trị dạng bảng (**Dự án × Chức danh → mức**)":

**Dự án Quan Lạn:**
| Chức danh | Mức (đ/tháng) |
|---|---|
| CHT / CHT ME | 5.000.000 |
| CHP / CHP ME | 4.000.000 |
| GS / CV | 3.000.000 |
| Tài xế / Admin / Thủ kho / Bảo vệ | 2.000.000 |

**Dự án Chingluh**: "CHT **2.000.000** → BV **500.000**" *(chỉ nêu 2 đầu mút — bậc trung gian **MISSING**)*.

**Làng Tây – Hòn Thơm**: "phụ cấp khó khăn **theo Tờ trình**, mức **2.000.000 đ/tháng** cho các gói **2B-6BL & 2B-18BL & MEP**; quản trị theo dự án với **ngày hiệu lực của Tờ trình**."

## A13. Phụ cấp (7) — KHÁC (duyệt riêng)

([PRD-2.1] §5.3.7)
- "Thủ kho các công trường **1.500.000 – 2.000.000 đ**"
- "GS bảo hành/bảo trì có **combo xăng xe + công tác xa + đi lại + khác**"
- Quản lý trong danh sách "**Theo dõi duyệt riêng**": MSNV, bộ phận, chức danh, từng loại phụ cấp **(2) → (7)**, ghi chú, tổng phụ cấp; "hệ thống dùng danh sách này **thay cho** định mức chung."
- **Phụ cấp GĐDA**: "**không áp dụng** phụ cấp công trường/đi lại theo bảng chung (chỉ hưởng theo Tờ trình riêng nếu có)."
- Ngoài ra Payroll Master còn có cột phụ cấp **nhà ở** ([PRD-2.1] §6.3) — **quy tắc tính: MISSING**.

## A14. TRUY THU / TRUY LĨNH

([PRD-2.1] §4.3)
> "**Truy thu/Truy lĩnh trước khóa kỳ**: trong phạm vi kỳ chưa khóa, khi định mức phụ cấp của nhân viên **thay đổi có hiệu lực hồi tố** (ví dụ: cập nhật **trình độ học vấn, nơi tuyển dụng, chức danh theo Tờ trình**), hệ thống tự tính chênh lệch **Phụ cấp truy thu/truy lĩnh = (định mức mới – định mức cũ) theo số ngày công tương ứng**, thể hiện thành **cột riêng** trên bảng phụ cấp (tương tự cột "**Phụ cấp truy thu/truy lĩnh (3)**" và **sheet "Truy lãnh"** trong file HR hiện hành), **kèm lý do**."

**Sau khóa kỳ**: "Không phát sinh biến động: mọi đơn duyệt muộn/sửa công trên hệ thống gốc sau ngày chốt sẽ **không được cập nhật hay truy thu vào tháng sau**."

**Truy thu/thoái thu BHXH** ([PRD-3.0] §4.6): "Hỗ trợ **Import file Excel theo lô (Batch)** để truy thu/thoái thu BHXH. Lưu ý: Hệ thống cần có thể **tự tính tiền lãi nộp chậm bảo hiểm**."
Bảng công chi tiết còn có cột "**số ngày công truy thu/truy lĩnh**" ([PRD-2.1] §6.4).
BHXH có "**các cột điều chỉnh (Đ/C) khi có truy đóng/hoàn trả**" ([PRD-2.1] §5.1.4).

> ⚠ **TENSION cần chốt**: [PRD-2.1] cấm truy thu **công** sau khóa kỳ, nhưng [PRD-3.0] yêu cầu batch truy thu/thoái thu **BHXH** + tính lãi nộp chậm. Hai cơ chế này phải cùng tồn tại (khác đối tượng: công vs BHXH) — cần khẳng định với khách hàng.

## A15. BHXH / BHYT / BHTN

**Đối tượng tham gia trong tháng** ([HR-QT] §V.2):
> "Ký hợp đồng chính thức (**tổng số ngày nghỉ không lương; nghỉ ốm dài ngày; nghỉ thai sản; nghỉ việc; thử việc >= 14 ngày thì KHÔNG tính BHXH**, tính từ **ngày 01 – ngày cuối của tháng**)"

[PRD-3.0] §4.6 — **Luật 14 ngày**: "Tự động đếm số ngày nghỉ không lương/thai sản và loại ngày thử việc… (áp cho thử việc vào chính thức trong kỳ) trong tháng (**chu kỳ mùng 1 → cuối tháng**). Nếu **>= 14 ngày → Không trích đóng BHXH tháng đó**."

**Công thức** ([HR-QT] §V.2):
```
Mức tiền đóng BHXH/BHYT/BHTN hàng tháng
  = Mức tiền lương tháng đóng BHXH bắt buộc × Tỷ lệ % đóng
```

**Lương đóng BHXH tại Unicons**: "là **mức lương hợp đồng lao động và phụ cấp trách nhiệm**."

**Trần đóng**: "Mức tiền đóng **BHXH, BHYT tối đa không quá 20 lần mức lương cơ sở** và **mức đóng tiền BHTN tối đa không quá 20 lần mức lương tối thiểu vùng**."
> Giá trị tuyệt đối của "mức lương cơ sở" / "mức lương tối thiểu vùng" tại thời điểm áp dụng: **MISSING**. [PRD-3.0]: "Hệ thống **tự động cập nhật trần đóng BHXH theo quy định Nhà nước, tỷ lệ đóng**…"

**Tỷ lệ — CBNV Việt Nam: tổng 32% (Công ty 21.5% / CBNV 10.5%)** ([HR-QT] §V.2):

| Bên | BHXH-HT | BHXH ÔĐ-TS | BHXH TNLĐ-BNN | BHTN | BHYT | **Tổng** |
|---|---|---|---|---|---|---|
| **Công ty** | 14% | 3% | 0.5% | 1% | 3% | **21.5%** |
| **CBNV** | 8% | – | – | 1% | 1.5% | **10.5%** |
| | | | | | **Tổng cộng** | **32%** |

**Tỷ lệ — CBNV nước ngoài: tổng 30% (Công ty 20.5% / CBNV 9.5%)** ([HR-QT] §V.2):

| Bên | BHXH-HT | BHXH ÔĐ-TS | BHXH TNLĐ-BNN | BHTN | BHYT | **Tổng** |
|---|---|---|---|---|---|---|
| **Công ty** | 14% | 3% | 0.5% | – | 3% | **20.5%** |
| **CBNV** | 8% | – | – | – | 1.5% | **9.5%** |
| | | | | | **Tổng cộng** | **30%** |

Đối tượng nước ngoài: "công dân nước ngoài làm việc tại Việt Nam thuộc đối tượng tham gia BHXH bắt buộc khi có **giấy phép lao động hoặc chứng chỉ hành nghề hoặc giấy phép hành nghề** do cơ quan có thẩm quyền của Việt Nam cấp và có **hợp đồng lao động từ đủ 01 năm trở lên**."

**Cách [PRD-2.1] §5.1.4 diễn đạt** (khớp về tổng, khác cách gộp):
> "tính đúng các khoản trích BHXH/BHYT/BHTN của **nhân viên (8% / 1.5% / 1%)** và của **công ty (17% / 0.5% / 3% / 1% + 2% KPCĐ)**, kèm các **cột điều chỉnh (Đ/C)** khi có truy đóng/hoàn trả."
> *(17% = 14% HT + 3% ÔĐ-TS; cộng 0.5% TNLĐ + 3% BHYT + 1% BHTN = 21.5% → khớp [HR-QT]. Không phải conflict.)*

**Xử lý 2 trục thời gian** ([PRD-2.1] §5.1.4):
> "Do **kỳ công (21 – 20) lệch với kỳ BHXH (01 – cuối tháng)**, hệ thống phải **quy đổi và đếm số ngày làm việc/không làm việc theo tháng dương lịch** để xác định tháng đó có thuộc diện đóng BHXH hay không. Các loại ngày không tính đóng BHXH (**thử việc, nghỉ không lương, nghỉ thai sản, nghỉ ốm BHXH…**) phải được **đếm riêng**."

## A16. CÔNG ĐOÀN

([HR-QT] §V.4)
- **Đoàn phí công đoàn (CĐP) — trích từ CBNV**: "**0.5% tiền lương làm căn cứ đóng bảo hiểm xã hội** theo quy định của pháp luật về BHXH, nhưng **mức đóng đoàn phí hàng tháng tối đa chỉ bằng 10% mức lương cơ sở** theo quy định của Nhà nước."
- **Kinh phí công đoàn (KPCĐ) — chi phí Công ty**: "**KPCĐ 2% tiền lương làm căn cứ đóng bảo hiểm xã hội**." (khớp [PRD-2.1] §5.1.4 "+ 2% KPCĐ")
- [PRD-3.0] §4.6: "**CĐP và KPCĐ cập nhật và trích theo quy định pháp luật hiện hành**" (cấu hình được).

## A17. CÁC KHOẢN GIẢM TRỪ KHÁC

([HR-QT] §V.4): "Hàng tháng C&B kiểm tra rà soát lại các khoản trừ khác như **phí thu hộ bảo hiểm sức khỏe, phí khám sức khỏe tự nguyện, …** để cập nhật vào bảng lương."
Payroll Master còn có "**các khoản cộng/trừ sau thuế**" ([PRD-2.1] §6.3).

## A18. THUẾ TNCN

**Có trong tài liệu:**
- "Hàng tháng C&B **tạm trích thuế TNCN** của CBNV." — [HR-QT] §V.5.
- "Hàng năm C&B sẽ thực hiện **quyết toán thuế TNCN thay** đối với CBNV **đủ điều kiện ủy quyền và có gửi bản gốc giấy ủy quyền** quyết toán thuế TNCN về Công ty **hoặc xuất chứng từ khấu trừ thuế và xác nhận thu nhập** để CBNV tự quyết toán theo quy định pháp luật hiện hành." — [HR-QT] §V.5.
- **Phụ cấp cơm miễn thuế tối đa 730.000 đ/tháng**, phần vượt tính thuế — [PRD-2.1] §5.2, §5.3.1.
- Mọi phụ cấp phải **tách cột Taxable / Non-tax**; OT cũng "**tách OT chịu thuế / không chịu thuế**" — [PRD-2.1] §5.2, §5.5, §6.3.
- "Thuế: **linh hoạt định nghĩa các khoản thu nhập miễn thuế** (tùy theo cách diễn giải luật của công ty)." — [PRD-3.0] §4.6.
- "Trích BHXH, Trích thuế TNCN … **theo quy định pháp luật hiện hành**." — [PRD-3.0] §4.6.
- Báo cáo: "**Báo cáo Quyết toán Thuế TNCN cuối năm**"; "Cho xuất **lũy kế thu nhập tại từng thời điểm**" — [PRD-3.0] §5.

**Giảm trừ gia cảnh / NPT — QUY TRÌNH** ([HR-QT] §V.4):
- "Các hồ sơ đăng ký Giảm trừ gia cảnh/NPT được gửi về P.NS-TH **trước ngày 15 hàng tháng** thì sẽ được kiểm tra đăng ký **trong kỳ lương tháng đó**, **sau ngày 15** hàng tháng hồ sơ sẽ được kiểm tra và đăng ký vào **kỳ lương tháng sau**."
- "C&B kiểm tra thông tin trên hồ sơ… nếu hợp lệ C&B sẽ **gửi đăng ký với cơ quan Thuế**, khi cơ quan Thuế trả kết quả về C&B sẽ **cập nhật thông tin NPT lên bảng lương** đối với hồ sơ đăng ký thành công. Những hồ sơ đăng ký không thành công C&B sẽ **phản hồi lại cho CBNV**."
- "Đối với những trường hợp đăng ký thành công thì **chỉ được cập nhật và tính thuế tại tháng đăng ký thành công**; việc **tính lại phần thu nhập tính thuế và áp dụng thời gian tính NPT theo ngày hiệu lực sẽ được C&B thực hiện tính toán lại trong kỳ quyết toán thuế cuối năm**."

> ### 🔴 MISSING NGHIÊM TRỌNG — thuế TNCN
> - **Biểu thuế lũy tiến từng phần (7 bậc, thuế suất 5%–35%, ngưỡng thu nhập tính thuế mỗi bậc): KHÔNG CÓ trong bất kỳ file nào.**
> - **Mức giảm trừ bản thân (đ/tháng): KHÔNG CÓ.**
> - **Mức giảm trừ mỗi người phụ thuộc (đ/tháng): KHÔNG CÓ.**
> - Thuế suất cho cá nhân **không cư trú** / hợp đồng ngắn hạn (khấu trừ 10%): KHÔNG CÓ.
> - Danh sách đầy đủ khoản thu nhập miễn thuế (ngoài cơm 730k): KHÔNG CÓ.
> → Tất cả chỉ được viện dẫn "**theo quy định pháp luật hiện hành**". **BR phải hỏi bù hoặc chốt là hệ thống cấu hình được toàn bộ biểu thuế + mức giảm trừ.**

## A19. THƯỞNG

**Danh sách khoản thưởng ([HR-QT] §V.4):**
- **Lì xì đầu năm**: "Mức chi tùy theo thông báo từng năm, áp dụng cho CBNV **có đi làm vào ngày đầu năm sau kỳ nghỉ Tết nguyên đán**."
- **Lương tháng 13**: "Sẽ có thông báo trước khi được chi. **Tối đa được 01 tháng lương bình quân 12 tháng**. Đối với những CBNV có thời gian làm việc **chưa đủ 12 tháng sẽ được tính theo tỷ lệ thời gian làm việc thực tế**." ([PRD-3.0]: "Lương tháng 13: 1 tháng BQ theo thời gian tính thưởng")
- **Tết Âm lịch**: "Tùy theo tình hình SXKD, sẽ có thông báo trước khi được chi. **Tối đa được 01 tháng lương bình quân 12 tháng và KHÔNG QUÁ 15 TRIỆU/CBNV**. Đối với những CBNV có thời gian làm việc chưa đủ 12 tháng sẽ được tính theo tỷ lệ thời gian làm việc thực tế." ([PRD-3.0]: "Tết âm: 1 tháng BQ, **cap 15tr** theo thời gian tính thưởng (**có thể cho set linh động định mức**)")
- **KPI**: "**phân bổ theo kpi công ty, khối/BU/bộ phận, cá nhân**" (cả 2 file dùng đúng câu này).
- **Thưởng khác**: "Thưởng đột xuất phòng đấu thầu xây dựng và ME, thưởng sáng kiến… khi có phát sinh."
- **Thưởng cá nhân xuất sắc trong năm**: "Theo danh sách phê duyệt, C&B thực hiện chi theo đối tượng và mức chi cụ thể theo từng năm."
- **Khoản khác phát sinh**: "tiền du lịch (nếu có chi bằng tiền)… theo danh sách thực tế được phê duyệt."
- **Thưởng dự án/công trình**: "Căn cứ theo đề xuất từ các công trình và Quy chế/Quy trình khen thưởng của công ty, hàng tháng C&B tổng hợp thêm danh sách **thưởng đột xuất, thưởng vượt lợi nhuận** được phê duyệt bởi **TGĐ BU / Hội đồng Khen thưởng Kỷ luật**. → **thiết lập rule tính trên hệ thống**."

**ĐIỀU KIỆN LOẠI TRỪ (áp cho mọi khoản thưởng) — [HR-QT] §V.4:**
1. "Đối tượng được chi thưởng thực tế sẽ **KHÔNG áp dụng cho những CBNV nghỉ việc / có kế hoạch nghỉ việc** đã được Trưởng Phòng ban/Công trường xác nhận thông tin và đang chờ hoàn tất thủ tục nghỉ việc từ Công ty."
2. "Thời gian CBNV **nghỉ thai sản, nghỉ ốm dài hạn và nghỉ việc riêng không lương vì lý do cá nhân lũy kế từ 10 ngày trở lên** trong thời gian xét **KHÔNG tính vào thời gian tính thưởng**." (khớp [PRD-3.0] §4.4)
3. "Đối với **thưởng theo tháng lương (không bao gồm thưởng công trình)** thì **mức lương tính thưởng là mức lương bình quân MƯỜI HAI (12) THÁNG liền kề trước thời điểm xét thưởng**."

**Bổ sung từ [PRD-3.0] §4.4 (Bonus Logic):**
- "Tính dựa trên **Bình quân lương 12 tháng** (**HR sẽ set thời gian xét** để hệ thống tự tính)."
- "**Áp dụng hệ số cho từng công trường.**"
- "**Điều động**: Tính phân tách tỷ lệ thưởng tương ứng với thời gian/tháng làm việc tại từng dự án trong năm. → Phục vụ hạch toán chi phí."
- **Thưởng công trình**: "HR set thời gian xét"; tự động loại trừ ≥10 ngày nghỉ như trên.
- **Đột xuất**: "**quỹ 1 tháng/lần xét**, tính theo **pro-rata**, set mức lương tháng nào → hệ thống tự động tính."
- **VLN (vượt lợi nhuận)**: "**set rule % thưởng tương ứng với quỹ vượt**, tính theo **thời gian và mức độ đóng góp** → **linh động cho HR set up rule**."

## A20. QUYẾT TOÁN PHÉP NĂM (khi nghỉ việc)

([HR-QT] §V.4)
- **Đối tượng**: "CBNV nghỉ việc theo đúng quy định của công ty và **hoàn tất xong các thủ tục liên quan** và **còn phép năm còn hiệu lực chưa dùng hết** tính tại thời điểm nghỉ việc."
- **Thời điểm thanh toán**: "Nếu CBNV **nghỉ việc trước ngày 20** thì được thanh toán **trong kỳ lương tháng đó**; nếu **nghỉ việc sau ngày 20** thì sẽ được thanh toán **trong kỳ lương tháng sau** hoặc kỳ lương gần nhất sau khi hoàn tất thủ tục nghỉ việc."
- **Công thức**:
```
Lương ngày phép = Phép năm còn hiệu lực
                  × Tiền lương bình quân 6 tháng liền kề
                  ÷ Ngày công chuẩn
```
- Payroll Master có cột "**lương phép tồn**" và "**phép tồn**" — [PRD-2.1] §6.3.

## A21. TRỢ CẤP THÔI VIỆC

([HR-QT] §V.4)
- **Đối tượng**: "CBNV nghỉ việc **có ngày nhận việc trước 01/01/2009** chưa nhận khoản trợ cấp này của Công ty **VÀ** CBNV có thời gian làm việc tại Công ty **nhưng không tham gia BHXH mà chưa được chi trả vào lương** (VD: **Nữ nghỉ thai sản; nghỉ ốm dài ngày; CBNV có thời gian thử việc trước 2018 & mức lương chưa bao gồm bảo hiểm thất nghiệp**) và **có chứng từ lưu trữ đầy đủ** (hợp đồng lao động hoặc hợp đồng thử việc)."
- **Thời điểm thanh toán**: giống quyết toán phép năm (trước ngày 20 → kỳ lương tháng đó; sau ngày 20 → kỳ sau).
- **Công thức (nguyên văn trong tài liệu — CÓ LỖI ĐỊNH DẠNG, cần xác nhận lại)**:
> "Phụ cấp được hưởng | = | **0.5** | × | **Tiền lương bình quân 06 tháng trước khi nghỉ việc** | **:** | **Thời gian làm việc để tính trợ cấp thôi việc**"
>
> ⚠ Ký hiệu `:` (chia) ở vị trí cuối gần như chắc chắn là **lỗi trích xuất từ docx** — công thức trợ cấp thôi việc chuẩn là `0.5 × BQ 6 tháng × số năm làm việc để tính trợ cấp` (NHÂN, không CHIA). **BẮT BUỘC hỏi lại khách hàng để chốt.**
- [PRD-3.0] §4.5: "Tính trợ cấp thất nghiệp: thời gian trc 2009, thai sản, ốm đau nguyên tháng ko đóng BHXH… **theo quy định pháp luật hiện hành**."

## A22. HẠCH TOÁN & PHÂN BỔ CHI PHÍ

([HR-QT] §V.4 "Hạch toán chi phí")
- "Chi phí thực tế **tại bộ phận nào sẽ được ghi nhận về đúng bộ phận đó**."
- "Đối với các khoản công trường sẽ **hạch toán đúng về công trường chi thưởng**."
- "**Thưởng định kỳ**: lương tháng 13, tết âm, KPI sẽ được **phân bổ theo thời gian thực tế làm việc của CBNV trong thời gian xét (thường là 12 tháng)**."
- "**Chi phí GĐDA** sẽ được **phân bổ theo các dự án thực tế quản lý theo tỷ lệ phân bổ (dựa theo DOANH THU để ra tỷ lệ phân bổ)**."
- "**Chi phí phòng ban trực tiếp hỗ trợ công trường** sẽ được **phân bổ về công trường theo tỷ lệ đề xuất của trưởng phòng ban liên quan**."

([PRD-3.0] §4.3 — Kiêm nhiệm / Cost Allocation)
- "Dựa vào **tỷ lệ % lấy từ file excel của kế toán hoặc thông tin từ Workday**, phân bổ tổng chi phí lương của NV đó vào các dự án khác nhau. Sau đó thông tin này được **đẩy qua SAP**."
- "**Điều động theo thời gian**: Nếu NV làm 5 ngày dự án A, 20 ngày dự án B → Hệ thống **tách 2 dòng lương/phụ cấp** tương ứng theo tỷ lệ Pro-rata."

Trường hạch toán trên Payroll Master: **Profit/Cost Center, WBS, Funds Center** — [PRD-2.1] §6.3.

## A23. NHÂN SỰ MẮT BÃO (Outsourced Staff)

([PRD-2.1] §6.1)
- **Nhận diện**: "tự động qua trường **EmployeeType** từ API."
- **Lịch trình**: "áp dụng **lịch chốt công SỚM HƠN** nhân sự chính thức." (xem timeline riêng ở S3.2 — chấm công 16–17, trả lương **trước 15h ngày 25**)
- **Phụ cấp**: "Quản trị viên thiết lập **bảng định mức phụ cấp (Grid) trực tiếp trên Payroll (KHÔNG lấy từ Workday)**."
- **OT**: "hệ số nhân (multiplier) **tách biệt** cho nhóm Chính thức và Mắt Bão" — §5.5.
- **Trình ký**: "Template 0 dùng chung định dạng cho Chính thức và Mắt Bão" — §6.3.

## A24. TEMPLATE BIỂU MẪU & BÁO CÁO (danh sách đầy đủ)

**Từ [PRD-2.1]:**
| Mã | Tên | Nội dung |
|---|---|---|
| Template 0 | **Trình ký** | Dùng chung Chính thức & Mắt Bão. Nhân sự điều động: gộp toàn bộ công vào bảng trình ký của **dự án cuối cùng (nơi làm việc ngày 20)** để CHT tại đó ký. |
| Template 2 | **Payroll Master** | File phẳng đầy đủ cho kế toán — cấu trúc chi tiết ở S5.2. |
| §6.4-a | **Bảng chấm công kỳ 21–20** | Ma trận ngày × NV, ký hiệu công, loại ngày, quy ra công theo từng loại, tổng công hưởng, công chuẩn, công truy thu/truy lĩnh, phép năm hiện tại & phép còn lại. **BẢO MẬT.** |
| §6.4-b | **Bảng tính phụ cấp cơm** | P1/P2/cơm đêm/cơm CN/tổng phần cơm/ghi chú điều động. **BẢO MẬT.** |
| §6.4-c | **Bảng tổng hợp phụ cấp tháng** | 8 cột phụ cấp (1)→(8) + PC bộ phận hiện tại/trước/truy thu. **BẢO MẬT.** |
| §6.4-d | **Danh sách theo dõi duyệt riêng và truy lĩnh** | So sánh kỳ trước/kỳ này + **lý do biến động**. **BẢO MẬT.** |
| §6.5 | **Báo cáo Đơn "Treo"** | Tự động gửi Email/Teams cho lãnh đạo tại ngày Cut-off + Dashboard realtime + HR xuất thủ công. |

**Từ [PRD-3.0] §5 — thư viện báo cáo động:**
- Nhóm Lương & Chi phí: Bảng lương tổng hợp (Payroll Master) · **Báo cáo Phân bổ chi phí (Cost Allocation Report) theo chuẩn excel kế toán cần** · **Báo cáo so sánh chênh lệch công/lương giữa các tháng** · **Xuất lũy kế thu nhập tại từng thời điểm**.
- Nhóm Nhân sự: **Báo cáo Headcount** · **Báo cáo Nhân viên mới/Nghỉ việc (Joiner/Leaver)**.
- Nhóm Pháp lý & Ngân hàng: **Template chuyển khoản Ngân hàng (HSBC, Citibank...)** · **Báo cáo trích nộp BHXH** · **Báo cáo Quyết toán Thuế TNCN cuối năm**.
- **Payslip**: "Thiết kế theo template khách hàng yêu cầu, **xuất PDF hoặc bắn qua API về Workday**."

**Từ [HR-QT] — hồ sơ nghiệp vụ:** Bảng chấm công · Bảng tổng hợp chấm công toàn Công ty · Bảng thưởng, phụ cấp · Bảng tính BHXH · Bảng tổng hợp + bảng chi tiết chi lương · **Bảng so sánh lương so với tháng trước** · Bảng phân tích liên quan · Bảng chi phí công đoàn / Kinh phí công đoàn · Bảng tổng hợp số tiền thanh toán BHXH/BHYT/BHTN · **Bảng hạch toán lương** · **Báo cáo số lượng nhân sự** · **Báo cáo tổng hợp chi phí nhân sự hàng tháng**.

## A25. KHÓA KỲ LƯƠNG

([PRD-2.1] §4.3 — **Manual Lock**)
> "HR thực hiện **khóa thủ công** sau khi kiểm soát xong. Sau khi khóa:
> - Hệ thống **ngừng đồng bộ API tháng đó**.
> - **Không phát sinh biến động**: mọi đơn duyệt muộn/sửa công trên hệ thống gốc sau ngày chốt sẽ không được cập nhật hay truy thu vào tháng sau."

([PRD-3.0] §4.1): "**Khóa dữ liệu (Lock Period)**: HR chốt và khóa dữ liệu **theo tháng** để bảo vệ tính toàn vẹn của số liệu."

---

# PHỤ LỤC B — DANH SÁCH CONFLICT & MISSING PHẢI HỎI BÙ (chốt trước khi soạn BR)

## B1. CONFLICT (phải chọn 1)

| # | Chủ đề | [PRD-2.1] | [PRD-3.0] / [HR-QT] |
|---|---|---|---|
| C1 | **Phạm vi tích hợp** | CHỈ Workday. "Không tích hợp với bất kỳ hệ thống HR nào khác" | Workday **+ SAP** (cost allocation, hạch toán) **+ Ngân hàng** (HSBC/Citibank) |
| C2 | **Tập người dùng** | Có role: thư ký công trường, CHT, trưởng bộ phận (duyệt Teams), lãnh đạo (dashboard) | "Chỉ dành cho HR Admin và C&B Staff. **Không có tài khoản** cho nhân viên hay Trưởng bộ phận" |
| C3 | **Multi-tenant** | Không đề cập | "hỗ trợ kiến trúc **Đa công ty (multi-tenant)**, nhiều pháp nhân, chính sách riêng biệt" |
| C4 | **Công chuẩn** | Payroll **TỰ TÍNH** (VP: trừ CN + chiều T7; CT: trừ CN) | "**lấy từ Workday**" |
| C5 | **Nhiên liệu công trường** | "level **L2 – L6**" | "level **2 trở lên**" |
| C6 | **Ô tô cấp quản lý** | GĐDA 10tr; Ban TGĐ 25–35tr (theo chức danh) | **L7: 10tr, L8: 25tr, TGĐ: 35tr** (theo level) |
| C7 | **Biến tính PC đi lại** | khoảng cách × nhóm đối tượng (trình độ/chức danh) | thêm biến "**Mức lương cơ bản cấp bậc**" |
| C8 | **Ngày thư ký chấm công** | — | [HR-QT] tự mâu thuẫn: §V.1 nói **13–19**, §IV.2 nói **16–19**, timeline Mắt Bão nói **16–17** |
| C9 | **OT hệ số** | Chủ nhật **200%**; Lễ/Tết **100%** (+2 nghỉ bù), "một số trường hợp **300%** theo danh sách" | [HR-QT] chỉ có "trả thêm **100%** + 2 ngày nghỉ bù"; **không có 200%/300%** |
| C10 | **Truy thu sau khóa kỳ** | **CẤM** truy thu công sang tháng sau | [PRD-3.0] yêu cầu **batch truy thu/thoái thu BHXH + tính lãi nộp chậm** (khác đối tượng — cần khẳng định cùng tồn tại) |

## B2. MISSING (không tài liệu nào nói)

**Nghiệp vụ — mức nghiêm trọng CAO:**
1. 🔴 **Biểu thuế TNCN lũy tiến (7 bậc, ngưỡng + thuế suất)** — hoàn toàn không có.
2. 🔴 **Mức giảm trừ bản thân** (đ/tháng) — không có.
3. 🔴 **Mức giảm trừ mỗi người phụ thuộc** (đ/tháng) — không có.
4. 🔴 **Công thức trợ cấp thôi việc** — bản trích có ký hiệu `:` (chia) thay vì `×` (nhân) → nghi lỗi OCR, phải xác nhận.
5. 🔴 **Giá trị "mức lương cơ sở" và "mức lương tối thiểu vùng"** áp dụng (để tính trần BHXH/BHYT/BHTN và trần CĐP 10%).
6. 🟠 **Quy tắc tính phụ cấp NHÀ Ở** — có cột trong Payroll Master nhưng không có quy tắc.
7. 🟠 **OT cho Level ≥ 7** — [HR-QT] chỉ quy định "Level 6 trở xuống".
8. 🟠 **Dự án Chingluh** — chỉ có 2 đầu mút (CHT 2tr → BV 500k), thiếu bậc trung gian.
9. 🟠 **"Điều kiện an ninh theo quy định"** cho suất ăn 2 bữa (CT <30km) — không định nghĩa.
10. 🟠 **Danh sách "một số trường hợp 300%"** cho OT ngày lễ — không có danh sách.
11. 🟠 **Layout file chuyển khoản ngân hàng** (HSBC/Citibank/NH nội địa) — chỉ nêu tên.
12. 🟠 **Định mức phụ cấp Mắt Bão** — nói "Admin thiết lập grid" nhưng không có số.
13. 🟡 **Mức lì xì đầu năm** ("tùy theo thông báo từng năm").
14. 🟡 **Rule KPI cụ thể** (chỉ nói "phân bổ theo kpi công ty, khối/BU/bộ phận, cá nhân").
15. 🟡 **Hệ số thưởng "cho từng công trường"** ([PRD-3.0] §4.4) — không có bảng.

**Dự án / phi chức năng:**
16. **Ưu tiên MoSCoW** cho toàn bộ feature (S4.3).
17. **Deadline / go-live / roadmap** (S8.2).
18. **Ngân sách / nguồn lực** (S8.3).
19. **Tech stack** (ngôn ngữ, DB, hosting cloud/on-prem) (S8.1).
20. **SLA khả dụng, backup, DR** (S7.4).
21. **Backlog / Phase 2** (S9.2).
22. **UAT plan, test case đầy đủ, tiêu chí Go/No-Go, parallel-run với Excel** (S10.1).
23. **Môi trường dev/staging/prod, Workday sandbox, SAP test** (S10.2).
24. **Headcount chính xác, số công trường, dung lượng dữ liệu** (S7.3).
25. **Wireframe / UI spec / responsive / theme** (S7.5).

---

## Ghi chú kỹ thuật về nguồn

Trong thư mục `scratchpad/raw-extract/` còn **file thứ 4 không nằm trong 3 file được giao**: `confidential-payroll-handover-assessment-1-param.txt` (610 dòng) — chưa đọc theo phạm vi yêu cầu. Nếu file này chứa đánh giá bàn giao Payroll (Excel engine thật), nó rất có thể **lấp được nhiều mục MISSING ở B2** (đặc biệt biểu thuế TNCN, giảm trừ gia cảnh, công thức trợ cấp thôi việc). **Khuyến nghị: bóc nốt file thứ 4 trước khi soạn BR.**
agentId: a7332b00d4000ffbb (use SendMessage with to: 'a7332b00d4000ffbb', summary: '<5-10 word recap>' to continue this agent)
<usage>subagent_tokens: 123716
tool_uses: 4
duration_ms: 684103</usage>