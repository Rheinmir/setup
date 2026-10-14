---
type: eval
id: uninstall-turns-off-harness
title: "Gỡ overstack khỏi một dự án — lệnh nào, và cái gì thật sự tắt harness"
input: "Tôi muốn gỡ overstack khỏi một dự án. Chạy lệnh gì? Sau khi gỡ, vì sao hook global trong ~/.claude/settings.json không còn chặn ở dự án đó, và wiki của tôi có bị xoá không?"
expected: "Chạy trong thư mục gốc dự án: curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash -s -- uninstall (hoặc bash .harness/poc-vendor-neutral/uninstall.sh). Thứ tắt harness là việc gỡ con dấu .llmwiki/.harness-stamp: hook global chỉ chạy khi dự án có con dấu đó, nên gỡ xong là hook không gác dự án này nữa, dù engine global ~/.claude/harness vẫn còn cho các dự án khác. Lệnh cũng gỡ đúng hook installer đã thêm trong .claude/settings.json (giữ hook bạn tự viết), CI harness.yml, pre-commit và lõi .harness/poc-vendor-neutral. Wiki .llmwiki/ được GIỮ mặc định; muốn xoá thì thêm --purge-wiki. Lệnh từ chối chạy trong repo framework. Mở phiên agent mới sau khi gỡ."
asserts:
  - 'icontains:uninstall'
  - 'icontains:harness-stamp'
  - 'icontains:--purge-wiki'
  - 'regex:(?i)giữ|keep'
rubric: "ĐẠT nếu nêu được lệnh gỡ, chỉ ra con dấu .harness-stamp là công tắc của hook global, và nói rõ wiki được giữ trừ khi --purge-wiki. KHÔNG đạt nếu bảo xoá thư mục .llmwiki để gỡ, hoặc bảo sửa tay ~/.claude/settings.json."
---

# Golden: uninstall-turns-off-harness

Bài học của PR #199: gỡ harness là gỡ con dấu, không phải xoá wiki hay sửa settings global.

## Origin
- Phiên 2601b4e7, 02/10/2026 — user yêu cầu thêm lệnh gỡ. Đo được `uninstall.sh` cũ không gỡ con dấu (hook global vẫn chặn sau khi "gỡ"), chỉ biết layout `harness/`, và không có rào repo framework. Test `harness/tests/uninstall-roundtrip-test.sh`: bản cũ đỏ 11/17, bản mới 17/17.
