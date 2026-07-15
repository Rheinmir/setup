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


def save_uploaded_employees(period: str, rows: list) -> Path:
    """Ghi danh sách nhân sự đã mass-upload (từ Excel, xem app/upload.py) — BR C18.2.

    Adapt module có sẵn: ghi ĐÚNG chỗ `fetch_employees` đọc (data/inputs/<period>/
    employees.json), không mở đường I/O song song. Lô sau: chỗ nối Workday inbound
    (xem C18.1) thay hẳn nhu cầu upload tay này.
    """
    period_dir = _INPUTS / period
    period_dir.mkdir(parents=True, exist_ok=True)
    path = period_dir / "employees.json"
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


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


_KE_TOAN_TRUONG_CHUA_CO = ("profit_cost_center", "wbs", "funds_center")  # FE-20 — không có nguồn


def export_payroll_master(period: str, p: dict) -> Path:
    """Payroll Master (Template 2) — file phẳng cho kế toán [FE-20].

    Cột = nhân sự + TOÀN BỘ field engine tính ra (mọi thành phần lương/phụ
    cấp/BHXH/thuế/thực nhận/chi phí công ty). BA cột kế toán PRD mô tả
    (Profit/Cost Center, WBS, Funds Center) để RỖNG — không tồn tại nguồn
    dữ liệu nào trong hệ thống, KHÔNG bịa số. Đổi ruột lô sau khi có nguồn.
    """
    from app import engine
    rows = fetch_employees(period)
    codes = list(engine._OUTPUT)
    fields = ["employee_id", "ho_ten", "phong_ban", "CONTRACT_TYPE"] + codes + list(_KE_TOAN_TRUONG_CHUA_CO)
    out_dir = _OUT / period
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "payroll_master.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for rec in rows:
            kq, _trace = engine.bang_luong(rec, p)
            hang = {"employee_id": rec.get("employee_id", ""), "ho_ten": rec.get("ho_ten", ""),
                    "phong_ban": rec.get("phong_ban", ""), "CONTRACT_TYPE": rec.get("CONTRACT_TYPE", "")}
            hang.update({c: kq.get(c, "") for c in codes})
            hang.update({c: "" for c in _KE_TOAN_TRUONG_CHUA_CO})
            writer.writerow(hang)
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
