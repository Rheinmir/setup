"""Test đỏ frame p17 — PC đi lại: nhóm đối tượng × dải khoảng cách (C5.3.4).
Tổng quát: tỉnh/dải/định mức tra CSV thật (dm_bo_phan, dm_khoang_cach, p03),
đoạn từ p10 thật, không tra bảng theo NV."""
import unittest
from app.p17_pcdilai import tinh_pc_di_lai


class TestPCDiLai(unittest.TestCase):
    def test_nv001_quan_lan_khac_mien(self):
        r = tinh_pc_di_lai("NV001")
        self.assertIn("CT Quan Lạn", r["theo_bo_phan"])
        self.assertGreater(r["theo_bo_phan"]["CT Quan Lạn"], 0)

    def test_nv001_vp_hcm_duoi_30_bang_0(self):
        r = tinh_pc_di_lai("NV001")
        self.assertEqual(r["theo_bo_phan"].get("VP HCM", 0), 0)

    def test_nv009_khong_co_ngay_lam_viec_thuc_te_o_ct_bang_0(self):
        # NV009 kỳ này chỉ 1 ngày LV thực tế (VP HCM, <30km→0đ) — CT Long An
        # toàn Ro/R (không LV thực tế) → PC đi lại thực = 0, đúng thực tế dữ liệu.
        r = tinh_pc_di_lai("NV009")
        self.assertEqual(r["tong"], 0)

    def test_gddar_bang_0(self):
        r = tinh_pc_di_lai("NV007")
        self.assertEqual(r["tong"], 0)
        self.assertIn("GĐDA", str(r["trace"]))

    def test_nv003_tong_quat_cho_nv_chua_test_truoc_do(self):
        # NV003 chưa từng xuất hiện trong test p17 cũ — CT Bình Dương dải 30-100.
        r = tinh_pc_di_lai("NV003")
        self.assertIn("CT Bình Dương", r["theo_bo_phan"])
        self.assertGreater(r["theo_bo_phan"]["CT Bình Dương"], 0)


if __name__ == "__main__":
    unittest.main()
