---
name: wiki-room
description: "Mở room (subagent 1 tầng) nạp chi tiết wiki khi context phiên chính đã rot — depth cap=1, budget cứng, circuit breaker. Trigger: 'mở room', 'context rot', 'nạp thêm chi tiết wiki', 'đào sâu wiki', '/wiki-room'."
---

# Skill: wiki-room

Tier C của wiki-core v2 (concept `wiki-core-relations`): khi context phiên chính đã dài/rot,
KHÔNG nạp thêm chi tiết vào phiên chính — mở MỘT room (subagent) nạp đầy đủ rồi trả về
kết luận nén. Phiên chính giữ bản đồ (Tier A), chi tiết sống trong room dùng-xong-bỏ.

## When to use
- Phiên chính đã dài (nhiều lần tóm tắt/summarize) mà cần chi tiết sâu từ nhiều trang wiki.
- Câu hỏi cần đọc >3 trang wiki đầy đủ + hàng xóm quan hệ của chúng.
- KHÔNG dùng khi chỉ cần 1-2 trang cụ thể — đọc thẳng rẻ hơn một room (tiêu chí tốc độ).

## Steps
1. **Lập brief Tier A (phiên chính, rẻ):** thu list id trang cần đào — từ câu hỏi + `wiki/index.md`
   + `wiki/stale.json` (trang stale liên quan phải nêu rõ trong brief là "có thể lỗi thời").
2. **Chốt budget TRƯỚC khi mở:** tối đa B trang Tier B (mặc định 12) + hàng xóm quan hệ 1 bước
   (đọc `relations:` frontmatter của các trang trong list — cũng tính vào B).
3. **Mở ĐÚNG MỘT room:** spawn 1 subagent Explore/general-purpose với prompt gồm: câu hỏi, list id,
   budget B, và 3 luật cứng ở mục Rules (chép nguyên văn vào prompt).
4. **Nhận kết luận nén** (≤500 từ + trích dẫn nguồn), phiên chính hành động tiếp trên đó —
   KHÔNG paste toàn văn các trang room đã đọc vào phiên chính.

## Rules (3 luật cứng — chép vào prompt room)
- **Depth cap = 1 (G3):** room KHÔNG được mở room/subagent con dưới bất kỳ lý do gì. Thiếu dữ liệu
  → ghi "thiếu: <gì>" vào kết luận, để phiên chính quyết.
- **Budget cứng:** đọc tối đa B trang. Chạm trần → DỪNG đọc, tổng hợp từ những gì đã có
  (circuit breaker — trả kết quả cắt ngắn kèm ghi chú "đã chạm budget, chưa đọc: <list>").
- **Kết luận nén có nguồn:** mọi khẳng định kèm trang nguồn (`concepts/x.md`); trang nguồn đang
  stale (theo brief) phải ghi kèm cờ "(stale — kiểm chứng lại trước khi tin)".

## Anti-patterns
- Mở nhiều room song song cho một câu hỏi (mất kiểm soát budget tổng) — một câu hỏi, một room.
- Dùng room như trí nhớ dài hạn — room là dùng-xong-bỏ; tri thức đọng lại phải distill vào wiki
  qua `/ingest` hoặc cập nhật trang, không nằm trong transcript room.
- Gọi room khi phiên chính còn ngắn — đọc thẳng luôn nhanh hơn.

## Origin
- **Source:** concept `wiki-core-relations` §2.4 Tier C + council 020726 guardrail G3/G6
- **Date:** 2026-07-02
