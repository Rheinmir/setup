"""f08 thưởng & trích quỹ (BR C10) — trích quỹ có ground-truth dòng 9."""
import unittest
from decimal import Decimal
from app import thuong, params


class TestThuong(unittest.TestCase):
    def setUp(self):
        self.p = params.load("2026-03")
        self.rec = {"CONTRACT_TOTAL": Decimal(200_000_000), "PAID_DAYS": Decimal(22),
                    "TERMINATION_DATE": None}

    def test_trich_quy_ground_truth_dong_9(self):
        # BR C10.2 — 4 con số này phải khớp dòng 9 Excel
        self.assertEqual(thuong.bonus_save_travel(self.rec, self.p), Decimal(500_000))
        self.assertEqual(thuong.bonus_save_kpi(self.rec, self.p), Decimal(50_000_000))
        self.assertEqual(thuong.bonus_save_13m(self.rec, self.p), Decimal(16_666_667))
        self.assertEqual(thuong.bonus_save_tet(self.rec, self.p), Decimal(1_250_000))

    def test_bonus_save_tet_bi_cap_15tr_chia_12(self):
        # MIN(CONTRACT/12, 15tr/12) — lương 200tr/12 = 16.666.667 > 1.250.000 → cap
        self.assertEqual(thuong.bonus_save_tet(self.rec, self.p), Decimal(1_250_000))

    def test_luong_thap_thi_bonus_save_tet_khong_bi_cap(self):
        rec = dict(self.rec, CONTRACT_TOTAL=Decimal(12_000_000))
        self.assertEqual(thuong.bonus_save_tet(rec, self.p), Decimal(1_000_000))

    def test_co_ngay_nghi_viec_thi_khong_trich_quy(self):
        # BR C10.2: điều kiện "không có ngày nghỉ việc"
        rec = dict(self.rec, TERMINATION_DATE="2026-03-15")
        self.assertEqual(thuong.bonus_save_kpi(rec, self.p), Decimal(0))
        self.assertEqual(thuong.bonus_save_travel(rec, self.p), Decimal(0))

    def test_khong_co_ngay_huong_luong_thi_khong_trich(self):
        rec = dict(self.rec, PAID_DAYS=Decimal(0))
        self.assertEqual(thuong.bonus_save_13m(rec, self.p), Decimal(0))

    def test_bonus_total_la_tong_cac_khoan_input(self):
        rec = {"BONUS_TET": Decimal(15_000_000), "BONUS_13M": Decimal(20_000_000),
               "BONUS_KPI": Decimal(5_000_000)}
        self.assertEqual(thuong.bonus_total(rec), Decimal(40_000_000))

    def test_nghi_luy_ke_tu_10_ngay_thi_loai_khoi_dien_thuong(self):
        # BR C10.1: thai sản/ốm dài/không lương lũy kế >= 10 ngày → không tính thời gian xét thưởng
        self.assertFalse(thuong.du_dieu_kien_thuong({"ngay_nghi_luy_ke": 10,
                                                     "TERMINATION_DATE": None}))
        self.assertTrue(thuong.du_dieu_kien_thuong({"ngay_nghi_luy_ke": 9,
                                                    "TERMINATION_DATE": None}))


if __name__ == "__main__":
    unittest.main()
