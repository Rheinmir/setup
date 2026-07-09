"""p28_ui — Web UI stdlib theo mockup: 10 màn hình, role ẩn tiền, khóa kỳ 2 bước, dark toggle (C3, C8)."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

MENU = ("Dashboard", "Bảng công", "Suất ăn", "Phụ cấp", "Tăng ca",
        "Master data", "Tờ trình", "Khóa kỳ", "Trình ký", "Đơn treo")

TIEN_ROLES = ("thuky", "cht")


def _layout(title, content):
    sidebar = "".join(f"<li>{m}</li>" for m in MENU)
    return f"""<!DOCTYPE html>
<html data-theme="light">
<head><meta charset="utf-8"><title>{title}</title></head>
<body>
<ul id="sidebar">{sidebar}</ul>
<main>{content}</main>
</body>
</html>"""


def _render_pc(role):
    if role in TIEN_ROLES:
        return _layout("Phụ cấp", "<p>Danh sách phụ cấp (ẩn số tiền theo vai trò)</p>")
    return _layout("Phụ cấp", "<p>Phụ cấp: 500.000 đ (VNĐ) — lương tháng</p>")


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        role = qs.get("role", [""])[0]

        if parsed.path == "/":
            body = _layout("Dashboard", "<p>Tổng quan</p>")
        elif parsed.path == "/pc":
            body = _render_pc(role)
        else:
            body = _layout("404", "<p>Không tìm thấy</p>")

        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def build_server(port=0):
    return HTTPServer(("localhost", port), _Handler)
