"""lichky.py — Kỳ lương 21→20 + công chuẩn VP/CT (BR C5)."""
from datetime import date, timedelta
from decimal import Decimal

# C5.4 — lễ dương lịch cố định (tháng, ngày). Lễ ÂM lịch (Tết, Giỗ Tổ) do HR nhập tay, ngoài phạm vi frame.
_LE_DUONG_LICH = ((1, 1), (4, 30), (5, 1), (9, 2), (9, 3))

_NUA_CONG_THU_BAY = Decimal("0.5")


def ky_cong(period: str):
    """'2026-03' -> (21/02/2026, 20/03/2026)  [C5.1]."""
    nam, thang = (int(x) for x in period.split("-"))
    cuoi = date(nam, thang, 20)
    dau = date(nam - 1, 12, 21) if thang == 1 else date(nam, thang - 1, 21)
    return dau, cuoi


def cong_chuan(period: str, khoi: str) -> Decimal:
    """Ngày công chuẩn của kỳ: CT trừ Chủ nhật; VP trừ thêm ½ ngày mỗi thứ 7 [C5.2]."""
    if khoi not in ("VP", "CT"):
        raise ValueError(f"Khối làm việc không hợp lệ: {khoi!r} (chỉ 'VP' hoặc 'CT')")
    dau, cuoi = ky_cong(period)
    cong = Decimal(0)
    d = dau
    while d <= cuoi:
        wd = d.weekday()  # 5 = thứ 7, 6 = Chủ nhật
        if wd == 6:
            pass
        elif wd == 5 and khoi == "VP":
            cong += _NUA_CONG_THU_BAY
        else:
            cong += Decimal(1)
        d += timedelta(days=1)
    return cong


def ngay_le(nam: int):
    """Danh mục ngày lễ dương lịch của năm [C5.4]."""
    return [date(nam, m, d) for m, d in _LE_DUONG_LICH]
