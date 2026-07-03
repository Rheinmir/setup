---
name: medic
description: >-
  Cổng sức khoẻ tổng / tuyến phòng thủ cuối của framework overstack — gõ /medic
  (hoặc `medic` ở CLI) để CHỨNG MINH hệ còn khoẻ trong MỘT lệnh: luật còn cắn
  (harness-doctor fire-drill), validator không lệch bản (drift), docs khớp đĩa,
  code compile, eval không regress, backstop git sống. Hub 1-tên — mô tả PHẠM VI
  thay vì nhớ subcommand (`medic` = all · `medic rules` · `medic docs eval`).
  Dùng trước commit/PR, sau khi pull/đổi máy, khi nghi một rule không chặn nữa,
  hoặc vừa thêm skill/rule/generator (medic tự báo nếu quên hàng rào). Trigger:
  /medic, "medic", "chạy medic", "hệ còn khoẻ không", "rà luật có cắn không",
  "cổng phòng thủ cuối", "health gate", "last line of defense".
---

# Skill: medic

> Chìa vạn năng: một lệnh = tuyến phòng thủ cuối. Nó KHÔNG sửa gì — chỉ **chứng minh** hệ còn khoẻ và, nếu không, in đúng chỗ hở + 1 dòng lệnh sửa.

## When to use
- Trước khi commit / mở PR — chốt: đỏ thì đừng đẩy.
- Sau khi kéo bản mới / đổi máy — xem overstack còn nguyên vẹn.
- Nghi một rule "có vẻ không chặn nữa" — rà riêng tầng luật.
- Vừa thêm skill / rule / generator — medic tự báo nếu quên hàng rào cho nó (tự-mở-coverage).
- Chỉ muốn coi cấu trúc phòng thủ đang có — `medic --list`.

## Steps
1. **Chọn phạm vi theo mô tả user** (không bắt nhớ subcommand): toàn bộ → không tham số; một phần → từ khoá khớp tên/tag probe (`rules`, `coverage`, `docs`, `code`, `eval`, `backstop`). Nhiều phạm vi → liệt kê cách nhau khoảng trắng.
2. **Chạy** `python3 fdk/tools/medic.py [phạm vi]` (hoặc `medic [phạm vi]` nếu symlink `~/.local/bin/medic` đã có). Thêm `--ci` khi cần exit-code để chốt (pre-commit/CI): FAIL → exit 1.
3. **Chuyển cho user NGUYÊN output** — medic đã in cô đọng: mỗi probe ✓/⚠/✗ + detail + `↳ sửa`, verdict, recap, cấu trúc thư mục. Đừng cắt gọn phần này.
4. **Nếu có ✗ (fail):** đề nghị chạy đúng 1 dòng `↳ sửa` medic gợi ý; nếu là drift/stale thì chỉ regen/sync, KHÔNG sửa logic. **Xác minh hướng** trước khi sync validator — bản đang CẮN mới là bản đúng (bài học 030726: sync sai hướng làm rail thành đen).
5. **Warn (⚠) = nợ đã biết** (vd coverage 5/17, pre-commit chưa cài) — báo user, không tự ý vá lớn; đó là việc của proposal `030726-medic`.

## Rules
- **Không sửa gì trong lúc rà** — medic chỉ chẩn đoán; sửa là bước riêng, có chủ đích.
- **Tôn trọng fail-open**: một probe lỗi → SKIP, không kết luận "hệ hỏng".
- **Mô tả phạm vi, đừng đẻ lệnh** — user cần kiểm tra chưa có thì thêm probe vào `medic.py` (một chỗ), đừng tạo tool lẻ mới.
- Self-contained: `medic.py` chỉ stdlib; compose tool đã có, không dependency ngoài.
