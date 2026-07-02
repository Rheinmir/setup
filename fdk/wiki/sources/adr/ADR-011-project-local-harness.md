---
type: decision
title: "ADR-011: project-local harness — dự án tự phát triển rule riêng (P-namespace, sandbox-safe)"
status: accepted
tags: [adr, harness, project-local, namespace, sync-safe, precedence, sandbox]
timestamp: 2026-06-29
id: ADR-011-project-local-harness
---

# ADR-011: project-local harness — rule RIÊNG của dự án chạy song song framework

## Status
Accepted (2026-06-29).

## Context
Framework cung cấp R1–R13 — bộ luật **chung** cho mọi dự án downstream. Nhưng mỗi dự án còn có luật **riêng** của nó: "không để `console.log` trong `src/`", "mỗi endpoint mới phải có test", "migration phải kèm rollback"… Những luật này không thuộc framework (không nên áp cho dự án khác), nên không thể nhét vào `harness/policy.yaml`.

Trước ADR này, dự án chỉ có hai lối — đều hỏng:
1. **Sửa thẳng file framework** (`harness/validators/`, `policy.yaml`) để thêm luật riêng → lần `sync-template`/framework-update kế tiếp **ghi đè mất** (những file đó nằm trong `.template-manifest.json`).
2. **Tự dựng hook song song** ngoài framework → dễ **giẫm chân**: trùng id rule, trùng tên validator, không rõ luật nào chạy trước, một validator lỗi làm gãy cả phiên/commit của framework.

Cần một cơ chế cho dự án **tự phát triển harness riêng** mà: (a) sống sót framework-update, (b) không bao giờ giẫm chân R1–R13, (c) không tắt được luật framework, (d) vắng mặt thì vô hại.

## Decision
Thêm một thư mục **`harness-local/`** ở gốc repo — **thuộc về dự án**, nằm **NGOÀI** `.template-manifest.json` nên `sync-template`/framework-update **không bao giờ đụng tới**.

- **Validator** = một file `.py` trong `harness-local/validators/` (không bắt đầu bằng `_`), dùng **đúng contract ổn định** của validator framework: nhận event qua **stdin JSON** (`{action,file_path,content,command}`) *hoặc* **argv là đường dẫn file**; `exit 0`=pass, `exit 2`=block (lý do ra stderr); lỗi bất ngờ → **fail-open** (exit 0). File mở đầu bằng `_` (như `_template.py`) bị runner **bỏ qua** → an toàn làm mẫu/helper.
- **Registry** `harness-local/policy.yaml`: mỗi rule khai id **`P<n>`** (P = project) — **khác namespace** framework `R<n>`. Runner tự guard: id `R<n>` → chặn; sai format → chặn; trùng id → chặn.
- **Runner** `harness-local/run.py` chạy ở **3 tầng y như framework**: write-time (`PreToolUse` → `pre_tool_use.py` gọi `run_local()`), commit (`pre-commit` hook `harness-local` + `harness-local-check`), merge (CI step + `harness/tests/harness-local-test.sh`).
- **Precedence:** trong `pre_tool_use.py`, vòng kiểm framework chạy **TRƯỚC**, `run_local()` chạy **SAU**. Hệ quả: cả luật dự án lẫn luật framework đều phải pass (**AND**) — dự án **không tắt được** rule framework.
- **Scaffold:** `install-harness.sh` tạo `harness-local/` (run.py + README + policy mẫu + `_template.py`) **chỉ khi CHƯA có**; đã có thì để nguyên (không đè rule dự án).

### Các case đụng độ đã sandbox (`harness/tests/harness-local-test.sh` — 13 test)
- **Namespace:** id `R<n>` → chặn (đụng framework); sai format → chặn; trùng id `P<n>` → chặn; `P<n>` hợp lệ + validator compile → cho qua.
- **Write-time (hook):** chặn vi phạm, cho qua bản sạch.
- **Commit-time (files):** chặn file vi phạm, cho qua file sạch.
- **Fail-open độc lập:** validator `_`-prefix bị bỏ qua; validator **crash** → fail-open (không gãy phiên/commit); **0 validator** → no-op (dự án không cài rule vẫn chạy như thường).
- **Sống chung framework:** `harness-local` **ngoài** `.template-manifest.json` (sync-safe); framework chạy **trước** harness-local (precedence — project không vô hiệu hoá được R framework).

## Consequences
- (+) Dự án có **quyền tự trị**: phát triển luật riêng ở 3 tầng giống hệt framework, không phải fork.
- (+) **Sống sót framework-update**: ngoài manifest → sync không đụng; contract ổn định → validator cũ vẫn chạy khi framework lên version.
- (+) **Không thể phá framework**: namespace tách (P≠R), dir tách, framework chạy trước, một validator dự án lỗi chỉ fail-open.
- (+) **Vô hại khi vắng**: không có `harness-local/` → mọi tầng no-op.
- (−) Dự án **tự chịu trách nhiệm** bảo trì validator của mình (framework không review luật P).
- (−) `run.py` **chạy mọi file** trong `validators/` bất kể có khai trong `policy.yaml` không (file = nguồn-sự-thật để chạy; policy chỉ là registry cho người + `--check`). Cố ý: hot-path không parse YAML → bền hơn.

## Origin
- **Source:** goal-set phiên 2026-06-28→29 ("các dự án của user có thể tự phát triển phần harness riêng… deep think… sandbox toàn bộ case fail/giẫm chân… 1 chức năng hoàn chỉnh + docs"). Mechanism + sandbox test + wiring trong commit `4c0e370`.
- **Liên quan:** [[harness-local]], [[harness-enforcement-floor]], [[ADR-008-framework-wiki-lives-in-the-kit]] (cùng tinh thần "thứ của-ai ở chỗ-nấy"), [[ADR-001-policy-as-source-of-truth]].
- **Date:** 2026-06-29
