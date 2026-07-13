"""f02 lịch & kỳ công — kỳ 21→20, công chuẩn VP/CT (BR C5)."""
import unittest
from datetime import date
from decimal import Decimal
from app import lichky


class TestLichKy(unittest.TestCase):
    def test_ky_cong_21_den_20(self):
        # BR C5.1: kỳ 03/2026 = 21/02/2026 → 20/03/2026
        d1, d2 = lichky.ky_cong("2026-03")
        self.assertEqual(d1, date(2026, 2, 21))
        self.assertEqual(d2, date(2026, 3, 20))

    def test_ky_cong_bat_qua_nam(self):
        d1, d2 = lichky.ky_cong("2026-01")
        self.assertEqual(d1, date(2025, 12, 21))
        self.assertEqual(d2, date(2026, 1, 20))

    def test_cong_chuan_cong_truong_chi_tru_chu_nhat(self):
        # 21/02/2026 → 20/03/2026 = 28 ngày, trong đó 4 Chủ nhật (22/02, 1/3, 8/3, 15/3)
        self.assertEqual(lichky.cong_chuan("2026-03", "CT"), Decimal("24"))

    def test_cong_chuan_van_phong_tru_chu_nhat_va_nua_thu_bay(self):
        # BR C5.2: VP trừ CN và CHIỀU thứ 7 → thứ 7 tính 1/2 ngày.
        # Cùng kỳ: 24 ngày (đã trừ CN), trong đó 4 thứ 7 → 24 - 4*0.5 = 22
        self.assertEqual(lichky.cong_chuan("2026-03", "VP"), Decimal("22"))

    def test_cong_chuan_vp_nho_hon_ct(self):
        for period in ("2026-01", "2026-05", "2026-11"):
            self.assertLess(lichky.cong_chuan(period, "VP"), lichky.cong_chuan(period, "CT"))

    def test_ngay_le_co_dinh_duong_lich(self):
        le = lichky.ngay_le(2026)
        for d in (date(2026, 1, 1), date(2026, 4, 30), date(2026, 5, 1), date(2026, 9, 2)):
            self.assertIn(d, le)


if __name__ == "__main__":
    unittest.main()
