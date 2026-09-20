---
type: concept
title: "Bảng luồng cài đặt và cập nhật overstack — mỗi đường code đi xuống một máy là một ô, mỗi ô có ca test hoặc ghi rõ chưa làm"
status: implemented
tags: [installer, bootstrap, harness-update, orca-graph, repo-role, upgrade-path, test-matrix]
timestamp: 2026-09-20
id: install-update-flows
relations:
  - {rel: touches, path: harness/poc-vendor-neutral/install.sh}
  - {rel: touches, path: harness/scripts/install-harness.sh}
  - {rel: touches, path: harness/scripts/repo_role.py}
  - {rel: touches, path: harness/tests/install-flows-test.sh}
  - {rel: touches, path: harness/scripts/fresh-install-smoke.sh}
  - {rel: relates-to, to: orca-graph}
---

# Bảng luồng cài đặt và cập nhật overstack

Trang này tồn tại vì một sai lầm cụ thể. Ngày 20/09/2026, sau khi tách engine orca-graph sang repo riêng, tôi test đúng một đường — `curl bootstrap | bash` — rồi báo xong. User hỏi lại "cơ chế update qua installer thì sao", và khi liệt kê hết các đường có thể đưa code xuống một máy thì lộ ra nhiều đường chưa ai kiểm, trong đó có đường hỏng thật. Bài học là: **"đã test installer" không có nghĩa gì nếu không nói test ĐƯỜNG nào**. Từ đó mỗi đường là một ô trong bảng dưới, mỗi ô trỏ tới một ca chạy được trong `harness/tests/install-flows-test.sh`, hoặc ghi thẳng là chưa làm và vì sao.

## Hai gốc chung đã sửa

Các ô hỏng không phải chín lỗi rời nhau. Chúng đổ về hai gốc.

Gốc thứ nhất là **shim đi theo nhiều đường, engine chỉ đi theo một**. Ba shim của orca-graph nằm trong `harness/scripts/` và `fdk/tools/` nên mọi đường copy engine xuống global đều mang chúng theo, còn việc kéo engine thật trước đây chỉ nằm ở `poc-vendor-neutral/install.sh`. Bản sửa đặt `ensure_orca_graph` vào đúng chỗ copy shim, tức nhánh `--global` của `install-harness.sh`; `install.sh` chỉ còn giữ phần hỏi user và truyền quyết định xuống bằng `ORCA_GRAPH_SKIP`.

Gốc thứ hai là **không cổng nào khẳng định engine tới nơi**. `fresh-install-smoke.sh`, probe `freshinstall` của `medic` và `/fdk-uat` đều xanh kể cả khi `/orca-graph` trả "chưa cài engine". Bản sửa thêm mục (G) vào smoke: chạy `orca-graph.py --version` qua shim trong HOME của dự án trống, phải ra `orca-graph X.Y.Z`. UAT ghi bước này vào checklist.

Một gốc thứ ba lộ ra khi đang sửa: công cụ **đoán loại repo theo hình dạng thư mục**. Installer chạy nhầm trong repo framework đã ghi đè `harness.yml` và `settings.json`. Bản sửa là nhãn khai báo `repo_role:` trong `.overstack.yaml` (đọc bằng `harness/scripts/repo_role.py`), installer từ chối khi nhãn là `framework`, và `/ship` rẽ luồng theo nhãn.

## A. Cài mới

| Ô | Luồng | Trạng thái | Ca test |
|---|---|---|---|
| A1 | `curl bootstrap \| bash` trong terminal | Đạt: checklist hiện `[x] 1. orca-graph`, Enter là kéo | pty thật, `install-graph-option-test.sh` (c); chạy tay nguyên văn lệnh từ remote 20/09 |
| A2 | cùng lệnh, agent hoặc CI chạy, không terminal | Đạt: không hỏi, kéo luôn | `install-graph-option-test.sh` (b) |
| A3 | `bootstrap --harness-only` | Đạt: module vẫn được kéo, launcher chạy; shim không có vì không cài global | `install-flows-test.sh A3` |
| A4 | `--no-graph`, bỏ tick, `ORCA_GRAPH_SKIP=1` | Đạt: không kéo; shim trả rc 3 kèm một lệnh cài | `install-graph-option-test.sh` (a)(d), `install-flows-test.sh A7` phần A7s |
| A5 | Windows `install.ps1` qua Git Bash hoặc WSL | Một phần: chỉ kiểm ca bỏ module bằng `pwsh` trên macOS; checklist trên Windows thật chưa kiểm | `install-ps1-test.sh` |
| A6 | Dán `00-New-Project.md` cho agent | Chưa kiểm riêng. Agent trong terminal có pty sẽ chờ checklist 60 giây; tránh bằng `--with-graph` hoặc `OVERSTACK_NONINTERACTIVE=1` | — |
| A7 | Gọi thẳng `install-harness.sh --global` | Đạt sau khi sửa gốc 1: shim và engine tới cùng chuyến | `install-flows-test.sh A7` |
| A8 | Chỉ `npx skills add rheinmir/setup#orca` | Chưa làm: có skill `/orca-graph` nhưng không shim lẫn engine. SKILL có ghi lệnh cài engine và đường launcher `~/.orca-graph/bin/orca-graph` | — |
| A9 | Cài riêng engine, không overstack | Đạt | `tests/install-test.sh` ở repo engine |

## B. Cập nhật máy đã cài

| Ô | Luồng | Trạng thái | Ca test |
|---|---|---|---|
| B1 | Máy còn engine v2 (trước khi tách) chạy lại bootstrap | Đạt: 978 dòng thành shim 28 dòng, engine 3.x tới, graph đang dở đọc nguyên state | `install-flows-test.sh B1` (tự bỏ qua trên checkout nông của CI) |
| B2 | Máy đã ở bản hiện tại chạy lại bootstrap | Đạt khi version được bump: global refresh, stamp dự án lên theo | chạy tay 20/09 cho 1.3.110 lên 1.3.111 |
| B3 | `/harness-update` kiểu cũ, tức `install-harness.sh . --self-heal`, trên dự án layout dot | Đã sửa. **Dữ kiện đo được khác dự đoán ban đầu của tôi**: lệnh này không hề đụng global (máy 1.3.109 vẫn 1.3.109, engine cũ nguyên) và còn chép 77 script vào `harness/scripts` của dự án, mọc thêm `llmwiki/` trần. Nay đường per-project dừng rc 5 và in lệnh bootstrap; skill `/harness-update` gọi bootstrap cho layout dot | `install-flows-test.sh B3` |
| B4 | `install-harness.sh --all-subrepos` | Ghi sai ở bảng nháp: tôi từng đoán nó "để lại shim không engine". Đọc code thì nó chỉ nhân cổng pre-push ra các subrepo, không copy engine. Không phải luồng cập nhật engine | — |
| B5 | Engine ra bản mới nhưng harness không bump | Chưa làm: máy khách không có tín hiệu "engine cũ"; engine chỉ được cập nhật khi bootstrap hoặc `--global` chạy lại | — |
| B6 | Thứ đi xuống máy khách đổi NỘI DUNG mà tên không đổi (hook, shim, installer) | Vẫn dựa vào người: `capability-stamp` chỉ băm tên bề mặt. `/ship` RULE mới ghi rõ phải `--update` trong ca này. Đã cháy 20/09: sửa hook R21 sau khi bump 1.3.110 nên máy ở 1.3.110 không nhận | — |
| B7 | Nhắc lệch bản đầu phiên (`harness-integrity`) | Chỉ so version harness, không biết engine | — |

## C. Ca đặc biệt

| Ô | Luồng | Trạng thái | Ca test |
|---|---|---|---|
| C1 | Chạy installer ngay trong repo framework | Đã sửa: dừng rc 3 trước khi ghi bất cứ file nào, cả khi khai nhãn lẫn khi chỉ suy từ `fdk/wiki`; ép bằng `--i-know-this-is-the-framework` | `install-flows-test.sh C1` |
| C2 | Thư mục cài engine là symlink tới bản dev, cây bẩn, hoặc có commit chưa push | Đạt: không bị đụng, không bị ép thành shallow | `tests/install-test.sh` ở repo engine |
| C3 | `ORCA_GRAPH_INSTALL_DIR` tuỳ biến | Một phần: shim đọc được biến nhưng phải export ở mọi phiên | — |
| C4 | Không mạng lúc cài | Đạt fail-open: cài tiếp, in lệnh cài tay. Sau đó không có nhắc lại | curl giả trong review 20/09 |
| C5 | Máy không có git | Có nhánh tải thẳng file engine, chưa chạy thật | — |
| C6 | Cài trong lúc daemon `watch` hoặc node đang chạy | Chưa kiểm | — |
| C7 | `uninstall.sh` | Không đụng `~/.orca-graph`; chưa quyết giữ hay gỡ | — |
| C8 | Hai máy chung một store, engine khác bản | Chiều v3 đọc graph v2: đạt (B1). Chiều ngược: chưa kiểm | — |

## D. Các cổng kiểm

| Ô | Cổng | Trạng thái |
|---|---|---|
| D1 | `medic` probe `freshinstall` | Đạt sau khi sửa gốc 2: gọi `fresh-install-smoke.sh --local`, có mục (G) |
| D2 | `fresh-install-smoke.sh --remote` | Có mục (G); chế độ remote kéo engine từ GitHub thật |
| D3 | `/fdk-uat` | Checklist có bước 5 "module repo riêng tới nơi" |
| D4 | CI `install-graph-option`, `install-flows`, `html-font-lint` | Runner sạch tự cài engine từ remote rồi chạy, không rơi vào SKIP |
| D5 | `ci-local` khi working tree có file lạ | Vẫn chấm nhầm workflow nếu `harness.yml` bị ghi đè. `/ship` RULE-11 yêu cầu chạy gate trên checkout sạch của commit |

## Cách dùng trang này

Khi thêm một đường cài mới, hoặc đổi một đường đang có, việc đầu tiên là thêm hoặc sửa một ô ở đây và một ca trong `install-flows-test.sh`. Khi ai đó nói "đã test installer", câu hỏi đúng là "ô nào". Ô ghi "chưa làm" là nợ có tên, không phải thứ bị quên.

## Origin

- Phiên 20/09/2026, graph `200926-repo-role-ship-flows` (PLAN `llmwiki/wiki/sources/draft/200926-repo-role-ship-flows-PLAN.md`), task 4 đến 8 và task 13.
- Bảng nháp đầu tiên lập trong chat cùng ngày; hai ô B3 và B4 của bản nháp là suy đoán và đã được thay bằng số đo thật ở trang này.
- Sự cố gốc: installer ghi đè `harness.yml` (−202 dòng) và `settings.json` (+67 dòng) của repo framework lúc 11:10:55 ngày 20/09/2026.
