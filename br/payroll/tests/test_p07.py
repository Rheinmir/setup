"""Test đỏ frame p07 — parser ký hiệu công thành thuộc tính (C4.2)."""
import unittest
from app.p07_kyhieu import phan_loai


class TestParserKyHieu(unittest.TestCase):
    def test_x_lam_viec_huong_luong_tinh_bhxh(self):
        p = phan_loai("x")
        self.assertTrue(p["lam_viec_thuc_te"])
        self.assertTrue(p["huong_luong"])
        self.assertTrue(p["tinh_bhxh"])

    def test_ro_khong_lam_khong_luong_khong_bhxh(self):
        p = phan_loai("Ro")
        self.assertFalse(p["lam_viec_thuc_te"])
        self.assertFalse(p["huong_luong"])
        self.assertFalse(p["tinh_bhxh"])

    def test_ts_khong_lam_khong_tinh_bhxh(self):
        p = phan_loai("Ts")
        self.assertFalse(p["lam_viec_thuc_te"])
        self.assertFalse(p["tinh_bhxh"])

    def test_cho_duyet_khong_cong_huong_luong(self):
        p = phan_loai("?P")
        self.assertTrue(p["cho_duyet"])
        self.assertFalse(p["huong_luong"])

    def test_tc200_he_so(self):
        p = phan_loai("TC200")
        self.assertEqual(p["he_so_tc"], 200)

    def test_ky_hieu_la_raise(self):
        with self.assertRaises(Exception):
            phan_loai("ZZ_KHONG_TON_TAI")


if __name__ == "__main__":
    unittest.main()
