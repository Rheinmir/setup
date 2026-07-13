"""f15 UI — 3 màn hình, phải HIT thật (BR C15)."""
import unittest
import threading
import urllib.request
from app import ui


class TestUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ui.build_server(0)          # cổng 0 = OS tự cấp, không đụng cổng đang dùng
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def get(self, path):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=10) as r:
            self.assertEqual(r.status, 200)
            return r.read().decode()

    def test_bang_luong_hien_dung_luong_thuc_nhan_cua_ground_truth(self):
        html = self.get("/")
        self.assertIn("189.930.161", html)          # BR C17.1 — số phải HIỆN trên màn, không chỉ trong test

    def test_phieu_luong_dung_layout_that(self):
        html = self.get("/payslip/GT-ROW9")
        self.assertIn("189.930.161", html)
        self.assertIn("21", html)                    # kỳ "Từ ngày 21/… đến ngày 20/…"
        for muc in ("Lương thực nhận", "Thuế TNCN"):
            self.assertIn(muc, html)

    def test_trace_cong_thuc_di_nguoc_duoc(self):
        # BR C14.1 — lý do dự án tồn tại
        html = self.get("/trace/GT-ROW9/NET_PAY")
        self.assertIn("NET_PAY", html)
        self.assertIn("GROSS", html)                 # phụ thuộc phải hiện ra
        self.assertIn("C13", html)                   # clause_id BR phải hiện ra

    def test_trace_hien_tham_so_da_dung(self):
        html = self.get("/trace/GT-ROW9/SI_EMP")
        self.assertIn("46.800.000", html)            # trần BH thật, kèm nguồn tham số

    def test_co_toggle_sang_toi_va_chong_FOUC(self):
        # BR C15.2 — không ép mode
        html = self.get("/")
        self.assertIn("localStorage", html)
        self.assertIn("prefers-color-scheme", html)

    def test_tien_can_phai_va_dinh_dang_viet_nam(self):
        html = self.get("/")
        self.assertIn("tabular-nums", html)


if __name__ == "__main__":
    unittest.main()
