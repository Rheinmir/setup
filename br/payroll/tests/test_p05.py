"""Test đỏ frame p05 — quy định ngày nghỉ: phép năm, thâm niên, phép tồn (C7)."""
import unittest
from app.p05_nghiphep import so_du_phep


class TestQuyDinhNghi(unittest.TestCase):
    def test_tham_nien_5_nam_len_13_ngay(self):
        ton, nam_nay, da_dung, con_lai = so_du_phep("NV_vao_2021", "2026-07-01")
        self.assertGreaterEqual(nam_nay, 13)

    def test_thang_khong_dat_50pct_khong_cong_phep(self):
        # NV chỉ đạt 40% công chuẩn 1 tháng → tháng đó không sinh phép
        _, nam_nay_thap, _, _ = so_du_phep("NV_thang_thieu_cong", "2026-07-01")
        _, nam_nay_du, _, _ = so_du_phep("NV_du_cong", "2026-07-01")
        self.assertLess(nam_nay_thap, nam_nay_du)

    def test_phep_ton_het_han_sau_31_12_nam_ke(self):
        ton_2026, _, _, _ = so_du_phep("NV_co_phep_2025", "2026-12-31")
        ton_2027, _, _, _ = so_du_phep("NV_co_phep_2025", "2027-01-01")
        self.assertGreater(ton_2026, 0)
        self.assertEqual(ton_2027, 0)

    def test_tru_ton_truoc_nam_nay_sau(self):
        ton, nam_nay, da_dung, con_lai = so_du_phep("NV_da_dung_it", "2026-07-01")
        self.assertAlmostEqual(con_lai, ton + nam_nay - da_dung, places=2)


if __name__ == "__main__":
    unittest.main()
