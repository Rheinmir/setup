"""Test đỏ frame p10 — tách công theo bộ phận khi điều động (C5.1.3, Ví dụ 2 PRD).
Tổng quát: engine thuần `gom_theo_bo_phan` nhận LIST bản ghi thật (không tra bảng
theo ID) + `tach_dieu_dong` đọc công thô THẬT từ p06 cho bất kỳ msnv nào."""
import unittest
from app.p10_dieudong import gom_theo_bo_phan, tach_dieu_dong


class TestGomTheoBoPhan(unittest.TestCase):
    def test_vi_du_2_prd(self):
        # Ví dụ 2 PRD: A={LV3,lễ1,phép6}, B={LV3,phép7,R2,Ro1,lễ2}
        rows = (
            [{"ngay": f"2026-06-{21+i}", "ky_hieu": "x", "bo_phan": "A"} for i in range(3)]
            + [{"ngay": "2026-06-24", "ky_hieu": "TC100", "bo_phan": "A"}]
            + [{"ngay": f"2026-06-{25+i}", "ky_hieu": "P", "bo_phan": "A"} for i in range(6)]
            + [{"ngay": f"2026-07-{1+i}", "ky_hieu": "x", "bo_phan": "B"} for i in range(3)]
            + [{"ngay": f"2026-07-{4+i}", "ky_hieu": "P", "bo_phan": "B"} for i in range(7)]
            + [{"ngay": f"2026-07-{11+i}", "ky_hieu": "R", "bo_phan": "B"} for i in range(2)]
            + [{"ngay": "2026-07-13", "ky_hieu": "Ro", "bo_phan": "B"}]
            + [{"ngay": f"2026-07-{14+i}", "ky_hieu": "TC100", "bo_phan": "B"} for i in range(2)]
        )
        r = gom_theo_bo_phan(rows)
        a, b = r["A"], r["B"]
        self.assertEqual(a["lam_viec"], 3)
        self.assertEqual(a["le"], 1)
        self.assertEqual(a["phep"], 6)
        self.assertEqual(b["lam_viec"], 3)
        self.assertEqual(b["phep"], 7)
        self.assertEqual(b["le"], 2)
        self.assertEqual(b["nghi_huong_luong"], 2)
        self.assertEqual(b["khong_luong"], 1)

    def test_ngay_dieu_dong_la_ngay_doi_bo_phan_dau_tien(self):
        rows = [
            {"ngay": "2026-07-01", "ky_hieu": "x", "bo_phan": "X"},
            {"ngay": "2026-07-02", "ky_hieu": "x", "bo_phan": "Y"},
        ]
        r = gom_theo_bo_phan(rows)
        self.assertEqual(r["ngay_dieu_dong"], "2026-07-02")


class TestTachDieuDongTuCSV(unittest.TestCase):
    def test_nv001_dieu_dong_05_07_tu_du_lieu_that(self):
        r = tach_dieu_dong("NV001", "2026-07")
        self.assertIn("ngay_dieu_dong", r)
        self.assertEqual(r["ngay_dieu_dong"], "2026-07-05")
        self.assertEqual(r["VP HCM"]["lam_viec"], 10)
        self.assertEqual(r["CT Quan Lạn"]["lam_viec"], 4)

    def test_khong_dieu_dong_mot_bo_phan(self):
        r = tach_dieu_dong("NV002", "2026-07")
        bo_phan_keys = [k for k in r if k != "ngay_dieu_dong"]
        self.assertEqual(len(bo_phan_keys), 1)
        self.assertNotIn("ngay_dieu_dong", r)

    def test_nv003_tong_quat_cho_nv_moi_chua_test_truoc_do(self):
        # NV003 chưa từng xuất hiện trong bất kỳ test cũ nào của p10 — chứng minh
        # tach_dieu_dong tính TỪ CSV cho bất kỳ NV nào, không tra bảng theo ID.
        r = tach_dieu_dong("NV003", "2026-07")
        self.assertIn("CT Bình Dương", r)
        self.assertGreater(r["CT Bình Dương"]["lam_viec"], 0)


if __name__ == "__main__":
    unittest.main()
