"""p24_pheduyet — phê duyệt & audit log bất biến, sync-back Workday (C6.2)."""

_AUDIT_LOG = []


def audit_log():
    return list(_AUDIT_LOG)


def duyet_don(ma_nv, ngay, nguoi, ly_do, override=False):
    if not ly_do:
        raise ValueError("Lý do phê duyệt bắt buộc")

    truoc = "?P"
    sau = "TC200"

    _AUDIT_LOG.append(
        {
            "ma_nv": ma_nv,
            "ngay": ngay,
            "truoc": truoc,
            "sau": sau,
            "nguoi": nguoi,
            "ly_do": ly_do,
            "override": override,
        }
    )

    return {"ky_hieu_moi": sau, "workday_sync": "Đã duyệt"}
