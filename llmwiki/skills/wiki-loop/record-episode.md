---
name: record-episode
description: "Ghi một SESSION EPISODE có cấu trúc (tầng nhớ episodic) vào memory store để phiên sau truy hồi được 'phiên trước làm gì' — theo NGỮ NGHĨA, không chỉ theo [[wikilink]]. Bọc mem-rank.py (engine). On-demand, KHÔNG auto-hook (ADR-004). Trigger: 'ghi episode', 'record episode', 'chốt phiên này vào nhớ', 'lưu lại phiên trước làm gì', 'session episode', '/record-episode'."
---

# Skill: record-episode

Tầng nhớ **episodic** cho overstack (4/4 tầng nhớ — working/semantic/procedural/**episodic**).
Wiki giữ tri thức chưng cất (semantic); skill giữ quy trình (procedural); `.claude/memory` giữ
sự thật phẳng. Còn thiếu: *sự kiện phiên cụ thể* — "phiên trước đã làm gì, đụng file nào, kết
quả ra sao". Skill này ghi đúng thứ đó vào `mem-rank` store để phiên sau `query` truy hồi được
theo NGHĨA (không cần ai đặt `[[wikilink]]`).

## When to use
- Cuối một phiên/mốc có ý nghĩa (đóng issue, xong một tính năng, một quyết định) — chốt lại làm gì.
- Khi muốn phiên sau tự nhớ được "việc X đã làm ở đâu, kết quả gì" mà không phải đọc lại git log.
- KHÔNG dùng cho tri thức bền (→ đó là wiki `/ingest`) hay sự thật phẳng người dùng (→ `.claude/memory`).

## Steps
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

## Rules
- **On-demand, KHÔNG auto-hook** — không đăng ký Stop-hook tự ghi (ADR-004: /fdk on-demand only).
- **Episode là sự kiện, không phải tri thức** — nếu nội dung là bài học bền, chưng cất vào wiki qua
  `/ingest`; episode chỉ trỏ "làm ở phiên nào", không thay wiki (wiki vẫn là nguồn chân lý).
- **Store là local/travel-được** — `harness/metrics/memory.jsonl` (đã gitignore); không kéo cloud.
- **Ranker hiện là token-overlap** (tất định); embedding là adapter `mem-rank.config.yaml`
  (`verified:false`) — bật khi có backend, không chặn việc dùng ngay.

## Anti-patterns
- Ghi episode dài như nhật ký — 1 câu `did` + file + outcome là đủ để truy hồi; dài = nhiễu.
- Dùng episode làm nơi lưu quyết định kiến trúc bền — đó là việc của wiki ADR.

## Origin
- **Source:** issue GH#9 (frontier-gap memory, 4/4 tầng nhớ); ledger `030726-memory-episodic-vector.md`.
  Engine: `harness/scripts/mem-rank.py` (episode/retrieve/temporal). Eval: `harness/scripts/mem-proxy.py`.
- **Date:** 2026-07-04
