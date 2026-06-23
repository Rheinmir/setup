---
type: draft
title: /sync-template dưới 30s — gộp mọi bước hậu-sync vào 1 lần gọi script
tags: [harness, skill, performance, sync-template, okf, self-contained]
timestamp: 2026-06-23
---

# Proposal: đưa `/sync-template` về dưới 30s

**Status:** implemented (2026-06-23 — gate duyệt; bench `--full`: steady-state 0.27s · pull+install+verify 0.76s, cả hai < 30s & < 5s)

## Bối cảnh

Đã đo: bản thân các script ĐÃ dưới 1s (fetch song song + tải song song max_workers=12).
`/sync-template` chậm KHÔNG vì CPU mà vì **số round-trip của agent** — y hệt nút thắt đã trị
ở `/harness-update` ([[230626-harness-update-sub30s]]).

`FAST PATH` của SKILL khoe "1 lệnh < 1 giây", nhưng các bước HẬU-SYNC **bắt buộc** quanh nó
ép agent gọi thêm 5–6 tool-call TUẦN TỰ, mỗi cái vài giây:

1. **Step 0 pre-flight** — `health-check` chạy riêng để chọn hướng sync.
2. **Step 6a OKF backfill** — `okf-check --check` rồi `--migrate` ("sau MỌI downstream sync").
3. **Step 6b fingerprint** — `health-check --update` riêng (thực ra script đã làm, nhưng SKILL vẫn liệt kê → agent dễ gọi lại).
4. **Step 8 verify** — agent LẶP qua từng skill kiểm tra 3 vị trí cài.
5. **Rule log.md** — agent tự `Edit` `wiki/log.md` cuối cùng.

Tổng: ~5–6 round-trip × vài giây = >30s, dù mỗi script <0.6s.

**Đòn bẩy:** gộp mọi bước hậu-sync cơ học vào 1 lệnh `sync-template.py --full` tự chứa
(script đã làm sync + install + fingerprint; chỉ cần THÊM OKF backfill, self-verify, ghi log).
Agent gọi 1 lần → đọc 1 report → báo cáo. Round-trip 6 → 2.

**Phạm vi tầng:** đụng `harness/scripts/sync-template.py` + skill `sync-template`.
KHÔNG đổi `policy.yaml` (L0), KHÔNG đổi ngữ nghĩa phân loại NEW/CLEAN/LOCAL/CONFLICT
(kết quả sync phải y hệt), KHÔNG đụng `raw/`.

## Plan

- [x] **T1** — Thêm cờ `--full` vào `sync-template.py`: sau khi sync + install skill (đã có), TỰ chạy tiếp trong CÙNG process: OKF backfill → refresh fingerprint (đặt CUỐI, sau OKF) → self-verify 3 vị trí cài → append `wiki/log.md`. Không cờ = hành vi cũ y nguyên (backward-compatible).
- [x] **T2** — OKF backfill in-process: import `okf-check.py` như module gọi hàm migrate (fallback subprocess 1 lần nếu import fail), idempotent (file đã có YAML frontmatter bỏ qua). Đảm bảo fingerprint refresh chạy SAU OKF migrate để health-check không báo DRIFT giả.
- [x] **T3** — Self-verify + ghi log trong script: thay vòng lặp agent Step 8 bằng kiểm tra 3 vị trí (`.claude/commands/`, `~/.claude/skills/`, `~/.claude/commands/`) cho mỗi skill vừa cài, gộp ✓/✗ vào report; append 1 dòng `wiki/log.md`. CONFLICT vẫn exit 3 — KHÔNG bao giờ tự `--strategy pull` để ăn gian thời gian.
- [x] **T4** — Viết lại `SKILL.md` FAST PATH về 1 phát gọi `sync-template.py --full` (bỏ Step 6a/6b/8 + log.md khỏi luồng agent, giữ làm fallback MANUAL); benchmark `time` 2 case (downstream có pull + chạy lại sạch) ghi `harness/metrics/sync-template-bench.json`; cổng: full < 30s, clean < 5s.

**Sequence diagram**: [230626-sync-template-sub30s-seq.html](../../../html/230626-sync-template-sub30s-seq.html)

## Agent Task Assignment

| Task | Agent CLI | Lý do chọn | Status |
|------|-----------|-----------|--------|
| T1 — cờ `--full` gộp pipeline | claude-cli | Ngữ nghĩa thứ tự bước + exit-code hook-critical, dễ vỡ | done |
| T2 — OKF in-process + thứ tự fingerprint | claude-cli | Phải giữ nguyên kết quả validator/phân loại; ordering tinh tế | done |
| T3 — self-verify + ghi log trong script | claude-cli | Coupled cùng file T1/T2 (sửa song song sẽ chọi) + opencode dispatch bất ổn → claude làm inline | done |
| T4 — viết lại skill + benchmark | claude-cli | Viết prose skill (không caveman) + đặt tiêu chí đo wall-clock | done |

## Tiêu chí hoàn thành

- Case downstream CÓ PULL trên repo thật: tổng wall-clock **< 30s** (đo bằng `time`).
- Case chạy lại SẠCH (không file nào đổi): **< 5s**.
- Agent chỉ gọi script **1 lần** trong luồng FAST PATH mới (không vòng lặp 6a/6b/8/log riêng).
- Phân loại NEW/CLEAN/LOCAL/CONFLICT và exit code GIỮ NGUYÊN — `--full` chỉ THÊM bước hậu-sync.
- CONFLICT vẫn **exit 3 + giữ local**, không tự overwrite để rút ngắn thời gian.
- Không cờ `--full` → script chạy y hệt hành vi cũ (backward-compatible).
- OKF backfill vẫn là THÊM frontmatter, không sửa/xóa body wiki; không đụng `raw/`.

## Origin

- **Source:** `wiki/sources/draft/230626-sync-template-sub30s.md` — đề xuất phiên 2026-06-23 qua `/orca-workflow`, sau khi đo `sync-template.py`/`okf-check.py`/`health-check.py` (đều <0.6s) và xác định nút thắt là số round-trip agent quanh các bước hậu-sync, không phải CPU. Theo khuôn đã chứng minh ở [[230626-harness-update-sub30s]].
- **Date:** 2026-06-23
