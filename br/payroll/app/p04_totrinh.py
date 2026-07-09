"""p04_totrinh — Tờ trình duyệt riêng ghi đè định mức chung theo MSNV/nhóm/dự án
kể từ ngày hiệu lực; GĐDA bị loại khỏi PC công trường/đi lại chung (C5.2, C5.3.3, C5.3.7)."""

OVERRIDES = [
    {"msnv": "NV007", "loai": "xang_xe", "tien": 10_000_000, "nguon": "TT-2026/018", "hieu_luc": "2026-07-01"},
    {"msnv": "NV006", "loai": "xang_xe", "tien": 2_600_000, "nguon": "TT-2026/031", "hieu_luc": "2026-01-01"},
    {"msnv": "NV008", "loai": "khac", "tien": 1_500_000, "nguon": "TT-2026/020", "hieu_luc": "2026-06-20"},
]

GDDA = {"NV007"}


def dinh_muc_cuoi(loai, msnv, ngay):
    if loai == "di_lai" and msnv in GDDA:
        return 0, "GĐDA bị loại khỏi PC đi lại chung"
    for o in OVERRIDES:
        if o["msnv"] == msnv and o["loai"] == loai and ngay >= o["hieu_luc"]:
            return o["tien"], o["nguon"]
    return 0, "QĐ chung"
