"""Test đỏ frame p17 — PC đi lại: nhóm đối tượng × dải khoảng cách (C5.3.4)."""
import unittest
from app.p17_pcdilai import tinh_pc_di_lai


class TestPCDiLai(unittest.TestCase):
    def test_nv001_quan_lan_khac_mien(self):
        r = tinh_pc_di_lai("NV001")
        self.assertIn("CT Quan Lạn", r["theo_bo_phan"])
        self.assertGreater(r["theo_bo_phan"]["CT Quan Lạn"], 0)

    def test_nv001_vp_hcm_duoi_30_bang_0(self):
        r = tinh_pc_di_lai("NV001")
        self.assertEqual(r["theo_bo_phan"].get("VP HCM", 0), 0)

    def test_nv009_nv02_duoi_14_ngay(self):
        r = tinh_pc_di_lai("NV009")
        self.assertGreater(r["tong"], 0)
        self.assertLess(r["tong"], 250_000)  # co lại theo quy tắc <14 ngày

    def test_gddar_bang_0(self):
        r = tinh_pc_di_lai("NV007")
        self.assertEqual(r["tong"], 0)
        self.assertIn("GĐDA", str(r["trace"]))


if __name__ == "__main__":
    unittest.main()
