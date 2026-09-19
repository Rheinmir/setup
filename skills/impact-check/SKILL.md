---
name: impact-check
description: Map all callers and dependents of a symbol before modifying shared code
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: impact-check

## WHAT

### Purpose và context
- **Purpose:** Before modifying any symbol (function, class, variable, config key), map all dependents so no callers blindsided.
- **Trigger (when to use):**
  - Before editing shared utility, base class, or widely-imported module
  - Before renaming or deleting anything
  - As first step of `safe-change` or `propose`
- **Non-goals:** không sửa code (output only); không tạo trang wiki cho symbol chưa document (chỉ ghi gap).

### Mental model
`symbol → mọi reference (import · call · đọc output) → Direct / Indirect → test refs tách riêng → báo cáo + wiki gap`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | symbol(s) cần đổi | có | function, class, variable, config key |
| Out | danh sách reference | có | file path, line number, cách dùng, nhãn Direct/Indirect; zero ngoài file thì nói rõ |
| Out | test refs | có nếu có | liệt kê riêng |
| Out | wiki gap | nếu có | symbol chưa có trong `wiki/` |
| Out | draft output report | có (trừ khi 0 artefact) | `llmwiki/wiki/sources/draft/DDMMYY-<ten>.md` |

### Rules và capabilities
- RULE-01 (MUST): Do not modify anything during this skill — output only.
- RULE-02 (MUST): If codebase large, search by symbol name AND file pattern (e.g. all `*.ts` files).
- RULE-03 (MUST): Do not assume symbol unused because no direct callers — check indirect dependents too.
- Capabilities: đọc/tìm toàn codebase (text search hoặc code graph); ghi draft report + index/log wiki.

### Failure boundaries
- Symbol mơ hồ (nhiều định nghĩa cùng tên) → **clarify** symbol chính xác.
- Zero reference ngoài file → **succeeded**, nói rõ "0 reference ngoài file".
- Không tìm được hết (codebase quá lớn, search lỗi) → **partial**, ghi phạm vi đã quét.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | judgment | yêu cầu sửa | Xác định đúng symbol | symbol list | mơ hồ → clarify |
| W02 | deterministic | symbol | Tìm mọi import/call/reference toàn codebase | hits | lớn → tên + file pattern |
| W03 | deterministic | hits | Ghi file path, line, cách dùng | bảng ref | — |
| W04 | judgment | bảng ref | Phân loại Direct / Indirect | ref đã gắn nhãn | — |
| W05 | deterministic | ref | Báo cáo đủ, tách test refs, zero thì nói rõ | báo cáo | — |
| W06 | deterministic | `wiki/` | Ghi gap nếu symbol chưa document (không tạo entry) | gap note | — |
| W07 | effect | kết quả | Output Report draft | draft + index + log | 0 artefact → skip |

Chi tiết từng bước (nguồn chân lý cho W01–W07):

1. Identify exact symbol(s) to change.
2. Search entire codebase for all imports, calls, references to each symbol.
3. For each reference: note file path, line number, how it uses symbol.
4. Classify each reference:
   - **Direct** — calls or imports symbol itself
   - **Indirect** — depends on behaviour symbol produces (e.g. reads its output)
5. Report full list. If zero references found outside file, state explicitly.
6. Flag any reference in test file separately — those must update or give false confidence.
7. If symbol not yet documented in `wiki/`, note as gap — do not create entry now. Wiki entries only written after code committed (see `verify-before-commit`).

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | codebase lớn | search theo tên symbol VÀ file pattern (RULE-02) | — | W03 |
| B02 | conditional_required | có reference trong test file | liệt kê riêng, cảnh báo phải cập nhật | không có → skip | W06 |

### Validation và stopping
Dừng khi mọi hit đã có path + line + nhãn Direct/Indirect. Không kết luận "unused" chỉ vì thiếu direct caller (RULE-03). Không file code nào bị sửa.

### Examples
- **Positive:** đổi chữ ký `formatDate(d)` trong `src/utils/date.ts` → 12 Direct (import) + 2 Indirect (đọc chuỗi output để parse) + 3 test refs liệt kê riêng → báo cáo + draft `DDMMYY-impact-format-date.md`.
- **Boundary/failure:** config key `retry_limit` không có caller trực tiếp nhưng được đọc qua `config[key]` động → xếp Indirect, KHÔNG báo "unused"; nếu quét không hết thì báo partial kèm phạm vi.

### Delivery — Output Report

After all main skill tasks complete, write a propose draft to the wiki.

#### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/sources/draft/DDMMYY-<ten>.md`:

```
---
type: draft
title: "DDMMYY-<ten>"
status: proposed
tags: [<skill-name>, output-report]
timestamp: YYYY-MM-DD
---

# DDMMYY-<ten>
**Type:** draft
**Status:** proposed
**Tags:** <skill-name>, output-report
**Proposed:** YYYY-MM-DD

## What
<One sentence — what this skill invocation produced or decided>

## Output
<Key artefacts, files created/modified, or decisions made>

## Files
| File | Action |
|------|--------|
| `path/to/file` | created / modified |

## Notes
- Invoked via: `/<skill-name>` skill

## Origin
- **Draft:** `wiki/sources/draft/DDMMYY-<ten>.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
```

**3. Update wiki index & log:**
- `llmwiki/wiki/index.md` — append one row: `| [DDMMYY-<ten>](sources/draft/DDMMYY-<ten>.md) | draft | YYYY-MM-DD |`
- `llmwiki/wiki/log.md` — append: `## YYYY-MM-DD — <skill-name> — <ten>`

> Skip only when the skill produces zero artefacts and zero decisions (e.g., a pure display mode like `/caveman-stats`).
