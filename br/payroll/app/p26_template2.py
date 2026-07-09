"""Template 2 Payroll Master — file phẳng cho kế toán (C6.3)."""

_PC_KEYS = ("pc_com", "pc_dien_thoai", "pc_xang", "pc_ct_ctx", "pc_di_lai", "pc_ct_xa", "pc_khac")

_DATA = {
    "NV001": {"trang_thai": "ct", "luong_co_ban": 10_000_000, "pc_com": 730_000,
              "pc_dien_thoai": 300_000, "pc_xang": 200_000, "pc_ct_ctx": 0,
              "pc_di_lai": 0, "pc_ct_xa": 0, "pc_khac": 0},
    "NV004": {"trang_thai": "tv", "luong_co_ban": 8_000_000, "pc_com": 0,
              "pc_dien_thoai": 0, "pc_xang": 0, "pc_ct_ctx": 0,
              "pc_di_lai": 0, "pc_ct_xa": 0, "pc_khac": 0},
    "NV010": {"trang_thai": "thai_san", "luong_co_ban": 9_000_000, "pc_com": 0,
              "pc_dien_thoai": 0, "pc_xang": 0, "pc_ct_ctx": 0,
              "pc_di_lai": 0, "pc_ct_xa": 0, "pc_khac": 0},
}

_COM_NON_TAX_TRAN = 730_000


def payroll_master(ky):
    rows = []
    for msnv, d in _DATA.items():
        pc_com = d["pc_com"]
        pc_com_non_tax = min(pc_com, _COM_NON_TAX_TRAN)
        pc_com_taxable = pc_com - pc_com_non_tax
        pc_tong = sum(d.get(k, 0) for k in _PC_KEYS)

        luong_thu_viec = d["luong_co_ban"] * 0.85 if d["trang_thai"] == "tv" else 0
        luong_chinh_thuc = d["luong_co_ban"] if d["trang_thai"] == "ct" else 0

        if d["trang_thai"] == "thai_san":
            thu_nhap_chiu_thue = 0
        else:
            thu_nhap_chiu_thue = luong_thu_viec + luong_chinh_thuc + pc_com_taxable
        thue_tncn = max(0.0, thu_nhap_chiu_thue * 0.0)

        rows.append({
            "msnv": msnv,
            "ky": ky,
            "trang_thai": d["trang_thai"],
            "luong_thu_viec": luong_thu_viec,
            "luong_chinh_thuc": luong_chinh_thuc,
            "pc_com": pc_com,
            "pc_com_non_tax": pc_com_non_tax,
            "pc_com_taxable": pc_com_taxable,
            "pc_dien_thoai": d["pc_dien_thoai"],
            "pc_xang": d["pc_xang"],
            "pc_ct_ctx": d["pc_ct_ctx"],
            "pc_di_lai": d["pc_di_lai"],
            "pc_ct_xa": d["pc_ct_xa"],
            "pc_khac": d["pc_khac"],
            "pc_tong": pc_tong,
            "thue_tncn": thue_tncn,
        })
    return rows
