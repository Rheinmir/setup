"""f09 BHXH/BHYT/BHTN (BR C11) — 7 con số dòng 9 phải khớp từng đồng."""
import unittest
from decimal import Decimal
from app import baohiem, params


class TestBaoHiem(unittest.TestCase):
    def setUp(self):
        self.p = params.load("2026-03")
        self.rec = {"CONTRACT_TYPE": "Chính thức", "NATIONALITY": "Việt Nam",
                    "CONTRACT_TOTAL": Decimal(200_000_000),
                    "SI_ADJ": 0, "HI_ADJ": 0, "UI_ADJ": 0,
                    "SI_CTY_ADJ": 0, "TNLD_CTY_ADJ": 0, "HI_CTY_ADJ": 0, "UI_CTY_ADJ": 0,
                    "UNPAID_DAYS": 0, "SI_DAYS": 0, "PROB_DAYS": 0}

    def test_hai_tran_cung_ton_tai(self):
        # BR C4.2 — cột HIỂN THỊ dùng 50,6tr; BASE TÍNH dùng 46,8tr
        self.assertEqual(baohiem.ins_sal_bh(self.rec, self.p), Decimal(50_600_000))
        self.assertEqual(baohiem.ins_base_bh(self.rec, self.p), Decimal(46_800_000))
        self.assertEqual(baohiem.ins_sal_ui(self.rec, self.p), Decimal(106_200_000))

    def test_bhxh_nhan_vien_ground_truth_dong_9(self):
        self.assertEqual(baohiem.si_emp(self.rec, self.p), Decimal(3_744_000))
        self.assertEqual(baohiem.hi_emp(self.rec, self.p), Decimal(702_000))
        self.assertEqual(baohiem.ui_emp(self.rec, self.p), Decimal(1_062_000))
        self.assertEqual(baohiem.total_ins(self.rec, self.p), Decimal(5_508_000))

    def test_bhxh_cong_ty_ground_truth_dong_9(self):
        self.assertEqual(baohiem.si_cty(self.rec, self.p), Decimal(7_956_000))
        self.assertEqual(baohiem.tnld_cty(self.rec, self.p), Decimal(234_000))
        self.assertEqual(baohiem.hi_cty(self.rec, self.p), Decimal(1_404_000))
        self.assertEqual(baohiem.ui_cty(self.rec, self.p), Decimal(1_062_000))
        self.assertEqual(baohiem.total_ins_cty(self.rec, self.p), Decimal(10_656_000))
        self.assertEqual(baohiem.kpcd_cty(self.rec, self.p), Decimal(936_000))

    def test_tnld_dung_tran_BH_khong_phai_tran_BHTN(self):
        # BR C3.3 — cạm bẫy: to-be dùng trần 106,2tr → 531.000 (SAI). as-is: 46,8tr → 234.000
        self.assertEqual(baohiem.tnld_cty(self.rec, self.p), Decimal(234_000))

    def test_phi_cong_doan_co_tran_253k(self):
        # BR C4.5: 46,8tr x 0,5% = 234.000 < trần 253.000 → lấy 234.000
        self.assertEqual(baohiem.union_fee(self.rec, self.p), Decimal(234_000))

    def test_luong_rat_cao_thi_cong_doan_van_khong_vuot_tran(self):
        rec = dict(self.rec, CONTRACT_TOTAL=Decimal(999_000_000))
        self.assertLessEqual(baohiem.union_fee(rec, self.p), Decimal(253_000))

    def test_thu_viec_khong_dong_bao_hiem(self):
        rec = dict(self.rec, CONTRACT_TYPE="Thử việc")
        self.assertEqual(baohiem.ins_sal_bh(rec, self.p), Decimal(0))
        self.assertEqual(baohiem.total_ins(rec, self.p), Decimal(0))

    def test_nguoi_nuoc_ngoai_khong_dong_BHTN(self):
        # BR C11.4
        rec = dict(self.rec, NATIONALITY="Nước ngoài")
        self.assertEqual(baohiem.ui_emp(rec, self.p), Decimal(0))
        self.assertGreater(baohiem.si_emp(rec, self.p), Decimal(0))

    def test_luat_14_ngay_mien_dong_bhxh(self):
        # BR C11.3: nghỉ không lương + ốm + thử việc >= 14 ngày trong tháng dương lịch → KHÔNG đóng
        rec = dict(self.rec, UNPAID_DAYS=Decimal(14))
        self.assertTrue(baohiem.mien_dong_bhxh(rec, self.p))
        self.assertEqual(baohiem.total_ins(rec, self.p), Decimal(0))
        self.assertEqual(baohiem.total_ins_cty(rec, self.p), Decimal(0))

    def test_13_ngay_van_dong_bhxh(self):
        rec = dict(self.rec, UNPAID_DAYS=Decimal(13))
        self.assertFalse(baohiem.mien_dong_bhxh(rec, self.p))
        self.assertEqual(baohiem.total_ins(rec, self.p), Decimal(5_508_000))


if __name__ == "__main__":
    unittest.main()
