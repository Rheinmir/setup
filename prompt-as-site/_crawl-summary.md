# Crawl motionsites.ai — báo cáo (110926)

## Kết quả: BỊ CHẶN bởi giới hạn free-tier của site, không lấy được prompt nào trọn vẹn

**Thời điểm chạy:** 2026-09-11 (fork thực thi trong phiên chat của user).

### Đã làm được
- Cuộn hết toàn bộ catalog (infinite scroll, ~700+ site tổng cộng) tới khi xác nhận hết (nội dung lặp lại, không tải thêm).
- Liệt kê đầy đủ **124 site ở trạng thái "Copy prompt" (miễn phí, không khoá)** — danh sách tên đầy đủ ở cuối file này.
- Dựng và xác nhận pipeline trích xuất hoạt động đúng: mở card → bấm "Copy full prompt" → site tự hiện modal fallback chứa `<textarea>` chứa toàn văn prompt (vì clipboard API bị chặn trong môi trường automation) → đọc trực tiếp giá trị textarea → đóng modal → quay lại lưới. Đã thử thành công cơ chế này trên "Playful Idea" và "Interactive Discovery" (xác nhận độ dài prompt lần lượt 30665 và 6894 ký tự).
- Chụp được ảnh đại diện (preview) cho 3 site trước khi bị chặn: Playful Idea, Interactive Discovery, Mostar Guide (file tạm còn trong thư mục screenshot của Claude-in-Chrome, CHƯA di chuyển vào đây vì không có prompt đi kèm — xem mục "Vì sao không có site.md" bên dưới).

### Vì sao KHÔNG có folder site nào được tạo
Site giới hạn số lần "copy prompt" cho khách chưa đăng nhập rất thấp (quan sát được: sau khoảng 2-3 lần bấm "Copy full prompt" trên toàn phiên trình duyệt, kể cả các lần test trong lúc dò cơ chế), site khoá lại với thông báo:

> **Copy without limits** — "You've reached your free copy limit. Create an account or upgrade to keep downloading." kèm nút "Go Unlimited →" / "Create free account".

Giới hạn này áp dụng cho TOÀN BỘ prompt kể cả những cái đã copy trước đó (test lại "Interactive Discovery" — đã copy thành công 1 lần trước — cũng bị chặn lần 2). Trong lúc dò cơ chế (phần lớn ở trong phiên investigate của user trước khi giao việc cho fork này), các lệnh test chỉ in ra ĐỘ DÀI và vài chục ký tự đầu của prompt để tránh đổ nguyên văn dài vào output — nên đến khi quota bị khoá, KHÔNG có bản toàn văn nào của bất kỳ prompt nào được lưu lại được. Kết quả: 0/124 site có đủ (tên + ảnh + prompt) để ghi vào `prompt-as-site/`.

Đã cân nhắc và **chủ động KHÔNG** làm các cách sau vì đi ngược lựa chọn "chỉ lấy free, không cần tài khoản" mà user đã chọn trước đó:
- Không tạo tài khoản / đăng nhập để mở khoá.
- Không dùng cửa sổ ẩn danh, không xoá cookie/localStorage để reset bộ đếm quota (về bản chất là lách giới hạn free-tier của site).

### Đề xuất hướng tiếp theo (cần user quyết định)
1. **Tạo tài khoản miễn phí trên motionsites.ai** — nếu site cho tài khoản free có quota copy cao hơn/không giới hạn, việc còn lại chỉ là đăng nhập rồi chạy lại pipeline đã kiểm chứng (đã có sẵn danh sách 124 tên).
2. **Chấp nhận số lượng rất nhỏ** (2-3 prompt) mỗi lần chạy, cách nhau đủ lâu để quota (nếu theo giờ/ngày) reset — cần xác minh chu kỳ reset trước khi làm.
3. Dừng lại, chỉ dùng danh sách 124 tên site làm tài liệu tham khảo, không crawl prompt/ảnh.

## Danh sách 124 site free tìm được trong catalog (không phân biệt hoa/thường theo tên hiển thị trên site)

Playful Idea, Mostar Guide, Space planet, Vectrus Energy, Agent Grove, Planetary Pulse, Cyber Ronin, Digital Experiences, Digital Epoch, Celestial Renewal, Creative Studio, Bold Studio, DesignPro Academy, No-Code Waitlist, Real-Time Alerts, AI Designer Portfolio, Vision Reveal, Subscription Agency, Northstar, Impact Ventures, CodeNest Coding Platform, Organic Odyssey, Datacore Booking, Quantum Lucid, Vinyl, Duolingo Styleguide, Agent Wave, Interactive Discovery, Aethera Studio, Rare Gallery, Intelligent Operations, Contact Cybernetic, Data Signal, Email Landing Page, Skybridge 404, TrustFlow, Mindloop Landing, Wellness Devicex, Intelligent Performance, Signal ID, Digitwist AI Builder, AI Workflow Agents, Modern Agency, ADHD Planner, Transform Data, Build With Us, Mind-Body Healing, Wellness Balance, SaaS Value, DeepThink, AI Runtime, Innovation, 3D Collectible Hero, Portfolio Cosmic, Stillmind, Quantum Core, Aurex Finance, Fastshot, Neon Logic, Scaling Platform, Creative Portfolio, Growth Decisions, LTX Video, USD Halo, Prosthetics Hero, Talent Collective, Convix Software, Nexora Automation, Neuralyn, Fun 404 Page, SkyElite Private Jets, Dot, TrueEarth, Audio Showcase, Nexto 404, 3D Portfolio, Intelligence Layer, Prisma Creative Studio, PROMPT, Heritage Grove, Asme, Aetheris Voyage, Palomar Labs, Synth Mode, Health Portal, CozyPaws, Visual Hero, Neo Museum, Sentinel AI, Orbis NFT, Cyber Layer, Wellbeing OS, Sparkform, Power AI, RIVR, Wellness Hero, Taskly, Innovation Lab, Stellar AI, 3D Character Studio, Velorah, Retro-Futurist, Immersive Ocean, VEX Ventures, Orbit Flora, Portal, Tech-Forward, Equilibrium, Personal Showcase, Securify Data Security, Digital Director, AI Trip Planner, AI Workflow Hero, Network Hero, Bloom AI, VaultShield, IntelligentX, JungleMind, Luminex, Wanderful Hero, Portal (2), AI Image Generator UI, Email Marketing, Cybersecurity Hero
