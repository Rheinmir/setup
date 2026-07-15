"""f11 tổng hợp → lương thực nhận (BR C13) — đích cuối NET_PAY."""
import unittest
from decimal import Decimal
from app import tonghop, params


class TestTongHop(unittest.TestCase):
    def setUp(self):
        self.p = params.load("2026-03")
        # dòng 9: EARNED_SAL 200tr + FUEL 25tr + MEAL_NONTAX -990k + PHONE_NONTAX 1tr
        self.rec = {
            "EARNED_SAL": Decimal(200_000_000),
            "MEAL_TAX": Decimal(0), "PHONE_ALLOW": Decimal(0),
            "FUEL_ALLOW": Decimal(25_000_000), "TRANSPORT_TAX": Decimal(0),
            "LIVING_ALLOW": Decimal(0), "OTHER_ALLOW_TAX": Decimal(0),
            "MEAL_NONTAX": Decimal(-990_000), "PHONE_NONTAX": Decimal(1_000_000),
            "FUEL_NONTAX": Decimal(0), "TRANSPORT_NONTAX": Decimal(0),
            "LIVING_NONTAX": Decimal(0), "OTHER_ALLOW_NONTAX": Decimal(0),
            "OT_TAX": Decimal(0), "OT_NONTAX": Decimal(0),
            "BONUS_TOTAL": Decimal(0), "BONUS_TRAVEL": Decimal(0),
            "TOTAL_SUPPORT": Decimal(0), "SEVER_ALLOW": Decimal(0), "SI_BENEFIT": Decimal(0),
            "ADJ_PLUS": Decimal(0), "ADJ_MINUS": Decimal(0), "CHARITY_DED": Decimal(0),
            "EARNED_PAID_LEAVE": Decimal(0),
        }

    def test_gross_ground_truth_dong_9(self):
        self.assertEqual(tonghop.gross(self.rec, self.p), Decimal(225_010_000))

    def test_taxable_gross_ground_truth_dong_9(self):
        g = tonghop.gross(self.rec, self.p)
        self.assertEqual(tonghop.taxable_gross(self.rec, g, self.p), Decimal(225_000_000))

    def test_adj_minus_duoc_CONG_theo_lop_as_is(self):
        # BR C3.3 / C13.1 — cạm bẫy: as-is CỘNG ADJ_MINUS (HR nhập số âm để trừ)
        rec = dict(self.rec, ADJ_MINUS=Decimal(-1_000_000))
        self.assertEqual(tonghop.gross(rec, self.p), Decimal(224_010_000))

    def test_net_pay_ground_truth_dong_9(self):
        # BR C13.3: GROSS - TOTAL_INS - TOTAL_PIT - TOTAL_POST_DED + TOTAL_POST_ADD
        net = tonghop.net_pay(gross=Decimal(225_010_000), total_ins=Decimal(5_508_000),
                              total_pit=Decimal(50_387_200), total_post_ded=Decimal(234_000),
                              total_post_add=Decimal(21_049_361))
        self.assertEqual(net, Decimal(189_930_161))

    def test_net_income(self):
        ni = tonghop.net_income(gross=Decimal(225_010_000), total_ins=Decimal(5_508_000),
                                total_pit=Decimal(50_387_200))
        self.assertEqual(ni, Decimal(169_114_800))

    def test_total_cty_cost_dung_NET_PAY_khong_phai_GROSS(self):
        # BR C3.3 / C13.4 — cạm bẫy: to-be dùng GROSS → 236.602.000 (SAI)
        cost = tonghop.total_cty_cost(net_pay=Decimal(189_930_161),
                                      total_ins_cty=Decimal(10_656_000),
                                      kpcd_cty=Decimal(936_000))
        self.assertEqual(cost, Decimal(201_522_161))

    def test_budget_save_ground_truth_dong_9(self):
        bs = tonghop.budget_save(gross=Decimal(225_010_000), total_ins_cty=Decimal(10_656_000),
                                 kpcd_cty=Decimal(936_000),
                                 trich_quy=[Decimal(500_000), Decimal(50_000_000),
                                            Decimal(16_666_667), Decimal(1_250_000)])
        self.assertEqual(bs, Decimal(305_018_667))

    # ── C8.8 / FE-06 — PC_TRUY_THU phải cộng vào GROSS ──────────────────────
    def test_PC_TRUY_THU_co_trong_GROSS_CODES(self):
        self.assertIn("PC_TRUY_THU", tonghop._GROSS_CODES)

    def test_gross_cong_them_pc_truy_thu(self):
        self.rec["PC_TRUY_THU"] = Decimal(250_000)
        self.assertEqual(tonghop.gross(self.rec, self.p), Decimal(225_260_000))

    def test_gross_ground_truth_dong_9_khong_doi_khi_khong_co_truy_thu(self):
        # PC_TRUY_THU vắng mặt (không có ca truy thu) → GROSS ground-truth vẫn nguyên
        self.assertEqual(tonghop.gross(self.rec, self.p), Decimal(225_010_000))


if __name__ == "__main__":
    unittest.main()
