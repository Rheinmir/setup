"""p05_nghiphep — Quy định ngày nghỉ (C7). Phép năm 12 ngày + 1/5 năm thâm niên
(nam_vao lấy THẬT từ hồ sơ p06); tháng đạt >=50% công chuẩn mới tính phép; phép
tồn dùng đến 31/12 năm kế. Sổ phép tồn/đã dùng là dữ liệu HR nhập tay (như tờ
trình p04) — mặc định hợp lý (chưa dùng, không tồn) cho NV không có trong sổ."""

from datetime import date

from app.p06_workday import ho_so

PHEP_CO_BAN = 12
THANG_DAT_MAC_DINH = 12  # giả định làm đủ cả năm nếu không có ghi chú khác

# Sổ HR nhập tay: các trường hợp có tháng-thiếu-công / phép tồn / đã dùng KHÁC mặc định.
_SO_PHEP_HR = {
    "NV003": {"thang_dat": 11},
    "NV004": {"phep_ton_nam_truoc": {2025: 5}},
    "NV006": {"da_dung": 3},
}


def _phep_nam(nam_vao, thang_dat, nam):
    tham_nien = max(0, nam - nam_vao)
    thuong_tham_nien = tham_nien // 5
    ty_le = thang_dat / 12
    return (PHEP_CO_BAN + thuong_tham_nien) * ty_le


def so_du_phep(msnv, ngay_str):
    ngay = date.fromisoformat(ngay_str)
    nam = ngay.year

    hs = ho_so(msnv)
    nam_vao_str = hs.get("ngay_vao", "")
    nam_vao = int(nam_vao_str[:4]) if nam_vao_str else nam

    ghi_chu = _SO_PHEP_HR.get(msnv, {})
    thang_dat = ghi_chu.get("thang_dat", THANG_DAT_MAC_DINH)
    da_dung = ghi_chu.get("da_dung", 0)
    ton_map = ghi_chu.get("phep_ton_nam_truoc", {})

    ton = ton_map.get(nam - 1, 0)
    nam_nay = _phep_nam(nam_vao, thang_dat, nam)
    con_lai = ton + nam_nay - da_dung

    return ton, nam_nay, da_dung, con_lai
