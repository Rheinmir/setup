"""Test đỏ frame p23 — nhánh Mắt Bão: chốt sớm + grid định mức riêng (C6.1)."""
import unittest
from app.p23_matbao import policy_nhan_su


class TestMatBao(unittest.TestCase):
    def test_nv005_la_mat_bao_grid_rieng(self):
        p = policy_nhan_su("NV005", ngay="2026-07-08")
        self.assertTrue(p["la_mat_bao"])
        self.assertEqual(p["dinh_muc_grid"]("dien_thoai"), 200_000)

    def test_sau_ngay_chot_dong_bang(self):
        p = policy_nhan_su("NV005", ngay="2026-07-20")
        self.assertTrue(p["da_qua_chot"])

    def test_chinh_thuc_khong_doi_hanh_vi(self):
        p = policy_nhan_su("NV002", ngay="2026-07-08")
        self.assertFalse(p["la_mat_bao"])


if __name__ == "__main__":
    unittest.main()
