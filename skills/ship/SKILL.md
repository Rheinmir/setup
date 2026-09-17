---
name: ship
description: "Workflow chốt PUSH/RELEASE/PR/MR — gọi khi user nhắc 'release'/'push'/'ship'/'lên release'/'mở PR'/'tạo MR'. Chạy CHECKLIST điều kiện TRƯỚC khi đẩy: (1) medic --ci (cổng sức khoẻ: luật cắn/drift/docs/code/eval), (2) UAT /fdk-uat qua remote thật nếu diff có năng lực mới (chỉ release/pr/mr, medic --ci không chứng minh được đường curl), (3) git sạch (scratchpad/ephemeral không track), (4) selftest, (5) version x.x.x+1 từ tag gần nhất (chỉ mức release), (6) patch note/PR-body trung thực (Added/Fixed/Removed/Known-limitations, KHÔNG phóng đại). Hỗ trợ 5 mức: 'ship push' = chỉ push không tag; 'ship release' = push + tag vX.Y.Z + release notes; 'ship pr' = push nhánh + gh pr create (GitHub); 'ship mr' = push nhánh + glab mr create (GitLab); 'ship merge' = liệt kê PR/MR ĐẾN của repo theo remote, kéo nhánh về, chạy gate+test, chỉ merge nếu XANH. STOP chờ duyệt trước bước side-effect. Trigger: /ship, 'release', 'push', 'ship', 'mở PR', 'tạo MR', 'ship pr', 'ship mr', 'ship merge', 'gom PR về merge', 'merge PR nếu test xanh', 'chuẩn bị push', 'lên release', 'checklist trước push', 'đủ điều kiện push chưa'."
---

# Skill: ship

> Workflow chốt quanh remote. Chạy checklist điều kiện, DỪNG chờ duyệt trước mọi bước side-effect (push/tag/PR/MR/merge). Năm mức — 4 mức ĐẨY ĐI (outbound) + 1 mức GOM VỀ (inbound): **push** (đủ mọi bước, không tag) · **release** (push + tag `vX.Y.Z` + release notes) · **pr** (push nhánh + mở Pull Request GitHub qua `gh`) · **mr** (push nhánh + mở Merge Request GitLab qua `glab`) · **merge** (liệt kê PR/MR *đến* → kéo nhánh về → gate+test → merge nếu xanh).

## When to use
- User nhắc "release" / "push" / "ship" / "lên release" / "chuẩn bị push" / "đủ điều kiện push chưa" / "mở PR" / "tạo MR".
- Trước khi đẩy code lên remote, cắt một release, hoặc mở PR/MR để review-then-merge.
- Muốn duyệt-rồi-merge các PR/MR đang mở của repo: "gom PR về merge" / "merge PR nếu test xanh" / "ship merge".

## Steps
Mô tả phạm vi thay vì nhớ cờ: **"push"** (chỉ đẩy) · **"release"** (đẩy + tag + notes) · **"pr"** (đẩy nhánh + Pull Request GitHub) · **"mr"** (đẩy nhánh + Merge Request GitLab) · **"merge"** (gom PR/MR đến → test → merge). Mặc định = push.

Mức `push/release/pr/mr` (ĐẨY ĐI) chạy bước 1-8 dưới. Mức `merge` (GOM VỀ) chạy nhánh riêng ở step 8 (đọc mục "Mức merge").

Bước 1, 3-4 áp dụng cho MỌI mức. Bước 2 (UAT) CHỈ `release`/`pr`/`mr`. Bước 5 (version tag) CHỈ mức `release`. Bước 6 đổi tên "sản phẩm viết": `release`→`RELEASE-vX.Y.Z.md`; `pr`/`mr`→ **PR/MR body** (cùng giọng người-dùng, cùng luật Known-limitations). `push` không cần văn bản, chỉ commit msg. Mức `merge` không viết note (chỉ báo cáo kết quả test + quyết định merge/không).

1. **CỔNG SỨC KHOẺ — `medic --ci`** (hoặc `python3 fdk/tools/medic.py --ci`). FAIL → **DỪNG**, in chỗ hở + lệnh sửa; không push khi đỏ. Warn (nợ đã biết) → cho qua nhưng LIỆT KÊ trong patch note.
   - **Rồi `python3 fdk/tools/ci-local.py`** (repo framework) — chạy TRỌN mọi step `run:` của mọi workflow GitHub tại local (L4). medic là L2; có gate CHỈ ở CI (search-index, skill-provenance, retrieval-eval…) — đã cháy 080926: medic xanh, push, CI đỏ 2 job. Đỏ → không push.
   - Gồm probe **`freshinstall`** (E2E): curl-cài overstack vào một dự án TRỐNG cô lập (mktemp ngoài repo) qua working-tree → assert 3 trụ + harness cắn + **orchestration-ready**. Đỏ = đường cài người-mới hỏng → KHÔNG push. Bản đầy đủ curl-github + acceptance live: `bash harness/scripts/fresh-install-smoke.sh --remote`.
2. **UAT gate — `/fdk-uat` (CHỈ mức `release`/`pr`/`mr`, KHÔNG `push` thường):** `medic --ci`/`ci-local` ở bước 1 chỉ cài qua `file://` working-tree — chứng minh "code trong máy lành", KHÔNG chứng minh "người lạ `curl` remote về chạy được" (lớp lỗi GH#77: "doc hứa mà user không nhận được", đo thật 2026-09-17 khi push `6c839d8` không hề qua UAT).
   - **Diff có năng lực MỚI** (skill mới / rule mới cắn được / engine-tool mới) → **BẮT BUỘC** chạy tối thiểu PHA 1 (canary: push nhánh tạm, curl-cài từ raw của chính nhánh đó, kiểm năng lực mới reachable) trước khi sang bước 7. PHA 2 (main-URL smoke, chờ CDN) chạy NGAY sau khi user duyệt merge/tag thật ở bước 8 — không phải lúc đề xuất.
   - **Diff thuần bugfix/refactor nội bộ, không thêm năng lực gì user thấy** → bỏ qua bước này, ghi rõ lý do trong checklist bước 7 ("không có năng lực mới — skip UAT").
   - **Không chắc diff có tính là "năng lực mới" hay không** → hỏi user, đừng tự quyết bỏ qua.
   - Push canary là side-effect thật (đẩy nhánh tạm lên remote) → DỪNG hỏi user trước khi chạy, cùng luật side-effect của skill này. FAIL ở pha nào → dừng ship, báo lỗi cụ thể + xoá canary (không phải "để sau").
3. **Git sạch:** `git status --short`; đảm bảo rác ephemeral (`scratchpad/…`) đã `.gitignore` + `git rm -r --cached` nếu lỡ track. Rà không có file bí mật/tạm lọt vào.
4. **Selftest/kiểm nhanh** các engine đụng tới (vd `council.py selftest`, test liên quan diff).
5. **Version:** `git tag --sort=-v:refname | head -1` → tag gần nhất `vX.Y.Z` → đề xuất **`vX.Y.(Z+1)`** (patch) hoặc minor/major nếu diff xứng — hỏi user nếu không chắc bậc.
6. **Patch note TRUNG THỰC (giọng release-note NGƯỜI DÙNG — kiểu Claude Code):** viết `RELEASE-vX.Y.Z.md`.
   - **Format:** header `Version X.Y.Z:` rồi danh sách bullet PHẲNG, mỗi bullet một dòng một ý.
   - **Giọng:** verb-first mô tả *thay đổi NGƯỜI DÙNG THẤY*, không dump commit/nội-bộ. `Fixed <triệu chứng> — <giờ ra sao>` · `Added <khả năng> — <dùng để làm gì>` · `Removed/Changed …`. Viết từ góc người đọc ("bạn/của bạn"), không SHA, không tên hàm trừ khi user gõ trực tiếp.
   - **Nhóm ngầm theo động từ:** Added/Changed trước, Fixed sau (như release-note Claude). KHÔNG cần tiêu đề nhóm nếu danh sách ngắn.
   - **Nguồn:** đọc `git log <tag-cũ>..HEAD` + scratch-log phiên → DỊCH commit kỹ-thuật sang câu người-dùng-hiểu (1 commit có thể gộp/tách thành bullet theo giá trị cảm nhận, không 1-1).
   - **Known-limitations (BẮT BUỘC nếu có phần nửa vời — điểm HƠN Claude):** proposal draft chưa impl, coverage một phần, warn medic đã biết → khai rõ "đang làm/đã biết". Im lặng = phóng đại (bài học council 2026-07-03).
7. **Hiện checklist + đề xuất lệnh** cho user (commit msg, push, tag/PR/MR, kết quả UAT pha 1 hoặc lý do skip). **DỪNG chờ duyệt.**
8. Sau khi user duyệt: thực thi theo mức. Không tự chạy bước side-effect trước khi có "yes". Nếu bước 2 đã chạy UAT pha 1 (PASS) → merge/tag/push xong thì chạy NGAY UAT pha 2 (main-URL smoke, chờ sentinel CDN) trước khi báo user "xong"; FAIL → gỡ commit khỏi remote theo `/fdk-uat` bước 5.
   - **push:** commit + `git push`.
   - **release:** commit + push + `git tag vX.Y.Z` + tạo release (notes = patch note).
   - **pr (GitHub):** commit + `git push -u origin <nhánh>` + `gh pr create --base <base> --head <nhánh> --title "…" --body-file <PR-body>`. Base mặc định = nhánh chính repo (vd `orca`), hỏi nếu không chắc.
   - **mr (GitLab):** commit + `git push -u origin <nhánh>` + `glab mr create --source-branch <nhánh> --target-branch <base> --title "…" --description "…"` (hoặc `-F <file>`).
   - **Chọn công cụ theo remote:** `git remote get-url origin` chứa `github.com`→`gh`, `gitlab`→`glab`. `ship pr`/`ship mr` ép rõ công cụ; nếu công cụ chưa cài/chưa auth (`gh auth status` / `glab auth status`) thì DỪNG, báo user cài+login (không tự làm).
   - **KHÔNG tự chèn `Closes #N`/`Fixes #N`** vào PR/MR body trừ khi user yêu cầu tường minh — để user giữ quyền đóng issue tay.

### Mức `merge` (GOM VỀ — duyệt-rồi-merge PR/MR đến)
Không viết note/tag. Bỏ qua bước 2, 5-6; thay bằng vòng test-per-request:
1. **Chọn công cụ theo remote** (như trên): `github.com`→`gh`, `gitlab`→`glab`. Chưa auth → DỪNG báo user.
2. **Liệt kê PR/MR đang mở của repo:**
   - GitHub: `gh pr list --json number,title,headRefName,mergeable,isDraft`
   - GitLab: `glab mr list` (hoặc `--output json` nếu bản hỗ trợ).
   Hiện danh sách cho user; nếu user chỉ định số cụ thể thì lọc, không thì hỏi làm hết hay chọn.
3. **Với mỗi PR/MR (một-tại-một, không gộp mù):**
   a. Kéo nhánh về LOCAL sạch: GitHub `gh pr checkout <n>`; GitLab `git fetch origin merge-requests/<n>/head:mr-<n> && git checkout mr-<n>` (hoặc `glab mr checkout <n>`).
   b. **Chạy GATE + TEST** trên nhánh đó: `medic --ci` + selftest/test liên quan diff của PR. Đây là điều kiện merge — KHÔNG merge khi chưa chạy.
   c. **Xanh** → đề xuất lệnh merge, **DỪNG chờ duyệt**, rồi merge: GitHub `gh pr merge <n> --squash` (hoặc --merge/--rebase theo repo); GitLab `glab mr merge <n>`. **Đỏ** → KHÔNG merge; báo cáo chỗ đỏ + để PR nguyên cho tác giả sửa.
   d. Sau merge: quay lại nhánh gốc (`git checkout <nhánh-cũ>`), dọn nhánh tạm.
4. **Báo cáo tổng:** mỗi PR/MR → đã-merge / bỏ-qua-vì-đỏ (kèm lý do) / bỏ-qua-vì-user.

## Rules
- **Không push khi `medic --ci` đỏ** — trừ khi user override tường minh; kể cả override phải ghi lý do vào patch note.
- **Patch note không phóng đại** — Known-limitations là bắt buộc nếu có phần chưa xong.
- **Mức khác nhau ở BƯỚC CUỐI, không ở checklist:** mọi mức đều qua gate sức khoẻ; chỉ khác sản phẩm cuối (tag / release / PR / MR / merge). Đừng tag khi user nói "pr"/"mr"; đừng mở PR khi user chỉ nói "push".
- **`medic --ci` xanh KHÔNG chứng minh đường remote chạy được — đó là việc của `/fdk-uat`.** `release`/`pr`/`mr` có năng lực mới BẮT BUỘC qua UAT pha 1 (canary) trước khi đề xuất bước 7; bỏ qua chỉ khi diff xác nhận không thêm năng lực gì user thấy, và phải ghi lý do. Quyết định đã cháy thật 2026-09-17: mọi push trước đó (kể cả `6c839d8`) chỉ qua `medic --ci`/`ci-local`, chưa từng qua UAT remote thật.
- **Mức `merge` — TEST là điều kiện merge, không phải hình thức:** phải kéo nhánh về + chạy `medic --ci` + test THẬT trước khi merge; đỏ thì tuyệt đối KHÔNG merge, để nguyên cho tác giả. Một-tại-một, không merge gộp mù nhiều PR cùng lúc.
- **PR/MR body cùng luật patch note:** giọng người-dùng, Known-limitations bắt buộc nếu có phần nửa vời. Không SHA/tên hàm nội bộ. KHÔNG `Closes #N` tự động.
- **Side-effect cần "yes":** push/tag/release/PR/MR là hành động khó lùi (outward-facing) → luôn STOP show lệnh, chờ duyệt; không commit/PR-body AI-attribution (theo fdk).
- **Không tự cài/auth `gh`/`glab`:** thiếu công cụ → DỪNG, báo user; đừng đoán host.
- Compose, đừng đẻ lại: dùng `medic` cho sức khoẻ, `git tag` cho version, `gh`/`glab` cho PR/MR — skill này chỉ điều phối checklist.
