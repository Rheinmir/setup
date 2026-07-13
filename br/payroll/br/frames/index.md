# Frames — Payroll CTD/Unicons (lô đầu)

> Nguồn chân lý: `br/BR.md` (lớp as-is). Test + fixture ground-truth do NGƯỜI viết — code do loop-runner viết.
> Đích cuối: `frame-f99-lap-rap` đối chiếu 30 cột dòng 9 bảng lương thật → **NET_PAY = 189.930.161**.

| frame_id | clause | scope_code | acceptance_test |
|---|---|---|---|
| frame-f01-params | C4.1, C4.2, C4.3, C4.4, C4.5, C4.6 | app/params.py | `python3 -m tests.test_f01` |
| frame-f02-lich-ky-cong | C5.1, C5.2, C5.4 | app/lichky.py | `python3 -m tests.test_f02` |
| frame-f03-cham-cong | C6.1, C6.2, C6.3 | app/chamcong.py | `python3 -m tests.test_f03` |
| frame-f04-luong-chinh | C7.1, C7.2, C7.3, C7.4, C13.5 | app/luong.py | `python3 -m tests.test_f04` |
| frame-f05-suat-an | C8.1, C8.2, C17.4 | app/com.py | `python3 -m tests.test_f05` |
| frame-f06-phu-cap | C8.3, C8.4, C8.5, C8.6, C8.7, C17.4 | app/phucap.py | `python3 -m tests.test_f06` |
| frame-f07-tang-ca | C9.1, C9.2, C9.3 | app/tangca.py | `python3 -m tests.test_f07` |
| frame-f08-thuong-trich-quy | C10.1, C10.2 | app/thuong.py | `python3 -m tests.test_f08` |
| frame-f09-bao-hiem | C4.2, C4.5, C11.1, C11.2, C11.3, C11.4 | app/baohiem.py | `python3 -m tests.test_f09` |
| frame-f10-thue-tncn | C4.4, C4.6, C12.1, C12.2, C12.3 | app/thue.py | `python3 -m tests.test_f10` |
| frame-f11-tong-hop | C13.1, C13.2, C13.3, C13.4, C13.5 | app/tonghop.py | `python3 -m tests.test_f11` |
| frame-f12-engine-dag | C3.1, C3.2, C3.3, C14.1 | app/engine.py | `python3 -m tests.test_f12` |
| frame-f13-adapters | C18.1 | app/adapters.py | `python3 -m tests.test_f13` |
| frame-f14-snapshot-diff | C16.1, C16.2 | app/snapshot.py | `python3 -m tests.test_f14` |
| frame-f15-man-hinh-hr | C15.1, C15.2, C14.1 | app/ui.py | `python3 -m tests.test_f15` |
| frame-f99-lap-rap | C17.1, C17.2, C17.3, C17.6 | app/pipeline.py | `python3 -m tests.test_f99` |
