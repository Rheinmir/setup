"""p28_ui — Web UI stdlib nối THẬT vào payroll_master (p26): Dashboard hiển thị
bảng lương 12 NV thật, role thư ký/CHT ẩn mọi số tiền (C3, C8)."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from app.p26_template2 import payroll_master

MENU = ("Dashboard", "Bảng công", "Suất ăn", "Phụ cấp", "Tăng ca",
        "Master data", "Tờ trình", "Khóa kỳ", "Trình ký", "Đơn treo")

TIEN_ROLES = ("thuky", "cht")
KY_MAC_DINH = "2026-07"


def _layout(title, content):
    sidebar = "".join(f"<li>{m}</li>" for m in MENU)
    return f"""<!DOCTYPE html>
<html data-theme="light">
<head><meta charset="utf-8"><title>{title}</title>
<style>
body{{font-family:-apple-system,sans-serif;margin:0;display:flex}}
#sidebar{{list-style:none;padding:12px;margin:0;width:160px;background:#f0f4fa;min-height:100vh}}
#sidebar li{{padding:6px 8px;font-size:13px}}
main{{padding:20px;flex:1}}
table{{border-collapse:collapse;width:100%;font-size:13px}}
th,td{{padding:6px 10px;border:1px solid #ddd;text-align:right}}
th:first-child,td:first-child{{text-align:left}}
th{{background:#eaf2fd}}
</style></head>
<body>
<ul id="sidebar">{sidebar}</ul>
<main>{content}</main>
</body>
</html>"""


def _tien(so, role):
    if role in TIEN_ROLES:
        return "—"
    return f"{so:,.0f} đ"


def _render_dashboard(role):
    rows = payroll_master(KY_MAC_DINH)
    tr = "".join(
        f"<tr><td>{r['msnv']}</td><td>{r['trang_thai']}</td>"
        f"<td>{_tien(r['luong_thu_viec'], role)}</td>"
        f"<td>{_tien(r['luong_chinh_thuc'], role)}</td>"
        f"<td>{_tien(r['pc_tong'], role)}</td></tr>"
        for r in rows
    )
    return _layout("Dashboard", f"""
<h2>Dashboard kỳ lương {KY_MAC_DINH}</h2>
<p>{len(rows)} nhân viên — tính THẬT từ công thô + hồ sơ + định mức (p06→p19).</p>
<table><tr><th>MSNV</th><th>Trạng thái</th><th>Lương TV</th><th>Lương CT</th><th>PC tổng</th></tr>{tr}</table>
""")


def _render_pc(role):
    rows = payroll_master(KY_MAC_DINH)
    if role in TIEN_ROLES:
        return _layout("Phụ cấp", "<p>Danh sách phụ cấp (ẩn số tiền theo vai trò)</p>")
    tr = "".join(
        f"<tr><td>{r['msnv']}</td><td>{_tien(r['pc_com'], role)}</td>"
        f"<td>{_tien(r['pc_dien_thoai'], role)}</td><td>{_tien(r['pc_tong'], role)}</td></tr>"
        for r in rows
    )
    return _layout("Phụ cấp", f"""
<h2>Bảng phụ cấp {KY_MAC_DINH}</h2>
<table><tr><th>MSNV</th><th>PC cơm</th><th>PC điện thoại</th><th>Tổng</th></tr>{tr}</table>
""")


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        role = qs.get("role", [""])[0]

        if parsed.path == "/":
            body = _render_dashboard(role)
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
