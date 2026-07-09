"""Test đỏ frame p21 — OT engine: multiplier CN/lễ/truyền thống, tách CT/Mắt Bão (C5.5)."""
import unittest
from app.p21_ot import tinh_ot


class TestOTEngine(unittest.TestCase):
    def test_tc200_2_ngay(self):
        r = tinh_ot("NV008", luong_ngay=400_000, so_ngay_tc200=2, employee_type="Official")
        self.assertAlmostEqual(r["tien_ot"], 2 * 400_000 * 2.0, delta=10_000)

    def test_le_luat_them_100pct_va_2_nghi_bu(self):
        r = tinh_ot("NV003", luong_ngay=500_000, so_ngay_le_luat=1, employee_type="Official")
        self.assertGreaterEqual(r["ngay_nghi_bu_sinh_them"], 2)

    def test_danh_sach_300_rong_canh_bao(self):
        r = tinh_ot("NV_test300", luong_ngay=500_000, so_ngay_le_300=1, employee_type="Official")
        self.assertIn("assumed", str(r.get("trace", "")).lower())

    def test_mat_bao_cot_rieng(self):
        r_cty = tinh_ot("NV003", luong_ngay=500_000, so_ngay_tc200=1, employee_type="Official")
        r_mb = tinh_ot("NV005", luong_ngay=500_000, so_ngay_tc200=1, employee_type="MatBao")
        self.assertIsInstance(r_cty["tien_ot"], (int, float))
        self.assertIsInstance(r_mb["tien_ot"], (int, float))


if __name__ == "__main__":
    unittest.main()
