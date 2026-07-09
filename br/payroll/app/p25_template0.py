"""p25_template0 — Template 0 trình ký: định dạng chung Chính thức + Mắt Bão;
NV điều động gộp TOÀN BỘ công tháng vào bảng của dự án nơi làm việc ngày 20 (C6.3)."""

_ROSTER = {
    "NV001": {"noi_ngay20": "CT Quan Lạn", "tong_cong": 16.0},
    "NV002": {"noi_ngay20": "VP HCM", "tong_cong": 11.0},
    "NV005": {"noi_ngay20": "CT Quan Lạn", "tong_cong": 20.0},
}


def bang_trinh_ky(thang):
    bang = {}
    for msnv, info in _ROSTER.items():
        du_an = info["noi_ngay20"]
        bang.setdefault(du_an, []).append({"msnv": msnv, "tong": info["tong_cong"]})
    return bang
