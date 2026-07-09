"""Test đỏ frame p04 — tờ trình duyệt riêng ghi đè định mức chung (C5.2, C5.3.3, C5.3.7)."""
import unittest
from app.p04_totrinh import dinh_muc_cuoi


class TestToTrinhOverride(unittest.TestCase):
    def test_gddar_xang_tu_to_trinh_va_loai_pc_di_lai(self):
        tien, nguon = dinh_muc_cuoi("xang_xe", "NV007", "2026-07-01")
        self.assertEqual(tien, 10_000_000)
        self.assertIn("TT-2026/018", nguon)
        tien_dl, nguon_dl = dinh_muc_cuoi("di_lai", "NV007", "2026-07-01")
        self.assertEqual(tien_dl, 0)
        self.assertIn("GĐDA", nguon_dl)

    def test_tai_xe_hn_dich_danh(self):
        tien, nguon = dinh_muc_cuoi("xang_xe", "NV006", "2026-07-01")
        self.assertEqual(tien, 2_600_000)
        self.assertIn("TT-2026/031", nguon)

    def test_ngay_hieu_luc_giua_ky(self):
        tien_truoc, _ = dinh_muc_cuoi("khac", "NV008", "2026-06-15")
        self.assertEqual(tien_truoc, 0)
        tien_sau, _ = dinh_muc_cuoi("khac", "NV008", "2026-06-21")
        self.assertEqual(tien_sau, 1_500_000)

    def test_khong_to_trinh_ve_muc_chung(self):
        tien, nguon = dinh_muc_cuoi("xang_xe", "NV002", "2026-07-01")
        self.assertEqual(tien, 0)
        self.assertIn("QĐ chung", nguon)


if __name__ == "__main__":
    unittest.main()
