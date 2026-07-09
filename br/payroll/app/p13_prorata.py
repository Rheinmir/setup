"""Engine pro-rata dùng chung: (định mức/công chuẩn) x ngày hưởng, chia theo bộ phận."""


def tinh_prorata(bo_phan, cong_chuan, dinh_muc_fn):
    tong = 0
    trace = {}
    for ten, so_lieu in bo_phan.items():
        ngay_huong = so_lieu.get("lam_viec", 0) + so_lieu.get("le", 0)
        dinh_muc = dinh_muc_fn(ten)
        so_tien = ngay_huong / cong_chuan * dinh_muc
        tong += so_tien
        trace[ten] = (
            f"{ngay_huong} ngày (làm việc + lễ) / {cong_chuan} công chuẩn x "
            f"định mức {dinh_muc} = {so_tien} (nguồn: {ten})"
        )
    return {"tong": tong, "trace": trace}
