"""Test đỏ frame p16 — PC xăng: CT chuẩn 1tr, VP chỉ qua tờ trình (C5.3.3)."""
import unittest
from app.p16_pcxang import tinh_pc_xang


class TestPCXang(unittest.TestCase):
    def test_ct_muc_chuan(self):
        r = tinh_pc_xang("NV_ct_l3_khong_tt")
        self.assertAlmostEqual(r["tong"], 1_000_000, delta=50_000)
        self.assertIn("QĐ chung", str(r["trace"]))

    def test_vp_khong_tt_bang_0(self):
        r = tinh_pc_xang("NV002")
        self.assertEqual(r["tong"], 0)

    def test_tai_xe_hn_tu_to_trinh(self):
        r = tinh_pc_xang("NV006")
        self.assertIn("TT-2026/031", str(r["trace"]))

    def test_gddar_tu_to_trinh(self):
        r = tinh_pc_xang("NV007")
        self.assertAlmostEqual(r["tong"], 10_000_000, delta=100_000)
        self.assertIn("TT-2026/018", str(r["trace"]))


if __name__ == "__main__":
    unittest.main()
