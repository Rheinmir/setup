"""f14 snapshot & diff — parallel-run (BR C16)."""
import unittest
import tempfile
import shutil
from decimal import Decimal
from pathlib import Path
from app import snapshot


class TestSnapshot(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_moi_lan_chay_ghi_snapshot_moi_khong_de(self):
        # BR C16.1 — snapshot bất biến
        rows = [{"employee_id": "E1", "NET_PAY": Decimal(1_000_000)}]
        a = snapshot.write_run("2026-03", rows, root=self.tmp)
        b = snapshot.write_run("2026-03", rows, root=self.tmp)
        self.assertNotEqual(a, b)
        self.assertTrue(a.exists() and b.exists())

    def test_diff_hai_lan_chay_giong_nhau_thi_rong(self):
        rows = [{"employee_id": "E1", "NET_PAY": Decimal(1_000_000)}]
        a = snapshot.write_run("2026-03", rows, root=self.tmp)
        b = snapshot.write_run("2026-03", rows, root=self.tmp)
        self.assertEqual(snapshot.diff(a, b), [])

    def test_diff_chi_ra_dung_nguoi_dung_CODE_dung_so_tien(self):
        # BR C16.2 — đây là thứ duy nhất cho phép HR dám cắt Excel
        a = snapshot.write_run("2026-03", [{"employee_id": "E1", "NET_PAY": Decimal(1_000_000)}],
                               root=self.tmp)
        b = snapshot.write_run("2026-03", [{"employee_id": "E1", "NET_PAY": Decimal(1_200_000)}],
                               root=self.tmp)
        d = snapshot.diff(a, b)
        self.assertEqual(len(d), 1)
        self.assertEqual(d[0]["employee_id"], "E1")
        self.assertEqual(d[0]["code"], "NET_PAY")
        self.assertEqual(Decimal(str(d[0]["delta"])), Decimal(200_000))

    def test_diff_bat_nguoi_bi_thieu_o_mot_ben(self):
        a = snapshot.write_run("2026-03", [{"employee_id": "E1", "NET_PAY": Decimal(1)},
                                           {"employee_id": "E2", "NET_PAY": Decimal(2)}],
                               root=self.tmp)
        b = snapshot.write_run("2026-03", [{"employee_id": "E1", "NET_PAY": Decimal(1)}],
                               root=self.tmp)
        d = snapshot.diff(a, b)
        self.assertTrue(any(x["employee_id"] == "E2" for x in d))


if __name__ == "__main__":
    unittest.main()
