---
type: draft
title: Hoàn tất đăng ký docs-gate hook (R10)
tags: [harness, hook, docs-gate, R10, install]
timestamp: 2026-06-23
---

# Proposal: Hoàn tất đăng ký docs-gate hook (R10)

**Status:** implemented (2026-06-23 — T1+T2 claude-cli, T3 opencode worker_done)

## Bối cảnh

Hook `llmwiki/.claude/hooks/user_prompt_submit.py` đã viết xong và **test 3 nhánh PASS**
(mốc-5 inject directive; có dùng `/docs-site-macos` hay `/orca-workflow` trong cửa sổ → im;
project không có wiki → im). Rule [[R10]] đã thêm vào `harness/policy.yaml`. Nhưng hook **chưa
được đăng ký** vào bất kỳ settings nào → chưa kích hoạt. Đây là nợ "code xong, chưa wire".

## Plan

- [ ] **T1** — Đăng ký `UserPromptSubmit` vào `llmwiki/.claude/settings.json` (template)
- [ ] **T2** — Đăng ký `UserPromptSubmit` vào `harness/scripts/install-harness.sh`: global `tpl` + ROOT `tpl`
- [ ] **T3** — Smoke-test qua settings thật + chạy `health-check.py --update` cho version.json

**Sequence diagram**: [230626-docs-gate-register-seq.html](../../../html/230626-docs-gate-register-seq.html)

## Agent Task Assignment

| Task | Agent CLI | Lý do chọn | Status |
|------|-----------|-----------|--------|
| T1 — settings.json template | claude-cli | Harness-critical: merge JSON + thứ tự hook, sai là gãy phiên | done |
| T2 — install-harness.sh (global+ROOT) | claude-cli | Bash+python heredoc, ngữ nghĩa exit-2 chặn — dễ vỡ | done |
| T3 — smoke-test + version.json | opencode | Cơ học: chạy hook, đọc exit code, health-check --update | done |

## Tiêu chí hoàn thành

- 3 settings (template `llmwiki/.claude/settings.json`, global `~/.claude/settings.json`, ROOT `.claude/settings.json`) đều có `UserPromptSubmit` sau khi cài.
- Smoke-test: hook im ở prompt 1–4, inject ở prompt 5; project không-wiki vẫn im.
- `version.json` nhận diện file hook mới (không drift cảnh báo sai ở SessionStart).
- Không hook nào khác mất khả năng chặn (exit 2 còn nguyên).

## Origin

- **Source:** `wiki/sources/draft/230626-docs-gate-register.md` — đề xuất trong phiên 2026-06-23 (feature từ /orca-workflow "hoàn tất đăng ký docs-gate hook").
- **Date:** 2026-06-23
