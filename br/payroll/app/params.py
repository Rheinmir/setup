"""params.py — Tham số lương một chỗ, chọn theo effective_from (BR C4.1).

Đổi số = sửa data/params.json, không sửa code.
"""
import json
from pathlib import Path

_PARAMS_FILE = Path(__file__).resolve().parent.parent / "data" / "params.json"


def _period_date(period: str) -> str:
    """'2026-03' -> '2026-03-01' (kỳ lương lấy ngày đầu tháng)."""
    return period if len(period) > 7 else period + "-01"


def load(period: str) -> dict:
    """Bộ tham số có effective_from lớn nhất mà <= kỳ đang tính."""
    sets = json.loads(_PARAMS_FILE.read_text(encoding="utf-8"))["param_sets"]
    day = _period_date(period)
    valid = [s for s in sets if s["effective_from"] <= day]
    if not valid:
        raise ValueError(f"Không có bộ tham số nào hiệu lực cho kỳ {period}")
    return max(valid, key=lambda s: s["effective_from"])


def list_all() -> dict:
    """Toàn bộ nội dung file — mọi bộ tham số (kể cả chưa hiệu lực) [FE-23].

    Chỉ-xem, không sửa qua đây. Trả nguyên cấu trúc file: `param_sets` (mỗi
    bộ có `effective_from`) + `_pending_hr` (số đã nằm trong sheet HR nhưng
    chưa công thức nào tiêu thụ — xem BR A2).
    """
    return json.loads(_PARAMS_FILE.read_text(encoding="utf-8"))
