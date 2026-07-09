"""p18_pcctctx — PC công trường + công tác xa: bảng khối (CT/VP) x dải khoảng cách
x 2 đối tượng (ĐH+ / CĐ-TC-Nghề), tra dinh_muc_ct_congtacxa.csv thật; pro-rata +
<14 ngày + chia bộ phận thật (p10) (C5.3.5). GĐDA loại trừ (C5.3.7)."""

import csv
import os

from app.p06_workday import ho_so
from app.p10_dieudong import tach_dieu_dong
from app.p13_prorata import tinh_prorata

CONG_CHUAN = 26
GDDA = {"NV007"}
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "br", "data-draft")
_CD_TC_NGHE = {"Cao đẳng", "Trung cấp", "Nghề"}

# dm_khoang_cach.csv có 6 dải chi tiết hơn bảng CT+CTX (4 dải) — quy đổi.
_QUY_DOI_DAI = {
    "<30": "<30", "30-100": "30-100", "100-400": ">100_phu_quoc",
    "phu_quoc": ">100_phu_quoc", "khac_mien": "khac_mien_mien_trung",
    "mien_trung": "khac_mien_mien_trung", "nam_trung_bo": "khac_mien_mien_trung",
}


def _grid():
    with open(os.path.join(_DATA_DIR, "dinh_muc_ct_congtacxa.csv"), newline="", encoding="utf-8") as f:
        out = {}
        for r in csv.DictReader(f):
            out[(r["khoi"], r["dai_khoang_cach"])] = {
                "dh": int(r["doi_tuong_1_dh"]), "cd": int(r["doi_tuong_2_cd_tc_nghe"])}
        return out


def _khoi_theo_bo_phan():
    with open(os.path.join(_DATA_DIR, "dm_bo_phan.csv"), newline="", encoding="utf-8") as f:
        return {r["bo_phan"]: (r["khoi"], r["tinh"]) for r in csv.DictReader(f)}


def _dai_theo_tinh(noi_tuyen_dung):
    out = {}
    with open(os.path.join(_DATA_DIR, "dm_khoang_cach.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["noi_tuyen_dung"] == noi_tuyen_dung:
                out[r["tinh_bo_phan"]] = r["dai_khoang_cach"]
    return out


def tinh_pc_ct_ctx(msnv, thang="2026-07"):
    if msnv in GDDA:
        return {"tong": 0, "theo_bo_phan": {},
                "trace": {"nguồn": "GĐDA bị loại khỏi PC công trường/công tác xa chung"}}

    hs = ho_so(msnv)
    doi_tuong = "cd" if hs.get("trinh_do") in _CD_TC_NGHE else "dh"
    noi_tuyen = hs.get("noi_tuyen_dung", "TP.HCM")
    khoi_map = _khoi_theo_bo_phan()
    dai_map = _dai_theo_tinh(noi_tuyen)
    grid = _grid()

    bp_split = {k: v for k, v in tach_dieu_dong(msnv, thang).items() if k != "ngay_dieu_dong"}
    tong_ngay_lv = sum(d["lam_viec"] for d in bp_split.values())
    duoi_14 = tong_ngay_lv < 14

    theo_bo_phan = {}
    trace = {}
    tong = 0
    for ten, d in bp_split.items():
        khoi, tinh = khoi_map.get(ten, ("VP", None))
        dai_tho = dai_map.get(tinh, "<30")
        dai = _QUY_DOI_DAI.get(dai_tho, "<30")
        dinh_muc_val = grid.get((khoi, dai), {}).get(doi_tuong, 0)
        if duoi_14:
            d = {"lam_viec": d["lam_viec"], "le": d.get("le", 0)}
        kq = tinh_prorata({ten: d}, CONG_CHUAN, lambda t, dm=dinh_muc_val: dm)
        theo_bo_phan[ten] = kq["tong"]
        trace[ten] = kq["trace"][ten]
        tong += kq["tong"]

    return {"tong": tong, "theo_bo_phan": theo_bo_phan, "trace": trace}
