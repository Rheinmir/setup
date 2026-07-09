"""Test đỏ frame p12 — tổng hợp suất ăn, phải tái lập đúng Ví dụ 1 PRD = 65 suất (C5.1.5)."""
import unittest
from app.p12_suatan import tong_hop_suat_an


class TestSuatAn(unittest.TestCase):
    def test_vi_du_1_prd_65_suat(self):
        # 5 ngày VP ×1 + 20 ngày dự án ≥30km ×3 = 65
        r = tong_hop_suat_an("NV_vidu1")
        tong = sum(bp["tong"] for bp in r.values())
        self.assertEqual(tong, 65)

    def test_ngay_duoi_4h_khong_tinh_suat(self):
        r = tong_hop_suat_an("NV004")
        # ngày 08/07 chỉ 3.5h → không cộng suất ngày đó
        tong = sum(bp["tong"] for bp in r.values())
        self.assertLess(tong, 18 * 2)  # không đạt tối đa nếu tính đủ 2 bữa/ngày

    def test_com_chu_nhat_thu_ky_gui(self):
        r = tong_hop_suat_an("NV008")
        self.assertGreaterEqual(r.get("CT Quan Lạn", {}).get("suat_cn_le", 0), 6)

    def test_dieu_dong_tach_rieng_bo_phan(self):
        r = tong_hop_suat_an("NV001")
        self.assertEqual(len(r), 2)


if __name__ == "__main__":
    unittest.main()
