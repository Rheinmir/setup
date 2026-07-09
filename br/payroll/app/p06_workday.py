"""p06_workday — Adapter Workday mock (C4.2).

Ranh giới BNAL verified:false: đọc bảng công thô ngày×NV + hồ sơ NV
(EmployeeType, ngày kết thúc thử việc) từ CSV thay cho API Workday thật.
"""

import csv
import os
from datetime import date

VERIFIED = False

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "br", "data-draft")
_CONG_THO_CSV = os.path.join(_DATA_DIR, "bang_cong_tho.csv")
_NHAN_VIEN_CSV = os.path.join(_DATA_DIR, "nhan_vien.csv")


def cong_tho(thang):
    y, m = (int(x) for x in thang.split("-"))
    if m == 1:
        prev_y, prev_m = y - 1, 12
    else:
        prev_y, prev_m = y, m - 1
    tu_ngay = date(prev_y, prev_m, 21).isoformat()
    den_ngay = date(y, m, 20).isoformat()

    rows = []
    with open(_CONG_THO_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if tu_ngay <= r["ngay"] <= den_ngay:
                rows.append(r)
    return rows


def ho_so(msnv):
    with open(_NHAN_VIEN_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["msnv"] == msnv:
                return r
    raise KeyError(f"Không tìm thấy hồ sơ nhân viên: {msnv}")
