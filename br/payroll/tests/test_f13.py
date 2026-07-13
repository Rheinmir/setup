"""f13 adapters — ranh giới I/O 4 hàm (BR C18.1)."""
import unittest
import inspect
from app import adapters


class TestAdapters(unittest.TestCase):
    def test_dung_4_ham_ranh_gioi(self):
        for name in ("fetch_employees", "fetch_timesheet", "push_payslip", "export_bank_file"):
            self.assertTrue(callable(getattr(adapters, name, None)), f"thiếu {name}")

    def test_fetch_employees_doc_tu_file_json(self):
        rows = adapters.fetch_employees("2026-03")
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0)
        self.assertIn("employee_id", rows[0])

    def test_khong_goi_mang(self):
        # BR C18.1 / A7 — lô đầu zero network. Chặn cứng: mã nguồn không được import socket/urllib/requests
        src = inspect.getsource(adapters)
        for banned in ("import requests", "import socket", "urllib.request", "http.client"):
            self.assertNotIn(banned, src, f"adapters không được gọi mạng ở lô đầu: {banned}")

    def test_moi_ham_ghi_ro_se_noi_vao_dau_o_lo_sau(self):
        # điều kiện của build-now-adapt-later: chỗ nối phải được đánh dấu, không mất dấu
        src = inspect.getsource(adapters)
        self.assertIn("Workday", src)


if __name__ == "__main__":
    unittest.main()
