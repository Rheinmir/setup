"""p16_pcxang — PC nhiên liệu/xăng/ô tô: CT chuẩn 1.000.000 (mọi bộ phận khối CT);
VP không mức chung (chỉ qua tờ trình — tài xế HN đích danh, GĐDA, Ban TGĐ); pro-rata
theo bộ phận thật (C5.3.3). Tờ trình LUÔN ưu tiên và ghi đè mức chuẩn (p04)."""

import csv
import os

from app.p04_totrinh import dinh_muc_cuoi
from app.p10_dieudong import tach_dieu_dong
from app.p13_prorata import tinh_prorata

CONG_CHUAN = 26
CT_CHUAN = 1_000_000
NGAY = "2026-07-09"
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "br", "data-draft")


def _khoi_theo_bo_phan():
    with open(os.path.join(_DATA_DIR, "dm_bo_phan.csv"), newline="", encoding="utf-8") as f:
        return {r["bo_phan"]: r["khoi"] for r in csv.DictReader(f)}


def tinh_pc_xang(msnv, thang="2026-07"):
    tien_tt, nguon = dinh_muc_cuoi("xang_xe", msnv, NGAY)
    if nguon != "QĐ chung":
        # Tờ trình đích danh MSNV ghi đè hoàn toàn, không chia theo bộ phận.
        bp_split = {k: v for k, v in tach_dieu_dong(msnv, thang).items() if k != "ngay_dieu_dong"}
        tong_ngay = sum(d["lam_viec"] + d["le"] for d in bp_split.values()) or CONG_CHUAN
        kq = tinh_prorata({msnv: {"lam_viec": tong_ngay}}, CONG_CHUAN, lambda t: tien_tt)
        return {"tong": kq["tong"], "trace": {**kq["trace"], "nguồn": nguon}}

    khoi_map = _khoi_theo_bo_phan()
    bp_split = {k: v for k, v in tach_dieu_dong(msnv, thang).items() if k != "ngay_dieu_dong"}
    theo_bo_phan = {}
    tong = 0
    for ten, d in bp_split.items():
        dinh_muc_val = CT_CHUAN if khoi_map.get(ten) == "CT" else 0
        kq = tinh_prorata({ten: d}, CONG_CHUAN, lambda t, dm=dinh_muc_val: dm)
        theo_bo_phan[ten] = kq["tong"]
        tong += kq["tong"]

    return {"tong": tong, "trace": {**theo_bo_phan, "nguồn": nguon}}
