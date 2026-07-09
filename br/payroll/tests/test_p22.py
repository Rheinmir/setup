"""Test đỏ frame p22 — khóa kỳ manual lock, tier compensable (C4.3)."""
import unittest
from app.p22_khoaky import khoa_ky, is_locked


class TestKhoaKy(unittest.TestCase):
    def test_khoa_ky_ghi_du_thong_tin(self):
        khoa_ky("2026-07", nguoi="hr.cb01", ly_do="đã kiểm soát xong")
        self.assertTrue(is_locked("2026-07"))

    def test_khoa_lai_idempotent(self):
        khoa_ky("2026-07", nguoi="hr.cb01", ly_do="lần 1")
        khoa_ky("2026-07", nguoi="hr.cb02", ly_do="lần 2 lặp")
        self.assertTrue(is_locked("2026-07"))

    def test_thieu_ly_do_tu_choi(self):
        with self.assertRaises(Exception):
            khoa_ky("2026-08", nguoi="hr.cb01", ly_do="")

    def test_ky_chua_khoa(self):
        self.assertFalse(is_locked("2099-01"))


if __name__ == "__main__":
    unittest.main()
