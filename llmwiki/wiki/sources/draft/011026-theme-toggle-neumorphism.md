---
type: draft
title: "PROPOSE — đổi nút sáng/tối mặc định của toàn framework sang nút tròn neumorphism (Uiverse · Creatlydev)"
status: proposed
tags: [propose, theme-toggle, html_base, dark-mode-maker, docs-site-macos, design-showcase]
timestamp: 2026-10-01
---

# PROPOSE 011026 — nút sáng/tối chuẩn = nút tròn neumorphism

## Origin
User gọi `/fdk` ngày 01/10/2026 và dán khối HTML/CSS lấy từ Uiverse.io (tác giả Creatlydev, giấy phép MIT): một nút tròn 56px nền trắng, bóng mờ rộng (neumorphism, tức kiểu nổi khối mềm), bên trong là icon mặt trăng/mặt trời. Hai icon đổi chỗ cho nhau bằng hiệu ứng xoay 360° và co giãn (500ms, trễ 200ms). Lệnh của user là đặt nút này làm **chuẩn mặc định cho nút chuyển sáng tối của toàn app**.

Hai điểm user đã chốt khi trả lời câu hỏi:
1. **Vị trí: giữ chỗ cũ, chỉ thay hình.** Trang sinh bằng `html_base` vẫn để nút nổi ở góc phải dưới. Trang có sidebar (`dark-mode-maker`, `docs-site-macos`) vẫn để nút ở hàng đáy nav.
2. **Code gốc: chép nguyên văn và thêm một lớp vá riêng.** Lý do cần vá: bản gốc ẩn checkbox bằng `display:none` nên không dùng được bằng bàn phím, và chỉ có nền trắng nên lạc tông ở chế độ tối.

## Hiện trạng: nút sáng/tối đang được định nghĩa ở đâu
| Bề mặt | File | Dạng hiện tại |
|---|---|---|
| Mọi trang sinh qua lớp nền | `fdk/tools/html_base.py` (`TOGGLE_HTML`, CSS `.ovs-theme`, `TOGGLE_JS`) | viên thuốc có chữ "Sáng/Tối", cố định ở góc phải dưới |
| Module dùng cho mọi trang có nav | `skills/dark-mode-maker/SKILL.md` + JS chèn `.theme-row > .theme-switch` | nút gạt (switch) 50×26 có nhãn, kèm hiệu ứng tỏa tròn (circle-reveal) |
| Trang tài liệu macOS | `skills/docs-site-macos/SKILL.md` § Theme Toggle | nút gạt có nhãn ở đáy nav |
| Vỏ trang tài liệu | `fdk/tools/html_shell.py` (`.theme-row`, `.theme-switch`) | ẩn nhãn, giữ nút gạt |
| Luật bằng chữ | `skills/fdk/SKILL.md` RULE-07, `llmwiki/CLAUDE.md`/`AGENT.md` RULE-05 | "NÚT GẠT (switch) có nhãn … KHÔNG chip icon" → **mâu thuẫn trực tiếp với yêu cầu mới** |
| Trang mẫu chuẩn | `skills/hallmark/references/design-showcase.html` (sinh bởi `build-design-showcase.py`) | chưa có khối nút sáng/tối kiểu mới |
| Cổng kiểm | `fdk/tools/html-visual-gate.mjs` (`TOGGLE_SEL`, kiểm nút có nhảy chỗ khi bấm), `fdk/tools/frontend-antipattern.py` (`no-theme-toggle`), `skills/dark-mode-maker/scripts/verify-theme-motion.mjs` | bám theo `aria-label` có chữ "giao diện" và theo class `.theme-switch` |

## Thiết kế

### 1. Một khối code dùng chung: chép nguyên văn + lớp vá
- **Phần chép nguyên văn:** giữ đủ các khai báo CSS và markup SVG của Creatlydev, ghi credit `/* From Uiverse.io by Creatlydev — MIT */`. Chỉ đổi một điều bắt buộc: **thêm tiền tố vào selector**. `.toggle`, `.input`, `.icon` là tên quá chung nên sẽ đụng CSS của trang chủ. Đổi thành `.ovs-theme.toggle`, `.ovs-theme .input`, … và đổi `#switch` thành `#ovs-theme-switch`. Không đổi giá trị nào.
- **Lớp vá** (khối CSS riêng, đặt ngay sau phần chép nguyên văn):
  - Input bị ẩn bằng kiểu vẫn focus được (clip 1px) thay cho `display:none`. Khi input được focus thì `label` có vòng focus: `.ovs-theme:has(.input:focus-visible){outline:2px solid var(--accent)}`.
  - Khi `html[data-theme=dark]`: nền nút dùng màu bề mặt tối, bóng `rgba(0,0,0,.45)` thay cho `.1`, icon đổi màu theo `currentColor`.
  - `prefers-reduced-motion`: lớp nền đã tắt transition sẵn, không cần thêm.
- **Ánh xạ trạng thái:** checkbox được tích nghĩa là đang ở chế độ tối. Đang sáng thì nút hiện mặt trăng (bấm để sang tối), đang tối thì hiện mặt trời. Khớp đúng hướng animation của bản gốc.
- `aria-label="Đổi giao diện sáng / tối"` đặt trên input, `title` đặt trên label. Nhờ vậy `TOGGLE_SEL` của cổng và regex `has_toggle` vẫn khớp mà không phải sửa cổng.

### 2. Áp vào từng bề mặt (giữ vị trí cũ)
1. **`html_base.py`:** thay `TOGGLE_HTML` + CSS `.ovs-theme` bằng khối trên. Vẫn `position:fixed; right:16px; bottom:16px`. `TOGGLE_JS` nghe sự kiện `change` của checkbox thay cho `click` của nút, phần còn lại giữ nguyên (localStorage, postMessage cho iframe con, chống nháy).
2. **`dark-mode-maker`:** `.theme-switch` thành nút tròn này. Giữ tên class `.theme-row`, `.theme-switch`, `.theme-reveal` để `verify-theme-motion.mjs` vẫn bám được. Circle-reveal tỏa từ tâm nút (RULE-03 kẹp trong biên nút vẫn đúng). Nhãn chữ của hàng được giữ lại cho trang có sidebar.
3. **`docs-site-macos`:** cập nhật snippet § Theme Toggle cho khớp `dark-mode-maker`.
4. **`html_shell.py`:** soát lại các rule `.theme-row`, `.theme-switch` (kích thước 56px trong hàng đáy nav: giảm còn 40px bằng `zoom`/`transform` nếu chật, và ghi rõ là bản thu nhỏ).
5. **Luật bằng chữ:** sửa `skills/fdk/SKILL.md` RULE-07 và RULE-05 trong `llmwiki/CLAUDE.md`/`AGENT.md`, từ "NÚT GẠT có nhãn, không chip icon" thành "nút tròn neumorphism mặt trăng/mặt trời (khối chuẩn trong design-showcase), vị trí theo bề mặt". Sau đó chạy `bash fdk/tools/sync-skill.sh fdk dark-mode-maker docs-site-macos`.
6. **design-showcase:** thêm khối `theme-toggle` vào `build-design-showcase.py`, lấy được bằng `--get theme-toggle`. Theo luật repo: thêm luật thì phải thêm khối mẫu.

### 3. Trang HTML đã sinh từ trước
Không dựng lại hàng loạt. Trang mới tự có nút mới. Trang cũ có nút mới khi được dựng lại lần sau. Chỉ dựng lại `overstack.html` và `design-showcase.html` để kiểm bằng mắt.

## Kiểm chứng (vòng phản hồi)
- Test tất định mới `harness/tests/theme-toggle-neumorphism-test.sh`: dựng 1 trang qua `html_base.apply`, rồi chạy Playwright để kiểm các điểm sau. Bấm nút thì `data-theme` đổi. Tải lại trang thì lựa chọn vẫn giữ. Tab bằng bàn phím tới được nút và Space đổi được giao diện. Hộp bao của nút không nhảy chỗ khi bấm (±1px). Icon đúng chiều (sáng → mặt trăng hiện).
- Chạy lại `html-visual-gate-test.sh`, `node skills/dark-mode-maker/scripts/verify-theme-motion.mjs` trên 1 trang mẫu, và `frontend-antipattern.py` trên `overstack.html`.
- Trước khi push: `python3 fdk/tools/ci-local.py` rồi `/fdk-uat` (RULE-01).

## Rủi ro
- Nhánh local đang **chậm 26 commit** so với `origin/orca` và có ~256 file đang sửa dở. Phải pull hoặc rebase trước khi sửa. Nếu các file trên đã đổi ở upstream thì gộp vào, không ghi đè (theo memory `framework-multi-session-dev` (ghi nhớ của agent, không phải trang wiki)).
- Nút 56px có bóng mờ rộng `50px 20px`, có thể đè lên nội dung ở góc phải dưới trên màn hẹp. Cổng overlap của `html-visual-gate` sẽ bắt. Nếu bị bắt thì vá bằng cách giảm bóng ở viewport < 600px.

## Ngoài phạm vi
- Không đổi vị trí nút (user đã chọn giữ chỗ cũ).
- Không đổi palette tối, không đổi cơ chế chống nháy.
