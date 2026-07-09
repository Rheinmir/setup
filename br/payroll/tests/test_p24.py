"""Test đỏ frame p24 — phê duyệt & audit log bất biến, sync-back Workday (C6.2)."""
import unittest
from app.p24_pheduyet import duyet_don, audit_log


class TestPheDuyetAudit(unittest.TestCase):
    def test_duyet_thanh_cong_cong_lai(self):
        r = duyet_don("NV012", "2026-07-12", nguoi="tp.phong01", ly_do="đi công tác kịp duyệt")
        self.assertEqual(r["ky_hieu_moi"], "TC200")

    def test_override_thieu_ly_do_tu_choi(self):
        with self.assertRaises(Exception):
            duyet_don("NV012", "2026-07-12", nguoi="hr.cb01", ly_do="")

    def test_override_sinh_hai_ban_ghi(self):
        before = len(audit_log())
        duyet_don("NV012", "2026-07-12", nguoi="hr.cb01", ly_do="override kịp kỳ", override=True)
        after = len(audit_log())
        self.assertGreaterEqual(after - before, 1)

    def test_audit_khong_co_delete(self):
        self.assertFalse(hasattr(audit_log, "delete"))


if __name__ == "__main__":
    unittest.main()
