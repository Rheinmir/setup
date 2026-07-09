"""Sinh lịch kỳ công 21–20 + kỳ BHXH song song (C4.1)."""
import datetime
import calendar


def _cong_chuan(tu, den, tru_chieu_t7):
    d = tu
    cong = 0.0
    while d <= den:
        wd = d.weekday()  # 0=Mon .. 6=Sun
        if wd == 6:
            pass
        elif wd == 5 and tru_chieu_t7:
            cong += 0.5
        else:
            cong += 1.0
        d += datetime.timedelta(days=1)
    return cong


def sinh_lich_ky(thang_str):
    nam, thang = (int(x) for x in thang_str.split("-"))

    den = datetime.date(nam, thang, 20)
    if thang == 1:
        nam_tu, thang_tu = nam - 1, 12
    else:
        nam_tu, thang_tu = nam, thang - 1
    tu = datetime.date(nam_tu, thang_tu, 21)

    cong_chuan_vp = _cong_chuan(tu, den, True)
    cong_chuan_ct = _cong_chuan(tu, den, False)

    ngay = []
    ngay_to_thang_bhxh = {}
    d = tu
    while d <= den:
        iso = d.isoformat()
        le = d.weekday() == 6
        ngay.append({"ngay": iso, "le": le})
        ngay_to_thang_bhxh[iso] = f"{d.year:04d}-{d.month:02d}"
        d += datetime.timedelta(days=1)

    return {
        "tu": tu.isoformat(),
        "den": den.isoformat(),
        "cong_chuan_vp": cong_chuan_vp,
        "cong_chuan_ct": cong_chuan_ct,
        "ngay": ngay,
        "ngay_to_thang_bhxh": ngay_to_thang_bhxh,
    }
