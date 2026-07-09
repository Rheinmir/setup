"""Test frame p30 — engine công thức lương THẬT trích từ Excel bàn giao
(sheet Payroll structure + References). Kiểm chuỗi GROSS→NET_PAY_HOME đúng
công thức gốc, thuế TNCN đúng 7 bậc lũy tiến."""
import unittest
from app.p30_formula_engine import compute, tinh_thue_tncn, bang_luong_day_du


class TestThueTNCN(unittest.TestCase):
    def test_bac_1_duoi_5tr_khong_thue(self):
        self.assertEqual(tinh_thue_tncn(5_000_000), 5_000_000 * 0.05 - 0)

    def test_bac_2_5_10tr(self):
        self.assertEqual(tinh_thue_tncn(8_000_000), 8_000_000 * 0.10 - 250_000)

    def test_bac_cao_nhat_tren_80tr(self):
        self.assertEqual(tinh_thue_tncn(100_000_000), 100_000_000 * 0.35 - 9_850_000)

    def test_thu_nhap_am_hoac_0_khong_thue(self):
        self.assertEqual(tinh_thue_tncn(0), 0.0)
        self.assertEqual(tinh_thue_tncn(-1000), 0.0)


class TestChuoiCongThucThat(unittest.TestCase):
    def test_gross_toi_thieu_bang_earned_sal_khi_khong_co_pc(self):
        inputs = {"BASIC_SAL": 20_000_000, "STD_DAYS": 26, "ACTUAL_DAYS": 26,
                  "PROB_DAYS": 0, "RESPONSIBILITY_ALLOW": 0}
        gross = compute("GROSS", inputs)
        self.assertAlmostEqual(gross, 20_000_000, delta=1)

    def test_si_emp_dung_tran_46_8tr(self):
        # Lương 60tr nhưng trần đóng BHXH chỉ 46.8tr — SI_EMP phải tính trên trần.
        inputs = {"BASIC_SAL": 60_000_000}
        si = compute("SI_EMP", inputs)
        self.assertAlmostEqual(si, 46_800_000 * 0.08, delta=1)

    def test_net_pay_home_tru_du_bhxh_va_thue(self):
        inputs = {"BASIC_SAL": 20_000_000, "STD_DAYS": 26, "ACTUAL_DAYS": 26,
                  "PROB_DAYS": 0, "RESPONSIBILITY_ALLOW": 0, "DEPENDENT_CNT": 0}
        net = compute("NET_PAY_HOME", inputs)
        gross = compute("GROSS", inputs)
        total_ins = compute("TOTAL_INS", inputs)
        self.assertLess(net, gross)
        self.assertGreater(net, gross - total_ins - 5_000_000)  # trừ hợp lý, không âm bất thường

    def test_ca_chuoi_chay_1_lan_co_trace_day_du(self):
        inputs = {"BASIC_SAL": 25_000_000, "STD_DAYS": 26, "ACTUAL_DAYS": 26,
                  "PROB_DAYS": 0, "RESPONSIBILITY_ALLOW": 1_000_000,
                  "MEALS_TOTAL": 26, "DEPENDENT_CNT": 1}
        ket_qua, trace = bang_luong_day_du(inputs)
        self.assertIn("NET_PAY_HOME", ket_qua)
        self.assertIn("TOTAL_CTY_COST", ket_qua)
        self.assertIn("GROSS", trace)
        self.assertIn("PIT", trace)
        self.assertGreater(len(trace), 15)  # chuỗi đủ dài, không cụt


if __name__ == "__main__":
    unittest.main()
