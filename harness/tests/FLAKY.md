# Sổ lỗi chập chờn (flaky)

Test chập chờn nghĩa là cùng một commit lúc xanh lúc đỏ. Không được xử lý bằng cách chạy lại cho tới khi xanh.

**Luật (user, 2026-09-29):**
1. Gặp test chập chờn thì ghi ngay một dòng vào bảng dưới, kể cả khi chưa sửa.
2. Khi sửa, phải chạy qua blackbox: `bash harness/tests/blackbox.sh <id>`. Script chạy lệnh của dòng đó **10 lần liên tiếp**, mỗi lần trong một `TMPDIR` mới. Chỉ khi đạt **10/10** mới được đổi trạng thái sang `đã-sửa` và cho merge. Chỉ cần 9/10 là vẫn còn chập chờn.
3. Ghi kết quả blackbox (ngày, số lần pass trên 10, load avg) vào cột "Blackbox".

Cột `lệnh` là thứ `blackbox.sh` chạy nguyên văn từ gốc repo, nên phải giữ nguyên dạng `` `...` ``.

| id | lệnh | triệu chứng | nguyên nhân gốc | trạng thái | blackbox |
|---|---|---|---|---|---|
| stop-budget | `bash harness/tests/stop-budget-test.sh .` | Thời gian chạy vẫn < 28s nhưng R3 auto-index không chạy; baseline pass 1/3 lần khi load avg khoảng 10 | Khối R3 (index_sync `--fix` rồi kiểm tra, trên 2 wiki, 7–10s khi máy tải) chỉ được chừa 6s trong ngân sách mềm 20s, lại còn bị `memory-map` ăn hết phần phụ. Validator R3 và `running_servers` nằm ngoài ngân sách (GH#177) | đã-sửa | 2026-09-29 · 10/10 (24–26s mỗi lần, load avg ~12) |
