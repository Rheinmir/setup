"""baohiem.py — BHXH/BHYT/BHTN + KPCĐ, hai trần, luật 14 ngày (BR C11)."""
from decimal import Decimal

from app.luong import CHINH_THUC, _dec, round0

NUOC_NGOAI = "Nước ngoài"

# Ngày nghỉ tính vào luật 14 ngày: thử việc + không lương + thai sản + ốm dài [C11.3]
EXEMPT_DAY_KEYS = ("PROB_DAYS", "UNPAID_DAYS", "MATERNITY_DAYS", "SI_DAYS")


def _chinh_thuc(rec: dict) -> bool:
    return rec["CONTRACT_TYPE"] == CHINH_THUC


def mien_dong_bhxh(rec: dict, p: dict) -> bool:
    """Tổng ngày nghỉ trong THÁNG DƯƠNG LỊCH >= 14 → tháng đó không trích đóng [C11.3]."""
    ngay = sum((_dec(rec.get(k, 0)) for k in EXEMPT_DAY_KEYS), Decimal(0))
    return ngay >= _dec(p["insurance_exempt_days"])


def _dong(rec: dict, p: dict) -> bool:
    """Có đóng bảo hiểm tháng này không [C11.1, C11.3, C11.4]."""
    return _chinh_thuc(rec) and not mien_dong_bhxh(rec, p) and not rec.get("no_insurance")


def ins_sal_bh(rec: dict, p: dict) -> Decimal:
    """Cột HIỂN THỊ — trần 50,6tr. KHÔNG dùng để tính tiền [C4.2]."""
    if not _chinh_thuc(rec):
        return Decimal(0)
    return min(_dec(rec["CONTRACT_TOTAL"]), _dec(p["ins_cap_bh_display"]))


def ins_base_bh(rec: dict, p: dict) -> Decimal:
    """Base TÍNH THẬT — trần 46,8tr; 7 công thức BH/KPCĐ/công đoàn đều ăn base này [C4.2, C11.1]."""
    if not _chinh_thuc(rec):
        return Decimal(0)
    return min(_dec(rec["CONTRACT_TOTAL"]), _dec(p["ins_cap_bh"]))


def ins_sal_ui(rec: dict, p: dict) -> Decimal:
    """Base BHTN — trần 106,2tr [C11.1]."""
    if not _chinh_thuc(rec):
        return Decimal(0)
    return min(_dec(rec["CONTRACT_TOTAL"]), _dec(p["ins_cap_ui"]))


def _khoan(base: Decimal, rate, adj) -> Decimal:
    return round0(base * _dec(rate) + _dec(adj))


def si_emp(rec: dict, p: dict) -> Decimal:
    """BHXH NLĐ 8% × base BH [C4.5, C11.2]."""
    if not _dong(rec, p):
        return Decimal(0)
    return _khoan(ins_base_bh(rec, p), p["si_emp"], rec.get("SI_ADJ", 0))


def hi_emp(rec: dict, p: dict) -> Decimal:
    """BHYT NLĐ 1,5% × base BH [C4.5, C11.2]."""
    if not _dong(rec, p):
        return Decimal(0)
    return _khoan(ins_base_bh(rec, p), p["hi_emp"], rec.get("HI_ADJ", 0))


def ui_emp(rec: dict, p: dict) -> Decimal:
    """BHTN NLĐ 1% × base BHTN; người nước ngoài KHÔNG đóng [C4.5, C11.4]."""
    if not _dong(rec, p) or rec.get("NATIONALITY") == NUOC_NGOAI:
        return Decimal(0)
    return _khoan(ins_sal_ui(rec, p), p["ui_emp"], rec.get("UI_ADJ", 0))


def total_ins(rec: dict, p: dict) -> Decimal:
    """Tổng bảo hiểm NLĐ [C11.2]."""
    return si_emp(rec, p) + hi_emp(rec, p) + ui_emp(rec, p)


def si_cty(rec: dict, p: dict) -> Decimal:
    """BHXH công ty 17% × base BH [C4.5]."""
    if not _dong(rec, p):
        return Decimal(0)
    return _khoan(ins_base_bh(rec, p), p["si_cty"], rec.get("SI_CTY_ADJ", 0))


def tnld_cty(rec: dict, p: dict) -> Decimal:
    """TNLĐ-BNN 0,5% × base BH — trần BH 46,8tr, KHÔNG phải trần BHTN [C3.3, C4.5]."""
    if not _dong(rec, p):
        return Decimal(0)
    return _khoan(ins_base_bh(rec, p), p["tnld_cty"], rec.get("TNLD_CTY_ADJ", 0))


def hi_cty(rec: dict, p: dict) -> Decimal:
    """BHYT công ty 3% × base BH [C4.5]."""
    if not _dong(rec, p):
        return Decimal(0)
    return _khoan(ins_base_bh(rec, p), p["hi_cty"], rec.get("HI_CTY_ADJ", 0))


def ui_cty(rec: dict, p: dict) -> Decimal:
    """BHTN công ty 1% × base BHTN [C4.5, C11.2]."""
    if not _dong(rec, p):
        return Decimal(0)
    return _khoan(ins_sal_ui(rec, p), p["ui_cty"], rec.get("UI_CTY_ADJ", 0))


def total_ins_cty(rec: dict, p: dict) -> Decimal:
    """Tổng bảo hiểm công ty (KHÔNG gồm KPCĐ) [C4.5]."""
    return si_cty(rec, p) + tnld_cty(rec, p) + hi_cty(rec, p) + ui_cty(rec, p)


def kpcd_cty(rec: dict, p: dict) -> Decimal:
    """KPCĐ 2% × base BH → 936.000 (không phải BASIC_SAL × 2%) [C3.3, C4.5]."""
    return round0(ins_base_bh(rec, p) * _dec(p["kpcd_cty"]))


def union_fee(rec: dict, p: dict) -> Decimal:
    """Phí công đoàn NLĐ: MIN(base BH × 0,5%, 253.000) [C3.3, C4.5]."""
    return min(round0(ins_base_bh(rec, p) * _dec(p["union_fee_rate"])),
               _dec(p["union_fee_cap"]))
