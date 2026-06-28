---
type: concept
title: "Harness enforcement floor — 3 lớp, vì sao CI mới là sàn thật"
status: active
tags: [harness, enforcement, ci, layers, vendor-neutral, policy]
timestamp: 2026-06-28
---

# Harness enforcement floor — vì sao CI mới là sàn thật

Harness gác cùng một bộ luật (`policy.yaml`) ở **ba lớp**, nhưng không lớp nào trong số đó đảm bảo như nhau. Hiểu đúng lớp nào là "sàn" quyết định bạn tin được gì.

## Ba lớp gác
1. **Hook (phiên) — L0/L1.** Khi agent (Claude Code, opencode…) định ghi, hook PreToolUse gọi lõi `llmwiki-validate.py` đọc `policy.yaml`; vi phạm → exit 2 = **chặn ngay tại tool-call**. Đây là lớp nhanh nhất, nhưng chỉ áp khi agent chạy qua một vendor có hook thật.
2. **Pre-commit — L2.** Khi commit, validator chạy lại; vi phạm → chặn commit. Bắt được cái lọt hook (vd sửa bằng editor ngoài agent).
3. **CI — L4.** Trên mọi PR/push, cùng lõi validator chạy trên checkout sạch; vi phạm → fail merge.

## Vì sao CI mới là SÀN THẬT (không phải hook)
Hai lý do, cả hai đều quan trọng:

- **Advisory bị lờ ở vendor non-Claude.** `policy.yaml` sinh ra wiring cho nhiều vendor, nhưng chỉ Claude Code có hook *thực thi* được. Với cursor/codex/kiro/antigravity, luật chỉ là **statement advisory** (gợi ý prose) — agent ở đó có thể lờ. Nên hook KHÔNG phải nơi đảm bảo phổ quát; chỉ **CI** là nơi mọi vendor đều phải qua và không ai bypass được khi merge.
- **Lõi phiên có KHOẢNG TRỐNG CÓ CHỦ ĐỊNH.** Hook session bắt lời gọi tool trực tiếp, nhưng KHÔNG bắt được ghi gián tiếp qua shell: `python -c "open('raw/x','w')"`, `rm raw/...`, `sed -i <script> raw/...`. Bắt mọi indirection ở session là vô vọng (và tốn). Thiết kế cố ý: session chặn ca thường, còn **CI/sandbox là nơi khẳng định sàn đảm bảo** cho ca lách.

Kết luận thực hành: *đừng tin một mình hook*. Hook là tiện-nghi-chặn-sớm; **CI là hợp đồng đảm bảo**. Một luật chưa có ở CI thì coi như chưa được đảm bảo.

## Session vs repo — `enforce_at` lái, không hard-code
Cùng một luật có thể chặn ở phiên nhưng cho qua ở repo, do trường `enforce_at` trong `policy.yaml`, không phải code cứng. Ví dụ `no_write_raw`: **chặn agent** ghi `raw/` ở phiên (raw/ là inbox của con người), nhưng **cho con người commit** `raw/` ở repo. Nhờ vậy "ai được làm gì, ở đâu" là dữ liệu khai báo, đọc một chỗ là hiểu.

## Hệ quả thiết kế
- Thêm/đổi luật → sửa `policy.yaml` (một chỗ) → regen wiring mọi vendor; **CI luôn là chốt chặn cuối** (xem [[ADR-001-policy-as-source-of-truth]]).
- Đánh giá "đủ an toàn chưa" = nhìn ở **CI**, không ở hook.
- Lớp chặn phải là hook/CI, không phải MCP (xem [[ADR-006-blocking-stays-hook-mcp-for-tooling]]).

## Origin
- **Source:** distill từ 2 draft local `250626-harness-poc-vendor-neutral.md` (PoC: lõi 1-CLI + gen-converters + demo 13/test-broad 54 PASS + KNOWN GAPS có chủ đích) và `250626-harness-arch-vs-current.md` (đối chiếu kiến trúc + ma trận quyết định đa-vendor + CI làm sàn). Promote lên wiki vì draft local gitignored — bản chất phải sống sót clone.
- **Liên quan:** [[ADR-001-policy-as-source-of-truth]], [[ADR-006-blocking-stays-hook-mcp-for-tooling]], [[rule-registry]], [[feature-catalog]].
