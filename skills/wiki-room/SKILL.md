---
name: wiki-room
description: "Mở room (subagent 1 tầng) nạp chi tiết wiki khi context phiên chính đã rot — depth cap=1, budget cứng, circuit breaker. Trigger: 'mở room', 'context rot', 'nạp thêm chi tiết wiki', 'đào sâu wiki', '/wiki-room'."
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: wiki-room

Tier C của wiki-core v2 (concept `wiki-core-relations`): khi context phiên chính đã dài/rot,
KHÔNG nạp thêm chi tiết vào phiên chính — mở MỘT room (subagent) nạp đầy đủ rồi trả về
kết luận nén. Phiên chính giữ bản đồ (Tier A), chi tiết sống trong room dùng-xong-bỏ.

## WHAT

### Purpose và context
- **Purpose:** trả lời câu hỏi cần chi tiết sâu từ nhiều trang wiki mà KHÔNG làm phình context phiên chính — chi tiết đọc trong một room (subagent) dùng-xong-bỏ, phiên chính chỉ nhận kết luận nén có nguồn.
- **Trigger (when to use):**
  - Phiên chính đã dài (nhiều lần tóm tắt/summarize) mà cần chi tiết sâu từ nhiều trang wiki.
  - Câu hỏi cần đọc >3 trang wiki đầy đủ + hàng xóm quan hệ của chúng.
  - User nói "mở room", "context rot", "nạp thêm chi tiết wiki", "đào sâu wiki", `/wiki-room`.
- **Non-goals:**
  - KHÔNG dùng khi chỉ cần 1-2 trang cụ thể — đọc thẳng rẻ hơn một room (tiêu chí tốc độ).
  - Không phải trí nhớ dài hạn — tri thức đọng lại phải distill vào wiki qua `/ingest` hoặc cập nhật trang.
  - Không sửa wiki; room chỉ đọc và tổng hợp.

### Mental model
`câu hỏi → brief Tier A (list id + trang stale + episode mồi) → budget B → MỘT room (subagent, depth 1) đọc Tier B + hàng xóm 1 bước → kết luận nén ≤500 từ có nguồn → phiên chính hành động`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | câu hỏi | có | điều cần đào sâu trong wiki |
| In | budget B | không (mặc định 12) | trần số trang Tier B, gồm cả hàng xóm quan hệ 1 bước |
| In | list id trang | tự lập ở W01 | từ câu hỏi + `wiki/index.md` + `wiki/stale.json` + truy hồi episode |
| Out | kết luận nén | có | ≤500 từ, mọi khẳng định kèm trang nguồn; trang stale gắn cờ; chạm budget → ghi "đã chạm budget, chưa đọc: <list>"; thiếu dữ liệu → "thiếu: <gì>" |

"Xong" = phiên chính nhận kết luận nén và hành động tiếp trên đó, không paste toàn văn trang.

### Rules và capabilities
Ba luật cứng (chép NGUYÊN VĂN vào prompt room):
- RULE-01 (MUST): **Depth cap = 1 (G3):** room KHÔNG được mở room/subagent con dưới bất kỳ lý do gì. Thiếu dữ liệu
  → ghi "thiếu: <gì>" vào kết luận, để phiên chính quyết.
- RULE-02 (MUST): **Budget cứng:** đọc tối đa B trang. Chạm trần → DỪNG đọc, tổng hợp từ những gì đã có
  (circuit breaker — trả kết quả cắt ngắn kèm ghi chú "đã chạm budget, chưa đọc: <list>").
- RULE-03 (MUST): **Kết luận nén có nguồn:** mọi khẳng định kèm trang nguồn (`concepts/x.md`); trang nguồn đang
  stale (theo brief) phải ghi kèm cờ "(stale — kiểm chứng lại trước khi tin)".

Anti-patterns (luật phụ cho phiên chính):
- RULE-04 (MUST NOT): Mở nhiều room song song cho một câu hỏi (mất kiểm soát budget tổng) — một câu hỏi, một room.
- RULE-05 (MUST NOT): Dùng room như trí nhớ dài hạn — room là dùng-xong-bỏ; tri thức đọng lại phải distill vào wiki
  qua `/ingest` hoặc cập nhật trang, không nằm trong transcript room.
- RULE-06 (SHOULD NOT): Gọi room khi phiên chính còn ngắn — đọc thẳng luôn nhanh hơn.

- Capabilities: đọc wiki (index, stale list, frontmatter `relations:`); truy hồi ngữ nghĩa episodic; spawn đúng một subagent read-only. Không ghi wiki.

### Failure boundaries
- Câu hỏi chỉ cần 1-2 trang → không mở room, đọc thẳng (từ chối hợp lệ).
- Room chạm budget B → **partial**: kết luận cắt ngắn + list trang chưa đọc.
- Room thiếu dữ liệu → ghi "thiếu: <gì>", phiên chính quyết (không mở room con).
- Trang nguồn stale → vẫn dùng nhưng gắn cờ kiểm chứng lại.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | judgment | câu hỏi, `wiki/index.md`, `wiki/stale.json`, `mem-rank.py` | Lập brief Tier A (phiên chính, rẻ) | list id trang + cờ stale + episode mồi | ≤2 trang → đọc thẳng, dừng |
| W02 | deterministic | list id, frontmatter `relations:` | Chốt budget B TRƯỚC khi mở (mặc định 12, gồm hàng xóm 1 bước) | B + list trong trần | — |
| W03 | effect | brief, B, 3 luật cứng | Mở ĐÚNG MỘT room (subagent Explore/general-purpose) | room chạy | — |
| W04 | judgment | kết luận room | Nhận kết luận nén (≤500 từ + nguồn), hành động tiếp | quyết định phiên chính | chạm budget/thiếu → B01 |

Chi tiết từng bước (nguồn chân lý cho W01–W04):

1. **Lập brief Tier A (phiên chính, rẻ):** thu list id trang cần đào — từ câu hỏi + `wiki/index.md`
   + `wiki/stale.json` (trang stale liên quan phải nêu rõ trong brief là "có thể lỗi thời").
   Mồi thêm bằng truy hồi NGỮ NGHĨA episodic: `python3 harness/scripts/mem-rank.py retrieve
   "<câu hỏi>" --kind-filter episode` — bắt "phiên trước làm gì" mà không cần `[[wikilink]]`;
   đưa các file/episode nổi lên vào brief cho room.
2. **Chốt budget TRƯỚC khi mở:** tối đa B trang Tier B (mặc định 12) + hàng xóm quan hệ 1 bước
   (đọc `relations:` frontmatter của các trang trong list — cũng tính vào B).
3. **Mở ĐÚNG MỘT room:** spawn 1 subagent Explore/general-purpose với prompt gồm: câu hỏi, list id,
   budget B, và 3 luật cứng ở mục Rules (chép nguyên văn vào prompt).
4. **Nhận kết luận nén** (≤500 từ + trích dẫn nguồn), phiên chính hành động tiếp trên đó —
   KHÔNG paste toàn văn các trang room đã đọc vào phiên chính.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | recovery | room chạm budget B hoặc báo "thiếu: <gì>" | phiên chính quyết: dùng kết luận cắt ngắn, hoặc đọc thẳng vài trang còn thiếu | không mở room con, không mở room thứ hai song song | W04 |

### Validation và stopping
Room dừng khi đọc đủ list hoặc chạm B (circuit breaker tất định theo đếm trang). Kiểm bằng review: kết luận ≤500 từ, mọi khẳng định có trang nguồn, trang stale có cờ. Một câu hỏi = tối đa một room.

### Examples
- **Positive:** phiên dài, hỏi "wiki-core v2 xử lý stale ra sao qua các tier?" → brief 6 trang + 3 hàng xóm (B=12) → một room → kết luận 400 từ trích `concepts/wiki-core-relations.md`, một trang gắn "(stale — kiểm chứng lại trước khi tin)".
- **Boundary/failure:** câu hỏi cần 20 trang, B=12 → room dừng ở trang 12, trả kết luận kèm "đã chạm budget, chưa đọc: <8 trang>"; không mở room con.
- **Boundary:** chỉ cần `concepts/solid-what-how.md` → không mở room, đọc thẳng.

## Origin
- **Source:** concept `wiki-core-relations` §2.4 Tier C + council 020726 guardrail G3/G6
- **Date:** 2026-07-02
