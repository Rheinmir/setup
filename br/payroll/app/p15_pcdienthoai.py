"""p15_pcdienthoai — PC điện thoại: tra bảng ngạch × VP/CT, áp engine pro-rata,
chia theo bộ phận/giai đoạn khi điều động hoặc thử việc (C5.3.2)."""

from app.p03_dinhmuc import DIEN_THOAI_TABLE
from app.p13_prorata import tinh_prorata

CONG_CHUAN = 26

_HO_SO = {
    "NV_ql02_ct_full": {
        "mode": "bo_phan",
        "cong_chuan": CONG_CHUAN,
        "doan": [
            {"ten": "CT", "ngach": "QL.02", "khoi": "CT", "lam_viec": 26, "le": 0},
        ],
    },
    "NV001": {
        "mode": "bo_phan",
        "cong_chuan": CONG_CHUAN,
        "doan": [
            {"ten": "VP HCM", "ngach": "NV.01", "khoi": "VP", "lam_viec": 10, "le": 0},
            {"ten": "CT Quan Lạn", "ngach": "NV.01", "khoi": "CT", "lam_viec": 6, "le": 0},
        ],
    },
    "NV004": {
        "mode": "giai_doan",
        "cong_chuan": CONG_CHUAN,
        "doan": [
            {"ten": "CT (thử việc)", "ngach": "TV", "khoi": "CT", "lam_viec": 9, "le": 0},
            {"ten": "CT (chính thức)", "ngach": "NV.01", "khoi": "CT", "lam_viec": 17, "le": 0},
        ],
    },
}


def tinh_pc_dien_thoai(ma_nv):
    hs = _HO_SO[ma_nv]
    cong_chuan = hs["cong_chuan"]

    theo_bo_phan = {}
    giai_doan = []
    tong = 0

    for doan in hs["doan"]:
        ngach = doan["ngach"]
        khoi = doan["khoi"]
        dinh_muc_val = DIEN_THOAI_TABLE.get(ngach, {}).get(khoi, 0)
        bo_phan_input = {doan["ten"]: {"lam_viec": doan["lam_viec"], "le": doan.get("le", 0)}}
        kq = tinh_prorata(bo_phan_input, cong_chuan, lambda ten, dm=dinh_muc_val: dm)
        so_tien = kq["tong"]
        tong += so_tien

        entry = {
            "ten": doan["ten"],
            "ngach": ngach,
            "khoi": khoi,
            "so_tien": so_tien,
            "trace": kq["trace"],
        }

        if hs["mode"] == "giai_doan":
            giai_doan.append(entry)
        theo_bo_phan[doan["ten"]] = entry

    result = {"tong": tong, "theo_bo_phan": theo_bo_phan}
    if giai_doan:
        result["giai_doan"] = giai_doan
    return result
