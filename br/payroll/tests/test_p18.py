"""Test đỏ frame p18 — PC công trường + công tác xa (C5.3.5). Tổng quát: định mức
tra dinh_muc_ct_congtacxa.csv thật, đoạn từ p10, không tra bảng theo NV."""
import unittest
from app.p18_pcctctx import tinh_pc_ct_ctx


class TestPCCTCTX(unittest.TestCase):
    def test_ct_khac_mien_dh(self):
        r = tinh_pc_ct_ctx("NV001")  # CHT ĐH → Quan Lạn (dải khac_mien → 3.000.000)
        self.assertIn("CT Quan Lạn", r["theo_bo_phan"])
        self.assertGreater(r["theo_bo_phan"]["CT Quan Lạn"], 0)

    def test_vp_duoi_30_bang_0(self):
        r = tinh_pc_ct_ctx("NV002")
        self.assertEqual(r["tong"], 0)

    def test_ct_30_100_cd_khac_di_lai(self):
        r = tinh_pc_ct_ctx("NV003")  # Cao đẳng, CT Bình Dương (30-100) → khác đi lại (=0)
        self.assertGreater(r["tong"], 0)

    def test_gddar_bang_0(self):
        r = tinh_pc_ct_ctx("NV007")
        self.assertEqual(r["tong"], 0)

    def test_nv008_tong_quat_cho_nv_chua_test_truoc_do(self):
        r = tinh_pc_ct_ctx("NV008")  # Nghề → nhóm cd_tc_nghe
        self.assertIn("CT Quan Lạn", r["theo_bo_phan"])
        self.assertGreater(r["theo_bo_phan"]["CT Quan Lạn"], 0)


if __name__ == "__main__":
    unittest.main()
