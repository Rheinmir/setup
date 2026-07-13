"""pipeline.py — LẮP RÁP: engine trên ground-truth, đối chiếu từng đồng (BR C17).

Không chép công thức: gọi lại engine + module domain đã có [C3.3].
"""
from decimal import Decimal
from functools import lru_cache

from app import engine, luong, params
from app.luong import CHINH_THUC, _dec, round0

# Bậc thuế của HR luôn có bậc cuối trần None → tách được ngưỡng SUMPRODUCT.
_PERIOD_MOI_NHAT = "9999-12"


@lru_cache(maxsize=None)
def _params(period: str) -> tuple:
    # dict không hash được → giữ trong tuple 1 phần tử cho lru_cache.
    return (params.load(period),)


def _cot_ngoai_engine(env: dict, p: dict) -> dict:
    """Cột kết quả Excel không phải nút engine — thành phần lương và giảm trừ [C17.1]."""
    chinh_thuc = env["CONTRACT_TYPE"] == CHINH_THUC
    personal = _dec(p["personal_ded"]) if chinh_thuc else Decimal(0)
    dependent = (round0(_dec(p["dependent_ded"]) * _dec(env.get("DEPENDENT_CNT", 0)))
                 if chinh_thuc else Decimal(0))
    return {
        "PROB_EARNED": luong.prob_earned(env, p),
        "OFFICIAL_EARNED": luong.official_earned(env, p),
        "RESP_EARNED": luong.resp_earned(env, p),
        "PERSONAL_DED": personal,
        "DEPENDENT_DED": dependent,
        # CM9 = PIT + PIT_ADJ [C13.3]
        "TOTAL_PIT": round0(env["PIT"] + _dec(env.get("PIT_ADJ", 0))),
    }


def _tinh(inputs: dict, p: dict) -> dict:
    kq, _ = engine.bang_luong(inputs, p)
    env = dict(inputs)
    env.update(kq)
    kq.update(_cot_ngoai_engine(env, p))
    return kq


def tinh(inputs: dict, period: str) -> dict:
    """Chạy cả engine cho một nhân sự trong một kỳ → dict mọi cột kết quả [C17.1]."""
    return _tinh(inputs, _params(period)[0])


def chay_roster(rows: list, period: str) -> list:
    """Chạy cả roster — tham số nạp một lần cho cả kỳ [C17.6]."""
    p = _params(period)[0]
    return [_tinh(rec, p) for rec in rows]


def pit_sumproduct(taxable, period: str = _PERIOD_MOI_NHAT) -> Decimal:
    """Cách tính thuế thứ hai của chính Excel (EX9): SUMPRODUCT trên phần vượt bậc [C17.2].

    Ngưỡng = trần bậc trước; suất biên = suất bậc này − suất bậc trước.
    """
    inc = _dec(taxable)
    brackets = _params(period)[0]["pit_brackets"]
    tong, nguong, suat_truoc = Decimal(0), Decimal(0), Decimal(0)
    for tran, suat, _tru in brackets:
        if inc > nguong:
            tong += (inc - nguong) * (_dec(suat) - suat_truoc)
        nguong, suat_truoc = (_dec(tran) if tran is not None else nguong), _dec(suat)
    return round0(tong)


def doi_chieu(gt: dict) -> list:
    """So engine với 30 cột thật của Excel → dòng lệch (rỗng = khớp từng đồng) [C17.1]."""
    kq = tinh(gt["inputs"], gt["period"])
    lech = []
    for code, mong_doi in gt["expected"].items():
        expected = _dec(mong_doi)
        got = kq.get(code)
        if got is None:
            lech.append({"code": code, "got": None, "expected": expected,
                         "delta": "thiếu cột"})
            continue
        if got != expected:
            lech.append({"code": code, "got": got, "expected": expected,
                         "delta": got - expected})
    return lech
