---
type: draft
title: "Review orca-graph v3 trước khi ship — hai reviewer độc lập, 5 lỗi CAO và 11 lỗi VỪA đều tái hiện được, đã sửa kèm test hồi quy"
status: done
tags: [review, orca-graph, repo-split, install, regression-test]
timestamp: 2026-09-20
---

# Review orca-graph v3 (20/09/2026)

## Cách review

Bản v3 được viết trong một phiên, nên người viết không được tự chấm. Hai reviewer chạy trong context riêng, không nhận lập luận của người viết, chỉ nhận đường dẫn code, bản v2 để so, PRD nguồn và danh sách chỗ cần soi. Luật giao cho cả hai: chỉ báo thứ đã tái hiện được bằng lệnh thật trong thư mục tạm với `HOME` cô lập, thứ chỉ nghi thì ghi "chưa tái hiện". Reviewer thứ nhất soi engine (`engine/orca-graph.py`, `graph-viz.py`, ma trận VT). Reviewer thứ hai soi phần tách repo: shim, `install.sh` của hai repo, test cài đặt và tài liệu.

Trước review, bộ test có 45 ca và đều xanh. Không ca nào chạm tới các lỗi dưới đây. Đây là lý do review độc lập nằm trong PLAN thành một node riêng (t11) chứ không gộp vào bước verify của từng task.

## Lỗi mức CAO (5) — đã sửa hết

| # | Lỗi | Tái hiện | Sửa | Test |
|---|---|---|---|---|
| C1 | `add-node --blocks` sửa nhầm dòng `**Depends:**` nằm trong code fence, vẫn báo thành công, cạnh không được tạo | Task có khối ```` ```md ```` chứa `**Depends:** Task 0`, chạy `--blocks t1` → rc 0 nhưng `t1.deps == []` | `plan_struct()` cho add-node nhìn PLAN đúng như parser; sau khi chèn kiểm lại cạnh `--blocks`, không khớp thì không ghi | `test_review_C1_V7_*` |
| C2 | Hai `add-node` song song đè mất task của nhau, cả hai đều in `+ t2` | 8/8 lần chạy song song chỉ còn một task | bọc trong `admission_mutex` | `test_review_C2_*` (4 process, đủ 4 task, `plan_version` = 5) |
| C3 | Parser nuốt im lặng token Depends không hiểu (`Task 1 (data) — vì cần schema`, `Task 1 và Task 2`, `Task 9` không tồn tại) và vẫn gắn `deps_conf = chắc` | 7 dạng viết đều ra `deps == []` | token không resolve được là lỗi `build`; tách theo `,` và `;`; reason nhận cả `effect-order`; dep xuyên graph phải khớp `<gid>/<tid>` | `test_review_C3_*` |
| C4 | `run` publish kết quả của plan cũ vào plan mới khi replan xảy ra giữa lúc agent chạy; ma trận VT ghi VT-27 `covered` là nhận vơ một nửa | `run … -- sleep 3`, sau 1,2 giây sửa PLAN rồi `build` → node vẫn `done`, `fresh = current` | `run` nhớ `plan_version` lúc dispatch; lệch thì STALE, node về `ready` | `test_VT27_review_C4_*` |
| C5 | `install.sh` của repo engine reset mất commit chưa push và ép bản clone đầy đủ thành shallow. Trên máy dev, `~/.orca-graph/repo` là symlink tới bản dev, và option graph của framework mặc định tick, nên lần cài framework kế tiếp sẽ xoá việc đang làm | clone → commit local → chạy install → commit biến khỏi nhánh, `is-shallow = true` | symlink thì không đụng; bản đầy đủ dùng `fetch` + `merge --ff-only` và dừng khi đi trước remote; bản shallow có hơn một commit thì dừng | hai ca mới trong `tests/install-test.sh` |

C5 là lỗi nguy hiểm nhất vì nó mất dữ liệu và chỉ chưa nổ do remote chưa tồn tại lúc review.

## Lỗi mức VỪA (11) — đã sửa hết

Phía engine: lease hết ở graph A vẫn chặn claim của graph B vì reaper chỉ quét graph đang gọi (nay `lock` và `next` quét cả store); `unlock` tay để nguyên state `locked` nên giữ claim vĩnh viễn (nay đưa về `unknown`); mutex admission kiểu O_EXCL cộng mtime có TOCTOU khi phá khoá stale, đo được 1 lần chồng lấn trên 150 vòng với 6 process (nay dùng `flock`, không còn logic stale); `capacity:N` phụ thuộc thứ tự lock và `shared` lách được quota (nay N là kích thước pool, lấy giá trị nhỏ nhất, mọi holder chiếm slot, `capacity:0` bị từ chối); `audit-edges` đề xuất bỏ một cạnh data thật khi downstream dùng output của upstream mà không viết chữ "Task N" (nay so thêm file và output trong Consumes, Verify, QC); `add-node` cho chèn cấu trúc PLAN qua field có xuống dòng (nay từ chối); `add-node` chèn sai chỗ và cấp sai id khi có `### Task` mẫu trong fence sau task cuối (cùng bản sửa với C1); graph-viz chưa escape dep id và kind (nay escape, parser cũng chặn bằng regex).

Phía cài đặt: shim không biết `ORCA_GRAPH_INSTALL_DIR` nên cài vào thư mục tuỳ biến thì framework báo thành công mà `/orca-graph` trả rc 3 (shim nay đọc biến này, installer in lời nhắc); nhánh không có git dựng URL raw sai khi `ORCA_GRAPH_REPO` không phải URL GitHub (nay báo lỗi rõ và dừng); test option cài đặt clone engine từ HEAD nên sửa chưa commit không được test mà vẫn xanh im lặng (nay in cảnh báo; CI cài engine trước khi chạy để không rơi vào SKIP).

## Lỗi mức THẤP — sửa phần rẻ, phần còn lại ghi nợ

Đã sửa: dep viết lặp gây báo CYCLE giả; `reconcile-items` để lọt dòng lỗi mâu thuẫn, ID lạ, file verdict thiếu và manifest rỗng; `add-node --depends` phân biệt hoa thường; file `mktemp` của installer không được xoá; nhập số quá dài ở checklist làm lộ lỗi thô của `[`; thêm `ORCA_GRAPH_NO_ROOM` để engine chạy độc lập không gọi cockpit của máy thật; tham chiếu chết tới `test_orca_graph.py` trong concept.

Chưa sửa, có lý do: `g["plan"]` vẫn lưu đường tương đối vì `graph.json` được commit vào repo và đường tuyệt đối sẽ lộ máy. Rủi ro ghi nhầm file đã được chặn bằng bước kiểm "PLAN phải khớp graph" trong `add-node`. PLAN `180926-ship-scroll-originals` còn lệnh Verify trỏ tới file test đã chuyển repo; đó là PLAN của việc khác, đã xong, không dispatch lại nên để nguyên. Agent chạy trình cài trong terminal có pty thật sẽ chờ 60 giây ở checklist; đã ghi cách tránh (`--with-graph` hoặc `OVERSTACK_NONINTERACTIVE=1`) vào phần đầu `install.sh`.

## Ma trận VT sau review

VT-06 hạ từ `covered` xuống `partial`: test chỉ chứng minh join của DAG, không có membership seal của PRD §24.2. VT-27 giữ `covered` nhưng nay phủ cả đường `run`. VT-03 thêm ca pool không phụ thuộc thứ tự. Kết quả: 13 `covered`, 2 `partial`, 13 `out_of_scope`; 15/15 kịch bản trong phạm vi pass.

## Số đo sau khi sửa

- Repo engine: 56 test pytest xanh (45 cũ cộng 11 ca `test_review_*`), `evals/run.py --check` rc 0, `tests/install-test.sh` PASS gồm hai ca an toàn mới.
- Repo framework: `medic --ci` 0 fail, `install-graph-option-test.sh` 4/4 (ca TTY chạy dưới pty thật), `test_control_room.py` 4/4, `dot-layout-runtime-test.sh` 6/6, `install-ps1-test.sh` và `install-seed-test.sh` PASS.
- Parser nghiêm đã được thử trên mọi PLAN thật trong `llmwiki/wiki/sources/draft/` kể cả `archive/`: không PLAN nào gãy.

## Những gì reviewer thử mà không thấy lỗi

Hai process `lock` song song cùng claim exclusive, 100 lần, luôn đúng một bên thắng. Tương thích ngược trên 23 file store thật: mọi lệnh cũ và mới chạy trên graph không có field mới, không KeyError. Hiệu năng với 30 graph nhân 12 node có claim: `next` 0,15 giây. Shim: import bằng importlib ra đúng `__file__` và đủ hàm, atlas nạp được graph-viz cạnh shim, `install-harness.sh` copy shim sang máy khách. Checklist cài đặt: nhập bậy đủ kiểu qua pty thật không làm script chết, curl hỏng thì fail-open đúng, không TTY thì không hỏi.

## Origin

- Node t11 của graph `200926-orca-graph-v3` (PLAN `200926-orca-graph-v3-PLAN`).
- Hai reviewer là subagent chạy context riêng trong phiên 20/09/2026; mọi tái hiện nằm trong thư mục tạm, không ghi vào hai repo.
- Bản sửa: repo `Rheinmir/orca-graph` (các test `test_review_*`, `tests/install-test.sh`) và repo `Rheinmir/setup` (shim, `install.sh`, workflow `harness.yml`).
