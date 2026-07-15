"""tonghop.py — GROSS → NET_PAY → chi phí công ty (BR C13)."""
from decimal import Decimal

from app.luong import _dec, round0

# C13.1 — as-is: SUM quét cả cột ADJ_MINUS nên nó được CỘNG (HR nhập số âm để trừ).
_GROSS_CODES = (
    "EARNED_SAL",
    "MEAL_TAX", "MEAL_NONTAX", "PHONE_ALLOW", "PHONE_NONTAX",
    "FUEL_ALLOW", "FUEL_NONTAX", "TRANSPORT_TAX", "TRANSPORT_NONTAX",
    "LIVING_ALLOW", "LIVING_NONTAX", "OTHER_ALLOW_TAX", "OTHER_ALLOW_NONTAX",
    "OT_TAX", "OT_NONTAX", "BONUS_TOTAL", "TOTAL_SUPPORT",
    "ADJ_PLUS", "ADJ_MINUS", "PC_TRUY_THU",
)

_NONTAX_CODES = (
    "MEAL_NONTAX", "PHONE_NONTAX", "FUEL_NONTAX", "TRANSPORT_NONTAX",
    "LIVING_NONTAX", "OTHER_ALLOW_NONTAX", "OT_NONTAX",
    "SEVER_ALLOW", "SI_BENEFIT", "BONUS_TRAVEL",
    "CHARITY_DED", "EARNED_PAID_LEAVE",
)


def _sum(rec: dict, codes) -> Decimal:
    return sum((_dec(rec.get(c, 0)) for c in codes), Decimal(0))


def gross(rec: dict, p: dict) -> Decimal:
    """Tổng thu nhập [C13.1]."""
    return round0(_sum(rec, _GROSS_CODES))


def taxable_gross(rec: dict, gross_amt, p: dict) -> Decimal:
    """Thu nhập chịu thuế = GROSS − mọi khoản không chịu thuế [C13.2]."""
    return round0(_dec(gross_amt) - _sum(rec, _NONTAX_CODES))


def net_income(gross, total_ins, total_pit) -> Decimal:
    """Thu nhập thuần = GROSS − bảo hiểm − thuế [C17.1]."""
    return round0(_dec(gross) - _dec(total_ins) - _dec(total_pit))


def net_pay(gross, total_ins, total_pit, total_post_ded, total_post_add) -> Decimal:
    """Lương thực nhận [C13.3]."""
    return round0(_dec(gross) - _dec(total_ins) - _dec(total_pit)
                  - _dec(total_post_ded) + _dec(total_post_add))


def total_cty_cost(net_pay, total_ins_cty, kpcd_cty) -> Decimal:
    """Chi phí công ty — as-is tính trên NET_PAY, không phải GROSS [C13.4]."""
    return round0(_dec(net_pay) + _dec(total_ins_cty) + _dec(kpcd_cty))


def budget_save(gross, total_ins_cty, kpcd_cty, trich_quy) -> Decimal:
    """Quỹ dự phòng = GROSS + BH công ty + KPCĐ + các khoản trích [C10.2]."""
    return round0(_dec(gross) + _dec(total_ins_cty) + _dec(kpcd_cty)
                  + sum((_dec(x) for x in trich_quy), Decimal(0)))
