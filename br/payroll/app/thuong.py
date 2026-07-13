"""thuong.py — Thưởng + trích quỹ hàng tháng (BR C10)."""
from decimal import Decimal

from app.luong import _dec, round0

BONUS_KEYS = (
    "BONUS_TET", "BONUS_30_04", "BONUS_CTD_DAY", "BONUS_02_09", "BONUS_KPI",
    "BONUS_13M", "BONUS_NEW_YEAR", "BONUS_PROJECT", "BONUS_EXCELLENCE",
    "BONUS_LOC", "BONUS_OTHER", "BONUS_TRAVEL", "BONUS_REFERRAL",
)

NGHI_LUY_KE_LOAI_TRU = 10  # ngày [C10.1]


def bonus_total(rec: dict) -> Decimal:
    """13 khoản thưởng đều là input, tổng lại [C10.1]."""
    return round0(sum((_dec(rec.get(k, 0)) for k in BONUS_KEYS), Decimal(0)))


def du_dieu_kien_thuong(rec: dict) -> bool:
    """Nghỉ việc, hoặc nghỉ thai sản/ốm/không lương lũy kế >= 10 ngày → loại [C10.1]."""
    if rec.get("TERMINATION_DATE"):
        return False
    return _dec(rec.get("ngay_nghi_luy_ke", 0)) < NGHI_LUY_KE_LOAI_TRU


def _duoc_trich(rec: dict) -> bool:
    """Có ngày hưởng lương > 0 và không có ngày nghỉ việc [C10.2]."""
    return not rec.get("TERMINATION_DATE") and _dec(rec.get("PAID_DAYS", 0)) > 0


def bonus_save_travel(rec: dict, p: dict) -> Decimal:
    """ROUND(6.000.000/12, 0) = 500.000 [C10.2]."""
    if not _duoc_trich(rec):
        return Decimal(0)
    return round0(_dec(p["bonus_save_travel_base"]) / 12)


def bonus_save_kpi(rec: dict, p: dict) -> Decimal:
    """ROUND(CONTRACT_TOTAL/4, 0) [C10.2]."""
    if not _duoc_trich(rec):
        return Decimal(0)
    return round0(_dec(rec["CONTRACT_TOTAL"]) / 4)


def bonus_save_13m(rec: dict, p: dict) -> Decimal:
    """ROUND(CONTRACT_TOTAL/12, 0) [C10.2]."""
    if not _duoc_trich(rec):
        return Decimal(0)
    return round0(_dec(rec["CONTRACT_TOTAL"]) / 12)


def bonus_save_tet(rec: dict, p: dict) -> Decimal:
    """MIN(ROUND(CONTRACT_TOTAL/12,0), ROUND(15.000.000/12,0)) [C10.2]."""
    if not _duoc_trich(rec):
        return Decimal(0)
    return min(round0(_dec(rec["CONTRACT_TOTAL"]) / 12),
               round0(_dec(p["bonus_save_tet_cap"]) / 12))
