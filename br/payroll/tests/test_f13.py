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

    def test_save_uploaded_employees_ghi_dung_cho_fetch_doc_lai_duoc(self):
        # BR C18.2 — hàm thứ năm: adapt module có sẵn, không mở đường I/O song song
        rows = [{"employee_id": "UP-001", "ho_ten": "Test Nhân Viên"}]
        path = adapters.save_uploaded_employees("2099-01", rows)
        self.assertTrue(path.exists())
        self.assertEqual(adapters.fetch_employees("2099-01"), rows)

    def test_save_uploaded_employees_khong_dung_ky_khac(self):
        # ghi kỳ demo không được đụng ground-truth 2026-03
        before = adapters.fetch_employees("2026-03")
        adapters.save_uploaded_employees("2099-02", [{"employee_id": "UP-002"}])
        self.assertEqual(adapters.fetch_employees("2026-03"), before)

    # ── FE-20 Payroll Master (Template 2) ────────────────────────────────────
    def test_export_payroll_master_dung_ground_truth(self):
        import csv
        from app import params
        p = params.load("2026-03")
        path = adapters.export_payroll_master("2026-03", p)
        self.assertTrue(path.exists())
        with path.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual(r["employee_id"], "GT-ROW9")
        self.assertEqual(int(r["NET_PAY_HOME"]), 189_930_161)
        self.assertEqual(int(r["GROSS"]), 225_010_000)
        # trường kế toán KHÔNG có dữ liệu trong hệ thống — cột rỗng, không bịa
        for c in ("profit_cost_center", "wbs", "funds_center"):
            self.assertIn(c, r)
            self.assertEqual(r[c], "")


if __name__ == "__main__":
    unittest.main()
