"""Test đỏ frame p26 — Template 2 Payroll Master, file phẳng cho kế toán (C6.3).
Tổng quát: nối THẬT vào p06-p19, tính cho TOÀN BỘ 12 NV trong nhan_vien.csv."""
import unittest
from app.p26_template2 import payroll_master


class TestTemplate2(unittest.TestCase):
    def test_nv004_luong_tach_moc(self):
        rows = {r["msnv"]: r for r in payroll_master("2026-07")}
        r = rows["NV004"]
        self.assertGreater(r["luong_thu_viec"], 0)
        self.assertGreaterEqual(r["luong_chinh_thuc"], 0)

    def test_tong_pc_khop_thanh_phan(self):
        rows = {r["msnv"]: r for r in payroll_master("2026-07")}
        r = rows["NV001"]
        thanh_phan = sum(r.get(k, 0) for k in
            ("pc_com", "pc_dien_thoai", "pc_xang", "pc_ct_ctx", "pc_di_lai", "pc_ct_xa", "pc_khac"))
        self.assertAlmostEqual(r["pc_tong"], thanh_phan, delta=1000)

    def test_non_tax_com_tran(self):
        rows = payroll_master("2026-07")
        for r in rows:
            self.assertLessEqual(r.get("pc_com_non_tax", 0), 730_000)

    def test_thai_san_thue_khong_am(self):
        rows = {r["msnv"]: r for r in payroll_master("2026-07")}
        r = rows["NV010"]
        self.assertGreaterEqual(r["thue_tncn"], -0.01)

    def test_du_12_nv_toan_bo_roster(self):
        # Tổng quát: tất cả 12 NV trong nhan_vien.csv đều có dòng, không chỉ 3 NV cũ.
        rows = payroll_master("2026-07")
        self.assertEqual(len(rows), 12)
        msnv_list = {r["msnv"] for r in rows}
        self.assertIn("NV007", msnv_list)   # GĐDA — chưa từng có trong _DATA cũ
        self.assertIn("NV012", msnv_list)   # Làng Tây – Hòn Thơm — chưa từng có


if __name__ == "__main__":
    unittest.main()
