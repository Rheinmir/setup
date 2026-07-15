"""f01 params — tham số MỘT chỗ, chọn theo effective_from (BR C4.1)."""
import unittest
from decimal import Decimal
from app import params


class TestParams(unittest.TestCase):
    def test_ky_2026_lay_bo_hien_hanh(self):
        p = params.load("2026-03")
        self.assertEqual(Decimal(p["personal_ded"]), Decimal(15_500_000))
        self.assertEqual(Decimal(p["dependent_ded"]), Decimal(6_200_000))

    def test_ky_cu_lay_bo_cu(self):
        p = params.load("2024-06")
        self.assertEqual(Decimal(p["personal_ded"]), Decimal(11_000_000))
        self.assertEqual(Decimal(p["dependent_ded"]), Decimal(4_400_000))

    def test_hai_tran_bhxh_cung_ton_tai(self):
        # BR C4.2: cột hiển thị dùng 50,6tr; công thức tính dùng 46,8tr
        p = params.load("2026-03")
        self.assertEqual(Decimal(p["ins_cap_bh_display"]), Decimal(50_600_000))
        self.assertEqual(Decimal(p["ins_cap_bh"]), Decimal(46_800_000))
        self.assertEqual(Decimal(p["ins_cap_ui"]), Decimal(106_200_000))

    def test_cac_tham_so_chot(self):
        p = params.load("2026-03")
        self.assertEqual(Decimal(p["meal_unit_price"]), Decimal(45_000))
        self.assertEqual(Decimal(p["meal_tax_free"]), Decimal(730_000))
        self.assertEqual(Decimal(p["union_fee_cap"]), Decimal(253_000))
        self.assertEqual(len(p["pit_brackets"]), 5)
        self.assertFalse(p["ot_from_hours"])

    def test_ky_truoc_moi_bo_tham_so_thi_bao_loi(self):
        with self.assertRaises(ValueError):
            params.load("1999-01")

    # ── FE-23 Master Data — xem toàn bộ, không chỉ bộ đang active ───────────
    def test_list_all_tra_du_2_bo_tham_so(self):
        d = params.list_all()
        self.assertEqual(len(d["param_sets"]), 2)
        self.assertEqual(d["param_sets"][0]["effective_from"], "2020-01-01")
        self.assertEqual(d["param_sets"][1]["effective_from"], "2026-01-01")

    def test_list_all_co_muc_chua_hieu_luc(self):
        d = params.list_all()
        self.assertIn("_pending_hr", d)
        self.assertIn("ins_cap_bh_new", d["_pending_hr"])


if __name__ == "__main__":
    unittest.main()
