"""Test đỏ frame p11 — BHXH 2 trục thời gian: kỳ công vs tháng dương lịch (C5.1.4)."""
import unittest
from app.p11_bhxh import tong_hop_bhxh_thang


class TestBHXHHaiTruc(unittest.TestCase):
    def test_thai_san_khong_dong(self):
        r = tong_hop_bhxh_thang("NV010", "2026-07")
        self.assertFalse(r["dien_dong"])
        self.assertEqual(r["trich_nv"], 0)

    def test_ty_le_trich(self):
        r = tong_hop_bhxh_thang("NV002", "2026-07")
        luong = 15_000_000
        expected_nv = luong * (8 + 1.5 + 1) / 100
        self.assertAlmostEqual(r["trich_nv"], expected_nv, delta=luong * 0.01)

    def test_ngay_25_06_thuoc_thang_bhxh_06(self):
        r = tong_hop_bhxh_thang("NV002", "2026-06")
        self.assertIn("2026-06-25", [d for d in r.get("ngay_tinh_list", [])] or r["ngay_tinh"])


if __name__ == "__main__":
    unittest.main()
