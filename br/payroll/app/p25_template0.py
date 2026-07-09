"""p25_template0 — Template 0 trình ký: định dạng chung Chính thức + Mắt Bão;
NV điều động gộp TOÀN BỘ công tháng vào bảng của dự án nơi làm việc ngày 20 (C6.3).
Tính THẬT từ công thô (p06/p07) cho TOÀN BỘ roster nhan_vien.csv, không danh sách cứng."""

import csv
import os

from app.p01_lichky import sinh_lich_ky
from app.p06_workday import cong_tho, ho_so
from app.p07_kyhieu import phan_loai

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "br", "data-draft")


def _toan_bo_msnv():
    with open(os.path.join(_DATA_DIR, "nhan_vien.csv"), newline="", encoding="utf-8") as f:
        return [r["msnv"] for r in csv.DictReader(f)]


def bang_trinh_ky(thang):
    ky = sinh_lich_ky(thang)
    ngay_20 = ky["den"]
    bang = {}

    for msnv in _toan_bo_msnv():
        rows = {r["ngay"]: r for r in cong_tho(thang) if r["msnv"] == msnv}
        if not rows:
            continue

        bo_phan_ngay20 = rows.get(ngay_20, {}).get(
            "bo_phan_trong_ngay") or ho_so(msnv).get("bo_phan_hien_tai", "?")

        tong_cong = 0.0
        for r in rows.values():
            thuoc_tinh = phan_loai(r["ky_hieu"])
            if thuoc_tinh["lam_viec_thuc_te"] or thuoc_tinh["huong_luong"]:
                tong_cong += 1.0

        bang.setdefault(bo_phan_ngay20, []).append({"msnv": msnv, "tong": tong_cong})

    return bang
