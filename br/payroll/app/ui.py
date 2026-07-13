"""ui.py — 3 màn: bảng lương / phiếu lương / trace (BR C15.1, C15.2, C14.1).

Chỉ XEM, không sửa dữ liệu. Số liệu lấy từ engine (không chép công thức sang đây).
"""
import html
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, HTTPServer

from app import adapters, engine, lichky, params

# Kỳ lương duy nhất đang có dữ liệu vào (data/inputs/<period>) [C18.1].
PERIOD = "2026-03"

_CSS = """
:root{color-scheme:light dark}
html[data-theme=light]{color-scheme:light}
html[data-theme=dark]{color-scheme:dark}
body{font:15px/1.5 system-ui,sans-serif;margin:0;padding:24px;
     background:Canvas;color:CanvasText}
h1,h2{margin:.6em 0 .3em}
table{border-collapse:collapse;width:100%;margin-bottom:1.5rem}
th,td{border:1px solid color-mix(in srgb,CanvasText 25%,transparent);
      padding:6px 10px;text-align:left}
th{background:color-mix(in srgb,CanvasText 8%,transparent)}
td.money,th.money{text-align:right;font-variant-numeric:tabular-nums;
                  font-feature-settings:"tnum"}
ul.trace{list-style:none;padding-left:18px;border-left:1px dashed
         color-mix(in srgb,CanvasText 30%,transparent)}
ul.trace>li{margin:.35rem 0}
code{font-family:ui-monospace,monospace}
.clause{opacity:.7;font-size:.85em}
a{color:LinkText}
#theme{position:fixed;top:12px;right:12px;padding:6px 12px;cursor:pointer}
@media print{#theme{display:none}}
"""

# Chống FOUC: đặt data-theme TRƯỚC khi vẽ; không ép mode — mặc định theo hệ điều hành [C15.2].
_HEAD_JS = """
(function(){var t=localStorage.getItem('theme');
if(!t){t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}
document.documentElement.setAttribute('data-theme',t);})();
"""
_TOGGLE_JS = """
document.getElementById('theme').onclick=function(){
var h=document.documentElement,t=h.getAttribute('data-theme')==='dark'?'light':'dark';
h.setAttribute('data-theme',t);localStorage.setItem('theme',t);};
"""


def _fmt(v) -> str:
    """Tiền/số kiểu Việt Nam: 189930161 -> '189.930.161'."""
    d = v if isinstance(v, Decimal) else Decimal(str(v))
    dau = "-" if d < 0 else ""
    d = abs(d)
    nguyen = int(d)
    le = d - nguyen
    s = f"{nguyen:,}".replace(",", ".")
    if le:
        s += "," + format(le, "f").split(".")[1].rstrip("0")
    return dau + s


def _e(x) -> str:
    return html.escape(str(x))


def _page(title: str, body: str) -> bytes:
    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<title>{_e(title)}</title>
<script>{_HEAD_JS}</script>
<style>{_CSS}</style>
</head><body>
<button id="theme" type="button">Sáng / Tối</button>
{body}
<script>{_TOGGLE_JS}</script>
</body></html>""".encode("utf-8")


def _tinh(emp_id: str):
    """(bản ghi, kết quả, vết truy, tham số) của một nhân sự trong kỳ [C14.1]."""
    p = params.load(PERIOD)
    for rec in adapters.fetch_employees(PERIOD):
        if rec["employee_id"] == emp_id:
            kq, vet = engine.bang_luong(rec, p)
            return rec, kq, vet, p
    return None, None, None, None


_COT = [("GROSS", "Tổng thu nhập"), ("TOTAL_INS", "Bảo hiểm"), ("PIT", "Thuế TNCN"),
        ("NET_PAY_HOME", "Lương thực nhận")]


def _man_bang_luong() -> bytes:
    p = params.load(PERIOD)
    dau, cuoi = lichky.ky_cong(PERIOD)
    hang = []
    for rec in adapters.fetch_employees(PERIOD):
        kq, _ = engine.bang_luong(rec, p)
        o = "".join(f'<td class="money">{_fmt(kq[c])}</td>' for c, _t in _COT)
        eid = _e(rec["employee_id"])
        hang.append(
            f'<tr><td><a href="/payslip/{eid}">{eid}</a></td>'
            f'<td>{_e(rec.get("ho_ten", ""))}</td>{o}'
            f'<td><a href="/trace/{eid}/NET_PAY">truy vết</a></td></tr>')
    th = "".join(f'<th class="money">{_e(t)}</th>' for _c, t in _COT)
    return _page(f"Bảng lương {PERIOD}", f"""
<h1>Bảng lương kỳ {_e(PERIOD)}</h1>
<p>Từ ngày {dau:%d/%m/%Y} đến ngày {cuoi:%d/%m/%Y}</p>
<table><thead><tr><th>Mã NV</th><th>Họ tên</th>{th}<th></th></tr></thead>
<tbody>{"".join(hang)}</tbody></table>""")


_KHOI_CONG = [("STD_DAYS", "Ngày công chuẩn"), ("OFFICIAL_DAYS", "Ngày công chính thức"),
              ("HOLIDAY_DAYS", "Ngày lễ"), ("PAID_LEAVE_DAYS", "Phép có lương"),
              ("PAID_DAYS", "Tổng ngày công hưởng lương")]
_KHOI_THU = [("EARNED_SAL", "Lương theo ngày công"), ("BONUS_TOTAL", "Thưởng"),
             ("GROSS", "Tổng thu nhập")]
_KHOI_TRU = [("SI_EMP", "BHXH (8%)"), ("HI_EMP", "BHYT (1,5%)"), ("UI_EMP", "BHTN (1%)"),
             ("TOTAL_INS", "Tổng bảo hiểm"), ("PIT", "Thuế TNCN"),
             ("TOTAL_POST_DED", "Trừ sau thuế"), ("TOTAL_POST_ADD", "Cộng sau thuế")]


def _man_phieu_luong(emp_id: str):
    rec, kq, _vet, _p = _tinh(emp_id)
    if rec is None:
        return None
    dau, cuoi = lichky.ky_cong(PERIOD)

    def khoi(ten, muc):
        r = "".join(
            # ngày công là field input (không có trong CODES) → lấy thẳng từ bản ghi
            f'<tr><td>{_e(t)}</td><td class="money">{_fmt(kq.get(c, rec.get(c, 0)))}</td>'
            f'<td class="clause"><a href="/trace/{_e(emp_id)}/{c}">{c}</a></td></tr>'
            for c, t in muc)
        return f'<h2>{_e(ten)}</h2><table><tbody>{r}</tbody></table>'

    return _page(f"Phiếu lương {emp_id}", f"""
<h1>PHIẾU LƯƠNG</h1>
<p>Kỳ lương: Từ ngày {dau:%d} tháng {dau:%m} năm {dau:%Y}
   đến ngày {cuoi:%d} tháng {cuoi:%m} năm {cuoi:%Y}</p>
<h2>Thông tin nhân viên</h2>
<table><tbody>
<tr><td>Mã nhân viên</td><td>{_e(emp_id)}</td></tr>
<tr><td>Họ tên</td><td>{_e(rec.get("ho_ten", ""))}</td></tr>
<tr><td>Chức danh</td><td>{_e(rec.get("chuc_danh", ""))}</td></tr>
<tr><td>Phòng ban</td><td>{_e(rec.get("phong_ban", ""))}</td></tr>
<tr><td>Loại hợp đồng</td><td>{_e(rec.get("CONTRACT_TYPE", ""))}</td></tr>
</tbody></table>
{khoi("Ngày công", _KHOI_CONG)}
{khoi("Lương và phụ cấp", _KHOI_THU)}
{khoi("Khấu trừ", _KHOI_TRU)}
<h2>Thực nhận</h2>
<table><tbody><tr><td><b>Lương thực nhận</b></td>
<td class="money"><b>{_fmt(kq["NET_PAY_HOME"])}</b></td>
<td class="clause"><a href="/trace/{_e(emp_id)}/NET_PAY">NET_PAY</a></td></tr></tbody></table>
<p><a href="/">← Bảng lương</a></p>""")


def _cay(code: str, vet: dict, emp_id: str, sau: set) -> str:
    n = vet[code]
    dong = (f'<code>{_e(code)}</code> = <b class="money">{_fmt(n["value"])}</b>'
            f' <span class="clause">[{_e(n["clause"])}] {_e(n["formula"])}</span>')
    if code in sau or not n["deps"]:
        return f"<li>{dong}</li>"
    sau = sau | {code}
    con = "".join(_cay(d, vet, emp_id, sau) for d in n["deps"] if d in vet)
    return f'<li>{dong}<ul class="trace">{con}</ul></li>'


def _man_trace(emp_id: str, code: str):
    _rec, _kq, vet, p = _tinh(emp_id)
    if vet is None or code not in vet:
        return None
    tham_so = "".join(
        f'<tr><td><code>{_e(k)}</code></td><td class="money">{_fmt(v)}</td></tr>'
        for k, v in p.items() if isinstance(v, (int, float)) and not isinstance(v, bool))
    return _page(f"Truy vết {code} — {emp_id}", f"""
<h1>Truy vết <code>{_e(code)}</code> — {_e(emp_id)}</h1>
<ul class="trace">{_cay(code, vet, emp_id, set())}</ul>
<h2>Tham số đã dùng</h2>
<p class="clause">Nguồn: <code>data/params.json</code>,
   bộ tham số hiệu lực từ {_e(p["effective_from"])} [C4.1]</p>
<table><thead><tr><th>Tham số</th><th class="money">Giá trị</th></tr></thead>
<tbody>{tham_so}</tbody></table>
<p><a href="/payslip/{_e(emp_id)}">← Phiếu lương</a></p>""")


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # im lặng khi chạy test
        pass

    def do_GET(self):
        phan = [x for x in self.path.split("?")[0].split("/") if x]
        try:
            if not phan:
                body = _man_bang_luong()
            elif len(phan) == 3 and phan[0] == "payslip":
                body = None
            elif len(phan) == 2 and phan[0] == "payslip":
                body = _man_phieu_luong(phan[1])
            elif len(phan) == 3 and phan[0] == "trace":
                body = _man_trace(phan[1], phan[2])
            else:
                body = None
        except Exception as exc:                      # không bịa số — báo lỗi ra màn
            self.send_error(500, explain=str(exc))
            return
        if body is None:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def build_server(port: int = 8000) -> HTTPServer:
    """Server 3 route: / · /payslip/<mã NV> · /trace/<mã NV>/<mã field> [C15.1]."""
    return HTTPServer(("127.0.0.1", port), _Handler)


if __name__ == "__main__":
    srv = build_server(8000)
    print("http://127.0.0.1:8000/")
    srv.serve_forever()
