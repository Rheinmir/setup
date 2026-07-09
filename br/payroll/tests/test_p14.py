"""Test đỏ frame p14 — PC cơm = suất × đơn giá, tách Taxable/Non-tax (C5.3.1)."""
import unittest
from app.p14_pccom import tinh_pc_com


class TestPCCom(unittest.TestCase):
    def test_65_suat(self):
        r = tinh_pc_com(65)
        self.assertEqual(r["thanh_tien"], 2_925_000)
        self.assertEqual(r["non_tax"], 730_000)
        self.assertEqual(r["taxable"], 2_195_000)

    def test_16_suat_duoi_tran(self):
        r = tinh_pc_com(16)
        self.assertEqual(r["thanh_tien"], 720_000)
        self.assertEqual(r["non_tax"], 720_000)
        self.assertEqual(r["taxable"], 0)

    def test_doi_don_gia_config(self):
        r = tinh_pc_com(10, don_gia=50_000)
        self.assertEqual(r["thanh_tien"], 500_000)


if __name__ == "__main__":
    unittest.main()
