"""f04 lương chính & pro-rata (BR C7)."""
import unittest
from decimal import Decimal
from app import luong, params


class TestLuong(unittest.TestCase):
    def setUp(self):
        self.p = params.load("2026-03")

    def test_official_earned_ground_truth_dong_9(self):
        # BR C7.1: ROUND(BASIC_SAL / STD_DAYS * PAID_DAYS, 0) = 200tr/22*22
        rec = {"CONTRACT_TYPE": "Chính thức", "BASIC_SAL": Decimal(200_000_000),
               "STD_DAYS": Decimal(22), "PAID_DAYS": Decimal(22)}
        self.assertEqual(luong.official_earned(rec, self.p), Decimal(200_000_000))

    def test_official_earned_bang_0_khi_thu_viec(self):
        rec = {"CONTRACT_TYPE": "Thử việc", "BASIC_SAL": Decimal(20_000_000),
               "STD_DAYS": Decimal(22), "PAID_DAYS": Decimal(22)}
        self.assertEqual(luong.official_earned(rec, self.p), Decimal(0))

    def test_prob_earned_chi_khi_thu_viec(self):
        rec = {"CONTRACT_TYPE": "Thử việc", "PROB_SAL": Decimal(17_000_000),
               "STD_DAYS": Decimal(22), "PAID_DAYS": Decimal(11)}
        self.assertEqual(luong.prob_earned(rec, self.p), Decimal(8_500_000))

    def test_prorata_nua_ky(self):
        rec = {"CONTRACT_TYPE": "Chính thức", "BASIC_SAL": Decimal(22_000_000),
               "STD_DAYS": Decimal(22), "PAID_DAYS": Decimal(11)}
        self.assertEqual(luong.official_earned(rec, self.p), Decimal(11_000_000))

    def test_lam_tron_half_up_khong_phai_half_even(self):
        # BR C13.5: Excel ROUND là half-up. 3 chia 2 = 1.5 → 2 (không phải 2 do banker's)
        rec = {"CONTRACT_TYPE": "Chính thức", "BASIC_SAL": Decimal(3),
               "STD_DAYS": Decimal(2), "PAID_DAYS": Decimal(1)}
        self.assertEqual(luong.official_earned(rec, self.p), Decimal(2))

    def test_earned_sal_gom_4_thanh_phan(self):
        # BR C3.3 as-is: PROB + OFFICIAL + RESP + EARNED_PAID_LEAVE
        rec = {"CONTRACT_TYPE": "Chính thức", "BASIC_SAL": Decimal(22_000_000),
               "PROB_SAL": 0, "RESP_SAL": Decimal(2_200_000),
               "STD_DAYS": Decimal(22), "PAID_DAYS": Decimal(22),
               "EARNED_PAID_LEAVE": Decimal(1_000_000)}
        self.assertEqual(luong.earned_sal(rec, self.p), Decimal(25_200_000))

    def test_resp_earned_prorata(self):
        rec = {"CONTRACT_TYPE": "Chính thức", "RESP_SAL": Decimal(2_200_000),
               "STD_DAYS": Decimal(22), "PAID_DAYS": Decimal(11)}
        self.assertEqual(luong.resp_earned(rec, self.p), Decimal(1_100_000))


if __name__ == "__main__":
    unittest.main()
