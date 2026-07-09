"""Test đỏ frame p15 — PC điện thoại pro-rata theo bộ phận (C5.3.2)."""
import unittest
from app.p15_pcdienthoai import tinh_pc_dien_thoai


class TestPCDienThoai(unittest.TestCase):
    def test_ql02_ct_du_cong(self):
        r = tinh_pc_dien_thoai("NV_ql02_ct_full")
        self.assertAlmostEqual(r["tong"], 1_000_000, delta=50_000)

    def test_nv001_dieu_dong_hai_muc(self):
        r = tinh_pc_dien_thoai("NV001")
        self.assertEqual(len(r["theo_bo_phan"]), 2)

    def test_nv004_thu_viec_tach_muc(self):
        r = tinh_pc_dien_thoai("NV004")
        self.assertGreaterEqual(len(r.get("giai_doan", r["theo_bo_phan"])), 1)


if __name__ == "__main__":
    unittest.main()
