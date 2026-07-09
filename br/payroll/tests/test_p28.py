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
        for kw in (" đ", "VNĐ", "lương"):
            self.assertNotIn(kw, body)

    def test_data_theme_hook(self):
        status, body = self._get("/")
        self.assertIn("data-theme", body)


if __name__ == "__main__":
    unittest.main()
