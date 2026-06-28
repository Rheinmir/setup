---
type: decision
title: "ADR-005: code-logger và bản đồ năng lực ĐI XUỐNG cùng dự án (có scope), không chỉ ở repo framework"
status: accepted
tags: [adr, downstream, logger, capabilities, scope, travel, adr-004, council]
timestamp: 2026-06-28
---

# ADR-005: logger + capability-map đi xuống cùng dự án (scoped)

## Status
Accepted (2026-06-28)

## Context

Hai năng lực vừa dựng — `code-logger` (ghi log.md bằng code thay vì trông chờ agent nhớ) và `build-capabilities` (sinh bản đồ "đồ nghề bạn có" để agent không làm lại thứ đã tồn tại) — ban đầu chỉ sống trong repo framework. Kiểm tra luồng cài thực tế xác nhận: cả hai **không** travel — `code-logger.py` và `build-capabilities.py` không nằm trong `.template-manifest.json` cũng không trong danh sách `bootstrap.sh` kéo về; hook có travel nhưng gọi `code-logger.py` ở đường dẫn vắng mặt downstream nên **fail-open, im lặng**.

Người dùng chỉ ra điều này chưa đúng: kỷ luật `log.md` ("append sau mỗi thao tác") và nhu cầu "biết mình có skill/rule gì" **áp dụng cho cả dự án downstream**, không riêng việc phát triển framework. Vậy cả hai nên đi xuống cùng dự án. Kèm một câu hỏi sắc: *"chỉ biết cách tương tác với skill thôi có đủ không?"* — và yêu cầu **debate các trường hợp nghịch chuyển** trước khi quyết, vì quyết định này đụng [[ADR-004-framework-dev-context-opt-in]] (vốn nói: context nội-bộ-framework phải opt-in, không tự bơm/không travel).

## Debate — các trường hợp nghịch chuyển (vì sao "cho travel" có thể vỡ)

| # | Nghịch chuyển | Phán | Cách chặn đã áp dụng |
|---|---------------|------|----------------------|
| 1 | `build-capabilities` quét `skills/` cục bộ — downstream **không có** thư mục đó (skill là global `~/.claude/skills`) → bản đồ rỗng, vô dụng. | Thật | Tool thành context-aware: khi không phải repo framework, đọc `~/.claude/skills` (global). |
| 2 | Cổng `--check` chặn commit downstream vì skill global đổi **bên ngoài** dự án (drift không phải lỗi của họ) → cổng thành kẻ phá. | Thật | `--check` chỉ là cổng **cứng ở repo framework** (trong `fdk-gate`); downstream nó chỉ thông báo, exit 0. |
| 3 | Agent downstream **đã** có danh sách skill trong system-prompt → bản đồ năng lực trùng lặp, "biết tương tác skill là đủ". | Nửa đúng | Cái THIẾU không phải tên skill, mà là **rule-awareness** (harness sẽ chặn gì) + **state** (đã làm gì). Nên bản đồ phải gồm RULES, và logger lo state. |
| 4 | `code-logger` lọc theo `FRAMEWORK_PREFIXES` (harness/fdk/skills) — downstream đó là framework **đã cài**, không phải app của user. | Thật | Giá trị downstream chính là log `llmwiki/` (wiki của họ); harness/fdk chỉ là nhiễu nhẹ, hiếm. |
| 5 | `log.md` bị churn — mỗi Stop lại sửa file tracked của họ. | Nhẹ | Render tất định, chỉ ghi khi nội dung đổi → không có thay đổi thì no-op. |
| 6 | Phình install / vi phạm ADR-004 — nhét file nội-bộ-framework vào mọi dự án. | Đánh đổi có chủ đích | Chỉ travel cái **phục vụ dự án** (wiki-log, bản đồ skill+rule). KHÔNG travel `fdk-gate` và các meta-guard (đồ nghề DEV framework). |

**Kết luận debate:** "biết tương tác skill" là **cần nhưng chưa đủ**. Đủ = skill-awareness (đã có) **＋** rule-awareness (harness chặn gì) **＋** state (đã làm gì = log). Cho travel là đúng — nhưng phải **scoped**, không bê nguyên đồ nghề dev-framework xuống.

## Decision

1. **`code-logger` đi xuống cùng dự án.** `install-harness --global` copy `code-logger.py` vào `~/.claude/harness/hooks/`; `hooklib.code_log` phân giải logger **cạnh hooks** (deployed) hoặc `<root>/harness/scripts/` (repo). Downstream nó tự động ghi `log.md` của *dự án đó* bằng code — đúng kỷ luật mà trước nay trông chờ agent nhớ.

2. **`build-capabilities` đi xuống, nhưng context-aware.** Cùng một tool, hai bối cảnh:
   - *Repo framework* (có `fdk/tools` + `harness/scripts`): bản đồ ĐẦY ĐỦ skill + rule + fdk-tool + harness-script → `fdk/CAPABILITIES.md`; `--check` là cổng cứng.
   - *Dự án downstream* (chỉ cài framework): skill từ **global** `~/.claude/skills`, rule từ `policy.yaml` đã cài → bản đồ GỌN "đồ nghề bạn có Ở DỰ ÁN NÀY" → `<root>/CAPABILITIES.md`; `--check` **không** chặn (vì #2).

3. **Bản đồ phải gồm RULES, không chỉ skill** (trả lời "đủ chưa"). Downstream agent vốn biết skill (system-prompt); cái net-new là biết **harness sẽ chặn gì** để làm việc *cùng* rào chắn thay vì đâm vào. Logger lo phần **state** (đã làm gì).

4. **Đồ nghề DEV framework KHÔNG travel.** `fdk-gate`, `harness-lint/doctor`, `adapt-registry`, scaffolder… ở lại repo framework. Sửa chính skill/rule/validator → làm ở repo với `/fdk`.

## Hoà giải với ADR-004

ADR-004 cấm **auto-bơm/đưa xuống context NỘI-BỘ-FRAMEWORK** (fdk.md, inventory framework, runbook sửa rule). ADR-005 không mâu thuẫn: thứ đi xuống ở đây là **bản đồ năng lực + log của CHÍNH dự án downstream** — nó *phục vụ dự án hiện tại*, nên qua đúng bài kiểm của ADR-004 ("chỉ cái phục vụ dự án hiện tại mới được travel/auto-fire"). Ranh giới: *project-serving* (skill+rule mình có, việc mình đã làm) travel; *framework-internal* (đồ nghề phát triển framework) ở lại. Vì lý do churn + latency + đúng ADR-004, bản đồ **không** auto-sinh ở `SessionStart`; pointer trong AGENT/CLAUDE (đã travel) trỏ tới nó, agent đọc/sinh lại **on-demand** — đúng nhịp: log phải bị động (agent không tự log), còn tra năng lực thì hỏi-khi-cần.

## Consequences

- (+) Downstream được auto-log `log.md` bằng code + một bản đồ "đồ nghề bạn có ở đây" gồm cả rule — đúng tinh thần "đừng dựa vào agent nhớ", áp dụng cho *mọi* dự án dùng framework.
- (+) Một tool, hai bối cảnh: không nhân đôi code; repo output giữ **byte-identical** nên `fdk-gate --check` vẫn xanh.
- (+) Có tiêu chí rạch ròi cho lần sau: *project-serving* travel, *framework-internal* ở lại — mở rộng được bài kiểm của ADR-004.
- (−) `~/.claude/skills` đổi thì bản đồ downstream cũ đi (chấp nhận: không cổng cứng, sinh lại rẻ).
- (−) Thêm 2 file vào payload cài global. Đánh đổi có chủ đích, đã giới hạn ở đúng 2 cái phục vụ dự án.

## Origin
- **Decision rút từ:** phản hồi user phiên 2026-06-28 — "code logger xuống cùng pj, capabilities cũng thế, thế thì chỉ biết cách tương tác với skill thôi có đủ k, debate luôn các trường hợp nghịch chuyển".
- **Nguồn:** `harness/scripts/code-logger.py`, `fdk/tools/build-capabilities.py`, `llmwiki/.claude/hooks/hooklib.py`, `harness/scripts/install-harness.sh`; họ [[ADR-004-framework-dev-context-opt-in]], [[fdk]], [[feature-catalog]].
