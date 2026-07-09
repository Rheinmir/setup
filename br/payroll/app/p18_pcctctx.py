"""p18_pcctctx — PC công trường + công tác xa: bảng khối (CT/VP) x dải khoảng cách
x 2 đối tượng (ĐH+ / CĐ-TC-Nghề); pro-rata + <14 ngày + chia bộ phận (C5.3.5).
GĐDA bị loại khỏi PC công trường/đi lại chung (C5.2, C5.3.3, C5.3.7)."""

from app.p13_prorata import tinh_prorata

CONG_CHUAN = 26
GDDA = {"NV007"}

GRID = {
    ("CT", "khac_mien"): {"dh": 3_000_000, "cd": 2_000_000},
    ("CT", "30_100"): {"dh": 2_000_000, "cd": 1_200_000},
    ("CT", "duoi_30"): {"dh": 1_000_000, "cd": 600_000},
    ("VP", "khac_mien"): {"dh": 1_500_000, "cd": 1_000_000},
    ("VP", "30_100"): {"dh": 1_000_000, "cd": 700_000},
    ("VP", "duoi_30"): {"dh": 500_000, "cd": 300_000},
}

_HO_SO = {
    "NV_ct_khacmien_dh": {
        "doan": [{"ten": "CT", "khoi": "CT", "dai": "khac_mien", "doi_tuong": "dh", "lam_viec": 26, "le": 0}],
    },
    "NV_vp_30100_cd": {
        "doan": [{"ten": "VP", "khoi": "VP", "dai": "30_100", "doi_tuong": "cd", "lam_viec": 26, "le": 0}],
    },
    "NV_ct_duoi30_dh": {
        "doan": [{"ten": "CT", "khoi": "CT", "dai": "duoi_30", "doi_tuong": "dh", "lam_viec": 26, "le": 0}],
    },
}


def tinh_pc_ct_ctx(ma_nv):
    if ma_nv in GDDA:
        return {"tong": 0, "theo_bo_phan": {}, "trace": {"nguồn": "GĐDA bị loại khỏi PC công trường/công tác xa chung"}}

    hs = _HO_SO[ma_nv]
    theo_bo_phan = {}
    trace = {}
    tong = 0

    for doan in hs["doan"]:
        dinh_muc_val = GRID.get((doan["khoi"], doan["dai"]), {}).get(doan["doi_tuong"], 0)
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
