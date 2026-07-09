"""Test đỏ frame p27 — báo cáo HR C&B bảo mật + đơn treo lãnh đạo, ghi log xuất (C6.4, C6.5)."""
import unittest
from app.p27_baocao_hr import bang_tong_hop_pc, xuat_bao_cao, don_treo


class TestBaoCaoHR(unittest.TestCase):
    def test_bang_pc_du_cot_1_8(self):
        b = bang_tong_hop_pc("2026-07")
        row = b[0]
        for col in ("pc1", "pc2", "pc3", "pc4", "pc5", "pc6", "pc7", "pc8"):
            self.assertIn(col, row)

    def test_xuat_khong_user_tu_choi(self):
        with self.assertRaises(Exception):
            xuat_bao_cao("bang_cong", user=None)

    def test_xuat_hop_le_ghi_log(self):
        r = xuat_bao_cao("bang_cong", user="hr.cb02")
        self.assertIn("log_id", r)

    def test_don_treo_nv012(self):
        treo = don_treo("2026-07")
        msnv_list = [d["msnv"] for d in treo]
        self.assertIn("NV012", msnv_list)


if __name__ == "__main__":
    unittest.main()
