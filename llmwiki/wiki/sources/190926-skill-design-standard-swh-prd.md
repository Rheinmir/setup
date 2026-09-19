---
type: source
title: "Skill Design Standard PRD v1.0 — SOLID WHAT/HOW (SWH): chuẩn bắt buộc cho skill, 14 blocking rule, 24 ticket"
status: ingested
tags: [prd, skills, swh, solid, standard, lint, conformance]
timestamp: 2026-09-19
id: 190926-skill-design-standard-swh-prd
relations:
  - {rel: informs, to: solid-what-how}
  - {rel: informs, to: skill-craft}
  - {rel: raw, path: llmwiki/raw/prd/Skill-Design-Standard-SOLID-WHAT-HOW-PRD.md}
---

# Skill Design Standard PRD v1.0 — SOLID WHAT/HOW

## Tóm tắt

PRD 1.181 dòng (21 phần) đặt chuẩn `solid-what-how/1` (SWH): mọi skill được tạo mới hoặc chuẩn hoá phải tách **WHAT** (purpose, mental model, input/output contract, rules có ID, capabilities trừu tượng, failure boundaries) khỏi **HOW** (preflight, main path có step ID và exit, branches có guard và rejoin, retry/stop có trần, validation, ví dụ positive và boundary). Vấn đề nó giải: skill trộn mục đích, luật, công cụ và các bước trong một khối Markdown, nên agent khó chọn đúng, dễ bỏ nhánh, và người mới phải đoán. Chi tiết chuẩn ở trang chính chủ [[solid-what-how]].

## Các điểm chính theo mục

| Mục PRD | Nội dung | Ghi chú áp dụng |
|---|---|---|
| §1 | Chuẩn là điều kiện nghiệm thu; legacy chỉ conformant sau migration có bằng chứng; `legacy_unassessed` không phải miễn trừ | Phạm vi migrate phải có danh sách package cụ thể |
| §3 | Ánh xạ SOLID vào skill; S không nghĩa là một bước; L gồm cả quyền và failure | Là thiết kế đề xuất của PRD |
| §4, §9, §10 | WHAT/HOW bắt buộc; compact (1 file) và expanded (references/ có routing); template compact có `metadata.design-standard` | Không tạo file/thư mục rỗng cho đủ bộ |
| §6 | Ba loại bước deterministic / judgment / effect; guard true/false/**unknown**, unknown ≠ false | |
| §7 | Bốn loại nhánh: conditional_required, user_optional, capability_optional, recovery | "Xét nhánh" không bắt bịa nhánh |
| §11–12 | Skill mẫu `prd-to-tickets` (W01–W10, B01–B03, rule PT-01…08) và hàm `select_delivery` thuần có 8 test vector | Chưa build trong overstack |
| §13 | Blocking rules SWH-001…014; linter trả `review_required` khi không chứng minh được | Structural lint không thay behavioral validation |
| §14 | Documented vs enforced conformance; lifecycle draft → active; versioning theo package hash | Host chỉ đọc Markdown thì chỉ được claim documented |
| §15 | Quy trình migrate legacy: baseline hành vi trước, tách câu vào WHAT/HOW, không đổi scope, có rollback | Áp cho đợt migrate skill native |
| §16–19 | 24 yêu cầu SS-R01…24, 24 ticket SS-01…24, 36 scenario EV-01…36, ước lượng 62 ngày công | Backlog dựng năng lực ở quy mô team, không phải điều kiện để viết một skill đúng chuẩn |

## Bản v1.1 — Reuse Layer (§22–29)

Bản `raw/prd/Skill-Design-Standard-SOLID-WHAT-HOW-PRD (1).md` (1.741 dòng) giữ nguyên §1–21 và thêm lớp **tái sử dụng pattern/template theo contract**, mục tiêu là chi phí biên tạo skill kế tiếp giảm dần. PRD nói rõ đây là mục tiêu cần đo, không phải quy luật bảo đảm. Chi tiết cơ chế ở [[solid-what-how]] mục Reuse Layer.

| Mục | Nội dung | Ghi chú áp dụng |
|---|---|---|
| §22 | Chính sách: mỗi lần tạo/chuẩn hoá skill phải ghi `reuse_decision` (reuse · compose · scratch · catalog_unavailable); công thức `C_total`, AC (bình quân) ≠ MC (biên); ví dụ hòa vốn 3 lần (4 lần khi tính maintenance) là giả định | Chưa có catalog thì ghi `catalog_unavailable`, không chặn việc |
| §23 | Sáu loại tài sản: pattern · template · component · test pack · recipe · skill instance; kế thừa bằng composition + delta, độ sâu tối đa 3 cạnh; frozen core + typed slots | Không dùng cờ `skip_validation` để "mở rộng" |
| §24 | Catalog manifest JSON trong repo (không cần vector DB); vòng đời candidate → reviewed → validated → active → deprecated → retired, có quarantined; lọc quyền/contract TRƯỚC khi xếp hạng | Seed mới chỉ được nhãn `limited_evidence` |
| §25 | Luồng R01–R09 (intake → discover → decide → resolve → instantiate → specialize → validate → commit → observe); module Catalog/Resolver/Composer/Validator/Registry/Feedback/Upgrader | Là contract nội bộ đề xuất, chưa có CLI thật |
| §26–27 | Seed P01 evidence→artifact, P02 verified external effect, P03 pure transform; template T01, T02; metrics tách authoring/runtime, pilot tối thiểu 10 episode | Tuyên bố "tiết kiệm" cần baseline, thiếu thì `benefit_unproven` |
| §28–29 | 12 ticket RU-01…12 (25 ngày công, tổng 87); 4 mức rollout manual seed → local MVP → managed → measured; 16 ca demo RE-01…16 | Lát cắt khởi đầu hợp lý là mức manual seed / local MVP |

## Cách overstack dùng nguồn này (19/09/2026)

User yêu cầu chuẩn hoá toàn bộ skill native theo SWH qua luồng `/fdk`, tách skill kéo từ upstream vào category riêng (vẫn cài xuống downstream), kiểm kỹ trước `/ship`, và đưa toàn bộ việc vào `/orca-graph`. Lát cắt áp dụng ngay: template compact, lint cấu trúc SWH (profile documented), migrate theo lô. Registry, trusted receipt, runtime enforcement (SS-11, SS-16, SS-18 bản đầy đủ) để sau, không claim đã có.

## Origin
- Nguồn thô: `llmwiki/raw/prd/Skill-Design-Standard-SOLID-WHAT-HOW-PRD.md` (v1.0) và `llmwiki/raw/prd/Skill-Design-Standard-SOLID-WHAT-HOW-PRD (1).md` (v1.1, cùng ngày), user đưa ngày 19/09/2026 qua `/ingest`.
- Concept chính chủ: [[solid-what-how]]; liên quan [[skill-craft]], [[adapt-modes]].
