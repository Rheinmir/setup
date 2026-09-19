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

## Cách overstack dùng nguồn này (19/09/2026)

User yêu cầu chuẩn hoá toàn bộ skill native theo SWH qua luồng `/fdk`, tách skill kéo từ upstream vào category riêng (vẫn cài xuống downstream), kiểm kỹ trước `/ship`, và đưa toàn bộ việc vào `/orca-graph`. Lát cắt áp dụng ngay: template compact, lint cấu trúc SWH (profile documented), migrate theo lô. Registry, trusted receipt, runtime enforcement (SS-11, SS-16, SS-18 bản đầy đủ) để sau, không claim đã có.

## Origin
- Nguồn thô: `llmwiki/raw/prd/Skill-Design-Standard-SOLID-WHAT-HOW-PRD.md` (user đưa ngày 19/09/2026 qua `/ingest`).
- Concept chính chủ: [[solid-what-how]]; liên quan [[skill-craft]], [[adapt-modes]].
