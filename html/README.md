# Visual Documentation Library

Thư mục này chứa các tài liệu kỹ thuật đã được render từ định dạng Markdown (.md) sang HTML chất lượng cao.

## Thành phần
- **`index.html`**: Dashboard chính để duyệt và tìm kiếm tài liệu.
- **`*.html`**: Các bản render đơn lẻ của các concept, entities hoặc reports.

## Cách sử dụng
Để xem thư viện một cách trực quan, hãy chạy lệnh host từ thư mục gốc của dự án:

```bash
./commands/serve <port>
```

Mặc định server sẽ chạy tại `http://localhost:8000` (hoặc port bạn chỉ định).

## Quy trình cập nhật
Các file trong này được sinh tự động bởi AI Agent thông qua kỹ năng `md-to-html`. Khi có thay đổi lớn trong Wiki hoặc Raw, hãy yêu cầu Agent render lại bản mới để đảm bảo tính cập nhật.

## Supported Visualizations
Hệ thống sử dụng **Chart.js** và **Mermaid.js** để trực quan hóa dữ liệu:
- **Bar Chart**: So sánh tài nguyên giữa các node.
- **Line Chart**: Theo dõi xu hướng (uptime, load average).
- **Pie/Doughnut**: Phân bổ dung lượng lưu trữ hoặc RAM.
- **Radar Chart**: Đánh giá hiệu năng tổng thể của node (CPU/RAM/IO/Net).
- **Mermaid Flowchart**: Quy trình triển khai Ansible/Cloud-Init.
- **Mermaid Graph**: Sơ đồ kiến trúc mạng Tailscale.

Sử dụng class `.viz-container` và `.chart-wrapper` trong HTML để đảm bảo biểu đồ hiển thị đúng chuẩn "Premium Dark".
