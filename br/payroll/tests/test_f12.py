"""f12 engine — registry CODE + compute đệ quy + trace (BR C3.1, C14.1)."""
import unittest
from decimal import Decimal
from app import engine, params


def _rec():
    return {
        "CONTRACT_TYPE": "Chính thức", "NATIONALITY": "Việt Nam",
        "STD_DAYS": Decimal(22), "OFFICIAL_DAYS": Decimal("19.5"), "PROB_DAYS": Decimal(0),
        "PAID_LEAVE_DAYS": Decimal(0), "HOLIDAY_DAYS": Decimal("2.5"), "COMP_DAYS": Decimal(0),
        "PAID_OTHER_DAYS": Decimal(0), "BEREAVE_DAYS": Decimal(0), "UNPAID_DAYS": Decimal(0),
        "SI_DAYS": Decimal(0), "ADJ_DAYS": Decimal(0),
        "BASIC_SAL": Decimal(200_000_000), "PROB_SAL": Decimal(0), "RESP_SAL": Decimal(0),
        "FUEL_ALLOW": Decimal(25_000_000), "MEAL_NONTAX": Decimal(-990_000),
        "PHONE_NONTAX": Decimal(1_000_000), "DEPENDENT_CNT": 3,
        "PIT_SETTLE": Decimal(21_049_361), "TERMINATION_DATE": None,
    }


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.p = params.load("2026-03")

    def test_goi_1_lan_cho_field_cuoi_tu_keo_ca_chuoi(self):
        # BR C3.1 — compute(NET_PAY) tự resolve đệ quy toàn bộ phụ thuộc
        net = engine.compute("NET_PAY_HOME", _rec(), self.p)
        self.assertEqual(net, Decimal(189_930_161))

    def test_field_thieu_trong_input_coi_nhu_0(self):
        # đúng hành vi ô Excel trống
        rec = _rec()
        rec.pop("FUEL_ALLOW")
        self.assertEqual(engine.compute("FUEL_ALLOW", rec, self.p), Decimal(0))

    def test_bang_luong_tra_ket_qua_va_trace(self):
        ket_qua, trace = engine.bang_luong(_rec(), self.p)
        self.assertEqual(ket_qua["NET_PAY"], Decimal(189_930_161))
        self.assertEqual(ket_qua["TOTAL_CTY_COST"], Decimal(201_522_161))
        self.assertGreater(len(trace), 20)
        self.assertIn("GROSS", trace)
        self.assertIn("PIT", trace)

    def test_trace_moi_field_co_cong_thuc_gia_tri_va_clause_BR(self):
        # BR C14.1 — truy vết về công thức + tham số + clause_id
        _, trace = engine.bang_luong(_rec(), self.p)
        t = trace["SI_EMP"]
        self.assertIn("formula", t)
        self.assertIn("value", t)
        self.assertIn("clause", t)
        self.assertIn("deps", t)
        self.assertTrue(t["clause"].startswith("C"))
        self.assertEqual(t["value"], Decimal(3_744_000))

    def test_trace_di_nguoc_duoc_tu_NET_PAY_xuong_BASIC_SAL(self):
        _, trace = engine.bang_luong(_rec(), self.p)
        seen, stack = set(), ["NET_PAY"]
        while stack:
            code = stack.pop()
            if code in seen or code not in trace:
                continue
            seen.add(code)
            stack.extend(trace[code].get("deps", []))
        self.assertIn("BASIC_SAL", seen)
        self.assertIn("TAXABLE_INC", seen)

    def test_khong_co_chu_trinh_trong_DAG(self):
        engine.kiem_tra_dag()   # raise nếu có vòng lặp phụ thuộc

    def test_registry_phu_het_field_ket_qua_cua_ground_truth(self):
        for code in ("PAID_DAYS", "CONTRACT_TOTAL", "INS_SAL_BH", "EARNED_SAL", "GROSS",
                     "TAXABLE_GROSS", "TOTAL_INS", "TOTAL_DED", "TAXABLE_INC", "PIT",
                     "NET_INCOME", "NET_PAY", "NET_PAY_HOME", "TOTAL_INS_CTY", "KPCD_CTY",
                     "TOTAL_CTY_COST", "BUDGET_SAVE"):
            self.assertIn(code, engine.CODES, f"thiếu CODE {code}")


if __name__ == "__main__":
    unittest.main()
