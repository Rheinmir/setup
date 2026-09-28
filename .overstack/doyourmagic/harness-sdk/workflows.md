# harness-sdk (strands-agents) — workflow đã kiểm chứng

Nguồn: https://github.com/strands-agents/harness-sdk (HEAD `c56b7de`, clone 2026-09-28). Chế độ đặt tên: **mặc định** (`dym-harness-sdk`).

"Harness" của họ là **agent lắp sẵn**: `create_harness()` trả một `strands.Agent` đủ tool/plugin/memory/session/context-offload với giá trị mặc định đã đo benchmark. Overstack thì là **lớp quản trị bao quanh** agent có sẵn (Claude Code): luật, hook, cổng kiểm, wiki, cùng hệ đo. Hai thứ cùng tên nhưng khác tầng. Vì vậy phần so sánh dưới đây chỉ so hai trục mà user hỏi: **cách đánh giá** và **cách tổ chức**.

## Skill

| skill | mục đích | nhánh | gọi |
|---|---|---|---|
| `dym-harness-sdk-quickstart` | cài + dựng agent, xem nó lắp gì | tiêu thụ · shell+python | `/dym-harness-sdk quickstart` |
| `dym-harness-sdk-interventions` | chốt chặn tool call có kiểu | tiêu thụ · python | `/dym-harness-sdk interventions` |
| `dym-harness-sdk-effect-tests` | test live-model bằng hiệu ứng | tiêu thụ · pytest | `/dym-harness-sdk effect-tests` |
| `dym-harness-sdk-evals` | chấm điểm bằng Evals SDK (**chưa kiểm chứng**) | tiêu thụ · python+CLI | `/dym-harness-sdk evals` |
| `dym-harness-sdk-contributor` | sửa chính harness, chạy như CI | đóng góp · shell | `/dym-harness-sdk contributor` |

**Thứ tự chạy đề xuất:** quickstart → interventions → effect-tests → (evals khi đã clone repo evals). Người đóng góp: contributor.

**Bẫy đắt nhất:** Số "benchmarked defaults" không tái lập được từ repo này. Nếu định chép giá trị mặc định của họ (offload 1500/750 token, compaction ở 85%) thì phải tự đo lại trên việc của mình.

## Kiểm chứng thế nào

| khẳng định | bằng chứng |
|---|---|
| unit harness-py xanh | chạy thật: `748 passed, 2 skipped`, rc 0, 50s (Py 3.13, venv cô lập) |
| fixture MCP cần lệnh `python` | chạy thật: FAIL `No such file or directory: 'python'` khi PATH chỉ có `python3`; hết lỗi khi đặt venv/bin lên đầu PATH |
| thiếu PATH venv + AWS env thì chậm và đỏ | chạy thật: lượt 1 mất 24 phút, `7 failed, 733 passed, 8 errors` (test MCP); lượt có venv/bin trong PATH + `AWS_EC2_METADATA_DISABLED`+`AWS_REGION` xong 50s, xanh. Chưa tách biến nào gây chậm |
| integ = 11 test live model | `pytest tests_integ --co` rc 0; **chưa chạy** (cần Bedrock) |
| `create_harness()` trả `strands.Agent` thường, 11 tool | chạy thật, rc 0 |
| web_search bị bỏ lặng khi model không hỗ trợ | chạy thật: chỉ in cảnh báo, `web_search` vắng trong `tool_names` |
| 2 intervention cùng loại → raise; giá trị sai kiểu → raise | chạy thật, rc 0 (bắt được ValueError) |
| grammar interventions tất định | `harness-py/src/strands_harness/interventions.py:1-17, 45-65` |
| thứ tự ưu tiên Deny>Interrupt>Transform>Guide>Proceed | `team/designs/0007-intervention-primitive.md:154-162` |
| assert hiệu ứng, không assert lời văn | `harness-py/tests_integ/conftest.py:7-8, 57-120` |
| cache read phải tăng mọi lượt | `harness-py/tests_integ/test_caching.py:44-66` |
| selective-test có test riêng, 19/19 | chạy thật: `classify.test.sh` rc 0; grep `.github` → **không workflow nào gọi** |
| harness không dùng Evals SDK trong CI | grep `strands_evals\|strands-evals` trong harness-py/ts/.github = rỗng |
| số benchmark chép tay, dữ liệu gốc vắng | `site/public/embeds/strands-harness-benchmarks.html:132-179`; các file `.xlsx` được trích dẫn không tồn tại trong repo |
| `.claude`/`.kiro` là symlink về `.agents/` | `ls -la` thật |
| `CLAUDE.md` = một dòng `@AGENTS.md` | `cat` thật |
| số design bị trùng 0009/0011/0015 | `ls team/designs` thật |
| Evals SDK: Experiment/Case/Evaluator/Detector, `--fail-on` | chỉ docs (`site/.../evals-sdk/*.mdx`) — **chưa kiểm chứng** |

## So với overstack — hơn / kém

### Đánh giá (evaluation)

| trục | Strands | overstack | ai hơn |
|---|---|---|---|
| Test live-model assert **hiệu ứng** (tool_succeeded / tool_attempted / tool_result_contains qua lịch sử hội thoại) | có, là trục chính của integ | `skill-ab-eval` chấm output bằng `contains/regex/equals` trên chữ, cộng thêm process từ span OTel | **Strands**: chấm chữ dễ flaky; predicate `tool_attempted` chống pass giả là thứ ta chưa có |
| Kiểm cơ chế bằng metric hạ tầng (cache read tăng đơn điệu) | có | không thấy | **Strands** |
| Thống kê độ ổn định (pass@k, pass^k) | không, chỉ `--reruns 2` (che flaky) | `skill-ab-eval --runs K` báo pass@k + pass^k | **overstack** |
| Benchmark công khai (6 bộ, Terminal-Bench…) | có số, nhưng không tái lập được từ repo | không chạy benchmark ngoài | Strands có "câu chuyện", ta có biên lai; không bên nào đủ |
| Regression eval khi đổi default/prompt | không | wikieval, trace-grader, council, capproof 197/197, mem-bench, retrieval-eval | **overstack** |
| Học từ lỗi (failure → luật) | không | failure-flywheel (đếm lớp lỗi → sinh stub luật) | **overstack** |
| Gate CI của lượt chạy live có mô hình trust (PR từ fork phải được duyệt tay trước khi cấp credential) | có (`authorization-check`, OIDC role) | CI ta không chạy live model | **Strands** (ta chưa cần) |
| Selective test theo đồ thị module (`vitest related`) | có (nhưng test của nó không nối CI) | chạy đủ bộ | Strands, nếu bộ test của ta còn phình |
| Eval tách "đạt không" (Evaluator) khỏi "vì sao" (Detector) | có trong Evals SDK | trace-grader chấm, failure-flywheel phân loại, nhưng rời rạc | ngang, chỉ khác cách đóng gói |

### Tổ chức

| trục | Strands | overstack | ai hơn |
|---|---|---|---|
| Chốt chặn | intervention trả **quyết định có kiểu** (5 action) + ưu tiên + cắt ngắn chuỗi + audit chung; subagent kế thừa; không lách qua tool gián tiếp | 22 luật `policy.yaml`, hook chặn qua **một kênh** exit 2 (đúng loại "last write wins" mà design 0007 chê) | **Strands** về mô hình; ta hơn về số luật đang cắn thật |
| Lớp chỉ dẫn agent | `CLAUDE.md` = `@AGENTS.md`; `.claude/.kiro` symlink về `.agents/` → một nguồn, nhiều client | `CLAUDE.md` trỏ llmwiki, cộng mirror llmwiki ↔ canonical (có drift như memory ghi) | **Strands** gọn hơn |
| Tách "lớp lắp ráp" khỏi SDK | harness mỏng, trả object SDK thường, giá trị tường minh luôn thắng | framework dày: hook, engine, wiki, installer | khác mục tiêu, không so |
| Governance | TENETS, DECISIONS (ADR nhẹ), API bar-raising 3 mức, lifecycle experimental có tiêu chí thoát, AI_USAGE_POLICY ("tất định được thì đừng dùng AI") | propose → gate → plan, ADR trong wiki, luật R1..R22 | ngang; điều "tất định được thì đừng dùng AI" trùng triết lý 0-token của ta |
| Parity đa ngôn ngữ | py↔ts chép tay, **không** có test parity | không áp dụng | Strands yếu |
| Độ khớp tài liệu ↔ code | lệch: AGENTS gốc không nhắc harness, workspace sai, design đánh số trùng, code trích "0017-subagents" sai | có lint/wiki-sync/drift gate (nhưng hiện đang trễ 114 commit) | **overstack** có máy bắt lệch |

## Verdict adapt-modes: **HÒA TAN** (một phần, nhỏ)

- **Lấy (viết lại thành code của ta, stdlib, 0 token):**
  1. Ba predicate hiệu ứng `tool_succeeded` / `tool_attempted` / `tool_result_contains`, cộng assert metric như cache-read, đưa vào `skill-ab-eval` / `trace-grader` dưới dạng một loại `check` mới đọc transcript/span thay vì chữ. Chi phí: vài chục dòng; tác dụng là giảm flaky và chặn pass giả.
  2. Mô hình quyết định có kiểu cho hook: Deny / Guide / Interrupt / Transform + ưu tiên + audit chung, làm hướng cho `harness-events.py`. Việc lớn hơn, cần propose riêng.
- **KHÔNG LẤY:** bản thân harness/SDK (khác tầng: ta bọc Claude Code, không tự viết agent loop); Evals SDK (ta đã có wikieval/trace-grader/council, và họ còn chưa tự dùng trong CI); số benchmark (không tái lập được).
- **Cân nhắc:** gom lớp chỉ dẫn về một nguồn + symlink như `.agents/` để hết drift mirror.

HÒA TAN thì phải **hỏi user trước khi scaffold**, chưa dựng gì vào repo chính.

## Install tại chỗ

```bash
mkdir -p .claude/skills && ln -sfn ../../.overstack/doyourmagic/harness-sdk/skills/dym-harness-sdk .claude/skills/dym-harness-sdk
```
