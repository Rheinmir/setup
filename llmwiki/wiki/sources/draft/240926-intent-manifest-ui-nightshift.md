---
type: draft
title: "240926-intent-manifest-ui-nightshift"
status: approved
tags: [propose, nightshift, intent-engine, overnight-loop, decision-log]
timestamp: 2026-09-24
task: T-260924-01
---

# 240926 — Giao một việc, một phiên hỏi, closebox, sáng đọc báo cáo: intake + đêm tự quyết cho nightshift

**Status:** approved (bản 3, người dùng duyệt ngày 24/09/2026)

**Sequence diagram:** [240926-intent-manifest-ui-seq.html](../../../html/240926-intent-manifest-ui-seq.html)

## What

Người dùng giao **một việc** bằng lời thường trong agent terminal (Claude Code, Codex). Intent engine tự chạy một **graph research** trên nguồn local và web để điền mọi thứ tra được, rồi chỉ hỏi những điều thật sự cần, gói trong **một phiên hỏi cỡ khoảng 30 phút công sức của người** (thước định cỡ, không phải đồng hồ). Người dùng gõ **closebox**: đó là lời duyệt duy nhất, có hiệu lực trong giới hạn của một **giấy phép** cấp trước. Qua đêm, khi gặp ngã rẽ, hệ **tự quyết** (được nới phạm vi file, không bao giờ được đụng bộ nghiệm thu) và ghi từng quyết định ra hai nơi: `decisions.jsonl` cho máy và `decisions.html` giải thích bằng lời thường cho người. Sáng ra người dùng chỉ đọc **báo cáo tiếng người** (`report.html`); thấy điều đáng ngờ thì mở lại các quyết định đêm qua. Manifest vẫn là hợp đồng máy đọc giữa intake và engine, nhưng người dùng không phải đọc nó.

## Luồng chính của người dùng

1. **Giao việc**: gõ một câu trong Claude Code hoặc Codex. Agent gọi `intake_create`.
2. **Research tự chạy**: intake dựng một graph research (bản đồ repo, lịch sử git, tài liệu và llmwiki, quyết định và báo cáo các đêm trước, tra cứu web cho thư viện và API) và điền các trường có nguồn. Người dùng không làm gì ở bước này.
3. **Một phiên hỏi**: intake gom mọi điều thật sự chặn việc thành một bảng câu hỏi bằng lời thường. "Khoảng 30 phút" là thước để định cỡ tổng số câu, không phải giới hạn thời gian: không có đồng hồ, người dùng trả lời lúc nào cũng được. Câu vụn (đặt tên, chi tiết cài đặt, lựa chọn đảo được dễ) máy tự quyết và ghi lại thành "quyết định trước giờ chạy".
4. **Closebox**: người dùng gõ `closebox`. Intake dựng manifest, chạy preflight, kiểm giấy phép, rồi khởi động run. Vượt giấy phép thì không chạy và nói rõ vượt ở đâu.
5. **Đêm tự quyết**: mỗi ngã rẽ trong lúc chạy thành một bản ghi quyết định: tình huống, các phương án, phương án đã chọn, lý do bằng lời thường, ảnh hưởng, có đảo ngược được không. Nới phạm vi file được phép và luôn được ghi; sửa bộ nghiệm thu hay vùng bảo vệ thì không bao giờ.
6. **Sáng nghiệm thu**: người dùng đọc `report.html`: xong gì, chưa xong gì, cần xem gì, các "mùi" đáng ngờ. Mỗi mùi dẫn tới đúng quyết định trong `decisions.html` và đúng đoạn diff.

## Context

- PRD nguồn: `llmwiki/raw/prd/Reprise-Intent-Engine-Product-Grade-PRD.md` ([[230926-reprise-intent-engine-prd]]): §3.1 bất biến (INV-02 tách nguồn, INV-03 không suy quyền từ ý định, INV-04 unknown phải gắn blocker, INV-13 ready không có nghĩa là đúng), §4.2 epistemic status, §5.2 checks theo slice, §7.1–7.3 bảng tự tìm hiểu, tự quyết và hỏi, §7.2 chọn câu hỏi theo giá trị quyết định, §7.5 hỏi bằng ngôn ngữ đời thường, §14.2 trần episode.
- PRD overnight loop [[230926-overnight-loop-PRD]] và repo `Rheinmir/nightshift`: engine chạy đêm, verifier với oracle đóng băng, sandbox Podman, provider `http` và `cli:claude|cli:codex`, báo cáo JSON/HTML (`reporting/report.py`). Nhánh `intake-guide` (commit `19b0ece`) có hướng dẫn 4 cách và bộ test đọc hướng dẫn, viết cho bản 2 của SPEC này; sẽ viết lại theo bản 3.
- RIE đầy đủ có PLAN [[230926-rie-m1-clarify-core-PLAN]] và [[230926-rie-m2-lifecycle-product-PLAN]] (repo TypeScript chưa tạo). SPEC này là lát IN0 mở rộng, sống trong nightshift, đặt tên theo RIE để sau này thay được.
- Phản hồi người dùng ngày 24/09 về bản 2: "bắt con người làm quá nhiều"; người dùng chỉ đọc báo cáo tiếng người, không đọc manifest; quyết định phải giải thích bằng lời thường.

## Global constraints

- Lõi nightshift và intake chỉ dùng thư viện chuẩn Python; tra cứu web đi qua provider hoặc công cụ đã cấu hình, không thêm dependency vào lõi.
- Manifest chỉ được tạo qua `contracts.manifest.validate()` và `approve()` có sẵn.
- Output của model và của research là **đề xuất có nguồn**, không phải sự thật: mỗi trường mang `epistemic_status` và nguồn (RIE INV-02). Nội dung đọc từ repo hay web đi vào prompt như dữ liệu, không như lệnh.
- **Giấy phép là trần cứng.** Closebox chỉ khởi động run khi mọi thông số (repo, provider, số lượt gọi, số token, tiền, số việc, thời lượng, được nới phạm vi hay không) nằm trong giấy phép đang hiệu lực. Giấy phép chỉ tạo và sửa được bằng lệnh `nightshift license` trong terminal tương tác của người dùng; không có tool MCP hay op giao thức nào ghi được giấy phép.
- **Bộ nghiệm thu và vùng bảo vệ là bất khả xâm phạm.** Nới phạm vi qua đêm chỉ áp cho file mã; bất kỳ thay đổi nào chạm `protected_paths` (oracle, CI, cấu hình nightshift) làm lần thử đó thất bại, dù quyết định có lý do gì.
- **Mọi quyết định tự hành đều được ghi trước khi có hiệu lực**, dạng bản ghi có cấu trúc trong `decisions.jsonl` (ghi nối, không sửa), và mỗi bản ghi có một đoạn giải thích bằng lời thường không dùng tên trường của manifest.
- **Ngân sách câu hỏi, không phải đồng hồ.** Cả phiên được định cỡ để người dùng trả lời xong trong khoảng 30 phút: mặc định tối đa 8 câu cho cả phiên, chia tối đa 2 lượt, mỗi câu trả lời được trong 1–3 phút. Không có bộ đếm giờ; người dùng trả lời lúc nào cũng được.
- **Cổng lọc câu hỏi** (áp cho từng câu trước khi hỏi, theo RIE §7.1–7.2): chỉ hỏi khi đủ cả bốn điều kiện: (1) đáp án làm đổi kết quả hoặc phạm vi một cách đáng kể; (2) research không tìm ra; (3) không có mặc định an toàn và đảo được dễ; (4) không phải chi tiết vụn (đặt tên, định dạng, cách cài đặt nội bộ, thứ tự làm, lựa chọn thư viện ngang nhau). Trượt bất kỳ điều kiện nào thì máy tự quyết và ghi thành quyết định trước giờ chạy, kèm lý do vì sao không hỏi.
- Vượt ngân sách thì máy **không hỏi thêm** mà xếp hạng theo giá trị quyết định, hỏi các câu đứng đầu, tự quyết phần còn lại với nhãn "máy tự quyết thay vì hỏi" để báo cáo sáng đưa lên đầu.
- Research có trần: thời gian tối đa 10 phút, số lần đọc nguồn và số truy vấn web có hạn trong giấy phép; web chỉ đi tới danh sách miền cho phép.
- Không sửa engine chạy đêm theo cách làm đổi hành vi hiện có; phần mới (điểm quyết định, báo cáo tiếng người) là phần thêm. Toàn bộ test hiện có của nightshift phải còn xanh; CI hai job phải xanh.
- Trang HTML (báo cáo, quyết định, web) theo sàn design của framework: toggle sáng/tối, font nhúng, qua cổng tĩnh và cổng chạy thật, đọc được ở 375px.

## Non-goals

- Không xây RIE đầy đủ (IN1): không nhiều người dùng, không handoff sang Graph Engine, không Evolve.
- Không nhận giọng nói, ảnh, OCR.
- Không để người dùng đọc hay sửa manifest trong luồng thường; manifest chỉ hiện ở mục "chi tiết kỹ thuật".
- Không cho quyết định đêm sửa bộ nghiệm thu, vùng bảo vệ hay giấy phép.
- Không gửi thông báo đẩy (điện thoại, chat) ở bản này; báo cáo nằm sẵn khi người dùng mở.

## Approaches

| # | Phương án | Được | Mất |
|---|---|---|---|
| A | **Intake + đêm tự quyết trong nightshift**: research graph và phiên hỏi ở intake; điểm quyết định và báo cáo tiếng người là phần thêm của engine; closebox giới hạn bằng giấy phép | Đúng luồng người dùng; tái dùng engine, verifier, sandbox, provider có sẵn | Engine phải thêm khái niệm "điểm quyết định" và nới phạm vi, là phần mới có rủi ro |
| B | **Giữ bản 2** (nhiều cổng duyệt, người đọc manifest) rồi thêm báo cáo | Ít thay đổi engine | Trái đúng phản hồi của người dùng: quá nhiều thao tác, phải đọc thứ của máy |
| C | **Không tự quyết ban đêm**: gặp ngã rẽ là gác việc tới sáng | An toàn nhất | Sáng ra phần lớn việc còn treo; mất lý do tồn tại của vòng chạy đêm |

**Chọn A.** B mâu thuẫn trực tiếp với phản hồi ngày 24/09. C an toàn nhưng làm vòng chạy đêm vô nghĩa với việc có ngã rẽ. A giữ an toàn bằng ba thứ không thương lượng: giấy phép là trần cứng, bộ nghiệm thu bất khả xâm phạm, và mọi quyết định được ghi trước khi có hiệu lực.

## Affected

| File / Symbol | Thay đổi |
|---|---|
| `nightshift/src/nightshift/intake/` (mới) | case store, research graph, brief, câu hỏi, compile, license, closebox, protocol |
| `nightshift/src/nightshift/intake/bindings/` (mới) | MCP stdio (chính), CLI JSON, hộp thư file, HTTP |
| `nightshift/src/nightshift/decisions/` (mới) | `DecisionRecord`, ghi nối `decisions.jsonl`, chính sách nới phạm vi, render `decisions.html` |
| `nightshift/src/nightshift/providers/base.py` | `ResultEnvelope` thêm trường tuỳ chọn `decisions[]` (không đổi hành vi khi thiếu) |
| `nightshift/src/nightshift/workspace/git_candidate.py` | thêm chế độ "nới phạm vi có log": file ngoài `allowed_paths` hợp lệ khi có quyết định tương ứng và giấy phép cho phép; `protected_paths` không đổi |
| `nightshift/src/nightshift/reporting/` | thêm `report.html` tiếng người (bản JSON hiện có giữ nguyên) |
| `nightshift/src/nightshift/cli.py` | thêm `intake`, `license`, `closebox` (chỉ thêm lệnh) |
| `nightshift/docs/intake-guide.md`, `tests/intake/` | viết lại theo bản 3 |

## Risks

- Nới phạm vi làm tăng khả năng "mùi" (sửa file không liên quan). Giảm bằng: mọi file ngoài phạm vi phải có quyết định kèm lý do, báo cáo sáng liệt kê riêng các file này đầu tiên, giấy phép có thể tắt nới phạm vi theo repo.
- Closebox gõ trong phiên agent nghĩa là agent về lý thuyết tự closebox được. Chấp nhận có chủ ý (quyết định người dùng 24/09); giới hạn bởi giấy phép, và giấy phép chỉ ghi được từ terminal tương tác của người.
- Research web có thể kéo nội dung độc hại vào prompt. Giảm bằng: nội dung web chỉ là dữ liệu có nguồn, danh sách miền cho phép, không bao giờ thực thi mã lấy từ web ở bước intake.
- Quyết định đêm giải thích bằng lời thường có thể nghe hợp lý mà sai. Giảm bằng: mỗi quyết định kèm bằng chứng máy (diff, lệnh, kết quả test) để người đối chiếu, không chỉ lời giải thích.
- Cổng lọc có thể lọc quá tay (tự quyết một điều lẽ ra nên hỏi) hoặc lỏng tay (hỏi câu vụn). Giảm bằng: mỗi quyết định trước giờ chạy ghi rõ vì sao không hỏi; báo cáo sáng có mục "máy tự quyết thay vì hỏi"; SC-002 đo tỷ lệ câu vụn trên bộ việc mẫu, và các lần người dùng sửa quyết định trước giờ chạy được đếm để chỉnh cổng.

## Plan

- [ ] **T1 — Case store + sự kiện:** IntentCase, InputEvent, IntentAtom (`user_asserted | observed | inferred | proposed_default | unknown`), Decision; sổ `events.jsonl` ghi nối, projection dựng lại từ sổ; idempotent theo `client_key`.
- [ ] **T2 — Graph research:** một DAG nhỏ các nút research chạy theo lớp: bản đồ repo, lịch sử git của vùng liên quan, README/docs/llmwiki, quyết định và báo cáo các đêm trước, tra cứu web (tài liệu thư viện, API) qua danh sách miền cho phép. Mỗi phát hiện là một atom có nguồn; trần thời gian và số lần đọc trong giấy phép; nút lỗi không làm hỏng cả graph.
- [ ] **T3 — Soạn brief:** từ atom, dựng bản nháp các việc (mục tiêu, file liên quan, lệnh baseline, tiêu chí xong, rủi ro) bằng reasoning của agent (`case.propose`) hoặc model của hệ thống; qua cùng schema và nhãn nguồn.
- [ ] **T4 — Phiên hỏi có ngân sách:** readiness từng việc; mỗi câu ứng viên qua cổng lọc bốn điều kiện; câu vụn hoặc tự giải được thì tự quyết và ghi thành "quyết định trước giờ chạy" kèm lý do không hỏi; các câu còn lại xếp theo giá trị quyết định, gom tối đa 2 lượt, cả phiên tối đa 8 câu (định cỡ khoảng 30 phút công sức), lời thường, có "để hệ thống đề xuất"; vượt ngân sách thì tự quyết phần đuôi với nhãn "máy tự quyết thay vì hỏi". Không có bộ đếm giờ.
- [ ] **T5 — Compile + preflight mở rộng:** dựng manifest bằng code tất định; tách **baseline** (test hiện có, phải xanh) khỏi **tiêu chí xong** (bộ nghiệm thu, được chụp làm oracle); preflight chạy baseline và chạy thử tiêu chí xong (phải chạy được và phải đỏ đúng chỗ, để bắt bộ nghiệm thu hỏng từ trước).
- [ ] **T6 — Giấy phép + closebox:** `nightshift license set|show` ghi giấy phép (repo, provider, trần gọi/token/tiền/việc/thời lượng, nới phạm vi bật/tắt, miền web) chỉ từ terminal tương tác; op `case.closebox` so manifest với giấy phép, rồi `approve()` + `start` tách tiến trình; vượt thì từ chối và nói vượt ở đâu bằng lời thường.
- [ ] **T7 — Điểm quyết định ban đêm:** worker nêu ngã rẽ qua `decisions[]` trong ResultEnvelope (hoặc file `decisions.json` trong thư mục attempt); engine kiểm từng bản ghi (có phương án, có lý do, có ảnh hưởng, đảo được không), ghi nối `decisions.jsonl` trước khi chấp nhận candidate; nới phạm vi file hợp lệ khi có quyết định tương ứng và giấy phép cho phép; chạm vùng bảo vệ luôn thất bại.
- [ ] **T8 — Báo cáo tiếng người:** `report.html` (một trang: kết quả chung, từng việc xong/chưa xong và vì sao, danh sách "mùi" cần xem đầu tiên, chi phí, cách xem diff) và `decisions.html` (mỗi quyết định: tình huống, đã chọn gì, vì sao, phương án bị bỏ, ảnh hưởng, đảo được không, bằng chứng); cả hai không dùng tên trường của manifest trong phần chính; manifest nằm ở mục "chi tiết kỹ thuật" thu gọn.
- [ ] **T9 — Giao thức + CLI JSON + hộp thư file:** lõi `nightshift.intake/1` (thêm `case.research`, `case.closebox`, `run.report`), response chung; binding CLI và hộp thư cho tự động hoá.
- [ ] **T10 — MCP (cách chính):** `nightshift intake mcp` stdio, các tool `intake_create`, `intake_status`, `intake_answer`, `intake_propose`, `intake_closebox`, `intake_report`; không có tool ghi giấy phép.
- [ ] **T11 — Web xem báo cáo + phiên hỏi:** HTTP binding phục vụ `report.html`, `decisions.html` và bảng câu hỏi của phiên; ghép thiết bị bằng mã một lần; tunnel `cloudflared` riêng để mở từ điện thoại.
- [ ] **T12 — E2E và hướng dẫn:** viết lại `docs/intake-guide.md` và `tests/intake/` theo bản 3; e2e: một câu giao việc → research → phiên hỏi có câu trả lời giả → closebox trong giấy phép → run có một quyết định nới phạm vi → `report.html` và `decisions.html` đúng; e2e chặn: vượt giấy phép không chạy, chạm bộ nghiệm thu thất bại.

## Requirements (FR)

- **FR-001**: Người dùng PHẢI giao được việc bằng một câu lời thường trong Claude Code hoặc Codex, không cần biết cấu trúc manifest.
- **FR-002**: Intake PHẢI tự chạy graph research trên nguồn local (code, git, docs, llmwiki, báo cáo và quyết định cũ) và web trong danh sách miền cho phép, và điền mọi trường tra được kèm nguồn.
- **FR-003**: Intake PHẢI cho mỗi câu ứng viên qua cổng lọc bốn điều kiện (đổi kết quả đáng kể, research không tìm ra, không có mặc định an toàn đảo được, không phải chi tiết vụn) trước khi hỏi; câu trượt cổng PHẢI được tự quyết và ghi thành quyết định trước giờ chạy kèm lý do không hỏi.
- **FR-003b**: Cả phiên hỏi PHẢI nằm trong ngân sách mặc định 8 câu, tối đa 2 lượt, bằng lời thường; vượt ngân sách thì PHẢI hỏi các câu có giá trị quyết định cao nhất và tự quyết phần còn lại với nhãn riêng. Phiên hỏi KHÔNG có giới hạn thời gian.
- **FR-004**: Mỗi trường PHẢI mang `epistemic_status` và nguồn; không trường nào do máy suy được gắn là lời người dùng.
- **FR-005**: `closebox` PHẢI là thao tác duy nhất người dùng cần làm sau phiên hỏi; nó dựng manifest, chạy preflight, kiểm giấy phép và khởi động run.
- **FR-006**: Closebox PHẢI từ chối khi bất kỳ thông số nào vượt giấy phép, và nói bằng lời thường vượt ở đâu.
- **FR-007**: Giấy phép PHẢI chỉ ghi được bằng `nightshift license` trong terminal tương tác; không op giao thức hay tool MCP nào ghi được giấy phép.
- **FR-008**: Preflight PHẢI kiểm baseline xanh và kiểm tiêu chí xong chạy được và đang đỏ đúng chỗ.
- **FR-009**: Qua đêm, mọi ngã rẽ hệ tự quyết PHẢI thành một bản ghi quyết định ghi nối vào `decisions.jsonl` trước khi có hiệu lực, gồm tình huống, phương án, phương án chọn, lý do lời thường, ảnh hưởng, đảo ngược được hay không, bằng chứng.
- **FR-010**: Nới phạm vi file PHẢI hợp lệ chỉ khi có bản ghi quyết định tương ứng và giấy phép cho phép; thay đổi chạm `protected_paths` PHẢI luôn làm lần thử thất bại.
- **FR-011**: Sau run, hệ PHẢI sinh `report.html` và `decisions.html` bằng lời thường, không dùng tên trường của manifest trong phần chính; mỗi "mùi" trong báo cáo PHẢI dẫn tới đúng quyết định và đúng đoạn diff.
- **FR-012**: Báo cáo PHẢI liệt kê đầu tiên: việc chạy với mặc định chưa được xác nhận, file ngoài phạm vi ban đầu, quyết định không đảo ngược được.
- **FR-013**: Mọi thao tác PHẢI đi qua lõi giao thức `nightshift.intake/1`; MCP, CLI JSON, hộp thư file và HTTP chỉ dịch vào/ra.
- **FR-014**: Hướng dẫn `docs/intake-guide.md` PHẢI là thước nghiệm thu chạy được: mỗi bước có mã, lệnh và kết quả phải thấy, và bộ `tests/intake/` đọc thẳng file đó.

## Success criteria (SC)

- **SC-001**: Từ lúc gõ câu giao việc tới lúc closebox, người dùng chỉ làm hai loại thao tác: trả lời câu hỏi và gõ closebox; công sức trả lời vào khoảng 30 phút trở xuống với việc cỡ một buổi làm (thước tham khảo, không phải giới hạn).
- **SC-002**: Trên 10 việc mẫu, số câu hỏi trung bình không quá 5; không câu nào hỏi điều research đã tìm được; và một người review độc lập đánh giá không quá 1 câu trong cả bộ là "vụn, lẽ ra máy tự quyết được".
- **SC-003**: Sáng hôm sau, người dùng hiểu kết quả đêm qua chỉ bằng `report.html` trong không quá 5 phút, không phải mở manifest hay log.
- **SC-004**: Mọi quyết định đêm qua đọc được bằng lời thường bởi người không biết cấu trúc manifest; 10 quyết định mẫu được một người ngoài dự án hiểu đúng lý do.
- **SC-005**: Không có run nào vượt giấy phép, và không lần thử nào sửa bộ nghiệm thu mà vẫn được tính là xong.
- **SC-006**: Mỗi "mùi" trong báo cáo dẫn người dùng tới đúng quyết định và đúng diff trong một cú bấm.

Bằng chứng tầng máy: bộ `tests/intake/` đọc hướng dẫn bản 3; e2e với provider giả có quyết định nới phạm vi; test chặn vượt giấy phép và chạm vùng bảo vệ; kiểm HTML báo cáo bằng hai cổng của framework và Playwright ở 375px; kiểm từ vựng báo cáo không chứa tên trường manifest trong phần chính.

## Assumptions

- Closebox gõ ngay trong agent, giới hạn bằng giấy phép (quyết định người dùng 24/09); rủi ro agent tự closebox được chấp nhận có chủ ý.
- Qua đêm được nới phạm vi file có ghi log (quyết định người dùng 24/09); bộ nghiệm thu và vùng bảo vệ không bao giờ nằm trong phạm vi được nới (default, ranh giới an toàn máy chọn).
- Research đọc nguồn local và web (quyết định người dùng 24/09); web chỉ qua danh sách miền cho phép, mặc định gồm tài liệu chính thức của ngôn ngữ và thư viện mà repo dùng (default).
- "30 phút" là thước định cỡ công sức trả lời, không phải đồng hồ (người dùng chốt 24/09); ngân sách mặc định 8 câu cả phiên, tối đa 2 lượt (default, cấu hình được trong giấy phép).
- Research mặc định tối đa 10 phút (default).
- Giấy phép mặc định khi tạo lần đầu: 1 repo, provider `cli:claude`, 40 lượt gọi mỗi đêm, 6 việc, 8 giờ, nới phạm vi bật, không tiền với subscription (default).
- Deadline mặc định 6 giờ sáng hôm sau theo giờ Asia/Ho_Chi_Minh (default).
- Truy cập từ điện thoại qua tunnel `cloudflared` riêng + ghép thiết bị bằng mã một lần (giữ từ bản 2).
- Web UI ở bản này chủ yếu để đọc báo cáo và trả lời phiên hỏi từ xa; giao việc chính vẫn ở agent terminal (default).

## Agent Task Assignment

| Task | Agent (CLI) | Lý do chọn | Status |
|---|---|---|---|
| T1 | claude-code | Contract nền cho mọi task sau | pending |
| T2 | claude-code | Research đọc repo và web: ranh giới dữ liệu và prompt injection | pending |
| T3 | claude-code | Schema brief và nhãn nguồn, dễ sai tinh vi | pending |
| T4 | claude-code | Chính sách hỏi quyết định trải nghiệm chính | pending |
| T5 | claude-code | Gọi validate/preflight có sẵn, thêm kiểm bộ nghiệm thu | pending |
| T6 | claude-code | Giấy phép là trần an toàn duy nhất của closebox | pending |
| T7 | claude-code | Sửa engine chạy đêm: điểm quyết định và nới phạm vi | pending |
| T8 | claude-code | Báo cáo tiếng người là thứ người dùng thực sự đọc | pending |
| T9 | claude-code | Lõi giao thức dùng chung cho mọi binding | pending |
| T10 | claude-code | MCP viết tay bằng stdlib, cần khớp đặc tả | pending |
| T11 | claude-code | Web, đăng nhập, tunnel: đường vào từ internet | pending |
| T12 | claude-code | Hướng dẫn là thước nghiệm thu; e2e xuyên suốt | pending |

Tất cả giao claude-code vì mỗi task chạm một ranh giới tin cậy hoặc chính trải nghiệm người dùng đã chốt; không có task thuần render.

## Render brief

- **T1:** Agent → Protocol case.create (add) · Store ghi nối (add) · client_key trùng trả case cũ (add).
- **T2:** Protocol → Research graph (add) · đọc repo/git/docs (add) · tra web miền cho phép (add) · miền lạ bị chặn (block).
- **T3:** Research → Brief (add) · Agent case.propose (add) · schema sai (block).
- **T4:** Brief → Readiness (add) · cổng lọc câu vụn (add) · câu vụn tự quyết + ghi lý do (add) · một bảng câu hỏi trong ngân sách (add).
- **T5:** Compile → validate() (legacy) · preflight baseline xanh (legacy) · tiêu chí xong đỏ đúng chỗ (add) · bộ nghiệm thu hỏng (block).
- **T6:** Người dùng license set ở terminal (add) · Agent intake_closebox (add) · so giấy phép (add) · vượt giấy phép (block).
- **T7:** Worker nêu ngã rẽ (add) · Engine ghi decisions.jsonl trước (add) · nới phạm vi có quyết định (add) · chạm vùng bảo vệ (block).
- **T8:** Engine → report.html (add) · decisions.html (add) · mùi dẫn tới quyết định và diff (add).
- **T9:** Agent → CLI JSON / hộp thư (add) · Protocol (add).
- **T10:** Agent → MCP tools (add) · không có tool ghi giấy phép (block).
- **T11:** Điện thoại → Tunnel → Web (add) · đọc báo cáo, trả lời phiên hỏi (add) · không phiên (block 401).
- **T12:** Hướng dẫn → test đọc hướng dẫn (add) · e2e (add).

## Self-review

1. **Phủ yêu cầu:** giao một việc → T1/T10; graph research tự đổ đầy thông tin → T2/T3; chỉ hỏi điều cần, không hỏi câu vụn, cỡ khoảng 30 phút công sức → T4 (cổng lọc + ngân sách, không đồng hồ); closebox → T6; chạy qua đêm → T5/T6; quyết định đêm ghi file máy và HTML cho người → T7/T8; báo cáo sau luồng, sáng chỉ nghiệm thu qua báo cáo → T8; quyết định giải thích bằng lời thường, người không đọc manifest → FR-011, SC-004; mở lại quyết định khi thấy mùi → FR-011/FR-012, SC-006.
2. **Placeholder:** không còn; ba quyết định mới (closebox, nới phạm vi, nguồn research) đã có câu trả lời của người dùng ngày 24/09.
3. **Nhất quán tên:** thống nhất `closebox`, `giấy phép` (`nightshift license`), `decisions.jsonl`, `decisions.html`, `report.html`, `graph research`, `phiên hỏi`, `quyết định trước giờ chạy`, `nightshift.intake/1`.

## Origin

- **Draft:** `wiki/sources/draft/240926-intent-manifest-ui-nightshift.md`
- **Nguồn:** `llmwiki/raw/prd/Reprise-Intent-Engine-Product-Grade-PRD.md` + repo `Rheinmir/nightshift` @ `19b0ece` (nhánh `intake-guide`) + phản hồi người dùng 24/09 (ba lượt)
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
