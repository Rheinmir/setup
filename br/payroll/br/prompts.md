# 📒 SỔ PROMPT — dây chuyền Ralph (br/prompts.md)

> MỘT file cho TẤT CẢ prompt. Mỗi frame một mục `## <frame_id>` — mở ra, tìm frame,
> SỬA / THÊM nội dung bằng tay, không cần qua model. Khi chạy (`/br run`), bản ở đây
> được ƯU TIÊN CAO NHẤT (trên queue inline / prompt_file / template mặc định).
> Placeholder được phép: {{muc_tieu}} {{scope_code}} {{scope_test}} {{clause_ids}}
> {{verify_cmd}} {{verify_output}} — máy điền lúc chạy.
> `br-prompts.py sync` chỉ THÊM mục cho frame mới, KHÔNG BAO GIỜ đè mục đã có.


## frame-p01-lich-ky-cong

<!-- mục tiêu: Sinh lịch kỳ công 21–20 và kỳ BHXH 01–cuối tháng chạy song song, tính ngày công chuẩn VP (trừ CN + chiều T7) và CT (trừ CN) cho từng kỳ — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p02-master-data-store

<!-- mục tiêu: Nạp và tra cứu 3 danh mục nền từ CSV: DM Bộ phận (→tỉnh/khối/vùng có ngày hiệu lực), DM Nơi cư trú, DM Khoảng cách (cặp nơi tuyển–tỉnh → dải) — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p03-bang-dinh-muc

<!-- mục tiêu: Kho định mức 4 bảng: điện thoại (ngạch×VP/CT), đi lại (dải×4 nhóm đối tượng), CT+công tác xa (khối×dải×2 đối tượng), CT xa theo dự án×chức danh — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p04-to-trinh-override

<!-- mục tiêu: Danh sách Tờ trình duyệt riêng ghi đè định mức chung theo MSNV/nhóm/dự án kể từ ngày hiệu lực; GĐDA bị loại khỏi PC công trường/đi lại chung — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p05-quy-dinh-nghi

<!-- mục tiêu: Quy định ngày nghỉ: phép năm 12 ngày +1/5 năm thâm niên, tháng đạt ≥50% công chuẩn mới tính phép, phép tồn dùng đến 31/12 năm kế, ốm Cty 3 ngày/năm — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p06-workday-adapter

<!-- mục tiêu: Adapter Workday mock (ranh giới BNAL verified:false): đọc bảng công thô ngày×NV + hồ sơ + EmployeeType + ngày kết thúc thử việc từ CSV thay cho API thật — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p07-parser-ky-hieu

<!-- mục tiêu: Parser ký hiệu công: phân loại 15+ ký hiệu (x, x1, OL, P/F, R/Fo, L, NB, Ts/TS, TSN, ON/OD, TN, Ro, TC100/200/300, ?P) thành thuộc tính máy hiểu — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p08-tach-thu-viec

<!-- mục tiêu: Đếm tách ngày công giai đoạn thử việc / sau thử việc theo 'Ngày kết thúc thử việc', gồm cả ngày nghỉ hưởng lương của từng giai đoạn — nền tính lương 85%/100% — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p09-tach-bo-nhiem

<!-- mục tiêu: Tách 2 giai đoạn trước/sau bổ nhiệm khi có thay đổi lương hoặc PC trách nhiệm giữa kỳ; PC trách nhiệm = ngày hưởng × (định mức / công chuẩn) theo từng giai đoạn — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p10-tach-dieu-dong

<!-- mục tiêu: Đếm ngày công tại TỪNG bộ phận khi điều động giữa kỳ, tách theo loại ngày (làm việc/lễ/phép/nghỉ hưởng lương/không lương) tại mỗi nơi, kèm ngày điều động — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p11-bhxh-hai-truc

<!-- mục tiêu: Quy đổi kỳ công 21–20 sang tháng dương lịch để đếm ngày tính/không tính đóng BHXH, xác định diện đóng, và tính các khoản trích NV 8/1.5/1 + Cty 17/0.5/3/1 + 2% KPCĐ — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p12-suat-an

<!-- mục tiêu: Tổng hợp suất ăn theo từng bộ phận: quy tắc bữa (VP 1 · CT<30km 2 · CT≥30km 3 · ≤4h 0), cộng cơm TC đêm + CN/lễ thư ký chấm + cơm bổ sung tháng trước — phải tái lập đúng Ví dụ 1 = 65 suất — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p13-prorata-engine

<!-- mục tiêu: Engine pro-rata dùng chung: (định mức/công chuẩn)×ngày hưởng; tự kích hoạt quy tắc <14 ngày (ngày hưởng = LV thực tế + lễ) và chia theo bộ phận với định mức từng nơi — tái lập đúng Ví dụ 2 PRD — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p14-pc-com

<!-- mục tiêu: PC cơm = tổng suất ăn × đơn giá 45.000 (cấu hình); tách Non-tax ≤730.000 đ/tháng, phần vượt vào Taxable — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p15-pc-dien-thoai

<!-- mục tiêu: PC điện thoại: tra bảng ngạch × VP/CT (kể cả thử việc VP=0, CT=300k), áp engine pro-rata + <14 ngày + chia bộ phận theo định mức từng nơi — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p16-pc-xang

<!-- mục tiêu: PC nhiên liệu/xăng/ô tô: CT chuẩn 1.000.000 cho L2–L6; VP không mức chung — chỉ qua tờ trình (kể cả 02 tài xế HN đích danh, GĐDA, Ban TGĐ); pro-rata + <14 ngày — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p17-pc-di-lai

<!-- mục tiêu: PC đi lại: xác định nhóm đối tượng (CHT/CHT ME · ĐH+ · CĐ/TC/Nghề · NV.02), tra nơi tuyển dụng × tỉnh bộ phận → dải khoảng cách → định mức; pro-rata + <14 ngày + chia bộ phận — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p18-pc-ct-ctx

<!-- mục tiêu: PC công trường + công tác xa: bảng khối (CT/VP) × dải khoảng cách × 2 đối tượng (ĐH+ / CĐ-TC-Nghề); pro-rata + <14 ngày + chia bộ phận — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p19-pc-ctxa-duan-dacthu

<!-- mục tiêu: PC công trường xa/khó khăn theo dự án đặc thù × chức danh (Quan Lạn, Chingluh) + PC khó khăn Làng Tây – Hòn Thơm theo tờ trình dự án; cộng PC khác (7) từ danh sách duyệt riêng — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p20-truy-thu-truy-linh

<!-- mục tiêu: Truy thu/truy lĩnh trong kỳ CHƯA khóa: định mức đổi hồi tố (trình độ, nơi tuyển, chức danh, tờ trình mới) → chênh = (mới − cũ) × ngày công tương ứng, cột riêng (3) kèm lý do — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p21-ot-engine

<!-- mục tiêu: OT engine: multiplier cấu hình tách Chính thức/Mắt Bão (CN 200%, lễ luật +100% & +2 nghỉ bù/ngày, danh sách 300%, truyền thống +1 nghỉ bù), tách OT thuế/không thuế — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p22-khoa-ky

<!-- mục tiêu: Khóa kỳ manual lock (tier: compensable): HR khóa → ngừng sync API tháng đó, chặn mọi biến động; đơn muộn/sửa công sau chốt không cập nhật và KHÔNG truy thu tháng sau — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p23-mat-bao

<!-- mục tiêu: Nhánh Mắt Bão: nhận diện EmployeeType từ adapter, áp lịch chốt công sớm (assumed ngày 15), lấy định mức từ grid riêng trên Payroll thay vì bảng chung — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p24-phe-duyet-audit

<!-- mục tiêu: Vòng phê duyệt: đơn ?P không cộng công; HR Override có lý do bắt buộc; sync-back trạng thái 'Đã duyệt' về Workday (mock); audit log bất biến cũ→mới+người+lúc+lý do — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p25-template0-trinh-ky

<!-- mục tiêu: Template 0 trình ký: định dạng chung Chính thức + Mắt Bão; NV điều động gộp TOÀN BỘ công tháng vào bảng của dự án nơi làm việc ngày 20 để CHT tại đó ký — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p26-template2-master

<!-- mục tiêu: Template 2 Payroll Master: file phẳng đầy đủ cho kế toán — ngày công các loại, lương TV 85%/CT 100%/PC trách nhiệm, 8 cột phụ cấp tách Taxable/Non-tax, OT, BHXH 2 phía, thuế TNCN, thực nhận, Profit/Cost Center-WBS — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p27-bao-cao-hr-treo

<!-- mục tiêu: Bộ báo cáo bảo mật HR C&B (ma trận công 21–20, bảng cơm P1/P2, tổng hợp PC (1)–(8) + cột (2)(3), danh sách duyệt riêng so kỳ) + báo cáo đơn treo lãnh đạo tại cut-off; MỌI lượt xuất ghi log — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.


## frame-p28-ui-serve

<!-- mục tiêu: Web UI stdlib theo mockup.html: 10 màn hình (dashboard, bảng công, suất ăn, phụ cấp, OT, master data, tờ trình, khóa kỳ 2 bước, báo cáo, đơn treo), role-based ẩn TIỀN với thư ký/CHT, dark/light toggle — sửa/thêm nội dung dưới đây tuỳ ý -->

Bạn là một agent sửa code trong một dây chuyền có kỷ luật. Nhiệm vụ của bạn là làm cho
MỘT bài kiểm tra chuyển từ ĐỎ sang XANH — không hơn.

### Bối cảnh frame
- Frame: `{{frame_id}}`  (điều khoản BR: {{clause_ids}})
- Mục tiêu (chỉ làm đúng cái này): {{muc_tieu}}
- Lệnh nghiệm thu (trọng tài — phải đạt exit 0): `{{verify_cmd}}`

### Kết quả chạy nghiệm thu lần gần nhất (đang ĐỎ)
```
{{verify_output}}
```

### LUẬT BẤT KHẢ XÂM PHẠM (hệ thống sẽ tự cắn nếu bạn phạm — đừng thử)
1. CHỈ được sửa file khớp scope code: {{scope_code}}. Mọi thay đổi ngoài phạm vi này sẽ bị
   REVERT tất định (diff-jail) và tính là không tiến triển.
2. TUYỆT ĐỐI không sửa file test: {{scope_test}}. Đụng vào là loop dừng fail-closed (test-hash).
3. Không chạy lệnh phụ, không cài gói, không truy cập mạng. Chỉ sửa code trong scope.
4. Sửa TỐI THIỂU để bài kiểm tra xanh. Không refactor lân cận, không thêm tính năng ngoài mục tiêu.

### Cách làm
- Đọc output ĐỎ ở trên để hiểu vì sao fail.
- Đọc code trong scope, sửa đúng chỗ gây fail.
- Đừng đoán mò: nếu sửa mà không chắc, ưu tiên thay đổi nhỏ, kiểm chứng được.

Chỉ sửa code. Không giải thích dài dòng.
