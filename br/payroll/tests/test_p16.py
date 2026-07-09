"""Test đỏ frame p16 — PC xăng: CT chuẩn 1tr, VP chỉ qua tờ trình (C5.3.3).
Tổng quát: đoạn từ p10 thật, tờ trình từ p04 thật, không tra bảng theo NV."""
import unittest
from app.p16_pcxang import tinh_pc_xang


class TestPCXang(unittest.TestCase):
    def test_ct_muc_chuan_khong_to_trinh(self):
        r = tinh_pc_xang("NV003")  # CT Bình Dương, không có tờ trình xăng
        self.assertIn("QĐ chung", str(r["trace"]))
        self.assertGreater(r["tong"], 0)

    def test_vp_khong_tt_bang_0(self):
        r = tinh_pc_xang("NV002")
        self.assertEqual(r["tong"], 0)

    def test_tai_xe_hn_tu_to_trinh(self):
        r = tinh_pc_xang("NV006")
        self.assertIn("TT-2026/031", str(r["trace"]))
        self.assertGreater(r["tong"], 0)

    def test_gddar_tu_to_trinh(self):
        r = tinh_pc_xang("NV007")
        self.assertGreater(r["tong"], 9_000_000)  # pro-rata gần 10tr, không đủ 26 ngày tròn
        self.assertIn("TT-2026/018", str(r["trace"]))

    def test_nv008_tong_quat_ct_khong_to_trinh(self):
        # NV008 chưa từng xuất hiện trong test p16 cũ.
        r = tinh_pc_xang("NV008")
        self.assertIn("QĐ chung", str(r["trace"]))
        self.assertGreater(r["tong"], 0)


if __name__ == "__main__":
    unittest.main()
