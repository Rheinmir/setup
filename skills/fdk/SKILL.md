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

## Adapt vào overstack remote — khi đang dev TỪ một dự án khác
Đang dở dự án khác mà muốn chưng cất một skill rồi đẩy vào overstack? `fdk-gate` + `fdk/tools` KHÔNG có ở dự án đó (cố ý — ADR-004), nên kéo **kit** về sandbox rồi submit bằng PR — đừng sửa tay lung tung:

1. **Pull kit** (lần đầu — chạy thẳng từ remote, không cần file local):
   ```bash
   bash <(curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/fdk/tools/fdk-kit.sh) pull
   ```
   → clone overstack vào `.overstack-kit/` (tự thêm vào `.gitignore`, KHÔNG đụng dự án của bạn).
2. **Distill skill TRONG kit:** `cd .overstack-kit && python3 fdk/tools/new-skill.py <tên>` → viết `SKILL.md` → register (mirror + LOOP_MAP + bảng AGENT/CLAUDE + CAPABILITIES — pre-flight #3 + checklist).
3. **Check:** `bash .overstack-kit/fdk/tools/fdk-kit.sh check` — `fdk-gate` đủ 15 bước mới hợp lệ.
4. **Submit (TỰ mở PR):** `bash .overstack-kit/fdk/tools/fdk-kit.sh submit skill/<tên> "<mô tả>"` → gate xanh → push branch → `gh pr create` vào `orca`.

Đang Ở TRONG repo overstack thì bỏ qua bước pull — `fdk-kit check` / `submit` chạy thẳng trên repo.

## Nếu đang TRONG repo framework (Rheinmir/setup) — bản đầy đủ
Các file dưới đây CHỈ có trong repo framework, KHÔNG distribute xuống project khác (cố ý — ADR-004). Khi có mặt thì đọc để lấy bản chi tiết:
- `fdk/wiki/concepts/fdk.md` — front-door đầy đủ (pre-flight + module map theo loại).
- `fdk/docs/CONTRIBUTING.md` — runbook thêm/sửa **rule harness** (content-check / hook-event / process-gate; số kế tiếp R13).
- `fdk/README.md` + `fdk/tools/` — kit folder (vd `build-cheatsheet.py`).
- `llmwiki/html/*-fdk-docs.html` — bản đọc HTML.

## Rules
- **KHÔNG ghi công AI** — commit message / PR / code / wiki KHÔNG được chèn `Co-Authored-By: Claude…`, `Generated with Claude Code`, `🤖`, hay bất kỳ credit/attribution nào cho AI. Author & committer chỉ là danh tính người dùng. Nếu template/tool sinh sẵn trailer ghi công thì cắt bỏ trước khi commit.
- **On-demand only** — không đăng ký hook auto-fire đầu phiên (ADR-004).
- **Self-contained** — phần trên (pre-flight + distill + inventory) đủ chạy ở project khác; mục "bản đầy đủ" chỉ áp dụng KHI các file đó tồn tại. Không bao giờ giả định file repo-local có mặt.
- Đếm số luôn LIVE; không hardcode (anti-drift).
