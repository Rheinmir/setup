"""Test đỏ frame p09 — tách giai đoạn bổ nhiệm giữa kỳ (C5.1.2)."""
import unittest
from app.p09_bonhiem import tach_bo_nhiem


class TestTachBoNhiem(unittest.TestCase):
    def test_nv003_hieu_luc_01_07(self):
        giai_doan = tach_bo_nhiem("NV003", "2026-07")
        self.assertEqual(len(giai_doan), 2)
        self.assertEqual(giai_doan[0]["den"], "2026-06-30")
        self.assertEqual(giai_doan[1]["tu"], "2026-07-01")

    def test_khong_bo_nhiem_mot_giai_doan(self):
        giai_doan = tach_bo_nhiem("NV002", "2026-07")
        self.assertEqual(len(giai_doan), 1)

    def test_pc_trach_nhiem_cong_thuc(self):
        giai_doan = tach_bo_nhiem("NV003", "2026-07")
        for gd in giai_doan:
            self.assertAlmostEqual(
                gd["pc_trach_nhiem"], gd["ngay_huong"] * gd["muc"] / 26, delta=1
            )


if __name__ == "__main__":
    unittest.main()
