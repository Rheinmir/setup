"""p16_pcxang — PC nhiên liệu/xăng/ô tô: CT chuẩn 1.000.000 cho L2–L6; VP không mức
chung (chỉ qua tờ trình, kể cả tài xế HN đích danh, GĐDA, Ban TGĐ); pro-rata + <14 ngày (C5.3.3)."""

from app.p04_totrinh import dinh_muc_cuoi
from app.p13_prorata import tinh_prorata

CONG_CHUAN = 26
CT_CHUAN = 1_000_000
HANG_CT_CHUAN = {"L2", "L3", "L4", "L5", "L6"}
NGAY = "2026-07-09"

_HO_SO = {
    "NV_ct_l3_khong_tt": {"khoi": "CT", "hang": "L3", "lam_viec": 26, "le": 0},
    "NV002": {"khoi": "VP", "hang": "L3", "lam_viec": 26, "le": 0},
    "NV006": {"khoi": "VP", "hang": None, "lam_viec": 26, "le": 0},
    "NV007": {"khoi": "VP", "hang": None, "lam_viec": 26, "le": 0},
}


def _dinh_muc_chung(khoi, hang):
    if khoi == "CT" and hang in HANG_CT_CHUAN:
        return CT_CHUAN
    return 0


def tinh_pc_xang(ma_nv):
    hs = _HO_SO[ma_nv]
    tien_tt, nguon = dinh_muc_cuoi("xang_xe", ma_nv, NGAY)

    if nguon != "QĐ chung":
        dinh_muc_val = tien_tt
    else:
        dinh_muc_val = _dinh_muc_chung(hs["khoi"], hs["hang"])

    bo_phan_input = {ma_nv: {"lam_viec": hs["lam_viec"], "le": hs.get("le", 0)}}
    kq = tinh_prorata(bo_phan_input, CONG_CHUAN, lambda ten, dm=dinh_muc_val: dm)

    trace = dict(kq["trace"])
    trace["nguồn"] = nguon

    return {"tong": kq["tong"], "trace": trace}
