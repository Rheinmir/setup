---
type: draft
title: Framework self-docs gap backfill — policy↔validator drift + ADR rỗng
status: proposed
tags: [harness, policy, adr, decisions, onboarding, bus-factor, R8, R10]
timestamp: 2026-06-27
---

# 270626 — Framework gap backfill

## Bối cảnh

Promote lên techlead nhờ ship framework (harness + llmwiki + orca-workflow). Mục tiêu sống còn của framework là **chống bus-factor=1**: người mới (kể cả fresher tester vừa promote) đọc tài liệu là tự chạy được, gap trình độ bù bằng framework.

Gemini (xem chat import) khuyên đúng tinh thần — "viết design philosophy / ADR" — nhưng nó **chưa từng đọc code**. Khi đọc bản canonical `rheinmir/setup#orca` (đã `fetch`, local = origin/orca, 0 ahead/0 behind) thì:

- Framework **đã chừa sẵn** ô tài liệu: `wiki/decisions.md`, `wiki/sources/adr/`, `wiki/concepts/architecture.md`, `concepts/R10.md`. Tốt hơn lời khuyên "đẻ file mới".
- Nhưng các ô đó **rỗng/lệch**. 4 gap kiểm chứng được dưới đây.

## Gap đã kiểm chứng

| Gap | Loại | Bằng chứng (đường dẫn thật) |
|-----|------|------------------------------|
| **G2 — policy↔validator drift** | Correctness (cao) | `harness/validators/` có 6 validator chạy thật gồm `index_sync.py` (**R8**); `concepts/R10.md` tự khai Origin "Policy: harness/policy.yaml R10". Nhưng `harness/poc-vendor-neutral/policy.yaml` — tự nhận *"NGUỒN CHÂN LÝ DUY NHẤT"* — chỉ chứa **R1,R2,R5,R7,R9**. R8 + R10 enforce thật mà **vắng mặt khỏi policy**. R3/R4/R6 được nhắc 27/17/10 lần trong wiki nhưng không validator, không policy → status mơ hồ (retired? reserved?). |
| **G3 — ADR/decisions rỗng** | Knowledge (cao) | `wiki/decisions.md` = template trống (header + 1 hàng rỗng); `wiki/sources/adr/README.md` = chỉ có template; **0 ADR thật**. Tiêu chí quyết định (agent vs deterministic, khi nào thêm rule, khi nào thêm abstraction/dependency) vẫn chỉ trong đầu tác giả. |
| **G-reg — không có registry luật** | Consistency (vừa) | Không một trang nào liệt kê đủ R1..R10 + tên + nơi enforce (validator/hook) + enforce_at + status + lý do. Người mới phải ghép từ policy.yaml (5), validators/ (6), R10.md (1 hook), refs rải rác. |
| **G5 — thiếu drift-test** | Verification (thấp) | `gen-converters.py` sinh config 6 engine từ `policy.yaml`, nhưng chưa thấy test fail khi adapter out-of-sync → "thick policy / thin adapter" mới đúng trên giấy. |

> Rủi ro trực tiếp: bảo fresher "đọc `policy.yaml` để học luật" → họ học thiếu R8 (chính `index_sync` sẽ chặn commit của họ) + R10. Đây đúng là lỗ hổng của một framework-để-scale-người.

## Plan

> Execution **hoãn** — scope user đợt này = "chỉ dựng propose draft". Các task dưới đây chờ gate.

- [x] **T1** ✓ — Reconcile `policy.yaml`: thêm R3/R4/R8/R10 (kind `hook_event`) → policy liệt kê đủ 11 rule. Điều tra ra **R3/R8 KHÔNG drift** (R3=index-sync nhất quán, R8=session-health). R6 vẫn reserved. Caveat: wiring còn hardcode ở gen-converters (T5 phủ).
- [x] **T2** ✓ — `wiki/concepts/rule-registry.md` R1..R12, 1 trang, flag honest caveat.
- [x] **T3** ✓ — Lấp `decisions.md` + `sources/adr/ADR-001-policy-as-source-of-truth` + `ADR-002-pull-before-change-gates` (gộp agent-vs-deterministic + thin-adapter + R12 reasoning).
- [x] **T4** ✓ — `harness/CONTRIBUTING-harness.md`: runbook thêm/sửa rule (cổng quyết định ADR → phân loại content/hook-event/process → quy trình từng loại → checklist + drift-test bắt buộc + test âm). **→ gap-backfill CLOSED: T1–T5 done.**
- [x] **T5** ✓ — `harness/tests/policy-converters-drift-test.sh`: assert mọi rule vào advisory + deny globs vào opencode/antigravity + **hook_event event khớp wiring claude** (R3→Stop…) + không orphan. **28/28 PASS**; negative test (rule chưa-wire → FAIL=2) chứng minh bắt drift. Wire `.pre-commit-config` (commit-stage). *(out/ gitignored → drift thật = gen-converters DROP/lệch policy, không phải out lệch git.)*
- [x] **R11 (thêm live 2026-06-27)** — `seq-html-glass-style` (kind `conditional_require`, enforce_at `[session]`): seq HTML phải có marker glass docs-site-macos (`backdrop-filter` + `linear-gradient(180deg,#f7fbff…` + edge-highlight). Đã test: chặn flat (exit 2), cho qua glass, không đụng non-seq. **Nợ:** backfill R11 vào rule-registry (T2) + 1 ADR (T3); cân nhắc bật `[repo]` sau khi migrate ~8 seq html cũ.
- [x] **R12 (thêm live 2026-06-27 · rút gọn về (B)+(C))** — `pull-before-change` (kind `process_gate`): **(B)** pre-work sweep MỘT LẦN do orchestrator (workflow Step 0, `pull-gate.sh gate1`) → base tươi trước fan-out đa-agent; **(C)** pre-push git-level (`.git/hooks/pre-push` + `.pre-commit` stage pre-push + install-harness `--hook-type pre-push`) chặn **mọi vendor**. **ĐÃ BỎ (A) per-edit PreToolUse** (cost cao, lệch vendor, (B) đã phủ) — gỡ khỏi `pre_tool_use.py` + `gen-converters.py`. Lý do: chỉ git-level (C) + orchestrator (B) phủ được mọi vendor; lifecycle session từng vendor không tin được. Đã test: synced→pass, local-sau-remote→pre-push block exit 2. **Nợ:** rule-registry (T2) + ADR (T3); R12 v3 workspace-aware sweep nhiều subrepo (propose riêng).

## Agent Task Assignment

| Task | Agent CLI | Lý do chọn | Status |
|------|-----------|------------|--------|
| T1 reconcile policy.yaml | Claude Code | Ngữ nghĩa hook/enforce_at dễ vỡ → architectural | done |
| T2 rule-registry.md | Claude Code (Kiro/OC thiếu) | Tổng hợp từ nguồn đã xác minh | done |
| T3 decisions.md + ADR | Claude Code | Cần reasoning tác giả | done |
| T4 CONTRIBUTING-harness.md | Claude Code (OC thiếu) | Runbook theo khuôn T1-T3+T5 | done |
| T5 drift-test | Claude Code (Kiro thiếu) | Test + wire pre-commit; 28/28 + negative chứng minh | done |

## Sequence diagram

Mỗi task một sơ đồ (badge agent, message từng bước, nhánh an toàn): [`270626-framework-gap-backfill-seq.html`](../../../html/270626-framework-gap-backfill-seq.html)

## Origin

- **Request:** user — "xem chat Gemini + /orca-workflow, bổ sung phần framework còn thiếu", scope chốt = "chỉ dựng propose draft".
- **Baseline:** `rheinmir/setup#orca` @ origin/orca (fetched 2026-06-27, 0 ahead/0 behind). Bằng chứng đọc trực tiếp: `harness/poc-vendor-neutral/policy.yaml`, `harness/validators/*.py`, `wiki/decisions.md`, `wiki/sources/adr/README.md`, `concepts/R10.md`, `concepts/architecture.md`.
- **Commit:** _(verify-before-commit điền khi promote)_
