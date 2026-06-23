---
type: draft
title: Hook thiếu file không được brick toàn bộ Bash — fail-open guard + kênh giao hook
tags: [harness, hook, orca-guard, install-harness, fail-open, manifest, bugfix]
timestamp: 2026-06-23
---

# Proposal: hook thiếu file phải FAIL-OPEN, đừng chặn cả CLI

**Status:** implemented (2026-06-23 — gate duyệt; golden test 6/6 PASS, idempotent re-merge sim OK, 3 python block compile OK)

## Bối cảnh — sự cố thật ở client

Client `cozyroom` (Windows, migrate/SAME_BUNDLE) chạy `/orca-workflow` → installer →
**MỌI lệnh Bash bị chặn**:

```
PreToolUse:Bash hook error: can't open file
'C:\Users\olive\orca\cozyroom\llmwiki\.claude\hooks\orca_guard.py': [Errno 2] No such file or directory
```

Đọc `install-harness.sh` + `llmwiki/.claude/settings.json` thấy **2 lỗi độc lập**:

1. **BRICK — lệnh hook không fail-open.** Lệnh hook là `python3 "<path>"` TRẦN: file thiếu →
   exit ≠ 0 → PreToolUse báo lỗi → **chặn luôn tool**. Có ở 3 chỗ:
   - `llmwiki/.claude/settings.json` (committed) — lệnh trần, không guard.
   - installer ROOT `h()` (L193-196) — sinh lệnh trần.
   - installer GLOBAL `cmd()` (L82) — chỉ guard `[ -d llmwiki ]`, KHÔNG kiểm file `-f`.
   → Một guard script (orca_guard) **mất tích lại có quyền khoá cả CLI** — sai về an toàn.

2. **DELIVERY GAP — không có kênh giao hook mới.** `orca_guard.py` (thêm ở commit b0f30e0)
   tới project kiểu-bundle qua **0 đường**: installer L149 `[ "$SAME_BUNDLE" = "0" ] && cp …hooks/*.py`
   → SAME_BUNDLE **bỏ qua copy**; và 8 file `llmwiki/.claude/hooks/*.py` **không nằm trong
   `.template-manifest.json`** → `/sync-template` không kéo. Nên client cập nhật settings/installer
   (có tham chiếu orca_guard) nhưng **không bao giờ nhận được file**.

Đòn bẩy: (1) guard fail-open ở MỌI nơi sinh lệnh hook → file thiếu thì BỎ QUA, không chặn;
(2) thêm hook vào manifest → `/sync-template --full` giao được file.

**Phạm vi tầng:** `harness/scripts/install-harness.sh` + `llmwiki/.claude/settings.json` +
`.template-manifest.json` + `harness/tests/`. KHÔNG đổi ngữ nghĩa `orca_guard.py`, KHÔNG đụng
`policy.yaml` (L0). Hook khi CÓ file vẫn chặn y như cũ — chỉ thay hành vi khi THIẾU file.

## Plan

- [x] **T1** — Fail-open guard ở mọi nơi sinh lệnh hook: đổi lệnh thành `if [ -f "<path>" ]; then python3 "<path>"; fi` tại installer ROOT `h()` (L193-196), GLOBAL `cmd()` (L82, thêm `-f`), và `llmwiki/.claude/settings.json` (committed, 7 command). File thiếu → skip, KHÔNG chặn tool. Re-merge idempotent: dedup theo BASENAME script để chạy lại NÂNG CẤP lệnh trần cũ thành lệnh có guard, không append trùng (sim: user-hook giữ nguyên, 0 trùng).
- [x] **T2** — Kênh giao hook: thêm 8 file `llmwiki/.claude/hooks/*.py` + `settings.json` vào `includes` của `.template-manifest.json` để `/sync-template --full` giao hook cho project kiểu-bundle; refresh `harness/version.json` (57 pattern, orca_guard tracked). Đóng khe hở khiến orca_guard.py không tới được client.
- [x] **T3** — Presence-check + test: installer in `WARN: hook <x> đã đăng ký nhưng THIẾU file` (không fatal) sau khi ghi settings; golden test `harness/tests/orca-guard-failopen-test.sh` 6/6 PASS: thiếu file → exit 0 (fail-open), có file → chạy, exit 2 → guard giữ mã chặn (không nuốt), orca_guard.py trong manifest.

**Sequence diagram**: [230626-orca-guard-failopen-seq.html](../../../html/230626-orca-guard-failopen-seq.html)

## Agent Task Assignment

| Task | Agent CLI | Lý do chọn | Status |
|------|-----------|-----------|--------|
| T1 — fail-open guard + re-merge idempotent | claude-cli | Ngữ nghĩa hook/exit-code hook-critical, dễ vỡ; phải giữ khả năng CHẶN khi có file | done |
| T2 — thêm hook vào manifest + fingerprint | claude-cli | Đụng baseline sync/version, phải khớp với phân loại sync-template | done |
| T3 — presence-check + golden test | claude-cli | Coupled cùng installer T1; làm inline (opencode dispatch bất ổn) | done |

## Tiêu chí hoàn thành

- Trên repo có orca_guard.py: hook **vẫn CHẶN** đúng như trước (không nới lỏng bảo mật).
- Khi orca_guard.py (hay bất kỳ hook nào) **thiếu file**: lệnh Bash chạy bình thường, **KHÔNG bị chặn** (fail-open) — golden test xác nhận.
- Chạy lại installer trên project đã có lệnh trần cũ → lệnh được **nâng cấp thành có guard**, không sinh hook trùng.
- `/sync-template --full` kéo được `llmwiki/.claude/hooks/orca_guard.py` về project kiểu-bundle (T2).
- Không đổi ngữ nghĩa `orca_guard.py`, không đụng `policy.yaml`.

## Cách gỡ ngay cho client (trước khi fix ship)

1. Đặt file vào đúng chỗ: `git show origin/orca:llmwiki/.claude/hooks/orca_guard.py > llmwiki/.claude/hooks/orca_guard.py` — Bash hết bị chặn ngay.
2. Hoặc tạm gỡ entry `orca_guard.py` khỏi `.claude/settings.json` đang active.
3. Sau khi T1 ship: chạy lại `install-harness.sh` (settings được vá guard) + `/sync-template --full` (T2 giao file).

## Origin

- **Source:** `wiki/sources/draft/230626-orca-guard-failopen.md` — đề xuất phiên 2026-06-23 qua `/orca-workflow`, từ sự cố client `cozyroom` (mọi Bash bị chặn vì hook `orca_guard.py` thiếu file). Đọc `install-harness.sh` (L82/L149/L193) + `llmwiki/.claude/settings.json` + `.template-manifest.json` xác định 2 lỗi: lệnh hook không fail-open + không có kênh giao hook mới. Liên quan [[230626-orca-guard-hook]].
- **Date:** 2026-06-23
