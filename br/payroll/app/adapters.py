"""adapters.py — Ranh giới I/O 4 hàm — nay JSON, sau Workday (BR C18.1).

Engine chỉ được chạm thế giới bên ngoài qua bốn hàm dưới đây. Lô sau thay ruột
từng hàm bằng Workday; chữ ký và kiểu trả về giữ nguyên, engine không đổi.
"""
import csv
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_INPUTS = _ROOT / "data" / "inputs"
_OUT = _ROOT / "out"


def _read_json(period: str, name: str) -> list:
    path = _INPUTS / period / name
    if not path.exists():
        raise FileNotFoundError(f"Thiếu dữ liệu vào cho kỳ {period}: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_employees(period: str) -> list:
    """Danh sách nhân sự của kỳ.

    Nay: đọc data/inputs/<period>/employees.json.
    Lô sau: Workday HCM — GET /workers (đang bị chặn quyền).
    """
    return _read_json(period, "employees.json")


def fetch_timesheet(period: str) -> list:
    """Chấm công của kỳ.

    Nay: timesheet.json nếu có; chưa có thì các cột ngày công nằm sẵn trong
    employees.json (bảng lương thật gộp chung một dòng).
    Lô sau: Workday Time Tracking — GET /timeEntries (đang bị chặn quyền).
    """
    if (_INPUTS / period / "timesheet.json").exists():
        return _read_json(period, "timesheet.json")
    return fetch_employees(period)


def push_payslip(period: str, payslips: list) -> Path:
    """Đẩy phiếu lương đi.

    Nay: ghi out/<period>/payslips.json.
    Lô sau: Workday Payroll — POST /payslips (đang bị chặn quyền).
    """
    out_dir = _OUT / period
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "payslips.json"
    path.write_text(
        json.dumps(payslips, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return path


def export_bank_file(period: str, rows: list) -> Path:
    """Xuất file chuyển khoản ngân hàng (CSV phẳng).

    Nay: ghi out/<period>/bank.csv.
    Lô sau: Workday Payroll → template ngân hàng thật + SFTP.
    """
    out_dir = _OUT / period
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "bank.csv"
    fields = list(rows[0].keys()) if rows else ["employee_id", "amount"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path
