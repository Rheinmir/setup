"""p08_thuviec — Đếm tách ngày công giai đoạn thử việc / sau thử việc theo
'Ngày kết thúc thử việc' (C5.1.1). Lương TV = ngày TV x 85%; chính thức x 100%.
"""
from datetime import date

from app.p01_lichky import sinh_lich_ky
from app.p06_workday import cong_tho, ho_so
from app.p07_kyhieu import phan_loai


def _giai_doan(ngay_iso, ket_thuc_tv):
    if not ket_thuc_tv:
        return "tv"
    return "tv" if ngay_iso < ket_thuc_tv else "sau_tv"


def tach_thu_viec(msnv, thang):
    ho_so_nv = ho_so(msnv)
    ket_thuc_tv = ho_so_nv.get("ngay_ket_thuc_thu_viec") or ""

    lich_ky = sinh_lich_ky(thang)

    theo_ngay = {}
    for r in cong_tho(thang):
        if r["msnv"] == msnv:
            theo_ngay[r["ngay"]] = r["ky_hieu"]

    ket_qua = {
        "tv": {"lam_viec": 0, "nghi_huong_luong": 0},
        "sau_tv": {"lam_viec": 0, "nghi_huong_luong": 0},
    }

    for d in lich_ky["ngay"]:
        ngay_iso = d["ngay"]
        ky_hieu = theo_ngay.get(ngay_iso)

        if ky_hieu is not None:
            thuoc_tinh = phan_loai(ky_hieu)
            lam_viec_thuc_te = thuoc_tinh["lam_viec_thuc_te"]
            huong_luong = thuoc_tinh["huong_luong"]
        elif not d["le"]:
            lam_viec_thuc_te = True
            huong_luong = True
        else:
            lam_viec_thuc_te = False
            huong_luong = False

        if not lam_viec_thuc_te and not huong_luong:
            continue

        giai_doan = _giai_doan(ngay_iso, ket_thuc_tv)
        if lam_viec_thuc_te:
            ket_qua[giai_doan]["lam_viec"] += 1
        elif huong_luong:
            ket_qua[giai_doan]["nghi_huong_luong"] += 1

    return {
        "ngay_tv": ket_qua["tv"],
        "ngay_sau_tv": ket_qua["sau_tv"],
    }
