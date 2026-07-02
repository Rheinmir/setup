# Council Transcript

_council.py/1.0 - DETERMINISTIC artifact (seed `42`)._

**Question:** <the question put to the council>

## Stage 1 - First Opinions

| Author (seat) | Blind label | Answer |
|---------------|-------------|--------|
| linus | A | Cái 'skill' query là một file text KHÔNG LÀM GÌ. Đừng viết framework eval cho một tính năng chưa tồn tại. Viết cái tool đi: ripgrep trên index.md làm tầng-1, Read làm tầng-2, wikilinks làm tầng-3 — 50 dòng, hôm nay THẤY nó chạy. Nhân tiện nhét logging vào luôn (rẻ, thật, debug được). RỒI, khi đã có tool thật đẻ ra output thật, mới dựng eval chấm nó. Đo hơi nước là quan liêu. C là rác ma thuật — một hook nhồi context mọi lượt thì không click được, không debug được, phình mọi request. Thứ tự: B(+telemetry) trước, A sau khi đã có cái để đo. |
| meadows | B | Hệ thống KHÔNG có vòng phản hồi — đó mới là khiếm khuyết gốc, sâu hơn 'query chỉ là prose'. Bạn không thể lái một hệ open-loop; mọi thay đổi là phỏng đoán không bao giờ được hiệu chỉnh. Telemetry + baseline truy-hồi lắp đúng cái cảm biến đang thiếu và ĐÓNG vòng lặp — đòn bẩy cao nhất. Thêm một L1 tool bóng bẩy TRƯỚC khi vòng lặp tồn tại chỉ khiến một hệ mù chạy nhanh hơn. Đặt cảm biến trước (A + telemetry), RỒI cải tiến tool với vòng lặp đang quan sát. C dời can thiệp sang sai chỗ (thượng nguồn suy nghĩ của model) và thêm một chi phí vĩnh viễn. Thứ tự: A → B, vòng lặp trước. |
| munger | C | Nghịch đảo — cái gì ĐẢM BẢO thất bại? Hai đường. Một: ship retrieval bóng bẩy (B) không đồng hồ đo, thấy năng suất, âm thầm hồi quy, không bao giờ biết — chết vì drift không đo. Hai: mạ vàng eval thành dự án nghiên cứu, không bao giờ ship tool — chết vì tê liệt phân tích. Tránh cả hai: telemetry GẦN-NHƯ-FREE trước (một dòng log), một eval truy-hồi TỐI THIỂU (vài chục golden), RỒI L1. C thất bại kiểu thứ ba: nhồi context mọi lượt đảm bảo phình + ô nhiễm — nghịch đảo của 'để model tự hỏi cái nó cần'. Thứ tự: telemetry+eval-mỏng (A) → B; C bét bảng. |
| taleb | D | Via negativa. Nước đi rẻ nhất và bền nhất là CÁI CẢM BIẾN, không phải tính năng. Baseline + telemetry là bảo hiểm: đó là cách bạn PHÁT HIỆN một thay đổi 'khôn ngoan' đã âm thầm đầu độc recall. Xây mà không có nó thì mọi cải tiến là đức tin. C là bẫy mong manh: prefetch-inject trả thuế token MỌI lượt và ép content lên model dù model không hỏi — rủi ro đuôi đầu độc context, đúng mùi wholesale đã bị loại 3.89. Giết C. Nhưng cũng đừng xây eval quá béo — một eval mạ vàng tự nó là một mong manh khác. Baseline mỏng, rồi mới tool. Thứ tự: A(mỏng)→B, C không bao giờ. |
| karpathy | E | Trong ML không ai ship một tối ưu mà không có metric — nhưng ở đây metric RẺ và retrieval thì đúng nghĩa đang ở 0. Làm cả hai trong một vòng chặt: dựng eval truy-hồi TỐI THIỂU (20-30 cặp câu-hỏi→trang-đúng, chấm recall@k + token) VÀ nâng L1 tool, nhưng LAND eval trước để commit đầu tiên của tool đã có một con số. Bỏ L2: inject context mù là RAG thời tiền-attention, nó ĐÁNH NHAU với khả năng tự truy hồi của model. Telemetry là một phần của A — log mỗi query trúng trang nào + tốn token, đó chính là tín hiệu học. Đừng mạ vàng eval: 30 golden dogfood ăn đứt 300 golden lý thuyết. Thứ tự: A(mỏng) → B, đo B trên nền A. |

## Stage 2 - Review (blind peer-rank)

### Anchor guard

Seed `42`. Each judge was shown the blind answers in this order (position-bias guard).

| Judge | Presentation order |
|-------|--------------------|
| seat-1 | C -> E -> D -> B -> A |
| seat-2 | B -> D -> A -> C -> E |
| seat-3 | A -> C -> B -> D -> E |

### Judge rankings (best first)

| Judge | Ranking (blind) |
|-------|-----------------|
| seat-1 | E > C > D > B > A |
| seat-2 | A > E > C > D > B |
| seat-3 | E > C > D > B > A |

### Mean-rank consensus

| Consensus | Author | Blind | Mean rank | Judge ranks |
|-----------|--------|-------|-----------|-------------|
| 1 | karpathy | E | 1.333333 | [1, 2, 1] |
| 2 | munger | C | 2.333333 | [2, 3, 2] |
| 3 | taleb | D | 3.333333 | [3, 4, 3] |
| 4 | linus | A | 3.666667 | [5, 1, 5] |
| 5 | meadows | B | 4.333333 | [4, 5, 4] |

**Consensus winner:** karpathy (blind E, mean rank 1.333333).

### Dissent - where the judges disagree most

**Most contested:** linus (blind A) - ranks [5, 1, 5], variance 3.555556.

| Author | Blind | Ranks | Range | Variance |
|--------|-------|-------|-------|----------|
| linus | A | [5, 1, 5] | 4 | 3.555556 |
| meadows | B | [4, 5, 4] | 1 | 0.222222 |
| munger | C | [2, 3, 2] | 1 | 0.222222 |
| taleb | D | [3, 4, 3] | 1 | 0.222222 |
| karpathy | E | [1, 2, 1] | 1 | 0.222222 |

## Stage 3 - Final Response (chairman brief)

Synthesize ONE final answer. Lead with the consensus winner, fold in unique correct points from the others, and explicitly resolve the contested answer(s) below rather than averaging them away.

Consensus order to lead with:
- 1. karpathy (mean rank 1.333333)
- 2. munger (mean rank 2.333333)
- 3. taleb (mean rank 3.333333)
- 4. linus (mean rank 3.666667)
- 5. meadows (mean rank 4.333333)

Must explicitly resolve:
- linus - split ranks [5, 1, 5] (variance 3.555556)
- meadows - split ranks [4, 5, 4] (variance 0.222222)
- munger - split ranks [2, 3, 2] (variance 0.222222)
- taleb - split ranks [3, 4, 3] (variance 0.222222)
- karpathy - split ranks [1, 2, 1] (variance 0.222222)

_chairman_synthesis: pending (produced by the chairman model via orca orchestration)._

