"""engine.py — Registry CODE + compute đệ quy + trace (BR C3, C14.1).

Mỗi mã field là một nút: (phụ thuộc, công thức nguyên văn, clause BR, hàm tính).
Hàm tính GỌI LẠI module domain đã có, không chép công thức sang đây [C3.3].
"""
from decimal import Decimal

from app import baohiem, chamcong, phucap, thue, thuong, tonghop
from app.luong import _dec, earned_sal, round0

# Clause gán cho field input (ô Excel gốc, không có công thức) [C14.1].
CLAUSE_INPUT = "C3.1"


class Node:
    def __init__(self, deps, formula, clause, fn):
        self.deps = tuple(deps)
        self.formula = formula
        self.clause = clause
        self.fn = fn


CODES: dict = {}


def _n(code, deps, formula, clause, fn):
    CODES[code] = Node(deps, formula, clause, fn)


_DAY_DEPS = ("OFFICIAL_DAYS", "PROB_DAYS", "PAID_LEAVE_DAYS", "HOLIDAY_DAYS",
             "COMP_DAYS", "PAID_OTHER_DAYS", "BEREAVE_DAYS")

_n("PAID_DAYS", _DAY_DEPS,
   "IF(chính thức, OFFICIAL_DAYS, PROB_DAYS) + PAID_LEAVE + HOLIDAY + COMP + PAID_OTHER + BEREAVE",
   "C6.3", lambda e, p: chamcong.paid_days(e))

_n("CONTRACT_TOTAL", ("BASIC_SAL", "RESP_SAL", "PROB_SAL"),
   "IF(chính thức, BASIC_SAL + RESP_SAL, PROB_SAL)",
   "C3.3", lambda e, p: round0(
       _dec(e.get("BASIC_SAL", 0)) + _dec(e.get("RESP_SAL", 0))
       if e["CONTRACT_TYPE"] == "Chính thức" else _dec(e.get("PROB_SAL", 0))))

_n("INS_SAL_BH", ("CONTRACT_TOTAL",),
   "IF(chính thức, MIN(CONTRACT_TOTAL, ins_cap_bh_display), 0) — cột hiển thị",
   "C4.2", baohiem.ins_sal_bh)
_n("INS_BASE_BH", ("CONTRACT_TOTAL",),
   "IF(chính thức, MIN(CONTRACT_TOTAL, ins_cap_bh), 0) — base tính thật",
   "C4.2", baohiem.ins_base_bh)
_n("INS_SAL_UI", ("CONTRACT_TOTAL",),
   "IF(chính thức, MIN(CONTRACT_TOTAL, ins_cap_ui), 0)",
   "C11.1", baohiem.ins_sal_ui)

_n("EARNED_SAL", ("BASIC_SAL", "PROB_SAL", "RESP_SAL", "STD_DAYS", "PAID_DAYS",
                  "EARNED_PAID_LEAVE"),
   "PROB_EARNED + OFFICIAL_EARNED + RESP_EARNED + EARNED_PAID_LEAVE (pro-rata PAID_DAYS/STD_DAYS)",
   "C7.3", earned_sal)

_n("BONUS_TOTAL", thuong.BONUS_KEYS,
   "SUM(13 khoản thưởng input)", "C10.1", lambda e, p: thuong.bonus_total(e))

_n("PC_TRUY_THU", ("RETRO_OLD_RATE", "RETRO_NEW_RATE", "RETRO_DAYS", "STD_DAYS"),
   "(định mức mới − định mức cũ) / công chuẩn × số ngày tương ứng — 0 nếu không có ca truy thu",
   "C8.8", phucap.truy_thu)

_n("GROSS", tonghop._GROSS_CODES,
   "EARNED_SAL + phụ cấp + OT + BONUS_TOTAL + TOTAL_SUPPORT + ADJ_PLUS + ADJ_MINUS (⚠ ADJ_MINUS được CỘNG)",
   "C13.1", tonghop.gross)
_n("TAXABLE_GROSS", ("GROSS",) + tonghop._NONTAX_CODES,
   "GROSS − mọi khoản non-tax − SEVER_ALLOW − SI_BENEFIT − BONUS_TRAVEL − CHARITY_DED − EARNED_PAID_LEAVE",
   "C13.2", lambda e, p: tonghop.taxable_gross(e, e["GROSS"], p))

_n("SI_EMP", ("INS_BASE_BH",), "INS_BASE_BH × si_emp (8%)", "C11.2", baohiem.si_emp)
_n("HI_EMP", ("INS_BASE_BH",), "INS_BASE_BH × hi_emp (1,5%)", "C11.2", baohiem.hi_emp)
_n("UI_EMP", ("INS_SAL_UI",), "INS_SAL_UI × ui_emp (1%) — nước ngoài không đóng", "C11.4", baohiem.ui_emp)
_n("TOTAL_INS", ("SI_EMP", "HI_EMP", "UI_EMP"),
   "SI_EMP + HI_EMP + UI_EMP", "C11.2",
   lambda e, p: e["SI_EMP"] + e["HI_EMP"] + e["UI_EMP"])

_n("SI_CTY", ("INS_BASE_BH",), "INS_BASE_BH × si_cty (17%)", "C4.5", baohiem.si_cty)
_n("TNLD_CTY", ("INS_BASE_BH",),
   "INS_BASE_BH × tnld_cty (0,5%) — trần BH, không phải trần BHTN", "C3.3", baohiem.tnld_cty)
_n("HI_CTY", ("INS_BASE_BH",), "INS_BASE_BH × hi_cty (3%)", "C4.5", baohiem.hi_cty)
_n("UI_CTY", ("INS_SAL_UI",), "INS_SAL_UI × ui_cty (1%)", "C4.5", baohiem.ui_cty)
_n("TOTAL_INS_CTY", ("SI_CTY", "TNLD_CTY", "HI_CTY", "UI_CTY"),
   "SI_CTY + TNLD_CTY + HI_CTY + UI_CTY (không gồm KPCĐ)", "C4.5",
   lambda e, p: e["SI_CTY"] + e["TNLD_CTY"] + e["HI_CTY"] + e["UI_CTY"])
_n("KPCD_CTY", ("INS_BASE_BH",), "INS_BASE_BH × kpcd_cty (2%)", "C3.3", baohiem.kpcd_cty)
_n("UNION_FEE", ("INS_BASE_BH",), "MIN(INS_BASE_BH × 0,5%, 253.000)", "C3.3", baohiem.union_fee)

_n("TOTAL_DED", ("DEPENDENT_CNT",),
   "personal_ded + dependent_ded × DEPENDENT_CNT (thử việc → 0)", "C4.4", thue.total_ded)
_n("TAXABLE_INC", ("TAXABLE_GROSS", "TOTAL_INS", "TOTAL_DED"),
   "MAX(0, TAXABLE_GROSS − TOTAL_INS − TOTAL_DED)", "C12.1",
   lambda e, p: thue.taxable_inc(e["TAXABLE_GROSS"], e["TOTAL_INS"], e["TOTAL_DED"]))
_n("PIT", ("TAXABLE_INC",), "Biểu lũy tiến 5 bậc (thử việc: khoán suất)", "C12.2",
   lambda e, p: thue.pit(e["TAXABLE_INC"], e, p))

_n("TOTAL_POST_DED", ("UNION_FEE", "OTHER_POST_DED"),
   "UNION_FEE + OTHER_POST_DED", "C13.3",
   lambda e, p: round0(e["UNION_FEE"] + _dec(e.get("OTHER_POST_DED", 0))))
_n("TOTAL_POST_ADD", ("PIT_SETTLE", "OTHER_POST_ADD"),
   "PIT_SETTLE + OTHER_POST_ADD", "C13.3",
   lambda e, p: round0(_dec(e.get("PIT_SETTLE", 0)) + _dec(e.get("OTHER_POST_ADD", 0))))

_n("NET_INCOME", ("GROSS", "TOTAL_INS", "PIT"),
   "GROSS − TOTAL_INS − PIT", "C17.1",
   lambda e, p: tonghop.net_income(e["GROSS"], e["TOTAL_INS"], e["PIT"]))
_n("NET_PAY", ("GROSS", "TOTAL_INS", "PIT", "TOTAL_POST_DED", "TOTAL_POST_ADD"),
   "GROSS − TOTAL_INS − PIT − TOTAL_POST_DED + TOTAL_POST_ADD", "C13.3",
   lambda e, p: tonghop.net_pay(e["GROSS"], e["TOTAL_INS"], e["PIT"],
                                e["TOTAL_POST_DED"], e["TOTAL_POST_ADD"]))
_n("NET_PAY_HOME", ("NET_PAY",), "ROUND(NET_PAY, 0)", "C13.3",
   lambda e, p: round0(e["NET_PAY"]))
_n("TOTAL_CTY_COST", ("NET_PAY", "TOTAL_INS_CTY", "KPCD_CTY"),
   "NET_PAY + TOTAL_INS_CTY + KPCD_CTY (as-is — không phải GROSS)", "C13.4",
   lambda e, p: tonghop.total_cty_cost(e["NET_PAY"], e["TOTAL_INS_CTY"], e["KPCD_CTY"]))

_n("BONUS_SAVE_TRAVEL", ("PAID_DAYS",), "ROUND(6.000.000/12, 0)", "C10.2",
   thuong.bonus_save_travel)
_n("BONUS_SAVE_KPI", ("CONTRACT_TOTAL", "PAID_DAYS"), "ROUND(CONTRACT_TOTAL/4, 0)", "C10.2",
   thuong.bonus_save_kpi)
_n("BONUS_SAVE_13M", ("CONTRACT_TOTAL", "PAID_DAYS"), "ROUND(CONTRACT_TOTAL/12, 0)", "C10.2",
   thuong.bonus_save_13m)
_n("BONUS_SAVE_TET", ("CONTRACT_TOTAL", "PAID_DAYS"),
   "MIN(ROUND(CONTRACT_TOTAL/12,0), ROUND(15.000.000/12,0))", "C10.2", thuong.bonus_save_tet)
_n("BUDGET_SAVE",
   ("GROSS", "TOTAL_INS_CTY", "KPCD_CTY", "BONUS_SAVE_TRAVEL", "BONUS_SAVE_KPI",
    "BONUS_SAVE_13M", "BONUS_SAVE_TET"),
   "GROSS + TOTAL_INS_CTY + KPCD_CTY + các khoản trích", "C10.2",
   lambda e, p: tonghop.budget_save(
       e["GROSS"], e["TOTAL_INS_CTY"], e["KPCD_CTY"],
       [e["BONUS_SAVE_TRAVEL"], e["BONUS_SAVE_KPI"], e["BONUS_SAVE_13M"], e["BONUS_SAVE_TET"]]))

_OUTPUT = tuple(CODES)


def _resolve(code: str, env: dict, p: dict, trace: dict, dang_tinh: set) -> Decimal:
    if code in trace:
        return env[code]
    node = CODES.get(code)
    if node is None:                       # field input — ô Excel trống coi như 0
        val = _dec(env.get(code, 0) or 0)
        env[code] = val
        trace[code] = {"formula": "input", "value": val,
                       "clause": CLAUSE_INPUT, "deps": []}
        return val
    if code in dang_tinh:
        raise ValueError(f"Chu trình phụ thuộc tại CODE {code}")
    dang_tinh.add(code)
    for d in node.deps:
        _resolve(d, env, p, trace, dang_tinh)
    val = node.fn(env, p)
    dang_tinh.discard(code)
    env[code] = val
    trace[code] = {"formula": node.formula, "value": val,
                   "clause": node.clause, "deps": list(node.deps)}
    return val


def compute(code: str, rec: dict, p: dict) -> Decimal:
    """Tính một CODE — tự resolve đệ quy toàn bộ phụ thuộc [C3.1]."""
    return _resolve(code, dict(rec), p, {}, set())


def bang_luong(rec: dict, p: dict):
    """Tính hết field kết quả → (kết_quả, vết_truy) [C14.1]."""
    env, trace = dict(rec), {}
    for code in _OUTPUT:
        _resolve(code, env, p, trace, set())
    return {c: env[c] for c in _OUTPUT}, trace


def kiem_tra_dag() -> None:
    """Ném lỗi nếu đồ thị phụ thuộc có chu trình [C3.1]."""
    xong, stack = set(), set()

    def di(code):
        if code in xong or code not in CODES:
            return
        if code in stack:
            raise ValueError(f"Chu trình phụ thuộc tại CODE {code}")
        stack.add(code)
        for d in CODES[code].deps:
            di(d)
        stack.discard(code)
        xong.add(code)

    for code in CODES:
        di(code)
