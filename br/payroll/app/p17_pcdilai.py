"""p17_pcdilai — PC đi lại: nhóm đối tượng x nơi tuyển dụng x tỉnh bộ phận -> dải
khoảng cách (dm_khoang_cach.csv) -> định mức (p03), pro-rata theo bộ phận thật
(p10) + quy tắc <14 ngày (C5.3.4). GĐDA loại trừ qua tờ trình (p04)."""

import csv
import os

from app.p03_dinhmuc import dinh_muc as tra_dinh_muc
from app.p04_totrinh import dinh_muc_cuoi
from app.p06_workday import ho_so
from app.p10_dieudong import tach_dieu_dong
from app.p13_prorata import tinh_prorata

CONG_CHUAN = 26
NGAY = "2026-07-09"
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "br", "data-draft")


def _tinh_theo_bo_phan():
    with open(os.path.join(_DATA_DIR, "dm_bo_phan.csv"), newline="", encoding="utf-8") as f:
        return {r["bo_phan"]: r["tinh"] for r in csv.DictReader(f)}


def _dai_theo_tinh(noi_tuyen_dung):
    out = {}
    with open(os.path.join(_DATA_DIR, "dm_khoang_cach.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["noi_tuyen_dung"] == noi_tuyen_dung:
                out[r["tinh_bo_phan"]] = r["dai_khoang_cach"]
    return out


def tinh_pc_di_lai(msnv, thang="2026-07"):
    tien_tt, nguon = dinh_muc_cuoi("di_lai", msnv, NGAY)
    if "GĐDA" in nguon:
        return {"tong": 0, "theo_bo_phan": {}, "trace": {"nguồn": nguon}}
    if nguon != "QĐ chung":
        return {"tong": tien_tt, "theo_bo_phan": {}, "trace": {"nguồn": nguon}}

    hs = ho_so(msnv)
    noi_tuyen = hs.get("noi_tuyen_dung", "TP.HCM")
    tinh_map = _tinh_theo_bo_phan()
    dai_map = _dai_theo_tinh(noi_tuyen)

    bp_split = {k: v for k, v in tach_dieu_dong(msnv, thang).items() if k != "ngay_dieu_dong"}
    tong_ngay_lv = sum(d["lam_viec"] for d in bp_split.values())
    duoi_14 = tong_ngay_lv < 14

    theo_bo_phan = {}
    trace = {}
    tong = 0
    for ten, d in bp_split.items():
        tinh = tinh_map.get(ten)
        dai = dai_map.get(tinh)
        dinh_muc_val = tra_dinh_muc("di_lai", hs, {"dai": dai})
        if duoi_14:
            # quy tắc <14 ngày: chỉ tính ngày LV thực tế + lễ (không phép/nghỉ khác)
            d = {"lam_viec": d["lam_viec"], "le": d.get("le", 0)}
        kq = tinh_prorata({ten: d}, CONG_CHUAN, lambda t, dm=dinh_muc_val: dm)
        theo_bo_phan[ten] = kq["tong"]
        trace[ten] = kq["trace"][ten]
        tong += kq["tong"]

    return {"tong": tong, "theo_bo_phan": theo_bo_phan, "trace": trace}
