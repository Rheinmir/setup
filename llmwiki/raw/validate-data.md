Bộ validate data thông thường gồm 5 lớp, đi từ rẻ → đắt:

1. Kiểu &amp; hình dạng (schema): field bắt buộc, kiểu dữ liệu, nullable, độ dài/khoảng giá trị, regex format (email, phone, ISO date), enum. Đây là lớp hay nhất — hầu hết lỗi chết ở đây, thư viện có sẵn (Zod/Pydantic/JSON Schema/DB constraint).

2. Chuẩn hoá trước khi check: trim, lowercase email, ép số, parse ngày về UTC. Validate trên dữ liệu đã chuẩn hoá, không phải raw.

3. Ràng buộc chéo trong bản ghi: end_date &gt;= start_date, tổng dòng = tổng đơn, discount ≤ price, field A bắt buộc khi field B = X.

4. Ràng buộc tham chiếu &amp; duy nhất: FK tồn tại (product_id có thật), unique key (SKU, email), không trùng dòng trong batch. Để DB lo bằng constraint thay vì code app nếu được.

5. Quy tắc nghiệp vụ &amp; sanity: tồn kho không âm, số lượng không vượt ngưỡng vô lý (&gt;1e6), trạng thái chuyển đúng state machine, quyền của user được ghi bản ghi này.

Kèm 2 thứ hay bị quên:

- Báo lỗi gom một lần, có path + code + message, không fail-fast ở lỗi đầu tiên (import/form rất cần).

- Chặn ở biên tin cậy (API/import/upload), không rải validate khắp nơi; bên trong tin schema đã qua.

Nếu bạn đang hỏi cho module inventory (co2-be) thì nói rõ ngữ cảnh — form nhập, import Excel, hay API — mình liệt kê rule cụ thể cho case đó.

⏺ Ran 3 stop hooks

  ⎿  Stop hook error: [python3 "$CLAUDE_PROJECT_DIR/llmwiki/.claude/hooks/[stop.py](http://stop.py)"]: 🩺 [medic gương-soi] phiên ĐỤNG framework mà medic --ci CÓ FAIL — sửa trước khi kết thúc:

    ✗ docs       1 docs CŨ so đĩa: build-overstack-docs

  ▉ FAIL — 1 fail · 1 warn · 17 ok · 0 skip

    → xem đầy đủ: `python3 fdk/tools/[medic.py](http://medic.py)`