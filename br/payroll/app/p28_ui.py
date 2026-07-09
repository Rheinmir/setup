"""p28_ui — Web UI stdlib nối THẬT vào toàn bộ engine p06-p27: 10 route thật
(trước đó chỉ 2/10 có route — nợ do sửa tay ngoài /br run, feedback user 09/07),
role thư ký/CHT ẩn mọi số tiền (C3, C8)."""
import csv
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from app.p03_dinhmuc import DIEN_THOAI_TABLE
from app.p06_workday import cong_tho
from app.p07_kyhieu import phan_loai
from app.p12_suatan import tong_hop_suat_an
from app.p22_khoaky import is_locked, khoa_ky
from app.p25_template0 import bang_trinh_ky, _toan_bo_msnv
from app.p26_template2 import payroll_master
from app.p27_baocao_hr import don_treo
from app.p29_import import validate_and_import
from app.p30_formula_engine import FIELDS, bang_luong_day_du

MENU_ROUTES = (
    ("/", "Dashboard"),
    ("/cong-thuc", "Công thức lương"),
    ("/bang-cong", "Bảng công"),
    ("/suat-an", "Suất ăn"),
    ("/pc", "Phụ cấp"),
    ("/tang-ca", "Tăng ca"),
    ("/master-data", "Master data"),
    ("/to-trinh", "Tờ trình"),
    ("/khoa-ky", "Khóa kỳ"),
    ("/trinh-ky", "Trình ký"),
    ("/don-treo", "Đơn treo"),
)
MENU = tuple(ten for _, ten in MENU_ROUTES)

TIEN_ROLES = ("thuky", "cht")
KY_MAC_DINH = "2026-07"
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "br", "data-draft")


def _doc_csv(ten_file):
    with open(os.path.join(_DATA_DIR, ten_file), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _layout(title, content, path="/"):
    items = "".join(
        f'<li><a class="{"on" if p == path else ""}" href="{p}">{ten}</a></li>'
        for p, ten in MENU_ROUTES
    )
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{title}</title>
<script>(function(){{try{{var t=localStorage.getItem("payroll-theme");
if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}}})();</script>
<style>
:root{{--bg:#fff;--ink:#223;--side:#f0f4fa;--border:#ddd;--th:#eaf2fd;--accent:#0a84ff}}
html[data-theme=dark]{{--bg:#12181f;--ink:#e3e8ee;--side:#1a2129;--border:#2b3440;--th:#1c2833}}
@media(prefers-color-scheme:dark){{html:not([data-theme=light]){{--bg:#12181f;--ink:#e3e8ee;--side:#1a2129;--border:#2b3440;--th:#1c2833}}}}
body{{font-family:-apple-system,sans-serif;margin:0;display:flex;background:var(--bg);color:var(--ink)}}
#sidebar{{list-style:none;padding:12px;margin:0;width:170px;background:var(--side);min-height:100vh;display:flex;flex-direction:column}}
#sidebar li{{padding:2px 0}}
#sidebar a{{display:block;padding:6px 8px;font-size:13px;color:inherit;text-decoration:none;border-radius:6px}}
#sidebar a:hover{{background:rgba(10,132,255,.12)}}
#sidebar a.on{{background:var(--accent);color:#fff}}
.theme-row{{margin-top:auto;padding-top:12px;border-top:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;font-size:12px}}
.theme-switch{{width:36px;height:20px;border-radius:99px;background:var(--border);cursor:pointer;position:relative;border:0}}
.theme-switch .knob{{position:absolute;top:2px;left:2px;width:16px;height:16px;border-radius:50%;background:#fff;transition:left .18s}}
.theme-switch.on{{background:var(--accent)}}
.theme-switch.on .knob{{left:18px}}
main{{padding:20px;flex:1;max-width:900px}}
table{{border-collapse:collapse;width:100%;font-size:13px;margin-top:10px}}
th,td{{padding:6px 10px;border:1px solid var(--border);text-align:right}}
th:first-child,td:first-child{{text-align:left}}
th{{background:var(--th)}}
.badge{{display:inline-block;padding:2px 8px;border-radius:99px;font-size:11px}}
.badge.ok{{background:#dcf5e3;color:#1a7a34}}
.badge.warn{{background:#fdf0d5;color:#a16207}}
form{{margin-top:14px;padding:14px;border:1px solid var(--border);border-radius:8px;max-width:360px}}
label{{display:block;margin:8px 0 3px;font-size:12px}}
input,button,textarea{{font:inherit;padding:6px}}
input[type=text],textarea{{width:100%;background:var(--bg);color:var(--ink);border:1px solid var(--border)}}
button{{margin-top:10px;background:var(--accent);color:#fff;border:0;border-radius:6px;padding:8px 14px}}
</style></head>
<body>
<ul id="sidebar">{items}<li class="theme-row"><span>Giao diện</span>
<button class="theme-switch" id="theme-switch" role="switch" aria-label="Đổi sáng/tối"><span class="knob"></span></button>
</li></ul>
<main>{content}</main>
<script>
(function(){{var K="payroll-theme",d=document.documentElement,sw=document.getElementById("theme-switch");
function isDark(){{var t=d.getAttribute("data-theme");return t?t==="dark":matchMedia("(prefers-color-scheme: dark)").matches}}
function paint(){{var dk=isDark();sw.classList.toggle("on",dk);sw.setAttribute("aria-checked",dk?"true":"false")}}
sw.addEventListener("click",function(){{var n=isDark()?"light":"dark";d.setAttribute("data-theme",n);try{{localStorage.setItem(K,n)}}catch(e){{}}paint()}});
paint();
}})();
</script>
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
""", "/")


def _render_bang_cong(role):
    rows = cong_tho(KY_MAC_DINH)
    theo_nv = {}
    for r in rows:
        theo_nv.setdefault(r["msnv"], []).append(r)
    tr = ""
    for msnv, du_lieu in sorted(theo_nv.items()):
        cong = sum(1 for r in du_lieu if phan_loai(r["ky_hieu"])["lam_viec_thuc_te"])
        tr += f"<tr><td>{msnv}</td><td>{len(du_lieu)}</td><td>{cong}</td></tr>"
    return _layout("Bảng công", f"""
<h2>Bảng chấm công kỳ {KY_MAC_DINH}</h2>
<p>Nguồn: công thô Workday (p06) — thư ký/CHT chỉ thấy NGÀY CÔNG, không thấy tiền (C3).</p>
<table><tr><th>MSNV</th><th>Số dòng công thô</th><th>Ngày làm việc thực tế</th></tr>{tr}</table>
""", "/bang-cong")


def _render_suat_an(role):
    rows = payroll_master(KY_MAC_DINH)
    tr = ""
    for r in rows:
        suat = tong_hop_suat_an(r["msnv"], KY_MAC_DINH)
        tong_suat = sum(bp["tong"] for bp in suat.values())
        tr += f"<tr><td>{r['msnv']}</td><td>{tong_suat:.0f}</td><td>{_tien(r['pc_com'], role)}</td></tr>"
    return _layout("Suất ăn", f"""
<h2>Suất ăn kỳ {KY_MAC_DINH}</h2>
<table><tr><th>MSNV</th><th>Tổng suất</th><th>Thành tiền</th></tr>{tr}</table>
""", "/suat-an")


def _render_pc(role):
    rows = payroll_master(KY_MAC_DINH)
    if role in TIEN_ROLES:
        return _layout("Phụ cấp", "<p>Danh sách phụ cấp (ẩn số tiền theo vai trò)</p>", "/pc")
    tr = "".join(
        f"<tr><td>{r['msnv']}</td><td>{_tien(r['pc_com'], role)}</td>"
        f"<td>{_tien(r['pc_dien_thoai'], role)}</td><td>{_tien(r['pc_tong'], role)}</td></tr>"
        for r in rows
    )
    return _layout("Phụ cấp", f"""
<h2>Bảng phụ cấp {KY_MAC_DINH}</h2>
<table><tr><th>MSNV</th><th>PC cơm</th><th>PC điện thoại</th><th>Tổng</th></tr>{tr}</table>
""", "/pc")


def _render_tang_ca(role):
    rows = _doc_csv("ot_multiplier.csv")
    tr = "".join(
        f"<tr><td>{r['loai_ngay']}</td><td>{r['chinh_thuc_pct']}%</td>"
        f"<td>{r['mat_bao_pct']}%</td><td>{r['nghi_bu_ngay']}</td></tr>"
        for r in rows
    )
    return _layout("Tăng ca", f"""
<h2>Cấu hình hệ số tăng ca (ot_multiplier.csv)</h2>
<table><tr><th>Loại ngày</th><th>Chính thức</th><th>Mắt Bão</th><th>Nghỉ bù</th></tr>{tr}</table>
""", "/tang-ca")


def _render_master_data(role, thong_bao=None):
    tr = "".join(
        f"<tr><td>{ngach}</td><td>{gia['CT']:,} đ</td><td>{gia['VP']:,} đ</td></tr>"
        for ngach, gia in DIEN_THOAI_TABLE.items()
    )
    bp = "".join(
        f"<tr><td>{r['bo_phan']}</td><td>{r['tinh']}</td><td>{r['khoi']}</td></tr>"
        for r in _doc_csv("dm_bo_phan.csv")
    )
    thong_bao_html = f'<p class="badge {"ok" if thong_bao[0] else "warn"}">{thong_bao[1]}</p>' if thong_bao else ""
    return _layout("Master data", f"""
<h2>Định mức điện thoại (p03)</h2>
<table><tr><th>Ngạch</th><th>Công trường</th><th>Văn phòng</th></tr>{tr}</table>
<h2>Bộ phận (dm_bo_phan.csv)</h2>
<table><tr><th>Bộ phận</th><th>Tỉnh</th><th>Khối</th></tr>{bp}</table>
<h2>Import nhân viên (CSV)</h2>
{thong_bao_html}
<form method="post" action="/master-data/import">
  <label>Dán nội dung CSV (đúng 13 cột header nhan_vien.csv)</label>
  <textarea name="csv_content" rows="6" style="width:100%;font:12px monospace" required></textarea>
  <button type="submit">Import — ghi đè nhan_vien.csv</button>
</form>
""", "/master-data")


def _render_to_trinh(role):
    rows = _doc_csv("to_trinh_duyet_rieng.csv")
    tr = "".join(
        f"<tr><td>{r['so_to_trinh']}</td><td>{r['msnv_hoac_nhom']}</td>"
        f"<td>{r['loai_pc']}</td><td>{_tien(int(r['dinh_muc_d_thang']), role)}</td></tr>"
        for r in rows
    )
    return _layout("Tờ trình", f"""
<h2>Danh sách Tờ trình duyệt riêng</h2>
<table><tr><th>Số TT</th><th>MSNV/Nhóm</th><th>Loại PC</th><th>Định mức</th></tr>{tr}</table>
""", "/to-trinh")


def _render_khoa_ky(role, qs):
    if qs.get("khoa") == ["1"] and qs.get("ly_do", [""])[0]:
        try:
            khoa_ky(KY_MAC_DINH, "web-ui", qs["ly_do"][0])
        except ValueError:
            pass
    da_khoa = is_locked(KY_MAC_DINH)
    badge = '<span class="badge warn">ĐÃ KHÓA</span>' if da_khoa else '<span class="badge ok">ĐANG MỞ</span>'
    form = "" if da_khoa else f"""
<form method="get" action="/khoa-ky">
  <label>Lý do khóa kỳ (bắt buộc)</label>
  <input type="text" name="ly_do" required>
  <input type="hidden" name="khoa" value="1">
  <button type="submit">Xác nhận khóa kỳ {KY_MAC_DINH}</button>
</form>
<p style="font-size:11px;color:#888">Bước 2 xác nhận (tier: compensable) — sau khóa KHÔNG truy thu tháng sau.</p>
"""
    return _layout("Khóa kỳ", f"""
<h2>Khóa kỳ lương {KY_MAC_DINH}</h2>
<p>Trạng thái: {badge}</p>
{form}
""", "/khoa-ky")


def _render_trinh_ky(role):
    bang = bang_trinh_ky(KY_MAC_DINH)
    sections = ""
    for du_an, rows in bang.items():
        tr = "".join(f"<tr><td>{r['msnv']}</td><td>{r['tong']}</td></tr>" for r in rows)
        sections += f"<h3>{du_an}</h3><table><tr><th>MSNV</th><th>Tổng công</th></tr>{tr}</table>"
    return _layout("Trình ký", f"""
<h2>Template 0 — Trình ký theo dự án (ngày 20)</h2>
<p>Không cột tiền — CHT chỉ ký xác nhận NGÀY CÔNG (C3).</p>
{sections}
""", "/trinh-ky")


def _render_don_treo(role):
    rows = don_treo(KY_MAC_DINH)
    tr = "".join(f"<tr><td>{r['msnv']}</td><td>{r['ky']}</td></tr>" for r in rows)
    return _layout("Đơn treo", f"""
<h2>Đơn "treo" chờ duyệt — kỳ {KY_MAC_DINH}</h2>
<table><tr><th>MSNV</th><th>Kỳ</th></tr>{tr}</table>
""", "/don-treo")


# ── Công thức lương (C9) — mỗi TAB = 1 công thức cuối, hiển thị luồng đi (trace) ──
# Nguồn: Excel bàn giao Payroll, sheet "Payroll structure". Mỗi tab gọi
# compute(FIELD_CUOI, inputs) — trace trả về theo ĐÚNG thứ tự tính (dependency
# trước, field phụ thuộc sau) = luồng đi thật của công thức, không phải thứ tự
# liệt kê tay.
FORMULA_TABS = (
    ("NET_PAY_HOME", "💰 Lương thực chi (cuối)"),
    ("GROSS", "📥 Tổng thu nhập (GROSS)"),
    ("TOTAL_INS", "🏥 BHXH nhân viên"),
    ("PIT", "🧾 Thuế TNCN"),
    ("TOTAL_CTY_COST", "🏢 Chi phí công ty"),
)

_INPUT_FIELDS = (
    ("BASIC_SAL", "Lương chính thức (100%)", 20_000_000),
    ("STD_DAYS", "Công chuẩn", 26),
    ("ACTUAL_DAYS", "Ngày công thực tế", 26),
    ("PROB_DAYS", "Ngày công thử việc", 0),
    ("RESPONSIBILITY_ALLOW", "PC trách nhiệm (HĐLĐ)", 0),
    ("MEALS_TOTAL", "Tổng bữa cơm", 26),
    ("PHONE_ALLOW", "PC điện thoại", 300_000),
    ("FUEL_ALLOW", "PC nhiên liệu/xăng", 0),
    ("TRANSPORT_ALLOW", "PC đi lại (chuẩn)", 0),
    ("DEPENDENT_CNT", "Số người phụ thuộc", 0),
    ("BONUS_KPI", "Thưởng KPI", 0),
)


def _render_cong_thuc(role, qs):
    tab = qs.get("tab", ["NET_PAY_HOME"])[0]
    if tab not in dict(FORMULA_TABS):
        tab = "NET_PAY_HOME"

    inputs = {}
    for code, ten, mac_dinh in _INPUT_FIELDS:
        raw = qs.get(code, [str(mac_dinh)])[0]
        try:
            inputs[code] = float(raw)
        except ValueError:
            inputs[code] = mac_dinh

    from app.p30_formula_engine import compute
    trace = {}
    ket_qua = compute(tab, inputs, {}, trace)

    tabs_html = "".join(
        f'<a class="ftab{" on" if t == tab else ""}" href="/cong-thuc?tab={t}&'
        + "&".join(f"{c}={inputs[c]:g}" for c, _, _ in _INPUT_FIELDS)
        + f'">{ten}</a>'
        for t, ten in FORMULA_TABS
    )

    form_fields = "".join(
        f'<label>{ten}<input type="text" name="{code}" value="{inputs[code]:g}"></label>'
        for code, ten, _ in _INPUT_FIELDS
    )

    rows = ""
    for i, (code, (ten, formula, val)) in enumerate(trace.items(), 1):
        cong_thuc_hien = formula if formula not in ("(input)",) else "<em>(bạn nhập ở trên)</em>"
        highlight = ' style="background:rgba(10,132,255,.08);font-weight:700"' if code == tab else ""
        rows += (f"<tr{highlight}><td>{i}</td><td><code>{code}</code></td><td>{ten}</td>"
                 f"<td><code style=\"font-size:11px\">{cong_thuc_hien}</code></td>"
                 f"<td>{val:,.0f}</td></tr>")

    return _layout("Công thức lương", f"""
<h2>Công thức lương — chạy thử trước khi ghi nhận (C9)</h2>
<p>Nguồn: Excel bàn giao Payroll (sheet "Payroll structure"). Mỗi tab bên dưới
là MỘT công thức cuối — chọn tab để xem luồng tính từ input thô đến kết quả đó.
Sửa số ở form rồi bấm "Chạy thử" để xem lại — <b>chưa ghi vào đâu cả</b>, chỉ tính
thử (dashboard test).</p>

<div style="display:flex;gap:6px;flex-wrap:wrap;margin:12px 0">{tabs_html}</div>

<form method="get" action="/cong-thuc">
  <input type="hidden" name="tab" value="{tab}">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px 16px">{form_fields}</div>
  <button type="submit">▶ Chạy thử công thức</button>
</form>

<h3 style="margin-top:20px">Kết quả: {dict(FORMULA_TABS)[tab]} = <span style="color:var(--accent)">{ket_qua:,.0f} đ</span></h3>
<p style="font-size:12px;color:var(--sub,#888)">Luồng đi (đúng thứ tự tính — phụ thuộc trước, kết quả sau):</p>
<table><tr><th>#</th><th>Code</th><th>Tên</th><th>Công thức gốc (Excel)</th><th>Giá trị</th></tr>{rows}</table>
<style>.ftab{{padding:6px 12px;border-radius:8px;background:var(--th);text-decoration:none;color:inherit;font-size:12px}}.ftab.on{{background:var(--accent);color:#fff}}
form label{{display:flex;flex-direction:column;font-size:11px;gap:2px}}
form input{{margin-top:2px}}</style>
""", "/cong-thuc")


_ROUTES = {
    "/": _render_dashboard,
    "/bang-cong": _render_bang_cong,
    "/suat-an": _render_suat_an,
    "/pc": _render_pc,
    "/tang-ca": _render_tang_ca,
    "/master-data": _render_master_data,
    "/to-trinh": _render_to_trinh,
    "/trinh-ky": _render_trinh_ky,
    "/don-treo": _render_don_treo,
}


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        role = qs.get("role", [""])[0]

        if parsed.path == "/khoa-ky":
            body = _render_khoa_ky(role, qs)
        elif parsed.path == "/cong-thuc":
            body = _render_cong_thuc(role, qs)
        elif parsed.path in _ROUTES:
            body = _ROUTES[parsed.path](role)
        else:
            body = _layout("404", "<p>Không tìm thấy</p>", parsed.path)

        self._send(body)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/master-data/import":
            self._send(_layout("404", "<p>Không tìm thấy</p>", parsed.path))
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8")
        form = parse_qs(raw)
        noi_dung_csv = form.get("csv_content", [""])[0]

        duong_dan = os.path.join(_DATA_DIR, "nhan_vien.csv")
        hop_le, so_dong, loi = validate_and_import(noi_dung_csv, duong_dan)
        if hop_le:
            thong_bao = (True, f"Import thành công {so_dong} dòng.")
        else:
            thong_bao = (False, f"Từ chối: {loi}")

        self._send(_render_master_data("", thong_bao))

    def _send(self, body):
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def build_server(port=0):
    return HTTPServer(("localhost", port), _Handler)
