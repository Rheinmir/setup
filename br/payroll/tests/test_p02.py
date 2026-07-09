"""Test đỏ frame p02 — master data store: DM Bộ phận / Nơi cư trú / Khoảng cách (C7)."""
import unittest
from app.p02_masterdata import bo_phan_info, dai_khoang_cach


class TestMasterData(unittest.TestCase):
    def test_bo_phan_doi_hieu_luc(self):
        tinh_sau, khoi, vung = bo_phan_info("Kho miền Nam", "2025-07-01")
        self.assertEqual(tinh_sau, "Bình Dương")
        tinh_truoc, _, _ = bo_phan_info("Kho miền Nam", "2025-01-01")
        self.assertEqual(tinh_truoc, "TP.HCM")

    def test_dai_khoang_cach_khac_mien(self):
        self.assertEqual(dai_khoang_cach("TP.HCM", "Quảng Ninh"), "khac_mien")

    def test_bo_phan_khong_ton_tai_raise(self):
        with self.assertRaises(Exception):
            bo_phan_info("Bộ phận không có thật", "2026-07-01")


if __name__ == "__main__":
    unittest.main()
