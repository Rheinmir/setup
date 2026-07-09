"""Test đỏ frame p06 — adapter Workday mock (ranh giới verified:false) (C4.2)."""
import unittest
import app.p06_workday as wd


class TestWorkdayAdapter(unittest.TestCase):
    def test_verified_false_flag(self):
        self.assertFalse(wd.VERIFIED)

    def test_cong_tho_loc_dung_bien_ky(self):
        rows = wd.cong_tho("2026-07")
        self.assertTrue(rows)
        for r in rows:
            self.assertGreaterEqual(r["ngay"], "2026-06-21")
            self.assertLessEqual(r["ngay"], "2026-07-20")

    def test_don_cho_duyet_giu_nguyen_trang(self):
        rows = wd.cong_tho("2026-07")
        cho_duyet = [r for r in rows if r["ky_hieu"] == "?P"]
        self.assertTrue(cho_duyet)
        self.assertEqual(cho_duyet[0]["ky_hieu"], "?P")

    def test_ho_so_mat_bao(self):
        hs = wd.ho_so("NV005")
        self.assertEqual(hs["employee_type"], "MatBao")


if __name__ == "__main__":
    unittest.main()
