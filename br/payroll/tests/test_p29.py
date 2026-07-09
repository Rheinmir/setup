"""Test đỏ frame p29 — validate + import CSV nhân viên upload từ UI (C7.1, gap mới)."""
import csv
import os
import tempfile
import unittest

from app.p29_import import validate_and_import

HEADER = ("msnv,ho_ten,ngach,trinh_do,chuc_danh,employee_type,bo_phan_hien_tai,"
          "noi_tuyen_dung,noi_cu_tru,ngay_vao,ngay_ket_thuc_thu_viec,"
          "luong_co_ban_thang(ASSUMED),ghi_chu")
DONG_HOP_LE = ("NV900,Test Một,NV.01,Đại học,Kế toán,Official,VP HCM,TP.HCM,TP.HCM,"
               "2024-01-01,2024-03-01,15000000,test")
DONG_HOP_LE_2 = ("NV901,Test Hai,NV.02,Cao đẳng,Thủ kho,Official,CT Long An,TP.HCM,"
                  "TP.HCM,2023-05-01,2023-07-01,12000000,test")


class TestImportNhanVien(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8")
        self.tmp.write(HEADER + "\nNV999,Cũ,NV.01,Đại học,Cũ,Official,VP HCM,TP.HCM,"
                        "TP.HCM,2020-01-01,2020-03-01,10000000,dữ liệu cũ\n")
        self.tmp.close()

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_csv_hop_le_2_dong_ghi_de_thanh_cong(self):
        noi_dung = f"{HEADER}\n{DONG_HOP_LE}\n{DONG_HOP_LE_2}\n"
        hop_le, so_dong, loi = validate_and_import(noi_dung, self.tmp.name)
        self.assertTrue(hop_le)
        self.assertEqual(so_dong, 2)
        self.assertIsNone(loi)
        with open(self.tmp.name, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["msnv"], "NV900")

    def test_thieu_cot_bat_buoc_tu_choi_khong_ghi_de(self):
        header_thieu_msnv = HEADER.replace("msnv,", "")
        noi_dung = f"{header_thieu_msnv}\n"
        hop_le, so_dong, loi = validate_and_import(noi_dung, self.tmp.name)
        self.assertFalse(hop_le)
        self.assertIn("msnv", loi)
        with open(self.tmp.name, encoding="utf-8") as f:
            noi_dung_sau = f.read()
        self.assertIn("NV999", noi_dung_sau)  # file đích GIỮ NGUYÊN, không bị ghi đè

    def test_csv_rong_khong_co_dong_du_lieu(self):
        noi_dung = f"{HEADER}\n"
        hop_le, so_dong, loi = validate_and_import(noi_dung, self.tmp.name)
        self.assertFalse(hop_le)
        self.assertIn("rỗng", loi.lower())

    def test_thua_cot_la_tu_choi(self):
        noi_dung = f"{HEADER},cot_thua_la\n{DONG_HOP_LE},thừa\n"
        hop_le, so_dong, loi = validate_and_import(noi_dung, self.tmp.name)
        self.assertFalse(hop_le)
        self.assertIn("cot_thua_la", loi)


if __name__ == "__main__":
    unittest.main()
