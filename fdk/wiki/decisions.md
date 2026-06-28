# Decisions Log

> Ghi lại các quyết định quan trọng (approve/reject proposal, chọn hướng kỹ thuật).

| Date | Decision | Type | Context | Outcome |
|------|----------|------|---------|---------|
| 2026-06-27 | Thêm R11 seq-html-glass-style | rule | Style glass chỉ ở prose skill → bị bỏ qua | policy.yaml `conditional_require`, enforce_at session; shipped |
| 2026-06-27 | R12 chỉ (B) orchestrator sweep + (C) pre-push; BỎ (A) per-edit | architecture | Đa-vendor: chỉ git-level + orchestrator phủ hết | gỡ per-edit PreToolUse; [[ADR-002-pull-before-change-gates]] |
| 2026-06-27 | Duyệt + ship R12 v3 workspace-aware | gate | gate_16a0e503882d; nhiều subrepo/1 workspace | T1-T5 done, test 4/4; commit 076f970 |
| 2026-06-27 | T2 gộp vào discovery dùng chung | design | list-subrepos cần cho sweep + installer (≥2 use case) | 1 file `list-subrepos.py` thay parser riêng |
| 2026-06-27 | Backfill rule-registry + ADR | docs | Bus-factor=1: luật/lý do trong đầu | [[rule-registry]] + ADR-001/002; decisions.md lấp |
| 2026-06-27 | T1 reconcile policy.yaml | rule | R3/R4/R8/R10 enforce bằng hook, vắng khỏi policy | thêm dạng hook_event (11 rule); R3/R8 điều tra ra KHÔNG drift |
| 2026-06-27 | T5 drift-test gen-converters↔policy | test | out/ gitignored → bắt 'gen DROP/lệch policy' | drift-test 28/28, negative proven, wire pre-commit |
| 2026-06-27 | T4 + đóng gap-backfill | docs | Runbook thiếu → người mới phải đọc đầu tác giả | CONTRIBUTING-harness.md; T1-T5 done |
| 2026-06-27 | policy-drives-wiring | architecture | wiring hook hardcode ở gen-converters | gen SINH từ hook_event (event_action/blocking/matcher/timeout); output IDENTICAL; drift-test 36/0 (mở rộng ADR-001 policy-as-source) |
| 2026-06-27 | R11 bật repo-tier | rule | 8 seq html cũ flat chặn repo-tier | migrate override glass (non-destructive); enforce_at +repo; pre-commit hook |
| 2026-06-27 | R6 + reconcile 2 policy | rule | R6 chỉ ở production policy; 2 policy lệch rule-set | R6=verify-before-commit; +R11/R12 prod, +R6 poc; drift-test gác parity |
| 2026-06-27 | propose = single source of truth | architecture | /propose ↔ orca-workflow tả lại lệch nhau (glass-style drift) | ADR-003: orchestrator delegate /propose; Claude=substance, CLI-rẻ=render (Full, watchdog+R7) |
| 2026-06-27 | seq html message phải hiện sẵn | rule | R7-(d) bài 130626: opacity:0 ẩn nội dung người-đọc | spec /propose + 2 seq html sửa: .msg opacity≥.82, animation chỉ highlight |
| 2026-06-27 | FDK = front-door phát triển framework | architecture | xương rải rác + AGENT.md không có lối vào + module-map drift | [[fdk]]: hợp nhất rule-registry/CONTRIBUTING/recipe/ADR/dev-loop; pre-flight gate; map bằng lệnh live (chốt ở ADR-004) |
| 2026-06-27 | FDK có cửa chủ động bơm ngữ cảnh | architecture | doc thụ động phải tự mở → vẫn miss | session_start.py thêm fdk_context() (sau REVERT bởi ADR-004 → opt-in /fdk); pointer ở AGENT/CLAUDE |
| 2026-06-27 | framework-dev context opt-in | architecture | auto-bơm FDK mọi phiên = nhiễu (phần lớn phiên dev dự án KHÁC) + trỏ file ma downstream | ADR-004: gỡ fdk_context khỏi SessionStart → skill /fdk on-demand; audit 5 điểm auto-fire |
| 2026-06-28 | content_files lọc gitignored tại lister + guard | architecture | wiki-tree scanner bỏ-quên-lọc gitignored → false-positive archive (recur 3×, bắt qua /failure-flywheel) | ADR-007: an-toàn-mặc-định ở lister + harness-lint --scanners/--copies vào CI repo-health; commit 06884e2/b0b238b/976c6c0 |
| 2026-06-28 | wiki framework tách sang the kit (fdk/wiki) | architecture | wiki riêng framework lẫn slot llmwiki/ với project tiêu thụ; "mọi thứ dev-harness nên trong kit" | ADR-008: mv → fdk/wiki + repath ~10 invocation + llmwiki/wiki giữ 1 demo; downstream không đổi |
| 2026-06-28 | session-orientation + auto-index + force-query | architecture | phiên mới "lơ ngơ" không biết query code-index/wiki; index sửa tay; propose không ground | ADR-009: orient() đầu phiên + stop.py index --fix + R7-f ## Context; test wire CI/pre-commit |
| 2026-06-28 | gate decision→ADR (R13) + edit/delete-when-superseded | architecture | quyết định kiến trúc dễ quên ghi ADR; nhưng ADR bất biến cứng thì không dọn được | ADR-010: decision_adr.py — ép decisions.md ref ADR, edit tự do, xóa chỉ khi bị đè; test 5/5 CI/pre-commit |
| 2026-06-29 | project-local harness (harness-local/) | architecture | dự án cần luật RIÊNG nhưng sửa file framework thì sync đè, dựng hook song song thì giẫm chân R1–R13 | ADR-011: dir harness-local/ ngoài manifest, id P<n>≠R<n>, framework chạy trước (AND), 3 tầng; sandbox 13 test CI |
| 2026-06-29 | docs-gate R10 thêm trụ đánh giá/eval | rule | R10 chỉ nhắc tài liệu; eval (wikieval) bị bỏ quên cùng nhịp 5-prompt | (no-adr: mở rộng R10) 2 trụ độc lập docs+eval trong user_prompt_submit.py; verified 4 case; [[R10]] |
| 2026-06-29 | 5 trend 2026 → 5 chức năng qua BNAL | architecture | last30days quét ra 5 hướng chưa có; mỗi hướng dính 1 ẩn số không chốt ngay được | ADR-012: success-flywheel·egress-guard·trace-otel·spec-gate·scoped-hooks — core tất định now, adapter verified:false; 10 self-test + leak-gate vào fdk-gate |
| 2026-06-29 | 5 trend 2026 nữa → 5 chức năng qua BNAL (đợt 2) | architecture | quét trend tiếp; lấp memory + token/$ governor + injection-output + hallucination + prospective-reflection | ADR-013: mem-rank·token-budget·inject-scan·claim-receipts·prospect-critic; 15 self-test BNAL trong fdk-gate; nối failure-flywheel/egress-guard |
| 2026-06-29 | kho pattern tham chiếu BẢO VỆ (R14) | architecture | user cần kho pattern+anti-pattern cho 7 vai trò + loops, bảo vệ chỉ sửa khi cho phép | ADR-014: llmwiki/patterns/ + patterns_guard (unlock env LLMWIKI_PATTERNS_UNLOCK), seed từ /last30days+repo star+crawl loop-library; BNAL verified:false; parity 14=14, test 7/7 |
