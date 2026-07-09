#!/usr/bin/env python3
"""Sinh dữ liệu NGẪU NHIÊN (~80 NV, đủ chấm công 1 kỳ) để stress-test app payroll
với quy mô lớn hơn 12 NV mẫu — KHÔNG đụng vào br/data-draft/ thật (nguồn PRD/HR),
ghi ra br/data-draft/stress-test/ riêng.

Chạy: python3 gen_random_data.py [--n-nv 80] [--seed 42]
Dùng thử: python3 gen_random_data.py --apply   (backup data-draft/ thật rồi thay bằng bản random)
Khôi phục: python3 gen_random_data.py --restore
"""
import argparse
import csv
import os
import random
import shutil
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REAL_DIR = os.path.join(_HERE, "br", "data-draft")
_OUT_DIR = os.path.join(_REAL_DIR, "stress-test")
_BACKUP_DIR = os.path.join(_HERE, "br", "data-draft.backup")

BO_PHAN = [
    ("VP HCM", "TP.HCM", "VP", "Nam"),
    ("VP Hà Nội", "Hà Nội", "VP", "Bắc"),
    ("CT Quan Lạn", "Quảng Ninh", "CT", "Bắc"),
    ("CT Long An", "Long An", "CT", "Nam"),
    ("CT Bình Dương", "Bình Dương", "CT", "Nam"),
    ("CT Đà Nẵng", "Đà Nẵng", "CT", "Trung"),
]
NGACH_VP = ["QL.01", "QL.02", "QL.03", "CV.01", "CV.02", "NV.01", "NV.02", "NV.03"]
TRINH_DO = ["Đại học", "Cao đẳng", "Trung cấp", "Nghề"]
CHUC_DANH = ["Kế toán", "Nhân sự", "GS", "CV", "Thủ kho", "Tài xế", "Admin", "NV hành chính"]
HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đặng", "Bùi", "Đỗ", "Hồ"]
TEN_DEM = ["Văn", "Thị", "Minh", "Quốc", "Thu", "Hữu", "Ngọc"]
TEN = ["An", "Bình", "Cường", "Dũng", "Em", "Phong", "Giang", "Hải", "Hà", "Kim", "Lâm", "Long"]
KY_HIEU_THUONG = ["x"] * 20 + ["P", "R", "L", "OL"]


def _random_ten():
    return f"{random.choice(HO)} {random.choice(TEN_DEM)} {random.choice(TEN)}"


def sinh_nhan_vien(n, rng):
    rows = []
    for i in range(1, n + 1):
        msnv = f"NVR{i:03d}"
        bo_phan = rng.choice(BO_PHAN)[0]
        employee_type = "MatBao" if rng.random() < 0.12 else "Official"
        nam_vao = rng.randint(2018, 2025)
        thang_vao = rng.randint(1, 12)
        ngay_vao = f"{nam_vao:04d}-{thang_vao:02d}-{rng.randint(1,28):02d}"
        rows.append({
            "msnv": msnv, "ho_ten": _random_ten(),
            "ngach": rng.choice(NGACH_VP), "trinh_do": rng.choice(TRINH_DO),
            "chuc_danh": rng.choice(CHUC_DANH), "employee_type": employee_type,
            "bo_phan_hien_tai": bo_phan, "noi_tuyen_dung": "TP.HCM",
            "noi_cu_tru": "TP.HCM", "ngay_vao": ngay_vao,
            "ngay_ket_thuc_thu_viec": f"{nam_vao:04d}-{min(thang_vao+2,12):02d}-15",
            "luong_co_ban_thang(ASSUMED)": rng.choice(range(9_000_000, 35_000_000, 1_000_000)),
            "ghi_chu": "sinh ngẫu nhiên — stress-test",
        })
    return rows


def sinh_cong_tho(nv_rows, rng):
    rows = []
    for nv in nv_rows:
        bo_phan = nv["bo_phan_hien_tai"]
        for d in range(21, 31):
            rows.append({"msnv": nv["msnv"], "ngay": f"2026-06-{d:02d}",
                         "ky_hieu": rng.choice(KY_HIEU_THUONG), "bo_phan_trong_ngay": bo_phan,
                         "so_gio": 8, "nguon": "random"})
        for d in range(1, 21):
            rows.append({"msnv": nv["msnv"], "ngay": f"2026-07-{d:02d}",
                         "ky_hieu": rng.choice(KY_HIEU_THUONG), "bo_phan_trong_ngay": bo_phan,
                         "so_gio": 8, "nguon": "random"})
    return rows


def ghi_csv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def sinh(n_nv, seed, out_dir):
    rng = random.Random(seed)
    nv_rows = sinh_nhan_vien(n_nv, rng)
    cong_rows = sinh_cong_tho(nv_rows, rng)
    bo_phan_rows = [{"bo_phan": t, "tinh": tinh, "khoi": khoi, "vung_mien": vung,
                      "ngay_hieu_luc": "", "ghi_chu": "sinh ngẫu nhiên"} for t, tinh, khoi, vung in BO_PHAN]

    ghi_csv(os.path.join(out_dir, "nhan_vien.csv"), nv_rows, list(nv_rows[0].keys()))
    ghi_csv(os.path.join(out_dir, "bang_cong_tho.csv"), cong_rows, list(cong_rows[0].keys()))
    ghi_csv(os.path.join(out_dir, "dm_bo_phan.csv"), bo_phan_rows, list(bo_phan_rows[0].keys()))
    print(f"[gen_random_data] sinh {n_nv} NV · {len(cong_rows)} dòng công thô -> {out_dir}")


def apply_(out_dir):
    if os.path.exists(_BACKUP_DIR):
        print("[gen_random_data] đã có backup — chạy --restore trước khi apply lại.", file=sys.stderr)
        sys.exit(1)
    shutil.copytree(_REAL_DIR, _BACKUP_DIR, ignore=shutil.ignore_patterns("stress-test", "template"))
    for fn in ("nhan_vien.csv", "bang_cong_tho.csv", "dm_bo_phan.csv"):
        shutil.copy(os.path.join(out_dir, fn), os.path.join(_REAL_DIR, fn))
    print(f"[gen_random_data] ĐÃ THAY data-draft/ bằng dữ liệu random (backup ở {_BACKUP_DIR}). "
          f"Chạy --restore để khôi phục.")


def restore_():
    if not os.path.exists(_BACKUP_DIR):
        print("[gen_random_data] không có backup để khôi phục.", file=sys.stderr)
        sys.exit(1)
    for fn in ("nhan_vien.csv", "bang_cong_tho.csv", "dm_bo_phan.csv"):
        shutil.copy(os.path.join(_BACKUP_DIR, fn), os.path.join(_REAL_DIR, fn))
    shutil.rmtree(_BACKUP_DIR)
    print("[gen_random_data] đã khôi phục data-draft/ thật.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n-nv", type=int, default=80)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--apply", action="store_true", help="thay data-draft/ thật bằng bản random (có backup)")
    p.add_argument("--restore", action="store_true", help="khôi phục data-draft/ thật từ backup")
    args = p.parse_args()

    if args.restore:
        restore_()
    else:
        sinh(args.n_nv, args.seed, _OUT_DIR)
        if args.apply:
            apply_(_OUT_DIR)
