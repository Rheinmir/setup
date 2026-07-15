"""auth.py — model quyền MỘT chỗ duy nhất [C2.1].

Lô đầu: MỘT vai duy nhất "HR C&B", không đăng nhập thật (chạy local).
Azure AD SSO (FE-32) vẫn `⊘ ngoài phạm vi` — xem C19. `require(perm)` là
điểm nối sẵn: khi có auth thật, chỉ cần đổi ruột `current_user()` để đọc
session/token thay vì trả cứng — mọi handler gọi `require(perm)` không đổi
gì (đúng nguyên tắc build-now-adapt-later đã dùng cho `app/adapters.py`).
"""
from enum import Enum


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
