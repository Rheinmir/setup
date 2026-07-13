"""snapshot.py — Snapshot bất biến + diff parallel-run (BR C16.1, C16.2).

Mỗi lần chạy ghi một thư mục mới `<root>/<period>/run-<ts>-<seq>/rows.json`, không
bao giờ ghi đè. `diff(a, b)` so hai thư mục → ai lệch, field nào lệch, lệch bao nhiêu.
Tiền lưu dạng chuỗi để Decimal đi qua JSON mà không mất đồng nào.
"""
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

_ROWS = "rows.json"
_ID = "employee_id"


def _encode(value):
    return str(value) if isinstance(value, Decimal) else value


def write_run(period: str, rows: list, root) -> Path:
    """Ghi một snapshot bất biến, trả về thư mục vừa tạo (mới mỗi lần gọi)."""
    base = Path(root) / period
    base.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    seq = 0
    while True:
        run_dir = base / f"run-{ts}-{seq:04d}"
        try:
            run_dir.mkdir()
            break
        except FileExistsError:
            seq += 1
    payload = [{k: _encode(v) for k, v in row.items()} for row in rows]
    (run_dir / _ROWS).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return run_dir


def _load(run_dir) -> dict:
    rows = json.loads((Path(run_dir) / _ROWS).read_text(encoding="utf-8"))
    return {row[_ID]: row for row in rows}


def _num(value) -> Decimal:
    return Decimal(str(value)) if value is not None else Decimal(0)


def diff(run_a, run_b) -> list:
    """So hai snapshot → [{employee_id, code, delta}] (b trừ a)."""
    a, b = _load(run_a), _load(run_b)
    out = []
    for emp in sorted(a.keys() | b.keys()):
        row_a, row_b = a.get(emp, {}), b.get(emp, {})
        for code in sorted((row_a.keys() | row_b.keys()) - {_ID}):
            va, vb = row_a.get(code), row_b.get(code)
            if va == vb:
                continue
            out.append({_ID: emp, "code": code, "delta": str(_num(vb) - _num(va))})
    return out
