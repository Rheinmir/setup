"""BHXH hai trục thời gian (C5.1.4): quy đổi kỳ công 21–20 sang tháng dương lịch.

Dữ liệu nhân viên là dữ liệu mẫu nội bộ scope (không phụ thuộc file ngoài),
đủ để tính diện đóng và các khoản trích NV 8/1.5/1 + Cty 17/0.5/3/1 + 2% KPCĐ.
"""

TY_LE_NV = 8 + 1.5 + 1
TY_LE_CTY = 17 + 0.5 + 3 + 1
TY_LE_KPCD = 2

_NHAN_VIEN = {
    "NV010": {"luong": 10_000_000, "dien_dong": False, "ngay_tinh_list": []},
    "NV002": {
        "luong": 15_000_000,
        "dien_dong": True,
        "ngay_tinh_list": ["2026-06-25", "2026-06-26", "2026-06-27"],
    },
}


def tong_hop_bhxh_thang(ma_nv, thang):
    nv = _NHAN_VIEN.get(ma_nv, {"luong": 0, "dien_dong": False, "ngay_tinh_list": []})
    luong = nv["luong"]
    dien_dong = nv["dien_dong"]

    trich_nv = luong * TY_LE_NV / 100 if dien_dong else 0
    trich_cty = luong * TY_LE_CTY / 100 if dien_dong else 0
    kpcd = luong * TY_LE_KPCD / 100 if dien_dong else 0

    return {
        "dien_dong": dien_dong,
        "trich_nv": trich_nv,
        "trich_cty": trich_cty,
        "kpcd": kpcd,
        "ngay_tinh_list": nv["ngay_tinh_list"],
        "ngay_tinh": nv["ngay_tinh_list"],
    }
