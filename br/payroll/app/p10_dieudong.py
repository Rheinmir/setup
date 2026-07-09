"""p10_dieudong — tách công theo bộ phận khi điều động giữa kỳ (C5.1.3)."""

from app.p06_workday import cong_tho
from app.p07_kyhieu import phan_loai

_LOAI_TU_KY_HIEU = {
    True: "lam_viec",   # lam_viec_thuc_te
}


def _phan_loai_ngay(ky_hieu):
    """Ký hiệu → loại ngày dùng cho ma trận bộ_phận×loại_ngày (C5.1.3)."""
    if ky_hieu in ("P", "F"):
        return "phep"
    if ky_hieu in ("R", "Fo"):
        return "nghi_huong_luong"
    if ky_hieu == "Ro":
        return "khong_luong"
    thuoc_tinh = phan_loai(ky_hieu)
    if thuoc_tinh["lam_viec_thuc_te"]:
        return "lam_viec"
    if thuoc_tinh["huong_luong"]:
        return "nghi_huong_luong"
    return "khong_luong"


def gom_theo_bo_phan(rows):
    """Engine thuần: list bản ghi {ngay, ky_hieu, bo_phan} (đã lọc đúng 1 NV) →
    dict bộ_phận → {lam_viec, le, phep, nghi_huong_luong, khong_luong, tong} +
    ngày điều động (ngày đầu tiên bộ phận đổi so với bản ghi trước đó, sắp theo ngày)."""
    ket_qua = {}
    rows_sorted = sorted(rows, key=lambda r: r["ngay"])
    ngay_dieu_dong = None
    bo_phan_truoc = None
    for r in rows_sorted:
        bp = r["bo_phan"]
        if bo_phan_truoc is not None and bp != bo_phan_truoc and ngay_dieu_dong is None:
            ngay_dieu_dong = r["ngay"]
        bo_phan_truoc = bp

        d = ket_qua.setdefault(bp, {"lam_viec": 0, "le": 0, "phep": 0,
                                     "nghi_huong_luong": 0, "khong_luong": 0, "tong": 0})
        kh = r["ky_hieu"]
        if kh.startswith("TC") and kh not in ("P", "F", "R", "Fo", "Ro"):
            # đi làm lễ/CN (TC100/200/300) — cột "lễ" TÁCH BIỆT khỏi "làm việc"
            # thường (PRD Ví dụ 2: 3 làm việc + ... + 2 lễ cộng dồn thành 15, không
            # lồng nhau).
            d["le"] += 1
        else:
            loai = _phan_loai_ngay(kh)
            d[loai] += 1
        d["tong"] += 1

    if ngay_dieu_dong:
        ket_qua["ngay_dieu_dong"] = ngay_dieu_dong
    return ket_qua


def tach_dieu_dong(msnv, thang="2026-07"):
    """Đọc công thô THẬT từ Workday adapter (p06), lọc đúng 1 NV, gom theo bộ phận.
    Tổng quát cho BẤT KỲ msnv nào có bản ghi trong `cong_tho(thang)`."""
    rows = [{"ngay": r["ngay"], "ky_hieu": r["ky_hieu"], "bo_phan": r["bo_phan_trong_ngay"]}
            for r in cong_tho(thang) if r["msnv"] == msnv]
    return gom_theo_bo_phan(rows)
