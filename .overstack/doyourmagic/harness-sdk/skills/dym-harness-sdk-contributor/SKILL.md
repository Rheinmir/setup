---
name: dym-harness-sdk-contributor
description: "Sửa chính Strands harness (harness-py/harness-ts trong monorepo harness-sdk) — chạy unit test, integ live-model, selective-test theo diff như CI; gồm bẫy môi trường đã đo."
disable-model-invocation: true
---

# Skill: dym-harness-sdk-contributor — nhánh người đóng góp

## When to use
- Đang sửa `harness-py/` hoặc `harness-ts/` trong clone `strands-agents/harness-sdk` và cần chạy đúng cổng CI tại máy.

## Steps
1. harness-py — unit (đo 2026-09-28: **748 passed, 2 skipped, rc 0, 50s**, Python 3.13):
   ```bash
   python3.13 -m venv .venv && .venv/bin/pip install -q './harness-py[dev]'
   cd harness-py && env -u OTEL_TRACES_EXPORTER PATH="$PWD/../.venv/bin:$PATH" \
     AWS_EC2_METADATA_DISABLED=true AWS_REGION=us-east-1 ../.venv/bin/python -m pytest tests -q
   ```
2. harness-py — integ (live model, tốn tiền, cần AWS Bedrock): `python -m pytest tests_integ --reruns 2` (cài `'.[integ]'`). `--collect-only` = 11 test, rc 0; **chưa chạy thật**.
3. harness-ts: `npm run check` (lint + `test:coverage`) trong `harness-ts/`; integ bằng `vitest.integration.config.ts` (retry 2, timeout 300s). **Chưa kiểm chứng** (chưa `npm ci`).
4. Test logic selective-test (bộ phân loại diff → chạy test liên quan): `bash test-infra/scripts/test/classify.test.sh` → **19 passed, rc 0** (đo 2026-09-28).
5. Trước PR: đổi hằng số mặc định thì sửa **cả hai** `defaults.py` và `defaults.ts` (chép tay, không có test parity chéo ngôn ngữ). Luật parity đặt ở `AGENTS.md` gốc.

## Rules
- **Bẫy đã đo:** fixture MCP gọi lệnh `python`; máy chỉ có `python3` → `test_subagent_delegate_inherits_parent_mcp_tools` FAIL với `No such file or directory: 'python'`. Đặt venv `bin` đầu `PATH`.
- **Bẫy đã đo (chưa khoanh biến nào gây):** lượt KHÔNG có venv trong PATH và KHÔNG có `AWS_EC2_METADATA_DISABLED`/`AWS_REGION` chạy **24 phút** (7 failed, 8 errors — đều test MCP thiếu `python`); thêm cả hai thì 50s, xanh.
- Python 3.9 không cài được (`requires-python >= 3.10`).
- `harness-ts/AGENTS.md` bảo `npm ci` ở root rồi `-w harness-ts`, nhưng root `package.json` chỉ khai workspace `strands-ts` → cài trong `harness-ts/` trực tiếp; pre-commit husky vì thế cũng không test harness-ts.
- Design doc đánh số trùng (0009, 0011, 0015 mỗi số 2 file) → trích design thì ghi cả tên file, đừng chỉ ghi số.
- PR do bot/agent mở cần 2 maintainer duyệt; mọi PR tự kích review agent `/strands review`.
