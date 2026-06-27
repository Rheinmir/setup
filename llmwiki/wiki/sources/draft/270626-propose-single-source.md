---
type: draft
title: propose-single-source — /propose là SoT, orca-workflow delegate
status: proposed
tags: [skill, dry, propose, orca-workflow, refactor]
timestamp: 2026-06-27
---

# 270626-propose-single-source

**Status:** proposed

## What
Biến skill `/propose` thành nguồn chân lý duy nhất cho hành vi propose (hấp thụ cả gap glass-style hiện chỉ có trong `orca-workflow`), rồi cho `orca-workflow` **gọi** `/propose` thay vì mô tả lại bằng văn xuôi — sau này sửa chỉ đụng skill con.

## Vì sao
- Hiện `orca-workflow` bước 2 mô tả lại toàn bộ quy trình propose **và** giàu hơn skill `/propose` thật (nó bắt buộc style `docs-site-macos` glass; `/propose` thì chỉ nói "2 màu"). → Hai định nghĩa cùng một việc, lệch nhau = drift.
- DRY: một nguồn chân lý. Tiền lệ có sẵn — `orca-workflow` bước 1 **đã** delegate sang skill `query` (không chép lại query), nên áp cùng pattern cho propose là nhất quán.

## Affected
| File / Symbol | How it changes |
|---------------|----------------|
| `llmwiki/skills/dev-loop/propose.md` | **SoT** — bước 7 thêm block bắt buộc style `docs-site-macos` glass (clone mẫu seq html), nuốt gap từ orca-workflow |
| `skills/propose/SKILL.md` (mirror) + `~/.claude/skills/propose/SKILL.md` | sync từ canonical (hiện đang giống hệt → giữ giống hệt) |
| `llmwiki/skills/orchestrate/orca-workflow.md` | bước 2 thay prose R7/style bằng **"GỌI `/propose`"**; giữ nguyên bước 0/1/3–7 |
| `skills/orca-workflow/SKILL.md` (mirror) | sync từ canonical |
| `llmwiki/wiki/sources/adr/ADR-003-*.md` | **mới (tùy chọn)** — ghi quyết định "skill con = SoT, orchestrator delegate" |

## Risks
- **orca-workflow mất chi tiết khi delegate** → giảm thiểu: mọi yêu cầu (R7 + glass-style) phải đã nằm trong `/propose` TRƯỚC khi xoá prose ở orca-workflow (T1 xong rồi mới T2). Validator R7 vẫn gác cặp `.md`+`.html` bất kể gọi từ đâu.
- **"Sửa 1 nơi" chỉ đúng nếu mirror được sync** → đã có cơ chế: `sync-template` + Output-Report push remote. Không chép tay 3 bản; canonical `dev-loop/propose.md` là nơi sửa.
- **ADR thừa** nếu thấy nặng → có thể bỏ T3, ghi quyết định gọn trong `decisions.md` thay vì ADR riêng.

## Plan
- [x] **T1** — Đưa gap vào SoT: bước 7 `/propose` thêm block bắt buộc style `docs-site-macos` glass **+ phần (B) prose chi tiết** (gap riêng phát hiện trong phiên). Đã sync 3 bản giống hệt.
- [x] **T2** — orca-workflow delegate + tách render: bước 2 đổi sang *"GỌI `/propose`"* (như bước 1 gọi `query`); thêm mô hình **Claude-nghĩ / CLI-rẻ-render** — Claude xuất SUBSTANCE (`.md` + `## Render brief`), `.html` render cơ học **dispatch sang CLI rẻ chung** (OpenCode `big-pickle` → `agy` → `kiro`, $0), tier **Full** `docs-site-macos`, watchdog ~60–90s + R7 gate + fallback Claude. Giữ nguyên bước 0/1/3–7. Đã sync mirror.
- [x] **T3** — Ghi quyết định: tạo `ADR-003-skill-as-single-source-of-truth.md` + dòng `decisions.md` + cập nhật `index.md`/`log.md`.

## Agent Task Assignment
| Task | Agent (CLI) | Lý do chọn | Status |
|------|-------------|------------|--------|
| T1 | claude | Hợp nhất spec + đảm bảo style block đúng & 3 bản đồng nhất, nặng phán đoán | done |
| T2 | claude | Cắt prose → delegate, phải giữ đúng ngữ cảnh orchestration không vỡ luồng | done |
| T3 | claude | Viết ADR văn xuôi đầy đủ cho người đọc (không caveman) | done |

> Toàn bộ trên `claude`: chỉnh sửa skill/ADR nặng phán đoán quy ước, khối lượng nhỏ (3 file canonical + 2 mirror), không có phần cơ học song song đáng tách sang opencode.

## Success criteria
- `orca-workflow` bước 2 không còn mô tả lại R7/style — chỉ còn 1 dòng delegate `/propose`; grep style-block trong orca-workflow = rỗng, trong `propose.md` = có.
- Chạy `/propose` standalone tạo seq HTML **glass-style** (giống file tạo trong phiên này), không còn ra bản phẳng/tối.
- 3 bản `propose` (canonical/mirror/global) vẫn `diff` = SAME sau thay đổi.
- Validator R7 vẫn PASS dù propose được gọi standalone hay qua orca-workflow.

## Notes
- Quan hệ với [[270626-wiki-sync-structure]]: tách riêng — đó là drift *số liệu tài liệu*, đây là DRY *skill*.
- [[ADR-001-policy-as-source-of-truth]], [[ADR-002-pull-before-change-gates]] — cùng họ "một nguồn chân lý, thin-adapter".
- **Giả định chờ xác nhận:** orca-workflow chỉ thay **bước 2**; query (bước 1) và gate/dispatch (3–7) giữ nguyên là việc điều phối.
- **Sequence diagram:** [270626-propose-single-source-seq.html](../../../html/270626-propose-single-source-seq.html)

## Origin
- **Draft:** `wiki/sources/draft/270626-propose-single-source.md`
- **Commit:** _(filled by `verify-before-commit`)_
- **Date promoted:** _(filled by `verify-before-commit`)_
