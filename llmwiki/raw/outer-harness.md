Outer Harness: Tại sao Process và Data quan trọng hơn Agent
Mỗi ngày không có Outer Harness là một ngày bạn tích thêm nợ kỹ thuật mà không ai đo được. Context thì phân mảnh, cost thì mù mờ, incident thì không trace nổi.
Phúc
Apr 12, 2026




Vấn đề
Công ty bạn có 500 engineer, mỗi người chạy 5–10 agent sessions/ngày với Claude Code, Cursor, hoặc Codex. Mỗi session đốt token, sinh code, push thẳng vào repo.

Bây giờ thử trả lời mấy câu này:

Tháng này team tốn bao nhiêu tiền API, chia theo dự án ra sao?

Agent vừa commit code vi phạm security policy, ai chịu trách nhiệm?

Cái migration làm sập staging sáng nay, ai approve nó?

Agent của team A viết code tốt hơn hay tệ hơn team B?

Senior dev vừa nghỉ, 6 tháng prompt engineering kinh nghiệm giờ ở đâu?

Nếu bạn lắc đầu với hầu hết, bạn không đơn độc. Đây không phải lỗi của AI, cũng không phải lỗi của team. Đây là lỗi kiến trúc: chúng ta đang thiếu một lớp hạ tầng mà chưa ai đặt tên cho nó rõ ràng.

Harness
LangChain đúc kết gọn lỏn: Agent = Model + Harness. Mọi thứ không phải model (system prompt, context files, skills, sensors, hooks, orchestration) đều là Harness.

Nghe thì trừu tượng, nhưng bạn đã sờ vào harness hằng ngày rồi:

Context files: file CLAUDE.md, coding standards, security policies mà bạn nhét vào đầu prompt

Skills: những prompt template bạn hay copy lại mỗi lần cần review code hay viết migration

Sensors: lúc bạn bảo agent “chạy lint rồi sửa trước khi trả kết quả”, đó chính là sensor

Hooks: script chạy before/after mỗi agent run

Sandbox: môi trường cách ly để agent thực thi code an toàn

Nhưng có một điều mà ít ai dừng lại để nghĩ: sandbox do Anthropic xây, còn file CLAUDE.md là bạn ngồi viết lúc 11 giờ đêm tuần trước. Hai thứ này hoàn toàn khác nguồn gốc, khác người sở hữu, khác vòng đời. Vậy mà chúng ta đang nhét chung vào một rổ gọi là “cấu hình agent”.

Inner vs. Outer Harness
Trong kỹ thuật ô tô, “wiring harness” chia thành inner harness (dây cáp hàn cố định trong engine block, đừng đụng vào) và outer harness (dây nối tùy biến ra dashboard, sensors, phụ kiện, thay đổi tùy mẫu xe). AI agent cũng có lằn ranh tương tự:




Inner là phần Anthropic, OpenAI, Cursor đã đổ hàng chục triệu đô để tối ưu. Bạn không cần và không nên rebuild. Cứ để họ lo.

Muốn thấy Inner Harness chuẩn mực nhất trông như thế nào? Cách đây vài tuần, source code của Claude Code bị leak. Community lập tức mổ xẻ và gần như đồng thuận: đây là ví dụ tiên phong nhất về thiết kế Inner Harness, và nhiều người đã reverse engineering để tạo ra phiên bản của riêng mình.

Nhưng hãy để ý điều này: toàn bộ thứ được khen ngợi đó đều thuộc Inner Harness. Không có gì trong đó nói về cách tổ chức của bạn phân phối context theo tầng, kiểm soát ngân sách API, hay trace incident khi production sập. Đó là Outer, và Anthropic không thể, cũng không có lý do gì để xây thay bạn phần đó.

Outer là phần mang DNA của tổ chức bạn: context doanh nghiệp, quy trình phê duyệt, tiêu chuẩn chất lượng, cách chia sẻ tri thức giữa các team. Provider sẽ không bao giờ làm thay phần này, vì họ không biết công ty bạn hoạt động ra sao.

Và đây là nghịch lý: hầu hết tổ chức đang chi hàng trăm ngàn đô cho Inner (token fees), trong khi Outer, thứ thực sự quyết định chất lượng output, thì nằm rải rác trên laptop từng người. Khi scale lên 50, 200, 1000 engineer, nó vỡ.

Khi xây Outer Harness, có hai mindset quan trọng hơn mọi quyết định kỹ thuật:

Process-centric: Đừng xây hệ thống xoay quanh con người (”nhớ paste policy nhé”) hay xoay quanh agent (”nó thông minh, kệ nó”). Quy trình là xương sống. Human và Agent đều là node trên cùng một pipeline, ai cắm vào cũng phải chạy đúng luồng.

Data-driven: Mọi thao tác phải sinh ra structured data. Không có data thì không có visibility, không có visibility thì không improve được. Đơn giản vậy thôi.

5 trụ cột của Outer Harness
1. Cost Attribution
Vấn đề: Hóa đơn API cuối tháng: $180K. CFO hỏi “tiền đi đâu?”, bạn chỉ biết trả lời “Anthropic”. Break down theo team? Theo feature? Theo con agent nào đốt nhiều nhất? Không thể.

Giải pháp: Log mọi agent run kèm đầy đủ metadata: agent nào, task nào, project nào, model nào, bao nhiêu input/output tokens, cost bao nhiêu.




Khi data đủ mịn, chuyện thú vị bắt đầu xảy ra: hệ thống tự phát hiện agent X đang đốt gấp 3 lần bình thường → alert ngay. Vượt budget ceiling → hard stop, không cần ai can thiệp. Đây là data-driven cost control, thay vì cuối tháng mở bill ra rồi thở dài.

2. Multi-layer Knowledge Flow
Vấn đề: Agent vi phạm security policy vì engineer quên paste compliance doc vào prompt. Nghe quen không? Tuần sau, senior dev nghỉ việc. 6 tháng kinh nghiệm prompt engineering bay theo người.

Hai vấn đề tưởng khác nhau nhưng có chung gốc rễ: context và skills đang sống trên máy cá nhân thay vì trên hệ thống.

Giải pháp: Context hierarchy 5 tầng với ownership rõ ràng ở mỗi tầng:




Hệ thống chạy theo hai chiều:

Top-down: CTO update security policy ở Layer 1 một lần → mọi agent tự động kế thừa. Không ai cần “nhớ” copy-paste. Không ai có thể bypass.

Bottom-up: Bạn vừa craft được một prompt xử lý migration cực ngon ở Layer 5? Đóng gói nó thành Skill, promote lên Layer 3, cả team dùng được ngay qua fetch_skill. Tri thức cá nhân trở thành tài sản chung.

Senior dev nghỉ? Skills vẫn ở đây. Engineer mới vào kế thừa ngay ngày đầu, không cần ai ngồi “truyền nghề” 2 tuần.

Đây là process-centric governance: quy trình tự động phân phối tri thức từ trên xuống, đồng thời mở xa lộ đóng góp từ dưới lên. Không phụ thuộc vào sự chăm chỉ hay trí nhớ của bất kỳ cá nhân nào.

3. Task Tracking
Vấn đề: Agent chạy migration, staging sập. Ai approve? Khi nào? Dựa trên tiêu chí gì? Câu trả lời thường là: “Để tìm lại thread Slack...”, và ai cũng biết thread đó sẽ không bao giờ được tìm lại.

Giải pháp: Task lifecycle tracking + approval gates với audit trail đầy đủ:




Mỗi task có trạng thái rõ ràng. Mỗi approval gắn liền người, thời điểm, lý do. Khi incident xảy ra, bạn trace ngược được toàn bộ: agent nào chạy, ai approve, context version nào, cost bao nhiêu. Data-driven incident response, thay vì mở Slack rồi scroll đến mỏi tay.

4. Quality Gates
Vấn đề: “Agent đã biết TDD rồi, tự chạy test tự sửa. Cần gì quality gate ở Outer?”

Câu hỏi rất hợp lý. Nhưng câu trả lời là: vẫn cần, vì Separation of Duties.

Inner Harness cho agent khả năng tự sửa lỗi (TDD loop), và nó làm việc này khá tốt. Nhưng hãy nghĩ kỹ: agent cũng hoàn toàn có thể comment-out một test case khó để pass nhanh hơn. Hoặc đơn giản là nó không biết rằng org bạn yêu cầu SonarQube scan, hay minimum coverage phải ≥ 80%.

Nguyên tắc cơ bản: kẻ viết code không nên là kẻ duy nhất judge code của chính mình. Quality Gates ở Outer Harness đóng vai trò hệ miễn dịch độc lập, tách biệt hoàn toàn khỏi agent:




Process: Agent output bắt buộc đi qua pipeline chất lượng do org quy định. Không bypass được.

Data: Mỗi lần gate chạy, kết quả được log. Tích lũy đủ lâu, bạn bắt đầu trả lời được những câu hỏi hay ho: “Claude hay GPT viết code ít bug hơn cho codebase của mình? Team Frontend đang improve hay degrade theo thời gian?”

5. Audit &amp; Analytics
4 trụ cột trên, nếu chạy đúng, sẽ sinh ra một lượng data rất lớn. Trụ cột thứ 5 là nơi data đó hội tụ và thực sự phát huy giá trị.

Audit Log ghi lại mọi biến đổi trong hệ thống (task status change, context edit, approval decision, gate result, cost event) dưới dạng append-only. Không sửa, không xóa. Với hash chain (mỗi record = hash của record trước + payload hiện tại), bạn có tamper-evidence, tức bằng chứng chống giả mạo ở cấp hệ thống.




Khi 4 trụ cột kia chạy đúng, trụ cột 5 bắt đầu trả lời những câu hỏi mà trước đây chẳng ai trả lời nổi:

Agent nào quality score cao nhất với cost thấp nhất?

Skill nào được reuse nhiều nhất và thực sự tiết kiệm thời gian?

Team nào đang improve, team nào đang đi xuống?

Khi incident xảy ra: chính xác ai, khi nào, context gì, approve như thế nào?

Đây là điểm hội tụ của data-driven: dữ liệu không chỉ để audit cho compliance. Nó trở thành cơ sở cho mọi quyết định chiến lược về AI trong tổ chức.

Kết
Model sinh output. Inner Harness giữ execution an toàn. Nhưng Outer Harness mới là thứ quyết định output đó có thực sự phục vụ tổ chức hay không:

Output có đúng context không → Multi-layer Knowledge Flow

Tốn bao nhiêu tiền, ai chịu → Cost Attribution

Ai approve, có trace được không → Task Tracking

Chất lượng có đạt chuẩn org không → Quality Gates

Data có được ghi lại để học từ đó không → Audit &amp; Analytics

Hai nguyên tắc xây dựng:

Process-centric. Human và Agent đều là node trên cùng một pipeline. Quy trình quyết định context nào được inject, output nào được approve, gate nào phải pass. Không phải human quyết đoán, không phải agent tự phán. Process quyết.

Data-driven. Mọi thao tác sinh structured data. Cost Attribution cho data về tiền. Quality Gates cho data về chất lượng. Audit Log giữ mọi thứ immutable. Không có data thì không có visibility, không có visibility thì mãi mãi đoán mò.

Mỗi ngày không có Outer Harness là một ngày bạn tích thêm nợ kỹ thuật mà không ai đo được. Context thì phân mảnh, cost thì mù mờ, incident thì không trace nổi. Sự khác biệt giữa tổ chức dùng AI hiệu quả và tổ chức chỉ đang “có AI” nằm ở chỗ: họ đã biến Outer Harness từ thói quen cá nhân thành hạ tầng chung. Nếu bạn chưa bắt đầu, thời điểm rẻ nhất là hôm nay.

Subscribe to Phúc’s Words
Launched 2 years ago
Chỗ viết dài của Phúc
Type your email...
Subscribe
By subscribing, you agree Substack's Terms of Use, and acknowledge its Information Collection Notice and Privacy Policy.
36 Likes
∙
7 Restacks
Discussion about this post
Write a comment...
linhvuquach
Apr 17

useful content, thanks bro

Like
Reply
Share

Context Engineering: Từ Vibe Coder Đến AI Orchestrator
Vibe Coder thì prompt rồi hy vọng. AI Orchestrator thì tạo ra một hệ sinh thái để AI hoạt động hiệu quả.
Aug 27, 2025 • Phúc

52

3

6


AI Coding: Từ "Vibe Coding" đến Chuyên Nghiệp
Hành trình với AI cũng giống như làm việc với con người – cần kế hoạch, cần phối hợp, và cần cả sự kiên nhẫn.
Jun 7, 2025 • Phúc

47

5

16


Symbol-based Analysis: Kỹ thuật giúp AI hiểu code như con người
Thay vì xử lý code như văn bản thuần túy, Symbol-based Analysis hiểu code như những entities có nghĩa với structure và relationships rõ ràng.
Aug 2, 2025 • Phúc

17

1

1


Ready for more?
Type your email...
Subscribe
© 2026 Nguyễn Trọng Phúc · Privacy ∙ Terms ∙ Collection notice
Start your Substack
Get the app
Substack is the home for great culture
