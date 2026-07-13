"""chamcong.py — Ký hiệu chấm công + PAID_DAYS lớp as-is (BR C6)."""
from decimal import Decimal

# C6.1 — bộ ký hiệu công. True = được cộng vào công hưởng lương (C6.2).
KY_HIEU = {
    "x": True,     # làm việc
    "x1": True,    # lương thời gian
    "OL": True,    # ốm hưởng lương Cty
    "P": True,     # phép năm
    "F": True,
    "R": True,     # việc riêng có lương
    "Fo": True,
    "L": True,     # lễ
    "NB": True,    # nghỉ bù
    "Ts": False,   # thai sản
    "TSN": False,
    "ON": False,   # ốm BHXH — as-is không cộng
    "OD": False,
    "TN": False,   # tai nạn
    "Ro": False,   # không lương
    "?P": False,   # chờ duyệt — C6.2
}

# C3.3/C6.3 — as-is: KHÔNG cộng SI_DAYS, ADJ_DAYS.
_CONG_THEM = ("PAID_LEAVE_DAYS", "HOLIDAY_DAYS", "COMP_DAYS", "PAID_OTHER_DAYS", "BEREAVE_DAYS")


def tinh_cong_huong_luong(ky_hieu: str) -> bool:
    """Ký hiệu có được cộng vào công hưởng lương không [C6.2]."""
    if ky_hieu not in KY_HIEU:
        raise ValueError(f"Ký hiệu chấm công không hợp lệ: {ky_hieu!r}")
    return KY_HIEU[ky_hieu]


def paid_days(rec: dict) -> Decimal:
    """IF(chính thức, OFFICIAL_DAYS, PROB_DAYS) + PAID_LEAVE + HOLIDAY + COMP + PAID_OTHER + BEREAVE [C6.3]."""
    goc = "OFFICIAL_DAYS" if rec["CONTRACT_TYPE"] == "Chính thức" else "PROB_DAYS"
    tong = Decimal(str(rec[goc]))
    for k in _CONG_THEM:
        tong += Decimal(str(rec[k]))
    return tong
