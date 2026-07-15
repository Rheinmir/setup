"""auth.py — model quyền MỘT chỗ duy nhất [C2.1].

Lô đầu: MỘT vai duy nhất "HR C&B". Azure AD SSO (FE-32) vẫn `⊘ ngoài phạm
vi` — xem C19. `require(perm)` là điểm nối sẵn: khi có auth thật, chỉ cần
đổi ruột `current_user()` để đọc session/token thay vì trả cứng — mọi
handler gọi `require(perm)` không đổi gì (đúng nguyên tắc build-now-adapt-
later đã dùng cho `app/adapters.py`).

Session (cập nhật 2026-07-15, quyết định trực tiếp của user): `/login`
giờ là cổng bắt buộc trước khi vào bất kỳ route nào — NHƯNG đây là CỔNG
UX/SESSION, TUYỆT ĐỐI KHÔNG PHẢI xác thực bảo mật thật. `login()` không
kiểm bất kỳ mật khẩu/tài khoản nào — gọi là tạo session ngay. Session lưu
TRONG BỘ NHỚ (mất khi restart server) — lô đầu 1 vai, không cần persist.
"""
import secrets
from enum import Enum

_SESSIONS = {}  # session_id (str) -> user dict, TRONG BỘ NHỚ, không persist


class Perm(Enum):
    VIEW = "view"
    EDIT = "edit"
    EXPORT = "export"
    LOCK_PERIOD = "lock_period"
    APPROVE_ON_BEHALF = "approve_on_behalf"
    MASK_MONEY = "mask_money"


# Lô đầu: vai HR C&B duy nhất, đủ tất cả quyền (C2.1). KHÔNG có vai thứ 2
# nào trong hệ thống hiện tại — require() do đó chưa từng thực sự chặn ai,
# nhưng cấu trúc gate đã sẵn cho lúc có vai thứ 2 (vd Thư ký công trường).
_HR_CB = frozenset(Perm)


def current_user() -> dict:
    """Stub — lô đầu không đăng nhập, luôn trả vai HR C&B.

    Nối Azure AD sau: đổi hàm này đọc session/token thật, trả đúng `perms`
    theo vai user đã đăng nhập. `require()` và mọi lời gọi nó không đổi.
    """
    return {"name": "HR C&B (mặc định lô đầu — chưa có auth thật)", "perms": _HR_CB}


def require(perm: Perm, user: dict = None) -> None:
    """Ném PermissionError nếu user không đủ quyền `perm`. Gọi ở ĐẦU mỗi
    handler nhạy cảm (báo cáo bảo mật, sửa dữ liệu, khoá kỳ...)."""
    u = user or current_user()
    if perm not in u["perms"]:
        raise PermissionError(f"Thiếu quyền {perm.value} (user: {u['name']})")


def login() -> str:
    """Tạo session mới cho vai HR C&B lô đầu. KHÔNG kiểm mật khẩu/tài khoản
    nào — bấm là được (xem C2.1, cập nhật 2026-07-15: cổng UX, không phải
    xác thực thật). Trả session_id để phía UI set cookie."""
    sid = secrets.token_urlsafe(16)
    _SESSIONS[sid] = current_user()
    return sid


def session_user(session_id) -> dict:
    """None nếu session không tồn tại (chưa login/đã logout/server restart/
    session_id rỗng)."""
    return _SESSIONS.get(session_id) if session_id else None


def logout(session_id) -> None:
    """Xoá session — không lỗi nếu session_id không tồn tại/đã xoá rồi."""
    _SESSIONS.pop(session_id, None)
