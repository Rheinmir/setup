"""Test đỏ frame p11 — BHXH 2 trục thời gian: kỳ công vs tháng dương lịch (C5.1.4).
Tổng quát: đọc công thô + hồ sơ THẬT từ p06/p07, không tra bảng theo msnv."""
import unittest
from app.p11_bhxh import tong_hop_bhxh_thang


class TestBHXHHaiTruc(unittest.TestCase):
    def test_thai_san_khong_dong(self):
        r = tong_hop_bhxh_thang("NV010", "2026-07")
        self.assertFalse(r["dien_dong"])
        self.assertEqual(r["trich_nv"], 0)

    def test_ty_le_trich_luong_that_tu_ho_so(self):
        r = tong_hop_bhxh_thang("NV002", "2026-06")
        luong = 15_000_000  # nhan_vien.csv luong_co_ban_thang(ASSUMED)
        expected_nv = luong * (8 + 1.5 + 1) / 100
        self.assertAlmostEqual(r["trich_nv"], expected_nv, delta=1)

    def test_ngay_25_06_thuoc_thang_bhxh_06(self):
        r = tong_hop_bhxh_thang("NV002", "2026-06")
        self.assertIn("2026-06-25", r["ngay_tinh"])

    def test_nv003_tong_quat_cho_nv_chua_test_truoc_do(self):
        # NV003 chưa từng xuất hiện trong test p11 cũ — chứng minh tính từ CSV thật.
        r = tong_hop_bhxh_thang("NV003", "2026-07")
        self.assertTrue(r["dien_dong"])
        self.assertGreater(r["trich_nv"], 0)
        expected_nv = 17_000_000 * (8 + 1.5 + 1) / 100
        self.assertAlmostEqual(r["trich_nv"], expected_nv, delta=1)


if __name__ == "__main__":
    unittest.main()
