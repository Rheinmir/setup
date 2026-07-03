---
name: ship
description: "Workflow chốt PUSH/RELEASE — gọi khi user nhắc 'release'/'push'/'ship'/'lên release'. Chạy CHECKLIST điều kiện TRƯỚC khi push và release: (1) medic --ci (cổng sức khoẻ: luật cắn/drift/docs/code/eval), (2) git sạch (scratchpad/ephemeral không track), (3) selftest, (4) version x.x.x+1 từ tag gần nhất, (5) patch note trung thực (Added/Fixed/Removed/Known-limitations, KHÔNG phóng đại). Hỗ trợ 2 mức: 'ship push' = đủ mọi bước trước, chỉ push không tag; 'ship release' = push + tag vX.Y.Z + release notes. STOP chờ duyệt trước bước side-effect. Trigger: /ship, 'release', 'push', 'ship', 'chuẩn bị push', 'lên release', 'checklist trước push', 'đủ điều kiện push chưa'."
---

# Skill: ship

> Workflow chốt trước khi PUSH/RELEASE. Chạy checklist điều kiện, DỪNG chờ duyệt trước mọi bước side-effect (push/tag). Hai mức: **push** (đủ mọi bước trước, không tag) · **release** (push + tag `vX.Y.Z` + release notes).

## When to use
- User nhắc "release" / "push" / "ship" / "lên release" / "chuẩn bị push" / "đủ điều kiện push chưa".
- Trước khi đẩy code lên remote hoặc cắt một release.

## Steps
Mô tả phạm vi thay vì nhớ cờ: nói **"push"** (chỉ đẩy) hay **"release"** (đẩy + tag + notes). Mặc định = push.

1. **CỔNG SỨC KHOẺ — `medic --ci`** (hoặc `python3 fdk/tools/medic.py --ci`). FAIL → **DỪNG**, in chỗ hở + lệnh sửa; không push khi đỏ. Warn (nợ đã biết) → cho qua nhưng LIỆT KÊ trong patch note.
2. **Git sạch:** `git status --short`; đảm bảo rác ephemeral (`scratchpad/…`) đã `.gitignore` + `git rm -r --cached` nếu lỡ track. Rà không có file bí mật/tạm lọt vào.
3. **Selftest/kiểm nhanh** các engine đụng tới (vd `council.py selftest`, test liên quan diff).
4. **Version:** `git tag --sort=-v:refname | head -1` → tag gần nhất `vX.Y.Z` → đề xuất **`vX.Y.(Z+1)`** (patch) hoặc minor/major nếu diff xứng — hỏi user nếu không chắc bậc.
5. **Patch note TRUNG THỰC:** viết `RELEASE-vX.Y.Z.md` — **Added / Fixed / Removed / Known-limitations**. KHÔNG phóng đại; cái nửa vời (proposal draft, coverage một phần) phải khai rõ "đang làm" (bài học council 2026-07-03: im lặng = phóng đại).
6. **Hiện checklist + đề xuất lệnh** cho user (commit msg, push, tag). **DỪNG chờ duyệt.**
7. Sau khi user duyệt: thực thi. **push:** commit + push. **release:** thêm `git tag vX.Y.Z` + tạo release (notes = patch note). Không tự chạy bước side-effect trước khi có "yes".

## Rules
- **Không push khi `medic --ci` đỏ** — trừ khi user override tường minh; kể cả override phải ghi lý do vào patch note.
- **Patch note không phóng đại** — Known-limitations là bắt buộc nếu có phần chưa xong.
- **push ≠ release:** push-only vẫn phải đủ bước 1-5; chỉ bỏ tag/notes. Đừng tag khi user chỉ nói "push".
- **Side-effect cần "yes":** push/tag/release là hành động khó lùi → luôn STOP show lệnh, chờ duyệt; không commit AI-attribution (theo fdk).
- Compose, đừng đẻ lại: dùng `medic` cho sức khoẻ, `git tag` cho version — skill này chỉ điều phối checklist.
