"""p19_pcctxa — PC công trường xa/khó khăn theo dự án đặc thù x chức danh
(dinh_muc_ct_xa_du_an.csv thật) + PC khác (7) từ danh sách duyệt riêng (p04)
(C5.3.6, C5.3.7)."""

import csv
import os

from app.p04_totrinh import dinh_muc_cuoi
from app.p06_workday import ho_so
from app.p10_dieudong import tach_dieu_dong
from app.p13_prorata import tinh_prorata

CONG_CHUAN = 26
NGAY = "2026-07-09"
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "br", "data-draft")
_DU_AN_KHO_KHAN = "Làng Tây – Hòn Thơm"


def _bang_du_an():
    with open(os.path.join(_DATA_DIR, "dinh_muc_ct_xa_du_an.csv"), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _du_an_theo_bo_phan(ten_bo_phan):
    """'CT Quan Lạn' -> 'Quan Lạn'; 'CT Làng Tây – Hòn Thơm' -> 'Làng Tây – Hòn Thơm'."""
    if ten_bo_phan.startswith("CT "):
        return ten_bo_phan[3:]
    return ten_bo_phan


def _muc_du_an(bang, du_an, chuc_danh):
    for r in bang:
        if r["du_an"] != du_an:
            continue
        if r["chuc_danh"] == chuc_danh or du_an == _DU_AN_KHO_KHAN:
            return int(r["muc_d_thang"]), r["nguon"]
    return 0, ""


def tinh_pc_ct_xa_va_khac(msnv, thang="2026-07"):
    hs = ho_so(msnv)
    chuc_danh = hs.get("chuc_danh")
    bang = _bang_du_an()

    bp_split = {k: v for k, v in tach_dieu_dong(msnv, thang).items() if k != "ngay_dieu_dong"}
    pc6 = 0
    trace6 = {}
    for ten, d in bp_split.items():
        du_an = _du_an_theo_bo_phan(ten)
        dinh_muc_val, nguon = _muc_du_an(bang, du_an, chuc_danh)
        if dinh_muc_val:
            kq = tinh_prorata({ten: d}, CONG_CHUAN, lambda t, dm=dinh_muc_val: dm)
            pc6 += kq["tong"]
            note = "TT-2026/044" if du_an == _DU_AN_KHO_KHAN else nguon
            trace6[ten] = f"{kq['trace'][ten]} (nguồn: {note})"

    tien7, nguon7 = dinh_muc_cuoi("khac", msnv, NGAY)

    return {"pc6": pc6, "pc7": tien7, "trace": {**trace6, "pc7_nguon": nguon7}}
