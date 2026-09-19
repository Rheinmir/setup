---
name: health-check
disable-model-invocation: true
description: >-
  Kiểm tra sức khỏe "pattern chuẩn" của template — pattern đã đủ chưa, có drift local không, và
  có cần /sync-template từ remote không. So version.json local ↔ remote ↔ disk (0 token, fail-
  open). Trigger: "health check", "check pattern", "cần sync chưa", "/health-check".
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: health-check

## WHAT

### Purpose và context
- **Purpose:** Trả lời nhanh 3 câu hỏi về bộ "pattern chuẩn" (tập file khai trong `.template-manifest.json`) mà không cần diff tay từng file như `sync-template`:
  1. **Đủ chưa?** — mọi pattern khai báo có mặt trên disk không (MISSING).
  2. **Có lệch local?** — pattern nào đã bị sửa kể từ lần sync gần nhất (DRIFT).
  3. **Cần sync remote?** — remote có bản pattern mới hơn không (BEHIND / version cũ).
- **Trigger (when to use):**
  - Đầu phiên harness tự chạy (SessionStart hook) — nếu lệch sẽ tự nhắc.
  - Người dùng gọi `/health-check` để kiểm thủ công bất cứ lúc nào.
  - Trước khi quyết định có chạy `/sync-template` hay không.
- **Non-goals:** không tự kéo/đẩy file (đó là `/sync-template` — health-check chỉ **chẩn đoán**), không soi nội dung wiki (broken link, orphan, stale — đó là `harness/scripts/wiki-health.py`).

### Mental model
Cơ chế: 1 file cấu hình duy nhất `harness/version.json` lưu `template_version` + **hash từng pattern**. So 3 mốc: disk ↔ version.json (drift), local ↔ remote version.json (behind), manifest ↔ disk (missing). Kết quả mỗi pattern → `OK` · `DRIFT` · `NEEDS-SYNC` → hành động khuyến nghị.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | `.template-manifest.json` + `harness/version.json` | có | tập pattern + fingerprint; thiếu version.json → báo phần local (fail-open) |
| In | `--branch` / `--offline` / `--json` / `--fail-on` | không | nhánh remote; bỏ fetch; output máy đọc; exit 2 cho gate CI |
| Out | báo cáo status từng nhóm + dòng OKF v0.1 | có | `OK` / `DRIFT` / `NEEDS-SYNC` + `✓ OKF v0.1: N/N …` |
| Out | exit code | khi `--fail-on` | 2 nếu nhóm chỉ định vi phạm |
| Out | `harness/version.json` đã refresh | chỉ khi `--update` sau sync | hash khớp disk |

### Rules và capabilities
- RULE-01 (MUST): Fail-open tuyệt đối: lỗi mạng / thiếu version.json → báo cáo phần local, KHÔNG chặn phiên.
- RULE-02 (MUST): `harness/version.json` là nguồn sự thật duy nhất cho version — không hardcode version ở chỗ khác.
- RULE-03 (MUST): Pattern set = `includes` trong `.template-manifest.json`, TRỪ `harness/version.json` và các file "sống" theo project (`index.md`, `log.md`, `active-context.md`, `decisions.md`) — chúng được seed nhưng không tính drift.
- RULE-04 (MUST): `--bump` chỉ ở repo template; project con chỉ `--update`.
- RULE-05 (MUST): Thêm pattern mới: add vào `.template-manifest.json` `includes` TRƯỚC, rồi `--update`.
- Capabilities: đọc disk + manifest + version.json cục bộ; đọc version.json remote (tuỳ chọn, có thể offline); ghi version.json chỉ khi `--update`.

### Failure boundaries
- Mạng lỗi / remote không với tới → báo phần local, **partial**, không chặn (RULE-01).
- Thiếu `harness/version.json` → báo phần kiểm được, không chặn.
- `--fail-on` gặp nhóm vi phạm → **failed** (exit 2) cho gate CI.
- DRIFT không rõ là cải tiến hay lỡ tay → **clarify** với user trước khi upstream hay revert.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | repo, nhánh | Chạy báo cáo `harness/scripts/health-check.py` (có/không remote) | bảng status + dòng OKF | offline → B01 |
| W02 | judgment | báo cáo | Đọc kết quả theo bảng status | hành động khuyến nghị | `OK` → xong |
| W03 | effect | khuyến nghị | Hành động: `/sync-template` downstream/upstream hoặc `git checkout -- <file>` | pattern đã đồng bộ/revert | DRIFT mơ hồ → clarify |
| W04 | effect | sau sync | Refresh fingerprint `--update` (bump chỉ repo template, B02) | version.json khớp disk | — |

Chi tiết từng bước (nguồn chân lý cho W01–W04):

#### 1. Chạy báo cáo (đối chiếu cả remote)
```bash
python3 harness/scripts/health-check.py --root . --branch orca
```
- `--offline` : chỉ kiểm local (bỏ fetch remote) khi không có mạng.
- `--json`    : output máy đọc (dùng cho hook / CI).
- `--fail-on behind,drift,missing` : exit 2 nếu nhóm chỉ định vi phạm (dùng cho gate CI).

#### 2. Đọc kết quả
| status | nghĩa | hành động |
|--------|-------|-----------|
| `OK` | pattern đủ + khớp remote | không cần làm gì |
| `DRIFT` | pattern bị sửa local | cân nhắc **upstream** (`/sync-template` push) hoặc revert |
| `NEEDS-SYNC` | thiếu file hoặc remote mới hơn | chạy **downstream** `/sync-template` |

Báo cáo còn kèm 1 dòng **OKF v0.1**: `✓ OKF v0.1: N/N concept đạt chuẩn` (mọi concept có YAML frontmatter + `type`) hoặc `⟳ OKF v0.1: x/N … cần migrate`. Đây là câu trả lời nhanh "project đã đạt chuẩn OKF chưa?". Chưa đạt → `python3 harness/scripts/okf-check.py --migrate`.

#### 3. Hành động theo khuyến nghị
- **BEHIND / MISSING** → gọi `/sync-template` (downstream): kéo pattern mới/thiếu về.
- **DRIFT** → nếu cải tiến muốn giữ: `/sync-template` upstream; nếu lỡ sửa: `git checkout -- <file>`.

#### 4. Sau khi sync xong — refresh version.json
Mỗi lần downstream sync đổi nội dung pattern, cập nhật lại fingerprint:
```bash
python3 harness/scripts/health-check.py --update            # giữ nguyên version
python3 harness/scripts/health-check.py --update --bump patch   # khi PHÁT HÀNH bản mới (chỉ làm ở repo template)
```
> `--bump` (major/minor/patch) CHỈ chạy ở repo template `Rheinmir/setup` khi muốn công bố version pattern mới cho mọi project. Project con chỉ `--update` (không bump) để đồng bộ hash sau khi pull.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | user_optional | không có mạng / user muốn chỉ kiểm local | thêm `--offline`, bỏ fetch remote | lỗi mạng khi không cờ → vẫn báo phần local (fail-open) | W02 |
| B02 | conditional_required | đang ở repo template `Rheinmir/setup` và phát hành bản pattern mới | `--update --bump patch` (major/minor/patch) | project con → chỉ `--update` | kết thúc |
| B03 | capability_optional | chạy trong gate CI/hook | `--json` và/hoặc `--fail-on behind,drift,missing` | — | W02 (hoặc exit 2) |

### Validation và stopping
Status do `health-check.py` tính tất định (hash + so version), không do model đoán. Dừng khi status `OK`, hoặc sau khi hành động khuyến nghị xong và `--update` đã đồng bộ hash.

### Examples
- **Positive:** đầu phiên, remote `orca` có `template_version` mới hơn → báo `NEEDS-SYNC` (BEHIND) → gọi `/sync-template` downstream → `python3 harness/scripts/health-check.py --update` → chạy lại ra `OK`.
- **Boundary/failure:** máy offline, chạy không `--offline` → fetch remote lỗi, vẫn in phần local (DRIFT/MISSING) và không chặn phiên; nhóm BEHIND không xác định được.

### Reference — Quan hệ với skill khác
- [[sync-template]] — health-check **chẩn đoán** (có cần sync không); sync-template **thực thi** (kéo/đẩy file). Luôn chạy health-check trước, sync-template sau.
- `harness/scripts/wiki-health.py` — anh em cùng tầng L4 nhưng soi **nội dung wiki** (broken link, orphan, stale), không soi version pattern.

## Origin
- Draft: `llmwiki/wiki/sources/draft/150626-health-check-pattern-sync.md`
