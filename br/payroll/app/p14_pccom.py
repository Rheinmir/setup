"""PC cơm = tổng suất ăn × đơn giá; tách Non-tax ≤730.000 đ/tháng, phần vượt vào Taxable (C5.3.1)."""

NON_TAX_TRAN = 730_000
DON_GIA_MAC_DINH = 45_000


def tinh_pc_com(so_suat, don_gia=DON_GIA_MAC_DINH):
    thanh_tien = so_suat * don_gia
    non_tax = min(thanh_tien, NON_TAX_TRAN)
    taxable = thanh_tien - non_tax
    return {
        "thanh_tien": thanh_tien,
        "non_tax": non_tax,
        "taxable": taxable,
    }
