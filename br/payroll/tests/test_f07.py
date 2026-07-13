"""f07 tăng ca (BR C9) — OT là SỐ TIỀN INPUT, không tự chế công thức giờ→tiền."""
import unittest
from decimal import Decimal
from app import tangca, params


class TestTangCa(unittest.TestCase):
    def setUp(self):
        self.p = params.load("2026-03")

    def test_ot_la_so_tien_input_khong_tinh_tu_gio(self):
        # BR C9.1: engine chỉ nhận tiền, không nhân hệ số từ giờ
        rec = {"OT_TAX": Decimal(5_000_000), "OT_NONTAX": Decimal(1_000_000)}
        self.assertEqual(tangca.ot_tax(rec, self.p), Decimal(5_000_000))
        self.assertEqual(tangca.ot_nontax(rec, self.p), Decimal(1_000_000))

    def test_co_ot_from_hours_mac_dinh_TAT(self):
        self.assertFalse(self.p["ot_from_hours"])

    def test_he_so_chua_biet_de_None_khong_bia(self):
        # BR C9.2 / A3: chỉ điền cái tài liệu nói thẳng
        m = self.p["ot_multipliers"]
        self.assertEqual(m["sunday"], 2.0)
        self.assertIsNone(m["weekday"])
        self.assertIsNone(m["night_extra"])
        self.assertIsNone(m["holiday_300"])

    def test_bat_ot_from_hours_ma_thieu_he_so_thi_no_ra_loi_khong_doan_bua(self):
        p = dict(self.p, ot_from_hours=True)
        with self.assertRaises(ValueError):
            tangca.ot_tu_gio({"gio_thuong": 10}, p)

    def test_ngay_nghi_bu_le_tet_cong_2_ngay(self):
        # BR C9.3: làm ngày Lễ/Tết → +2 ngày nghỉ bù cho mỗi ngày làm
        self.assertEqual(tangca.ngay_nghi_bu({"ngay_lam_le": 2, "ngay_lam_truyen_thong": 0}),
                         Decimal(4))

    def test_ngay_nghi_bu_truyen_thong_cong_1_ngay(self):
        self.assertEqual(tangca.ngay_nghi_bu({"ngay_lam_le": 0, "ngay_lam_truyen_thong": 3}),
                         Decimal(3))


if __name__ == "__main__":
    unittest.main()
