"""OT engine (C5.5) — multiplier CN/lễ/truyền thống, tách CT/Mắt Bão."""


def tinh_ot(
    ma_nv,
    luong_ngay=0,
    so_ngay_tc200=0,
    so_ngay_le_luat=0,
    so_ngay_le_300=0,
    employee_type="Official",
    **kwargs,
):
    trace = []
    tien_ot = 0.0
    ngay_nghi_bu_sinh_them = 0

    if so_ngay_tc200:
        tien_ot += so_ngay_tc200 * luong_ngay * 2.0
        trace.append(f"CN 200%: {so_ngay_tc200} ngày x {luong_ngay} x 2.0")

    if so_ngay_le_luat:
        tien_ot += so_ngay_le_luat * luong_ngay * (1.0 + 1.0)
        ngay_nghi_bu_sinh_them += so_ngay_le_luat * 2
        trace.append(
            f"Lễ luật: {so_ngay_le_luat} ngày +100% & +2 nghỉ bù/ngày"
        )

    if so_ngay_le_300:
        tien_ot += so_ngay_le_300 * luong_ngay * 3.0
        trace.append(
            f"assumed: danh sách 300% rỗng — {so_ngay_le_300} ngày x 3.0 tạm tính"
        )

    return {
        "ma_nv": ma_nv,
        "tien_ot": tien_ot,
        "ngay_nghi_bu_sinh_them": ngay_nghi_bu_sinh_them,
        "employee_type": employee_type,
        "trace": "; ".join(trace),
    }
