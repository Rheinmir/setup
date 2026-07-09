"""Test đỏ frame p28 — Web UI stdlib theo mockup: role ẩn tiền, khóa kỳ 2 bước, dark toggle (C3, C8)."""
import unittest
import http.client
import threading
import time
from app.p28_ui import build_server


class TestUIServe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = build_server(port=0)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.2)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def _get(self, path, headers=None):
        conn = http.client.HTTPConnection("localhost", self.port, timeout=5)
        conn.request("GET", path, headers=headers or {})
        resp = conn.getresponse()
        body = resp.read().decode("utf-8")
        conn.close()
        return resp.status, body

    def test_trang_chu_200_du_sidebar(self):
        status, body = self._get("/")
        self.assertEqual(status, 200)
        for muc in ("Dashboard", "Bảng công", "Suất ăn", "Phụ cấp", "Tăng ca",
                    "Master data", "Tờ trình", "Khóa kỳ", "Trình ký", "Đơn treo"):
            self.assertIn(muc, body)

    def test_vai_thu_ky_khong_thay_tien(self):
        status, body = self._get("/pc?role=thuky")
        self.assertEqual(status, 200)
        # Chỉ kiểm vùng NỘI DUNG <main>, không phải cả trang — sidebar có menu
        # "Công thức lương" chứa chữ "lương" hợp lệ, không liên quan tới việc ẩn
        # số tiền của NV (bug test cũ quá rộng, phát hiện khi thêm menu mới).
        main_content = body.split("<main>")[1].split("</main>")[0]
        for kw in (" đ", "VNĐ", "lương"):
            self.assertNotIn(kw, main_content)

    def test_toggle_theme_that_khong_chi_data_theme_tinh(self):
        # Test cũ chỉ kiểm "data-theme" xuất hiện — hard-code data-theme="light" cũng
        # pass được mà không cần toggle thật (bug lọt qua, feedback user 09/07).
        # Kiểm chặt hơn: có script chống FOUC + nút gạt thật + ghi localStorage.
        status, body = self._get("/")
        self.assertIn("localStorage.getItem(\"payroll-theme\")", body)  # chống FOUC
        self.assertIn('id="theme-switch"', body)  # nút gạt thật, không phải chữ tĩnh
        self.assertIn("localStorage.setItem(", body)  # đổi theme có lưu lại
        self.assertNotIn('data-theme="light">', body)  # KHÔNG còn hard-code cứng


if __name__ == "__main__":
    unittest.main()
