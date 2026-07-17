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

## AP-5 · "Split-brain enablement" — tín hiệu bật tính năng ở code-path KHÁC path thực chạy (GH#70)

**Triệu chứng.** Tính năng có đủ engine + hook nhưng **không bao giờ kích hoạt** ở downstream; không lỗi,
không cảnh báo — chỉ im lặng tắt.

**Vì sao sập.** Cờ bật (`OVERSTACK_WIKIGRAPH=1`) được set ở **section 4b per-repo** của
`install-harness.sh`, NHƯNG đường cài thật downstream là `bootstrap.sh → install.sh --full →
install-harness.sh --global`, mà nhánh `--global` **`exit 0` TRƯỚC section 4b**. Enablement sống ở một
nhánh; nhánh thực thi là nhánh khác → cờ không bao giờ được set → `stop.py` `wikigraph_on=False` →
graph tự lệch (đúng #70). Migration v4 (GH#63) dời engine sang global nhưng **tín hiệu bật không dời theo**.

**Cách chặn.**
- **Khoá enablement vào tín hiệu ĐÃ gate code-path đó**, đừng đẻ cờ song song. Ở đây: hook global chỉ
  fire khi có `llmwiki/.harness-stamp` → dùng CHÍNH stamp làm điều kiện bật wiki-graph. Một tín hiệu, một
  sự thật (Meadows: sửa luồng thông tin, không thêm tham số).
- Sau khi tách một install-path mới (per-repo ↔ global), liệt kê MỌI thứ path cũ set (env, wiring, seed) và
  hỏi "path mới còn set không?". Cái gì `exit` sớm bỏ qua thì phải mang lên trước điểm exit.

## AP-6 · "Test tự chống đỡ tín hiệu mà production thiếu" (best-practice cho bài test — GH#70)

**Triệu chứng.** Test XANH bền vững nhưng production hỏng ở đúng thứ test tưởng đã phủ.

**Vì sao sập.** `wiki-graph-user-reachability-test.sh` drive `stop.regen_docs` với
`OVERSTACK_WIKIGRAPH=1` **set tay trong test env**. Chính cờ đó là thứ install path downstream KHÔNG set.
Test dựng sẵn tiền-đề mà thực tế không có → xanh giả, che AP-5 suốt nhiều PR.

**Best-practice rút ra (áp cho mọi test downstream/install của dự án).**
- **Fixture phải TÁI HIỆN đúng môi trường đích, không mồi thêm tín hiệu.** Chỉ set những gì install path
  thật tạo ra (ở đây: `.harness-stamp`); đừng export env/biến mà chỉ có trong đầu người viết test.
- **Test bất-biến, không test giá trị hiện tại.** Guard đúng = "repo đã bootstrap ⇒ auto-draw", bất kể
  cơ chế bật là gì — nên khi cơ chế đổi (env→stamp) test vẫn đo đúng ý định.
- **Kèm negative-control cho ĐIỀU KIỆN bật, không chỉ cho engine.** Đã thêm STAMP-control: không stamp +
  không env ⇒ KHÔNG vẽ — chốt cả hai chiều (bật đúng lúc, tắt đúng lúc).
- Liên hệ [[AP-4]] (ludic-fallacy): cả hai là "test dễ hơn thực tế"; AP-4 dễ ở *input*, AP-6 dễ ở *môi trường*.

## Origin
- Chưng cất từ phiên dev 2026-07-05 (wiki-graph downstream): các instance GH#41/#43/#47/#49/**#51**.
- Bổ sung 2026-07-08 (GH#70): AP-5 split-brain enablement + AP-6 test tự-chống-đỡ tín hiệu.
- Bằng chứng: `llmwiki/html/council/council-report-028-seed42.html`, PR#42/#45/#49/#52; fix GH#70 ở
  `stop.py` + `wiki-graph-user-reachability-test.sh` (bỏ `OVERSTACK_WIKIGRAPH=1` mồi + thêm STAMP-control).
