---
type: concept
title: harness-local — harness RIÊNG của dự án
status: implemented
tags: [harness, project-local, validator, namespace, sync-safe]
timestamp: 2026-06-29
---

# harness-local — dự án tự phát triển rule riêng

Nơi **một dự án downstream** tự viết rule/validator riêng, chạy **song song** framework R1–R13 mà **không giẫm chân**. Thư mục `harness-local/` **thuộc về dự án** — nằm ngoài `.template-manifest.json` nên `sync-template`/framework-update **không bao giờ đụng**.

## Cách thêm một rule (3 bước)
1. `cp harness-local/validators/_template.py harness-local/validators/<ten>.py` rồi viết logic trong `check()`.
2. Khai vào `harness-local/policy.yaml` với id **`P<n>`** (P = project; **không** dùng `R<n>` — đụng framework).
3. Xong. Rule tự chạy 3 tầng như framework: write-time (PreToolUse), commit (pre-commit), merge (CI).

## Contract (framework cam kết ổn định)
Một validator nhận event qua **stdin JSON** (`{action,file_path,content,command}`) *hoặc* **argv là file**; `exit 0`=pass, `exit 2`=block (lý do ra stderr); lỗi → **fail-open**. File mở đầu bằng `_` bị bỏ qua. Vì cùng contract, có thể copy một validator framework (`harness/validators/*.py`) làm mẫu.

## Vì sao không giẫm chân
- **Namespace tách:** id `P<n>` ≠ `R<n>` (runner guard chặn nếu khai `R`); validator ở dir riêng.
- **Sync-safe:** ngoài manifest → framework-update bỏ qua; contract ổn định → validator cũ vẫn chạy khi framework lên version.
- **Precedence:** framework kiểm TRƯỚC, harness-local SAU → cả hai phải pass (AND); dự án **không tắt được** rule framework.
- **An toàn khi vắng/lỗi:** không có rule → no-op; validator crash → fail-open (không gãy phiên/commit).

## Công cụ
- `harness-local/run.py --list` — xem rule hiện có · `--check` — self-test (id hợp lệ + validator compile).
- `harness/tests/harness-local-test.sh` — 13 test sandbox mọi case đụng độ (chạy trong CI `repo-health`).

## Liên quan
- [[ADR-011-project-local-harness]] — quyết định kiến trúc + đầy đủ case sandbox.
- [[harness-enforcement-floor]] — 3 tầng enforce của framework mà cơ chế này soi gương theo.
- Front-door how-to chi tiết: `harness-local/README.md` (đi cùng dự án).

## Origin
- **Source:** goal-set phiên 2026-06-28→29 (dự án tự phát triển harness riêng + sandbox case fail). Code: commit `4c0e370`.
- **Date:** 2026-06-29
