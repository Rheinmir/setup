"""f06 phụ cấp — pro-rata, luật <14 ngày, điều động (BR C8.3–C8.7) + AC-2."""
import unittest
from decimal import Decimal
from app import phucap, params


class TestPhuCap(unittest.TestCase):
    def setUp(self):
        self.p = params.load("2026-03")

    def test_prorata_thuong(self):
        # BR C8.3: định mức / công chuẩn * ngày hưởng
        self.assertEqual(phucap.prorata(Decimal(1_000_000), Decimal(11), Decimal(22)),
                         Decimal(500_000))

    def test_du_14_ngay_thi_dung_ngay_huong_luong_binh_thuong(self):
        # 14 ngày làm việc thực tế → KHÔNG áp luật <14; ngày hưởng gồm cả phép
        seg = {"ngay_lam_viec": 14, "ngay_le": 2, "ngay_phep": 4, "ngay_khong_luong": 0}
        self.assertEqual(phucap.ngay_huong(seg, self.p), Decimal(20))

    def test_duoi_14_ngay_chi_tinh_lam_viec_cong_le(self):
        # BR C8.4: < 14 ngày làm việc thực tế → chỉ (làm việc + lễ), BỎ phép/không lương
        seg = {"ngay_lam_viec": 3, "ngay_le": 1, "ngay_phep": 6, "ngay_khong_luong": 0}
        self.assertEqual(phucap.ngay_huong(seg, self.p), Decimal(4))

    def test_AC2_phu_cap_di_lai_khi_dieu_dong_va_duoi_14_ngay(self):
        # BR C17.4 / AC-2 (biên bản họp 23/03/2026):
        # BP A: 3 làm việc + 1 lễ + 6 phép ; BP B: 3 làm việc + 7 phép + 2 việc riêng + 1 không lương + 2 lễ
        # Tổng làm việc thực tế = 6 < 14 → PC = (3+1)/CC * ĐM_A + (3+2)/CC * ĐM_B
        cc = Decimal(22)
        segs = [
            {"ngay_lam_viec": 3, "ngay_le": 1, "ngay_phep": 6, "ngay_khong_luong": 0,
             "dinh_muc": Decimal(1_100_000)},
            {"ngay_lam_viec": 3, "ngay_le": 2, "ngay_phep": 7, "ngay_khong_luong": 1,
             "dinh_muc": Decimal(550_000)},
        ]
        expect = (Decimal(4) / cc * Decimal(1_100_000)) + (Decimal(5) / cc * Decimal(550_000))
        got = phucap.phu_cap_dieu_dong(segs, cc, self.p)
        self.assertEqual(got, phucap.lam_tron(expect))

    def test_luat_14_ngay_xet_tren_TONG_ngay_lam_viec_ca_ky(self):
        # Cạm bẫy: 3 + 3 = 6 < 14 → cả HAI bộ phận đều áp luật <14, không xét riêng từng bộ phận.
        segs = [
            {"ngay_lam_viec": 3, "ngay_le": 0, "ngay_phep": 10, "ngay_khong_luong": 0,
             "dinh_muc": Decimal(2_200_000)},
            {"ngay_lam_viec": 3, "ngay_le": 0, "ngay_phep": 0, "ngay_khong_luong": 0,
             "dinh_muc": Decimal(2_200_000)},
        ]
        cc = Decimal(22)
        # nếu áp đúng: (3/22 + 3/22) * 2.2tr = 600.000 ; nếu SAI (tính cả phép ở seg 1): 1.3tr
        self.assertEqual(phucap.phu_cap_dieu_dong(segs, cc, self.p), Decimal(600_000))

    def test_to_trinh_ghi_de_dinh_muc_chung(self):
        # BR C8.6: tờ trình override định mức chung, VẪN chịu pro-rata
        dm = phucap.dinh_muc("dien_thoai", level="NV.03", khoi="VP",
                             to_trinh={"dinh_muc": Decimal(800_000)})
        self.assertEqual(dm, Decimal(800_000))

    def test_khoi_van_phong_khong_ap_dinh_muc_chung_phu_cap_xang(self):
        # BR C8.6: VP không có định mức chung PC xăng — chỉ theo tờ trình
        self.assertEqual(phucap.dinh_muc("xang", level="NV.03", khoi="VP"), Decimal(0))
        self.assertEqual(phucap.dinh_muc("xang", level="NV.03", khoi="CT"), Decimal(1_000_000))

    # ── C8.8 / FE-06 — Phụ cấp truy thu/truy lĩnh (hồi tố) ──────────────────
    def test_truy_thu_khong_co_ca_thi_bang_0(self):
        self.assertEqual(phucap.truy_thu({}, self.p), Decimal(0))

    def test_truy_thu_dung_cong_thuc_dinh_muc_moi_tru_cu_pro_rata(self):
        # PRD-2.1 §4.3: (định mức mới − định mức cũ) / công chuẩn × số ngày tương ứng
        e = {"RETRO_OLD_RATE": Decimal(500_000), "RETRO_NEW_RATE": Decimal(1_000_000),
             "RETRO_DAYS": Decimal(11), "STD_DAYS": Decimal(22),
             "RETRO_REASON": "Cập nhật trình độ học vấn theo Tờ trình"}
        self.assertEqual(phucap.truy_thu(e, self.p), Decimal(250_000))

    def test_truy_thu_am_khi_dieu_chinh_giam(self):
        e = {"RETRO_OLD_RATE": Decimal(1_000_000), "RETRO_NEW_RATE": Decimal(500_000),
             "RETRO_DAYS": Decimal(22), "STD_DAYS": Decimal(22),
             "RETRO_REASON": "Điều chỉnh giảm chức danh"}
        self.assertEqual(phucap.truy_thu(e, self.p), Decimal(-500_000))

    def test_truy_thu_bat_buoc_ly_do_khong_am_tham_bo_qua(self):
        e = {"RETRO_OLD_RATE": Decimal(500_000), "RETRO_NEW_RATE": Decimal(1_000_000),
             "RETRO_DAYS": Decimal(11), "STD_DAYS": Decimal(22)}
        with self.assertRaises(ValueError):
            phucap.truy_thu(e, self.p)

    def test_truy_thu_bat_buoc_so_ngay_tuong_ung(self):
        e = {"RETRO_OLD_RATE": Decimal(500_000), "RETRO_NEW_RATE": Decimal(1_000_000),
             "STD_DAYS": Decimal(22), "RETRO_REASON": "thiếu RETRO_DAYS"}
        with self.assertRaises(ValueError):
            phucap.truy_thu(e, self.p)


if __name__ == "__main__":
    unittest.main()
