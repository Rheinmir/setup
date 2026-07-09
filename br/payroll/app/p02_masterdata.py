"""p02_masterdata — DM Bộ phận (tỉnh/khối/vùng theo ngày hiệu lực), DM Nơi cư trú, DM Khoảng cách (C7)."""

_BO_PHAN = {
    "Kho miền Nam": [
        ("2025-01-01", "TP.HCM", "Kho vận", "Miền Nam"),
        ("2025-07-01", "Bình Dương", "Kho vận", "Miền Nam"),
    ],
}

_KHOANG_CACH = {
    ("TP.HCM", "Quảng Ninh"): "khac_mien",
}


def bo_phan_info(ten_bo_phan, ngay):
    lich_su = _BO_PHAN.get(ten_bo_phan)
    if lich_su is None:
        raise ValueError(f"Bộ phận không tồn tại: {ten_bo_phan}")

    hang_hieu_luc = None
    for hieu_luc_tu, tinh, khoi, vung in sorted(lich_su, key=lambda r: r[0]):
        if hieu_luc_tu <= ngay:
            hang_hieu_luc = (tinh, khoi, vung)
    if hang_hieu_luc is None:
        _, tinh, khoi, vung = sorted(lich_su, key=lambda r: r[0])[0]
        hang_hieu_luc = (tinh, khoi, vung)
    return hang_hieu_luc


def dai_khoang_cach(noi_tuyen, tinh):
    key = (noi_tuyen, tinh)
    if key in _KHOANG_CACH:
        return _KHOANG_CACH[key]
    if noi_tuyen == tinh:
        return "cung_tinh"
    return "khac_mien"
