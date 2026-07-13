"""f03 chấm công — ký hiệu + PAID_DAYS theo lớp as-is (BR C6)."""
import unittest
from decimal import Decimal
from app import chamcong


class TestChamCong(unittest.TestCase):
    def test_ky_hieu_toi_thieu(self):
        for k in ("x", "x1", "OL", "P", "L", "NB", "Ts", "ON", "Ro", "?P"):
            self.assertIn(k, chamcong.KY_HIEU)

    def test_don_cho_duyet_khong_cong_vao_cong_huong_luong(self):
        # BR C6.2: ?P KHÔNG được cộng
        self.assertFalse(chamcong.tinh_cong_huong_luong("?P"))
        self.assertTrue(chamcong.tinh_cong_huong_luong("x"))

    def test_paid_days_ground_truth_dong_9(self):
        # BR C6.3 as-is: chính thức → OFFICIAL + PHÉP + LỄ + BÙ + KHÁC + HIẾU HỈ
        # dòng 9: 19.5 + 0 + 2.5 = 22
        rec = {"CONTRACT_TYPE": "Chính thức", "OFFICIAL_DAYS": Decimal("19.5"),
               "PROB_DAYS": 0, "PAID_LEAVE_DAYS": 0, "HOLIDAY_DAYS": Decimal("2.5"),
               "COMP_DAYS": 0, "PAID_OTHER_DAYS": 0, "BEREAVE_DAYS": 0,
               "SI_DAYS": 5, "ADJ_DAYS": 3}
        self.assertEqual(chamcong.paid_days(rec), Decimal("22"))

    def test_paid_days_khong_cong_si_days_va_adj_days(self):
        # Đây là điểm LỆCH giữa to-be và as-is — engine bám as-is (BR C3.3).
        # SI_DAYS=5, ADJ_DAYS=3 ở trên KHÔNG được cộng → vẫn 22, không phải 30.
        rec = {"CONTRACT_TYPE": "Chính thức", "OFFICIAL_DAYS": 10, "PROB_DAYS": 0,
               "PAID_LEAVE_DAYS": 0, "HOLIDAY_DAYS": 0, "COMP_DAYS": 0,
               "PAID_OTHER_DAYS": 0, "BEREAVE_DAYS": 0, "SI_DAYS": 5, "ADJ_DAYS": 3}
        self.assertEqual(chamcong.paid_days(rec), Decimal("10"))

    def test_paid_days_thu_viec_dung_prob_days(self):
        rec = {"CONTRACT_TYPE": "Thử việc", "OFFICIAL_DAYS": 0, "PROB_DAYS": 15,
               "PAID_LEAVE_DAYS": 1, "HOLIDAY_DAYS": 2, "COMP_DAYS": 0,
               "PAID_OTHER_DAYS": 0, "BEREAVE_DAYS": 0, "SI_DAYS": 0, "ADJ_DAYS": 0}
        self.assertEqual(chamcong.paid_days(rec), Decimal("18"))


if __name__ == "__main__":
    unittest.main()
