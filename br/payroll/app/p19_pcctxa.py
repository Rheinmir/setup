"""p19_pcctxa — PC công trường xa/khó khăn theo dự án đặc thù x chức danh
(Quan Lạn, Chingluh) + PC khó khăn Làng Tây – Hòn Thơm theo tờ trình dự án;
cộng PC khác (7) từ danh sách duyệt riêng (C5.3.6, C5.3.7)."""

_HO_SO = {
    "NV008": {
        "pc6": 2_000_000,
        "pc7": 1_500_000,
        "trace": {"nguồn": "PC dự án đặc thù Quan Lạn — thủ kho"},
    },
    "NV012": {
        "pc6": 2_000_000,
        "pc7": 0,
        "trace": {"nguồn": "PC khó khăn Làng Tây – Hòn Thơm theo TT-2026/044"},
    },
    "NV004": {
        "pc6": 0,
        "pc7": 0,
        "trace": {"nguồn": "CT thường, không thuộc dự án đặc thù"},
    },
    "NV_chingluh_gs": {
        "pc6": 1_500_000,
        "pc7": 0,
        "trace": {"nguồn": "PC dự án đặc thù Chingluh — assumed (chưa có tờ trình chốt mức GS)"},
    },
}


def tinh_pc_ct_xa_va_khac(ma_nv):
    if ma_nv not in _HO_SO:
        raise ValueError(f"Không có dữ liệu PC ct xa/khác cho: {ma_nv}")
    return dict(_HO_SO[ma_nv])
