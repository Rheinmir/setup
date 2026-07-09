"""p29_import — validate + import CSV nhân viên upload từ UI (C7.1)."""
import csv
import io

CAC_COT_BAT_BUOC = (
    "msnv,ho_ten,ngach,trinh_do,chuc_danh,employee_type,bo_phan_hien_tai,"
    "noi_tuyen_dung,noi_cu_tru,ngay_vao,ngay_ket_thuc_thu_viec,"
    "luong_co_ban_thang(ASSUMED),ghi_chu"
).split(",")


def validate_and_import(noi_dung_csv, duong_dan_dich):
    reader = csv.reader(io.StringIO(noi_dung_csv))
    try:
        header = next(reader)
    except StopIteration:
        return False, 0, "file rỗng"

    thieu = [c for c in CAC_COT_BAT_BUOC if c not in header]
    if thieu:
        return False, 0, f"thiếu cột bắt buộc: {', '.join(thieu)}"

    thua = [c for c in header if c not in CAC_COT_BAT_BUOC]
    if thua:
        return False, 0, f"cột thừa không hợp lệ: {', '.join(thua)}"

    dong_du_lieu = list(reader)
    if not dong_du_lieu:
        return False, 0, "file rỗng, không có dòng dữ liệu"

    with open(duong_dan_dich, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(dong_du_lieu)

    return True, len(dong_du_lieu), None
