---
name: lint
description: Periodic wiki health check — orphans, missing links, contradictions, stale (wiki→wiki VÀ code→wiki drift), index gaps. Bước 0 là cổng no-op tất định (wiki-sync, 0 token) — code không đổi kể từ neo thì kết luận "wiki current" và dừng sớm hợp lệ.
---

# Skill: lint

## When to invoke
After every 10 ingests, or when wiki stale/inconsistent, hoặc session_start báo `[wiki-sync] code đã đổi N commit`.

## Steps

0. **Code-drift gate (0 token)** — `RUN: python3 harness/scripts/wiki-sync.py --check` (downstream không có harness/ trong repo thì dùng bản global: `python3 ~/.claude/harness/harness/scripts/wiki-sync.py --check --root .`).
   - Exit 0 (`current`): code không đổi kể từ neo → nếu mục đích lượt lint này là "wiki có khớp code không" thì **dừng tại đây, trả lời "wiki đã current"** — no-op là kết quả tốt, đừng bịa việc. Vẫn muốn quét sức khoẻ nội-wiki (orphan/index/origin) thì đi tiếp bước 1.
   - Exit 3 (`drift`): các trang nghi stale đã được cờ `code-drift` trong `stale.json` kèm file code gây ra. **Lập docs-impact-plan TRƯỚC khi sửa**: mỗi trang định sửa phải truy về một thay-đổi-code cụ thể (`code đổi → trang → sửa gì → vì sao`); trang không truy được về thay đổi nào thì KHÔNG đụng.
   - Exit 2 (chưa có neo / neo mất hiệu lực): làm trọn lint rồi chốt neo ở bước 10.

1. **Orphans** — `RUN: grep -rL "wiki/" --include="*.md" llmwiki/wiki/concepts/ llmwiki/wiki/entities/` → files not referenced anywhere. Flag each.

2. **Missing links** — scan pages for entity/concept names that exist as wiki files but not written as `[[wikilinks]]`. Fix in place.

3. **Contradictions** — compare claims about same entity across ≤2 pages at a time. Flag pairs (file:line vs file:line). Do NOT pick winner — flag for human review.

4. **Stale claims** — `RUN: grep -rl "raw/" --include="*.md" llmwiki/wiki/` → pages referencing raw/. Flag each.

5. **Index gaps** — `RUN: comm -23 <(find llmwiki/wiki -name "*.md" | sort) <(grep -o "llmwiki/wiki/[^)]*" llmwiki/wiki/index.md | sort)` → files missing from index. Add rows.

6. **Empty pages** — `RUN: for f in llmwiki/wiki/**/*.md; do [ $(wc -l < "$f") -lt 5 ] && echo "$f"; done` → flag for deletion or content.

7. **Missing Origin** — `RUN: grep -rL "## Origin" llmwiki/wiki/concepts/ llmwiki/wiki/entities/` → flag each as incomplete.

8. **Marker nợ thiếu trigger** — `RUN: grep -rn "shortcut:" --include="*.py" --include="*.js" --include="*.ts" --include="*.sh" . | grep -v ",";` → mỗi marker `shortcut:` cố ý phải có định dạng `<trần hiện tại>, <trigger nâng cấp>` (dấu phẩy tách 2 vế). Dòng lọt qua grep này = marker thiếu trigger nâng cấp (nợ không hạn → dễ thành "never"). Flag từng dòng cho người viết bổ sung trigger; KHÔNG tự đoán trigger.

8c. **Nợ unknown (fill-first, chờ verify — tất định, 0 token)** — `RUN: python3 harness/scripts/unknown-ledger.py --list` → in số unknown mở + cái cũ nhất + SPEC nào nhiều nợ nhất. Đây là các default model điền "để việc chạy tiếp, tính sau" (`(default, find-out-later)`). **BÁO CÁO, KHÔNG CHẶN** — fill-first cố ý không chặn; chặn ở đây là phản bội cơ chế. Mục đích: nợ hiện ra để không chìm, người duyệt tự quyết khi nào trả (xem `[[150726-unknown-ledger]]`).

8b. **Skill-health (hình dạng skill, tất định — 0 token)** — `RUN: python3 harness/scripts/skill-health.py` (repo có `skills/`) → in tổng context load model-invoked + skill nào có cờ: `desc` (description quá dài) · `sprawl` (SKILL.md quá dài mà không progressive disclosure) · `negation` (tỉ lệ câu cấm cao — nên chuyển sang câu khẳng định) · `weak-criterion` (khối `### Task` thiếu điều kiện kiểm được ở cuối) · cặp description chớm-trùng. Tiêu chí gốc ở `[[skill-craft]]`. **Báo cáo, KHÔNG chặn** — chất lượng, không phải an toàn. Flag để người viết cân nhắc, đừng tự sửa hàng loạt.

8b. **Skill-usage pulse (0 token, chỉ repo framework)** — `RUN: python3 fdk/tools/skill-usage.py --weekly --no-html` → bảng tần suất tuần + skill chết (idle ≥4 tuần). Đây là dây nuôi máy đo "skill nào đáng giữ" (wired 2026-07-18, vòng grower): usage tụt/chết là DỮ KIỆN cho quyết định cắt-giữ, không phải cảm tính. Downstream không có `fdk/tools` → bỏ qua bước này.

9. Append to `llmwiki/wiki/log.md`: `## YYYY-MM-DD — lint` with issues found/fixed vs flagged.

10. **Chốt neo** — `RUN: python3 harness/scripts/wiki-sync.py --mark-synced` (hoặc bản global như bước 0). Chỉ ghi khi nội dung wiki thực sự đổi (content-hash); tự xoá cờ `code-drift` đã rà. Vòng phản hồi phải khép: không chốt neo = lần check sau báo drift giả.

## Rules
- Fix automatically: missing links (step 2), index gaps (step 5).
- Flag, not resolve: contradictions, orphans, empty pages — need human decision.
- **Surgical update** (distill openwiki 060726): sửa trang stale = thay đúng câu sai, KHÔNG viết lại trang còn đúng; ưu tiên sửa 1 câu hơn thêm 1 đoạn.
- **Soft diff budget**: <5 file code đổi → sửa tối đa 1–2 trang wiki; thấy cần sửa >3 trang → dừng lại tự vấn vì sao trước khi sửa rộng.
- **Cấm formatting-only edit**: không reformat bảng, không chuẩn hoá dòng trống/wording khi nội dung xung quanh không sai — diff nhiễu là nợ cho reviewer.
- **Canonical home**: mỗi concept một trang chính chủ; trang khác chỉ nhắc ngắn + `[[wikilink]]`, không nhân bản giải thích.
- **No-op hợp lệ**: "wiki đã current, không sửa gì" là một kết quả lint thành công — ghi log rồi dừng, đừng sửa lấy có.

---

## Output Report

After all main skill tasks complete, write a propose draft to the wiki.

### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/sources/draft/DDMMYY-<ten>.md`:

```
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
