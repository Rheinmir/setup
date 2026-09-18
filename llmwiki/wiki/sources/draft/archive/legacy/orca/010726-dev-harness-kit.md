---
type: draft
title: "Dev tự build harness riêng — thiết kế BNAL + council 18 ông"
status: proposed
tags: [build-now-adapt-later, council, harness-local, output-report]
proposed: 2026-07-01
id: 010726-dev-harness-kit
---

# 010726-dev-harness-kit

**Type:** draft · **Status:** proposed · **Proposed:** 2026-07-01

## What
Thiết kế (chưa code) cơ chế cho mỗi dự án **tự build harness riêng** — adapt vào dự án mà KHÔNG chạm module gốc (cài curl) + **bảo vệ file dev tạo** khỏi sửa nhầm. Phân tích theo build-now-adapt-later, đánh giá bằng council 18 persona (lõi `council.py` tất định, đã thoát loop). Báo cáo người-đọc: `llmwiki/html/010726-dev-harness-kit-council.html`.

## Nền ĐÃ CÓ (đừng dẫm)
- `harness-local/` (ADR-011): dự án tự viết validator `P<n>`, 3 tầng (write/commit/CI), AND-precedence, NGOÀI `.template-manifest.json` → curl/framework-update không đụng. Fail-open. → **"adapt không chạm core" ĐÃ giải.**
- `patterns_guard.py` (R14): `protected_dir` + `unlock_env`, fail-safe block. → cơ chế "protected file" CÓ nhưng mới phủ `llmwiki/patterns`, chưa phủ harness-local.
- `install-harness.sh`: scaffold `harness-local/` (run.py+README+policy mẫu+`_template.py`) khi chưa có.

## Boundary (BNAL)
- **Contract (dựng now, chắc):** (1) scaffolder `new-local-rule.py` sinh 1 rule P<n> từ template; (2) `harness-local seal` ghi sha256 manifest + `--verify` wire fdk-gate/CI; (3) R14-ext phủ `harness-local/`.
- **Quarantine (verified:false):** mức/hạt seal (từng-file vs cả-dir) + unlock (env vs lệnh) → 1 config `harness-local/seal.config.yaml`; và có làm sealed-bundle để PHÂN PHỐI harness sang dự án khác không.

## Council 18 ông — verdict (mean-rank, blind)
| # | Phương án bảo vệ | mean-rank |
|---|---|---|
| 1 | **checksum-seal** (sha256 manifest, gate verify) | 1.39 |
| 2 | R14-ext (protected_dir phủ harness-local) | 1.72 |
| 3 | chmod OS read-only | 3.00 |
| 4 | sealed-zip | 3.89 |

**Chairman:** checksum-seal làm CHÍNH (bắt mọi thay đổi qua git, transparent, cross-platform, hợp audit-chain Trụ 5) + R14-ext làm lớp write-time (bù điểm mù lúc-ghi) = phòng-thủ-tầng. Loại zip (phản transparency). Dissent: Linus/Machiavelli/Aurelius/Munger đẩy R14-ext #1 (tái dùng, ship ngay); Lão Tử thích chmod (tối giản).

## Cái CÒN THIẾU (cho user quyết)
3 mảnh CHẮC dựng được ngay (scaffolder · seal-command · R14-ext); 2 ẩn số chờ user finalize (hạt seal + unlock UX; distribution bundle).

## Files
| File | Action |
|------|--------|
| `llmwiki/html/010726-dev-harness-kit-council.html` | created (report, gitignored render) |
| `harness/scripts/council.py` (roster/personas) | dùng lại — engine không đổi |

## Notes
- Invoked via: `/fdk` + `/build-now-adapt-later` (thiết kế) → `/council` 18 persona → `/docs-site-macos` (report).
- Council THOÁT LOOP: chạy 1 lượt mean-rank tất định, không vòng lặp.

## Origin
- **Draft:** `wiki/draft/orca/010726-dev-harness-kit.md`
- **Commit:** _(chưa — đây là thiết kế/đánh giá, code dựng sau khi user duyệt)_
- **Date promoted:** _(sau khi user quyết 2 ẩn số)_
