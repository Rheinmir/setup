"""f05 suất ăn (BR C8.1, C8.2) — gồm AC-1 chốt tại họp 23/03/2026."""
import unittest
from decimal import Decimal
from app import com, params


class TestCom(unittest.TestCase):
    def setUp(self):
        self.p = params.load("2026-03")

    def test_so_bua_theo_noi_lam_viec(self):
        self.assertEqual(com.so_bua({"noi": "VP", "gio": 8}, self.p), 1)
        self.assertEqual(com.so_bua({"noi": "CT_GAN", "gio": 8}, self.p), 2)   # < 30km
        self.assertEqual(com.so_bua({"noi": "CT_XA", "gio": 8}, self.p), 3)    # >= 30km

    def test_lam_duoi_4_tieng_khong_tinh_suat_an(self):
        # BR C8.1 — ngày <= 4 tiếng: 0 bữa, mọi đối tượng
        self.assertEqual(com.so_bua({"noi": "CT_XA", "gio": 4}, self.p), 0)
        self.assertEqual(com.so_bua({"noi": "VP", "gio": 3}, self.p), 0)
        self.assertEqual(com.so_bua({"noi": "VP", "gio": 4.5}, self.p), 1)

    def test_AC1_tong_suat_an_khi_dieu_dong(self):
        # BR C17.4 / AC-1: VP A 5 ngày (1 bữa) + dự án B >=30km 20 ngày (3 bữa) = 65 suất
        ngay = [{"noi": "VP", "gio": 8}] * 5 + [{"noi": "CT_XA", "gio": 8}] * 20
        self.assertEqual(com.tong_suat_an(ngay, self.p), 65)

    def test_AC1_co_ngay_duoi_4_tieng_thi_ngay_do_khong_tinh(self):
        ngay = [{"noi": "VP", "gio": 8}] * 5 + [{"noi": "CT_XA", "gio": 8}] * 19 + [{"noi": "CT_XA", "gio": 2}]
        self.assertEqual(com.tong_suat_an(ngay, self.p), 62)

    def test_tach_thue_com_theo_nguong_730k(self):
        # BR C4.3 / C8.2: MEAL_ALLOW = 78 x 45.000 = 3.510.000
        allow = com.meal_allow(78, self.p)
        self.assertEqual(allow, Decimal(3_510_000))
        self.assertEqual(com.meal_nontax(allow, self.p), Decimal(730_000))
        self.assertEqual(com.meal_tax(allow, self.p), Decimal(2_780_000))

    def test_com_it_hon_nguong_thi_khong_chiu_thue(self):
        allow = com.meal_allow(10, self.p)   # 450.000
        self.assertEqual(com.meal_nontax(allow, self.p), Decimal(450_000))
        self.assertEqual(com.meal_tax(allow, self.p), Decimal(0))


if __name__ == "__main__":
    unittest.main()
