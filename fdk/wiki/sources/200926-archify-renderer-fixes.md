---
type: source
title: "archify (fork của ta) — vá renderer 20/09/2026: nhãn node hết chui dưới icon, chữ đạt 4,5:1 ở cả hai chế độ, khối nav hết dính"
status: recorded
tags: [archify, diagram, a11y, contrast, html-visual-gate, fork, slop]
timestamp: 2026-09-20
id: 200926-archify-renderer-fixes
---

# archify — vá renderer ở fork, không vá bản cài tại chỗ

Task 9 của `200926-self-slop-gate`. Ba lỗi user nhìn thấy trên ảnh `arch-dark.png` đều nằm trong renderer của archify chứ không nằm ở trang đích: icon vai trò đè lên tiêu đề node, nhãn vùng (`01 / PLAN.md · Ledger`) mờ tới mức không đọc được, và thanh công cụ mỗi chỗ một kiểu viết hoa. Theo `diagram-route-and-own-fork`, lỗi renderer phải sửa ở fork `Rheinmir/archify` rồi cài lại skill, tuyệt đối không sửa thẳng bản đã cài trong `~/.agents/skills/archify` — bản cài là sản phẩm của fork, sửa ở đó là mất ngay lần cài kế tiếp.

## Fork và commit

Repo: `git@github.com:Rheinmir/archify.git` (upstream `tt-a1i/archify`). Bản skill: `2.17.0-dev.1`.

| Commit | Nội dung |
|---|---|
| `f528f9d` | nhãn node hết chui dưới icon · màu chữ đạt 4,5:1 · khối nav hết dính |
| `0aecf24` | workflow `readable-v2` hạ nhãn khỏi sigil · bảng delta có màu nhấn cho nền sáng |

Cả hai commit còn nằm ở nhánh local của fork. Việc đẩy lên remote thuộc Task 13 (`review độc lập + ship ba repo`), chưa làm ở đây.

## Lỗi và cách sửa

**1. Icon đè chữ.** Nhãn node căn giữa, sigil vai trò nằm góc trên trái (11px, thụt 6px). Node hẹp thì nhãn chạy thẳng dưới sigil — đo được `"Task PLAN.md"` còn 11×9px bị đè. Thêm `sigilSafeLabelFitWidth()` trong `renderers/shared/brand-marks.mjs`: chỉ co nhãn NÀO rộng hơn khoảng trống giữa sigil và ảnh gương của nó, nên nhãn ngắn không reflow. Bốn renderer (architecture, dataflow, lifecycle, sequence) đổi sang dùng hàm này.

Riêng workflow phải xử lý hai lần. Lần đầu bỏ qua vì compiler khai `fixed-v1` là hợp đồng byte-for-byte; đọc kỹ thì `fixed-v1` chỉ áp cho `schema_version: 1`, còn `schema_version: 2` là `readable-v2` và được phép đổi. Sau khi bật cho `readable-v2` vẫn còn một node (`"Claim+Dispatch"`, đè 5×4px) vì co chữ đã chạm sàn cỡ chữ tối thiểu — không thể hẹp thêm. Chốt bằng cách hạ chân chữ xuống dưới đáy sigil, và chỉ hạ với node THẬT SỰ chạm nên node rộng giữ nguyên vị trí cũ.

**2. Chữ mờ.** Ba nhóm, đều đo bằng nền phủ THẬT chứ không phải nền trang:

- `--text-muted` / `--text-dim` ở mọi preset (mặc định, `signal-flow`, `blueprint`, `editorial`, `macos`) và màu chữ theo loại node ở chế độ sáng — nâng tới ≥ 4,6:1. Hai trang đỏ cuối cùng (`01 / Sources` 4,48:1 và `request accepted` 4,19:1) là preset `macos` ở chế độ tối, không phải preset mặc định — tìm ra bằng cách suy ngược luminance của chữ từ tỉ số cổng báo rồi dò trong bảng token.
- Chip nav `PATH` / `MAP` / `LENS` và `%` thu phóng pha `color-mix(… 86%, transparent)` nên còn 4,42:1. Bỏ pha, dùng thẳng `--toolbar-text`.
- `Guided views` / `Play story` lấy nguyên `--frontend-stroke` nên chìm; trộn 50% với `--text`.

**3. Khối dính.** `.guided-views` cách `.diagram-container` 6px ở chế độ màn thấp (`@media (max-height: 920px)`, `margin-bottom: 0.375rem`) — dưới ngưỡng 8px của cổng. Nâng lên `0.5rem`. Chỗ này chỉ lộ ra ở một media query, bản `margin` chính đã là `1rem` từ trước.

**4. Bảng delta (`delta/architecture-delta.mjs`).** `:root` khai `--d-add` / `--d-remove` / `--d-change` / `--d-move` cho nền tối, nhánh `[data-theme="light"]` chỉ ghi đè `--d-ink` / `--d-muted` / `--d-line` nên chữ nhấn còn 1,5:1 trên nền sáng; `.eyebrow` thì ghi cứng `#7dd3fc`. Thêm `--d-accent`, thay màu cứng bằng token, khai đủ bộ màu nhấn cho nhánh sáng.

## Sửa luôn cổng: nút đang tắt không phải lỗi

Trong lúc soi trang delta, cổng báo đỏ nút `Overview` ở `1,54:1`. Nút này `disabled`, bị làm mờ `opacity: .45` đúng như quy ước "bấm không được". WCAG 1.4.3 miễn trừ điều khiển đang tắt, nên đây là đỏ GIẢ của cổng chứ không phải lỗi sản phẩm. `fdk/tools/html-visual-gate.mjs` nay bỏ qua `:disabled` / `[aria-disabled="true"]` / `fieldset[disabled]`. Bộ test của cổng vẫn `12 PASS · 0 FAIL`.

## Nghiệm thu

| Việc | Lệnh | Kết quả |
|---|---|---|
| Test của fork | `npm test` trong `archify/archify` | `1029 pass · 0 fail` |
| Trang sơ đồ trong repo | `html-visual-gate.mjs` trên 11 trang `llmwiki/html` do archify sinh | `11/11 đạt` (trước: 0/11) |
| Trang ví dụ của fork | `html-visual-gate.mjs` trên 10 trang `examples/` | `10/10 đạt` |
| Trang đích của PLAN | `170926-orca-graph-gates-architecture.html` | đạt |

Sinh lại toàn bộ: `render:examples` (cả hai thư mục `examples/`), `build-gallery`, `build-readme-showcase`, `build-zip`, và 11 trang cục bộ trong `llmwiki/html` từ JSON nguồn của chúng. Skill cài lại bằng cách đồng bộ `archify/archify/` sang `~/.agents/skills/archify/` (trừ `node_modules`, `.git`).

## Nợ còn mở

- **`examples/checkout-platform-delta.html` chưa qua cổng.** Còn 15 chữ ở chế độ sáng và 6 ở chế độ tối dưới 4,5:1, tất cả nằm trong node `data-delta-state="moved-from"` — bóng mờ (`opacity: .42`) đánh dấu vị trí CŨ của node đã dời. Nhãn thật của cùng node vẫn hiện đủ tương phản ở vị trí mới. Muốn qua cổng thì bóng phải lên `opacity ≥ 0,85`, tức mất hẳn ngôn ngữ thị giác của bảng so sánh. Đây là quyết định thiết kế cần user chốt, không phải lỗi để tự sửa. Cổng chưa biết khái niệm "bóng mờ có bản gốc rõ ở chỗ khác".
- **`docs/gallery.html` của fork** (trang giới thiệu, không phải trang sơ đồ): `toggle: NO-EFFECT`, `/ proof lab` ở `2,6:1`, ba chỗ khối dính 1px. Đây là template site của upstream, ngoài phạm vi Task 9.

## Origin

- Ảnh `scratchpad/slop/arch-dark.png` user gửi ngày 20/09/2026 kèm nhận xét: icon đè tiêu đề node, nhãn vùng mờ, thanh công cụ mỗi chỗ một kiểu viết hoa.
- Task 9 của `llmwiki/wiki/sources/draft/200926-self-slop-gate-PLAN.md` (user duyệt cùng ngày: "dựng qua graph và xử lý hết đi").
- Memory `diagram-route-and-own-fork`: archify là fork ta sở hữu → lỗi renderer sửa ở fork `Rheinmir/archify`, không vá bản cài tại chỗ.
- Commit của fork: `f528f9d`, `0aecf24`.
