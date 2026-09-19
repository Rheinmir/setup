---
name: record-episode
description: "Ghi một SESSION EPISODE có cấu trúc (tầng nhớ episodic) vào memory store để phiên sau truy hồi được 'phiên trước làm gì' — theo NGỮ NGHĨA, không chỉ theo [[wikilink]]. Bọc mem-rank.py (engine). On-demand, KHÔNG auto-hook (ADR-004). Trigger: 'ghi episode', 'record episode', 'chốt phiên này vào nhớ', 'lưu lại phiên trước làm gì', 'session episode', '/record-episode'."
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: record-episode

Tầng nhớ **episodic** cho overstack (4/4 tầng nhớ — working/semantic/procedural/**episodic**).
Wiki giữ tri thức chưng cất (semantic); skill giữ quy trình (procedural); `.claude/memory` giữ
sự thật phẳng. Còn thiếu: *sự kiện phiên cụ thể* — "phiên trước đã làm gì, đụng file nào, kết
quả ra sao". Skill này ghi đúng thứ đó vào `mem-rank` store để phiên sau `query` truy hồi được
theo NGHĨA (không cần ai đặt `[[wikilink]]`).

## WHAT

### Purpose và context
- **Purpose:** ghi một session episode có cấu trúc (did · files · outcome · session) vào memory store để phiên sau truy hồi "phiên trước làm gì" theo NGỮ NGHĨA, không cần `[[wikilink]]`.
- **Trigger (when to use):**
  - Cuối một phiên/mốc có ý nghĩa (đóng issue, xong một tính năng, một quyết định) — chốt lại làm gì.
  - Khi muốn phiên sau tự nhớ được "việc X đã làm ở đâu, kết quả gì" mà không phải đọc lại git log.
  - User nói "ghi episode", "record episode", "chốt phiên này vào nhớ", "lưu lại phiên trước làm gì", "session episode", `/record-episode`.
- **Non-goals:** KHÔNG dùng cho tri thức bền (→ đó là wiki `/ingest`) hay sự thật phẳng người dùng (→ `.claude/memory`). Không tự chạy qua hook.

### Mental model
`phiên làm việc → did (1 câu) + files + outcome + session → mem-rank.py episode → harness/metrics/memory.jsonl → retrieve --kind-filter episode`. Episode là SỰ KIỆN (episodic), trỏ về phiên; wiki (semantic) vẫn là nguồn chân lý. Sửa episode = supersede có link thời gian, không ghi đè.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | `"<did>"` | có | hành động chính (động từ + đối tượng), đủ term để truy hồi |
| In | `--files` | không | path đụng tới, ngăn cách phẩy (lấy từ `git diff --name-only` nếu cần) |
| In | `--outcome` | không | kết quả kiểm chứng được (test xanh / issue đóng / PR số mấy) |
| In | `--session` | không | tên phiên / issue |
| In | `--id <ID> --supersedes <ID>` | chỉ khi sửa | thay bản cũ, giữ link `supersedes` |
| Out | episode trong `harness/metrics/memory.jsonl` | có | "xong" = `retrieve ... --kind-filter episode` trả lại được episode vừa ghi |

### Rules và capabilities
- RULE-01 (MUST): **On-demand, KHÔNG auto-hook** — không đăng ký Stop-hook tự ghi (ADR-004: /fdk on-demand only).
- RULE-02 (MUST): **Episode là sự kiện, không phải tri thức** — nếu nội dung là bài học bền, chưng cất vào wiki qua `/ingest`; episode chỉ trỏ "làm ở phiên nào", không thay wiki (wiki vẫn là nguồn chân lý).
- RULE-03 (MUST): **Store là local/travel-được** — `harness/metrics/memory.jsonl` (đã gitignore); không kéo cloud.
- RULE-04 (SHOULD): **Ranker hiện là token-overlap** (tất định); embedding là adapter `mem-rank.config.yaml` (`verified:false`) — bật khi có backend, không chặn việc dùng ngay.
- Capabilities: ghi append vào memory store local + truy hồi xếp hạng; không mạng, không hook.

### Failure boundaries
- Nội dung là bài học bền / quyết định kiến trúc → **clarify/redirect** sang `/ingest` hoặc wiki ADR, không ghi episode.
- Không có kết quả kiểm chứng được → ghi `did` + files, bỏ `--outcome` (**partial**), không bịa outcome.
- `retrieve` không trả lại episode vừa ghi → **failed**, báo user, không coi là xong.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | judgment | phiên | Tóm tắt phiên thành 1 câu `did` | câu did | nội dung là tri thức bền → `/ingest` |
| W02 | deterministic | git diff, kết quả test/issue | Thu `--files` + `--outcome` | tham số | không có outcome kiểm được → bỏ trống |
| W03 | effect | did + tham số | `mem-rank.py episode ...` | dòng episode trong store | — |
| W04 | effect | episode cũ sai | Supersede bằng `--id <ID> --supersedes <ID>` (B01) | episode mới + link | — |
| W05 | deterministic | câu hỏi | `mem-rank.py retrieve "<câu hỏi>" --kind-filter episode` | episode hiện trong kết quả | không thấy → failed |

Chi tiết từng bước (nguồn chân lý cho W01–W05):

#### Steps
1. **Tóm tắt phiên thành 1 câu `did`** — hành động chính (động từ + đối tượng), đủ term để truy hồi.
2. **Thu file + kết quả:** `--files` = các path đụng tới (lấy từ `git diff --name-only` nếu cần);
   `--outcome` = kết quả kiểm chứng được (test xanh / issue đóng / PR số mấy).
3. **Ghi episode:**
   ```sh
   python3 harness/scripts/mem-rank.py episode "<did>" \
     --files "path1,path2" --outcome "<kết quả>" --session "<tên/issue>"
   ```
4. **Sửa lại một episode cũ (temporal supersede):** dùng `--id <ID> --supersedes <ID>` — bản mới
   thay bản cũ và giữ link `supersedes` để trả lời "điều này đúng ở thời điểm nào".
5. **Kiểm nhanh:** `python3 harness/scripts/mem-rank.py retrieve "<câu hỏi>" --kind-filter episode`.


#### Anti-patterns
- Ghi episode dài như nhật ký — 1 câu `did` + file + outcome là đủ để truy hồi; dài = nhiễu.
- Dùng episode làm nơi lưu quyết định kiến trúc bền — đó là việc của wiki ADR.


### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | user_optional | cần sửa một episode cũ | ghi bản mới với `--id <ID> --supersedes <ID>` (temporal supersede) | không sửa → skip | W05 |
| B02 | capability_optional | có backend embedding, `mem-rank.config.yaml` `verified:true` | ranker dùng embedding thay token-overlap | chưa có → token-overlap (mặc định) | W05 |

### Validation và stopping
Xong khi W05 truy hồi được episode vừa ghi. Một episode = 1 câu `did` + file + outcome; dài hơn là nhiễu (xem Anti-patterns).

### Examples
- **Positive:** vừa đóng GH#9 → `python3 harness/scripts/mem-rank.py episode "add episodic memory layer to mem-rank" --files "harness/scripts/mem-rank.py" --outcome "GH#9 closed, mem-proxy eval pass" --session "GH#9"` → `retrieve "episodic memory làm ở đâu" --kind-filter episode` trả episode đó.
- **Boundary/failure:** user muốn "ghi episode: quyết định dùng SQLite thay JSONL cho store" → đây là quyết định kiến trúc bền → không ghi episode, chuyển sang wiki ADR / `/ingest`.

## Origin
- **Source:** issue GH#9 (frontier-gap memory, 4/4 tầng nhớ); ledger `030726-memory-episodic-vector.md`.
  Engine: `harness/scripts/mem-rank.py` (episode/retrieve/temporal). Eval: `harness/scripts/mem-proxy.py`.
- **Date:** 2026-07-04
