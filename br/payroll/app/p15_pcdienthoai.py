"""p15_pcdienthoai — PC điện thoại: tra bảng ngạch × VP/CT (p03), áp engine
pro-rata (p13), chia theo bộ phận (p10, điều động) hoặc theo giai đoạn thử
việc/chính thức (p08) khi NV chỉ ở 1 bộ phận trong kỳ (C5.3.2)."""

import csv
import os

from app.p01_lichky import sinh_lich_ky
from app.p03_dinhmuc import DIEN_THOAI_TABLE
from app.p06_workday import ho_so
from app.p08_thuviec import tach_thu_viec
from app.p10_dieudong import tach_dieu_dong
from app.p13_prorata import tinh_prorata

CONG_CHUAN = 26
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "br", "data-draft")


def _khoi_theo_bo_phan():
    with open(os.path.join(_DATA_DIR, "dm_bo_phan.csv"), newline="", encoding="utf-8") as f:
        return {r["bo_phan"]: r["khoi"] for r in csv.DictReader(f)}


def _doan_theo_ky(msnv, thang, bp_split):
    """Trả list (tên_đoạn, ngạch, lam_viec): điều động (>1 bộ phận) → mỗi bộ phận
    1 đoạn cùng ngạch hồ sơ; 1 bộ phận + có mốc kết thúc thử việc trong kỳ → tách
    2 đoạn TV/chính thức theo p08."""
    hs = ho_so(msnv)
    ngach = hs.get("ngach")
    ket_thuc_tv = hs.get("ngay_ket_thuc_thu_viec") or ""

    ky = sinh_lich_ky(thang)
    tv_trong_ky = bool(ket_thuc_tv) and ky["tu"] <= ket_thuc_tv <= ky["den"]
    if len(bp_split) == 1 and tv_trong_ky:
        tv = tach_thu_viec(msnv, thang)
        bo_phan_ten = next(iter(bp_split))
        doan = []
        if tv["ngay_tv"]["lam_viec"] > 0:
            doan.append((f"{bo_phan_ten} (thử việc)", "TV", tv["ngay_tv"]["lam_viec"]))
        if tv["ngay_sau_tv"]["lam_viec"] > 0:
            doan.append((f"{bo_phan_ten} (chính thức)", ngach, tv["ngay_sau_tv"]["lam_viec"]))
        if doan:
            return doan, bo_phan_ten

    return [(ten, ngach, d["lam_viec"]) for ten, d in bp_split.items()], None


def tinh_pc_dien_thoai(msnv, thang="2026-07"):
    khoi_map = _khoi_theo_bo_phan()
    bp_split = {k: v for k, v in tach_dieu_dong(msnv, thang).items() if k != "ngay_dieu_dong"}
    doan, bo_phan_goc = _doan_theo_ky(msnv, thang, bp_split)

    theo_bo_phan = {}
    trace = {}
    tong = 0
    for ten, ngach, lam_viec in doan:
        khoi = khoi_map.get(bo_phan_goc or ten, "VP")
        dinh_muc_val = DIEN_THOAI_TABLE.get(ngach, {}).get(khoi, 0)
        kq = tinh_prorata({ten: {"lam_viec": lam_viec}}, CONG_CHUAN,
                           lambda t, dm=dinh_muc_val: dm)
        theo_bo_phan[ten] = kq["tong"]
        trace[ten] = kq["trace"][ten]
        tong += kq["tong"]

    return {"tong": tong, "theo_bo_phan": theo_bo_phan, "trace": trace,
            "giai_doan": [ten for ten, _, _ in doan]}
