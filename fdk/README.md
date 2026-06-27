# FDK — Framework Development Kit (folder)

Đây là folder vật lý gom mọi thứ phục vụ việc phát triển **chính** framework này, để chúng travel cùng repo và được quản lý ở một nơi thay vì rải rác. Nó dành cho người (hoặc agent) đang sửa skill, rule, validator, hook, hay tài liệu của framework — KHÔNG dùng khi chỉ dùng framework để phát triển dự án khác.

> **Đọc trước:** front-door *khái niệm* — pre-flight gate, "không miss rule", "không dẫm module" — nằm ở wiki concept `llmwiki/wiki/concepts/fdk.md` (gọi nhanh bằng skill `/fdk`). Folder này là phần *vật lý* (tool + tài liệu di động) đi kèm concept đó.

## Cấu trúc

- **`tools/`** — script phục vụ dev framework.
  - `build-cheatsheet.py` — nhồi toàn bộ `skills/*/SKILL.md` vào trang skills-cheatsheet để nó self-contained (mở `file://` vẫn xem được full nội dung, không cần server). Chạy: `python3 fdk/tools/build-cheatsheet.py`.
- **`docs/`** — tài liệu dev framework di động được (không bị coupled với engine).
  - `CONTRIBUTING.md` — runbook thêm/sửa một rule của harness (cổng quyết định ADR, phân loại content-check / hook-event / process-gate).

## Bản đồ tài liệu dev framework

Không phải tài liệu nào cũng dời được vào đây. Tài liệu nằm trong wiki cần ở lại knowledge-graph để được cross-link và validate; tài liệu coupled với engine cần ở lại cạnh engine. Bảng dưới là bản đồ đầy đủ:

| Tài liệu | Vị trí | Vì sao ở đó |
|----------|--------|------------|
| Front-door concept (pre-flight, rule, module map) | `llmwiki/wiki/concepts/fdk.md` | wiki knowledge-graph — cross-link + validate |
| Rule registry R1..Rn | `llmwiki/wiki/concepts/rule-registry.md` | wiki concept |
| Architecture Decision Records | `llmwiki/wiki/sources/adr/ADR-*.md` | wiki decision |
| Runbook thêm/sửa rule | `fdk/docs/CONTRIBUTING.md` | thuần dev-framework → đã dời vào đây |
| Recipe harness (kiến trúc 5 lớp) | `harness/recipe.md` | **giữ tại chỗ** — coupled |
| Kiến trúc harness | `harness/harness.md` | **giữ tại chỗ** — coupled |
| Vendor-neutral chi tiết | `harness/poc-vendor-neutral/DOCS.md` | **giữ tại chỗ** — coupled |

Ba tài liệu cuối **cố ý không dời** vào `fdk/`: impact-check cho thấy `.pre-commit-config.yaml`, `harness/scripts/install-harness.sh`, `harness/evals/` và một số validator đang trỏ trực tiếp tới chúng — dời đi sẽ làm vỡ máy harness. Đây chính là nguyên tắc "không dẫm/đá module cũ" mà FDK gác (xem `fdk.md` Phần 3). Khi cần, đọc chúng ngay tại `harness/`.

## Quy ước khi thêm vào folder này

- Thêm **tool** dev-framework mới → đặt ở `tools/`, đặt tên rõ nghĩa, có docstring + usage.
- Thêm **tài liệu** dev-framework mới mà *không* coupled với engine và *không* cần nằm trong wiki-graph → đặt ở `docs/`.
- Tài liệu thuộc về knowledge-graph (concept/decision) vẫn vào `llmwiki/wiki/` như cũ; chỉ cần thêm một dòng vào bảng bản đồ trên.
