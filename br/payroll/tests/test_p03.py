"""Test đỏ frame p03 — bảng định mức: điện thoại, đi lại, CT+CTX, CT xa dự án (C5.3.x)."""
import unittest
from app.p03_dinhmuc import dinh_muc


class TestBangDinhMuc(unittest.TestCase):
    def test_dien_thoai_theo_khoi(self):
        hs = {"ngach": "QL.02"}
        self.assertEqual(dinh_muc("dien_thoai", hs, {"khoi": "CT"}), 1_000_000)
        self.assertEqual(dinh_muc("dien_thoai", hs, {"khoi": "VP"}), 800_000)
        self.assertEqual(dinh_muc("dien_thoai", {"ngach": "TV"}, {"khoi": "VP"}), 0)

    def test_di_lai_nhom_doi_tuong(self):
        cht = {"chuc_danh": "CHT", "trinh_do": "Đại học"}
        self.assertEqual(dinh_muc("di_lai", cht, {"dai": "khac_mien"}), 11_200_000)
        nv02 = {"ngach": "NV.02", "trinh_do": "Cao đẳng"}
        self.assertEqual(dinh_muc("di_lai", nv02, {"dai": "30-100"}), 250_000)

    def test_ct_xa_du_an(self):
        hs = {"chuc_danh": "Thủ kho"}
        self.assertEqual(dinh_muc("ct_xa_du_an", hs, {"du_an": "Quan Lạn"}), 2_000_000)

    def test_nhom_doi_tuong_dh_khong_phai_cd(self):
        nv01_dh = {"ngach": "NV.01", "trinh_do": "Đại học"}
        nv02_dh = {"ngach": "NV.02", "trinh_do": "Đại học"}
        self.assertNotEqual(
            dinh_muc("di_lai", nv01_dh, {"dai": "30-100"}),
            dinh_muc("di_lai", nv02_dh, {"dai": "30-100"}),
        )


if __name__ == "__main__":
    unittest.main()
