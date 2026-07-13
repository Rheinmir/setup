"""f99 LẮP RÁP — engine chạy ground-truth thật, đối chiếu từng đồng (BR C17)."""
import json
import time
import unittest
from decimal import Decimal
from pathlib import Path
from app import pipeline

FIX = Path(__file__).parent / "fixtures" / "gt1_row9.json"


class TestLapRap(unittest.TestCase):
    def setUp(self):
        self.gt = json.loads(FIX.read_text(encoding="utf-8"))

    def test_GT1_khop_tung_dong_toan_bo_25_cot(self):
        # BR C17.1 — đây là điều kiện sống còn của cả dự án
        lech = pipeline.doi_chieu(self.gt)
        self.assertEqual(lech, [], "\n".join(
            f"{d['code']}: engine={d['got']} ≠ excel={d['expected']} (lệch {d['delta']})"
            for d in lech))

    def test_GT1_dich_cuoi_NET_PAY(self):
        kq = pipeline.tinh(self.gt["inputs"], period=self.gt["period"])
        self.assertEqual(kq["NET_PAY_HOME"], Decimal(189_930_161))

    def test_GT1b_o_tu_kiem_can_so_cua_chinh_excel(self):
        # BR C17.2 — EF9: SUM(thu nhập) - BH - thuế + cộng sau thuế - trừ sau thuế - NET_PAY == 0
        kq = pipeline.tinh(self.gt["inputs"], period=self.gt["period"])
        can = (kq["GROSS"] - kq["TOTAL_INS"] - kq["TOTAL_PIT"]
               + kq["TOTAL_POST_ADD"] - kq["TOTAL_POST_DED"] - kq["NET_PAY"])
        self.assertEqual(can, Decimal(0), "sổ không cân — engine mất/thừa tiền ở đâu đó")

    def test_GT1b_hai_cach_tinh_thue_cho_cung_ket_qua(self):
        # BR C17.2 — EX9: thang IF ≡ SUMPRODUCT
        kq = pipeline.tinh(self.gt["inputs"], period=self.gt["period"])
        self.assertEqual(kq["PIT"], pipeline.pit_sumproduct(kq["TAXABLE_INC"]))

    def test_GT2_doi_param_set_thi_so_doi_theo(self):
        # BR C17.3 — chứng minh effective_from là thật
        kq_cu = pipeline.tinh(self.gt["inputs"], period="2024-06")
        self.assertEqual(kq_cu["TOTAL_DED"], Decimal(24_200_000))
        self.assertEqual(kq_cu["TAXABLE_INC"], Decimal(195_292_000))
        self.assertEqual(kq_cu["PIT"], Decimal(53_852_200))
        # cùng engine, param khác → NET khác
        kq_moi = pipeline.tinh(self.gt["inputs"], period="2026-03")
        self.assertNotEqual(kq_cu["NET_PAY"], kq_moi["NET_PAY"])

    def test_PERF_4179_nhan_su_duoi_5_phut(self):
        # BR C17.6 — NFR: hàng ngàn người < 5 phút
        t0 = time.time()
        rows = pipeline.chay_roster([dict(self.gt["inputs"]) for _ in range(4179)],
                                    period=self.gt["period"])
        elapsed = time.time() - t0
        self.assertEqual(len(rows), 4179)
        self.assertLess(elapsed, 300, f"chạy 4.179 nhân sự mất {elapsed:.1f}s (> 5 phút)")


if __name__ == "__main__":
    unittest.main()
