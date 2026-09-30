---
type: draft
title: "280926-overstack-strands-wrapper"
status: approved
tags: [propose, harness, strands, adapter, evaluation, separate-repo]
timestamp: 2026-09-28
task: T-260928-01
---

# 280926 — overstack-strands: Strands thành vendor thứ 7 của harness overstack, kèm hệ đánh giá bọc ngoài

**Status:** approved (bản 2, user duyệt lại 28/09/2026) — sửa sau khi `/plan` phát hiện 5 chỗ lệch (xem `## Sửa đổi bản 2`); bản 1 user duyệt 28/09/2026

**Sequence diagram:** [280926-overstack-strands-wrapper-seq.html](../../../html/280926-overstack-strands-wrapper-seq.html)

## What

Tạo repo private `Rheinmir/overstack-strands`. Repo này lấy **Strands harness** (`create_harness()` của strands-agents) làm lõi chạy agent. Bên ngoài lõi, nó gắn **lớp bọc của overstack**: cùng bộ luật `policy.yaml` và cùng các validator, ghim theo commit của setup. Như vậy Strands trở thành **vendor thứ 7**, cạnh claude, opencode, antigravity, cursor, codex và kiro. Kèm theo là một **hệ đánh giá bọc ngoài**, trả lời hai câu: lớp bọc có cắn đúng không, và nó tốn bao nhiêu so với chạy Strands trần. Hệ này chạy trên các model Trung Quốc giá rẻ qua OpenRouter, đổi model tuỳ ý.

## Context

- **Thick policy, thin adapter** (ADR-001-policy-as-source-of-truth (fdk/wiki), `fdk/wiki/sources/adr/ADR-001-policy-as-source-of-truth.md`):
  - `harness/poc-vendor-neutral/policy.yaml` là nguồn chân lý. Mỗi vendor chỉ là một dây nối mỏng do `gen-converters.py` sinh.
  - Thêm luật thì sửa policy, không sửa adapter.
  - Strands vì vậy không cần kiến trúc mới, chỉ cần thêm một adapter.
- **Recipe 5 lớp** (`harness/recipe.md`):
  - L0 POLICY → L1 SESSION (adapter theo vendor) → L2 REPO (pre-commit) → L3 AUDIT → L4 EVALS.
  - Hợp đồng validator: stdin là event JSON chuẩn hoá `{action, file_path, content, command, wiki_dir}`. Exit 0 là pass, exit 2 là vi phạm; lý do in ra stderr để agent đọc và tự sửa.
  - Khoảng 80% hệ thống dùng lại nguyên khi đổi vendor.
- **Hiện trạng 22 luật** trong `policy.yaml`, đếm theo `kind`:
  - hook_event 6, content_check 5, conditional_require 3
  - deny_write 2, process_gate 2
  - require_section 1, forbid_root 1, require_frontmatter 1, repo_gate 1
- **Tiền lệ tách repo:** engine `orca-graph` tách sang `Rheinmir/orca-graph` từ 20/09/2026.
  - Repo đó khai `repo_role: module` và `upstream_pin` trong `.overstack.yaml`.
  - Setup giữ shim, mirror skill và provenance `external-pull`.
  - `/ship` đọc nhãn qua `harness/scripts/repo_role.py`.
- **Bundle vừa distill** (`.overstack/doyourmagic/harness-sdk/workflows.md`, PR Rheinmir/dym#12):
  - Intervention của Strands trả **quyết định có kiểu**: Proceed, Deny, Guide, Interrupt, Transform.
    - Ưu tiên: Deny > Interrupt > Transform > Guide > Proceed.
    - Có audit chung; subagent kế thừa luật.
    - Gọi gián tiếp qua `programmatic_tool_caller` cũng không lách được.
  - Test live của họ assert **hiệu ứng** qua ba predicate: `tool_succeeded`, `tool_attempted`, `tool_result_contains`.
  - Họ không có regression eval hay pass@k. Ta có pass@k / pass^k (công thức Chen et al. 2021, đang nằm trong `harness/scripts/skill-ab-eval.py` — file này **chưa được commit**) và `harness/scripts/trace-grader.py` (đã commit).
- **Đã kiểm chứng trong phiên (28/09/2026):**
  - `create_harness(model="openai/<slug OpenRouter>")` với `OPENAI_BASE_URL=https://openrouter.ai/api/v1` dựng được agent, rc 0, cho `deepseek/deepseek-chat-v3.1`, `qwen/qwen3-coder`, `moonshotai/kimi-k2`.
    - Đường này dùng `OpenAIResponsesModel` (Responses API).
    - Harness có thêm đường `litellm/*`, đọc `LITELLM_API_KEY` và `LITELLM_BASE_URL` (`strands_harness/models.py:260-270`).
  - Unit harness-py: 748 passed, với điều kiện venv `bin` nằm đầu `PATH` và có biến AWS.

## Global constraints

- `policy.yaml` là nguồn chân lý duy nhất cho luật (ADR-001-policy-as-source-of-truth (fdk/wiki)).
  - Repo mới **ghim** policy và validators theo commit của setup; không chép rồi sửa riêng.
  - Nhãn repo: `repo_role: module`, `upstream_pin: <commit setup>` (khuôn `orca-graph`).
- Setup **giữ nguyên** adapter Claude Code và 5 vendor còn lại. Repo mới chỉ **thêm** vendor thứ 7.
- Adapter Strands **không mã hoá luật**. Nó chỉ làm ba việc: chuẩn hoá event của Strands về event JSON ở trên, gọi validator có sẵn, rồi dịch exit code thành quyết định intervention.
- Strands được **KÉO NGOÀI**:
  - Pin chính xác phiên bản `strands-harness`, không vendor code.
  - Harness của họ còn 0.x và bật mặc định `strands.experimental.ContextManager`, nên mỗi lần nâng pin phải chạy lại toàn bộ bộ đánh giá.
- Lõi adapter và lõi eval chỉ dùng stdlib Python và `strands-harness[litellm]`. Python ≥ 3.10.
- Model cho đánh giá đi qua **OpenRouter**, mặc định là các model Trung Quốc giá rẻ (DeepSeek, Qwen, Kimi, GLM, MiniMax).
  - Danh sách model là cấu hình, đổi được mà không sửa code.
  - Khoá API chỉ đọc từ biến môi trường, không bao giờ ghi vào repo.
- Mọi lượt đo tốn tiền phải chạy dưới trần ngân sách khai trước. Chạm trần thì dừng, không tự nới.
- Repo private cho tới khi E1 xanh.
- Commit không ghi công AI (R15, ADR-016-no-ai-attribution-in-commits (fdk/wiki)).

## Non-goals

- Không gỡ hay thay thế adapter Claude Code và 5 vendor còn lại.
- Không tách lõi harness (policy, validators, `gen-converters.py`) ra khỏi setup ở pha này.
- Không viết lại agent loop, không fork Strands.
- Không dùng Strands Evals SDK trong lõi eval: chưa kiểm chứng, và chính họ cũng không dùng trong CI. Có thể thêm sau làm backend tuỳ chọn.
- Không chạy lại 6 benchmark công khai của họ. Bộ đánh giá đo **lớp bọc**, không đo năng lực model.
- Không làm UI hay dashboard. Báo cáo là một file HTML tĩnh.

## Approaches

1. **A — Adapter Strands trong repo riêng, policy ghim từ setup (đã chọn, user duyệt ở câu hỏi phạm vi).**
   - Repo mới gồm adapter L1 (policy → intervention + hook), bộ đánh giá bọc ngoài và CI. Policy và validators kéo từ setup theo commit ghim.
   - Được:
     - đúng ADR-001, một nguồn luật;
     - đúng khuôn `orca-graph`;
     - không đụng người dùng Claude Code;
     - đo được "bọc vs trần" trên cùng một lõi.
   - Mất: hai repo phải đồng bộ pin. Setup đổi policy thì repo này phải re-pin và chạy lại eval.
2. **B — Tách toàn bộ lõi harness ra repo mới; setup và mọi vendor tiêu thụ nó.**
   - Được: một repo lõi sạch, dùng chung được.
   - Mất: đụng installer, đường dẫn downstream `.harness/`, 101 test và hook của mọi dự án khách.
   - Có thể làm sau, nếu A chứng minh nhu cầu dùng chung lõi là có thật.
3. **C — Agent CLI riêng trên Strands, thay Claude Code làm runtime.**
   - Được: kiểm soát trọn runtime.
   - Mất: toàn bộ hệ skill và trải nghiệm Claude Code, và phải tự làm TUI.
   - Đây là đổi hướng sản phẩm; user đã loại.

**Chọn A.** Đây là cách duy nhất đạt cả hai mục tiêu mà không phá vỡ thứ đang chạy: lớp bọc chạy trên Strands, và có hệ đánh giá.

## Affected

| File / Symbol | How it changes |
|---|---|
| repo mới `Rheinmir/overstack-strands` (private) | tạo mới: adapter, eval, CI, `.overstack.yaml` (`repo_role: module`) |
| `harness/poc-vendor-neutral/policy.yaml` | **không đổi nội dung**. Chỉ thêm trường tuỳ chọn `strands:` nếu T2 chứng minh là cần |
| `harness/poc-vendor-neutral/gen-converters.py` | không đổi ở pha này; adapter đọc policy lúc chạy, không cần sinh file |
| `harness/scripts/repo_role.py` | không đổi; dùng nhãn `module` có sẵn |
| `fdk/skills.provenance.json`, `fdk/CAPABILITIES.md` | thêm một dòng tham chiếu repo mới (T5) |
| `harness/scripts/trace-grader.py`, `harness/trace-grader.config.yaml` | không đổi; repo mới ghim để dùng lại bộ chấm trace |
| `harness/poc-vendor-neutral/gen-converters.py` | không đổi; repo mới ghim để tự sinh `out/claude/settings.snippet.json` (thư mục `out/` bị gitignore) |

Không có hành vi nào của setup bị đổi.

## Risks

- **Ngữ nghĩa lệch giữa hook exit 2 và Deny của Strands.**
  - Hook Claude chặn rồi đưa stderr cho agent; agent sửa và thử lại. Deny của Strands thì cắt ngắn chuỗi handler.
  - Nếu dịch exit 2 thành Deny không kèm lý do, agent không biết phải sửa gì.
  - T2 phải dịch thành Deny kèm lý do là stderr, hoặc Guide tuỳ luật. T3 phải kiểm đúng hành vi đó.
- **Luật chỉ biết trạng thái đĩa.**
  - R3 index-sync đọc `wiki/index.md` trên đĩa lúc Stop. Strands không có sự kiện "Stop" trùng nghĩa.
  - Đã đối chiếu mã nguồn SDK (strands-agents 1.57.1): `AfterInvocationEvent.resume` cho phép hook bắt agent chạy tiếp với một input mới. Adapter đặt `resume = "GUIDANCE: <lý do>"`, có trần số lần để không lặp vô hạn (U-01 đã trả).
- **Ghi file gián tiếp.**
  - Agent có thể ghi qua `shell` (`echo > raw/x`) thay vì qua `write`. Claude có cùng lỗ này; L2 pre-commit là hàng rào cuối.
  - Adapter phải soi cả lệnh shell, giống hook Claude đang làm.
- **Model Trung Quốc qua OpenRouter gọi tool kém ổn định hơn Claude.**
  - Tỉ lệ chặn nhầm và pass^k có thể phản ánh model yếu chứ không phải lớp bọc yếu.
  - E2 luôn so bọc với trần **trên cùng model**, nên chênh lệch vẫn quy được về lớp bọc.
  - Đường gọi OpenRouter nào ổn cho tool calling còn chưa chắc (U-03).
- **Pin Strands 0.x có thể vỡ API khi nâng.** Giảm rủi ro bằng pin chính xác và chạy toàn bộ bộ đánh giá mỗi lần nâng.

## Plan

- [ ] **T1 — Dựng repo và ghim nguồn.**
  - Tạo repo private `Rheinmir/overstack-strands` gồm:
    - `pyproject.toml` pin `strands-harness[litellm]`;
    - `.overstack.yaml` (`repo_role: module`, `upstream_pin`);
    - script `sync-upstream` kéo `policy.yaml`, `llmwiki-validate.py`, `harness-events.py`, `gen-converters.py`, `trace-grader.py` và `trace-grader.config.yaml` từ setup theo commit ghim, sinh lại snippet hook Claude bằng `gen-converters.py`, rồi ghi sha256 từng file vào `upstream/PIN.json`.
  - CI chạy bộ tất định.
- [ ] **T2 — Adapter policy → intervention.** Gồm handler intervention `OverstackPolicy` (tên `overstack:policy`) và plugin `OverstackHooks` (tên `overstack:hooks`).
  - Adapter **giả lập giao thức hook Claude Code**: đọc `out/claude/settings.snippet.json` đã ghim (7 lệnh hook trên 6 sự kiện) và chạy đúng các lệnh đó với JSON đúng dạng hook Claude. Luật mới ở setup đi vào chỉ bằng re-pin.
  - Trước mỗi tool call `write` / `edit` / `shell` (map sang `Write` / `Edit` / `Bash`): chạy hook `PreToolUse`, rồi dịch exit code:
    - exit 0 → Proceed;
    - exit 2 (mọi luật) → Guide chứa stderr: tool bị huỷ, model thấy `GUIDANCE: <lý do>` và tự sửa được — đúng ngữ nghĩa hook Claude, nơi exit 2 luôn chặn và đưa stderr cho agent.
    - R15 (commit không ghi công AI) giữ như bên Claude: do hook git ở tầng repo gác, adapter không làm riêng.
  - Hook sự kiện: `Stop` (R3) → `AfterInvocationEvent`, exit 2 thì `resume` kèm lý do, tối đa 2 lần; `PostToolUse` (R4 audit) → `AfterToolCallEvent`; `SessionStart` và `UserPromptSubmit` (R8, R10) → `BeforeInvocationEvent`; `SessionEnd` → lúc tiến trình thoát.
  - Mỗi quyết định ghi một dòng audit JSONL (L3).
  - Cách dùng: `create_overstack_harness(workspace, model=..., **kw)` — gọi `create_harness` với hai thành phần trên đặt TRƯỚC interventions/plugins của người dùng.
- [ ] **T3 — Bộ conformance tất định, 0 token.**
  - Chạy cùng một bộ fixture event qua hai đường:
    - (a) validator trực tiếp;
    - (b) adapter Strands với model giả, không gọi mạng.
  - Fixture gồm các ca như ghi vào `raw/`, wiki thiếu `## Origin`, commit có Co-Authored-By.
  - Kỳ vọng: cùng verdict, cùng lý do, cho từng luật.
- [ ] **T4 — Hệ đánh giá bọc ngoài, 4 tầng.** Model lấy từ danh sách OpenRouter khai trong `eval.config.yaml`.
  - **E0** là T3.
  - **E1 — hiệu ứng live.** Mỗi luật chặn được có một kịch bản dụ agent vi phạm, assert ba điều:
    - `tool_attempted`: agent đã thật sự thử;
    - tool bị Deny;
    - đĩa không đổi.
    - Thêm kịch bản hợp lệ để đo **chặn nhầm**.
  - **E2 — A/B bọc vs trần.** Cùng bộ tác vụ, chạy K lần cho mỗi cấu hình và mỗi model. Báo:
    - pass@k và pass^k: chép hai hàm thuần của `skill-ab-eval.py` (Chen et al. 2021) vào `evals/stats.py`, kèm test so với số đo trên bản ở setup (pass@3(5,2) = 0.900, pass^3(5,2) = 0.000);
    - token và tiền mỗi tác vụ;
    - số vi phạm lọt ra đĩa;
    - tỉ lệ chặn nhầm.
  - **E3 — chấm trace.** Chuyển lịch sử hội thoại của Strands (mỗi `toolUse` + `toolResult` thành một bước, tên tool đổi sang tên Claude) sang `traces.json` mà `trace-grader.py` đọc được, để chấm quá trình: số bước, tool lỗi, tool cấm. Không cần bật OTel.
  - **Cổng CI:**
    - E0 bắt buộc ở mỗi PR.
    - E1 và E2 chạy khi đổi pin hoặc đổi policy, phải qua ngưỡng khai trong `eval.config.yaml` và dừng khi chạm trần ngân sách.
- [ ] **T5 — Nối về setup và báo cáo.**
  - Thêm tham chiếu repo mới vào `fdk/CAPABILITIES.md` và provenance.
  - Sinh báo cáo HTML tĩnh gồm:
    - bảng từng luật: conformance, hiệu ứng live, chặn nhầm;
    - bảng A/B cho từng model;
    - vỏ `docs-site-macos`, có toggle sáng/tối.

## Requirements (FR)

- **FR-001**: Repo mới PHẢI ghim `policy.yaml` và validators theo một commit của setup, và ghi provenance; không được sửa tay bản ghim.
- **FR-002**: Adapter PHẢI gọi đúng validator có sẵn theo hợp đồng stdin và exit code, không được tự mã hoá luật.
- **FR-003**: Adapter PHẢI trả quyết định intervention có kiểu, kèm lý do là stderr của validator, để agent sửa được mà không cần người.
- **FR-004**: Adapter PHẢI soi cả ghi file trực tiếp (`write` / `edit`) lẫn gián tiếp qua `shell`; luật PHẢI được kế thừa xuống subagent.
- **FR-005**: Mỗi quyết định của adapter PHẢI ghi một dòng audit JSONL gồm luật, verdict, lý do, tool và thời điểm.
- **FR-006**: Bộ conformance E0 PHẢI chạy không cần mạng và không cần credential, và PHẢI so verdict adapter với verdict validator cho từng luật chặn được.
- **FR-007**: E1 PHẢI chứng minh mỗi luật chặn được đã cắn một lần thử thật (agent đã thử, bị chặn, đĩa không đổi), và PHẢI đo tỉ lệ chặn nhầm trên kịch bản hợp lệ.
- **FR-008**: E2 PHẢI so bọc với trần trên cùng bộ tác vụ và cùng model, báo pass@k, pass^k, chi phí mỗi tác vụ và số vi phạm lọt.
- **FR-009**: Model đánh giá PHẢI gọi qua OpenRouter theo danh sách cấu hình đổi được, và mọi lượt tốn tiền PHẢI dừng khi chạm trần ngân sách.
- **FR-010**: Repo mới PHẢI sinh được báo cáo HTML tĩnh tổng hợp E0–E3, và setup PHẢI có tham chiếu tới repo này.

## Success criteria (SC)

- **SC-001**: Người dùng dựng một agent Strands có đủ luật overstack chỉ bằng một lệnh cài và một dòng `create_harness(...)`, dưới 10 phút tính từ lúc clone.
- **SC-002**: Với mọi luật chặn được, agent thật cố vi phạm đều bị chặn và tự sửa được theo lý do nhận về. Không có vi phạm nào lọt ra đĩa trên bộ E1.
- **SC-003**: Lớp bọc không làm hỏng việc hợp lệ. Tỉ lệ chặn nhầm dưới 2% trên kịch bản hợp lệ, và pass^k của bản bọc không thấp hơn bản trần quá 5 điểm phần trăm trên cùng model.
- **SC-004**: Nhìn một trang báo cáo là biết lớp bọc tốn thêm bao nhiêu (token, tiền, thời gian) mỗi tác vụ, và đổi lại chặn được bao nhiêu vi phạm, cho từng model.
- **SC-005**: Khi setup đổi `policy.yaml`, chỉ cần re-pin và chạy E0 là biết adapter Strands còn khớp hay không, không phải sửa code adapter.
- **SC-006**: Một lượt đo đầy đủ E1 + E2 trên một model tốn không quá trần ngân sách đã khai.

Bằng chứng ở tầng máy: E0 xanh trong CI mỗi PR; E1/E2 xuất JSON + HTML có số đo; audit JSONL đếm được từng quyết định.

## Assumptions

- Phạm vi: **thêm vendor thứ 7**; setup giữ nguyên Claude Code và 5 vendor kia. *User chọn 28/09/2026.*
- Repo: `Rheinmir/overstack-strands`, **private** cho tới khi E1 xanh. *User chọn 28/09/2026.*
- Model đánh giá: **OpenRouter**, linh hoạt giữa các model Trung Quốc giá rẻ. *User chọn 28/09/2026.* Danh sách khởi đầu là `deepseek/deepseek-v4.1-flash`, `qwen/qwen3.8-flash`, `z-ai/glm-5.3-flash`: ba model mới nhất, rẻ nhất có hỗ trợ `tools` theo danh mục OpenRouter ngày 28/09/2026 (giá vào/ra mỗi triệu token: 0.035/0.29, 0.15/0.47, 0.15/0.50 USD) `(default)`.
- Đường gọi OpenRouter là `litellm/openrouter/*` (Chat Completions), chưa dùng `openai/*` + `OPENAI_BASE_URL` (Responses API) `(default, find-out-later → [[unknown-280926-overstack-strands-wrapper]] U-03)`.
- Trần ngân sách là 2 USD mỗi lượt đo `(default, find-out-later → [[unknown-280926-overstack-strands-wrapper]] U-04)`.
- Adapter viết bằng **Python** (harness-py), vì validators và lõi eval của ta đều là Python `(default)`.
- Sự kiện Strands thay cho Stop của Claude là `AfterInvocationEvent`, dùng trường `resume` (đã kiểm mã nguồn SDK 1.57.1; U-01 đã trả).
- Mọi exit 2 của hook `PreToolUse` dịch thành Guide, để giữ đúng ngữ nghĩa hook Claude `(default)`. Bản 1 định dịch `deny_write` thành Deny; bỏ vì adapter chỉ thấy exit code, không thấy loại luật, và Deny không mang thêm lợi ích nào cho agent.
- Bộ tác vụ E2 khởi đầu với 10 tác vụ thao tác wiki/repo nhỏ, lấy từ các kịch bản sẵn có trong `harness/evals/`, K = 3 `(default)`.
- Ngưỡng SC-003 (2% chặn nhầm, 5 điểm pass^k) là con số khởi điểm `(default, find-out-later → [[unknown-280926-overstack-strands-wrapper]] U-02)`.
- Báo cáo dùng vỏ `docs-site-macos`, macrostructure "report một trang có bảng", có toggle sáng/tối `(default)`.

## Agent Task Assignment

| Task | Agent (CLI) | Lý do chọn | Status |
|---|---|---|---|
| T1 | claude-code | Tạo repo và ghim provenance là side-effect ra ngoài, cần người duyệt từng bước | done (Rheinmir/overstack-strands v0.1.0, 371173f) |
| T2 | claude-code | Ánh xạ ngữ nghĩa hook sang intervention dễ sai tinh vi; cần đọc mã nguồn SDK thật | done (Rheinmir/overstack-strands v0.1.0, 371173f) |
| T3 | opencode (mimo-v2.5-free) | Viết fixture và test tất định theo PLAN rõ ràng; rẻ, không cần suy luận sâu | done (Rheinmir/overstack-strands v0.1.0, 371173f) |
| T4 | claude-code | Thiết kế kịch bản dụ vi phạm và thống kê A/B cần phán đoán | done (Rheinmir/overstack-strands v0.1.0, 371173f) |
| T5 | opencode (mimo-v2.5-free) | Render báo cáo HTML và thêm dòng tham chiếu là việc cơ học | done (Rheinmir/overstack-strands v0.1.0, 371173f) |

## Render brief

- **T1:**
  - Dev tạo repo private trên GitHub (**add**).
  - `sync-upstream` lấy từ Setup `policy.yaml`, validators và `gen-converters.py` theo commit ghim, sinh lại snippet hook Claude (**add**).
  - Repo ghi provenance (**add**); CI chạy E0 (**add**).
  - Bài văn: repo mới không sở hữu luật, chỉ ghim một bản chụp của setup, nên mọi thay đổi luật vẫn bắt đầu ở setup.
- **T2:**
  - Agent Strands gọi tool → Registry intervention (**legacy**) → Handler `overstack:policy` (**add**) → Validator (**legacy**).
  - Validator trả exit 2 → Handler dịch thành Deny kèm lý do (**block**).
  - Agent sửa rồi gọi lại → exit 0 → Proceed (**add**) → ghi audit JSONL (**add**).
- **T3:**
  - Fixture → Validator trực tiếp (**legacy**) → verdict A.
  - Fixture → Adapter với model giả (**add**) → verdict B.
  - So A với B (**add**); lệch thì đỏ (**block**).
- **T4:**
  - Runner chạy Strands trần (**legacy**) và Strands bọc (**add**), K lần mỗi model.
  - OpenRouter (**add**) → lịch sử hội thoại → Trace-grader (**legacy**).
  - Tính pass@k/pass^k, chi phí, vi phạm lọt, chặn nhầm (**add**); vượt trần ngân sách thì dừng (**block**).
- **T5:** Eval JSON → Trình dựng báo cáo (**add**) → HTML tĩnh (**add**) → Setup thêm tham chiếu CAPABILITIES và provenance (**add**).

## Sửa đổi bản 2

Viết `/plan` là lúc phải khai đường dẫn và chữ ký thật, và nó lộ ra năm chỗ bản 1 không thi hành đúng nguyên văn được. Cả năm đã được kiểm bằng prototype chạy thật (15 test xanh, E0 khớp 11/11) trước khi sửa ở đây.

1. **`skill-ab-eval.py` chưa được commit** ở setup (file untracked, việc đang dở của một phiên khác), nên không ghim được theo commit. Bản 2 chép hai hàm thuần pass@k / pass^k (khoảng 10 dòng) vào repo mới, kèm test đối chiếu số.
2. **`out/claude/settings.snippet.json` bị gitignore** ở setup. Bản 2 ghim `gen-converters.py` và sinh lại snippet từ policy đã ghim (đã kiểm: bản sinh lại giống hệt từng byte).
3. **Exit 2 dịch thành Guide cho mọi luật**, thay vì chia Deny/Guide theo loại luật. Adapter chỉ thấy exit code; Guide đúng ngữ nghĩa hook Claude.
4. **E3 đọc lịch sử hội thoại** thay vì span OTel: đủ dữ liệu cho `trace-grader.py`, và không cần bật exporter.
5. **Danh sách model mặc định** đổi sang ba bản mới hơn và rẻ hơn trên OpenRouter.

U-01 đã trả bằng mã nguồn SDK (`AfterInvocationEvent.resume`).

## Self-review

1. **Phủ yêu cầu:**
   - "Tạo repo khác" → T1.
   - "Chuyển lớp bọc harness sang Strands" (đã chốt: vendor thứ 7) → T2.
   - "Design hệ thống đánh giá bọc ngoài" → T3 và T4.
   - "OpenRouter, model Trung Quốc linh hoạt" → FR-009, T4.
   - "Nối lại với framework" → T5.
2. **Quét placeholder:** không còn chỗ để trống hay hẹn làm sau. Ba câu hỏi chặn cổng đã được user trả lời và thay bằng giá trị thật.
3. **Nhất quán tên:**
   - "adapter Strands", handler `OverstackPolicy` (`overstack:policy`), plugin `OverstackHooks` (`overstack:hooks`), hàm `create_overstack_harness`, và các tầng E0–E3 được dùng thống nhất.
   - "Bọc" và "trần" luôn chỉ đúng hai cấu hình của E2.

## Origin

- **Draft:** `wiki/sources/draft/280926-overstack-strands-wrapper.md`
- **Nguồn:**
  - phiên distill `strands-agents/harness-sdk` 2026-09-28 (bundle `.overstack/doyourmagic/harness-sdk/`, PR Rheinmir/dym#12);
  - `harness/recipe.md`;
  - ADR-001-policy-as-source-of-truth (fdk/wiki).
- **Commit:** _(filled by `verify-before-commit`)_
- **Date promoted:** _(filled by `verify-before-commit`)_
