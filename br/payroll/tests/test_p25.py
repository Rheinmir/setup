"""Test đỏ frame p25 — Template 0 trình ký, gộp về dự án ngày 20 (C6.3).
Tổng quát: tính cho TOÀN BỘ roster nhan_vien.csv từ công thô thật (p06/p07)."""
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
        self.assertEqual(row["tong"], 14.0)  # 10 VP + 4 Quan Lạn (dữ liệu thật)

    def test_co_mat_bao(self):
        bang = bang_trinh_ky("2026-07")
        quan_lan = bang.get("CT Quan Lạn", [])
        self.assertIn("NV005", [r["msnv"] for r in quan_lan])

    def test_khong_co_cot_tien(self):
        bang = bang_trinh_ky("2026-07")
        text = str(bang).lower()
        for kw in ("lương", "phụ cấp", "tiền"):
            self.assertNotIn(kw, text)

    def test_du_ca_12_nv_trong_roster(self):
        # Tổng quát: tất cả NV có công thô trong nhan_vien.csv đều xuất hiện.
        bang = bang_trinh_ky("2026-07")
        tat_ca = {r["msnv"] for rows in bang.values() for r in rows}
        self.assertGreaterEqual(len(tat_ca), 11)  # 12 NV, trừ NV không có công thô


if __name__ == "__main__":
    unittest.main()
