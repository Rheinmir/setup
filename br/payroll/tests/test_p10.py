"""Test đỏ frame p10 — tách công theo bộ phận khi điều động (C5.1.3, Ví dụ 2 PRD)."""
import unittest
from app.p10_dieudong import tach_dieu_dong


class TestTachDieuDong(unittest.TestCase):
    def test_vi_du_2_prd(self):
        # NV giả lập theo đúng số Ví dụ 2: A={LV3,lễ1,phép6}, B={LV3,phép7,R2,Ro1,lễ2}
        r = tach_dieu_dong("NV_vidu2")
        a, b = r["bo_phan_A"], r["bo_phan_B"]
        self.assertEqual(a["lam_viec"], 3)
        self.assertEqual(a["le"], 1)
        self.assertEqual(a["phep"], 6)
        self.assertEqual(b["lam_viec"], 3)
        self.assertEqual(b["phep"], 7)
        self.assertEqual(b["le"], 2)

    def test_nv001_dieu_dong_05_07(self):
        r = tach_dieu_dong("NV001")
        self.assertIn("ngay_dieu_dong", r)
        self.assertEqual(r["ngay_dieu_dong"], "2026-07-05")
        self.assertEqual(len(r) - 1, 2)  # 2 bộ phận + key ngay_dieu_dong

    def test_khong_dieu_dong_mot_bo_phan(self):
        r = tach_dieu_dong("NV002")
        bo_phan_keys = [k for k in r if k != "ngay_dieu_dong"]
        self.assertEqual(len(bo_phan_keys), 1)


if __name__ == "__main__":
    unittest.main()
