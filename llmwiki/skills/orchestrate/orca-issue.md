---
name: orca-issue
description: Vòng xử lý SỰ CỐ first-class — dùng khi có bug, lỗi runtime, hành vi sai, "approve treo", regression, incident production. Điều phối triage → repro-first gate (chưa tái hiện được thì CHƯA được sửa) → khoanh vùng (code-graph/impact-check/bisect) → fix qua safe-change với bằng chứng đỏ→xanh → distill kép (wiki incident + failure-flywheel + problem-tree). KHÔNG dùng cho tính năng mới (đó là propose/orca-workflow).
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: orca-issue — vòng xử lý sự cố

Khác vòng làm-tính-năng ở hai chốt cứng: **không tái hiện được thì không sửa**, và **không đỏ→xanh thì không đóng**. Skill này điều phối đồ nghề đã có (impact-check, safe-change, verify-before-commit, failure-flywheel) — không làm lại chúng.

## WHAT

### Purpose và context
- **Purpose:** đưa một sự cố (bug/regression/incident) từ triệu chứng tới fix có bằng chứng đỏ→xanh và tri thức được distill, qua 5 chốt tuần tự không nhảy cóc.
- **Trigger (when to use):**
  - Bug, lỗi runtime, regression, hành vi sai so với mong đợi, incident production.
  - User nói: "lỗi rồi", "bị bug", "chạy sai", "hôm qua còn chạy", "trace lỗi này", "/orca-issue".
- **Non-goals:** KHÔNG dùng khi: yêu cầu tính năng/thay đổi mới → `propose` / `orca-workflow`. Không làm lại đồ nghề có sẵn (impact-check, safe-change, verify-before-commit, failure-flywheel) — chỉ điều phối. Không dọn code lân cận trong vòng sự cố.

### Mental model
`triệu chứng → repro ĐỎ (bằng chứng) → root cause ("nằm ở X vì Y") → fix surgical → repro XANH + verify → commit → distill kép (wiki incident + flywheel + problem-tree)`. Hai chốt cứng: chốt 2 (repro) và chốt 4 (đỏ→xanh).

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | triệu chứng | có | cái gì sai, thấy ở đâu, từ bao giờ; chưa rõ → hỏi user |
| In | log / screenshot / bối cảnh | không | thu ở triage; error message nguyên văn nếu có |
| Out | repro | có | script/test + output ĐỎ đã lưu làm bằng chứng |
| Out | fix + repro XANH + verify pass | có (trừ nhánh không tái hiện được) | commit qua `verify-before-commit` |
| Out | trang wiki incident | có | `llmwiki/wiki/sources/` — triệu chứng, root cause, fix, `## Origin` trỏ commit + repro |
| Out | record failure-flywheel + node problem-tree | có (problem-tree nếu dự án có) | rào chắn cho lần sau |

"Xong" = repro xanh + verify pass + commit + distill (wiki + flywheel).

### Rules và capabilities
- RULE-01 (MUST): **Không repro, không sửa** — mọi fix phải truy được về một bằng chứng đỏ đã lưu. Fix không có repro là fix mò, bị trả lại.
- RULE-02 (MUST): **Không xanh, không đóng** — lời agent không phải bằng chứng; chỉ repro chuyển xanh + verify pass mới được đóng.
- RULE-03 (MUST): **Surgical** — chỉ chạm vùng đã khoanh ở bước 3; thấy code lân cận "muốn dọn" thì ghi chú, không dọn trong vòng sự cố.
- RULE-04 (MUST): **Distill là bắt buộc, không phải lịch sự** — vòng chưa xong khi chưa ghi wiki + flywheel; đây là cách lỗi hôm nay thành rào chắn ngày mai.
- RULE-05 (SHOULD): Sự cố nặng cần nhiều người/agent → escalate sang `orca-workflow` để dispatch, nhưng các chốt 2 và 4 vẫn giữ nguyên.
- RULE-06 (MUST): **Đọc thông báo lỗi NGUYÊN VĂN trước khi đoán** (superpowers systematic-debugging) — error message + stack trace là dữ kiện rẻ nhất; triage mà chưa trích nguyên văn lỗi là đang đoán.
- RULE-07 (MUST): **Một hypothesis một lần** — mỗi vòng chỉ đổi MỘT thứ rồi chạy lại repro; đổi nhiều thứ cùng lúc (shotgun-fix) thì xanh cũng không biết vì sao xanh.
- RULE-08 (MUST): **3 fix liên tiếp thất bại → dừng, nghi ngờ TẦM kiến trúc** — không thử fix thứ 4 cùng cỡ; quay lại bước 3 với giả thuyết to hơn (sai tầng, sai component, sai giả định nền).
- Capabilities: đọc log/code, định vị (code-graph, impact-map, lịch sử VCS), chạy test cục bộ, ghi code qua luồng safe-change, ghi wiki + ledger failure. Không deploy.

### Failure boundaries
- Triệu chứng chưa rõ → **clarify** (hỏi user), không đoán.
- Không tái hiện được (flaky/heisenbug) → **blocked** cho việc sửa: ghi điều kiện đã thử, hạ xuống chế độ giám sát (thêm log/probe).
- Repro còn đỏ sau fix → chưa xong, quay lại bước 3.
- 3 fix liên tiếp thất bại → dừng, nghi tầm kiến trúc, không thử fix thứ 4 cùng cỡ.
- Sự cố nặng cần nhiều người/agent → escalate `orca-workflow` (chốt 2 và 4 giữ nguyên).

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | judgment | triệu chứng, log | Triage: chép triệu chứng 1–2 câu, trích lỗi nguyên văn, phân mức | triệu chứng + mức | chưa rõ → hỏi user |
| W02 | deterministic | triệu chứng | Repro-first GATE: viết script/test, chạy ra ĐỎ, lưu | repro đỏ đã lưu | không tái hiện → B01 |
| W03 | judgment | repro, code-graph, impact-check, git | Khoanh vùng | "root cause nằm ở X vì Y" | — |
| W04 | effect | root cause | Fix qua `safe-change`, chạy lại repro + test dự án + `verify-before-commit` | repro XANH, commit | còn đỏ → W03; 3 lần fail → B02 |
| W05 | effect | commit, repro | Distill kép: wiki incident + failure-flywheel + problem-tree | trang wiki, record, node | chưa distill = chưa xong |

Chi tiết từng bước (nguồn chân lý cho W01–W05) — 5 chốt tuần tự, không nhảy cóc:

1. **Triage** — chép lại triệu chứng bằng 1–2 câu (cái gì sai, thấy ở đâu, từ bao giờ); thu log/screenshot/bối cảnh; phân mức (chặn việc / khó chịu / thẩm mỹ). Chưa rõ triệu chứng → hỏi user, đừng đoán.
2. **Repro-first GATE (chốt cứng #1)** — viết script/test tái hiện lỗi, chạy ra kết quả **ĐỎ** (fail) và lưu lại làm bằng chứng (file test hoặc script + output). **Chưa có repro đỏ thì DỪNG ở đây** — không bàn nguyên nhân, không sửa. Lỗi không tái hiện được (flaky/heisenbug) → ghi rõ điều kiện đã thử, hạ xuống chế độ giám sát (thêm log/probe), không sửa mò.
3. **Khoanh vùng** — dùng đồ nghề định vị thay vì grep mù: code-graph (`get_callers`/`get_symbol_context`), `impact-check` để map ai phụ thuộc vùng nghi vấn, `git bisect`/`git log` khi nghi regression theo thời gian. Kết quả: 1 câu "root cause nằm ở X vì Y".
4. **Fix red→green (chốt cứng #2)** — sửa qua `safe-change` (code dùng chung thì map caller trước), surgical đúng vùng đã khoanh. Chạy lại repro ở bước 2: phải chuyển **ĐỎ → XANH**; chạy thêm test/verify sẵn có của dự án; chốt bằng `verify-before-commit`. Repro còn đỏ = chưa xong, quay lại bước 3 — không được "chắc là được rồi".
5. **Distill kép** — sau khi commit: (a) trang wiki incident vào `llmwiki/wiki/sources/` (triệu chứng, root cause, fix, kèm `## Origin` trỏ commit + repro); (b) record vào `failure-flywheel` để lỗi lặp đủ ngưỡng tự đề xuất rule/skill; (c) dự án có problem-tree (`llmwiki/html/problem-tree.html` hoặc `fdk-problem-tree.html`) → thêm/flip node tương ứng.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | recovery | lỗi không tái hiện được (flaky/heisenbug) | ghi rõ điều kiện đã thử, hạ xuống chế độ giám sát (thêm log/probe), không sửa mò | không có repro đỏ → không sang W03/W04 | W02 khi lỗi xuất hiện lại với dữ kiện mới |
| B02 | recovery | 3 fix liên tiếp thất bại | dừng, nghi ngờ TẦM kiến trúc; quay lại khoanh vùng với giả thuyết to hơn (sai tầng, sai component, sai giả định nền) | không thử fix thứ 4 cùng cỡ | W03 |
| B03 | conditional_required | sự cố nặng cần nhiều người/agent | escalate sang `orca-workflow` để dispatch | chốt 2 và 4 vẫn giữ nguyên | W04 |
| B04 | capability_optional | dự án có problem-tree (`llmwiki/html/problem-tree.html` hoặc `fdk-problem-tree.html`) | thêm/flip node tương ứng ở W05 | không có → skip | W05 |

### Validation và stopping
Chốt 2 và chốt 4 kiểm bằng chạy thật: repro phải ra ĐỎ trước khi sửa và XANH sau khi sửa, cộng test/verify sẵn có. Lời agent không phải bằng chứng. Dừng khi distill xong; trần: 3 fix fail liên tiếp → B02.

### Examples
- **Positive:** "approve treo từ hôm qua" → triage trích lỗi timeout nguyên văn → test repro ĐỎ → `git bisect` chỉ commit đổi lock → fix qua safe-change → repro XANH + `verify-before-commit` → trang incident trong `llmwiki/wiki/sources/` + record failure-flywheel.
- **Boundary/failure:** lỗi chỉ xảy ra 1/50 lần, không repro được → không sửa, ghi điều kiện đã thử, thêm log/probe (B01).
- **Boundary:** user xin "thêm nút export" → không phải sự cố, chuyển `propose` / `orca-workflow`.

## Origin
- **Absorb 2026-07-17 (adapt_mode: dissolve, T-260717-02):** 3 chốt cuối (đọc lỗi nguyên văn · một hypothesis một lần · 3-fail-nghi-kiến-trúc) distill từ `obra/superpowers` (`systematic-debugging` — Iron Law + Four Phases). Các chốt trùng vòng sẵn có (repro-first, root-cause, red→green) KHÔNG absorb lại. Clone sẵn trong scratchpad/superpowers.
