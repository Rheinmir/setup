---
type: issue
kind: feature-gap
title: "ui-kit-from-code chưa tự đẩy kit lên Rheinmir/uiux-asset — không có id chống trùng, không có phiên bản v1, v2, v3 cho cùng một dự án"
status: done
assignee: "@Rheinmir"
dispatch: Claude
entry: /fdk
priority: P2
labels: done
tags: [issue, skill, ui-kit, uiux-asset, sync, versioning]
timestamp: 2026-09-29
id: 290926-ui-kit-sync-uiux-asset
source_session: "m3e-canvas — user yêu cầu mọi ui-kit sinh từ /ui-kit-from-code từ nay tự sync ngược lên uiux-asset"
---

# Issue: ui-kit-from-code chưa tự đẩy kit lên uiux-asset, chưa có id và phiên bản

## Vấn đề (một câu)
Mỗi lần chạy `/ui-kit-from-code`, kit chỉ nằm ở máy người chạy (`docs/ui-kit.html` hoặc đường tự chọn). Chưa có bước tự đẩy kit lên kho chung `Rheinmir/uiux-asset` vào đúng thư mục của dự án, chưa có id để biết kit đã có hay chưa, và chạy lại trên cùng dự án thì không sinh được v2, v3 mà ghi đè hoặc để rải rác.

## Bối cảnh & bằng chứng
- Skill `[[ui-kit-from-code]]` được thêm qua issue `[[280926-ui-kit-from-code]]` (GH#181, PR #182 đã merge vào `orca` ngày 2026-09-28). Output contract hiện tại chỉ có `docs/ui-kit.html` + báo cáo nguồn gốc + bằng chứng Playwright; phần "Không thuộc phạm vi" của issue đó ghi "Đồng bộ ngược kit → code", tức là đồng bộ về code, không phải lên kho asset. Issue này không trùng.
- Kit đã sinh thật đang nằm rải rác, không ai thấy ngoài máy này:
  - `~/orca/m3e-canvas/docs/ui-kit.html`: kit của `lnkiai/m3e-canvas` (repo PUBLIC), file untracked.
  - `~/orca/ui-kits/drafted-ai.html`, `~/orca/ui-kits/facebook.html`: kit rút từ site của bên thứ ba (nhánh URL của skill).
- `Rheinmir/uiux-asset` là kho PUBLIC (nhánh `main`, GitHub Pages `rheinmir.github.io/uiux-asset` + Vercel `uiux-asset.vercel.app`). Cấu trúc hiện có: mỗi loại asset là một thư mục cấp một (`scroll-effects/`, `components/`) kèm `manifest.json`, gallery sinh bằng `tools/build-index.py`, và tìm theo nghĩa qua `tools/build-search-index.py` + `tools/upload-search.mjs` (Upstash). Chưa có thư mục cho ui-kit.
- Yêu cầu nguyên văn của user (2026-09-29): *"tất cả những ui-kit được tạo ra từ skill ui-kit-from-code từ giờ tự sync ngược lên https://github.com/Rheinmir/uiux-asset vào folder tương ứng, đánh id của chúng để lọc trùng và tạo ra v1,2,3... mới khi đã có ui-kit cũ cho project này"*.

## Phạm vi
- `skills/ui-kit-from-code/SKILL.md`: thêm một bước cuối sau cổng Playwright (sau khi kit đã PASS, không bao giờ đẩy kit đỏ), cập nhật bảng Input/Output và Failure boundaries, và mirror sang llmwiki + các bề mặt curated như mọi skill.
- Script mới trong `skills/ui-kit-from-code/references/` (ví dụ `sync-uiux-asset.mjs` hoặc `.py`) làm phần tất định: tính id, tính hash, chọn số phiên bản, ghi file, commit, push.
- Phía `Rheinmir/uiux-asset`: thư mục mới `ui-kits/` + gallery. Đụng repo này là cố ý và nằm trong phạm vi.
- Universal: áp cho mọi dự án chạy skill, không riêng m3e-canvas.

## Không thuộc phạm vi
- Đồng bộ ngược kit → code (vẫn ngoài phạm vi như issue gốc).
- Sửa nội dung kit hay cách skill rút kit.
- Xoá hoặc gộp phiên bản cũ. Phiên bản chỉ tăng, không bao giờ ghi đè.
- Đẩy lên kho nào khác ngoài `Rheinmir/uiux-asset`.

## Hướng gợi ý (không bắt buộc)
**Id dự án (lọc trùng theo dự án):**
- Nguồn là code: chuẩn hoá `git remote get-url origin` thành `<owner>-<repo>` viết thường (vd `lnkiai-m3e-canvas`). Không có remote thì dùng tên thư mục gốc kèm hậu tố `-local`.
- Nguồn là URL: host bỏ `www.`, dấu chấm đổi thành gạch (vd `drafted-ai`).
- Id ghi vào `<meta name="ui-kit-id">` trong chính kit, để kit tải về lại vẫn nhận ra mình.

**Hash nội dung (lọc trùng theo phiên bản):** sha256 của kit sau khi bỏ phần hay đổi mà không mang nghĩa (dấu thời gian sinh, id ngẫu nhiên). Hash trùng với phiên bản mới nhất thì KHÔNG tạo phiên bản mới; script in "không đổi so với vN" và dừng rc 0.

**Bố cục trong uiux-asset:**
```
ui-kits/
  registry.json                 # { "<id>": { "source": "...", "latest": 3 } }
  index.html                    # gallery, sinh bằng tool
  <id>/
    manifest.json               # versions: [{ v, hash, date, source_commit | source_url, skill_version, file }]
    v1/index.html
    v2/index.html
    latest/index.html           # bản sao của phiên bản mới nhất, link ổn định
```
**Chọn số phiên bản:** `git pull --rebase` repo uiux-asset trước, đọc `manifest.json`, lấy `max(v) + 1`. Push bị từ chối vì máy khác vừa đẩy cùng số thì pull lại, tính lại, thử tối đa 3 lần.

**Quyền riêng tư (uiux-asset là PUBLIC):**
- Kit rút từ site của bên thứ ba: KHÔNG tự đẩy. Đây là hệ quả trực tiếp của RULE-09 và nhánh B03 hiện có trong skill ("kit giữ ở máy user; muốn chia sẻ ra ngoài thì hỏi trước"). Chỉ đẩy khi user cho phép rõ ràng cho đúng lần đó.
- Kit từ codebase mà repo nguồn là PUBLIC: tự đẩy, đúng yêu cầu user.
- Kit từ codebase mà repo nguồn là PRIVATE hoặc không có remote: hỏi một lần cho mỗi id rồi nhớ lựa chọn trong file cấu hình local (vd `~/.config/overstack/ui-kit-sync.json`). Lý do: đẩy tự động token và component của một dự án riêng tư lên kho công khai là rò rỉ không lấy lại được.
- Có cờ tắt: `UI_KIT_SYNC=0` bỏ qua toàn bộ bước sync.

**Lỗi mạng hoặc không có quyền push:** kit local vẫn là kết quả hợp lệ của skill; bước sync báo rõ "chưa sync, lý do …" và không làm fail cả skill.

## Tiêu chí HOÀN THÀNH
- Chạy skill trên m3e-canvas lần đầu → xuất hiện `ui-kits/lnkiai-m3e-canvas/v1/index.html` + `manifest.json` + dòng trong `registry.json` trên `Rheinmir/uiux-asset`, mở được qua GitHub Pages.
- Chạy lại ngay, kit không đổi → không có commit mới; script in "không đổi so với v1".
- Sửa một token rồi chạy lại → có `v2/`, `latest/` trỏ nội dung v2, `v1/` giữ nguyên byte-for-byte.
- Chạy trên một URL bên thứ ba mà không có đồng ý → không có gì bị đẩy, skill báo lý do.
- Test tất định cho phần tính id, hash và số phiên bản (không cần mạng), chạy được trong CI của setup.
- `swh-lint --skills ui-kit-from-code --ci`, `sync-skills.py --check`, `skill-registry.py --check`, `skill-provenance.py check --ci` đều rc 0.
- Backfill: kit m3e-canvas hiện có được đẩy thành v1. Hai kit facebook và drafted-ai KHÔNG được đẩy nếu không có đồng ý.

## Kết quả (2026-09-29)
Đích sync đổi theo quyết định của `[[290926-uiux-asset-private]]`: kho **PRIVATE** `Rheinmir/ui-kits` thay vì `uiux-asset`. Vì kho private nên ba nhánh chặn quyền riêng tư đã bỏ; RULE-09 (không nhúng ảnh hay nội dung có bản quyền) vẫn giữ.
- `skills/ui-kit-from-code/references/sync-kit.py`: gồm id, hash bỏ meta `ui-kit-id`, `vN+1`/`latest`/`manifest`/`registry`/README, push có retry 3 lần, `UI_KIT_SYNC=0`, `UI_KIT_SYNC_REPO`, `--id` và `--dry-run`. Script từ chối kho không PRIVATE. Lỗi mạng hoặc quyền thì in "chưa sync" và trả rc 0.
- SKILL.md: thêm W09, RULE-12 và dòng Out; cập nhật Failure và B03. Mirror llmwiki đã đồng bộ.
- Test tất định `harness/tests/test_ui_kit_sync.py` (id, hash, số phiên bản, v1 giữ nguyên byte-for-byte khi ra v2, quay lại nội dung cũ vẫn thành v3) đã gắn vào CI `harness.yml`.
- Chạy thật: m3e-canvas lên `lnkiai-m3e-canvas/v1`; chạy lại ngay thì báo "không đổi so với v1" và không có commit mới.
- Backfill: 17 kit lên v1, gồm m3e-canvas cùng 16 kit site có trong `~/orca/m3e-canvas/docs`. Không đẩy `bonbon-ui-need-remake-kit.html` vì tên file ghi là chưa xong. Kit bonbon không ghi host nên dùng `--id bonbon`.
- Cổng: `swh-lint --skills ui-kit-from-code --ci`, `sync-skills.py --check`, `skill-registry.py --check` đều rc 0; `skill-provenance check` không còn lệch với ui-kit-from-code.
- Không làm: gallery `index.html` (kho private không có Pages, README bảng kit thay thế). Thêm khi nào có đường xem web được bảo vệ.

## Assign & lý do
@Rheinmir, dispatch Claude qua `/fdk`. Yêu cầu đã rõ và mọi quyết định có default an toàn (chính sách quyền riêng tư ở trên suy trực tiếp từ RULE-09 sẵn có), nên agent làm được: `ready-for-agent`. Nếu người nhận muốn tự đẩy cả kit từ repo private mà không hỏi, đó là đổi chính sách và cần user xác nhận trước khi code.

## Origin
Raise bằng `/raise-issue` từ phiên Claude Code ở `~/orca/m3e-canvas` ngày 2026-09-29, theo yêu cầu trực tiếp của user. Bằng chứng: `gh repo view Rheinmir/uiux-asset` (PUBLIC, `main`), README uiux-asset, `git log` của skill (PR #182), file kit hiện có đã liệt kê ở trên.
