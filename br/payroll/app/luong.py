"""luong.py — Lương chính pro-rata, làm tròn half-up (BR C7, C13.5)."""
from decimal import Decimal, ROUND_HALF_UP

CHINH_THUC = "Chính thức"


def _dec(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


def round0(x: Decimal) -> Decimal:
    """ROUND() của Excel: half-up, KHÔNG phải round() half-even của Python [C13.5]."""
    return _dec(x).quantize(Decimal(1), rounding=ROUND_HALF_UP)


def _prorata(muc: Decimal, rec: dict) -> Decimal:
    """ROUND(mức / STD_DAYS × PAID_DAYS, 0)."""
    std = _dec(rec["STD_DAYS"])
    if not std:
        raise ValueError("STD_DAYS = 0 — không tính được đơn giá ngày")
    return round0(_dec(muc) / std * _dec(rec["PAID_DAYS"]))


def prob_earned(rec: dict, p: dict) -> Decimal:
    """Lương thử việc pro-rata; chính thức → 0 [C7.1]."""
    if rec["CONTRACT_TYPE"] == CHINH_THUC:
        return Decimal(0)
    return _prorata(rec.get("PROB_SAL", 0), rec)


def official_earned(rec: dict, p: dict) -> Decimal:
    """Lương chính thức pro-rata; thử việc → 0 [C7.1]."""
    if rec["CONTRACT_TYPE"] != CHINH_THUC:
        return Decimal(0)
    return _prorata(rec.get("BASIC_SAL", 0), rec)


def resp_earned(rec: dict, p: dict) -> Decimal:
    """Phụ cấp trách nhiệm cũng pro-rata theo ngày công [C7.2]."""
    return _prorata(rec.get("RESP_SAL", 0), rec)


def earned_sal(rec: dict, p: dict) -> Decimal:
    """As-is 4 thành phần: PROB + OFFICIAL + RESP + EARNED_PAID_LEAVE [C3.3, C7.3]."""
    return round0(
        prob_earned(rec, p)
        + official_earned(rec, p)
        + resp_earned(rec, p)
        + _dec(rec.get("EARNED_PAID_LEAVE", 0))
    )
