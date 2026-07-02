---
type: decision
title: "ADR-004: framework-dev context là opt-in (gọi /fdk), không auto-bơm đầu phiên"
status: accepted
tags: [adr, fdk, session, hook, downstream, opt-in, anti-pattern]
timestamp: 2026-06-27
id: ADR-004-framework-dev-context-opt-in
---

# ADR-004: framework-dev context là opt-in, không auto-bơm

## Status
Accepted (2026-06-27)

## Context
Mục đích **chính** của framework này là được cài vào **dự án khác** để hỗ trợ phát triển chúng (kỷ luật wiki, propose, harness gác rule cho dự án đó). Việc phát triển *chính* framework chỉ là một nhánh phụ, ít phiên.

Khi dựng FDK, một context-pump đã bị gắn vào hook `SessionStart` (`session_start.py` → `fdk_context()`): mỗi phiên tự in "Phát triển CHÍNH framework? — N skills · M validators · …". Đây là một **lỗi tư duy**: nó mặc định *mọi phiên là dev framework*. Trong một phiên dùng framework để xây app của người khác, block này là nhiễu; tệ hơn, nó trỏ tới `llmwiki/wiki/concepts/fdk.md` — một file **không được distribute downstream** (wiki content là per-project, không nằm trong template manifest), nên ở dự án khác nó trỏ vào hư không.

Audit cùng lúc soi các điểm auto-fire khác xem có phạm cùng lỗi không:

| Nơi | Phán | Lý do |
|-----|------|-------|
| `session_start.py` → `fdk_context()` | phạm | bơm nội-bộ-framework mọi phiên (đã gỡ) |
| `AGENT.md`/`CLAUDE.md` pointer FDK | phạm nhẹ | auto-load + distributed downstream, trỏ file không có downstream (đã slim) |
| `session_start.py` pattern-health | không | báo template downstream tụt remote — đúng việc downstream |
| `user_prompt_submit.py` R10 docs-gate | không | nhắc tài liệu hoá *dự án hiện tại* (bất kỳ), không phải nội-bộ-framework |
| `harness-events.py` m_session | biên | "N rule đang gác" — về harness gác wiki dự án hiện tại, giữ |

## Decision
1. **Framework-dev context là opt-in.** Gỡ `fdk_context()` khỏi `SessionStart`. Front-door FDK chuyển thành skill gọi chủ động **`/fdk`** (canonical `llmwiki/skills/utils/fdk.md` + mirror `skills/fdk/SKILL.md`): khi gọi mới nạp front-door + in inventory live + nhắc pre-flight.
2. **Pointer trong AGENT.md/CLAUDE.md là điều kiện, trỏ skill.** Đổi từ "đọc fdk.md TRƯỚC" (directive vô điều kiện, trỏ file không-có-downstream) sang "Đang phát triển CHÍNH framework? Gọi `/fdk`" — điều kiện, trỏ skill (skill *được* distribute, nên không trỏ hư không).
3. **Nguyên tắc chung:** chỉ auto-bơm vào mọi phiên những gì phục vụ *dự án hiện tại* (downstream-relevant: pattern-health, docs-gate, harness gác). Mọi context *nội-bộ-framework* (FDK, inventory framework, runbook sửa rule) phải opt-in.

## Consequences
- (+) Phiên dev dự án khác không còn bị nhiễu bởi nội-bộ-framework; không còn pointer trỏ file ma downstream.
- (+) Người dev framework vẫn lấy đủ context bằng một lệnh `/fdk` — chủ động, đúng lúc.
- (+) Có tiêu chí rõ để xét hook tương lai: "cái này phục vụ dự án hiện tại hay nội-bộ-framework?" — chỉ loại đầu mới được auto-fire.
- (−) Mất tính "tự nhắc" — người mới phải biết có `/fdk`. Bù lại: pointer điều kiện ở AGENT/CLAUDE + skill nằm trong danh sách skill.

## Origin
- **Decision rút từ:** phản hồi user phiên 2026-06-27 — "cái tự fill đầu session bơm context framework… thành 1 slash skill để chủ động gọi vì ko phải phiên nào cũng là dev framework"; kèm yêu cầu audit "cái nào cũng phạm lỗi tư duy này không".
- **Nguồn:** `llmwiki/.claude/hooks/session_start.py`, `skills/fdk/SKILL.md`, [[fdk]], cùng họ [[ADR-003-skill-as-single-source-of-truth]].
