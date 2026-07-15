"""f15 auth — model quyền MỘT chỗ [C2.1]. Lô đầu: 1 vai HR C&B đủ quyền,
không đăng nhập thật (FE-32 SSO ⊘ ngoài phạm vi — xem C19). Cấu trúc
require(perm) là điểm nối sẵn cho Azure AD sau này (chỉ đổi current_user())."""
import unittest
from app import auth


class TestAuth(unittest.TestCase):
    def test_du_6_quyen_dung_ten_da_hua_o_C2_1(self):
        ten = {p.value for p in auth.Perm}
        self.assertEqual(ten, {"view", "edit", "export", "lock_period",
                              "approve_on_behalf", "mask_money"})

    def test_current_user_lo_dau_du_tat_ca_quyen(self):
        u = auth.current_user()
        for p in auth.Perm:
            self.assertIn(p, u["perms"], f"vai lô đầu phải có quyền {p.value}")

    def test_require_pass_khi_du_quyen(self):
        auth.require(auth.Perm.MASK_MONEY)  # không ném lỗi = pass

    def test_require_nem_loi_khi_thieu_quyen(self):
        vai_gioi_han = {"name": "Thư ký công trường (giả định test)", "perms": {auth.Perm.VIEW}}
        with self.assertRaises(PermissionError):
            auth.require(auth.Perm.MASK_MONEY, user=vai_gioi_han)
        auth.require(auth.Perm.VIEW, user=vai_gioi_han)  # quyền có thì vẫn pass

    # ── C2.1 (cập nhật 2026-07-15) — cổng session, KHÔNG PHẢI xác thực thật ──
    def test_login_tao_session_hop_le_tra_ve_du_lieu_vai_lo_dau(self):
        sid = auth.login()
        self.assertIsInstance(sid, str)
        u = auth.session_user(sid)
        self.assertIsNotNone(u)
        self.assertEqual(u["name"], auth.current_user()["name"])
        self.assertEqual(u["perms"], auth.current_user()["perms"])

    def test_session_khong_ton_tai_tra_none(self):
        self.assertIsNone(auth.session_user("khong-ton-tai-bao-gio"))
        self.assertIsNone(auth.session_user(None))
        self.assertIsNone(auth.session_user(""))

    def test_logout_xoa_dung_session_khong_dung_session_khac(self):
        sid1 = auth.login()
        sid2 = auth.login()
        auth.logout(sid1)
        self.assertIsNone(auth.session_user(sid1))
        self.assertIsNotNone(auth.session_user(sid2))  # session khác không bị đụng
        auth.logout(sid2)  # dọn


if __name__ == "__main__":
    unittest.main()
