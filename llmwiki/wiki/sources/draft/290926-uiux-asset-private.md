---
type: issue
kind: architecture
title: "Chuyển nơi lưu ui-kit sang private: uiux-asset đang PUBLIC nên chưa thể sync kit của repo riêng tư và kit rút từ site bên thứ ba"
status: done
assignee: "@Rheinmir"
dispatch: human
entry: /fdk
priority: P2
labels: done
tags: [issue, uiux-asset, privacy, ui-kit, visibility]
timestamp: 2026-09-29
id: 290926-uiux-asset-private
source_session: "m3e-canvas — sau khi raise GH#186, user yêu cầu private kho luôn để mọi kit đều sync được"
---

# Issue: Chuyển nơi lưu ui-kit sang private

## Vấn đề (một câu)
User muốn MỌI kit sinh từ `/ui-kit-from-code` đều tự sync (issue `[[290926-ui-kit-sync-uiux-asset]]`, GH#186), nhưng `Rheinmir/uiux-asset` đang PUBLIC. Vì vậy GH#186 phải chặn kit của repo riêng tư và kit rút từ site bên thứ ba. User yêu cầu private luôn để bỏ chặn đó.

## Bối cảnh & bằng chứng
- Yêu cầu nguyên văn của user (2026-09-29), trả lời cho phần chính sách quyền riêng tư của GH#186: *"raise issue yêu cầu private nó luôn"*.
- Trạng thái đo được ngày 2026-09-29:
  - `gh repo view Rheinmir/uiux-asset`: PUBLIC, nhánh `main`, 0 fork, 0 star.
  - `gh api repos/Rheinmir/uiux-asset/pages`: GitHub Pages bật tại `https://rheinmir.github.io/uiux-asset/` (build `legacy` từ `main`).
  - Còn một bản deploy Vercel `uiux-asset.vercel.app` (trang tổng hợp, `/stats.html`, API tìm kiếm Upstash).
  - `gh api user`: `plan = null`, tức gói Free. Ở gói Free, GitHub Pages KHÔNG chạy được từ repo private.
- Framework đang dựa vào việc repo công khai: 8 skill trên `origin/orca` nhắc `uiux-asset` (`scroll-effects`, `lenis-smooth-scroll`, `gsap-scrolltrigger-pin`, `infinite-webgl-grid`, `mask-reveal-transition`, `svg-stroke-reveal`, `threejs-particle-morph`, `ship`). Chúng dùng link `rheinmir.github.io/uiux-asset/...` ("chạy") cùng `github.com/Rheinmir/uiux-asset/blob/...` ("code"), và bảo agent `git clone --depth 1 https://github.com/Rheinmir/uiux-asset` khi cần bản gốc. Người dùng downstream không có quyền vào repo private thì mọi link và lệnh clone này hỏng, skill rơi về `assets/` rút gọn (partial).
- Nội dung đang có trong repo (`scroll-effects/`, `components/`) là mã CodePen công khai, giấy phép MIT. Đây là loại nội dung được phép và nên để công khai.

## Phạm vi
Quyết định nơi lưu ui-kit và mức hiển thị, sau đó cập nhật đích sync của GH#186 cho khớp. Có hai hướng:

| | A. Tách repo private riêng cho kit (khuyến nghị) | B. Chuyển cả uiux-asset sang private |
|---|---|---|
| Làm gì | Tạo `Rheinmir/ui-kits` (private); GH#186 sync vào đó. `uiux-asset` giữ public cho asset MIT | Đổi visibility `uiux-asset` → private |
| GitHub Pages | Không đụng | Tắt, vì gói Free không có Pages private. Phải chuyển gallery sang Vercel và bật Deployment Protection, hoặc nâng gói |
| 8 skill framework | Không đụng | Phải sửa link và fallback; người dùng downstream không có quyền thì luôn rơi về `assets/` partial |
| Vercel, stats, search | Không đụng | Deploy vẫn chạy (Vercel đọc được repo private), nhưng trang public vẫn lộ nội dung trừ khi bật protection |
| Xem kit | Chỉ người có quyền repo (clone hoặc GitHub UI); muốn xem như web thì thêm một Vercel project riêng có protection | Như cột A nếu có bật protection |

## Không thuộc phạm vi
- Viết code sync (đó là GH#186).
- Xoá hay di chuyển asset MIT hiện có.
- Nâng gói GitHub.

## Hướng gợi ý (không bắt buộc)
Hướng A: rủi ro thấp nhất, không phá gì đang chạy, và đúng mục tiêu "mọi kit đều sync". Khi chọn A, GH#186 đổi đích sync thành `Rheinmir/ui-kits` (cấu hình bằng biến môi trường, ví dụ `UI_KIT_SYNC_REPO`) và bỏ ba nhánh chặn quyền riêng tư: kit của repo private, kit rút từ site bên thứ ba, và bước hỏi một lần cho mỗi id. Id, hash và phiên bản giữ nguyên thiết kế.

## Tiêu chí HOÀN THÀNH
- Có quyết định A hoặc B, ghi vào file này (mục Quyết định) và comment lên GH#186.
- Nơi lưu kit là private: `gh repo view <repo> --json visibility` ra `PRIVATE`.
- Nếu chọn B: 8 skill framework đã sửa link và fallback, GitHub Pages đã được thay bằng một đường xem có bảo vệ, `medic --ci` của setup xanh.
- GH#186 được cập nhật đích sync và chính sách quyền riêng tư theo quyết định.

## Quyết định (2026-09-29)
**Hướng A.** Tạo repo PRIVATE riêng `Rheinmir/ui-kits`. `Rheinmir/uiux-asset` giữ nguyên PUBLIC cho asset MIT, nên GitHub Pages, bản deploy Vercel và 8 skill framework đều không bị đụng tới.
- Kiểm chứng: `gh repo view Rheinmir/ui-kits --json visibility` → `PRIVATE`.
- Lý do: hướng này không phá thứ gì đang chạy, đảo ngược được, và không cần nâng gói GitHub. Hướng B sẽ tắt Pages, làm hỏng link của 8 skill cho người dùng downstream, và vẫn để lộ trang Vercel nếu chưa bật protection.
- Người chọn: agent, theo chỉ thị của user "tự hành giải quyết hết các vấn đề" và khuyến nghị sẵn có trong issue. Agent không đổi visibility của repo nào đang có.
- GH#186 đổi đích sync thành `Rheinmir/ui-kits` (biến `UI_KIT_SYNC_REPO`) và bỏ ba nhánh chặn quyền riêng tư. Script tự kiểm `visibility` và từ chối đẩy lên kho PUBLIC.

## Assign & lý do
@Rheinmir, dispatch **human**, nhãn `ready-for-human`. Đổi visibility repo và tạo repo mới cần quyền chủ sở hữu, và việc chọn A hay B là đánh đổi mà chỉ chủ repo quyết được (Pages, link công khai, gói GitHub). Agent headless không được tự đổi visibility.

## Origin
Raise bằng `/raise-issue` từ phiên Claude Code ở `~/orca/m3e-canvas` ngày 2026-09-29, ngay sau GH#186, theo yêu cầu trực tiếp của user. Bằng chứng: các lệnh `gh repo view`, `gh api .../pages`, `gh api user` và `git grep uiux-asset origin/orca` đã liệt kê ở trên.
