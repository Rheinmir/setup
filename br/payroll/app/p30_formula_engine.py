"""p30_formula_engine — Engine công thức lương THẬT, trích từ Excel bàn giao
"(Confidential) Payroll Handover Assessment - inferred.xlsx" sheet "Payroll
structure" (127 dòng field: code, tên, loại input/formula, công thức Excel gốc)
+ sheet "References" (bảng thuế TNCN lũy tiến 7 bậc, NĐ 65/2013).

Thiết kế: mỗi field là một NODE trong dependency graph (input hoặc formula tham
chiếu field khác qua [CODE]). compute(code, inputs) resolve đệ quy — CHẠY 1 LẦN
là ra đủ chuỗi từ input thô đến NET_PAY_HOME, không cần biết thứ tự phụ thuộc
tay. Đây là nguồn THẬT thay literal fake trước đây (p26_template2.py cũ)."""

import re

# ── Bảng field: code -> (tên, công thức Excel gốc hoặc None nếu là input) ──
# Trích nguyên văn cột I "công thức hiện tại" sheet Payroll structure — KHÔNG
# tự suy diễn, đúng những gì HR/Payroll team đã viết trong file bàn giao.
FIELDS = {
    "STD_DAYS": ("Công chuẩn", None),
    "PROB_DAYS": ("Ngày công thử việc", None),
    "OFFICIAL_DAYS": ("Ngày công chính thức", None),
    "PAID_LEAVE_DAYS": ("Nghỉ phép năm", None),
    "HOLIDAY_DAYS": ("Nghỉ lễ, tết", None),
    "COMP_DAYS": ("Nghỉ bù", None),
    "REGIME_DAYS": ("Nghỉ chế độ & có hưởng lương", None),
    "SI_DAYS": ("Nghỉ chế độ BHXH", None),
    "ADJ_DAYS": ("Ngày công điều chỉnh", None),
    "ACTUAL_DAYS": ("Tổng ngày công thực tế", None),  # input thô từ Workday
    "PAID_DAYS": ("Tổng ngày làm việc hưởng lương",
                  "[ACTUAL_DAYS] + [HOLIDAY_DAYS] + [PAID_LEAVE_DAYS] + [COMP_DAYS] + [REGIME_DAYS] + [SI_DAYS] + [ADJ_DAYS]"),
    "PROB_SAL": ("Lương thử việc (85%)", None),
    "BASIC_SAL": ("Lương chính thức (100%)", None),
    "RESPONSIBILITY_ALLOW": ("Phụ cấp trách nhiệm (HĐLĐ)", None),
    "CONTRACT_TOTAL": ("Tổng lương trên HĐLĐ", "[BASIC_SAL] + [RESPONSIBILITY_ALLOW]"),
    "INS_SAL_BH": ("Mức lương đóng BHXH, BHYT", "MIN([BASIC_SAL], 46800000)"),
    "INS_SAL_UI": ("Mức lương đóng BHTN", "MIN([BASIC_SAL], 106200000)"),
    "PROB_EARNED": ("Lương thử việc (thực tế)", "[PROB_DAYS] * [PROB_SAL] / [STD_DAYS]"),
    "OFFICIAL_EARNED": ("Lương chính thức (thực tế)", "([PAID_DAYS] - [PROB_DAYS]) * [BASIC_SAL] / [STD_DAYS]"),
    "RESP_EARNED": ("Phụ cấp trách nhiệm (thực tế)", "[PAID_DAYS] * [RESPONSIBILITY_ALLOW] / [STD_DAYS]"),
    "EARNED_SAL": ("Tổng lương thực tế trong tháng", "[PROB_EARNED] + [OFFICIAL_EARNED] + [RESP_EARNED]"),
    "MEALS_TOTAL": ("Tổng bữa cơm", None),  # input (tổng hợp từ p12 suất ăn)
    "MEAL_ALLOW": ("PC cơm (tổng)", "[MEALS_TOTAL] * 45000"),
    "MEAL_TAX": ("PC cơm (chịu thuế)", "MAX(0, [MEAL_ALLOW] - 1200000)"),
    "MEAL_NONTAX": ("PC cơm (không chịu thuế)", "MIN([MEAL_ALLOW], 1200000)"),
    "PHONE_ALLOW": ("PC điện thoại (tổng)", None),
    "PHONE_TAX": ("PC điện thoại (chịu thuế)", "0"),
    "PHONE_NONTAX": ("PC điện thoại (không chịu thuế)", "[PHONE_ALLOW]"),
    "FUEL_ALLOW": ("PC nhiên liệu/xăng", None),
    "FUEL_NONTAX": ("PC NL/Xăng (không chịu thuế)", None),
    "TRANSPORT_ALLOW": ("PC đi lại (chuẩn)", None),
    "TRIP_OVERRIDE": ("PC đi lại duyệt riêng", None),
    "TRANSPORT_TAX": ("PC đi lại (chịu thuế)", "[TRANSPORT_ALLOW] + [TRIP_OVERRIDE]"),
    "TRANSPORT_NONTAX": ("PC đi lại (không chịu thuế)", None),
    "LIVING_ALLOW": ("PC nhà ở", None),
    "LIVING_NONTAX": ("PC nhà ở (không chịu thuế)", None),
    "OTHER_ALLOW_TAX": ("PC khác (chịu thuế)", None),
    "OTHER_ALLOW_NONTAX": ("PC khác (không chịu thuế)", None),
    "OT_TAX": ("Tăng ca (chịu thuế)", None),
    "OT_NONTAX": ("Tăng ca (không chịu thuế)", None),
    "BONUS_TET": ("Thưởng tết âm lịch", None),
    "BONUS_30_04": ("Thưởng 30/04", None),
    "BONUS_CTD_DAY": ("Thưởng Coteccons Day", None),
    "BONUS_02_09": ("Thưởng 02/09", None),
    "BONUS_KPI": ("Thưởng KPIs", None),
    "BONUS_13M": ("Lương tháng 13", None),
    "BONUS_NEW_YEAR": ("Thưởng tết dương lịch 1/1", None),
    "BONUS_PROJECT": ("Thưởng dự án", None),
    "BONUS_EXCELLENCE": ("Thưởng cá nhân xuất sắc", None),
    "BONUS_LOC": ("Lộc đầu năm", None),
    "BONUS_OTHER": ("Thưởng khác", None),
    "BONUS_TRAVEL": ("Du lịch (không chịu thuế)", None),
    "BONUS_REFERRAL": ("Thưởng giới thiệu ứng viên", None),
    "BONUS_TOTAL": ("Tổng thưởng",
                     "[BONUS_TET] + [BONUS_30_04] + [BONUS_CTD_DAY] + [BONUS_02_09] + [BONUS_KPI] + "
                     "[BONUS_13M] + [BONUS_NEW_YEAR] + [BONUS_PROJECT] + [BONUS_EXCELLENCE] + [BONUS_LOC] + "
                     "[BONUS_OTHER] + [BONUS_TRAVEL] + [BONUS_REFERRAL]"),
    "SEVER_ALLOW": ("Trợ cấp nghỉ việc", None),
    "SI_BENEFIT": ("BHXH chi vào lương", None),
    "OTHER_SUPPORT": ("Trợ cấp khác", None),
    "FAMILY_SUPPORT": ("Các khoản hỗ trợ", None),
    "TOTAL_SUPPORT": ("Tổng trợ cấp", "[SEVER_ALLOW] + [SI_BENEFIT] + [OTHER_SUPPORT] + [FAMILY_SUPPORT]"),
    "ADJ_PLUS": ("Điều chỉnh cộng (+)", None),
    "ADJ_MINUS": ("Điều chỉnh trừ (-)", None),
    "GROSS": ("Tổng thu nhập trong tháng",
              "[EARNED_SAL] + [MEAL_TAX] + [MEAL_NONTAX] + [PHONE_TAX] + [PHONE_NONTAX] + [FUEL_ALLOW] + "
              "[FUEL_NONTAX] + [TRANSPORT_TAX] + [TRANSPORT_NONTAX] + [LIVING_ALLOW] + [LIVING_NONTAX] + "
              "[OTHER_ALLOW_TAX] + [OTHER_ALLOW_NONTAX] + [OT_TAX] + [OT_NONTAX] + [BONUS_TOTAL] + "
              "[TOTAL_SUPPORT] + [ADJ_PLUS] - [ADJ_MINUS]"),
    "TAXABLE_GROSS": ("Tổng thu nhập chịu thuế",
                       "[GROSS] - [MEAL_NONTAX] - [PHONE_NONTAX] - [FUEL_NONTAX] - [TRANSPORT_NONTAX] - "
                       "[LIVING_NONTAX] - [OTHER_ALLOW_NONTAX] - [OT_NONTAX] - [SEVER_ALLOW] - "
                       "[SI_BENEFIT] - [BONUS_TRAVEL]"),
    "SI_EMP": ("BHXH NV 8%", "MIN([BASIC_SAL], 46800000) * 0.08"),
    "SI_ADJ": ("Điều chỉnh BHXH NV", None),
    "HI_EMP": ("BHYT NV 1.5%", "MIN([BASIC_SAL], 46800000) * 0.015"),
    "HI_ADJ": ("Điều chỉnh BHYT NV", None),
    "UI_EMP": ("BHTN NV 1%", "MIN([BASIC_SAL], 106200000) * 0.01"),
    "UI_ADJ": ("Điều chỉnh BHTN NV", None),
    "TOTAL_INS": ("Tổng BHXH nhân viên", "[SI_EMP] + [SI_ADJ] + [HI_EMP] + [HI_ADJ] + [UI_EMP] + [UI_ADJ]"),
    "PERSONAL_DED": ("Giảm trừ bản thân", "15500000"),
    "DEPENDENT_CNT": ("Số người phụ thuộc", None),
    "DEPENDENT_DED": ("Giảm trừ gia cảnh NPT", "[DEPENDENT_CNT] * 6200000"),
    "TOTAL_DED": ("Tổng khoản giảm trừ", "[PERSONAL_DED] + [DEPENDENT_DED]"),
    "TAXABLE_INC": ("Thu nhập tính thuế", "MAX(0, [TAXABLE_GROSS] - [TOTAL_INS] - [TOTAL_DED])"),
    "PIT": ("Thuế TNCN", None),  # type=system — tính bằng tinh_thue_tncn(), không phải chuỗi công thức
    "PIT_ADJ": ("Điều chỉnh thuế TNCN", None),
    "TOTAL_PIT": ("Tổng thuế TNCN đã khấu trừ", "[PIT] + [PIT_ADJ]"),
    "NET_INCOME": ("Thu nhập thuần", "[GROSS] - [TOTAL_INS] - [PIT] - [PIT_ADJ]"),
    "PIT_SETTLE": ("Quyết toán thuế", None),
    "SI_REGIME": ("Chế độ BHXH", None),
    "SEVER_FUND": ("Trợ cấp thôi việc (trích quỹ)", None),
    "SEVER_PAY": ("Trợ cấp thôi việc NĐ 145/2020", None),
    "OTHER_POST_ADD": ("Cộng sau thuế khác", None),
    "TOTAL_POST_ADD": ("Tổng cộng sau thuế", "[PIT_SETTLE] + [SI_REGIME] + [SEVER_FUND] + [SEVER_PAY] + [OTHER_POST_ADD]"),
    "UNION_FEE": ("Phí công đoàn (0.5%)", "[BASIC_SAL] * 0.005"),
    "BAOVET_INS": ("Thu hộ BH Bảo Việt", None),
    "DEDUCT_LOC": ("Trừ lộc đầu năm", None),
    "PIT_SETTLE_DED": ("Quyết toán thuế (trừ)", None),
    "OTHER_POST_DED": ("Trừ sau thuế khác", None),
    "FAMILY_HEALTH_INS": ("BHSK người thân (Cty tài trợ)", None),
    "TOTAL_POST_DED": ("Tổng trừ sau thuế",
                        "[UNION_FEE] + [BAOVET_INS] + [DEDUCT_LOC] + [PIT_SETTLE_DED] + [OTHER_POST_DED] + [FAMILY_HEALTH_INS]"),
    "NET_PAY": ("Lương thực nhận (VND)", "[GROSS] - [TOTAL_INS] - [TOTAL_PIT] - [TOTAL_POST_DED] + [TOTAL_POST_ADD]"),
    "NET_PAY_HOME": ("Lương thực chi (VND)", "ROUND([NET_PAY], 0)"),
    "ADVANCE_1": ("Tạm ứng / thực chi đợt 1", None),
    "NET_PAY_2": ("Lương thực chi đợt 2", "[NET_PAY] - [ADVANCE_1]"),
    "SI_CTY": ("BHXH Cty 17%", "MIN([BASIC_SAL], 46800000) * 0.17"),
    "SI_CTY_ADJ": ("Điều chỉnh BHXH Cty", None),
    "TNLD_CTY": ("BHTNLĐ-BNN Cty 0.5%", "MIN([BASIC_SAL], 106200000) * 0.005"),
    "TNLD_CTY_ADJ": ("Điều chỉnh BHTNLĐ Cty", None),
    "HI_CTY": ("BHYT Cty 3%", "MIN([BASIC_SAL], 46800000) * 0.03"),
    "HI_CTY_ADJ": ("Điều chỉnh BHYT Cty", None),
    "UI_CTY": ("BHTN Cty 1%", "MIN([BASIC_SAL], 106200000) * 0.01"),
    "UI_CTY_ADJ": ("Điều chỉnh BHTN Cty", None),
    "TOTAL_INS_CTY": ("Tổng BHXH Cty đóng",
                       "[SI_CTY] + [SI_CTY_ADJ] + [TNLD_CTY] + [TNLD_CTY_ADJ] + [HI_CTY] + [HI_CTY_ADJ] + [UI_CTY] + [UI_CTY_ADJ]"),
    "KPCD_CTY": ("2% KPCĐ Cty", "[BASIC_SAL] * 0.02"),
    "TOTAL_CTY_COST": ("Tổng chi phí công ty", "[GROSS] + [TOTAL_INS_CTY] + [KPCD_CTY]"),
}

# Field input mặc định 0 nếu người dùng không truyền (mọi field "None formula"
# không có trong inputs coi như 0 — đúng hành vi Excel ô trống).
_REF = re.compile(r"\[([A-Z0-9_]+)\]")
_SAFE_FUNCS = {"MIN": min, "MAX": max, "ROUND": round}


def _to_python_expr(formula):
    """[CODE] -> _v('CODE'); Excel MIN/MAX/ROUND đã là tên hàm Python-safe sẵn."""
    return _REF.sub(lambda m: f"_v({m.group(1)!r})", formula)


# ── Bảng thuế TNCN lũy tiến 7 bậc (NĐ 65/2013, khớp 3 bậc đọc được từ sheet
# References: 5% 0-5tr, 10% 5-10tr, 30% 52-80tr) ──
BAC_THUE = (
    (0, 5_000_000, 0.05, 0),
    (5_000_000, 10_000_000, 0.10, 250_000),
    (10_000_000, 18_000_000, 0.15, 750_000),
    (18_000_000, 32_000_000, 0.20, 1_650_000),
    (32_000_000, 52_000_000, 0.25, 3_250_000),
    (52_000_000, 80_000_000, 0.30, 5_850_000),
    (80_000_000, float("inf"), 0.35, 9_850_000),
)


def tinh_thue_tncn(thu_nhap_tinh_thue):
    """Thuế TNCN lũy tiến từng phần — công thức rút gọn (thuế = TNTT × thuế suất
    − số tiền trừ) theo bậc TNTT rơi vào. Nguồn: sheet References, bảng
    Progressive TaxTable."""
    if thu_nhap_tinh_thue <= 0:
        return 0.0
    for tu, den, thue_suat, tru in BAC_THUE:
        if tu < thu_nhap_tinh_thue <= den or (den == float("inf") and thu_nhap_tinh_thue > tu):
            return round(thu_nhap_tinh_thue * thue_suat - tru, 0)
    return 0.0


def compute(code, inputs, _cache=None, _trace=None):
    """Resolve đệ quy field `code` từ `inputs` (dict CODE->số hoặc chuỗi input
    thô). _trace (nếu truyền dict rỗng) được điền {code: (ten, formula, giá_trị)}
    cho MỌI field đã tính qua — dùng để hiển thị "luồng đi" trên UI."""
    if _cache is None:
        _cache = {}
    if code in _cache:
        return _cache[code]

    if code == "PIT":
        val = tinh_thue_tncn(compute("TAXABLE_INC", inputs, _cache, _trace))
        _cache[code] = val
        if _trace is not None:
            _trace[code] = (FIELDS[code][0], "tinh_thue_tncn(TAXABLE_INC) — 7 bậc lũy tiến", val)
        return val

    if code not in FIELDS:
        raise KeyError(f"Field không tồn tại trong Payroll structure: {code}")
    ten, formula = FIELDS[code]

    if formula is None:
        val = float(inputs.get(code, 0) or 0)
        _cache[code] = val
        if _trace is not None:
            _trace[code] = (ten, "(input)", val)
        return val

    def _v(dep_code):
        return compute(dep_code, inputs, _cache, _trace)

    expr = _to_python_expr(formula)
    val = eval(expr, {"__builtins__": {}}, {**_SAFE_FUNCS, "_v": _v})
    _cache[code] = val
    if _trace is not None:
        _trace[code] = (ten, formula, val)
    return val


def bang_luong_day_du(inputs):
    """Chạy 1 LẦN → toàn bộ chuỗi field liên quan tới NET_PAY_HOME (và
    TOTAL_CTY_COST phía Cty) — trả kèm trace đầy đủ cho UI hiển thị luồng đi."""
    trace = {}
    cache = {}
    ket_qua = {
        "NET_PAY_HOME": compute("NET_PAY_HOME", inputs, cache, trace),
        "TOTAL_CTY_COST": compute("TOTAL_CTY_COST", inputs, cache, trace),
    }
    return ket_qua, trace
