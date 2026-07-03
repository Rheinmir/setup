Version 1.0.6:

- Added `/raise-issue` — ghi lại một issue đầy đủ bối cảnh vào ledger local trong repo (feature-gap, tech-debt, nền tảng, câu hỏi kiến trúc) để bạn hoặc dev khác pull về xử lý ở bất kỳ máy nào qua `/fdk`, không đụng nhánh hay dự án khác. Tự mirror lên tracker remote nếu có (GitHub, GitLab, Gitea) để issue hiện ở tab Issues và assign được người thật, trong khi file ledger vẫn là nguồn chân lý. Khác `/orca-issue` vốn dành cho sự cố/bug (bắt buộc tái hiện trước khi sửa).
- Added `/ovs-notes` — xem release-notes/changelog tức thì: liệt kê các bản (tag + GitHub release) mới nhất trước để chọn đọc, chỉ đọc, không side-effect.
- Added ledger issue local `llmwiki/wiki/sources/ISSUES.md` — một chỗ quét nhanh các issue đang mở, đi theo repo khi clone (không lệ thuộc GitHub).
- Added trang tự-thuật cho overstack: narrative-as-data + code-state self-narration — trang tổng quan giờ suy ra nội dung từ nguồn khai báo thay vì chép tay, nên không lệch âm thầm.
- Added "gương-soi" cuối phiên: khi một phiên có đụng vào framework, hệ tự chạy cổng sức khoẻ và nhắc bạn sửa trước khi kết thúc nếu có gì đỏ.
- Added bản đồ trí-nhớ-phụ (secondary-memory): ghi lại diễn tiến phiên theo session và hiện dạng bản đồ để tra cứu về sau.
- Changed cổng sức khoẻ `medic` — phủ kiểm đủ 17/17 luật (trước chỉ 5–7): mỗi luật được thử "cắn" thật để chứng minh còn hiệu lực, không chỉ giả định.
- Changed `/ovs-notes` sau góp ý: an toàn khi travel sang dự án khác, mặc định lấy nguồn từ framework, và gắn nhãn nguồn rõ ràng.

Known limitations:
- Hai issue vừa raise — mục Foundation phổ quát cho mọi wiki, và phương án orchestration tự-chủ làm Plan B khi không được dùng orca — mới ở trạng thái raise-only: đã ghi đủ bối cảnh nhưng CHƯA thực hiện, cố ý để lại cho phiên `/fdk` kế.
- `medic --ci` còn 1 cảnh báo đã biết: skill `/ovs-notes` chưa được xếp vào nhóm mind-map (chỉ ảnh hưởng cách hiển thị sơ đồ, không ảnh hưởng chức năng).
- narrative-as-data và code-state self-narration đang ở Phase 2 / mức cố-vấn — phủ một phần, chưa bao trọn mọi cơ chế.
