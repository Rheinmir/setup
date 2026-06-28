---
type: decision
title: "ADR-007: wiki-tree scanner lọc gitignored TẠI LISTER (nguồn), không per-consumer; guard mọi bản hand-synced"
status: accepted
tags: [adr, harness, gitignore, drift, failure-flywheel, content-files, guard]
timestamp: 2026-06-28
---

# ADR-007: wiki-tree scanner lọc gitignored tại lister, không per-consumer

## Status
Accepted (2026-06-28). Guardrail đã ship trên `orca` qua 3 commit: `06884e2`, `b0b238b`, `976c6c0`. ADR này promote từ một seed do `/failure-flywheel` sinh (class `spec-violation`, recur 3 lần ≥ threshold 3).

## Context
Có nhiều công cụ "quét cây wiki" (wiki-tree scanner): R3 index-sync (so cây file với `index.md`), R9 OKF (kiểm frontmatter), wiki-health, duplicate-basename… Mỗi cái có **lister `content_files()` riêng** liệt kê file dưới `concepts/entities/sources/draft/architecture/tours`.

Quy ước nền (`.gitignore` + skill `/docs-curate`): các thư mục **local-only bị gitignore** — `sources/draft/archive/`, `html/`, draft cá nhân — **cố ý không nằm trong `index.md`** và không phải đối tượng của các rule wiki. Một file gitignored là "rác cục bộ", không phải nội dung wiki chính thức.

Lỗi lặp lại: bộ lọc gitignored được đặt ở **CHỖ TIÊU THỤ** (trong `main()`, trong từng caller) chứ không ở **lister**. Lister trả về *tất cả* file, mỗi consumer phải tự nhớ lọc `git check-ignore`. Khi logic được copy sang scanner mới, người ta **quên lọc** — và scanner false-positive trên file `archive/`. Lỗi này tái diễn **3 lần** trong một phiên trước khi được đóng có hệ thống:

| # | Scanner | Triệu chứng |
|---|---------|-------------|
| 1 | `harness-events.py` `m_stop` (R3, bản PoC bundled) | Stop-hook **nag** đòi thêm 1 file `archive/` đã gitignored vào `index.md` |
| 2 | `audit.py` `detect` (R3) | **18 false-positive** `index_missing`, toàn bộ dưới `archive/`; `audit --fix` sẽ **nhồi cả 18 file gitignored vào `index.md`** (đảo ngược đúng thứ `/docs-curate` vừa archive ra) |
| 3 | `okf-check.py` `content_files` (R9) | Latent — chưa cắn (file archive tình cờ có OKF hợp lệ) nhưng cùng lỗ hổng |

Đây là `spec-violation`: scanner phớt lờ ràng buộc "gitignored = local-only, ngoài index/rule". Nguyên nhân gốc không phải "một người cẩu thả" mà là **kiến trúc mời gọi quên** — an-toàn phụ thuộc việc mỗi consumer nhớ làm đúng.

## Decision
Đóng lỗi ở **3 tầng**, từ vá tức thời tới làm-cho-bất-khả-tái-diễn:

1. **Vá từng consumer** (tầng tức thời) — mỗi scanner trên lọc `git check-ignore` cho chiều `exist`; chiều `stale` vẫn lọc riêng (vì `indexed` lấy từ `index.md` có thể trỏ file gitignored).
2. **An-toàn-mặc-định ở LISTER** (tầng gốc rễ) — chuyển bộ lọc gitignored **vào trong `content_files()`**. Lister giờ trả về tập đã-loại-gitignored; mọi caller (`main`, `audit`, `indexed_files`, okf) đúng **mà không cần nhớ lọc**. Đây là điểm mấu chốt: *lọc tại nguồn, không per-consumer*.
3. **Guard chống tái drift** (tầng phòng thủ) — `harness-lint` thêm hai check, gộp vào `--check` (đã chạy ở CI job `repo-health`):
   - `--scanners`: mọi file trong `WIKI_TREE_SCANNERS` phải còn marker skip-gitignored (`git check-ignore`/`gitignored()`). Bắt được khi một scanner mới/sửa đánh rơi skip.
   - `--copies`: bản R3 validator deployed (`llmwiki/.claude/hooks/validators/index_sync.py`) phải **byte-identical** với bản master (`harness/validators/index_sync.py`). Bản deployed phải self-contained cho downstream clone không có `harness/`, nên buộc tồn tại 2 bản hand-synced — guard này chống chúng lệch (chúng từng lệch: deployed thiếu self-heal `fix()`).

**Nguyên tắc tổng quát hoá:** lọc/chuẩn-hoá ở **lister/nguồn**, đừng bắt mỗi consumer tự làm. Khi không thể có một nguồn duy nhất (bản deploy phải self-contained), thì **duplicate có chủ đích + guard byte-identity** — đừng để bản sao âm thầm trôi.

## Consequences
- (+) Lỗi `archive/` false-positive đóng ở 3 tầng: vá · an-toàn-mặc-định · guard CI. Scanner tương lai khó tái phạm mà không bị `harness-lint --check` chặn trên PR/push.
- (+) Tiêu chí dứt khoát cho mọi lister wiki mới: nó phải lọc gitignored *bên trong*, và nếu là bản sao thì phải vào `WIKI_TREE_SCANNERS`/`SYNCED_COPIES`.
- (−) Logic `gitignored()` buộc lặp ở các đơn-vị-deploy self-contained (deployed `index_sync`, PoC `harness-events`, `okf-check`) — chấp nhận, và `--scanners` gác sự lặp đó.
- (−) Guard chỉ "cắn" ở CI (push/PR) vì repo chưa `pre-commit install`; gating lúc-commit cục bộ là tuỳ chọn. Không hạ thấp giá trị — CI là sàn không bypass được.

## Origin
- **Source:** chưng cất bởi `/failure-flywheel` — class `spec-violation` recur 3× (≥ threshold 3, `harness/failure-flywheel.config.yaml` verified=True, `distill.model=null` nên seed là stub cho người hoàn thiện). Seed `280626-failure-spec-violation.md` được promote thành ADR này rồi gỡ. Lịch sử lỗi ở `harness/metrics/failures.jsonl` (gitignored, local).
- **Code:** `06884e2` (consumer fix + `--scanners`), `b0b238b` (`content_files` an-toàn-mặc-định + sync 2 bản + `--copies`), `976c6c0` (okf-check + mở guard R3→R9). Tất cả trên `orca`, CI `repo-health` xanh.
- **Liên quan:** [[rule-registry]], [[ADR-006-blocking-stays-hook-mcp-for-tooling]], [[ADR-004-framework-dev-context-opt-in]].
- **Date:** 2026-06-28
