---
type: draft
title: "PLAN — Reprise Intent Engine, phần 1: nền tảng và lõi làm rõ (RI-01…RI-13)"
status: proposed
tags: [plan, reprise, intent-engine, orca-graph]
timestamp: 2026-09-23
---

# PLAN 230926 — Reprise Intent Engine, phần 1: nền tảng và lõi làm rõ (RI-01…RI-13)

Nguồn: [[230926-reprise-intent-engine-prd]] (raw `llmwiki/raw/prd/Reprise-Intent-Engine-Product-Grade-PRD.md`). Backlog 24 ticket vượt trần 20 node/graph của orca-graph nên tách HAI graph anh em: `230926-rie-m1-clarify-core` (RI-01…RI-13, mốc M1+M2) và `230926-rie-m2-lifecycle-product` (RI-14…RI-24, mốc M3+M4). Graph này là phần 1.

## Global constraints
- Repo đích: `/Users/giatran/orca/reprise-intent-engine` (repo MỚI, Task 1 của graph 1 tạo). Mọi đường dẫn trong **Files:** tính từ gốc repo đó; PRD là nguồn đặc tả — mỗi task đọc đúng mục §16 của ticket mình.
- Bất biến §3.1 là luật cứng cho mọi task: không có nguồn thì không thành requirement; draft chưa niêm phong không được coi là sealed brief; actor/grant không tự khai; mọi hiệu ứng ra ngoài phải có receipt.
- Model chỉ được dùng ở các điểm PRD cho phép (§6.1); output của model là *untrusted proposal*, phải qua schema + kiểm nguồn trước khi vào brief.
- Trần mặc định §14.2: 1 job/case, tối đa 6 model call một episode, ≤ 2 vòng hỏi chủ động, ≤ 3 câu/vòng, ≤ 5 source read, context ≤ 12.000 token, deadline 5 phút máy chạy; host cap nhỏ hơn luôn thắng.
- Test kiểm BẤT BIẾN và ca gây mất/sai dữ liệu, không mirror từng dòng code. Mỗi task có đúng file `tests/qc/qc-NN.test.ts` theo kịch bản QA ở PRD §17.3; tên `it(...)` bắt đầu bằng `QC-NN`.
- Không mở port public, không egress chưa duyệt, không bí mật trong URL/log.
- Không AI-attribution trong commit.

### Task 1: RI-01 — Domain contracts và fixture vocabulary
**Kind:** build
**Thoả:** RI-R01 · QA-01 · PRD §16 RI-01 · effort 2 ngày
**Depends:** —
**Files:**
- Tạo: `contracts/`
- Tạo: `tests/fixtures/`
- Tạo: `tests/qc/qc-01.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: schema package, glossary, valid/invalid fixtures + `tests/qc/qc-01.test.ts` xanh
**Bước:** (1) tạo enums/IDs cho §4–5, phân biệt event/atom/decision/brief/report; (2) schema cho phase-specific required fields, unknown/null/missing và typed errors; (3) viết synthetic fixtures rõ/mơ hồ/conflict/unreadable; (4) document ownership và input trust boundaries.
**AC:** schema reject thiếu source status và boolean giả thay enum; draft unresolved không thể deserialize thành sealed brief; actor/grant self-assertion không thành trusted facts.
**QA:** QA-01, làm nền QA-26/27.
**Code:**
```ts
// tests/qc/qc-01.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-01)
import { describe, it, expect } from 'vitest'

describe('QC-01 — Domain contracts và fixture vocabulary', () => {
  it('schema reject thiếu source status và boolean giả thay enum', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module contracts/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-01`

### Task 2: RI-02 — Ingress và idempotent event reception
**Kind:** build
**Thoả:** RI-R02 · QA-02 · PRD §16 RI-02 · effort 2 ngày
**Depends:** Task 1 (data)
**Files:**
- Tạo: `ingestion/`
- Tạo: `tests/qc/qc-02.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: ingress command handler dùng StorePort fake trước + `tests/qc/qc-02.test.ts` xanh
**Bước:** (1) validate input size/type theo host; (2) bind actor/workspace từ session; (3) compute payload digest và lưu raw event/inbox; (4) duplicate same-key cùng body trả receipt cũ; key collision khác body trả conflict; (5) phân biệt received/applied.
**AC:** hai retries không tạo hai events/cases; invalid attachment ref không bị tự thay bằng file khác; event text được giữ khi apply revision conflict.
**QA:** QA-02, QA-28.
**Code:**
```ts
// tests/qc/qc-02.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-02)
import { describe, it, expect } from 'vitest'

describe('QC-02 — Ingress và idempotent event reception', () => {
  it('hai retries không tạo hai events/cases', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module ingestion/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-02`

### Task 3: RI-03 — Durable store, CAS và transactional outbox
**Kind:** build
**Thoả:** RI-R03 · QA-03 · PRD §16 RI-03 · effort 3 ngày
**Depends:** Task 1 (data), Task 2 (data)
**Files:**
- Tạo: `handoff/outbox`
- Tạo: `tests/qc/qc-03.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: store adapter + migration và crash fixture + `tests/qc/qc-03.test.ts` xanh
**Bước:** (1) schema bảng §12.3 với unique/FK; (2) transaction update aggregate bằng expected revision; (3) event/outbox cùng commit; (4) append history, immutable sealed bytes; (5) recovery scan cho pending outbox không dùng LLM.
**AC:** concurrent writes chỉ một commit trên cùng revision; crash giữa domain write và outbox không tạo trạng thái nửa vời; history truy được; workspace isolation server-side.
**QA:** QA-03, QA-28.
**Code:**
```ts
// tests/qc/qc-03.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-03)
import { describe, it, expect } from 'vitest'

describe('QC-03 — Durable store, CAS và transactional outbox', () => {
  it('concurrent writes chỉ một commit trên cùng revision', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module handoff/outbox
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-03`

### Task 4: RI-04 — RuntimePort và budget binding
**Kind:** infra
**Thoả:** RI-R04 · QA-04 · PRD §16 RI-04 · effort 3 ngày
**Depends:** Task 1 (data), Task 3 (data)
**Files:**
- Tạo: `adapters/runtime`
- Tạo: `adapters/policy`
- Tạo: `tests/qc/qc-04.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: conformance suite và capability matrix + `tests/qc/qc-04.test.ts` xanh
**Bước:** (1) bind current grants/capabilities; (2) reserve/settle usage qua ledger; (3) liên kết intake allocation tới Graph root; (4) cap min(host, profile); (5) implement unknown settlement/revocation responses; fake/real capability profiles tách rõ.
**AC:** không có host → IN0/export; retry/episode mới không reset cumulative quota; denied hoặc unknown grant không dispatch action; cost unknown không ghi zero.
**QA:** QA-04, QA-29/30.
**Code:**
```ts
// tests/qc/qc-04.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-04)
import { describe, it, expect } from 'vitest'

describe('QC-04 — RuntimePort và budget binding', () => {
  it('không có host → IN0/export', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module adapters/runtime
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-04`

### Task 5: RI-05 — Scoped context và source manifest
**Kind:** build
**Thoả:** RI-R05 · QA-05 · PRD §16 RI-05 · effort 3 ngày
**Depends:** Task 1 (data), Task 3 (data), Task 4 (data)
**Files:**
- Tạo: `context/`
- Tạo: `tests/qc/qc-05.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: ContextReadPort adapter + context packet builder + `tests/qc/qc-05.test.ts` xanh
**Bước:** (1) resolve authorized sources; (2) đọc relevant spans có version/digest; (3) access filter trước retrieval; (4) distinguish empty/unreadable/revoked; (5) bounded packet + omission manifest; (6) cache key/invalidation theo actor/scope/epochs.
**AC:** nguồn denied không xuất hiện trong snippets/context/log/visible existence; cache không bypass revoke; packet truncated vẫn giữ constraints và unknown summary.
**QA:** QA-05, QA-25/27/30.
**Code:**
```ts
// tests/qc/qc-05.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-05)
import { describe, it, expect } from 'vitest'

describe('QC-05 — Scoped context và source manifest', () => {
  it('nguồn denied không xuất hiện trong snippets/context/log/visible existence', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module context/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-05`

### Task 6: RI-06 — Resolver cho “cái trước”, tiếp việc và corrections
**Kind:** build
**Thoả:** RI-R06 · QA-06 · PRD §16 RI-06 · effort 2 ngày
**Depends:** Task 2 (data), Task 5 (data)
**Files:**
- Tạo: `ingestion/reference-resolution`
- Tạo: `tests/qc/qc-06.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: resolver result có alternatives/source refs và typed status + `tests/qc/qc-06.test.ts` xanh
**Bước:** (1) match explicit IDs/current task refs; (2) xét known thread/project relation; (3) nhiều candidates tương đương → ambiguity; (4) user choice tạo target decision; (5) stale reference không tự bind project gần nhất.
**AC:** “tiếp tục” có duy nhất active task đúng context resume được; hai plausible targets cần resolve trước read/write; correction cùng task không tạo root mới.
**QA:** QA-06, QA-28.
**Code:**
```ts
// tests/qc/qc-06.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-06)
import { describe, it, expect } from 'vitest'

describe('QC-06 — Resolver cho “cái trước”, tiếp việc và corrections', () => {
  it('“tiếp tục” có duy nhất active task đúng context resume được', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module ingestion/reference-resolution
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-06`

### Task 7: RI-07 — Extractor có schema, provenance và bounded repair
**Kind:** build
**Thoả:** RI-R07 · QA-07 · PRD §16 RI-07 · effort 3 ngày
**Depends:** Task 1 (data), Task 4 (data), Task 5 (data), Task 6 (data)
**Files:**
- Tạo: `extraction/`
- Tạo: `tests/qc/qc-07.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: extractor pipeline + tagged atoms + `tests/qc/qc-07.test.ts` xanh
**Bước:** (1) prompt contract WHAT/HOW cho untrusted proposal; (2) schema parse; (3) validate source span/ref và status; (4) semantic support review theo risk/profile; (5) tối đa một repair trong same budget; (6) persist proposal/validation riêng, minimize raw logs.
**AC:** model đề xuất billing từ “product-grade” bị giữ proposed/unsupported, không thành user requirement; invalid source link không pass; provider lỗi trả incomplete record.
**QA:** QA-07, QA-25/26.
**Code:**
```ts
// tests/qc/qc-07.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-07)
import { describe, it, expect } from 'vitest'

describe('QC-07 — Extractor có schema, provenance và bounded repair', () => {
  it('model đề xuất billing từ “product-grade” bị giữ proposed/unsupported, không thành user requirement', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module extraction/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-07`

### Task 8: RI-08 — Ambiguity Map và conflict classifier
**Kind:** build
**Thoả:** RI-R08 · QA-08 · PRD §16 RI-08 · effort 2 ngày
**Depends:** Task 6 (data), Task 7 (data)
**Files:**
- Tạo: `ambiguity/`
- Tạo: `tests/qc/qc-08.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: map có resolution route và evidence + `tests/qc/qc-08.test.ts` xanh
**Bước:** (1) taxonomy identity/goal/domain/constraint/delivery/source; (2) gắn alternatives và affected decisions/slices; (3) dedup semantic candidates bằng refs có kiểm; (4) identify conflicts và uncertain dependency; (5) không inflate optional cosmetics thành global blockers.
**AC:** single/multi-tenant unknown chặn data boundary phụ thuộc; accent color không chặn source inventory; “offline hoàn toàn” + “live cloud sync bắt buộc” xuất conflict rõ.
**QA:** QA-08, QA-31.
**Code:**
```ts
// tests/qc/qc-08.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-08)
import { describe, it, expect } from 'vitest'

describe('QC-08 — Ambiguity Map và conflict classifier', () => {
  it('single/multi-tenant unknown chặn data boundary phụ thuộc', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module ambiguity/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-08`

### Task 9: RI-09 — Decision và Assumption Ledger
**Kind:** build
**Thoả:** RI-R09 · QA-09 · PRD §16 RI-09 · effort 2 ngày
**Depends:** Task 3 (data), Task 7 (data), Task 8 (data)
**Files:**
- Tạo: `decisions/`
- Tạo: `tests/qc/qc-09.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: lifecycle service + typed decision commands + `tests/qc/qc-09.test.ts` xanh
**Bước:** (1) create/supersede decisions với actor/source/scope; (2) safe-default classes và reversal criteria; (3) map delegation “tự quyết” vào scope hiện hành; (4) expiry/source invalidation; (5) render user asserted khác active default.
**AC:** im lặng không confirm; user chọn scope mới supersede đúng scope cũ, không xóa history; grant không được sinh từ assumption.
**QA:** QA-09, QA-29/32.
**Code:**
```ts
// tests/qc/qc-09.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-09)
import { describe, it, expect } from 'vitest'

describe('QC-09 — Decision và Assumption Ledger', () => {
  it('im lặng không confirm', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module decisions/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-09`

### Task 10: RI-10 — Question Planner và xử lý replies từng phần
**Kind:** build
**Thoả:** RI-R10 · QA-10 · PRD §16 RI-10 · effort 3 ngày
**Depends:** Task 8 (data), Task 9 (data)
**Files:**
- Tạo: `interaction/questions`
- Tạo: `tests/qc/qc-10.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: batch lifecycle và response mapper + `tests/qc/qc-10.test.ts` xanh
**Bước:** (1) rank theo §7.2; (2) require unlock/why-now/evidence; (3) lookup answered decisions trước hỏi; (4) enforce round/question caps; (5) support free text/không biết/partial replies; (6) no-progress detection bằng fingerprints.
**AC:** câu hỏi không đổi next action bị loại; answered/current question không lặp; “web thôi” chỉ resolve platform; hết lượt hỏi chuyển wait/draft phù hợp, không chọn bừa.
**QA:** QA-10, QA-32/33.
**Code:**
```ts
// tests/qc/qc-10.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-10)
import { describe, it, expect } from 'vitest'

describe('QC-10 — Question Planner và xử lý replies từng phần', () => {
  it('câu hỏi không đổi next action bị loại', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module interaction/questions
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-10`

### Task 11: RI-11 — Draft Probe có scope và learning objective
**Kind:** research
**Thoả:** RI-R11 · QA-11 · PRD §16 RI-11 · effort 2 ngày
**Depends:** Task 4 (data), Task 9 (data), Task 10 (data)
**Files:**
- Tạo: `interaction/probes`
- Tạo: `tests/qc/qc-11.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: probe contract, renderer hoặc Graph draft adapter request + `tests/qc/qc-11.test.ts` xanh
**Bước:** (1) define decision being tested và artifact limit; (2) bind draft-only capability; (3) output 1–2 small alternatives với assumptions; (4) interpret feedback theo property được nói; (5) enforce one probe/no-progress cap.
**AC:** thích layout không confirm auth/tenant; probe không thực hiện live effects; no feedback giữ decision unknown; cost settlement thuộc allocation cũ.
**QA:** QA-11, QA-29/33.
**Code:**
```ts
// tests/qc/qc-11.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-11)
import { describe, it, expect } from 'vitest'

describe('QC-11 — Draft Probe có scope và learning objective', () => {
  it('thích layout không confirm auth/tenant', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module interaction/probes
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-11`

### Task 12: RI-12 — Phase/slice Readiness Gate
**Kind:** build
**Thoả:** RI-R12 · QA-12 · PRD §16 RI-12 · effort 3 ngày
**Depends:** Task 4 (data), Task 8 (data), Task 9 (data)
**Files:**
- Tạo: `readiness/`
- Tạo: `tests/qc/qc-12.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: gate library và per-slice report + `tests/qc/qc-12.test.ts` xanh
**Bước:** (1) implement required check sets theo phase; (2) dependency closure và unknown independence; (3) pure preflight tương đương §15; (4) bind report vào exact brief inputs/policy epochs; (5) map unresolved sang authorized investigation hoặc question route.
**AC:** discovery có thể proceed khi solution unknown nhưng question/source/scope đủ; implement chưa có contract không proceed; một slice pass không bù slice fail; model confidence không quyết định admission.
**QA:** QA-12, QA-31/34.
**Code:**
```ts
// tests/qc/qc-12.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-12)
import { describe, it, expect } from 'vitest'

describe('QC-12 — Phase/slice Readiness Gate', () => {
  it('discovery có thể proceed khi solution unknown nhưng question/source/scope đủ', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module readiness/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-12`

### Task 13: RI-13 — Brief compiler, coverage và immutable seal
**Kind:** build
**Thoả:** RI-R13 · QA-13 · PRD §16 RI-13 · effort 2 ngày
**Depends:** Task 3 (data), Task 7 (data), Task 9 (data), Task 12 (data)
**Files:**
- Tạo: `briefs/`
- Tạo: `tests/qc/qc-13.test.ts`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (xem **Output** của ticket đó trong PRD §16)
- Produces: Markdown/read projection và machine contract cùng nguồn dữ liệu + `tests/qc/qc-13.test.ts` xanh
**Bước:** (1) compile normalized atoms/decisions thành brief theo phase; (2) map every explicit requirement to disposition; (3) derive observable AC có rationale, không inflate scope; (4) validate resolved refs; (5) canonical bytes/digest và seal transaction.
**AC:** không có requirement bị rơi im lặng; snapshot cũ không sửa được; deferred must-have hiện chưa đáp ứng scope; draft unresolved không gửi như execution-ready.
**QA:** QA-13, QA-26/34.
**Code:**
```ts
// tests/qc/qc-13.test.ts — viết TEST TRƯỚC, đỏ rồi mới code (AC §16 RI-13)
import { describe, it, expect } from 'vitest'

describe('QC-13 — Brief compiler, coverage và immutable seal', () => {
  it('không có requirement bị rơi im lặng', async () => {
    // arrange: fixture theo contracts/ (enum epistemic + provenance bắt buộc)
    // act:     gọi cổng của module briefs/
    // assert:  kiểm RECEIPT/state, không kiểm chuỗi phản hồi
    expect.hasAssertions()
  })
})
```
**Verify:** `cd /Users/giatran/orca/reprise-intent-engine && pnpm vitest run tests/qc/qc-13`

## Origin
- **Nguồn:** PRD v1.0 `llmwiki/raw/prd/Reprise-Intent-Engine-Product-Grade-PRD.md` §16 (ticket RI-01…RI-13), §3.1 bất biến, §14.2 trần mặc định, §17.3 kịch bản nghiệm thu; bản chưng cất [[230926-reprise-intent-engine-prd]].
- **Yêu cầu user:** 23/09/2026 — "task làm graph của tôi về phần intent engine đã có chưa" rồi "tách ra 2 graph đi".
- **Sinh bằng:** `scratchpad/gen_rie_plans.py` đọc thẳng PRD (deps/module/AC/QA lấy từ ticket, không chép tay).
