"""Test đỏ frame p25 — Template 0 trình ký, gộp về dự án ngày 20 khi điều động (C6.3)."""
import unittest
from app.p25_template0 import bang_trinh_ky


class TestTemplate0(unittest.TestCase):
    def test_nv001_gom_ve_quan_lan(self):
        bang = bang_trinh_ky("2026-07")
        quan_lan = bang.get("CT Quan Lạn", [])
        msnv_list = [r["msnv"] for r in quan_lan]
        self.assertIn("NV001", msnv_list)
        vp_hcm = bang.get("VP HCM", [])
        self.assertNotIn("NV001", [r["msnv"] for r in vp_hcm])
        row = next(r for r in quan_lan if r["msnv"] == "NV001")
        self.assertAlmostEqual(row["tong"], 16.0, delta=1.0)

    def test_co_mat_bao(self):
        bang = bang_trinh_ky("2026-07")
        quan_lan = bang.get("CT Quan Lạn", [])
        self.assertIn("NV005", [r["msnv"] for r in quan_lan])

    def test_khong_co_cot_tien(self):
        bang = bang_trinh_ky("2026-07")
        text = str(bang).lower()
        for kw in ("lương", "phụ cấp", "tiền"):
            self.assertNotIn(kw, text)


if __name__ == "__main__":
    unittest.main()
