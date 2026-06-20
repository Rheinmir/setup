---
name: health-check
description: Kiểm tra sức khỏe "pattern chuẩn" của template — pattern đã đủ chưa, có drift local không, và có cần /sync-template từ remote không. So version.json local ↔ remote ↔ disk (0 token, fail-open). Trigger: "health check", "check pattern", "cần sync chưa", "/health-check".
---

# Skill: health-check

## Purpose
Trả lời nhanh 3 câu hỏi về bộ "pattern chuẩn" (tập file khai trong `.template-manifest.json`) mà không cần diff tay từng file như `sync-template`:
1. **Đủ chưa?** — mọi pattern khai báo có mặt trên disk không (MISSING).
2. **Có lệch local?** — pattern nào đã bị sửa kể từ lần sync gần nhất (DRIFT).
3. **Cần sync remote?** — remote có bản pattern mới hơn không (BEHIND / version cũ).

Cơ chế: 1 file cấu hình duy nhất `harness/version.json` lưu `template_version` + **hash từng pattern**. So 3 mốc: disk ↔ version.json (drift), local ↔ remote version.json (behind), manifest ↔ disk (missing).

## When to use
- Đầu phiên harness tự chạy (SessionStart hook) — nếu lệch sẽ tự nhắc.
- Người dùng gọi `/health-check` để kiểm thủ công bất cứ lúc nào.
- Trước khi quyết định có chạy `/sync-template` hay không.

## Steps

### 1. Chạy báo cáo (đối chiếu cả remote)
```bash
python3 harness/scripts/health-check.py --root . --branch orca
```
- `--offline` : chỉ kiểm local (bỏ fetch remote) khi không có mạng.
- `--json`    : output máy đọc (dùng cho hook / CI).
- `--fail-on behind,drift,missing` : exit 2 nếu nhóm chỉ định vi phạm (dùng cho gate CI).

### 2. Đọc kết quả
| status | nghĩa | hành động |
|--------|-------|-----------|
| `OK` | pattern đủ + khớp remote | không cần làm gì |
| `DRIFT` | pattern bị sửa local | cân nhắc **upstream** (`/sync-template` push) hoặc revert |
| `NEEDS-SYNC` | thiếu file hoặc remote mới hơn | chạy **downstream** `/sync-template` |

Báo cáo còn kèm 1 dòng **OKF v0.1**: `✓ OKF v0.1: N/N concept đạt chuẩn` (mọi concept có YAML frontmatter + `type`) hoặc `⟳ OKF v0.1: x/N … cần migrate`. Đây là câu trả lời nhanh "project đã đạt chuẩn OKF chưa?". Chưa đạt → `python3 harness/scripts/okf-check.py --migrate`.

### 3. Hành động theo khuyến nghị
- **BEHIND / MISSING** → gọi `/sync-template` (downstream): kéo pattern mới/thiếu về.
- **DRIFT** → nếu cải tiến muốn giữ: `/sync-template` upstream; nếu lỡ sửa: `git checkout -- <file>`.

### 4. Sau khi sync xong — refresh version.json
Mỗi lần downstream sync đổi nội dung pattern, cập nhật lại fingerprint:
```bash
python3 harness/scripts/health-check.py --update            # giữ nguyên version
python3 harness/scripts/health-check.py --update --bump patch   # khi PHÁT HÀNH bản mới (chỉ làm ở repo template)
```
> `--bump` (major/minor/patch) CHỈ chạy ở repo template `Rheinmir/setup` khi muốn công bố version pattern mới cho mọi project. Project con chỉ `--update` (không bump) để đồng bộ hash sau khi pull.

## Quan hệ với skill khác
- [[sync-template]] — health-check **chẩn đoán** (có cần sync không); sync-template **thực thi** (kéo/đẩy file). Luôn chạy health-check trước, sync-template sau.
- `harness/scripts/wiki-health.py` — anh em cùng tầng L4 nhưng soi **nội dung wiki** (broken link, orphan, stale), không soi version pattern.

## Rules
- Fail-open tuyệt đối: lỗi mạng / thiếu version.json → báo cáo phần local, KHÔNG chặn phiên.
- `harness/version.json` là nguồn sự thật duy nhất cho version — không hardcode version ở chỗ khác.
- Pattern set = `includes` trong `.template-manifest.json`, TRỪ `harness/version.json` và các file "sống" theo project (`index.md`, `log.md`, `active-context.md`, `decisions.md`) — chúng được seed nhưng không tính drift.
- `--bump` chỉ ở repo template; project con chỉ `--update`.
- Thêm pattern mới: add vào `.template-manifest.json` `includes` TRƯỚC, rồi `--update`.

## Origin
- Draft: `llmwiki/wiki/sources/draft/150626-health-check-pattern-sync.md`
