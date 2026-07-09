"""Test đỏ frame p20 — truy thu/truy lĩnh khi định mức đổi hồi tố, kỳ chưa khóa (C4.3)."""
import unittest
from app.p20_truythu import tinh_truy_thu_linh


class TestTruyThuLinh(unittest.TestCase):
    def test_nv008_truy_linh_tang(self):
        r = tinh_truy_thu_linh("NV008", "khac", muc_cu=0, muc_moi=1_500_000,
                                ngay_hieu_luc="2026-06-21", ky="2026-07")
        self.assertGreater(r["chenh_lech"], 0)
        self.assertIn("ly_do", r)

    def test_giam_hoi_to_am(self):
        r = tinh_truy_thu_linh("NV_giam", "dien_thoai", muc_cu=800_000, muc_moi=600_000,
                                ngay_hieu_luc="2026-06-21", ky="2026-07")
        self.assertLess(r["chenh_lech"], 0)

    def test_ky_da_khoa_tu_choi(self):
        with self.assertRaises(Exception):
            tinh_truy_thu_linh("NV002", "khac", muc_cu=0, muc_moi=100_000,
                                ngay_hieu_luc="2026-05-01", ky="2026-06")


if __name__ == "__main__":
    unittest.main()
