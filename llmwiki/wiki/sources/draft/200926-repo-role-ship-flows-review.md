---
type: draft
title: "Review đợt repo_role · font Lexend Deca · luồng cài — reviewer độc lập tìm 2 lỗi CAO và 4 lỗi VỪA trước khi push, đã sửa kèm test"
status: done
tags: [review, repo-role, installer, html-font, regression-test]
timestamp: 2026-09-20
---

# Review đợt repo_role, font và luồng cài (20/09/2026)

## Cách review

Commit `813b2b6` được giữ ở local, chưa push, trong lúc một reviewer chạy context riêng soi năm hạng mục: `install.sh`, `install-harness.sh`, `repo_role.py`, `html_font.py` cùng các generator, và hai bộ test mới. Luật giao cho reviewer giống đợt trước: chỉ báo lỗi đã tái hiện được bằng lệnh thật trong thư mục tạm với `HOME` cô lập. Song song, `medic --ci` và `ci-local` (71/71) chạy trên một checkout sạch của chính commit đó và đều xanh, tức các lỗi dưới đây là thứ cổng máy hiện có không bắt được.

## Hai lỗi mức CAO

**Dòng nhãn dính vào dòng cuối của file cấu hình.** `install.sh` thêm `repo_role: downstream` vào `.overstack.yaml` bằng cách nối đuôi. Khi file sẵn có thiếu newline ở cuối, kết quả là `wiki_dir: xrepo_role: downstream`, tức giá trị `wiki_dir` của người dùng bị đổi. Bản sửa chèn newline khi byte cuối không phải xuống dòng. Ca `C1b` trong `install-flows-test.sh` giữ lỗi này không quay lại.

**`html_font.apply()` quét regex trên toàn trang.** Ý định là trỏ các stack `-apple-system,…` chép tay về token `--font-text`. Vì quét cả trang, nó đã làm hỏng thứ đang ship: hai iframe `srcdoc` trong `overstack.html` (memory-map và skill-whiteboard) bị đổi sang `var(--font-text)` trong khi tài liệu con không định nghĩa biến đó, nên chữ bên trong rơi về font mặc định của trình duyệt. Trên input tổng hợp reviewer còn tái hiện được ba kiểu hỏng khác: stack có `"Segoe UI"` bị cắt đôi, nháy đóng của một chuỗi JS bị ăn mất gây lỗi cú pháp, và biểu thức `${x}` trong template string bị nuốt. `html-font-lint` vẫn xanh vì nó chỉ tìm chuỗi ở trang ngoài. Bản sửa chỉ đụng CSS nằm trong khối `<style>` của `<head>`, bỏ qua stack kết thúc bằng `monospace`, và nhận `</HEAD>` không phân biệt hoa thường. Sau khi sinh lại, cả hai iframe trở về nguyên vẹn. Bản sao ở repo engine được chép lại và phát hành thành 3.0.4.

## Bốn lỗi mức VỪA

`repo_role.py` dùng `\s*` trong regex đọc nhãn; vì `\s` khớp cả xuống dòng nên `--set` xoá mất dòng trống và comment ngay dưới dòng nhãn, và `repo_role:` với giá trị nằm ở dòng dưới vẫn bị đọc thành nhãn. Đã đổi sang `[ \t]*` và nhận thêm nhãn có nháy. Hàm chuẩn hoá remote cho ra khoá khác nhau với cùng một repo khi URL ở dạng `ssh://`, có `user@`, hoặc có `/` cuối, khiến sổ máy của role `foreign` tra không ra; nay năm dạng URL ra cùng một khoá. Test font đếm `SKIP parity` là PASS vì `--parity` trả rc 0 khi bỏ qua; nay có rc riêng, SKIP đếm tách, và trên CI thì SKIP bị tính là FAIL. Ca `C1 (declared)` của test luồng cài vẫn tạo `fdk/wiki` nên phá hẳn nhánh đọc nhãn thì ca vẫn PASS; nay ca này chỉ có nhãn, không có `fdk/wiki`, kiểm đúng câu thông báo của nhánh đọc nhãn, và có thêm ca ép cờ `--i-know-this-is-the-framework`.

## Lỗi mức THẤP

Đã sửa: thông báo sai của `--apply` khi trang không có `</head>`; skill `orca-onboard` gọi đường per-project trên dự án dot-layout (nay bỏ qua bootstrap khi thấy `.llmwiki/.harness-stamp`, và câu cảnh báo chỉ sang bootstrap). Chưa sửa, có lý do: `repo_role.py --set` đổi CRLF thành LF trên file Windows (hiếm, không làm hỏng YAML). Nội dung bên trong hai iframe `srcdoc` của `overstack.html` chưa dùng Lexend Deca vì đó là tài liệu con được escape trong thuộc tính; nhúng font vào đó cần sửa nơi sinh ra từng iframe, ghi thành nợ.

## Số đo sau khi sửa

`test_html_font.py` và `test_repo_role.py` 9/9 (thêm hai test hồi quy mang tên `review_`), `install-flows-test.sh` 10 ca, `html-font-lint-test.sh` 6 PASS 0 SKIP, Playwright offline 6/6 (font nạp thật, weight 300, đủ dấu tiếng Việt, contrast từ 7,6:1), engine 59 test và eval 15/15.

## Origin

- Node t8 của graph `200926-repo-role-ship-flows`. Reviewer là subagent chạy context riêng trong phiên 20/09/2026; mọi tái hiện nằm trong thư mục tạm.
- Commit được review: `813b2b6` (local, chưa push tại thời điểm review). Bản sửa nằm ở commit kế tiếp của repo framework và bản 3.0.4 của `Rheinmir/orca-graph`.
