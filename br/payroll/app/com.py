"""com.py — Suất ăn 1/2/3 bữa + tách thuế (BR C8.1-C8.2)."""
from decimal import Decimal

# C8.1 — số bữa/ngày theo nơi làm việc.
BUA_THEO_NOI = {
    "VP": 1,        # văn phòng
    "CT_GAN": 2,    # công trường/dự án < 30 km
    "CT_XA": 3,     # công trường/dự án >= 30 km
}


def so_bua(ngay: dict, p: dict) -> int:
    """Số bữa của một ngày. Ngày làm <= 4 tiếng: 0 bữa, mọi đối tượng [C8.1]."""
    noi = ngay["noi"]
    if noi not in BUA_THEO_NOI:
        raise ValueError(f"Nơi làm việc không hợp lệ: {noi!r}")
    if Decimal(str(ngay["gio"])) <= Decimal(str(p["meal_min_hours"])):
        return 0
    return BUA_THEO_NOI[noi]


def tong_suat_an(ngay_list: list, p: dict) -> int:
    """Tổng suất ăn cả kỳ — cộng theo từng ngày ngồi ở đâu, không theo phòng ban [C8.1, C17.4]."""
    return sum(so_bua(n, p) for n in ngay_list)


def meal_allow(tong_suat: int, p: dict) -> Decimal:
    """MEAL_ALLOW = tổng_suất × đơn giá [C8.1, C4.3]."""
    return Decimal(tong_suat) * Decimal(str(p["meal_unit_price"]))


def meal_nontax(allow: Decimal, p: dict) -> Decimal:
    """MEAL_NONTAX = MIN(MEAL_ALLOW, ngưỡng miễn thuế) [C8.2]."""
    return min(allow, Decimal(str(p["meal_tax_free"])))


def meal_tax(allow: Decimal, p: dict) -> Decimal:
    """MEAL_TAX = MAX(0, MEAL_ALLOW − ngưỡng miễn thuế) [C8.2]."""
    return max(Decimal(0), allow - Decimal(str(p["meal_tax_free"])))
