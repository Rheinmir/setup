"""Test đỏ frame p08 — tách thử việc/chính thức theo mốc kết thúc TV (C5.1.1)."""
import unittest
from app.p08_thuviec import tach_thu_viec


class TestTachThuViec(unittest.TestCase):
    def test_nv004_moc_giua_ky(self):
        r = tach_thu_viec("NV004", "2026-07")
        # mốc kết thúc TV = 2026-07-10 → 09/07 trở về trước là TV
        self.assertGreater(r["ngay_tv"]["lam_viec"], 0)
        self.assertGreater(r["ngay_sau_tv"]["lam_viec"], 0)

    def test_khong_co_moc_toan_bo_sau_tv(self):
        r = tach_thu_viec("NV002", "2026-07")
        self.assertEqual(r["ngay_tv"]["lam_viec"], 0)
        self.assertGreater(r["ngay_sau_tv"]["lam_viec"], 0)

    def test_mat_bao_khong_vo(self):
        r = tach_thu_viec("NV005", "2026-07")
        self.assertIsInstance(r, dict)


if __name__ == "__main__":
    unittest.main()
