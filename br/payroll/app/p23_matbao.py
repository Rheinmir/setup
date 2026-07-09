"""p23_matbao — nhánh Mắt Bão: chốt sớm + grid định mức riêng (C6.1)."""
from datetime import date

_MAT_BAO_IDS = {"NV005"}

_GRID_MAT_BAO = {
    "dien_thoai": 200_000,
}

_NGAY_CHOT = 15


def _parse_ngay(ngay):
    y, m, d = (int(x) for x in ngay.split("-"))
    return date(y, m, d)


def policy_nhan_su(ma_nv, ngay):
    la_mat_bao = ma_nv in _MAT_BAO_IDS
    d = _parse_ngay(ngay)

    def dinh_muc_grid(khoan):
        return _GRID_MAT_BAO.get(khoan)

    return {
        "la_mat_bao": la_mat_bao,
        "da_qua_chot": d.day > _NGAY_CHOT,
        "dinh_muc_grid": dinh_muc_grid,
    }
