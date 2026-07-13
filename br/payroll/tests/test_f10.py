"""f10 thuế TNCN (BR C12) — biểu 5 bậc + case thử việc/nước ngoài."""
import unittest
from decimal import Decimal
from app import thue, params


class TestThue(unittest.TestCase):
    def setUp(self):
        self.p = params.load("2026-03")
        self.chinh_thuc = {"CONTRACT_TYPE": "Chính thức", "NATIONALITY": "Việt Nam"}

    def test_pit_ground_truth_dong_9(self):
        # BR C17.1: 185.392.000 x 35% - 14.500.000 = 50.387.200
        self.assertEqual(thue.pit(Decimal(185_392_000), self.chinh_thuc, self.p),
                         Decimal(50_387_200))

    def test_bac_1_5_phan_tram(self):
        self.assertEqual(thue.pit(Decimal(8_000_000), self.chinh_thuc, self.p),
                         Decimal(400_000))

    def test_bac_2_10_phan_tram_tru_500k(self):
        self.assertEqual(thue.pit(Decimal(20_000_000), self.chinh_thuc, self.p),
                         Decimal(1_500_000))

    def test_bac_3_20_phan_tram_tru_3tr5(self):
        self.assertEqual(thue.pit(Decimal(50_000_000), self.chinh_thuc, self.p),
                         Decimal(6_500_000))

    def test_bac_4_30_phan_tram_tru_9tr5(self):
        self.assertEqual(thue.pit(Decimal(80_000_000), self.chinh_thuc, self.p),
                         Decimal(14_500_000))

    def test_bien_bac_dung_dau_khong_lech(self):
        # đúng 10tr = bậc 1 (5%) ; 10tr + 1đ = bậc 2
        self.assertEqual(thue.pit(Decimal(10_000_000), self.chinh_thuc, self.p),
                         Decimal(500_000))
        self.assertEqual(thue.pit(Decimal(10_000_001), self.chinh_thuc, self.p),
                         Decimal(500_000))  # 10.000.001 x 10% - 500.000 = 500.000.1 → làm tròn

    def test_thu_nhap_am_hoac_0_thi_thue_0(self):
        self.assertEqual(thue.pit(Decimal(0), self.chinh_thuc, self.p), Decimal(0))
        self.assertEqual(thue.pit(Decimal(-5_000_000), self.chinh_thuc, self.p), Decimal(0))

    def test_thu_viec_viet_nam_tu_2tr_tro_len_chiu_10_phan_tram(self):
        # BR C12.2
        rec = {"CONTRACT_TYPE": "Thử việc", "NATIONALITY": "Việt Nam"}
        self.assertEqual(thue.pit(Decimal(5_000_000), rec, self.p), Decimal(500_000))

    def test_thu_viec_viet_nam_duoi_2tr_khong_chiu_thue(self):
        rec = {"CONTRACT_TYPE": "Thử việc", "NATIONALITY": "Việt Nam"}
        self.assertEqual(thue.pit(Decimal(1_999_999), rec, self.p), Decimal(0))

    def test_thu_viec_nguoi_nuoc_ngoai_chiu_20_phan_tram(self):
        rec = {"CONTRACT_TYPE": "Thử việc", "NATIONALITY": "Nước ngoài"}
        self.assertEqual(thue.pit(Decimal(10_000_000), rec, self.p), Decimal(2_000_000))

    def test_giam_tru_ground_truth_dong_9(self):
        # BR C4.4: 15.500.000 + 3 x 6.200.000 = 34.100.000
        rec = dict(self.chinh_thuc, DEPENDENT_CNT=3)
        self.assertEqual(thue.total_ded(rec, self.p), Decimal(34_100_000))

    def test_thu_viec_khong_duoc_giam_tru_ban_than(self):
        rec = {"CONTRACT_TYPE": "Thử việc", "NATIONALITY": "Việt Nam", "DEPENDENT_CNT": 0}
        self.assertEqual(thue.total_ded(rec, self.p), Decimal(0))

    def test_taxable_inc_khong_bao_gio_am(self):
        # BR C12.1: MAX(0, ...)
        self.assertEqual(
            thue.taxable_inc(Decimal(10_000_000), Decimal(1_000_000), Decimal(34_100_000)),
            Decimal(0))

    def test_effective_from_doi_giam_tru_thi_doi_thue(self):
        # BR C17.3 (GT-2): cùng engine, param-set kỳ CŨ → TOTAL_DED = 11tr + 3 x 4,4tr = 24,2tr
        p_cu = params.load("2024-06")
        rec = dict(self.chinh_thuc, DEPENDENT_CNT=3)
        self.assertEqual(thue.total_ded(rec, p_cu), Decimal(24_200_000))
        taxable = thue.taxable_inc(Decimal(225_000_000), Decimal(5_508_000), Decimal(24_200_000))
        self.assertEqual(taxable, Decimal(195_292_000))
        self.assertEqual(thue.pit(taxable, rec, p_cu), Decimal(53_852_200))


if __name__ == "__main__":
    unittest.main()
