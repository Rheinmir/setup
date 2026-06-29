---
type: decision
title: "ADR-015: áp 5 archetype Boris Cherny vào template — sweep-gate (nhịp Sweeper) + persona dispatch + phase-map"
status: accepted
tags: [adr, boris-cherny, archetypes, persona, sweep-gate, orca-workflow, build-now-adapt-later]
timestamp: 2026-06-29
---

# ADR-015: áp 5 archetype Boris Cherny vào template

## Status
Accepted (2026-06-29).

## Context
5 archetype của Boris Cherny ([[boris-cherny-agent-roles]] — Prototyper/Builder/Sweeper/Grower/
Maintainer, theo vòng đời) làm thước đo lộ ra một lệch nhịp của overstack: framework **xài Prototyper
+ Builder rất nhiều** (cứ THÊM feature/rule/skill) nhưng **Sweeper + Maintainer chạy theo cảm hứng**.
Bằng chứng: vừa phải làm một đợt "gọn 13 chức năng" *thủ công* (user phải hỏi "merge được không").
User muốn: (1) thể chế hoá nhịp Sweep, (2) định tuyến tool theo archetype, (3) biến 5 archetype thành
**persona dispatch** cho agy/opencode/kiro trong orca-workflow, có **từ khoá** gọi.

## Decision
Ba thứ, đều build-now-adapt-later (lõi tất định now, routing/ngưỡng là adapter `verified:false`):

1. **sweep-gate** (`harness/scripts/sweep-gate.py` + `sweep-gate.config.yaml`) — đếm "đã THÊM bao
   nhiêu kể từ Sweep cuối" (counted_globs vs marker local) và **nhắc gọt** khi vượt `sweep_threshold`
   (như R10 docs-gate nhưng cho nhịp Sweeper). `--mark` chốt mốc sau khi gọt. Advisory, không chặn.
   Dogfood `bnal_config` + `bnal_metrics`.

2. **archetype system** (`harness/scripts/archetype.py` + `archetypes.config.yaml` + 5 file posture
   `llmwiki/personas/<archetype>.md`) phục vụ CẢ:
   - **#2 phase-map:** `--phase <archetype>` → tool overstack hợp phase (Prototyper→last30days/BNAL,
     Builder→propose/verify, Sweeper→simplify/docs-curate/sweep-gate, Grower→success-flywheel/wikieval,
     Maintainer→harness-update/orca-sec-scans).
   - **#3 persona dispatch:** mỗi archetype có **từ khoá** (`/proto /build /sweep /grow /maintain`).
     `archetype.py --get /<kw>` → in CLI gợi ý + **PREAMBLE posture** để orca-workflow **inject vào
     `<task>`** trước khi dispatch cho agy/opencode/kiro (agent vào đúng vai; vd Sweeper cấm thêm feature).
   - **Adapter (`verified:false`):** CLI/model nào HỢP archetype nào là phán đoán (ADAPT-CHECKLIST:
     dispatch thử + orca-eval đo rồi chốt). Keyword/tools/posture thì tất định.

3. **Wire:** orca-workflow bước dispatch nêu cơ chế persona-keyword; 2 self-test mới vào fdk-gate
   (19 chức năng BNAL).

## Consequences
- (+) Nhịp **Sweeper** được thể chế hoá → chữa bệnh **accretion** của overstack (cái lens vừa chẩn).
- (+) 5 archetype **gọi được bằng từ khoá** + inject đúng posture cho CLI agent → dispatch có chủ đích,
   không phải task trần.
- (+) phase-map cho agent/user biết "đang ở phase nào → dùng đồ nào" (route tất định).
- (+) Trục archetype (vòng đời) **bổ sung** trục chức năng của pattern-library (một người = chức năng × archetype).
- (−) Routing CLI↔archetype còn `verified:false` (đoán) — phải đo bằng orca-eval rồi chốt.
- (−) Thêm 2 script + 2 config + 5 posture để bảo trì (chính nó cũng là accretion — sweep-gate sẽ nhắc).

## Origin
- **Source:** goal-set 2026-06-29 ("làm cả 1 và 2 + biến 5 agent thành persona của agy/opencode/kiro
  trong orca-workflow, cần từ khoá gọi"). Nối từ [[boris-cherny-agent-roles]].
- **Liên quan:** `scoped-hooks` (guard theo component — họ hàng với persona theo archetype),
  [[ADR-003-skill-as-single-source-of-truth]] (orca-workflow delegate), `success-flywheel`/`sweep-gate`.
- **Date:** 2026-06-29
