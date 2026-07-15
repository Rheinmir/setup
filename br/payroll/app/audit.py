"""audit.py — sổ nhật ký thay đổi dữ liệu (BR C14.2 / FE-17).

Trả lời gap #9 chính HR nêu: "When payroll output is wrong, how does anyone
know?" — mọi lần dữ liệu đổi (lô đầu: chỉ có mass-upload — xem C15.4/C18.2)
ghi lại giá-trị-cũ → giá-trị-mới, người, thời gian, lý do BẮT BUỘC.

Phạm vi lô đầu: "giá trị" ghi ở mức DANH SÁCH employee_id (mass-upload là
ghi-đè cả file, không phải sửa từng field) — không diff từng field/từng
nhân sự, vì lô đầu chỉ có MỘT hành động ghi (mass-upload thay nguyên file).
Sổ APPEND-ONLY, không sửa/xoá dòng cũ.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

_LOG = Path(__file__).resolve().parent.parent / "data" / "audit_log.jsonl"


def log_action(action: str, period: str, performed_by: str, reason: str,
               old_ids: list, new_ids: list) -> dict:
    """Ghi một dòng nhật ký. Lý do + người thực hiện BẮT BUỘC không rỗng."""
    performed_by = (performed_by or "").strip()
    reason = (reason or "").strip()
    if not performed_by:
        raise ValueError("audit: thiếu người thực hiện (bắt buộc)")
    if not reason:
        raise ValueError("audit: thiếu lý do (bắt buộc)")
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "period": period,
        "performed_by": performed_by,
        "reason": reason,
        "old_employee_ids": list(old_ids),
        "new_employee_ids": list(new_ids),
    }
    _LOG.parent.mkdir(parents=True, exist_ok=True)
    with _LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def read_log() -> list:
    """Đọc toàn bộ sổ, thứ tự cũ → mới (thứ tự ghi)."""
    if not _LOG.exists():
        return []
    rows = []
    for line in _LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows
