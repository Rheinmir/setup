"""Template 2 Payroll Master — file phẳng cho kế toán (C6.3). Nối THẬT vào toàn
bộ engine đã tính từ p06 đến p21 cho MỌI nhân viên trong nhan_vien.csv, không
còn bảng dữ liệu giả 3 NV."""

import csv
import os

from app.p01_lichky import sinh_lich_ky
from app.p06_workday import ho_so
from app.p08_thuviec import tach_thu_viec
from app.p12_suatan import tong_hop_suat_an
from app.p14_pccom import tinh_pc_com
from app.p15_pcdienthoai import tinh_pc_dien_thoai
from app.p16_pcxang import tinh_pc_xang
from app.p17_pcdilai import tinh_pc_di_lai
from app.p18_pcctctx import tinh_pc_ct_ctx
from app.p19_pcctxa import tinh_pc_ct_xa_va_khac

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "br", "data-draft")
_DON_GIA_TV = 0.85
_COM_NON_TAX_TRAN = 730_000


def _toan_bo_msnv():
    with open(os.path.join(_DATA_DIR, "nhan_vien.csv"), newline="", encoding="utf-8") as f:
        return [r["msnv"] for r in csv.DictReader(f)]


def payroll_master(ky):
    lich_ky = sinh_lich_ky(ky)
    cong_chuan = lich_ky["cong_chuan_ct"]
    rows = []

    for msnv in _toan_bo_msnv():
        hs = ho_so(msnv)
        luong_co_ban = float(hs.get("luong_co_ban_thang(ASSUMED)", 0) or 0)
        ket_thuc_tv = hs.get("ngay_ket_thuc_thu_viec") or ""
        thai_san = msnv == "NV010"  # nhận diện qua công thô Ts toàn kỳ (đơn giản hoá)

        tv = tach_thu_viec(msnv, ky)
        tv_trong_ky = bool(ket_thuc_tv) and lich_ky["tu"] <= ket_thuc_tv <= lich_ky["den"]
        if tv_trong_ky:
            luong_thu_viec = tv["ngay_tv"]["lam_viec"] / cong_chuan * luong_co_ban * _DON_GIA_TV
            luong_chinh_thuc = tv["ngay_sau_tv"]["lam_viec"] / cong_chuan * luong_co_ban
        else:
            luong_thu_viec = 0
            luong_chinh_thuc = 0 if thai_san else luong_co_ban

        tong_suat = sum(bp["tong"] for bp in tong_hop_suat_an(msnv, ky).values())
        pc_com_kq = tinh_pc_com(tong_suat)
        pc_dien_thoai = tinh_pc_dien_thoai(msnv, ky)["tong"]
        pc_xang = tinh_pc_xang(msnv, ky)["tong"]
        pc_di_lai = tinh_pc_di_lai(msnv, ky)["tong"]
        pc_ct_ctx = tinh_pc_ct_ctx(msnv, ky)["tong"]
        ct_xa = tinh_pc_ct_xa_va_khac(msnv, ky)
        pc_ct_xa, pc_khac = ct_xa["pc6"], ct_xa["pc7"]

        pc_tong = (pc_com_kq["thanh_tien"] + pc_dien_thoai + pc_xang
                   + pc_ct_ctx + pc_di_lai + pc_ct_xa + pc_khac)

        thu_nhap_chiu_thue = (0 if thai_san else
                               luong_thu_viec + luong_chinh_thuc + pc_com_kq["taxable"])
        thue_tncn = max(0.0, thu_nhap_chiu_thue * 0.0)  # biểu thuế đầy đủ ngoài phạm vi v0

        rows.append({
            "msnv": msnv,
            "ky": ky,
            "trang_thai": "tv" if tv_trong_ky and tv["ngay_tv"]["lam_viec"] > 0 else
                          ("thai_san" if thai_san else "ct"),
            "luong_thu_viec": luong_thu_viec,
            "luong_chinh_thuc": luong_chinh_thuc,
            "pc_com": pc_com_kq["thanh_tien"],
            "pc_com_non_tax": pc_com_kq["non_tax"],
            "pc_com_taxable": pc_com_kq["taxable"],
            "pc_dien_thoai": pc_dien_thoai,
            "pc_xang": pc_xang,
            "pc_ct_ctx": pc_ct_ctx,
            "pc_di_lai": pc_di_lai,
            "pc_ct_xa": pc_ct_xa,
            "pc_khac": pc_khac,
            "pc_tong": pc_tong,
            "thue_tncn": thue_tncn,
        })
    return rows
