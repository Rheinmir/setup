---
name: query
description: Synthesize answer from wiki; persist new insights as wiki entries. Trả lời kèm mục Evidence trích dẫn edge ID (eid) của các cạnh trong đồ thị wiki thật sự chống lưng kết luận — dùng khi cần biết "căn cứ nào", "trích dẫn cạnh nào", "đường đi trong graph", "cite evidence".
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: query

## WHAT

### Purpose và context
- **Purpose:** Answer question by synthesizing wiki knowledge. Valuable findings not in wiki become new pages, compounding knowledge over time.
- **Trigger (when to invoke):** When user asks question requiring synthesis across multiple wiki pages or raw sources; hoặc khi cần biết "căn cứ nào", "trích dẫn cạnh nào", "đường đi trong graph", "cite evidence".
- **Non-goals:** không trả lời bằng kiến thức ngoài wiki/`raw/` (không bịa fact); không tự ingest cả nguồn (gap → gọi `ingest`); không sửa cờ drift của trang (việc của `/lint`/`wiki-sync`).

### Mental model
`câu hỏi → Tầng 0 mem-rank (episodic) → Tầng 1 rg xếp hạng theo độ phủ term → Tầng 2 Read full top-N → Tầng 3 wikilinks → cổng drift → tổng hợp → [trang wiki mới nếu insight mới] → log + telemetry → Evidence (eid cạnh)`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | câu hỏi | có | cần tổng hợp nhiều trang wiki / raw |
| Out | câu trả lời | có | cảnh báo `⚑ CẢNH BÁO DRIFT` (nếu có) đặt đầu câu trả lời |
| Out | mục `## Evidence` | có | eid cạnh thật sự chống lưng, hoặc `Evidence: none (page-level only)` |
| Out | trang wiki mới + index + log | chỉ khi có insight mới | concept hoặc source |
| Out | dòng `wiki/log.md` + bản ghi `query-log.py` | có | log `## YYYY-MM-DD — query — <question summary>`; telemetry fail-open |
| Out | output report draft | có (trừ khi 0 artifact) | mục Delivery |

### Rules và capabilities
- RULE-01 (MUST): **OKF v0.1 (R9):** any new wiki page starts with a YAML frontmatter block (`---`) with a non-empty `type`; copy the matching `_template.md` and keep the `## Origin` section.
- RULE-02 (MUST): Never invent facts. Synthesize from wiki and `raw/` only.
- RULE-03 (SHOULD): Query revealing gap (missing entity, missing concept) should trigger `ingest` of relevant `raw/` source if one exists.
- RULE-04 (MUST): Progressive disclosure — ĐỪNG nạp cả trang ở bước 1; chỉ Read full top-N.
- RULE-05 (MUST): Cảnh báo drift phải được chuyển nguyên văn vào câu trả lời — không nuốt, không từ chối trả lời.
- Capabilities: đọc wiki + `raw/` + tầng nhớ episodic + wiki graph; ghi trang wiki mới, index, log, telemetry. Code-graph cho câu hỏi về code.

### Failure boundaries
- Wiki và `raw/` không có thông tin → nói rõ không có căn cứ (**partial**), không bịa.
- Không cạnh nào chống lưng → `Evidence: none (page-level only)`.
- Trang đọc bị cờ drift → vẫn trả lời, kèm cảnh báo đầu câu trả lời.
- Script tầng 0 / drift / telemetry lỗi → fail-open, bỏ qua bước đó, không gãy phiên.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | câu hỏi | Tầng 0 `mem-rank.py retrieve` | top-k memory/episode | NOOP → bỏ qua |
| W02 | deterministic | câu hỏi | Tầng 1 `rg` xếp hạng theo độ phủ term (code → `search_symbols`) | danh sách slug | — |
| W03 | effect | top-N | Tầng 2 Read full top-N (~5); Tầng 3 lần wikilinks nếu cần | nội dung trang | — |
| W04 | deterministic | slug đã đọc | Cổng drift `wiki-sync.py --flags-for` | cảnh báo hoặc im lặng | luôn exit 0 |
| W05 | judgment | nội dung | Thiếu → check `raw/`; tổng hợp và trả lời | câu trả lời | không có căn cứ → partial |
| W06 | judgment | câu trả lời | Insight mới? → tạo trang + index + log | trang mới / skip | không → skip |
| W07 | effect | kết quả | Log `wiki/log.md` + telemetry `query-log.py --record` | log + bản ghi | fail-open |
| W08 | deterministic | trang căn cứ | `wiki-graph.py cite <page>` → mục `## Evidence` | eid cạnh | none → page-level only |

Chi tiết từng bước (nguồn chân lý cho W01–W08):

#### Steps — progressive disclosure 3 tầng (ĐỪNG nạp cả trang ở bước 1)
> Nguyên tắc: quét RẺ để xếp hạng trước, chỉ ĐỌC FULL vài trang cao điểm. Đo trên bộ golden
> `wiki/sources/evals/retrieval/` cho thấy cách này giữ nguyên recall mà cắt ~65% token so với
> "đọc mọi trang khớp" (baseline L0). Kiểm chứng: `retrieval-eval.py --check`.

0. **Tầng 0 — truy hồi NGỮ NGHĨA (episodic + memory), KHÔNG chỉ theo link:** trước khi quét wiki,
   hỏi tầng nhớ episodic xem *phiên trước* đã đụng câu hỏi này chưa:
   `python3 harness/scripts/mem-rank.py retrieve "<câu hỏi>" --k 5` (thêm `--kind-filter episode`
   để chỉ lấy sự kiện phiên). Trả về top-k memory/episode liên quan theo **nghĩa** (token-overlap,
   sẽ là embedding khi adapter `mem-rank.config.yaml` được wire) — bắt được trang KHÔNG có
   `[[wikilink]]` trỏ tới. NOOP (rỗng) thì bỏ qua, không nhồi nhiễu. Dùng kết quả này để mồi
   danh sách trang cho Tầng 1 + biết "việc này từng làm ở phiên nào".
1. **Tầng 1 — quét, KHÔNG mở full trang nào:** `ripgrep` câu hỏi trên `wiki/index.md` + nội dung wiki (`rg -c '<term>' wiki/` để đếm khớp), xếp hạng trang theo **độ phủ term** (trang chứa nhiều term của câu hỏi nhất). Câu hỏi về code → dùng code-graph MCP (`search_symbols`) thay `rg`. Kết quả tầng này = danh sách slug + dòng khớp; chưa `Read` full trang nào.
2. **Tầng 2 — khoan:** chỉ `Read` FULL **top-N trang cao điểm nhất** (mặc định ~5). Bỏ phần đuôi bảng xếp hạng — không đọc cho "chắc".
3. **Tầng 3 — bối cảnh:** nếu câu trả lời cần mạch liên quan, lần theo `[[wikilinks]]` của các trang vừa đọc (tương đương timeline/related của engram) — vẫn chỉ mở trang được trỏ tới, không mở tất cả.
3b. **Cổng drift trên đường ĐỌC (0 token, fail-open)** — trước khi tổng hợp, hỏi xem trang mình vừa đọc có đang lệch code không:
   `RUN: python3 harness/scripts/wiki-sync.py --flags-for "<slug1,slug2,…>"` (downstream không có `harness/` trong repo thì dùng bản global: `python3 ~/.claude/harness/harness/scripts/wiki-sync.py --flags-for "…" --root .`).
   Truyền đúng các trang đã `Read` ở tầng 2–3. Lệnh **luôn exit 0**; im lặng = không trang nào bị cờ.
   Có dòng `⚑ CẢNH BÁO DRIFT` → **chuyển nguyên văn cảnh báo đó vào câu trả lời** (một dòng mỗi trang, đặt ngay đầu phần trả lời) rồi mới trả lời bình thường; đừng nuốt cảnh báo, cũng đừng từ chối trả lời.
   Vì sao có bước này: `wiki-sync --check` ghi cờ `code-drift` vào `stale.json`, nhưng trước 2026-07-19 chỉ `/lint` đọc cờ đó — mà lint chạy theo chu kỳ, nên giữa hai lần lint `/query` trả về trang đã lệch code **mà không cảnh báo gì**. Đó đúng là ca "wiki là nguồn sự thật nhưng nội dung đã lệch" khiến model lập luận tự tin trên tri thức cũ.

4. If answer needs info not in wiki, check `raw/` for unprocessed sources.
5. Synthesize and answer directly.
6. Evaluate: does answer contain non-obvious insight, connection, or conclusion not already in wiki?
   - If yes: create new wiki page (concept or source), update `wiki/index.md`, log in `wiki/log.md`.
   - If no: skip.
7. Append to `wiki/log.md`: `## YYYY-MM-DD — query — <question summary>` with note on whether new page created.
8. **Telemetry (đo TRUY HỒI — fail-open):** sau khi trả lời, ghi lại query để độ hiệu quả truy-hồi đo được:
   `python3 harness/scripts/query-log.py --record --question "<câu hỏi>" --pages "<slug1,slug2>" --tokens <ước tính token đã đọc> --tier <1|2|3>`
   `--pages` = các trang wiki thực sự đọc; `--tier` = tầng sâu nhất chạm tới (1 quét / 2 đọc full / 3 wikilinks). Script fail-open — không bao giờ làm gãy phiên. Giới hạn đã biết: chỉ đo khi skill `query` được gọi, không đo lượt model tự Read thẳng.

9. **Evidence — trích cạnh, không chỉ trích trang.** Với MỖI trang wiki đã dùng làm căn cứ, chạy:
   `python3 harness/scripts/wiki-graph.py cite <page>`
   rồi đính mục `## Evidence` vào cuối câu trả lời, liệt kê **eid của những cạnh thật sự chống lưng** kết luận — không liệt kê cạnh chỉ vì nó tồn tại:
   ```
   ## Evidence
   - e:4b65f8c5  concepts/decision-anchoring.md -> concepts/adapt-modes.md  (wikilink)
   - e:988aa19d  index.md -> concepts/example-concept.md  (mdlink)
   ```
   Không cạnh nào chống lưng → ghi thẳng `Evidence: none (page-level only)`. Trung thực hơn bịa một đường đi. Cạnh có kiểu (`supports`/`contradicts`/`supersedes`/`derives-from`/`depends-on`) khai trong frontmatter `relations:` của trang, mạnh hơn `wikilink` trần vì nó nói RÕ quan hệ.


### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | câu hỏi về code | dùng code-graph MCP (`search_symbols`) thay `rg` ở Tầng 1 | — | W03 |
| B02 | conditional_required | có dòng `⚑ CẢNH BÁO DRIFT` | chuyển nguyên văn vào đầu câu trả lời | im lặng → skip | W05 |
| B03 | conditional_required | downstream không có `harness/` trong repo | dùng bản global `~/.claude/harness/harness/scripts/wiki-sync.py --root .` | — | W05 |
| B04 | conditional_required | câu trả lời có insight mới không có trong wiki | tạo trang concept/source + index + log (OKF) | không → skip | W07 |
| B05 | conditional_required | query lộ gap và có nguồn `raw/` liên quan | gọi `ingest` nguồn đó | không có nguồn → ghi gap | W07 |

### Validation và stopping
Tất định: `retrieval-eval.py --check` đo recall/token của progressive disclosure; `wiki-graph.py cite` sinh eid thật. Judgment: tổng hợp và đánh giá "insight mới". Dừng sau W08 + Delivery; không mở thêm trang ngoài top-N "cho chắc".

### Examples
- **Positive:** "vì sao adapt-modes tách 3 kiểu absorb?" → rg xếp hạng, Read `concepts/adapt-modes.md` + 2 trang cao điểm, drift im lặng → trả lời + `## Evidence` liệt kê `e:4b65f8c5  concepts/decision-anchoring.md -> concepts/adapt-modes.md  (wikilink)`; không insight mới → không tạo trang.
- **Boundary/failure:** trang đọc bị cờ code-drift → câu trả lời mở đầu bằng dòng `⚑ CẢNH BÁO DRIFT` nguyên văn rồi mới trả lời; không cạnh nào chống lưng → `Evidence: none (page-level only)`.

---

### Delivery — Output Report

After all main skill tasks complete, write a propose draft to the wiki.

#### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/sources/draft/DDMMYY-<ten>.md`:

```
---
type: draft
title: "DDMMYY-<ten>"
status: proposed
tags: [<skill-name>, output-report]
timestamp: YYYY-MM-DD
---

# DDMMYY-<ten>
**Type:** draft
**Status:** proposed
**Tags:** <skill-name>, output-report
**Proposed:** YYYY-MM-DD

## What
<One sentence — what this skill invocation produced or decided>

## Output
<Key artefacts, files created/modified, or decisions made>

## Files
| File | Action |
|------|--------|
| `path/to/file` | created / modified |

## Notes
- Invoked via: `/<skill-name>` skill

## Origin
- **Draft:** `wiki/sources/draft/DDMMYY-<ten>.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
```

**3. Update wiki index & log:**
- `llmwiki/wiki/index.md` — append one row: `| [DDMMYY-<ten>](sources/draft/DDMMYY-<ten>.md) | draft | YYYY-MM-DD |`
- `llmwiki/wiki/log.md` — append: `## YYYY-MM-DD — <skill-name> — <ten>`

> Skip only when the skill produces zero artefacts and zero decisions (e.g., a pure display mode like `/caveman-stats`).
