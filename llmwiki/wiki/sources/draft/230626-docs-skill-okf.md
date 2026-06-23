---
type: draft
title: Skill tạo docs phải xuất chuẩn OKF v0.1 — vá 3 skill còn lệch
tags: [harness, skill, okf, R9, docs, onboard]
timestamp: 2026-06-23
---

# Proposal: skill tạo docs đạt chuẩn OKF v0.1 (vá nguồn tạo nợ)

**Status:** implemented (2026-06-23 — test docs-skill-okf 10/10 PASS, wiki OKF 7/8)

## Bối cảnh

Audit OKF (sau khi ship `/harness-update --self-heal`) cho thấy nền OKF tốt nhưng **nguồn tạo
docs còn lệch**:

- **Wiki repo:** 6/7 file đạt OKF (chỉ `220626-chown.md` legacy chưa migrate — ngoài phạm vi).
- **Template:** 4/4 `_template.md` (`concepts`/`sources`/`entities`/`draft`) đã đạt OKF → "copy template" là tự đúng chuẩn.
- **Skill tạo docs — 3 chỗ lệch:**
  1. `orca-onboard`: heredoc (~dòng 240) ghi draft bằng `**Type:** draft` **bold** — đúng format CŨ mà OKF thay thế → file sinh ra **fail R9 ngay lúc tạo**. Nghịch lý: skill onboard *tạo nợ OKF* mà chính `/harness-update --self-heal` phải đi dọn.
  2. `onboard-codebase`: KHÔNG nhắc OKF/frontmatter (chỉ `## Origin`).
  3. `new-project-setup`: nói "frontmatter" mơ hồ, không nêu `type`.
- `ingest`/`propose`/`query` đã nhắc R9 rõ → đạt. `md-to-html`/`docs-site-macos` xuất HTML → OKF không áp (N/A).

Nguyên tắc vá: **sửa tận nguồn** (skill tạo docs) thay vì dựa self-heal dọn mãi.

**Phạm vi tầng:** chỉ sửa file skill trong `llmwiki/skills/` + thêm test `harness/tests/`. KHÔNG đụng
`policy.yaml` (L0), KHÔNG đổi validator (R9 giữ nguyên).

## Plan

- [ ] **T1** — `orca-onboard.md`: đổi heredoc draft từ `**Type:** / **Status:** / **Tags:**` bold sang khối YAML frontmatter `---\ntype: draft\ntitle: …\nstatus: proposed\ntags: […]\ntimestamp: …\n---`; giữ `**Status:** proposed` trong body (R7) + `## Origin` (R2). Output phải pass `okf-check`.
- [ ] **T2** — `onboard-codebase.md` + `new-project-setup.md`: thêm 1 dòng Rule nhắc OKF (chép pattern từ `ingest`/`propose`): "mọi trang wiki bắt đầu bằng YAML frontmatter có `type` không rỗng — copy `_template.md` (R9)". Chỉ thêm dòng nhắc, không đổi logic.
- [ ] **T3** — `harness/tests/docs-skill-okf-test.sh`: với mỗi skill sinh wiki .md → assert prose nhắc OKF/`_template.md`; riêng heredoc `orca-onboard` → render thử ra file tạm rồi `okf-check --check` phải rc=0; skill HTML ghi N/A. Cổng: wiki repo `okf-check` rc=0 (trừ legacy đã biết).

**Sequence diagram**: [230626-docs-skill-okf-seq.html](../../../html/230626-docs-skill-okf-seq.html)

## Agent Task Assignment

| Task | Agent CLI | Lý do chọn | Status |
|------|-----------|-----------|--------|
| T1 — vá heredoc orca-onboard | claude-cli | Output phải pass `okf-check` chính xác; heredoc dễ vỡ escape | done (sửa cả 2 chỗ: heredoc + example block) |
| T2 — thêm dòng nhắc OKF (2 skill) | opencode → claude-cli | Dispatch opencode no-op lần 2 (0 output, không sửa file) → claude-cli tiếp quản | done |
| T3 — test chặn hồi quy OKF | claude-cli | Thiết kế test + phân biệt skill .md (áp) vs HTML (N/A) | done (10/10 PASS) |

## Tiêu chí hoàn thành

- Heredoc `orca-onboard` sinh draft **pass `okf-check --check` (rc=0)** — không còn `**Type:**` bold.
- `onboard-codebase` + `new-project-setup` có dòng Rule nhắc OKF + copy `_template.md`.
- `harness/tests/docs-skill-okf-test.sh` chạy: mọi skill tạo wiki .md đạt, skill HTML ghi N/A, tổng PASS.
- `python3 harness/scripts/okf-check.py --wiki-dir llmwiki/wiki` rc=0 (trừ `220626-chown.md` legacy đã biết).
- Không đổi validator R9, không đụng `policy.yaml`, không sửa logic skill ngoài khối metadata/Rule.

## Origin

- **Source:** `wiki/sources/draft/230626-docs-skill-okf.md` — đề xuất phiên 2026-06-23 qua `/orca-workflow`, sau audit OKF phát hiện `orca-onboard` emit format bold cũ + 2 skill onboard không nhắc OKF.
- **Date:** 2026-06-23
