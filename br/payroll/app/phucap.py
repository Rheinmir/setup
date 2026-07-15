"""phucap.py — Phụ cấp pro-rata + luật <14 ngày + điều động (BR C8.3-C8.7)."""
from decimal import Decimal

from app.luong import _dec, round0

lam_tron = round0

# C8.7 — định mức chung theo (loại, level) × khối. None = chưa có số → ném lỗi, không đoán.
DINH_MUC_CHUNG = {
    ("dien_thoai", "QL.01"): {"VP": Decimal(1_000_000), "CT": Decimal(1_000_000)},
    ("dien_thoai", "NV.03"): {"VP": Decimal(200_000), "CT": Decimal(300_000)},
    # C8.6 — khối VP KHÔNG có định mức chung phụ cấp xăng (chỉ theo tờ trình).
    ("xang", None): {"VP": Decimal(0), "CT": Decimal(1_000_000)},
}


def dinh_muc(loai: str, level: str, khoi: str, to_trinh: dict = None) -> Decimal:
    """Định mức tháng; tờ trình duyệt riêng ghi đè định mức chung [C8.6, C8.7]."""
    if to_trinh:
        return _dec(to_trinh["dinh_muc"])
    for key in ((loai, level), (loai, None)):
        if key in DINH_MUC_CHUNG:
            bang = DINH_MUC_CHUNG[key]
            if khoi not in bang:
                raise ValueError(f"Khối không hợp lệ: {khoi!r}")
            return bang[khoi]
    raise ValueError(f"Chưa có định mức chung cho {loai!r} / {level!r}")


def prorata(dm: Decimal, ngay: Decimal, cong_chuan: Decimal) -> Decimal:
    """phụ_cấp = định_mức / công_chuẩn × ngày_hưởng [C8.3]."""
    cc = _dec(cong_chuan)
    if not cc:
        raise ValueError("Công chuẩn = 0 — không tính được pro-rata")
    return lam_tron(_dec(dm) / cc * _dec(ngay))


def ngay_huong(seg: dict, p: dict, tong_ngay_lam_viec=None) -> Decimal:
    """Ngày hưởng của một đoạn công tác.

    Luật <14 ngày xét trên TỔNG ngày làm việc thực tế CẢ KỲ, không xét riêng
    từng bộ phận: < 14 → chỉ (làm việc + lễ), bỏ phép/không lương [C8.4, C8.5].
    """
    lv = _dec(seg["ngay_lam_viec"])
    tong = lv if tong_ngay_lam_viec is None else _dec(tong_ngay_lam_viec)
    ngay = lv + _dec(seg["ngay_le"])
    if tong >= _dec(p["allowance_min_days_rule"]):
        ngay += _dec(seg["ngay_phep"])
    return ngay


def phu_cap_dieu_dong(segs: list, cong_chuan: Decimal, p: dict) -> Decimal:
    """Chia ngày thực tế theo từng bộ phận, áp định mức của nơi đó [C8.5, C17.4]."""
    cc = _dec(cong_chuan)
    if not cc:
        raise ValueError("Công chuẩn = 0 — không tính được pro-rata")
    tong_lv = sum((_dec(s["ngay_lam_viec"]) for s in segs), Decimal(0))
    tong = sum(
        (ngay_huong(s, p, tong_lv) / cc * _dec(s["dinh_muc"]) for s in segs),
        Decimal(0),
    )
    return lam_tron(tong)


def truy_thu(e: dict, p: dict) -> Decimal:
    """Phụ cấp truy thu/truy lĩnh (hồi tố) [C8.8/FE-06].

    = (định mức mới − định mức cũ) / công chuẩn × số ngày công tương ứng
    (PRD v2.1 §4.3 — "Truy thu/Truy lĩnh trước khóa kỳ"). Không có ca truy
    thu (không khai RETRO_OLD_RATE/RETRO_NEW_RATE) → trả 0.

    Bắt buộc lý do (RETRO_REASON) + số ngày tương ứng (RETRO_DAYS) khi có ca
    — không âm thầm đoán, ném lỗi để người nhập phải khai đủ.

    Phạm vi lô đầu: hàm này KHÔNG kiểm được điều kiện "kỳ chưa khoá" vì FE-15
    (khoá kỳ) nằm ngoài phạm vi (BR C19) — coi như mọi kỳ đang tính đều mở.
    """
    old, new = e.get("RETRO_OLD_RATE"), e.get("RETRO_NEW_RATE")
    # "not old and not new" (không phải "is None"): gọi qua engine DAG (deps đã
    # khai) thì field vắng mặt bị _resolve tự default thành Decimal(0) TRƯỚC
    # khi hàm này chạy — 0/None đều coi là "không có ca truy thu"
    if not old and not new:
        return Decimal(0)
    if not (e.get("RETRO_REASON") or "").strip():
        raise ValueError("PC_TRUY_THU: có định mức cũ/mới nhưng thiếu RETRO_REASON (bắt buộc)")
    if e.get("RETRO_DAYS") is None:
        raise ValueError("PC_TRUY_THU: có định mức cũ/mới nhưng thiếu RETRO_DAYS (bắt buộc)")
    cc = _dec(e.get("STD_DAYS", 0))
    if not cc:
        raise ValueError("Công chuẩn = 0 — không tính được truy thu")
    delta = _dec(new or 0) - _dec(old or 0)
    return lam_tron(delta / cc * _dec(e["RETRO_DAYS"]))
