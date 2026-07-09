"""Test đỏ frame p12 — tổng hợp suất ăn (C5.1.5). Tổng quát: tính THẬT từ công
thô (p06) + dm_bo_phan/dm_khoang_cach/suat_an_bo_sung CSV, không tra bảng theo ID."""
import unittest
from app.p12_suatan import tong_hop_suat_an, SUAT_VP, SUAT_CT_GAN, SUAT_CT_XA


class TestCongThucViDu1PRD(unittest.TestCase):
    def test_vi_du_1_prd_cong_thuc_65_suat(self):
        # Ví dụ 1 PRD: 5 ngày VP ×1 + 20 ngày dự án ≥30km ×3 = 65 — kiểm công thức
        # (hằng số bữa) tách biệt khỏi CSV, vì không NV mẫu nào có đúng 5+20 ngày.
        self.assertEqual(5 * SUAT_VP + 20 * SUAT_CT_XA, 65)


class TestSuatAnTuCSVThat(unittest.TestCase):
    def test_ngay_duoi_4h_khong_tinh_suat(self):
        r = tong_hop_suat_an("NV004")
        # NV004 có 3 dòng công thô: 2 ngày 8h (CT Long An, dải 30-100 → xa → 3 suất/ngày)
        # + 1 ngày 3.5h (08/07, bị loại). Tổng = 2 × 3 = 6, KHÔNG cộng ngày ≤4h.
        self.assertEqual(r["CT Long An"]["tong"], 6)

    def test_com_chu_nhat_thu_ky_gui(self):
        r = tong_hop_suat_an("NV008")
        self.assertGreaterEqual(r.get("CT Quan Lạn", {}).get("suat_cn_le", 0), 6)

    def test_dieu_dong_tach_rieng_bo_phan(self):
        r = tong_hop_suat_an("NV001")
        self.assertEqual(len(r), 2)
        self.assertEqual(r["VP HCM"]["tong"], 10)  # 10 ngày VP × 1 suất

    def test_nv003_tong_quat_cho_nv_chua_test_truoc_do(self):
        # NV003 chưa từng xuất hiện trong test p12 cũ.
        r = tong_hop_suat_an("NV003")
        self.assertIn("CT Bình Dương", r)
        self.assertGreater(r["CT Bình Dương"]["tong"], 0)
        self.assertGreaterEqual(r["CT Bình Dương"]["suat_cn_le"], 2)


if __name__ == "__main__":
    unittest.main()
