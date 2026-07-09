"""Test đỏ frame p19 — PC công trường xa/khó khăn theo dự án + PC khác (7) (C5.3.6, C5.3.7)."""
import unittest
from app.p19_pcctxa import tinh_pc_ct_xa_va_khac


class TestPCCTXaDuAnDacThu(unittest.TestCase):
    def test_nv008_quan_lan_thu_kho(self):
        r = tinh_pc_ct_xa_va_khac("NV008")
        self.assertAlmostEqual(r["pc6"], 2_000_000, delta=100_000)
        self.assertAlmostEqual(r["pc7"], 1_500_000, delta=100_000)

    def test_nv012_lang_tay(self):
        r = tinh_pc_ct_xa_va_khac("NV012")
        self.assertAlmostEqual(r["pc6"], 2_000_000, delta=100_000)
        self.assertIn("TT-2026/044", str(r["trace"]))

    def test_ct_thuong_bang_0(self):
        r = tinh_pc_ct_xa_va_khac("NV004")
        self.assertEqual(r["pc6"], 0)
        self.assertEqual(r["pc7"], 0)

    def test_chingluh_assumed_flag(self):
        r = tinh_pc_ct_xa_va_khac("NV_chingluh_gs")
        self.assertIn("assumed", str(r["trace"]).lower())


if __name__ == "__main__":
    unittest.main()
