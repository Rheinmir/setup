# Council - Blind Review Packet (Stage 2 setup)

**Question:** <the question put to the council>

## Blind answers (identities stripped)

| Label | Answer |
|-------|--------|
| A | 'ALWAYS render HTML' nhiều khả năng do effort-justification / IKEA effect — vừa xây docs-site-macos xong nên nhìn đâu cũng thấy đinh. Cộng planning-fallacy: mỗi run tốn thêm token+thời-gian. Nhưng phần blind-vote CÓ giá trị nhận thức thật: cho người đọc thấy phiếu ẩn danh A/B/C TRƯỚC khi reveal ai-là-ai = debias người đọc, đúng bài. Vấn đề là chữ 'ALWAYS' bỏ qua base-rate: đa số council là check nội bộ nhanh. Kết luận: section blind-vote-reveal đáng giữ; 'ALWAYS' mới là cái bias cần bỏ. |
| B | Optionality. Một bước HTML bắt buộc thêm fragility — thêm một thứ để hỏng (coupling docs-site), một dependency có thể mục. transcript.json mới là lõi robust; HTML là trang trí. Nhưng payoff lồi: debate-room chat có thể phơi bày một bất đồng thảm họa mà md phẳng giấu đi — dissent table làm cho thành visceral. Giữ lõi transcript deterministic là bất khả xâm phạm; để HTML là option rẻ, gỡ-được. KHÔNG BAO GIỜ ép trang trí thành bắt buộc. Kết luận: đáng giá khi opt-in, có hại khi 'ALWAYS'. |
| C | Nghịch đảo: cái gì ĐẢM BẢO council thất bại? Không ai đọc output, hoặc không tin nó. HTML đẹp không sửa được lòng tin — transcript.md đã tồn tại và audit được. Rủi ro: 'ALWAYS render' biến docs-site-macos thành một dependency phải bảo trì, và là solution đi tìm problem. NHƯNG nếu debate thực sự được người ngoài kỹ thuật (stakeholder) tiêu thụ, một artifact đọc-được là chính đáng. Kết luận: CẦN chỉ khi output chia sẻ ra ngoài người vận hành; còn lại là over-engineering. Giữ optional, đừng ép ALWAYS. |

## Anchor guard - per-judge presentation order

Seed: `42`. Show each judge its answers in THIS order to cancel position bias.

| Judge | Show in this order |
|-------|--------------------|
| seat-1 | B -> C -> A |
| seat-2 | A -> B -> C |
| seat-3 | A -> B -> C |

Hand each judge its blind answers in its row's order; collect a ranking of the labels (best first) into judges.json, then re-run `council.py rank ... --judges judges.json`.

