---
type: draft
title: /harness-update dưới 30s — installer tự trả nợ trong 1 lần gọi
tags: [harness, skill, performance, install-harness, self-heal]
timestamp: 2026-06-23
---

# Proposal: đưa `/harness-update` về dưới 30s

**Status:** implemented (2026-06-23 — bench: migrate-có-nợ 0.56s, re-run sạch 0.31s, smoke ⛔×3)

## Bối cảnh

`/harness-update` hôm nay chậm KHÔNG vì CPU mà vì **số round-trip của agent**. Đọc `SKILL.md`
+ `install-harness.sh` thấy 4 nút thắt:

1. **Vòng lặp backfill phía agent** (SKILL bước 3/3b): khi audit thấy nợ (rc=3), AGENT đọc
   output → sửa file → **re-run cả installer**, lặp tới 3 vòng; rồi okf-check `--check` → `--migrate`
   → re-run nữa. Mỗi re-run lặp lại TOÀN BỘ copy + ~8 `python3` spawn + smoke. Đây là chi phí lớn nhất.
2. **`git log` từng file** trong backfill Origin → N subprocess.
3. **~8 `python3` rời** mỗi lần install (cold-start ~100-150ms mỗi cái).
4. **Clone mạng fallback** có thể treo ~20s khi `src_ok` mơ hồ.

Đòn bẩy: **gộp vòng lặp nhiều round-trip thành 1 lệnh bash tự chữa**. Backfill (Origin, index, OKF)
đều đã là thao tác cơ học có sẵn script — chuyển vào trong installer thay vì để agent lặp.

**Phạm vi tầng:** đụng `harness/scripts/` (install-harness.sh + audit.py mới) và skill `harness-update`.
KHÔNG đổi `policy.yaml` (L0), KHÔNG đổi ngữ nghĩa validator (kết quả audit phải y hệt).

## Plan

- [ ] **T1** — Thêm cờ `--self-heal` vào `install-harness.sh`: sau audit (mục 6), nếu có nợ thì installer TỰ backfill (Origin + index + OKF migrate) ngay trong process, re-audit 1 lần, rồi activate + smoke. Không cờ = hành vi cũ y nguyên.
- [ ] **T2** — Thêm `harness/scripts/audit.py` gộp origin + index + wiki-health + okf về 1 process (import validator như module, in 1 JSON debt-report); Origin backfill dùng 1 lượt `git log` cho cả lô thay vì từng file.
- [ ] **T3** — Idempotent + chặn clone treo: thêm `--no-clone` fast-fail (rc=1, không treo mạng), skip copy khi `cmp -s` bằng, skip `pre-commit install` nếu đã cài. Lần chạy lại (sạch) < 5s. Smoke 3-rule cuối GIỮ NGUYÊN.
- [ ] **T4** — Viết lại `SKILL.md` về 1 phát gọi `install-harness.sh --self-heal` (bỏ vòng lặp agent-side); benchmark `time` 2 case (migrate có nợ + update sạch) ghi `harness/metrics/harness-update-bench.json`; cổng: migrate < 30s, update < 5s, smoke ⛔×3.

**Sequence diagram**: [230626-harness-update-sub30s-seq.html](../../../html/230626-harness-update-sub30s-seq.html)

## Agent Task Assignment

| Task | Agent CLI | Lý do chọn | Status |
|------|-----------|-----------|--------|
| T1 — cờ `--self-heal` | claude-cli | Ngữ nghĩa exit-code/backfill hook-critical, dễ vỡ | done |
| T2 — gộp audit + git log 1 lượt | claude-cli | Phải giữ nguyên kết quả validator (in-process semantics) | done |
| T3 — idempotent + no-clone guard | opencode → claude-cli | Dispatch opencode treo >6 phút (0 output, không sửa file) → kill theo rule skill, claude-cli tiếp quản | done |
| T4 — viết lại skill + benchmark | claude-cli | Viết prose skill (không caveman) + đặt tiêu chí đo wall-clock | done |

## Tiêu chí hoàn thành

- Case migrate CÓ NỢ trên repo thật: tổng wall-clock **< 30s** (đo bằng `time`).
- Case update SẠCH (chạy lại): **< 5s**.
- Agent chỉ gọi installer **1 lần** trong luồng skill mới (không vòng lặp re-run phía agent).
- Smoke 3-rule cuối vẫn **⛔×3 BỊ CHẶN ✓** — không cắt smoke để ăn gian thời gian.
- Không cờ `--self-heal` → installer chạy y hệt hành vi cũ (backward-compatible).
- Backfill vẫn là THÊM, không sửa/xóa nội dung wiki; không đụng `raw/`.

## Origin

- **Source:** `wiki/sources/draft/230626-harness-update-sub30s.md` — đề xuất phiên 2026-06-23 qua `/orca-workflow`, sau khi đọc `install-harness.sh` + `harness-update/SKILL.md` và xác định nút thắt là số round-trip agent, không phải CPU.
- **Date:** 2026-06-23
