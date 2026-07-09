"""Tổng hợp suất ăn theo bộ phận (C5.1.5, C5.3.1, C5.4) — tính THẬT từ công thô
(p06), dm_bo_phan.csv (khối), dm_khoang_cach.csv (dải), suat_an_bo_sung.csv
(cơm TC đêm/CN thư ký chấm). Quy tắc bữa: VP 1 · CT<30km 2 · CT≥30km 3 · ngày
≤4h/ngày 0 suất."""

import csv
import os

from app.p06_workday import cong_tho, ho_so

SUAT_VP = 1
SUAT_CT_GAN = 2   # <30km
SUAT_CT_XA = 3    # >=30km

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "br", "data-draft")


def _doc_csv(ten_file):
    path = os.path.join(_DATA_DIR, ten_file)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _khoi_theo_bo_phan():
    return {r["bo_phan"]: r["khoi"] for r in _doc_csv("dm_bo_phan.csv")}


def _dai_theo_tinh(noi_tuyen_dung):
    out = {}
    for r in _doc_csv("dm_khoang_cach.csv"):
        if r["noi_tuyen_dung"] == noi_tuyen_dung:
            out[r["tinh_bo_phan"]] = r["dai_khoang_cach"]
    return out


def _tinh_theo_bo_phan():
    return {r["bo_phan"]: r["tinh"] for r in _doc_csv("dm_bo_phan.csv")}


def _suat_bua(bo_phan, noi_tuyen_dung, khoi_map, tinh_map, dai_map):
    khoi = khoi_map.get(bo_phan)
    if khoi == "VP":
        return SUAT_VP
    tinh = tinh_map.get(bo_phan)
    dai = dai_map.get(tinh)
    return SUAT_CT_GAN if dai == "<30" else SUAT_CT_XA


def tong_hop_suat_an(msnv, thang="2026-07"):
    hs = ho_so(msnv)
    noi_tuyen = hs.get("noi_tuyen_dung", "TP.HCM")
    khoi_map = _khoi_theo_bo_phan()
    tinh_map = _tinh_theo_bo_phan()
    dai_map = _dai_theo_tinh(noi_tuyen)

    bo_sung = [r for r in _doc_csv("suat_an_bo_sung.csv") if r["msnv"] == msnv]

    ket_qua = {}
    for r in cong_tho(thang):
        if r["msnv"] != msnv:
            continue
        bo_phan = r["bo_phan_trong_ngay"]
        so_gio = float(r["so_gio"] or 0)
        d = ket_qua.setdefault(bo_phan, {"tong": 0, "suat_cn_le": 0})
        if so_gio <= 4:
            continue
        d["tong"] += _suat_bua(bo_phan, noi_tuyen, khoi_map, tinh_map, dai_map)

    for r in bo_sung:
        so_suat = int(r["so_suat"])
        # cơm bổ sung ghi theo msnv+ngày, cộng vào bộ phận NV đang làm hôm đó
        ngay = r["ngay"]
        bp_hom_do = next((rr["bo_phan_trong_ngay"] for rr in cong_tho(thang)
                           if rr["msnv"] == msnv and rr["ngay"] == ngay), None)
        if bp_hom_do is None and ket_qua:
            bp_hom_do = next(iter(ket_qua))
        if bp_hom_do:
            d = ket_qua.setdefault(bp_hom_do, {"tong": 0, "suat_cn_le": 0})
            d["tong"] += so_suat
            if r["loai"] == "com_chu_nhat":
                d["suat_cn_le"] += so_suat

    return ket_qua
