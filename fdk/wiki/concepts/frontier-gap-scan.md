---
type: concept
title: "frontier-gap-scan — quét đối thủ hàng tuần để overstack là frontier TOÀN DIỆN, không chỉ vài mặt"
status: living
tags: [strategy, competitive, frontier, scout, weekly, harness-engineering, evolution]
timestamp: 2026-07-03
id: frontier-gap-scan
relations:
  - {rel: depends-on, to: fdk-dev-strategy}
  - {rel: depends-on, to: feature-catalog}
  - {rel: derives-from, path: llmwiki/html/overstack-vs-world-30d.html}
---

# frontier-gap-scan

**Kỷ luật quét đối thủ định kỳ (hàng tuần) để đối chiếu overstack với biên giới thế giới agent-framework, biến MỖI khoảng cách thành issue có chủ, và tiến hoá liên tục — mục tiêu là frontier TOÀN DIỆN chứ không mạnh vài mặt.** Không ngủ trên chiến thắng: ngay cả trục đang thắng cũng phải tái-kiểm mỗi kỳ vì biên giới dịch chuyển hàng tuần.

## Vì sao tồn tại (Foundation)
- **Bài toán:** model đang hội tụ; khác biệt thật nằm ở lớp deterministic quanh model ("harness engineering" — ngành mới được đặt tên 2026 bởi field-report OpenAI/Anthropic/LangChain). overstack đi ĐÚNG hướng này nhưng thế giới chạy nhanh ở vài trục ta còn yếu.
- **Vì sao cần kỷ luật định kỳ:** một lần rà (03/07/2026) chỉ chụp một khung hình. Biên giới đổi hàng tuần (arXiv + release + marketplace). Không quét lại ⇒ tưởng thắng mà đã tụt. Cần vòng lặp, không phải sự kiện.

## Ảnh chụp 03/07/2026 — overstack ở đâu (baseline)
Nguồn: [[overstack-vs-world-30d]] (report HTML) — 5 truy vấn WebSearch + đối chiếu `fdk/CAPABILITIES.md`.

**Đang ĐÚNG & trước (giữ + tái-kiểm):**
- Harness-first: 17 rule cắn cứng · `medic` cổng cuối · `loop-runner` propose→verify→revise → khớp GUARDRAILS.md / Self-Harness.
- Wiki như bộ nhớ thể chế (institutional knowledge primitive — arXiv 2603.14805): Origin + ADR + wikilink + ingest.
- `failure-flywheel` = phôi thai self-harness (weakness-mining → guardrail).

**Đang THUA (→ issue P1):**
1. **Memory** — thế giới chuẩn hoá 4 tầng (working/episodic/semantic/procedural) + vector + temporal graph (Letta/Mem0/Zep, có benchmark). overstack ~1.5/4 tầng. → issue `030726-memory-episodic-vector`.
2. **Self-evolving skills** — CoEvoSkills/SkillForge sinh + tiến hoá skill qua verify vòng lặp. overstack viết tay. → issue `030726-self-evolving-skills`.
3. **Observability/eval runtime** — Galileo Agent Control / future-agi: tracing·simulation·guardrail lúc chạy. overstack chỉ eval tĩnh. → issue `030726-observability-runtime`.

**CHỚM (→ issue P2):**
4. **Deterministic orchestration scale** — DAG + file-bus, hàng trăm subagent song song (Claude Code dynamic workflows). orca nhỏ hơn. → issue `030726-orchestration-scale`.
5. **Skill-resolve ambiguity + supply-chain** — SkillResolve-Bench (nhập nhằng cùng-năng-lực) + paper supply-chain security. → issue `030726-skill-resolve-supplychain` **ĐÃ GIẢI (GH#13, 2026-07-04)**: `new-skill` cảnh báo trùng-năng-lực bằng BM25 khi scaffold; golden `skill-resolve-eval` (18 case, hit@1 18/18) gắn CI chặn regress; skill+tool `skill-provenance` ghi nguồn+sha256 khi cài skill ngoài, `check --ci` chặn skill lạ/bị-sửa. Trục này chuyển **Chớm → có cơ chế**; tái-kiểm kỳ sau.

**Positioning (không phải gap):** quy mô marketplace (18k–1.2M skill ngoài vs 71 nội bộ) là lựa chọn chất-lượng-hẹp-private, không phải nợ cần trả.

## Phương pháp scout (chạy lại hàng tuần — travel-được)
Runbook lặp; phần tự-động-hoá lịch là machine-local (xem "Tự động hoá").
1. **Quét** 5 truy vấn WebSearch cố định (giữ so-sánh-được qua các kỳ): (a) Claude Code / agent framework updates <tháng>; (b) memory + context engineering; (c) self-improving agents + harness eval; (d) skills marketplace + supply-chain; (e) 1 truy vấn tự-chọn theo tin nóng.
2. **Đối chiếu** kết quả với `fdk/CAPABILITIES.md` theo 8 trục ở bảng report — chấm verdict Ngang/Chớm/Thua cho từng trục.
3. **Diff với kỳ trước:** trục nào tụt hạng? xuất hiện trục mới nào? → đây là tín hiệu quan trọng nhất.
4. **Raise:** mỗi trục Thua/Chớm MỚI hoặc xấu đi → `/raise-issue` (ledger + mirror GH). Trục đã có issue → cập nhật bằng chứng, không raise trùng (R7-f query trước).
5. **Report:** cập nhật/append vào `llmwiki/html/overstack-vs-world-30d.html` (hoặc bản mới theo tuần) + ghi 1 dòng ledger.

## Tự động hoá (machine-local — không đi theo repo, ADR-004)
- Lịch tuần dựng bằng `/schedule` (cloud routine cron) hoặc cron cá nhân, chạy runbook trên. Vì cron là máy-local, KHÔNG commit vào repo — chỉ concept + runbook này travel.
- Đầu ra mỗi kỳ: issue mới (nếu có) + report cập nhật. Con người duyệt ở bước raise (giữ người-trong-vòng-lặp như `failure-flywheel`).

## Tiêu chí "frontier toàn diện" (định nghĩa thắng)
Không trục nào ở verdict **Thua** quá 2 kỳ liên tiếp mà không có issue đang chạy. Mọi trục hoặc **Ngang/Hơn**, hoặc **Chớm + issue in-progress**. Đạt được ⇒ tái-định-nghĩa biên giới (thêm trục mới), không dừng.

## Notes
- [[fdk-dev-strategy]] — Mongol pattern cho dev framework (scout là ứng dụng của "trinh sát trước khi đánh").
- [[feature-catalog]] — bản đồ năng lực dùng làm cột "overstack" khi đối chiếu.
- [[overstack-vs-world-30d]] — report baseline.

## Origin
- **Source:** `llmwiki/html/overstack-vs-world-30d.html` (report /last30days chế độ web-research, 2026-07-03)
- **Raise bởi:** phiên hỏi "framework khác gì / thua gì với thế giới 30 ngày qua" → user chốt mục tiêu frontier-toàn-diện + quét hàng tuần ("cùng tiến hoá thực sự").
- **Date:** 2026-07-03
