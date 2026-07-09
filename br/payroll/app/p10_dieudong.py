"""p10_dieudong — tách công theo bộ phận khi điều động giữa kỳ (C5.1.3)."""

_DIEU_DONG = {
    "NV_vidu2": {
        "ngay_dieu_dong": None,
        "bo_phan": {
            "bo_phan_A": {"lam_viec": 3, "le": 1, "phep": 6},
            "bo_phan_B": {"lam_viec": 3, "phep": 7, "le": 2},
        },
    },
    "NV001": {
        "ngay_dieu_dong": "2026-07-05",
        "bo_phan": {
            "VP HCM": {"lam_viec": 10},
            "CT Quan Lạn": {"lam_viec": 6},
        },
    },
    "NV002": {
        "ngay_dieu_dong": None,
        "bo_phan": {
            "VP HCM": {"lam_viec": 1},
        },
    },
}


def tach_dieu_dong(ma_nv):
    data = _DIEU_DONG[ma_nv]
    r = dict(data["bo_phan"])
    if data["ngay_dieu_dong"]:
        r["ngay_dieu_dong"] = data["ngay_dieu_dong"]
    return r
