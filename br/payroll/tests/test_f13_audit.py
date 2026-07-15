"""f13 audit — FE-17 / BR C14.2: log giá-trị-cũ → giá-trị-mới, người, thời gian, lý do bắt buộc."""
import unittest
from pathlib import Path
from app import audit

_LOG = Path(__file__).resolve().parent.parent / "data" / "audit_log.jsonl"


class TestAudit(unittest.TestCase):
    def setUp(self):
        self._before = _LOG.read_text(encoding="utf-8") if _LOG.exists() else ""

    def tearDown(self):
        # không để test bẩn sổ audit thật — cắt lại đúng số dòng đã có trước test
        if _LOG.exists():
            _LOG.write_text(self._before, encoding="utf-8")

    def test_log_action_ghi_du_5_truong_bat_buoc(self):
        entry = audit.log_action(
            action="mass_upload_employees", period="2099-09",
            performed_by="Nguyễn Test", reason="Test đơn vị",
            old_ids=["A", "B"], new_ids=["A", "C", "D"])
        for k in ("timestamp", "action", "period", "performed_by", "reason",
                   "old_employee_ids", "new_employee_ids"):
            self.assertIn(k, entry)
        self.assertEqual(entry["performed_by"], "Nguyễn Test")
        self.assertEqual(entry["reason"], "Test đơn vị")

    def test_log_action_bat_buoc_ly_do_khong_rong(self):
        with self.assertRaises(ValueError):
            audit.log_action(action="x", period="2099-09", performed_by="A",
                              reason="", old_ids=[], new_ids=[])
        with self.assertRaises(ValueError):
            audit.log_action(action="x", period="2099-09", performed_by="",
                              reason="ly do", old_ids=[], new_ids=[])

    def test_log_action_append_only_doc_lai_dung_thu_tu(self):
        n0 = len(audit.read_log())
        audit.log_action(action="a1", period="2099-09", performed_by="X",
                          reason="r1", old_ids=[], new_ids=["1"])
        audit.log_action(action="a2", period="2099-09", performed_by="X",
                          reason="r2", old_ids=["1"], new_ids=["1", "2"])
        rows = audit.read_log()
        self.assertEqual(len(rows), n0 + 2)
        self.assertEqual(rows[-2]["action"], "a1")
        self.assertEqual(rows[-1]["action"], "a2")


if __name__ == "__main__":
    unittest.main()
