"""Test đỏ frame p13 — engine pro-rata dùng chung, tái lập Ví dụ 2 PRD (C5.2, C5.4)."""
import unittest
from app.p13_prorata import tinh_prorata


class TestProrataEngine(unittest.TestCase):
    def test_vi_du_2_duoi_14_ngay(self):
        bo_phan = {
            "A": {"lam_viec": 3, "le": 1, "phep": 6, "nghi_huong_luong": 0, "khong_luong": 0},
            "B": {"lam_viec": 3, "le": 2, "phep": 7, "nghi_huong_luong": 2, "khong_luong": 1},
        }
        dinh_muc = {"A": 500_000, "B": 350_000}
        r = tinh_prorata(bo_phan, cong_chuan=26, dinh_muc_fn=lambda bp: dinh_muc[bp])
        expected = (3 + 1) / 26 * 500_000 + (3 + 2) / 26 * 350_000
        self.assertAlmostEqual(r["tong"], expected, delta=1000)

    def test_du_14_ngay_dung_quy_tac_thuong(self):
        bo_phan = {"A": {"lam_viec": 20, "le": 1, "phep": 2, "nghi_huong_luong": 0, "khong_luong": 0}}
        r = tinh_prorata(bo_phan, cong_chuan=26, dinh_muc_fn=lambda bp: 800_000)
        self.assertGreater(r["tong"], 0)

    def test_trace_du_4_yeu_to(self):
        bo_phan = {"A": {"lam_viec": 20, "le": 0, "phep": 0, "nghi_huong_luong": 0, "khong_luong": 0}}
        r = tinh_prorata(bo_phan, cong_chuan=26, dinh_muc_fn=lambda bp: 800_000)
        trace = r["trace"]["A"]
        for kw in ("ngày", "định mức", "nguồn", "26"):
            self.assertIn(kw, trace if isinstance(trace, str) else str(trace))


if __name__ == "__main__":
    unittest.main()
