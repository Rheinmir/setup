"""Test đỏ frame p15 — PC điện thoại pro-rata (C5.3.2). Tổng quát: đoạn lấy từ
p10 (điều động)/p08 (thử việc) thật, định mức tra p03, không tra bảng theo NV."""
import unittest
from app.p15_pcdienthoai import tinh_pc_dien_thoai


class TestPCDienThoai(unittest.TestCase):
    def test_nv001_dieu_dong_hai_muc(self):
        r = tinh_pc_dien_thoai("NV001")
        self.assertEqual(len(r["theo_bo_phan"]), 2)
        # VP HCM (NV.01-VP=300k) 10 ngày + Quan Lạn (NV.01-CT=400k) 4 ngày /26
        self.assertAlmostEqual(r["tong"], 10 / 26 * 800_000 + 4 / 26 * 1_000_000, delta=1)

    def test_nv004_thu_viec_tach_2_giai_doan(self):
        r = tinh_pc_dien_thoai("NV004")
        self.assertEqual(len(r["giai_doan"]), 2)
        self.assertIn("thử việc", r["giai_doan"][0])
        self.assertIn("chính thức", r["giai_doan"][1])

    def test_nv002_khong_dieu_dong_khong_con_tv_trong_ky(self):
        # NV002 chưa từng xuất hiện trong test p15 cũ — 1 bộ phận, thử việc đã
        # kết thúc từ 2022 (ngoài kỳ) → 1 đoạn duy nhất, tổng quát cho NV "bình thường".
        r = tinh_pc_dien_thoai("NV002")
        self.assertEqual(len(r["theo_bo_phan"]), 1)
        self.assertAlmostEqual(r["tong"], 26 / 26 * 300_000, delta=30_000)


if __name__ == "__main__":
    unittest.main()
