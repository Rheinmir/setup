"""p23_matbao — nhánh Mắt Bão: nhận diện employee_type THẬT từ hồ sơ (p06), chốt
sớm ngày 15, định mức grid tra matbao_dinh_muc_grid.csv theo chức danh (C6.1)."""

import csv
import os

from app.p06_workday import ho_so

_NGAY_CHOT = 15
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "br", "data-draft")


def _grid_theo_chuc_danh():
    with open(os.path.join(_DATA_DIR, "matbao_dinh_muc_grid.csv"), newline="", encoding="utf-8") as f:
        return {r["ngach_hoac_chuc_danh"]: r for r in csv.DictReader(f)}


def policy_nhan_su(msnv, ngay):
    hs = ho_so(msnv)
    la_mat_bao = hs.get("employee_type") == "MatBao"
    ngay_trong_thang = int(ngay.split("-")[2])
    grid = _grid_theo_chuc_danh()
    hang = grid.get(hs.get("chuc_danh"))

    def dinh_muc_grid(khoan):
        if not hang:
            return None
        col = {"dien_thoai": "dien_thoai_d_thang", "xang": "xang_d_thang"}.get(khoan)
        return int(hang[col]) if col and hang.get(col) else None

    return {
        "la_mat_bao": la_mat_bao,
        "da_qua_chot": la_mat_bao and ngay_trong_thang > _NGAY_CHOT,
        "dinh_muc_grid": dinh_muc_grid,
    }
