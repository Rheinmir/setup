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

- [ ] **T1** — Reconcile `policy.yaml` về đúng nguồn chân lý: thêm entry R8 (`index_sync`) + R10 (`docs-gate`, enforce_at `[session]` UserPromptSubmit); annotate trạng thái R3/R4/R6 (retired/reserved) ngay trong file để không còn số ma.
- [ ] **T2** — Tạo `wiki/concepts/rule-registry.md`: bảng canonical R1..R10 (id · name · validator/hook · enforce_at · status · vì sao). Một trang người mới đọc là đủ.
- [ ] **T3** — Lấp `wiki/decisions.md` + seed ADR thật: `ADR-001-policy-as-source-of-truth`, `ADR-002-agent-vs-deterministic`, `ADR-003-thin-adapter-thick-policy` — chốt tiêu chí quyết định rút từ chat Gemini + đầu tác giả.
- [ ] **T4** — `harness/CONTRIBUTING-harness.md`: runbook "thêm một rule thế nào" gắn với tiêu chí ADR (sửa policy.yaml → thêm validator → regen converters → test).
- [ ] **T5** — Drift-test: assert output `gen-converters.py` khớp `policy.yaml`; wire vào CI (`.github/`/`evals`). *(Ghi chú: `out/` đang gitignored — regenerate từ policy → drift chặn từ nguồn; test chỉ cần assert gen chạy sạch.)*
- [x] **R11 (thêm live 2026-06-27)** — `seq-html-glass-style` (kind `conditional_require`, enforce_at `[session]`): seq HTML phải có marker glass docs-site-macos (`backdrop-filter` + `linear-gradient(180deg,#f7fbff…` + edge-highlight). Đã test: chặn flat (exit 2), cho qua glass, không đụng non-seq. **Nợ:** backfill R11 vào rule-registry (T2) + 1 ADR (T3); cân nhắc bật `[repo]` sau khi migrate ~8 seq html cũ.
- [x] **R12 (thêm live 2026-06-27 · rút gọn về (B)+(C))** — `pull-before-change` (kind `process_gate`): **(B)** pre-work sweep MỘT LẦN do orchestrator (workflow Step 0, `pull-gate.sh gate1`) → base tươi trước fan-out đa-agent; **(C)** pre-push git-level (`.git/hooks/pre-push` + `.pre-commit` stage pre-push + install-harness `--hook-type pre-push`) chặn **mọi vendor**. **ĐÃ BỎ (A) per-edit PreToolUse** (cost cao, lệch vendor, (B) đã phủ) — gỡ khỏi `pre_tool_use.py` + `gen-converters.py`. Lý do: chỉ git-level (C) + orchestrator (B) phủ được mọi vendor; lifecycle session từng vendor không tin được. Đã test: synced→pass, local-sau-remote→pre-push block exit 2. **Nợ:** rule-registry (T2) + ADR (T3); R12 v3 workspace-aware sweep nhiều subrepo (propose riêng).

## Agent Task Assignment

| Task | Agent CLI | Lý do chọn | Status |
|------|-----------|------------|--------|
| T1 reconcile policy.yaml (R8/R10/annotate R3-4-6) | Claude Code | Ngữ nghĩa hook/enforce_at dễ vỡ, ảnh hưởng gate thật → architectural | pending |
| T2 rule-registry.md | OpenCode `big-pickle` | Tổng hợp bảng từ nguồn đã xác định, cơ học | pending |
| T3 decisions.md + 3 ADR | Claude Code | Cần reasoning của tác giả (tiêu chí quyết định), không boilerplate | pending |
| T4 CONTRIBUTING-harness.md | OpenCode `big-pickle` | Runbook theo khuôn đã chốt ở T1–T3 | pending |
| T5 drift-test + CI wire | Kiro | Test + config CI, độc lập verify được | pending |

## Sequence diagram

Mỗi task một sơ đồ (badge agent, message từng bước, nhánh an toàn): [`270626-framework-gap-backfill-seq.html`](../../../html/270626-framework-gap-backfill-seq.html)

## Origin

- **Request:** user — "xem chat Gemini + /orca-workflow, bổ sung phần framework còn thiếu", scope chốt = "chỉ dựng propose draft".
- **Baseline:** `rheinmir/setup#orca` @ origin/orca (fetched 2026-06-27, 0 ahead/0 behind). Bằng chứng đọc trực tiếp: `harness/poc-vendor-neutral/policy.yaml`, `harness/validators/*.py`, `wiki/decisions.md`, `wiki/sources/adr/README.md`, `concepts/R10.md`, `concepts/architecture.md`.
- **Commit:** _(verify-before-commit điền khi promote)_
