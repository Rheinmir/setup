"""p20_truythu — truy thu/truy lĩnh khi định mức đổi hồi tố, kỳ chưa khóa (C4.3)."""
import calendar
from datetime import date

KY_HIEN_TAI = "2026-07"


def tinh_truy_thu_linh(ma_nv, loai_phu_cap, muc_cu, muc_moi, ngay_hieu_luc, ky):
    if ky < KY_HIEN_TAI:
        raise ValueError(f"Kỳ {ky} đã khóa, không thể truy thu/truy lĩnh")

    nam, thang = (int(x) for x in ky.split("-"))
    ngay_hl = date.fromisoformat(ngay_hieu_luc)
    so_ngay_thang = calendar.monthrange(nam, thang)[1]

    if ngay_hl.year == nam and ngay_hl.month == thang:
        ngay_cong = so_ngay_thang - ngay_hl.day + 1
    else:
        ngay_cong = so_ngay_thang

    don_gia_ngay_cu = muc_cu / so_ngay_thang
    don_gia_ngay_moi = muc_moi / so_ngay_thang
    chenh_lech = round((don_gia_ngay_moi - don_gia_ngay_cu) * ngay_cong)

    ly_do = (
        f"Đổi định mức {loai_phu_cap} từ {muc_cu:,.0f} sang {muc_moi:,.0f} "
        f"hiệu lực {ngay_hieu_luc}, truy {'lĩnh' if chenh_lech >= 0 else 'thu'} "
        f"kỳ {ky} ({ngay_cong} ngày công tương ứng)"
    )

    return {
        "ma_nv": ma_nv,
        "loai_phu_cap": loai_phu_cap,
        "ky": ky,
        "ngay_cong": ngay_cong,
        "chenh_lech": chenh_lech,
        "ly_do": ly_do,
    }
