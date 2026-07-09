"""p17_pcdilai — PC đi lại: nhóm đối tượng (CHT/CHT ME · ĐH+ · CĐ/TC/Nghề · NV.02) x
nơi tuyển dụng x tỉnh bộ phận -> dải khoảng cách -> định mức; pro-rata + <14 ngày + chia bộ phận (C5.3.4)."""

from app.p02_masterdata import dai_khoang_cach
from app.p04_totrinh import dinh_muc_cuoi
from app.p13_prorata import tinh_prorata

CONG_CHUAN = 26
NGAY = "2026-07-09"

DINH_MUC = {
    "khac_mien": 1_000_000,
    "khac_tinh": 500_000,
    "cung_tinh": 0,
}

_HO_SO = {
    "NV001": {
        "nhom": "NV.01",
        "noi_tuyen": "TP.HCM",
        "doan": [
            {"ten": "VP HCM", "tinh": "TP.HCM", "lam_viec": 10, "le": 0},
            {"ten": "CT Quan Lạn", "tinh": "Quảng Ninh", "lam_viec": 6, "le": 0},
        ],
    },
    "NV007": {
        "nhom": "NV.02",
        "noi_tuyen": "TP.HCM",
        "doan": [{"ten": "CT", "tinh": "Quảng Ninh", "lam_viec": 26, "le": 0}],
    },
    "NV009": {
        "nhom": "NV.02",
        "noi_tuyen": "TP.HCM",
        "doan": [{"ten": "CT", "tinh": "Quảng Ninh", "lam_viec": 12, "le": 0}],
    },
}


def tinh_pc_di_lai(ma_nv):
    hs = _HO_SO[ma_nv]
    tien_tt, nguon = dinh_muc_cuoi("di_lai", ma_nv, NGAY)

    if nguon != "QĐ chung":
        return {"tong": tien_tt, "theo_bo_phan": {}, "trace": {"nguồn": nguon}}

    theo_bo_phan = {}
    trace = {}
    tong = 0

    for doan in hs["doan"]:
        dai = dai_khoang_cach(hs["noi_tuyen"], doan["tinh"])
        dinh_muc_val = DINH_MUC.get(dai, 0)
        ngay_huong = doan["lam_viec"] + doan.get("le", 0)
        if ngay_huong < 14:
            dinh_muc_val = dinh_muc_val / 2

        bo_phan_input = {doan["ten"]: {"lam_viec": doan["lam_viec"], "le": doan.get("le", 0)}}
        kq = tinh_prorata(bo_phan_input, CONG_CHUAN, lambda ten, dm=dinh_muc_val: dm)
        so_tien = kq["tong"]
        tong += so_tien
        theo_bo_phan[doan["ten"]] = so_tien
        trace.update(kq["trace"])

    return {"tong": tong, "theo_bo_phan": theo_bo_phan, "trace": trace}
