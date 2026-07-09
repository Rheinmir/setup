"""Tổng hợp suất ăn theo bộ phận (C5.1.5, C5.3.1, C5.4).

Quy tắc bữa: VP 1 · CT<30km 2 · CT≥30km 3 · ngày ≤4h 0 suất.
Cộng thêm cơm TC đêm + cơm CN/lễ do thư ký chấm + cơm bổ sung tháng trước.

Dữ liệu nhân viên là dữ liệu mẫu nội bộ scope (không phụ thuộc file ngoài).
"""

SUAT_VP = 1
SUAT_CT_DUOI_30KM = 2
SUAT_CT_TU_30KM = 3
SUAT_DUOI_4H = 0

_DU_LIEU = {
    "NV_vidu1": {
        "VP HCM": {
            "vp": 5,
            "ct_duoi_30": 0,
            "ct_tu_30": 20,
            "tc_dem": 0,
            "cn_le_ngay": 0,
            "com_bo_sung_thang_truoc": 0,
        },
    },
    "NV004": {
        "VP HCM": {
            "vp": 18,
            "ct_duoi_30": 0,
            "ct_tu_30": 0,
            "duoi_4h": 1,
            "tc_dem": 0,
            "cn_le_ngay": 0,
            "com_bo_sung_thang_truoc": 0,
        },
    },
    "NV008": {
        "CT Quan Lạn": {
            "vp": 0,
            "ct_duoi_30": 0,
            "ct_tu_30": 0,
            "tc_dem": 0,
            "cn_le_ngay": 6,
            "com_bo_sung_thang_truoc": 0,
        },
    },
    "NV001": {
        "VP HCM": {
            "vp": 10,
            "ct_duoi_30": 0,
            "ct_tu_30": 0,
            "tc_dem": 0,
            "cn_le_ngay": 0,
            "com_bo_sung_thang_truoc": 0,
        },
        "CT Quan Lạn": {
            "vp": 0,
            "ct_duoi_30": 0,
            "ct_tu_30": 6,
            "tc_dem": 0,
            "cn_le_ngay": 0,
            "com_bo_sung_thang_truoc": 0,
        },
    },
}


def tong_hop_suat_an(ma_nv):
    du_lieu = _DU_LIEU.get(ma_nv, {})
    ket_qua = {}
    for bo_phan, d in du_lieu.items():
        theo_bua = (
            d.get("vp", 0) * SUAT_VP
            + d.get("ct_duoi_30", 0) * SUAT_CT_DUOI_30KM
            + d.get("ct_tu_30", 0) * SUAT_CT_TU_30KM
        )
        tc_dem = d.get("tc_dem", 0)
        cn_le_ngay = d.get("cn_le_ngay", 0)
        com_bo_sung = d.get("com_bo_sung_thang_truoc", 0)
        ket_qua[bo_phan] = {
            "tong": theo_bua + tc_dem + cn_le_ngay + com_bo_sung,
            "suat_cn_le": cn_le_ngay,
        }
    return ket_qua
