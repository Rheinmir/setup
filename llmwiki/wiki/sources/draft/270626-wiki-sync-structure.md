---
type: draft
title: wiki-sync-structure — skill phát hiện & sửa drift tài liệu cấu trúc
status: proposed
tags: [wiki, drift, skill, utils, maintenance]
timestamp: 2026-06-27
---

# 270626-wiki-sync-structure

**Status:** proposed

## What
Tạo một skill tái gọi được `/wiki-sync-structure` để phát hiện & sửa drift giữa các tài liệu mô tả cấu trúc trong `llmwiki/` và thực tế repo; lần chạy đầu sửa luôn các drift đã phát hiện.

## Approach (trần phức tạp thấp)
- Skill là **một file markdown thuần** chứa quy trình + **shell one-liner đếm ground-truth** — KHÔNG thêm module Python mới để bảo trì.
- Mọi số liệu volatile (số skill, số file harness) được nhốt trong **marker block** `<!-- auto:counts --> … <!-- /auto:counts -->`. Mỗi lần chạy skill chỉ ghi đè vùng giữa marker → không đụng văn xuôi, không regex mò, idempotent.
- Phần khó tự-động-sửa (bảng skill, dedupe) → skill **báo cáo diff + đề xuất**, người duyệt xác nhận. Tránh auto-edit rủi ro = giữ chi phí bảo trì thấp.

## Affected
| File / Symbol | How it changes |
|---------------|----------------|
| `llmwiki/skills/utils/wiki-sync-structure.md` | **mới** — canonical skill (markdown + shell one-liner) |
| `skills/wiki-sync-structure/SKILL.md` | **mới** — published mirror để `/wiki-sync-structure` gọi được sau cài |
| `llmwiki/AGENT.md` | +1 dòng skill table (loop `utils`) |
| `llmwiki/CLAUDE.md` | đồng bộ skill table với AGENT.md (đang thiếu các dòng utils) |
| `llmwiki/wiki/entities/project-structure.md` | chèn marker auto-counts; số `skills/ = 32` → `56` |
| `llmwiki/wiki/concepts/architecture.md` | chèn marker auto-counts; `32 SKILL.md`→`56`, `harness 25 files`→`44`; ghi chú gap file `03` |
| `llmwiki/wiki/sources/design-pattern-v{1,2,3}.md` ↔ `sources/draft/design-pattern-v{1,2,3}.md` | dedupe — giữ `sources/` làm canonical |
| `llmwiki/wiki/sources/draft/210626-design-pattern-infographic.md` ↔ `draft/orca/210626-…` | dedupe — giữ 1 bản |
| `llmwiki/wiki/index.md` | dọn dòng trỏ tới bản trùng + thêm dòng skill mới |

## Risks
- **Auto-patch số liệu sai vùng** → đã chặn bằng marker block; skill chỉ ghi giữa `<!-- auto -->`.
- **Dedupe xoá nhầm bản canonical** → R4-reversible: skill chỉ đề xuất, người duyệt chọn bản giữ; mặc định giữ `sources/` (bản đã promote) thay vì `sources/draft/` (bản nháp cũ).
- **Skill table 2 file lệch tiếp trong tương lai** → skill so khớp mỗi lần chạy và cảnh báo; không tự sửa âm thầm.
- Quy ước R8: `skills/` (56 published) là con số sẽ tăng — đó chính là lý do nhốt trong marker để re-sync rẻ.

## Plan
- [ ] **T1** — Tạo skill canonical `llmwiki/skills/utils/wiki-sync-structure.md` + published mirror `skills/wiki-sync-structure/SKILL.md`; đăng ký 1 dòng vào bảng skill `AGENT.md` & `CLAUDE.md` (loop `utils`). Skill gồm: shell one-liner đếm `skills/` dirs + `harness/` files + kickoff files; ghi đè marker auto-counts; diff 2 bảng skill; quét basename trùng giữa `sources/` và `sources/draft/`; check `index.md` ↔ đĩa.
- [ ] **T2** — First-run fix số liệu: chèn marker `<!-- auto:counts -->` vào `project-structure.md` & `architecture.md`, đồng bộ `skills 32→56`, `harness 25→44`, và thêm ghi chú gap file `03` (kickoff còn 01/02/04).
- [ ] **T3** — First-run fix bảng skill: reconcile `AGENT.md` ↔ `CLAUDE.md` về cùng một danh sách (CLAUDE.md bổ sung các dòng `utils` đang thiếu; bổ sung `build-now-adapt-later`, `tour-guide`, `new-project-setup` nếu xác nhận là skill chính thức của loop).
- [ ] **T4** — First-run fix dedupe: gỡ bản trùng `design-pattern-v{1,2,3}` + `210626-infographic` (giữ canonical theo quy ước location), dọn dòng `index.md` trỏ tới bản đã gỡ.

## Agent Task Assignment
| Task | Agent (CLI) | Lý do chọn | Status |
|------|-------------|------------|--------|
| T1 | claude | Thiết kế skill + nội dung markdown cần phán đoán cấu trúc/quy ước repo | pending |
| T2 | claude | Chèn marker + đồng bộ số (cơ học nhưng phải đặt marker đúng ngữ cảnh prose) | pending |
| T3 | claude | Hợp nhất 2 bảng skill cần quyết định dòng nào là skill chính thức | pending |
| T4 | claude | Dedupe cần đối chiếu nội dung & chọn bản canonical (không cơ học thuần) | pending |

> Toàn bộ trên `claude`: khối lượng nhỏ (vài file md), nặng phán đoán quy ước wiki, không có phần song song/cơ học lớn đáng tách sang `opencode`. Sau khi ổn định, shell one-liner đếm số trong skill có thể chạy bởi bất kỳ agent nào.

## Success criteria
- `/wiki-sync-structure` chạy lại được, in báo cáo drift và sửa được phần auto (số liệu) idempotent — chạy 2 lần liên tiếp lần 2 báo "no drift".
- Sau first-run: `project-structure.md` & `architecture.md` khớp số thật (56 / 44); `AGENT.md` skill table == `CLAUDE.md` skill table; không còn basename trùng giữa `sources/` và `sources/draft/`; `index.md` không còn dòng trỏ tới file đã gỡ.
- Validator harness (R5 folder, R3 index-sync, R9 OKF) vẫn PASS sau thay đổi.

## Notes
- [[architecture]] · [[project-structure]] — hai tài liệu là nguồn drift chính.
- [[rule-registry]] — skill này hỗ trợ R3 (index-sync) & R8 (fingerprint) ở mức tài liệu.
- **Sequence diagram:** [270626-wiki-sync-structure-seq.html](../../../html/270626-wiki-sync-structure-seq.html)

## Origin
- **Draft:** `wiki/sources/draft/270626-wiki-sync-structure.md`
- **Commit:** _(filled by `verify-before-commit`)_
- **Date promoted:** _(filled by `verify-before-commit`)_
