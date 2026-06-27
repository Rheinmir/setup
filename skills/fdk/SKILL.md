---
name: fdk
description: On-demand front-door để phát triển CHÍNH framework này (FDK) — nạp rule + module map + pre-flight gate. Chỉ gọi khi đang dev framework, KHÔNG dùng khi chỉ dùng framework để dev dự án khác.
---

# Skill: fdk

## When to use
CHỈ khi đang phát triển **chính** framework này — thêm/sửa skill, rule, validator, script, hook, hoặc wiki của framework. KHÔNG dùng khi chỉ dùng framework để dev dự án khác (đó là phần lớn phiên, FDK không liên quan). Đây là lý do FDK là skill gọi **chủ động**, không auto-bơm đầu phiên (xem `ADR-004`).

## Steps
1. **Nạp front-door**: đọc `llmwiki/wiki/concepts/fdk.md` (pre-flight gate + Phần 2 không-miss-rule + Phần 3 không-dẫm-module). Bản đọc HTML đẹp: `llmwiki/html/270626-fdk-docs.html`.
2. **In inventory LIVE** (đừng tin số nhớ — đếm từ đĩa):
   ```bash
   echo "skills:     $(ls -d skills/*/ 2>/dev/null | wc -l)"
   echo "validators: $(ls harness/validators/*.py 2>/dev/null | wc -l)"
   echo "scripts:    $(ls harness/scripts/* 2>/dev/null | wc -l)"
   echo "poc-bin:    $(ls harness/poc-vendor-neutral/bin/* 2>/dev/null | wc -l)"
   echo "hooks:      $(ls llmwiki/.claude/hooks/*.py 2>/dev/null | wc -l)"
   echo "rules:      $(grep -cE 'id: R' harness/poc-vendor-neutral/policy.yaml 2>/dev/null)"
   ```
3. **Nhắc pre-flight** trước khi sửa: pull-gate (R12) → biết rule (`rule-registry`) → check trùng (Phần 3 + `impact-check`) → `propose` → verify + drift-test.
4. **Thêm/sửa rule** → theo `harness/CONTRIBUTING-harness.md` (content-check / hook-event / process-gate; số kế tiếp R13).

## Rules
- **On-demand only** — KHÔNG đăng ký vào hook auto-fire đầu phiên. Phần lớn phiên là dev dự án khác; bơm nội-bộ-framework vào đó là nhiễu (ADR-004: framework-dev context là opt-in).
- Đếm số luôn LIVE từ đĩa; không hardcode (anti-drift).
