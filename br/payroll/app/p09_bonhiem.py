"""p09_bonhiem — tách 2 giai đoạn trước/sau bổ nhiệm khi thay đổi lương/PC giữa kỳ (C5.1.2)."""
import calendar

CONG_CHUAN = 26

_BO_NHIEM = {
    "NV003": {"ngay_hieu_luc": "01-07", "muc_truoc": 500000, "muc_sau": 1000000},
}


def tach_bo_nhiem(ma_nv, thang):
    nam, ky = thang.split("-")
    nam = int(nam)
    ky = int(ky)
    so_ngay = calendar.monthrange(nam, ky)[1]

    bo_nhiem = _BO_NHIEM.get(ma_nv)
    if not bo_nhiem:
        return [
            {
                "tu": f"{nam:04d}-{ky:02d}-01",
                "den": f"{nam:04d}-{ky:02d}-{so_ngay:02d}",
                "ngay_huong": so_ngay,
                "muc": 0,
                "pc_trach_nhiem": 0,
            }
        ]

    nam_truoc, ky_truoc = (nam, ky - 1) if ky > 1 else (nam - 1, 12)
    so_ngay_truoc = calendar.monthrange(nam_truoc, ky_truoc)[1]

    gd1 = {
        "tu": f"{nam_truoc:04d}-{ky_truoc:02d}-01",
        "den": f"{nam_truoc:04d}-{ky_truoc:02d}-{so_ngay_truoc:02d}",
        "ngay_huong": so_ngay_truoc,
        "muc": bo_nhiem["muc_truoc"],
    }
    gd1["pc_trach_nhiem"] = gd1["ngay_huong"] * gd1["muc"] / CONG_CHUAN

    gd2 = {
        "tu": f"{nam:04d}-{ky:02d}-01",
        "den": f"{nam:04d}-{ky:02d}-{so_ngay:02d}",
        "ngay_huong": so_ngay,
        "muc": bo_nhiem["muc_sau"],
    }
    gd2["pc_trach_nhiem"] = gd2["ngay_huong"] * gd2["muc"] / CONG_CHUAN

    return [gd1, gd2]
