"""Bảng định mức: điện thoại, đi lại, CT+công tác xa, CT xa theo dự án (C5.3.2, C5.3.4, C5.3.5, C5.3.6)."""

DIEN_THOAI_TABLE = {
    "QL.01": {"CT": 1_000_000, "VP": 1_000_000},
    "QL.02": {"CT": 1_000_000, "VP": 800_000},
    "QL.03": {"CT": 800_000, "VP": 800_000},
    "QL.04": {"CT": 800_000, "VP": 800_000},
    "QL.05": {"CT": 600_000, "VP": 600_000},
    "QL.06": {"CT": 600_000, "VP": 600_000},
    "CV.01": {"CT": 400_000, "VP": 300_000},
    "CV.02": {"CT": 400_000, "VP": 300_000},
    "NV.01": {"CT": 400_000, "VP": 300_000},
    "NV.02": {"CT": 400_000, "VP": 300_000},
    "NV.03": {"CT": 300_000, "VP": 200_000},
    "NV.04": {"CT": 300_000, "VP": 200_000},
    "NV.05": {"CT": 300_000, "VP": 200_000},
    "TV": {"CT": 300_000, "VP": 0},
}

DI_LAI_TABLE = {
    "<30": {"CHT": 0, "dh_tro_len": 0, "cd_tc_nghe": 0, "NV.02": 0},
    "30-100": {"CHT": 900_000, "dh_tro_len": 500_000, "cd_tc_nghe": 350_000, "NV.02": 250_000},
    "100-400": {"CHT": 1_400_000, "dh_tro_len": 1_100_000, "cd_tc_nghe": 850_000, "NV.02": 550_000},
    "400-1000": {"CHT": 1_400_000, "dh_tro_len": 1_100_000, "cd_tc_nghe": 850_000, "NV.02": 550_000},
    "mien_trung": {"CHT": 7_200_000, "dh_tro_len": 3_600_000, "cd_tc_nghe": 2_700_000, "NV.02": 1_800_000},
    "nam_trung_bo": {"CHT": 6_000_000, "dh_tro_len": 3_000_000, "cd_tc_nghe": 2_200_000, "NV.02": 1_500_000},
    "phu_quoc": {"CHT": 6_000_000, "dh_tro_len": 3_000_000, "cd_tc_nghe": 2_200_000, "NV.02": 1_500_000},
    "khac_mien": {"CHT": 11_200_000, "dh_tro_len": 5_600_000, "cd_tc_nghe": 4_200_000, "NV.02": 2_800_000},
}

CT_XA_DU_AN_TABLE = {
    "Quan Lạn": {
        "CHT": 5_000_000, "CHT ME": 5_000_000,
        "CHP": 4_000_000, "CHP ME": 4_000_000,
        "GS": 3_000_000, "CV": 3_000_000,
        "Tài xế": 2_000_000, "Admin": 2_000_000,
        "Thủ kho": 2_000_000, "Bảo vệ": 2_000_000,
    },
    "Chingluh": {
        "CHT": 2_000_000, "CHP": 1_500_000,
        "GS": 1_000_000, "Bảo vệ": 500_000,
    },
}

_CD_TC_NGHE_TRINH_DO = {"Cao đẳng", "Trung cấp", "Nghề"}


def _nhom_doi_tuong(hs):
    if hs.get("chuc_danh") in ("CHT", "CHT ME"):
        return "CHT"
    if hs.get("ngach") == "NV.02":
        return "NV.02"
    if hs.get("trinh_do") in _CD_TC_NGHE_TRINH_DO:
        return "cd_tc_nghe"
    return "dh_tro_len"


def _dien_thoai(hs, opts):
    khoi = opts.get("khoi")
    return DIEN_THOAI_TABLE.get(hs.get("ngach"), {}).get(khoi, 0)


def _di_lai(hs, opts):
    dai = opts.get("dai")
    nhom = _nhom_doi_tuong(hs)
    return DI_LAI_TABLE.get(dai, {}).get(nhom, 0)


def _ct_xa_du_an(hs, opts):
    du_an = opts.get("du_an")
    chuc_danh = hs.get("chuc_danh")
    return CT_XA_DU_AN_TABLE.get(du_an, {}).get(chuc_danh, 0)


_HANDLERS = {
    "dien_thoai": _dien_thoai,
    "di_lai": _di_lai,
    "ct_xa_du_an": _ct_xa_du_an,
}


def dinh_muc(loai, hs, opts):
    handler = _HANDLERS.get(loai)
    if handler is None:
        return 0
    return handler(hs, opts)
