"""Test đỏ frame p05 — quy định ngày nghỉ: phép năm, thâm niên, phép tồn (C7).
Tổng quát: nam_vao lấy THẬT từ hồ sơ p06, không tra ID giả."""
import unittest
from app.p05_nghiphep import so_du_phep


class TestQuyDinhNghi(unittest.TestCase):
    def test_tham_nien_5_nam_len_13_ngay(self):
        # NV001 vào 2021-03-01 → 2026 = đúng 5 năm thâm niên → +1 ngày = 13.
        ton, nam_nay, da_dung, con_lai = so_du_phep("NV001", "2026-07-01")
        self.assertGreaterEqual(nam_nay, 13)

    def test_thang_khong_dat_50pct_khong_cong_phep(self):
        # NV003 (sổ HR: thang_dat=11) < NV002 (mặc định thang_dat=12)
        _, nam_nay_thap, _, _ = so_du_phep("NV003", "2026-07-01")
        _, nam_nay_du, _, _ = so_du_phep("NV002", "2026-07-01")
        self.assertLess(nam_nay_thap, nam_nay_du)

    def test_phep_ton_het_han_sau_31_12_nam_ke(self):
        # NV004 (sổ HR: phep_ton_nam_truoc={2025:5})
        ton_2026, _, _, _ = so_du_phep("NV004", "2026-12-31")
        ton_2027, _, _, _ = so_du_phep("NV004", "2027-01-01")
        self.assertGreater(ton_2026, 0)
        self.assertEqual(ton_2027, 0)

    def test_tru_ton_truoc_nam_nay_sau(self):
        # NV006 (sổ HR: da_dung=3)
        ton, nam_nay, da_dung, con_lai = so_du_phep("NV006", "2026-07-01")
        self.assertAlmostEqual(con_lai, ton + nam_nay - da_dung, places=2)

    def test_nv008_mac_dinh_khong_co_trong_so_hr(self):
        # NV008 chưa từng xuất hiện trong sổ HR/test cũ — dùng mặc định hợp lý.
        ton, nam_nay, da_dung, con_lai = so_du_phep("NV008", "2026-07-01")
        self.assertEqual(da_dung, 0)
        self.assertEqual(ton, 0)
        self.assertGreaterEqual(nam_nay, 12)


if __name__ == "__main__":
    unittest.main()
