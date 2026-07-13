"""thue.py — Thuế TNCN 5 bậc + case thử việc/expat (BR C12)."""
from decimal import Decimal

from app.baohiem import NUOC_NGOAI
from app.luong import CHINH_THUC, _dec, round0


def taxable_inc(taxable_gross, total_ins, total_ded) -> Decimal:
    """MAX(0, chịu thuế − bảo hiểm − giảm trừ) [C12.1]."""
    return max(Decimal(0), _dec(taxable_gross) - _dec(total_ins) - _dec(total_ded))


def total_ded(rec: dict, p: dict) -> Decimal:
    """Giảm trừ bản thân + NPT; thử việc không được giảm trừ [C4.4]."""
    if rec["CONTRACT_TYPE"] != CHINH_THUC:
        return Decimal(0)
    return round0(_dec(p["personal_ded"])
                  + _dec(p["dependent_ded"]) * _dec(rec.get("DEPENDENT_CNT", 0)))


def pit(taxable, rec: dict, p: dict) -> Decimal:
    """Thuế TNCN: biểu 5 bậc lũy tiến, thử việc khoán suất [C4.6, C12.2]."""
    inc = _dec(taxable)
    if inc <= 0:
        return Decimal(0)

    if rec["CONTRACT_TYPE"] != CHINH_THUC:
        if rec["NATIONALITY"] == NUOC_NGOAI:
            return round0(inc * _dec(p["pit_probation_foreign_rate"]))
        if inc < _dec(p["pit_probation_vn_threshold"]):
            return Decimal(0)
        return round0(inc * _dec(p["pit_probation_vn_rate"]))

    for tran, suat, tru in p["pit_brackets"]:
        if tran is None or inc <= _dec(tran):
            return max(Decimal(0), round0(inc * _dec(suat) - _dec(tru)))
    raise ValueError("Biểu thuế thiếu bậc cuối (trần None)")
