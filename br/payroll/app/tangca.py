"""tangca.py — OT là tiền input, không tự chế công thức giờ→tiền (BR C9)."""
from decimal import Decimal

from app.luong import _dec

# C9.3 — mỗi ngày đi làm được bao nhiêu ngày nghỉ bù.
NGHI_BU = {"ngay_lam_le": Decimal(2), "ngay_lam_truyen_thong": Decimal(1)}

# tên trường giờ → khoá hệ số trong params.ot_multipliers
HE_SO_CUA_GIO = {"gio_thuong": "weekday", "gio_dem": "night_extra", "gio_cn": "sunday"}


def ot_tax(rec: dict, p: dict) -> Decimal:
    """OT chịu thuế — SỐ TIỀN input, đi thẳng, không nhân hệ số [C9.1]."""
    return _dec(rec.get("OT_TAX", 0))


def ot_nontax(rec: dict, p: dict) -> Decimal:
    """OT không chịu thuế — SỐ TIỀN input, đi thẳng [C9.1]."""
    return _dec(rec.get("OT_NONTAX", 0))


def ot_tu_gio(gio: dict, p: dict) -> Decimal:
    """Quy giờ → tiền. Hệ số nào tài liệu không nói thì NÉM LỖI, không đoán [C9.1, C9.2]."""
    if not p.get("ot_from_hours"):
        raise ValueError("ot_from_hours đang TẮT — OT phải là số tiền input [C9.1]")
    he_so = p["ot_multipliers"]
    thieu = [k for k in gio if he_so.get(HE_SO_CUA_GIO.get(k, k)) is None]
    if thieu:
        raise ValueError(f"Thiếu hệ số OT cho {thieu} — không bịa [C9.2]")
    raise ValueError("Chưa có công thức giờ→tiền được duyệt [C9.1]")


def ngay_nghi_bu(rec: dict) -> Decimal:
    """Lễ/Tết → +2 ngày; ngày truyền thống công ty → +1 ngày [C9.3]."""
    return sum((_dec(rec.get(k, 0)) * v for k, v in NGHI_BU.items()), Decimal(0))
