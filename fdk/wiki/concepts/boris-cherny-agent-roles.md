---
type: concept
title: "Boris Cherny — 5 archetype (Prototyper/Builder/Sweeper/Grower/Maintainer): scope deep-dive"
status: implemented
tags: [boris-cherny, archetypes, roles, product-lifecycle, claude-code, reference]
timestamp: 2026-06-29
---

# Boris Cherny — 5 archetype của người làm sản phẩm (deep-dive scope)

> **Nguồn (verbatim từ Boris Cherny):** khi engineering, product, design, DS… *tan vào* một loại
> vai trò mới, nhìn team Claude Code ông thấy **5 archetype**. Quan trọng: **không gắn job function**
> — ở Anthropic có designer thuộc nhóm 1, có người nhóm 2/3; engineer/PM/DS cũng vậy. **Nhiều người
> span 2 role, đôi khi 3.**

5 archetype xếp theo **vòng đời sản phẩm**: ý-tưởng → production → gọt → vừa-thị-trường → quy-mô.

## 1. Prototyper — *đẻ ý tưởng mới (0→1)*
> "comes up with brand new ideas; churns out many ideas, most of which don't ship"
- **Scope:** khám phá phân kỳ; bắn ra **nhiều** prototype/ý tưởng, **phần lớn không ship** (đó là điểm).
- **Output/dấu hiệu:** nhiều bản nháp vứt đi, tốc độ ý tưởng cao, gắn bó thấp với từng cái.
- **Khúc vòng đời:** sớm nhất, trước khi có gì "thật".
- **Ranh giới (KHÔNG):** không productionize, không bảo trì, không tối ưu PMF.
- **Failure mode:** yêu một ý tưởng → không buông để thử cái mới; hoặc prototype-rồi-bỏ-mãi.
- **↔ overstack:** `/last30days` (quét trend đẻ hướng) + `build-now-adapt-later` (ship phần chắc, nhốt ẩn số để thử nhanh).

## 2. Builder — *biến ý tưởng → production (1→N)*
> "quickly turns a prototype/idea into production-grade product/infra"
- **Scope:** lấy một prototype/ý tưởng đã chọn → **dựng thành sản phẩm/hạ tầng production-grade, NHANH**.
- **Output/dấu hiệu:** thứ chạy thật, đủ chắc để giao; tốc độ ship cao.
- **Khúc vòng đời:** ngay sau khi một ý tưởng được chọn.
- **Ranh giới (KHÔNG):** không lặp PMF vô hạn, không dọn dẹp sâu, không gánh vận hành dài hạn.
- **Failure mode:** ship nhanh nhưng để lại nợ kỹ thuật/UI lộn xộn (việc của Sweeper sau đó).
- **↔ overstack:** chính các feature BNAL (lõi tất định + adapter) + `propose → verify-before-commit`.

## 3. Sweeper — *gọt, đơn giản hoá, GỠ BỚT*
> "cleans up the UI, simplifies the code and system, unships, optimizes performance"
- **Scope:** dọn UI, **đơn giản hoá code + hệ thống**, **unship** (gỡ thứ thừa), tối ưu hiệu năng.
- **Output/dấu hiệu:** diff âm (xoá nhiều), hệ thống nhỏ hơn/nhanh hơn, **không thêm tính năng**.
- **Khúc vòng đời:** sau Builder, định kỳ suốt đời sản phẩm.
- **Ranh giới (KHÔNG):** không thêm feature, không đổi hành vi — chỉ làm gọn + nhanh.
- **Failure mode:** bikeshed / gọt quá đà / xoá nhầm thứ còn dùng.
- **↔ overstack:** `/simplify`, đợt **refactor "gọn 13 chức năng"** (merge flywheel, unship trùng lặp), `docs-curate` (gỡ render phình).

## 4. Grower — *lặp để vừa thị trường (PMF)*
> "takes a product that has been built and iterates on it to improve Product-Market Fit"
- **Scope:** sản phẩm đã dựng xong → **lặp dựa trên dữ liệu dùng thật** để cải thiện product-market fit.
- **Output/dấu hiệu:** thử nghiệm có đo, vòng lặp metric-driven, tăng retention/activation.
- **Khúc vòng đời:** sau khi có sản phẩm chạy, trước/song song scale.
- **Ranh giới (KHÔNG):** không đẻ ý tưởng mới toanh (Prototyper), không gánh hardening dài hạn (Maintainer).
- **Failure mode:** kẹt local-maxima, đuổi **vanity metric**, tối ưu cục bộ hại tổng thể.
- **↔ overstack:** `success-flywheel` (promote cái thắng trên holdout), `wikieval`/`trace-grader` (đo), PM patterns (outcome>output, guardrail metric).

## 5. Maintainer — *giữ hệ trưởng thành khoẻ ở quy mô*
> "owns a mature system to make it secure, reliable, fast, and efficient as it scales"
- **Scope:** **sở hữu** một hệ đã trưởng thành → giữ **an toàn, tin cậy, nhanh, hiệu quả** khi scale.
- **Output/dấu hiệu:** SLO, hardening bảo mật, vá CVE, tối ưu chi phí/perf dưới tải.
- **Khúc vòng đời:** muộn nhất, dài nhất.
- **Ranh giới (KHÔNG):** không chạy theo feature mới — ưu tiên sức khoẻ hệ thống.
- **Failure mode:** cứng nhắc / gatekeeping quá mức / sợ thay đổi.
- **↔ overstack:** `harness-update` (self-maintain), `orca-sec-scans`, dàn rail R1–R14 + "CI là sàn".

## Hai insight cốt lõi (đáng nhớ hơn cả danh sách)
1. **Role ≠ job function.** Eng/PM/Design/DS đang *tan* vào nhau; một designer có thể là Prototyper,
   một engineer có thể là Maintainer. Phân theo **việc bạn giỏi ở khúc nào của vòng đời**, không theo chức danh.
2. **Người span 2–3 archetype.** Hiếm ai thuần một cái. Hữu ích để **tự định vị** (mình mạnh khúc nào)
   và **ghép đội** (phủ đủ 5 khúc idea→prod→gọt→PMF→scale).

## Khác trục với pattern-library hiện có
Kho `llmwiki/patterns/` chia theo **chức năng** (FE/BE/adapter/BA/tester/PM). 5 archetype này là một
**trục KHÁC** — theo **khúc vòng đời**. Hai trục bổ sung nhau: một người = (chức năng) × (archetype),
vd "BE × Sweeper" hay "PM × Grower".

## Origin
- **Source:** transcript Boris Cherny do user cung cấp (ảnh đính kèm + text), goal-set 2026-06-29
  ("tạo file .md của boris cherny về 5 role, deep dive scope"). Định nghĩa từng role trích **verbatim**;
  phần scope/ranh giới/failure-mode/map-overstack là deep-dive thêm.
- **Liên quan:** [[harness-enforcement-floor]]; pattern library `llmwiki/patterns/` (trục chức năng);
  `success-flywheel`/`/simplify`/`harness-update` (đồ overstack khớp Grower/Sweeper/Maintainer).
- **Date:** 2026-06-29
