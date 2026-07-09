# Frames — Payroll & Timesheet (PRD 2.1)

> 28 frame CỠ NGHIỆP VỤ (khác att40 = cỡ hàm). Source of truth: `br/BR.md` (hash `19d405e59625…`).
> Trạng thái: PLANNING — chưa run frame nào. Thứ tự khuyến nghị: p01→p07 (nền) → p08→p12 (công) → p13→p20 (PC) → p21→p24 → p25→p28.

| frame_id | clause | scope_code | acceptance_test |
|---|---|---|---|
| frame-p01-lich-ky-cong | C4.1 | app/p01_lichky.py | python3 -m tests.test_p01 |
| frame-p02-master-data-store | C7 | app/p02_masterdata.py | python3 -m tests.test_p02 |
| frame-p03-bang-dinh-muc | C5.3.2,C5.3.4,C5.3.5,C5.3.6 | app/p03_dinhmuc.py | python3 -m tests.test_p03 |
| frame-p04-to-trinh-override | C5.2,C5.3.3,C5.3.7 | app/p04_totrinh.py | python3 -m tests.test_p04 |
| frame-p05-quy-dinh-nghi | C7 | app/p05_nghiphep.py | python3 -m tests.test_p05 |
| frame-p06-workday-adapter | C4.2 | app/p06_workday.py | python3 -m tests.test_p06 |
| frame-p07-parser-ky-hieu | C4.2 | app/p07_kyhieu.py | python3 -m tests.test_p07 |
| frame-p08-tach-thu-viec | C5.1.1 | app/p08_thuviec.py | python3 -m tests.test_p08 |
| frame-p09-tach-bo-nhiem | C5.1.2 | app/p09_bonhiem.py | python3 -m tests.test_p09 |
| frame-p10-tach-dieu-dong | C5.1.3 | app/p10_dieudong.py | python3 -m tests.test_p10 |
| frame-p11-bhxh-hai-truc | C5.1.4 | app/p11_bhxh.py | python3 -m tests.test_p11 |
| frame-p12-suat-an | C5.1.5,C5.3.1,C5.4 | app/p12_suatan.py | python3 -m tests.test_p12 |
| frame-p13-prorata-engine | C5.2,C5.4 | app/p13_prorata.py | python3 -m tests.test_p13 |
| frame-p14-pc-com | C5.3.1 | app/p14_pccom.py | python3 -m tests.test_p14 |
| frame-p15-pc-dien-thoai | C5.3.2 | app/p15_pcdienthoai.py | python3 -m tests.test_p15 |
| frame-p16-pc-xang | C5.3.3 | app/p16_pcxang.py | python3 -m tests.test_p16 |
| frame-p17-pc-di-lai | C5.3.4 | app/p17_pcdilai.py | python3 -m tests.test_p17 |
| frame-p18-pc-ct-ctx | C5.3.5 | app/p18_pcctctx.py | python3 -m tests.test_p18 |
| frame-p19-pc-ctxa-duan-dacthu | C5.3.6,C5.3.7 | app/p19_pcctxa.py | python3 -m tests.test_p19 |
| frame-p20-truy-thu-truy-linh | C4.3 | app/p20_truythu.py | python3 -m tests.test_p20 |
| frame-p21-ot-engine | C5.5 | app/p21_ot.py | python3 -m tests.test_p21 |
| frame-p22-khoa-ky | C4.3 | app/p22_khoaky.py | python3 -m tests.test_p22 |
| frame-p23-mat-bao | C6.1 | app/p23_matbao.py | python3 -m tests.test_p23 |
| frame-p24-phe-duyet-audit | C6.2 | app/p24_pheduyet.py | python3 -m tests.test_p24 |
| frame-p25-template0-trinh-ky | C6.3 | app/p25_template0.py | python3 -m tests.test_p25 |
| frame-p26-template2-master | C6.3 | app/p26_template2.py | python3 -m tests.test_p26 |
| frame-p27-bao-cao-hr-treo | C6.4,C6.5 | app/p27_baocao_hr.py | python3 -m tests.test_p27 |
| frame-p28-ui-serve | C3,C8 | app/p28_ui.py | python3 -m tests.test_p28 |
