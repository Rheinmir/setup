"""ui.py — 4 màn: bảng lương / phiếu lương / trace / upload (BR C15.1, C15.2, C15.4, C14.1).

3 màn gốc chỉ XEM, không sửa dữ liệu. /upload là ngoại lệ DUY NHẤT — mass-upload
nguyên file Excel, không sửa từng field. Số liệu lấy từ engine (không chép công
thức sang đây).
"""
import html
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, HTTPServer

from app import adapters, audit, auth, engine, lichky, params, upload

# Kỳ lương duy nhất đang có dữ liệu vào (data/inputs/<period>) [C18.1].
PERIOD = "2026-03"

_CSS = """
:root{color-scheme:light;--bg:#e6e7ee;--ink:#1a1c23;--muted:#43475a;--accent:#1c1e26;
      --sh-light:-6px -6px 14px #f4f5fa;--sh-dark:6px 6px 14px #c3c6d4}
[data-theme=dark]{color-scheme:dark;--bg:#22242c;--ink:#eef0f6;--muted:#b6bccd;
      --accent:#ecedf0;--sh-light:-6px -6px 14px #2b2e38;--sh-dark:6px 6px 14px #16171d}
body{font:15px/1.6 "Plus Jakarta Sans",ui-sans-serif,system-ui,sans-serif;margin:0;
     padding:32px;background:var(--bg);color:var(--ink)}
h1,h2{margin:1.2em 0 .5em;letter-spacing:-.02em}
table{border-collapse:separate;border-spacing:0;width:100%;margin-bottom:1.5rem;
      padding:14px;border-radius:20px;background:var(--bg);
      box-shadow:var(--sh-dark),var(--sh-light)}
th,td{padding:10px 14px;text-align:left}
th{color:var(--muted);font-weight:600;font-size:.85em;text-transform:uppercase;
   letter-spacing:.06em}
tbody tr td:first-child{border-radius:12px 0 0 12px}
tbody tr td:last-child{border-radius:0 12px 12px 0}
tbody tr:hover td{box-shadow:inset 2px 2px 5px rgba(0,0,0,.10),
                  inset -2px -2px 5px rgba(255,255,255,.06)}
td.money,th.money{text-align:right;font-variant-numeric:tabular-nums;
                  font-feature-settings:"tnum"}
ul.trace{list-style:none;padding:8px 0 8px 20px;margin:.4rem 0;
         border-left:2px dashed var(--muted)}
ul.trace>li{margin:.4rem 0}
code{font-family:ui-monospace,monospace}
.clause{color:var(--muted);font-size:.85em}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
/* MỘT thanh top cố định — gom nút lùi/badge/theme vào cùng một hàng flex,
   hết cảnh 3 phần tử fixed riêng lẻ đè lên nhau vì magic-number offset. */
.topbar{position:fixed;top:0;left:0;right:0;z-index:50;display:flex;
        align-items:center;justify-content:space-between;gap:12px;
        padding:12px 16px;background:var(--bg)}
.topbar .right{display:flex;align-items:stretch;gap:10px}
body{padding-top:76px}
/* MỌI pill trong top bar dùng CHUNG một khối kích thước → cao bằng nhau,
   không còn cảnh nút Sáng/Tối cao hơn badge. height:38px + flex canh giữa
   nội dung theo chiều dọc, bất kể font/nội dung khác nhau. */
.topbar .back,.topbar #theme,.topbar .who{
  height:38px;display:inline-flex;align-items:center;box-sizing:border-box;
  padding:0 16px;border-radius:14px;font-size:.85em;background:var(--bg);
  box-shadow:var(--sh-dark),var(--sh-light);color:var(--ink)}
#theme{cursor:pointer;border:0;font-family:inherit}
#theme:active{box-shadow:inset 3px 3px 7px rgba(0,0,0,.18),
                         inset -3px -3px 7px rgba(255,255,255,.10)}
.back:hover{text-decoration:underline}
#theme,.back{transition:box-shadow .2s ease,transform .15s ease}
#theme:active,.back:active{transform:scale(.97)}
@media print{.topbar{display:none}}
a:focus-visible,button:focus-visible,input:focus-visible{
  outline:2px solid var(--accent);outline-offset:3px;border-radius:6px}
.skip-link{position:absolute;left:-9999px;top:0;padding:10px 18px;border-radius:14px;
  background:var(--bg);box-shadow:var(--sh-dark),var(--sh-light);z-index:200;
  color:var(--ink);text-decoration:none}
.skip-link:focus{left:16px;top:16px}
.toolbar{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 26px;padding:0;list-style:none}
.toolbar a{display:inline-block;padding:9px 16px;border-radius:12px;font-size:.85em;
  font-weight:600;background:var(--bg);box-shadow:var(--sh-dark),var(--sh-light);
  transition:box-shadow .2s ease,transform .15s ease;text-decoration:none!important}
.toolbar a:hover{transform:translateY(-2px)}
.toolbar a:active{transform:translateY(0);
  box-shadow:inset 3px 3px 7px rgba(0,0,0,.14),inset -3px -3px 7px rgba(255,255,255,.08)}
.stats{display:grid;grid-template-columns:1.3fr 1fr 1fr;gap:16px;margin-bottom:24px}
@media (max-width:720px){.stats{grid-template-columns:1fr}}
.stat{padding:20px 22px;border-radius:20px;background:var(--bg);
  box-shadow:var(--sh-dark),var(--sh-light)}
.stat .n{font-size:1.9em;font-weight:700;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.stat .t{color:var(--muted);font-size:.8em;text-transform:uppercase;letter-spacing:.06em;margin-top:2px}
.who{gap:8px}  /* kích thước pill do .topbar .who lo; đây chỉ khoảng cách nội bộ */
.who a{color:var(--muted);text-decoration:underline}
@media (max-width:520px){.who span{display:none}}  /* màn hẹp: badge chỉ còn icon + đăng xuất */
.login-card{max-width:380px;margin:8vh auto 0;padding:32px 30px;border-radius:22px;
  background:var(--bg);box-shadow:var(--sh-dark),var(--sh-light);text-align:center}
.login-card h1{font-size:1.3em;margin-bottom:4px}
.login-card p{color:var(--muted);font-size:.85em;margin:6px 0 20px}
.login-card button{width:100%;padding:13px;border:0;border-radius:14px;font:inherit;
  font-weight:700;cursor:pointer;background:var(--bg);color:var(--ink);
  box-shadow:var(--sh-dark),var(--sh-light);transition:box-shadow .2s ease,transform .15s ease}
.login-card button:hover{transform:translateY(-2px)}
.login-card button:active{transform:translateY(0);
  box-shadow:inset 3px 3px 7px rgba(0,0,0,.14),inset -3px -3px 7px rgba(255,255,255,.08)}
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


# Vai của request HIỆN TẠI — server chạy đơn luồng (HTTPServer thường, không
# Threading) nên biến module-level này an toàn: set 1 lần đầu do_GET/do_POST,
# đọc lại trong _page() cùng request, không có race condition đa luồng.
_current_user = None


def _page(title: str, body: str, back=None) -> bytes:
    """back = (href, nhãn) — link lùi nằm trong TOP BAR, luôn thấy khi cuộn dài. None = màn gốc."""
    nut_lui = f'<a class="back" href="{_e(back[0])}">← {_e(back[1])}</a>' if back else "<span></span>"
    who = (f'<div class="who">👤 <span>{_e(_current_user["name"].split(" (")[0])}</span> '
          f'· <a href="/logout">Đăng xuất</a></div>') if _current_user else ""
    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<title>{_e(title)}</title>
<script>{_HEAD_JS}</script>
<style>{_CSS}</style>
</head><body>
<a class="skip-link" href="#main">Bỏ qua, đến nội dung chính</a>
<header class="topbar">
  {nut_lui}
  <div class="right">{who}<button id="theme" type="button">Sáng / Tối</button></div>
</header>
<main id="main">
{body}
</main>
<script>{_TOGGLE_JS}</script>
</body></html>""".encode("utf-8")


def _man_login() -> bytes:
    """Cổng session [C2.1, cập nhật 2026-07-15] — TUYỆT ĐỐI KHÔNG PHẢI xác
    thực bảo mật thật: không mật khẩu/tài khoản nào để kiểm, bấm là vào
    được ngay. Lô đầu chỉ MỘT vai HR C&B — chỉ là cổng UX/session."""
    return _page("Đăng nhập — Payroll", """
<div class="login-card">
  <h1>PAYROLL</h1>
  <p>Vai: <b>HR C&amp;B</b> (mặc định lô đầu — không có tài khoản/mật khẩu để kiểm)</p>
  <form method="POST" action="/login">
    <button type="submit">Vào hệ thống</button>
  </form>
</div>""")


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
    tong_chi_phi = Decimal(0)
    nhan_su = adapters.fetch_employees(PERIOD)
    for rec in nhan_su:
        kq, _ = engine.bang_luong(rec, p)
        o = "".join(f'<td class="money">{_fmt(kq[c])}</td>' for c, _t in _COT)
        eid = _e(rec["employee_id"])
        hang.append(
            f'<tr><td><a href="/payslip/{eid}">{eid}</a></td>'
            f'<td>{_e(rec.get("ho_ten", ""))}</td>{o}'
            f'<td><a href="/trace/{eid}/NET_PAY">truy vết</a></td></tr>')
        tong_chi_phi += kq["TOTAL_CTY_COST"]
    th = "".join(f'<th class="money">{_e(t)}</th>' for _c, t in _COT)
    # trang chủ LUÔN cố định PERIOD — đây chính là kỳ ground-truth đã đối chiếu (khác /report/*
    # nhận period tuỳ ý qua query string, có thể là dữ liệu DRAFT).
    trang_thai = "✓ Ground-truth đã kiểm chứng"
    return _page(f"Bảng lương {PERIOD}", f"""
<h1>Bảng lương kỳ {_e(PERIOD)}</h1>
<p>Từ ngày {dau:%d/%m/%Y} đến ngày {cuoi:%d/%m/%Y}</p>
<div class="stats">
  <div class="stat"><div class="n">{_fmt(tong_chi_phi)}</div><div class="t">Tổng chi phí công ty kỳ này</div></div>
  <div class="stat"><div class="n">{len(nhan_su)}</div><div class="t">Nhân sự trong kỳ</div></div>
  <div class="stat"><div class="n">{_e(trang_thai)}</div><div class="t">Trạng thái tính toán</div></div>
</div>
<nav class="toolbar" aria-label="Công cụ">
  <a href="/upload">↑ Tải Excel (mass upload)</a>
  <a href="/audit">📋 Sổ audit</a>
  <a href="/params">⚙ Tham số lương</a>
  <a href="/export/payroll-master?period={_e(PERIOD)}">⬇ Payroll Master (CSV)</a>
  <a href="/report/signoff?period={_e(PERIOD)}">🖊 Trình ký</a>
  <a href="/report/cost-by-dept?period={_e(PERIOD)}">📊 Phân bổ chi phí</a>
  <a href="/report/attendance-detail?period={_e(PERIOD)}">⚠ Bảng công chi tiết</a>
</nav>
<table><thead><tr><th>Mã NV</th><th>Họ tên</th>{th}<th></th></tr></thead>
<tbody>{"".join(hang)}</tbody></table>""")


_KHOI_CONG = [("STD_DAYS", "Ngày công chuẩn"), ("OFFICIAL_DAYS", "Ngày công chính thức"),
              ("HOLIDAY_DAYS", "Ngày lễ"), ("PAID_LEAVE_DAYS", "Phép có lương"),
              ("PAID_DAYS", "Tổng ngày công hưởng lương")]
_KHOI_THU = [("EARNED_SAL", "Lương theo ngày công"), ("BONUS_TOTAL", "Thưởng"),
             ("PC_TRUY_THU", "Phụ cấp truy thu/truy lĩnh"), ("GROSS", "Tổng thu nhập")]
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
<td class="clause"><a href="/trace/{_e(emp_id)}/NET_PAY">NET_PAY</a></td></tr></tbody></table>""", back=("/", "Bảng lương"))


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
<tbody>{tham_so}</tbody></table>""", back=(f"/payslip/{_e(emp_id)}", "Phiếu lương"))


def _man_upload() -> bytes:
    """Tab tối giản — chọn kỳ + chọn file Excel, KHÔNG có ô nhập tay từng field [C15.4].
    performed_by/reason là METADATA cho audit log [C14.2], không phải dữ liệu lương."""
    return _page("Tải Excel — mass upload", """
<h1>Tải Excel (mass upload)</h1>
<p class="clause">Header hàng 1 của file phải đúng tên field (vd employee_id, BASIC_SAL...).
Chỉ nạp NGUYÊN file — không sửa từng dòng ở đây. Người thực hiện + lý do BẮT BUỘC
(ghi vào <a href="/audit">sổ audit</a>).</p>
<form id="f">
  <p>Kỳ lương: <input type="text" name="period" placeholder="2026-04" required></p>
  <p>Người thực hiện: <input type="text" name="performed_by" required></p>
  <p>Lý do: <input type="text" name="reason" required></p>
  <p><input type="file" name="xlsx" accept=".xlsx" required></p>
  <button type="submit">Tải lên</button>
</form>
<p id="kq"></p>
<script>
document.getElementById('f').onsubmit = async function(ev){
  ev.preventDefault();
  var period = this.period.value, by = this.performed_by.value, reason = this.reason.value;
  var file = this.xlsx.files[0];
  var qs = 'period=' + encodeURIComponent(period)
    + '&performed_by=' + encodeURIComponent(by)
    + '&reason=' + encodeURIComponent(reason);
  var r = await fetch('/upload?' + qs, {method:'POST', body: file});
  document.getElementById('kq').innerHTML = await r.text();
};
</script>""", back=("/", "Bảng lương"))


def _xu_ly_upload(period: str, performed_by: str, reason: str, body: bytes) -> bytes:
    # validate người/lý do TRƯỚC khi đụng tới file — 400 phải là 400, không bị
    # lỗi parse Excel che mất (C14.2: bắt buộc, không âm thầm bỏ qua)
    if not (performed_by or "").strip():
        raise ValueError("audit: thiếu người thực hiện (bắt buộc)")
    if not (reason or "").strip():
        raise ValueError("audit: thiếu lý do (bắt buộc)")
    try:
        old_rows = adapters.fetch_employees(period)
    except FileNotFoundError:
        old_rows = []
    old_ids = [r.get("employee_id") for r in old_rows]
    rows = upload.parse_employees_xlsx(body)
    adapters.save_uploaded_employees(period, rows)
    new_ids = [r.get("employee_id") for r in rows]
    audit.log_action(action="mass_upload_employees", period=period,
                      performed_by=performed_by, reason=reason,
                      old_ids=old_ids, new_ids=new_ids)
    return f'<p>Đã tải <b>{len(rows)}</b> nhân sự cho kỳ {_e(period)}. <a href="/">Xem bảng lương</a></p>'.encode("utf-8")


def _man_audit() -> bytes:
    """Sổ audit — CHỈ XEM, giống 3 màn gốc [C14.2/FE-17]."""
    rows = audit.read_log()
    hang = "".join(
        f'<tr><td>{_e(r["timestamp"])}</td><td>{_e(r["period"])}</td>'
        f'<td>{_e(r["action"])}</td><td>{_e(r["performed_by"])}</td>'
        f'<td>{_e(r["reason"])}</td>'
        f'<td>{len(r["old_employee_ids"])} → {len(r["new_employee_ids"])}</td></tr>'
        for r in reversed(rows))
    return _page("Sổ audit", f"""
<h1>Sổ audit (giá trị cũ → mới, người, thời gian, lý do)</h1>
<table><thead><tr><th>Thời gian</th><th>Kỳ</th><th>Hành động</th>
<th>Người thực hiện</th><th>Lý do</th><th>Số nhân sự (cũ→mới)</th></tr></thead>
<tbody>{hang}</tbody></table>""", back=("/", "Bảng lương"))


def _fmt_param(v):
    return _fmt(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else _e(v)


def _man_params() -> bytes:
    """Toàn bộ tham số lương — CHỈ XEM [C4.1/FE-23]. Không sửa qua đây (đổi số = sửa data/params.json)."""
    d = params.list_all()
    bo_khoi = []
    for bo in d["param_sets"]:
        hang = "".join(
            f'<tr><td><code>{_e(k)}</code></td><td class="money">{_fmt_param(v)}</td></tr>'
            for k, v in bo.items() if k != "effective_from")
        bo_khoi.append(f"""<h2>Bộ hiệu lực từ {_e(bo['effective_from'])}</h2>
<table><thead><tr><th>Tham số</th><th class="money">Giá trị</th></tr></thead>
<tbody>{hang}</tbody></table>""")
    cho = d.get("_pending_hr", {})
    cho_hang = "".join(
        f'<tr><td><code>{_e(k)}</code></td><td class="money">{_fmt_param(v)}</td></tr>'
        for k, v in cho.items() if k != "_note")
    return _page("Tham số lương", f"""
<h1>Tham số lương (Master Data)</h1>
<p class="clause">Nguồn: <code>data/params.json</code> [C4.1]. Đổi số = sửa file này,
không sửa code — chỉ-xem tại đây.</p>
{"".join(bo_khoi)}
<h2>Chưa hiệu lực</h2>
<p class="clause">{_e(cho.get("_note", ""))}</p>
<table><thead><tr><th>Tham số</th><th class="money">Giá trị</th></tr></thead>
<tbody>{cho_hang}</tbody></table>""", back=("/", "Bảng lương"))


def _bao_cao_phan_bo(period: str) -> bytes:
    """Chi phí công ty cộng dồn theo phòng ban [C15.6/FE-31].

    CHỈ phân bổ theo phòng ban (TOTAL_CTY_COST cộng dồn theo phong_ban) —
    KHÔNG phải phân bổ theo dự án/doanh thu (GĐDA) hay tỷ lệ đề xuất trưởng
    phòng ban như PRD §4.3 mô tả đầy đủ — hai thứ đó cần dữ liệu doanh thu/
    tỷ lệ đề xuất KHÔNG tồn tại trong hệ thống. Đây là nền (department-level
    aggregation), không phải bản đầy đủ.
    """
    p = params.load(period)
    theo_pb = {}
    tong = Decimal(0)
    for rec in adapters.fetch_employees(period):
        chi_phi = engine.compute("TOTAL_CTY_COST", rec, p)
        pb = rec.get("phong_ban", "(chưa khai)")
        theo_pb.setdefault(pb, {"so_nguoi": 0, "chi_phi": Decimal(0)})
        theo_pb[pb]["so_nguoi"] += 1
        theo_pb[pb]["chi_phi"] += chi_phi
        tong += chi_phi
    hang = "".join(
        f'<tr><td>{_e(pb)}</td><td class="money">{v["so_nguoi"]}</td>'
        f'<td class="money">{_fmt(v["chi_phi"])}</td></tr>'
        for pb, v in sorted(theo_pb.items()))
    is_draft = period != PERIOD
    canh_bao = (f'<p style="color:var(--danger,#b3261e)"><b>⚠ DỮ LIỆU DRAFT</b> — kỳ '
               f'{_e(period)} không phải ground-truth đã kiểm chứng ({_e(PERIOD)}), '
               f'chỉ dùng để demo cơ chế phân bổ.</p>') if is_draft else ""
    return _page(f"Phân bổ chi phí — {period}", f"""
<h1>Phân bổ chi phí theo phòng ban — kỳ {_e(period)}</h1>
{canh_bao}
<p class="clause">Chỉ phân bổ theo phòng ban (tổng TOTAL_CTY_COST cộng dồn). KHÔNG
phải phân bổ theo dự án/doanh thu (GĐDA) — chưa có dữ liệu doanh thu trong hệ thống.</p>
<table><thead><tr><th>Phòng ban</th><th class="money">Số người</th>
<th class="money">Chi phí công ty</th></tr></thead>
<tbody>{hang}</tbody></table>
<table><tbody><tr><td><b>Tổng toàn kỳ</b></td><td class="money"><b>{_fmt(tong)}</b></td></tr></tbody></table>""",
        back=("/", "Bảng lương"))


def _bao_cao_trinh_ky(period: str) -> bytes:
    """Báo cáo Trình ký (Template 0) — gộp theo dự án để Chỉ huy trưởng ký [C15.7/FE-19].

    PRD: gộp theo dự án CUỐI CÙNG nơi nhân viên làm việc vào ngày 20 (cần
    theo dõi nhiều đoạn công tác trong tháng — dữ liệu đó KHÔNG tồn tại).
    Ở đây gộp thẳng theo field `du_an` của record (giản lược — coi mỗi
    nhân viên chỉ có 1 dự án trong kỳ). Không phải quy trình duyệt/ký điện
    tử (đó là FE-16, ⊘ ngoài phạm vi) — đây chỉ là BẢN BÁO CÁO để in ký tay.
    """
    p = params.load(period)
    theo_du_an = {}
    for rec in adapters.fetch_employees(period):
        net = engine.compute("NET_PAY_HOME", rec, p)
        da = rec.get("du_an", "(chưa khai dự án)")
        theo_du_an.setdefault(da, []).append(
            f'<tr><td>{_e(rec.get("employee_id",""))}</td><td>{_e(rec.get("ho_ten",""))}</td>'
            f'<td class="money">{_fmt(net)}</td></tr>')
    is_draft = period != PERIOD
    canh_bao = (f'<p style="color:var(--danger,#b3261e)"><b>⚠ DỮ LIỆU DRAFT</b> — kỳ '
               f'{_e(period)} không phải ground-truth đã kiểm chứng ({_e(PERIOD)}), '
               f'chỉ dùng để demo cơ chế trình ký.</p>') if is_draft else ""
    khoi = "".join(
        f'<h2>{_e(da)}</h2><table><thead><tr><th>Mã NV</th><th>Họ tên</th>'
        f'<th class="money">Lương thực nhận</th></tr></thead><tbody>{"".join(hang)}</tbody>'
        f'</table><p class="clause">Chỉ huy trưởng {_e(da)} ký xác nhận: _______________</p>'
        for da, hang in sorted(theo_du_an.items()))
    return _page(f"Trình ký — {period}", f"""
<h1>Báo cáo Trình ký (Template 0) — kỳ {_e(period)}</h1>
{canh_bao}
<p class="clause">Gộp theo dự án (giản lược — chưa theo dõi nhiều đoạn công tác/tháng
để xác định đúng dự án ngày 20). Chỉ là bản in để ký tay, KHÔNG phải quy trình duyệt
điện tử (⊘ ngoài phạm vi).</p>
{khoi}""", back=("/", "Bảng lương"))


_CANH_BAO_BAO_MAT = (
    '<p style="color:var(--danger,#b3261e)"><b>⚠ BÁO CÁO NHẠY CẢM</b> — theo PRD gốc '
    '"chỉ cấp cho HR C&amp;B và ghi log truy cập/xuất file" (§6.4). Hệ thống hiện '
    '<b>CHƯA có kiểm soát truy cập</b> (đăng nhập/phân quyền là FE-32, ⊘ ngoài phạm vi '
    'lô đầu) — route này KHÔNG bị hạn chế ai xem. Không dùng cho môi trường thật tới '
    'khi FE-32 được build.</p>')

_KHOI_NGAY = [("STD_DAYS", "Ngày công chuẩn"), ("OFFICIAL_DAYS", "Ngày công chính thức"),
             ("PROB_DAYS", "Ngày công thử việc"), ("PAID_LEAVE_DAYS", "Phép có lương"),
             ("HOLIDAY_DAYS", "Ngày lễ"), ("COMP_DAYS", "Nghỉ bù"),
             ("PAID_OTHER_DAYS", "Nghỉ hưởng lương khác"), ("BEREAVE_DAYS", "Hiếu hỉ"),
             ("UNPAID_DAYS", "Không lương"), ("SI_DAYS", "Ngày không đóng BHXH")]


def _bang_cong_chi_tiet(period: str) -> bytes:
    """Bảng công chi tiết (mẫu 02__HR C&B) [C15.8/FE-21] — TÓM TẮT theo người,
    KHÔNG PHẢI ma trận ngày × nhân viên đầy đủ (dữ liệu ký hiệu công từng
    ngày không tồn tại trong hệ thống — chỉ có tổng từng loại ngày/kỳ).

    Gate qua auth.require(MASK_MONEY) [C2.1] — vai lô đầu HR C&B đủ quyền
    nên chưa từng thực chặn ai, nhưng cấu trúc gate đã sẵn cho vai thứ 2.
    """
    auth.require(auth.Perm.MASK_MONEY)
    p = params.load(period)
    hang = []
    for rec in adapters.fetch_employees(period):
        paid = engine.compute("PAID_DAYS", rec, p)
        o = "".join(f'<td class="money">{_fmt(rec.get(c, 0))}</td>' for c, _t in _KHOI_NGAY)
        hang.append(f'<tr><td>{_e(rec.get("employee_id",""))}</td>'
                    f'<td>{_e(rec.get("ho_ten",""))}</td>{o}'
                    f'<td class="money"><b>{_fmt(paid)}</b></td></tr>')
    th = "".join(f'<th class="money">{_e(t)}</th>' for _c, t in _KHOI_NGAY)
    return _page(f"Bảng công chi tiết — {period}", f"""
<h1>Bảng công chi tiết (mẫu 02__HR C&amp;B) — kỳ {_e(period)}</h1>
{_CANH_BAO_BAO_MAT}
<p class="clause">TÓM TẮT theo người (tổng từng loại ngày/kỳ) — KHÔNG phải ma trận
ngày × nhân viên với ký hiệu công từng ngày như PRD mô tả đầy đủ (dữ liệu đó không
tồn tại: hệ thống chỉ nhận tổng số ngày mỗi loại, không nhận lịch sử từng ngày).</p>
<table><thead><tr><th>Mã NV</th><th>Họ tên</th>{th}
<th class="money">Tổng công hưởng lương</th></tr></thead>
<tbody>{"".join(hang)}</tbody></table>""", back=("/", "Bảng lương"))


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # im lặng khi chạy test
        pass

    def _session_id(self):
        from http.cookies import SimpleCookie
        c = SimpleCookie(self.headers.get("Cookie", ""))
        return c["session"].value if "session" in c else None

    def _redirect(self, location, clear_cookie=False):
        self.send_response(302)
        self.send_header("Location", location)
        if clear_cookie:
            self.send_header("Set-Cookie", "session=; Path=/; Max-Age=0")
        self.end_headers()

    def do_GET(self):
        global _current_user
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        phan = [x for x in parsed.path.split("/") if x]
        # Đặt vai theo session THẬT của request NÀY ngay từ đầu — tránh badge
        # hiện nhầm do global sót lại từ request trước (vd trang /login lẽ ra
        # không có badge nhưng lại hiện vai của lần login trước).
        _current_user = auth.session_user(self._session_id())
        if phan == ["login"]:                          # cổng — KHÔNG đòi session (else kẹt vòng lặp)
            body = _man_login()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if phan == ["logout"]:
            auth.logout(self._session_id())
            self._redirect("/login", clear_cookie=True)
            return
        if _current_user is None:                       # chưa "đăng nhập" [C2.1] → về cổng
            self._redirect("/login")
            return
        if phan == ["export", "payroll-master"]:  # file tải về, KHÔNG phải màn HTML [FE-20]
            try:
                period = parse_qs(parsed.query).get("period", [PERIOD])[0]
                path = adapters.export_payroll_master(period, params.load(period))
                data = path.read_bytes()
            except Exception as exc:
                self.send_error(500, explain=str(exc))
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition",
                             f'attachment; filename="payroll_master_{period}.csv"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        try:
            if not phan:
                body = _man_bang_luong()
            elif len(phan) == 3 and phan[0] == "payslip":
                body = None
            elif len(phan) == 2 and phan[0] == "payslip":
                body = _man_phieu_luong(phan[1])
            elif len(phan) == 3 and phan[0] == "trace":
                body = _man_trace(phan[1], phan[2])
            elif phan == ["upload"]:
                body = _man_upload()
            elif phan == ["audit"]:
                body = _man_audit()
            elif phan == ["params"]:
                body = _man_params()
            elif phan == ["report", "cost-by-dept"]:
                qperiod = parse_qs(parsed.query).get("period", [PERIOD])[0]
                body = _bao_cao_phan_bo(qperiod)
            elif phan == ["report", "signoff"]:
                qperiod = parse_qs(parsed.query).get("period", [PERIOD])[0]
                body = _bao_cao_trinh_ky(qperiod)
            elif phan == ["report", "attendance-detail"]:
                qperiod = parse_qs(parsed.query).get("period", [PERIOD])[0]
                body = _bang_cong_chi_tiet(qperiod)
            else:
                body = None
        except PermissionError as exc:                # gate quyền [C2.1] — 403, không phải 500
            self.send_error(403, explain=str(exc))
            return
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

    def do_POST(self):
        global _current_user
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        phan = [x for x in parsed.path.split("/") if x]
        if phan == ["login"]:
            sid = auth.login()
            self.send_response(302)
            self.send_header("Location", "/")
            self.send_header("Set-Cookie", f"session={sid}; Path=/")
            self.end_headers()
            return
        user = auth.session_user(self._session_id())
        if user is None:
            self._redirect("/login")
            return
        _current_user = user
        if phan != ["upload"]:
            self.send_error(404)
            return
        qs = parse_qs(parsed.query)
        period = qs.get("period", [None])[0]
        performed_by = qs.get("performed_by", [None])[0]
        reason = qs.get("reason", [None])[0]
        if not period:
            self.send_error(400, explain="thiếu ?period=YYYY-MM")
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            body = _xu_ly_upload(period, performed_by, reason, raw)
        except ValueError as exc:                     # thiếu người/lý do bắt buộc [C14.2]
            self.send_error(400, explain=str(exc))
            return
        except Exception as exc:                      # không bịa số — báo lỗi ra màn
            self.send_error(500, explain=str(exc))
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def build_server(port: int = 8000) -> HTTPServer:
    """Server 4 route: / · /payslip/<mã NV> · /trace/<mã NV>/<mã field> · /upload [C15.1, C15.4]."""
    return HTTPServer(("127.0.0.1", port), _Handler)


if __name__ == "__main__":
    srv = build_server(8000)
    print("http://127.0.0.1:8000/")
    srv.serve_forever()
