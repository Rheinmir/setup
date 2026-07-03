---
type: eval
id: ep-episodic-wire
question: "Phiên nào đã nối episodic + vector retrieval vào tầng nhớ memory layer, và sửa file gì?"
expected_pages: [ep-episodic-wire]
---

# Episodic golden: nối episodic + vector retrieval

Đo TRUY HỒI NGỮ NGHĨA trên tầng nhớ **episodic** (sự kiện phiên), KHÔNG theo `[[wikilink]]`.
Câu hỏi diễn đạt khác nguyên văn episode; ranker token-overlap vẫn phải trả đúng episode
`ep-episodic-wire` trong top-k (hit@k). Sinh output tất định qua `mem-proxy.py` — không gọi model.

## Origin
- Seed issue #9 (frontier-gap memory, 4/4 tầng nhớ). Golden episodic đầu tiên; fixtures ở
  `harness/evals/episodic-fixtures.json`. Cap 30 (case xấu #1 — giữ eval mỏng).
