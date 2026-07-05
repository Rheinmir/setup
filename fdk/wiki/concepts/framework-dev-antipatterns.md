---
type: concept
title: "Framework-dev anti-patterns (bài học dev overstack)"
tags: [anti-pattern, framework-dev, reachability, install, scope, lesson]
timestamp: 2026-07-05
id: framework-dev-antipatterns
---

# Framework-dev anti-patterns

Bài học TÍCH LUỸ khi dev CHÍNH framework overstack (không phải dev tính năng dự án). Mỗi mục:
triệu chứng → vì sao sập → cách chặn. Đọc trước khi sửa engine/hook/install; thêm mục mới khi vấp.

## AP-1 · "Dev-repo-only reachability trap" (⚠️ nghiêm trọng nhất)

**Triệu chứng.** Sửa xong, test XANH trong REPO FRAMEWORK, merge, đóng issue — nhưng thay đổi
**không bao giờ tới người dùng downstream**. "Chạy được ở nhà mình" ≠ "user có".

**Vì sao sập.** Overstack có ÍT NHẤT HAI đường giao hàng KHÁC NHAU, dễ chỉ chạm một:
1. `.template-manifest.json` (sync-template) — file-list kéo về khi cài/update.
2. `harness/poc-vendor-neutral/install.sh` (bootstrap.sh one-liner) — DANH SÁCH RIÊNG, từng KHÔNG
   trùng manifest.
3. **Wiring** — file tới nơi CHƯA đủ: hook phải được nối vào **ROOT `.claude/settings.json`**
   (Claude Code CHỈ đọc root; `llmwiki/.claude/settings.json` KHÔNG được đọc ở downstream).
   Framework repo tự nối tay ở root nên "fire" — downstream thì không.

**Instance thật (GH#51).** PR#42/#45/#49 ship engine wiki-graph + scope vào manifest, test xanh ở
repo framework. Nhưng `bootstrap.sh` (one-liner CHÍNH THỨC) không kéo từ manifest → user chạy curl
chính thức **không có engine, hook không fire**. Engine tồn tại nhưng vô hình với user suốt nhiều PR.

**Cách chặn (bắt buộc cho MỌI thay đổi engine/hook/rule).**
- Sau khi sửa, **bootstrap một dự án TRỐNG bằng đúng one-liner user dùng** (`curl … bootstrap.sh | bash`),
  rồi kiểm 3 điều: (a) file tới nơi; (b) được WIRE để chạy (grep root `.claude/settings.json`);
  (c) **fire thật** end-to-end (đổi input → thấy output). KHÔNG chỉ test trong repo framework.
- Với file mới: thêm vào `.template-manifest.json` VÀ xác nhận đường bootstrap cũng kéo nó.
- Probe nhanh: file có trong manifest? hook có trong ROOT settings? — hai câu hỏi tách biệt, phải hỏi CẢ hai.

## AP-2 · "Framework-only by design ≠ bug"

Không phải cái gì thiếu ở downstream cũng sai. Generator (`build-*.py`) là **framework-only ĐÚNG THIẾT
KẾ** — downstream nhận OUTPUT tĩnh (vd `overstack.html`), không regen. `install.sh` tới user qua
**bootstrap-fetch** (REPO_RAW), không qua manifest — "không trong manifest" ở đây là ĐÚNG. Khi audit
reachability, phân biệt "framework-only cố ý" với "lẽ ra phải tới user mà không tới" (AP-1).

## AP-3 · Scope index NGẦM ĐỊNH (đã fix GH#49)

code-root từng = repo root cứng → mơ hồ khi lồng folder, không thu hẹp/relocate được. Bài học: scope
phải **khai tường minh** (`.overstack.yaml`), đừng để harness đoán theo cwd. Xem [[wiki-core-relations]].

## AP-4 · Ludic-fallacy khi tự-test (đã vấp)

Tự chọn "đề thi" dễ (dự án 3-file đồ chơi) rồi tuyên bố "đã test". Phải: scale thật (≥40-50 quan hệ đủ
loại), ground-truth THẬT (repo chính nó), negative test (input gãy → không đẻ cạnh giả), determinism.
Thêm lăng kính **senior-tester nghi ngờ chính bài test** — nó tìm ra defect (GH#47 dangling wikilink).

## Origin
- Chưng cất từ phiên dev 2026-07-05 (wiki-graph downstream): các instance GH#41/#43/#47/#49/**#51**.
- Bằng chứng: `llmwiki/html/council/council-report-028-seed42.html`, PR#42/#45/#49/#52.
