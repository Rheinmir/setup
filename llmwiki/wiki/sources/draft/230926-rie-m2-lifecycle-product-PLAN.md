---
type: draft
title: "PLAN — Reprise Intent Engine, phần 2: vòng đời graph và chất lượng sản phẩm (RI-14…RI-24)"
status: proposed
tags: [plan, reprise, intent-engine, orca-graph]
timestamp: 2026-09-23
---

# PLAN 230926 — Reprise Intent Engine, phần 2: vòng đời graph và chất lượng sản phẩm (RI-14…RI-24)

Nguồn: [[230926-reprise-intent-engine-prd]] (raw `llmwiki/raw/prd/Reprise-Intent-Engine-Product-Grade-PRD.md`). Backlog 24 ticket vượt trần 20 node/graph của orca-graph nên tách HAI graph anh em: `230926-rie-m1-clarify-core` (RI-01…RI-13, mốc M1+M2) và `230926-rie-m2-lifecycle-product` (RI-14…RI-24, mốc M3+M4). Graph này là phần 2.

## Global constraints
- Repo đích: `/Users/giatran/orca/reprise-intent-engine` (repo MỚI, Task 1 của graph 1 tạo). Mọi đường dẫn trong **Files:** tính từ gốc repo đó; PRD là nguồn đặc tả — mỗi task đọc đúng mục §16 của ticket mình.
- Bất biến §3.1 là luật cứng cho mọi task: không có nguồn thì không thành requirement; draft chưa niêm phong không được coi là sealed brief; actor/grant không tự khai; mọi hiệu ứng ra ngoài phải có receipt.
- Model chỉ được dùng ở các điểm PRD cho phép (§6.1); output của model là *untrusted proposal*, phải qua schema + kiểm nguồn trước khi vào brief.
- Trần mặc định §14.2: 1 job/case, tối đa 6 model call một episode, ≤ 2 vòng hỏi chủ động, ≤ 3 câu/vòng, ≤ 5 source read, context ≤ 12.000 token, deadline 5 phút máy chạy; host cap nhỏ hơn luôn thắng.
- Test kiểm BẤT BIẾN và ca gây mất/sai dữ liệu, không mirror từng dòng code. Mỗi task có đúng file `tests/qc/qc-NN.test.ts` theo kịch bản QA ở PRD §17.3; tên `it(...)` bắt đầu bằng `QC-NN`.
- Không mở port public, không egress chưa duyệt, không bí mật trong URL/log.
- Không AI-attribution trong commit.

### Task 1: RI-14 — RGE Handoff, idempotency và reconcile
**Kind:** integration
**Thoả:** RI-R14 · QA-14 · PRD §16 RI-14 · effort 3 ngày
**Depends:** 230926-rie-m1-clarify-core/t3 (data), 230926-rie-m1-clarify-core/t4 (data), 230926-rie-m1-clarify-core/t13 (data)
**Files:**
- Tạo: `handoff/`
- Tạo: `tests/qc/qc-14.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: end-to-end adapter với fake runtime fault harness và real conformance + `tests/qc/qc-14.test.ts` xanh
**Bước:** (1) map brief subset sang RGE intake contract; (2) same case liên kết đúng root; (3) unique handoff identity/digest; (4) query/retry pending receipt; (5) recheck epochs/revisions; (6) project accepted/started/completed từ đúng receipts.
**AC:** mất response sau accept chỉ có một run; key reused khác digest conflict; offline chỉ pending/export; scope không sẵn sàng bị RGE reject dù report trước pass.
**QA:** QA-14, QA-30/35.
**Code:**
```ts
// tests/qc/qc-14.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-14)
import { describe, it, expect } from 'vitest'

describe('QC-14 — RGE Handoff, idempotency và reconcile', () => {
  it('mất response sau accept chỉ có một run', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module handoff/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-14`

### Task 2: RI-15 — Semantic change và impact proposal
**Kind:** integration
**Thoả:** RI-R15 · QA-15 · PRD §16 RI-15 · effort 3 ngày
**Depends:** 230926-rie-m1-clarify-core/t9 (data), 230926-rie-m1-clarify-core/t12 (data), 230926-rie-m1-clarify-core/t13 (data), Task 1 (data)
**Files:**
- Tạo: `changes/`
- Tạo: `tests/qc/qc-15.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: change proposal workflow và history UI contract + `tests/qc/qc-15.test.ts` xanh
**Bước:** (1) diff structured IDs/constraints/AC; (2) classify cosmetic/detail/contract/root/unknown; (3) create change alert và expected base refs; (4) map affected artifacts qua RGE; (5) track apply/hold/fence receipts, không mutate scheduler; (6) present reuse/invalidation/unknown.
**AC:** tenant change không là cosmetic; stale apply conflict; in-flight effect unknown hiện reconcile; goal cũ không được âm thầm thay vào tests để pass.
**QA:** QA-15, QA-28/35.
**Code:**
```ts
// tests/qc/qc-15.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-15)
import { describe, it, expect } from 'vitest'

describe('QC-15 — Semantic change và impact proposal', () => {
  it('tenant change không là cosmetic', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module changes/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-15`

### Task 3: RI-16 — Child clarification coalescing và resolution fan-out
**Kind:** build
**Thoả:** RI-R16 · QA-16 · PRD §16 RI-16 · effort 3 ngày
**Depends:** 230926-rie-m1-clarify-core/t8 (data), 230926-rie-m1-clarify-core/t10 (data), Task 1 (data), Task 2 (data)
**Files:**
- Tạo: `handoff/discovery`
- Tạo: `changes/requirement-map`
- Tạo: `tests/qc/qc-16.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: aggregate clarification inbox nối RGE + `tests/qc/qc-16.test.ts` xanh
**Bước:** (1) ClarificationRequest schema từ child; (2) dedup cùng decision/scope/revision; (3) attach blocked milestone refs; (4) answer mapping tới subscribers còn hợp lệ; (5) scope-filter context trả xuống; (6) distinguish technical investigation có thể làm và user decision.
**AC:** ba children hỏi cùng tenant decision chỉ tạo một user question; answer chỉ unlock đúng revision/dependencies; private context của sibling không bị fan-out.
**QA:** QA-16, QA-25/35.
**Code:**
```ts
// tests/qc/qc-16.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-16)
import { describe, it, expect } from 'vitest'

describe('QC-16 — Child clarification coalescing và resolution fan-out', () => {
  it('ba children hỏi cùng tenant decision chỉ tạo một user question', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module handoff/discovery
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-16`

### Task 4: RI-17 — SWH profiles, template pins và reuse fallback
**Kind:** build
**Thoả:** RI-R17 · QA-17 · PRD §16 RI-17 · effort 2 ngày
**Depends:** 230926-rie-m1-clarify-core/t1 (data), 230926-rie-m1-clarify-core/t7 (data), 230926-rie-m1-clarify-core/t10 (data), 230926-rie-m1-clarify-core/t12 (data), 230926-rie-m1-clarify-core/t13 (data)
**Files:**
- Tạo: `src/ri17/`
- Tạo: `tests/qc/qc-17.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: profile definitions + conformance reports, chưa tự publish + `tests/qc/qc-17.test.ts` xanh
**Bước:** (1) tạo bốn template families §11.3 theo WHAT/HOW; (2) typed extension slots và contraindications; (3) resolve access/compatibility/lifecycle trước rank; (4) pin version/closure; (5) core fallback nếu không fit; (6) fixtures cho false inheritance.
**AC:** task mới không kế thừa tenant/grants project cũ; template update không hot-swap brief; incompatible/retired asset không admission mới.
**QA:** QA-17, QA-26/36.
**Code:**
```ts
// tests/qc/qc-17.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-17)
import { describe, it, expect } from 'vitest'

describe('QC-17 — SWH profiles, template pins và reuse fallback', () => {
  it('task mới không kế thừa tenant/grants project cũ', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module src/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-17`

### Task 5: RI-18 — API commands, conflicts và late reply routing
**Kind:** build
**Thoả:** RI-R18 · QA-18 · PRD §16 RI-18 · effort 2 ngày
**Depends:** 230926-rie-m1-clarify-core/t2 (data), 230926-rie-m1-clarify-core/t3 (data), 230926-rie-m1-clarify-core/t10 (data), 230926-rie-m1-clarify-core/t13 (data), Task 1 (data), Task 2 (data)
**Files:**
- Tạo: `api/`
- Tạo: `tests/qc/qc-18.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: API contracts và examples cho frontend + `tests/qc/qc-18.test.ts` xanh
**Bước:** (1) endpoints §13.1; (2) authorization + expected revision; (3) late batch answer binding; (4) idempotent error mapping; (5) event cursor reconnect; (6) reject direct writes tới ready/authorized/applied fields.
**AC:** concurrent tab không mất raw reply; late answer không gán vào câu hỏi mới chỉ vì cùng vị trí; unauthorized actor không đọc case khác.
**QA:** QA-18, QA-25/28/32.
**Code:**
```ts
// tests/qc/qc-18.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-18)
import { describe, it, expect } from 'vitest'

describe('QC-18 — API commands, conflicts và late reply routing', () => {
  it('concurrent tab không mất raw reply', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module src/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-18`

### Task 6: RI-19 — UI intake, questions, brief diff và progress
**Kind:** design
**Thoả:** RI-R19 · QA-19 · PRD §16 RI-19 · effort 3 ngày
**Depends:** 230926-rie-m1-clarify-core/t11 (data), Task 3 (data), Task 5 (data)
**Files:**
- Tạo: `ui/`
- Tạo: `tests/qc/qc-19.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: usable intake screen nối API + `tests/qc/qc-19.test.ts` xanh
**Bước:** (1) bốn vùng §13.3; (2) render badges/source explanations; (3) partial answers/free text/không biết; (4) actual admission/progress state; (5) diff + unresolved panel; (6) keyboard/mobile/Unicode và reconnect.
**AC:** user sửa cách hiểu mà không mất draft; pending không hiển thị running; màu không là tín hiệu duy nhất; không có blanket approval gộp effects.
**QA:** QA-19, QA-32/33.
**Code:**
```ts
// tests/qc/qc-19.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-19)
import { describe, it, expect } from 'vitest'

describe('QC-19 — UI intake, questions, brief diff và progress', () => {
  it('user sửa cách hiểu mà không mất draft', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module src/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-19`

### Task 7: RI-20 — Stop controller, fallback và invalidation
**Kind:** build
**Thoả:** RI-R20 · QA-20 · PRD §16 RI-20 · effort 2 ngày
**Depends:** 230926-rie-m1-clarify-core/t4 (data), 230926-rie-m1-clarify-core/t5 (data), 230926-rie-m1-clarify-core/t10 (data), 230926-rie-m1-clarify-core/t12 (data), Task 1 (data), Task 2 (data)
**Files:**
- Tạo: `stop/`
- Tạo: `tests/qc/qc-20.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: error/stop contracts, operator commands + `tests/qc/qc-20.test.ts` xanh
**Bước:** (1) stop order §14.3; (2) no-progress và max rounds/calls; (3) durable wait/resume; (4) source revoke invalidation và cache purge theo scope; (5) provider/runtime unavailable fallback; (6) cancel receipt handling.
**AC:** wait không giữ worker/model poll; cancel/revoke chặn new admission; no source/model không fake completeness; intake pause không giả mọi external effects đã hủy.
**QA:** QA-20, QA-27/29/30/33.
**Code:**
```ts
// tests/qc/qc-20.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-20)
import { describe, it, expect } from 'vitest'

describe('QC-20 — Stop controller, fallback và invalidation', () => {
  it('wait không giữ worker/model poll', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module src/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-20`

### Task 8: RI-21 — Golden semantic evaluation và grader rules
**Kind:** test
**Thoả:** RI-R21 · QA-21 · PRD §16 RI-21 · effort 3 ngày
**Depends:** 230926-rie-m1-clarify-core/t7 (data), 230926-rie-m1-clarify-core/t8 (data), 230926-rie-m1-clarify-core/t10 (data), 230926-rie-m1-clarify-core/t12 (data), 230926-rie-m1-clarify-core/t13 (data), Task 4 (data)
**Files:**
- Tạo: `tests/evaluation/`
- Tạo: `tests/qc/qc-21.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: evaluation runner/report + development/selection/holdout split + `tests/qc/qc-21.test.ts` xanh
**Bước:** (1) 12 task families × 3 variants ở §17; (2) reference obligations và acceptable ambiguity outcomes, không exact prose; (3) deterministic validators cho contracts/rights; (4) human/model rubric cho intent fidelity, question utility và source support; (5) freeze splits/versions và record disagreement.
**AC:** benchmark không chỉ đếm fewer questions; user correction/abandoned cases được tính; paraphrases cùng family không leak sang holdout; model-only grade không cấp admission.
**QA:** QA-21, QA-26/36.
**Code:**
```ts
// tests/qc/qc-21.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-21)
import { describe, it, expect } from 'vitest'

describe('QC-21 — Golden semantic evaluation và grader rules', () => {
  it('benchmark không chỉ đếm fewer questions', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module tests/evaluation/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-21`

### Task 9: RI-22 — Fault và cross-engine integration suite
**Kind:** test
**Thoả:** RI-R22 · QA-22 · PRD §16 RI-22 · effort 3 ngày
**Depends:** 230926-rie-m1-clarify-core/t3 (data), 230926-rie-m1-clarify-core/t4 (data), Task 1 (data), Task 2 (data), Task 3 (data), Task 5 (data), Task 7 (data), Task 8 (data)
**Files:**
- Tạo: `tests/contract/`
- Tạo: `tests/scenario/`
- Tạo: `tests/qc/qc-22.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: integration evidence gắn exact revisions/capabilities + `tests/qc/qc-22.test.ts` xanh
**Bước:** (1) run QA-25…36 với runtime adapter; (2) inject crash/timeout/revoke/concurrent update; (3) verify receipts/state không chỉ response text; (4) run end-to-end ambiguous app và changed-tenant flow; (5) check graph mappings/critical acceptance preserved.
**AC:** no duplicate roots/effects do intake retry; no cross-scope leak; affected work không tiếp dưới stale goal; unknown effect được reconcile hoặc blocked rõ.
**QA:** QA-22, QA-25…36.
**Code:**
```ts
// tests/qc/qc-22.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-22)
import { describe, it, expect } from 'vitest'

describe('QC-22 — Fault và cross-engine integration suite', () => {
  it('no duplicate roots/effects do intake retry', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module tests/contract/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-22`

### Task 10: RI-23 — Telemetry, economics và Evolve signals
**Kind:** data
**Thoả:** RI-R23 · QA-23 · PRD §16 RI-23 · effort 2 ngày
**Depends:** 230926-rie-m1-clarify-core/t4 (data), 230926-rie-m1-clarify-core/t10 (data), Task 1 (data), Task 4 (data), Task 6 (data), Task 8 (data)
**Files:**
- Tạo: `projections/telemetry`
- Tạo: `tests/qc/qc-23.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: metrics dashboard/report + minimized signal schema + `tests/qc/qc-23.test.ts` xanh
**Bước:** (1) receipts question/default/handoff/outcome với scope; (2) latency active vs user wait; (3) runtime/improvement cost attribution một ledger; (4) rework/source-fidelity rubric và censoring; (5) reuse net-cost report; (6) emit versioned improvement proposal, no auto profile mutation.
**AC:** failed/abandoned có denominator; unknown cost không zero; không nói profile cải thiện khi chưa có outcome evidence; user answer không bị gửi thành public reusable memory.
**QA:** QA-23, QA-29/36.
**Code:**
```ts
// tests/qc/qc-23.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-23)
import { describe, it, expect } from 'vitest'

describe('QC-23 — Telemetry, economics và Evolve signals', () => {
  it('failed/abandoned có denominator', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module projections/telemetry
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-23`

### Task 11: RI-24 — Pilot, runbook và release decision
**Kind:** release
**Thoả:** RI-R24 · QA-24 · PRD §16 RI-24 · effort 2 ngày
**Depends:** Task 6 (data), Task 7 (data), Task 8 (data), Task 9 (data), Task 10 (data)
**Files:**
- Tạo: `release/`
- Tạo: `tests/qc/qc-24.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: pilot dossier, runbook và release checklist có results + `tests/qc/qc-24.test.ts` xanh
**Bước:** (1) staged rollout §18; (2) limited traffic policy và support workflow; (3) restore/pause/rollback rehearsal; (4) verify targets/caps, unresolved risks; (5) handoff fresher/TL, record actual test evidence; (6) release decision only within authorized scope.
**AC:** IN0 vs IN1 capabilities hiển thị đúng; không đạt hard gates không release; old sealed briefs vẫn đọc/resume được theo compatible policy; pilot measurements không claim general benefit.
**QA:** QA-24, QA-30/35/36.
**Code:**
```ts
// tests/qc/qc-24.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-24)
import { describe, it, expect } from 'vitest'

describe('QC-24 — Pilot, runbook và release decision', () => {
  it('IN0 vs IN1 capabilities hiển thị đúng', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module src/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-24`

## Origin
- **Nguồn:** PRD v1.0 `llmwiki/raw/prd/Reprise-Intent-Engine-Product-Grade-PRD.md` §16 (ticket RI-14…RI-24), §3.1 bất biến, §14.2 trần mặc định, §17.3 kịch bản nghiệm thu; bản chưng cất [[230926-reprise-intent-engine-prd]].
- **Yêu cầu user:** 23/09/2026 — "task làm graph của tôi về phần intent engine đã có chưa" rồi "tách ra 2 graph đi".
- **Sinh bằng:** `scratchpad/gen_rie_plans.py` đọc thẳng PRD (deps/module/AC/QA lấy từ ticket, không chép tay).
