"""Test đỏ frame p19 — PC công trường xa/khó khăn theo dự án + PC khác (7) (C5.3.6, C5.3.7).
Tổng quát: định mức tra dinh_muc_ct_xa_du_an.csv thật, đoạn từ p10, pc7 từ p04 thật."""
import unittest
from app.p19_pcctxa import tinh_pc_ct_xa_va_khac


class TestPCCTXaDuAnDacThu(unittest.TestCase):
    def test_nv008_quan_lan_thu_kho(self):
        r = tinh_pc_ct_xa_va_khac("NV008")
        self.assertGreater(r["pc6"], 0)
        self.assertEqual(r["pc7"], 1_500_000)

    def test_nv012_lang_tay(self):
        r = tinh_pc_ct_xa_va_khac("NV012")
        self.assertGreater(r["pc6"], 0)
        self.assertIn("TT-2026/044", str(r["trace"]))

    def test_ct_thuong_bang_0(self):
        r = tinh_pc_ct_xa_va_khac("NV004")
        self.assertEqual(r["pc6"], 0)
        self.assertEqual(r["pc7"], 0)

    def test_bang_du_an_co_chingluh_assumed(self):
        # Kiểm bảng CSV nguồn có ghi rõ "ASSUMED" cho Chingluh (PRD chỉ cho 2 đầu mút,
        # nội suy các chức danh giữa) — kiểm ở nguồn dữ liệu, không cần NV cụ thể.
        from app.p19_pcctxa import _bang_du_an
        rows = [r for r in _bang_du_an() if r["du_an"] == "Chingluh"]
        self.assertTrue(any("ASSUMED" in r["nguon"] for r in rows))


if __name__ == "__main__":
    unittest.main()
