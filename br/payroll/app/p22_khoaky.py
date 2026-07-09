"""p22_khoaky — khóa kỳ manual lock (tier: compensable, BR C4.3)."""

_locked_ky = {}


def khoa_ky(ky, nguoi, ly_do):
    if not ly_do:
        raise ValueError("ly_do khóa kỳ không được rỗng")
    if ky not in _locked_ky:
        _locked_ky[ky] = {"nguoi": nguoi, "ly_do": ly_do}


def is_locked(ky):
    return ky in _locked_ky
