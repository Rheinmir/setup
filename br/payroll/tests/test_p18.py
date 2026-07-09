"""Test đỏ frame p18 — PC công trường + công tác xa (C5.3.5)."""
import unittest
from app.p18_pcctctx import tinh_pc_ct_ctx


class TestPCCTCTX(unittest.TestCase):
    def test_ct_khac_mien_dh(self):
        r = tinh_pc_ct_ctx("NV_ct_khacmien_dh")
        self.assertAlmostEqual(r["tong"], 3_000_000, delta=100_000)

    def test_vp_30_100_cd(self):
        r = tinh_pc_ct_ctx("NV_vp_30100_cd")
        self.assertAlmostEqual(r["tong"], 700_000, delta=50_000)

    def test_ct_duoi_30_khac_di_lai(self):
        r = tinh_pc_ct_ctx("NV_ct_duoi30_dh")
        self.assertGreater(r["tong"], 0)  # khác đi lại (=0) là ĐÚNG thiết kế

    def test_gddar_bang_0(self):
        r = tinh_pc_ct_ctx("NV007")
        self.assertEqual(r["tong"], 0)


if __name__ == "__main__":
    unittest.main()
