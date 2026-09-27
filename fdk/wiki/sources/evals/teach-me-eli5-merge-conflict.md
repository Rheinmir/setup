---
type: eval
id: teach-me-eli5-merge-conflict
title: "teach-me ELI5 — git merge conflict cho trẻ 5 tuổi"
input: "ELI5: git merge conflict là gì? Giải thích cho con tôi 5 tuổi."
expected: |
  Kể cho bạn nhỏ nghe nhé, giọng vui thôi.

  Tên gọi: người lớn gọi là đụng nhau khi ghép bài. Mình gọi vui là hai bạn tô trúng một ô.

  Nguồn gốc: chuyện này xuất hiện khi hai người cùng sửa một bức tranh, rồi muốn ghép hai bản lại thành một.

  Lý do tồn tại: tưởng tượng con và bạn cùng tô một trang tô màu. Nếu không có ai nhắc chỗ này hai đứa tô khác nhau, bức tranh ghép lại sẽ lộn xộn mà không ai biết.

  Cơ chế hoạt động: máy ghép hai bản giống như xếp hai tờ giấy chồng lên nhau. Chỗ nào chỉ một bạn tô thì máy giữ luôn. Chỗ nào hai bạn tô khác màu, máy dừng lại và hỏi người lớn chọn màu nào. Mình đã thử cho hai bản sửa cùng một dòng rồi ghép, và máy đúng là dừng lại hỏi thật.

  Trade-off (đổi lại được gì): máy chịu khó hỏi nên không bao giờ tự ý bôi hỏng tranh của ai — bù lại, có lúc con phải dừng chơi một chút để chọn giúp.

  Giới hạn (máy chưa giỏi chỗ nào): máy không tự biết màu nào đẹp hơn; nó chỉ biết hai màu khác nhau và phải nhờ người chọn.

  Vị trí (nằm ở đâu trong trò chơi lớn): bước này ở lúc cuối, khi hai bạn muốn gộp tranh chung thành một bức để treo lên.
asserts:
  - 'regex:(?s)Tên gọi.*Nguồn gốc.*Lý do tồn tại.*Cơ chế hoạt động.*Trade-off.*Giới hạn.*Vị trí'
  - 'regex:(?i)tưởng tượng|giống như|giống hệt|cũng như'
  - 'not-contains:<<<<<<<'
  - 'regex:^(?![\s\S]*\b(?:rebase|HEAD|SHA)\b)'
rubric: "ĐẠT nếu trẻ 5 tuổi (qua lời bố mẹ đọc) hiểu được: câu ngắn, giọng vui không bề trên, một phép so sánh đồ chơi/tranh vẽ/bạn bè xuyên suốt; bảy phần có mặt nhưng không nặng nề. KHÔNG đạt nếu viết như cho người lớn, hay dán output git."
---

# Golden: teach-me-eli5-merge-conflict

Ca người nghe đơn giản nhất. Khung bảy phần vẫn giữ — đây là chỗ dễ vỡ nhất vì "Trade-off", "Giới hạn" là từ người lớn; skill cho phép phụ đề đời thường mà vẫn giữ tên tiêu đề.

## Origin
- Phiên 11/09/2026 — distill [dreambigou/eli5](https://github.com/dreambigou/eli5) (ca `explain-db-index-age5` và `explain-git-merge-5th-grader`) vào `skills/teach-me/SKILL.md`.
