"""p05_nghiphep — Quy định ngày nghỉ (C7).

Phép năm 12 ngày + 1 ngày/5 năm thâm niên; tháng đạt >=50% công chuẩn
mới tính phép; phép tồn dùng đến 31/12 năm kế; ốm Cty 3 ngày/năm.
"""

from datetime import date

PHEP_CO_BAN = 12

_NHAN_VIEN = {
    "NV_vao_2021": {
        "nam_vao": 2021,
        "thang_dat": 12,
        "phep_ton_nam_truoc": {},
        "da_dung": 0,
    },
    "NV_thang_thieu_cong": {
        "nam_vao": 2024,
        "thang_dat": 11,
        "phep_ton_nam_truoc": {},
        "da_dung": 0,
    },
    "NV_du_cong": {
        "nam_vao": 2024,
        "thang_dat": 12,
        "phep_ton_nam_truoc": {},
        "da_dung": 0,
    },
    "NV_co_phep_2025": {
        "nam_vao": 2024,
        "thang_dat": 12,
        "phep_ton_nam_truoc": {2025: 5},
        "da_dung": 0,
    },
    "NV_da_dung_it": {
        "nam_vao": 2018,
        "thang_dat": 12,
        "phep_ton_nam_truoc": {},
        "da_dung": 3,
    },
}


def _phep_nam(nv, nam):
    tham_nien = max(0, nam - nv["nam_vao"])
    thuong_tham_nien = tham_nien // 5
    ty_le = nv["thang_dat"] / 12
    return (PHEP_CO_BAN + thuong_tham_nien) * ty_le


def _phep_ton(nv, nam_hien_tai):
    # Phép tồn của năm (nam_hien_tai - 1) dùng được đến 31/12 năm kế
    # (tức đến hết nam_hien_tai). Sang năm sau nữa thì hết hạn.
    nam_truoc = nam_hien_tai - 1
    return nv["phep_ton_nam_truoc"].get(nam_truoc, 0)


def so_du_phep(nv_id, ngay_str):
    nv = _NHAN_VIEN[nv_id]
    ngay = date.fromisoformat(ngay_str)
    nam = ngay.year

    ton = _phep_ton(nv, nam)
    nam_nay = _phep_nam(nv, nam)
    da_dung = nv["da_dung"]
    con_lai = ton + nam_nay - da_dung

    return ton, nam_nay, da_dung, con_lai
