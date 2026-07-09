"""BHXH hai trục thời gian (C5.1.4): quy đổi kỳ công 21–20 sang tháng dương lịch.
Đếm ngày tính/không tính đóng BHXH từ công thô THẬT (p06+p07), tính trích NV
8/1.5/1 + Cty 17/0.5/3/1 + 2% KPCĐ trên lương thật (hồ sơ p06)."""

from app.p06_workday import cong_tho, ho_so
from app.p07_kyhieu import phan_loai

TY_LE_NV = 8 + 1.5 + 1
TY_LE_CTY = 17 + 0.5 + 3 + 1
TY_LE_KPCD = 2


def _thang_sau(thang):
    y, m = (int(x) for x in thang.split("-"))
    y, m = (y, m + 1) if m < 12 else (y + 1, 1)
    return f"{y:04d}-{m:02d}"


def tong_hop_bhxh_thang(msnv, thang_duong_lich):
    """thang_duong_lich: 'YYYY-MM' (trục BHXH). Một tháng dương lịch nằm vắt qua HAI
    kỳ công (21–20): đầu tháng (1–20) thuộc kỳ công CÙNG tên, cuối tháng (21–cuối)
    thuộc kỳ công KẾ TIẾP — đọc cả hai cửa sổ rồi lọc đúng ngày thuộc tháng này."""
    rows = []
    for ky_cong in (thang_duong_lich, _thang_sau(thang_duong_lich)):
        rows += [r for r in cong_tho(ky_cong)
                 if r["msnv"] == msnv and r["ngay"].startswith(thang_duong_lich)]
    rows = list({r["ngay"]: r for r in rows}.values())  # khử trùng nếu 2 cửa sổ chồng

    ngay_tinh, ngay_khong_tinh = [], []
    for r in rows:
        if phan_loai(r["ky_hieu"])["tinh_bhxh"]:
            ngay_tinh.append(r["ngay"])
        else:
            ngay_khong_tinh.append(r["ngay"])

    dien_dong = len(ngay_tinh) > 0
    luong = float(ho_so(msnv).get("luong_co_ban_thang(ASSUMED)", 0) or 0)

    trich_nv = luong * TY_LE_NV / 100 if dien_dong else 0
    trich_cty = luong * TY_LE_CTY / 100 if dien_dong else 0
    kpcd = luong * TY_LE_KPCD / 100 if dien_dong else 0

    return {
        "dien_dong": dien_dong,
        "trich_nv": trich_nv,
        "trich_cty": trich_cty,
        "kpcd": kpcd,
        "ngay_tinh": ngay_tinh,
        "ngay_khong_tinh": ngay_khong_tinh,
        "ngay_tinh_list": ngay_tinh,
    }
