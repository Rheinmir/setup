---
name: fdk
description: Front-door on-demand cho phát triển framework HOẶC distill/author một skill — SELF-CONTAINED, chạy được ở BẤT KỲ project nào (không phụ thuộc file repo-local). Gọi khi đang sửa chính framework, hoặc đang viết/chưng cất một skill trong phiên của dự án khác. KHÔNG dùng cho dev tính năng dự án thường (đó là phần lớn phiên — ADR-004).
---

# Skill: fdk — Framework Dev Kit (self-contained)

On-demand: KHÔNG auto-bơm đầu phiên (phần lớn phiên là dev dự án khác). Skill này **tự chứa đủ** guidance để chạy ở bất kỳ project nào; mục "bản đầy đủ" ở cuối chỉ áp dụng KHI bạn đang ở trong repo framework.

## Khi nào dùng
- Đang sửa CHÍNH framework (skill / rule / validator / hook / wiki), HOẶC
- Đang distill / author một skill trong phiên của project bất kỳ.

## Pre-flight — chạy trước mọi thay đổi framework/skill
1. **Pull trước khi sửa** — đồng bộ base, đừng làm trên bản cũ.
2. **Biết luật** — nếu repo có harness: xem `rule-registry` / `policy.yaml`. Luật phổ quát luôn đúng: file wiki phải có `## Origin`; không ghi `raw/`; file wiki đúng subfolder (concepts/entities/sources/draft/…); proposal phải đủ cặp `.md`+`.html`.
3. **Đừng dẫm module cũ** — trước khi tạo skill/validator/script/hook mới, **grep tên** xem đã tồn tại chưa; sửa code dùng-chung thì map caller trước (impact-check) rồi safe-change.
4. **Propose trước** — mọi thay đổi → draft kế hoạch, STOP chờ duyệt; đừng code thẳng.
5. **Surgical → verify → ghi vết** — chỉ chạm cái buộc phải chạm; chạy test/drift-test; cập nhật registry/log.

## Distill / author một skill (dùng ở project bất kỳ)
- 1 skill = 1 file `SKILL.md`: frontmatter `name` + `description`, rồi `## When to use`, `## Steps`, `## Rules`.
- `description` phải **đủ trigger** — nêu rõ KHI NÀO gọi (từ khoá, tình huống); đây là thứ router dùng để chọn skill.
- `## Steps` = các bước cụ thể, kiểm chứng được. `## Rules` = ràng buộc + anti-pattern.
- Giữ **self-contained**: đừng trỏ tới file chỉ có ở 1 repo; nếu cần thì ghi "nếu file X có mặt thì…".
- Sau khi viết: thử 1–2 câu mẫu xem skill có được trigger đúng không.

## Inventory — đừng tin số nhớ, đếm LIVE (path tuỳ layout repo)
```bash
ls -d skills/*/ 2>/dev/null | wc -l                                   # số skill
ls harness/validators/*.py 2>/dev/null | wc -l                        # số validator
grep -cE 'id: R' harness/poc-vendor-neutral/policy.yaml 2>/dev/null   # số rule
```

## Nếu đang TRONG repo framework (Rheinmir/setup) — bản đầy đủ
Các file dưới đây CHỈ có trong repo framework, KHÔNG distribute xuống project khác (cố ý — ADR-004). Khi có mặt thì đọc để lấy bản chi tiết:
- `llmwiki/wiki/concepts/fdk.md` — front-door đầy đủ (pre-flight + module map theo loại).
- `fdk/docs/CONTRIBUTING.md` — runbook thêm/sửa **rule harness** (content-check / hook-event / process-gate; số kế tiếp R13).
- `fdk/README.md` + `fdk/tools/` — kit folder (vd `build-cheatsheet.py`).
- `llmwiki/html/*-fdk-docs.html` — bản đọc HTML.

## Rules
- **On-demand only** — không đăng ký hook auto-fire đầu phiên (ADR-004).
- **Self-contained** — phần trên (pre-flight + distill + inventory) đủ chạy ở project khác; mục "bản đầy đủ" chỉ áp dụng KHI các file đó tồn tại. Không bao giờ giả định file repo-local có mặt.
- Đếm số luôn LIVE; không hardcode (anti-drift).
