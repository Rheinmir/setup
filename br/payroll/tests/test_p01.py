"""Test đỏ frame p01 — lịch kỳ công 21–20 + kỳ BHXH song song (C4.1)."""
import unittest
from app.p01_lichky import sinh_lich_ky


class TestLichKyCong(unittest.TestCase):
    def setUp(self):
        self.ky = sinh_lich_ky("2026-07")

    def test_bien_ky_cong(self):
        self.assertEqual(self.ky["tu"], "2026-06-21")
        self.assertEqual(self.ky["den"], "2026-07-20")

    def test_cong_chuan_vp_thap_hon_ct(self):
        self.assertLess(self.ky["cong_chuan_vp"], self.ky["cong_chuan_ct"])

    def test_cong_chuan_ct_hop_ly(self):
        self.assertGreater(self.ky["cong_chuan_ct"], 20)

    def test_ngay_thuoc_ky_cong_nhung_khac_thang_bhxh(self):
        m = self.ky["ngay_to_thang_bhxh"]
        self.assertEqual(m["2026-06-25"], "2026-06")

    def test_co_ngay_le(self):
        self.assertTrue(any(d.get("le") for d in self.ky["ngay"]))


if __name__ == "__main__":
    unittest.main()
