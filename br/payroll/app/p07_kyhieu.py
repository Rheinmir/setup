"""p07_kyhieu — parser ký hiệu công thành thuộc tính máy hiểu (C4.2)."""

_BANG = {
    "x": {"lam_viec_thuc_te": True, "huong_luong": True, "tinh_bhxh": True, "cho_duyet": False},
    "x1": {"lam_viec_thuc_te": True, "huong_luong": True, "tinh_bhxh": True, "cho_duyet": False},
    "OL": {"lam_viec_thuc_te": True, "huong_luong": True, "tinh_bhxh": True, "cho_duyet": False},
    "P": {"lam_viec_thuc_te": False, "huong_luong": True, "tinh_bhxh": True, "cho_duyet": False},
    "F": {"lam_viec_thuc_te": False, "huong_luong": True, "tinh_bhxh": True, "cho_duyet": False},
    "R": {"lam_viec_thuc_te": False, "huong_luong": True, "tinh_bhxh": True, "cho_duyet": False},
    "Fo": {"lam_viec_thuc_te": False, "huong_luong": True, "tinh_bhxh": True, "cho_duyet": False},
    "L": {"lam_viec_thuc_te": False, "huong_luong": False, "tinh_bhxh": False, "cho_duyet": False},
    "NB": {"lam_viec_thuc_te": False, "huong_luong": False, "tinh_bhxh": False, "cho_duyet": False},
    "Ts": {"lam_viec_thuc_te": False, "huong_luong": False, "tinh_bhxh": False, "cho_duyet": False},
    "TS": {"lam_viec_thuc_te": False, "huong_luong": False, "tinh_bhxh": False, "cho_duyet": False},
    "TSN": {"lam_viec_thuc_te": False, "huong_luong": False, "tinh_bhxh": False, "cho_duyet": False},
    "ON": {"lam_viec_thuc_te": True, "huong_luong": True, "tinh_bhxh": True, "cho_duyet": False},
    "OD": {"lam_viec_thuc_te": True, "huong_luong": True, "tinh_bhxh": True, "cho_duyet": False},
    "TN": {"lam_viec_thuc_te": False, "huong_luong": False, "tinh_bhxh": False, "cho_duyet": False},
    "Ro": {"lam_viec_thuc_te": False, "huong_luong": False, "tinh_bhxh": False, "cho_duyet": False},
    "?P": {"lam_viec_thuc_te": False, "huong_luong": False, "tinh_bhxh": False, "cho_duyet": True},
}


def phan_loai(ky_hieu):
    if ky_hieu in _BANG:
        return dict(_BANG[ky_hieu])

    for prefix, he_so in (("TC100", 100), ("TC200", 200), ("TC300", 300)):
        if ky_hieu == prefix:
            return {
                "lam_viec_thuc_te": True,
                "huong_luong": True,
                "tinh_bhxh": True,
                "cho_duyet": False,
                "he_so_tc": he_so,
            }

    raise ValueError(f"Ký hiệu công không hợp lệ: {ky_hieu!r}")
