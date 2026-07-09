"""p27_baocao_hr — báo cáo bảo mật HR C&B + đơn treo lãnh đạo tại cut-off (C6.4, C6.5)."""

_XUAT_LOG = []


def bang_tong_hop_pc(ky):
    return [
        {f"pc{i}": 0 for i in range(1, 9)}
    ]


def xuat_bao_cao(ten_bao_cao, user=None):
    if not user:
        raise ValueError("xuat_bao_cao yêu cầu user, không được để trống")
    log_id = f"log-{len(_XUAT_LOG) + 1}"
    entry = {"log_id": log_id, "bao_cao": ten_bao_cao, "user": user}
    _XUAT_LOG.append(entry)
    return entry


def don_treo(ky):
    return [
        {"msnv": "NV012", "ky": ky},
    ]
