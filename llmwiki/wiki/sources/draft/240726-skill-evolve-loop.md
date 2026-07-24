---
type: draft
title: "skill-evolve — vòng đo chất lượng per-skill và tự đề xuất sửa SKILL.md"
status: proposed
tags: [skill-evolve, self-improvement, trace-grader, failure-flywheel, skill-usage, skillrl]
timestamp: 2026-07-24
task: T-260724-01
---

# 240726-skill-evolve-loop

**Status:** proposed

Yêu cầu gốc, một câu: issue GH#84 ("skill improve loop") trỏ tới `aiming-lab/SkillRL` — user muốn **chưng cất (distill)** ý tưởng của nó thành một vòng lặp trong overstack **tự động cải thiện các skill sẵn có**, không chỉ đo mà còn đóng vòng sửa.

**Sequence diagram:** [240726-skill-evolve-loop-seq.html](../../../html/240726-skill-evolve-loop-seq.html)

## Context

**SkillRL là gì (đã đọc README qua WebFetch trong phiên).** SkillRL trừu tượng hoá trajectory RL thô thành một **skill library phân tầng** (`general_skills`/`task_specific_skills`/`common_mistakes`) rồi tiêm (inject) skill liên quan vào prompt trong lúc **RL training** (retrieve → inject → chạy episode → thu reward → update policy). Điểm cốt lõi: **skill bank tự tiến hoá song song với policy** — khi success-rate của một nhóm task rớt dưới ngưỡng (mặc định 40%), hệ tự phân tích validation-failure và thêm tối đa 3 skill mới/chu kỳ.

**Khác biệt gốc rễ cần khai rõ ngay:** SkillRL vận hành trong vòng lặp **fine-tune model thật** (có reward số, có policy gradient, có "task success" nhị phân từ RL env). Overstack không có việc đó — "skill" ở đây là **markdown hướng dẫn cho agent**, không phải trọng số mô hình, và không có RL env để phát reward. Vì vậy đây không phải một cổng "port SkillRL", mà là **chưng cất đúng MỘT cơ chế của nó** — vòng phản hồi *đo chất lượng → khi tệ đi thì tự sửa skill bank* — vào hình dạng phù hợp overstack, dùng tín hiệu chất lượng SẴN CÓ trong repo thay cho reward RL.

**Khảo sát repo (agent Explore, phiên này) tìm 7 module đã giải một phần bài toán, không cái nào đóng trọn vòng per-skill:**
- `llmwiki/skills/dev-loop/failure-flywheel.md` (`harness/scripts/failure-flywheel.py`) — record/report/draft theo NGƯỠNG TÁI DIỄN, nhưng category là lỗi tự do do agent gõ tay, không gắn `skill_id`, không tự động hoá thu thập.
- `fdk/tools/skill-usage.py` — đo **tần suất** gọi skill từ transcript (`collect()` trả `{skill, ts, week, session}` mỗi lần gọi Skill-tool), không đo chất lượng.
- `llmwiki/skills/orchestrate/trace-grader.md` (`harness/scripts/trace-grader.py`) — chấm **đường đi** một run (`runs_from_transcript(lines, task_hint)` parse MỘT lát cắt jsonl thành MỘT Run, `grade_run()` trả verdict `clean-pass/pass-with-warnings/corrupt-success/fail` từ rule tất định: `forbidden_tool/out_of_order/retry_storm/excessive_steps/edited_without_read`) — nhưng hiện luôn chấm **cả transcript** làm một run, chưa từng cắt theo TỪNG lần gọi skill.
- `llmwiki/skills/orchestrate/orca-eval.md` — quét N session, tín hiệu "Correction/Repetition/Friction/Win" — nhưng việc PHÂN LOẠI tín hiệu đó là **LLM đọc digest phán đoán tại chỗ** (`skills/orca-eval/assets/orca-eval-scan.sh` chỉ in PROMPTS/ERRORS/REPEATED thô, không có regex correction), không phải hàm tất định, và không gắn với skill nào đang chạy lúc đó.
- `llmwiki/skills/dev-loop/new-skill.md` — cách THÊM skill mới (thủ công, đúng 4 nơi).
- `llmwiki/skills/orchestrate/council.md` — hội đồng multi-model có thể làm "judge" nội dung, hiện chỉ chạy ad-hoc theo câu hỏi.
- `llmwiki/skills/dev-loop/wikieval.md` — eval hồi quy nhưng đo NỘI DUNG wiki, không đo skill.

⇒ Khoảng trống thật: **chưa ai gắn một verdict chất lượng tất định vào ĐÚNG một `skill_id`, tích luỹ theo thời gian, rồi tự soạn đề xuất sửa ĐÚNG file `SKILL.md` đó khi verdict xấu đi** — khác `orca-eval` (đề xuất action rời rạc, không lặp một skill cụ thể) và khác `failure-flywheel` (category là text tự do, không phải skill_id, không tự động thu thập).

**Tiền lệ kỹ thuật cho phần glue (không cần công cụ mới):** cross-import file có dấu gạch ngang qua `importlib.util.spec_from_file_location` đã chạy sống ở `fdk/tools/new-skill.py`, `fdk/tools/build-wiki-graph.py`, `harness/scripts/decision-guard.py` — cùng kỹ thuật sẽ dùng để `skill-evolve.py` gọi thẳng `runs_from_transcript()`/`grade_run()` của `trace-grader.py` mà KHÔNG sửa file đó.

**`/fdk` problem-tree ([[problem-tree]]):** đây là một nhánh con của "framework rất giỏi PHÁT HIỆN nợ, kém nhịp TRẢ nợ" (ghi trong `llmwiki/AGENT.md` 5-Why, đo 2026-07-20) — nhưng ở tầng hẹp hơn: nợ chất lượng CỦA TỪNG SKILL, không phải nợ chung. `/fdk` sẽ được cập nhật cây vấn đề cuối phiên theo quy ước của chính nó.

## Global constraints

- **Never auto-promote** (nguyên văn rule của `failure-flywheel`, áp lại y hệt ở đây): mọi đề xuất sửa SKILL.md PHẢI dừng ở `/propose`, chờ người duyệt. `skill-evolve` không bao giờ tự ghi đè SKILL.md.
- **Build-now-adapt-later** (`llmwiki/skills/dev-loop/build-now-adapt-later.md`): ngưỡng số (recurrence threshold, min-sample-size) là **giả định best-guess**, phải cô lập trong ĐÚNG MỘT file config `verified:false` — đúng khuôn `harness/failure-flywheel.config.yaml` và `harness/trace-grader.config.yaml` đã làm.
- **Fail-open tuyệt đối ở phần ghi/scan** (khuôn `code-logger.py::record()`, `failure-flywheel.py` rule): quét/ghi ledger lỗi không được chặn phiên đang chạy.
- **Không sửa `trace-grader.py` hay `failure-flywheel.py`** — chỉ import/gọi CLI của chúng làm black-box (trừ MỘT thay đổi additive, backward-compatible vào `skill-usage.py::collect()` — thêm field `line_idx`, không đổi field cũ, không đổi hành vi `--weekly`/`--json` hiện tại).
- `llmwiki/CLAUDE.md` 5-Why + cái thang chống over-engineering: đã chạy — kết luận glue-only, không viết engine mới trùng trace-grader.
- Ledger mới (`harness/skill-evolve-ledger.jsonl`) đi theo đúng convention **gitignored local** của `failures.jsonl`/`events.jsonl` — không tự ý đổi thành git-tracked (khác quyết định của `provenance-log.jsonl`, vốn CỐ Ý git-track vì cần travel qua branch; ledger này thuần local-signal, không cần).

## Non-goals

- **Không** tự động SỬA nội dung SKILL.md — chỉ tự động **soạn stub đề xuất** rồi dừng ở `/propose` (giữ nguyên gate người duyệt, đúng convention `failure-flywheel`).
- **Không** train/fine-tune model gì cả — không có "policy update", không có reward số theo nghĩa RL. "Reward" ở đây là verdict tất định của `trace-grader` (an toàn/quy trình), không phải đo "task có đúng về mặt nghiệp vụ không" (câu đó cần domain judge, ngoài phạm vi v0.1).
- **Không** làm lại việc `orca-eval` đã làm (report tổng quát về best-practice toàn phiên) — `skill-evolve` hẹp hơn: CHỈ verdict gắn `skill_id`, tích luỹ, có ngưỡng, có auto-draft. Hai skill SONG SONG, không thay thế nhau.
- **Không** tự thêm skill MỚI (khác nhánh "skill bank thêm skill" của SkillRL) — v0.1 chỉ SỬA skill đã có. Thêm-skill-mới tự động là mở rộng tương lai, không phải bây giờ (rủi ro cao hơn nhiều: sửa 1 file có gate còn dễ review hơn tạo file mới hàng loạt).
- **Không** bật "agent-as-judge" (LLM chấm nội dung câu trả lời của skill) trong v0.1 — chỉ dùng verdict tất định của `trace-grader` (rule-based). Trục LLM-judge để ngỏ như một cấu hình TẮT, giống `trace-grader.config.yaml`'s `judge_trajectory()` đã làm — bật sau khi có model/ngưỡng thật.

## Approaches

**Phương án A — Correlator mỏng, tái dùng nguyên `skill-usage.py` + `trace-grader.py`, feed ledger riêng, tự soạn draft giàu ngữ cảnh (chọn).** Một script mới `harness/scripts/skill-evolve.py` KHÔNG viết lại logic chấm — nó chỉ: (1) quét transcript, tìm ranh giới mỗi lần gọi Skill-tool (tái dùng field `line_idx` mới thêm vào `skill-usage.py::collect()`); (2) cắt lát jsonl giữa hai ranh giới liền kề, gọi thẳng `trace_grader.runs_from_transcript()` + `grade_run()` (import qua `importlib.util`, đúng tiền lệ đã chạy sống trong repo) để lấy verdict tất định CHO ĐÚNG LẦN GỌI SKILL ĐÓ; (3) ghi verdict vào ledger cục bộ theo `skill_id`; (4) `--report` xếp hạng skill theo tỷ lệ `corrupt-success`/`fail` (chỉ tính khi đủ mẫu tối thiểu); (5) `--draft <skill_id>` khi vượt ngưỡng — khác `failure-flywheel --draft` (stub rỗng để người tự điền) ở chỗ stub này **tự nhúng sẵn** nội dung `SKILL.md` hiện tại + danh sách bằng chứng (session, rule vi phạm, verdict) để người duyệt sửa ngay tại chỗ, không phải đi tìm lại. Ưu điểm: không sửa 2 file lõi đã có test/hành vi ổn định, chi phí review thấp (1 file mới + 1 dòng thêm field). Nhược điểm: verdict chỉ phản ánh "an toàn/quy trình" (theo rule của trace-grader: forbidden-tool, retry-storm, edited-without-read…), KHÔNG phản ánh "câu trả lời có đúng về nghiệp vụ không" — chấp nhận, ghi rõ ở Non-goals, để ngỏ trục LLM-judge cho bản sau.

**Phương án B — Gắn signal-detection kiểu SkillRL/orca-eval (LLM đọc digest, tự phân loại correction/friction) làm reward chính, thay vì rule tất định của trace-grader.** Bám sát tinh thần SkillRL hơn (SkillRL cũng dùng "validation failure" — một dạng phán đoán, không phải rule cứng). Bác: mỗi lần scan phải gọi một model để phân loại digest (chi phí token cho MỖI phiên, MỖI skill invocation) và không tất định (2 lần chạy có thể ra kết luận khác nhau) — vi phạm nguyên tắc `trace-grader` đã chọn cho tầng rule ("Never present a guessed threshold as verified" áp tương tự cho verdict: đừng giả một điểm số suy luận khi chưa cấu hình+verify). Giữ lại làm **trục LLM-judge tuỳ chọn, tắt mặc định** — đúng pattern `trace-grader.config.yaml`'s `judge_trajectory()` STUB, không phải bản build ngay.

**Phương án C — Mở rộng `failure-flywheel.py` để nó tự nhận diện `skill:<id>` là category đặc biệt và tự động `record` từ transcript (không cần script mới).** Đơn giản hơn về số file, nhưng phá vỡ hợp đồng hiện tại của `failure-flywheel`: nó được thiết kế cho **agent gõ tay `record` khi tự nhận ra lỗi** (fail-open, tối giản, không transcript-parsing) — nhồi thêm logic quét transcript + cắt lát theo skill + gọi trace-grader vào MỘT file sẽ làm nó phình đôi trách nhiệm (manual-record ngắn gọn ↔ auto-scan phức tạp), và bất kỳ lỗi nào ở phần auto-scan mới sẽ rủi ro kéo theo cả đường manual-record đang chạy ổn định. Bác vì vi phạm "surgical changes" — sửa file dùng chung cho một trách nhiệm mới hoàn toàn khác trách nhiệm gốc của nó.

## Requirements (FR)

**FR-001**: `fdk/tools/skill-usage.py::collect()` PHẢI trả thêm field `line_idx` (chỉ số dòng 0-based của dòng chứa lời gọi Skill-tool trong file transcript) cho mỗi event — additive, không đổi field cũ (`skill`/`ts`/`week`/`session`), không đổi hành vi CLI hiện có (`--weekly`/`--json`/`--top`/`--dead-weeks`).

**FR-002**: Hệ thống PHẢI, cho mỗi session transcript được quét, xác định ranh giới TỪNG lần gọi Skill-tool (dùng `line_idx` từ FR-001) và cắt lát các dòng jsonl từ ranh giới này tới ranh giới kế tiếp (hoặc hết file) thành một lát cắt riêng cho lần gọi đó.

**FR-003**: Mỗi lát cắt PHẢI được chấm bằng `trace_grader.runs_from_transcript()` + `grade_run()` gọi qua `importlib.util.spec_from_file_location` (KHÔNG sửa `harness/scripts/trace-grader.py`), lấy đúng verdict tất định `clean-pass/pass-with-warnings/corrupt-success/fail` + danh sách flag đã có sẵn của engine đó.

**FR-004**: Verdict PHẢI được ghi thành một dòng vào `harness/skill-evolve-ledger.jsonl` (gitignored local, khuôn `failures.jsonl`): `{skill, session, ts, verdict, flags}`. Ghi PHẢI fail-open (lỗi ghi không chặn scan/phiên chính).

**FR-005**: `skill-evolve.py --scan [N]` PHẢI **idempotent** — quét lại cùng một session không được ghi trùng verdict cho cùng một lần gọi skill (dùng watermark theo `session + line_idx` đã xử lý, lưu trong `harness/skill-evolve.state.json`, khuôn tinh thần "đếm số LIVE, không hardcode" nhưng ở đây là tránh double-count chứ không phải đếm lại từ đầu).

**FR-006**: `skill-evolve.py --report` PHẢI xếp hạng theo skill: tổng số lần gọi, tỷ lệ `corrupt-success + fail` trên tổng, đánh dấu `DRAFT-ELIGIBLE` khi (a) đủ số mẫu tối thiểu (`min_sample`, config) VÀ (b) tỷ lệ vượt ngưỡng (`fail_rate_threshold`, config) — cùng khuôn hiển thị "leaderboard" của `failure-flywheel --report`.

**FR-007**: `skill-evolve.py --draft <skill_id>` CHỈ được chạy khi skill đó đang `DRAFT-ELIGIBLE`; PHẢI sinh file `llmwiki/wiki/sources/draft/DDMMYY-skill-evolve-<skill_id>.md` chứa: nội dung hiện tại của `SKILL.md` (đọc từ registry — xem FR-008), bảng bằng chứng (session/verdict/flag/snippet) của các lần gọi lỗi gần nhất, và **DỪNG** cho `/propose` hoàn thiện — không tự sửa `SKILL.md`.

**FR-008**: Hệ thống PHẢI định vị đúng file `SKILL.md` nguồn của một `skill_id` bằng cơ chế đã có (đường dẫn trong bảng skill của `AGENT.md`/`CLAUDE.md`, hoặc `fdk/CAPABILITIES.md`) — KHÔNG tự đoán đường dẫn bằng convention tên file.

**FR-009**: Toàn bộ ngưỡng số (`min_sample`, `fail_rate_threshold`) PHẢI sống trong ĐÚNG MỘT file `harness/skill-evolve.config.yaml`, `verified: false`, mỗi giá trị gắn `# ASSUMPTION` — khuôn `build-now-adapt-later`.

## Success criteria (SC)

**SC-001**: Cho một transcript có thật chứa ≥ 2 lần gọi Skill-tool khác nhau trong cùng session, `--scan` tạo ra đúng số dòng ledger bằng số lần gọi, mỗi dòng gắn đúng `skill_id` của lần gọi tương ứng (không lẫn verdict giữa hai skill).

**SC-002**: Chạy `--scan` hai lần liên tiếp trên cùng dữ liệu — số dòng ledger KHÔNG tăng gấp đôi (idempotent thật, không phải lời hứa).

**SC-003**: Một skill có ≥ `min_sample` lần gọi và tỷ lệ lỗi vượt ngưỡng — `--report` đánh dấu đúng `DRAFT-ELIGIBLE`; một skill dưới `min_sample` KHÔNG bao giờ bị đánh dấu (tránh kết luận từ mẫu quá nhỏ).

**SC-004**: `--draft <skill_id>` cho một skill hợp lệ tạo ra draft chứa **cả** nội dung SKILL.md hiện tại **và** bảng bằng chứng cụ thể (không phải khung rỗng chờ điền) — người duyệt đọc xong biết ngay đang sửa gì, dựa trên bằng chứng nào, không cần tự đi tìm thêm.

**SC-005**: Ngắt giả lập lỗi ghi ledger (đổi quyền file thành read-only) — `--scan` vẫn chạy xong, không crash, không chặn phiên (fail-open thật).

## Assumptions

- `fail_rate_threshold` mặc định **40%** — **(default, find-out-later → cần đo trên ledger thật sau vài tuần, U-06)**: mượn đúng con số SkillRL dùng cho việc RL của họ, chưa có cơ sở riêng cho verdict trace-grader.
- `min_sample` mặc định **5 lần gọi** — **(default)**: đủ để tránh 1 lần lỗi ngẫu nhiên kết luận cả skill tệ, chưa tối ưu bằng dữ liệu thật.
- Phạm vi verdict v0.1 CHỈ dùng rule tất định của `trace-grader` (an toàn/quy trình) — **(default)**: không đo đúng-sai nghiệp vụ, ghi rõ ở Non-goals, không phải thiếu sót bị bỏ quên.
- Ledger + state file đặt tại `harness/skill-evolve-ledger.jsonl` / `harness/skill-evolve.state.json` — **(default)**: theo đúng convention thư mục `harness/` của các ledger cục bộ khác (`failures.jsonl`, `events.jsonl`).
- `--scan` mặc định quét session HIỆN TẠI, nhận `[N]` để mở rộng — **(default)**: khuôn `orca-eval`/`skill-usage.py` đã dùng, người dùng quen lệnh này.

## Plan

**v0.1 — MUST, lõi chạy được:**
- [ ] **T1 — `fdk/tools/skill-usage.py::collect()` thêm field `line_idx` (additive).** Verify: FR-001; test cũ (`--weekly`/`--json`) vẫn xanh nguyên (self-test có sẵn trong file).
- [ ] **T2 — `harness/scripts/skill-evolve.py`: cắt lát transcript theo ranh giới Skill-tool, gọi `trace_grader.runs_from_transcript()`/`grade_run()` qua `importlib.util`, ghi `harness/skill-evolve-ledger.jsonl` fail-open + idempotent qua `harness/skill-evolve.state.json`.** Verify: FR-002/003/004/005, SC-001/002/005.
- [ ] **T3 — `harness/skill-evolve.config.yaml` (`verified:false`, `min_sample`/`fail_rate_threshold` mỗi giá trị `# ASSUMPTION`) + `--report` leaderboard.** Verify: FR-006/009, SC-003.
- [ ] **T4 — `--draft <skill_id>`: định vị `SKILL.md` nguồn (FR-008), nhúng nội dung + bằng chứng vào draft, dừng ở `/propose`.** Verify: FR-007, SC-004.
- [ ] **T5 — Bundled self-test (khuôn `trace-grader.py --self-test`/`skill-usage.py::self_test()`): fixture transcript giả lập 2+ lần gọi skill, 1 clean 1 corrupt-success, assert ledger + report + idempotency.** Verify: toàn bộ SC.

**v0.2 — SHOULD, hoãn có chủ đích:**
- [ ] **T6 — Wiring vào `/lint` (đúng cách `skill-usage.py --weekly` đã được gọi định kỳ) để `--scan` chạy tự động, không cần user gõ tay.** Verify: (default, U-07) — chưa có SC riêng, mở khi T1-T5 đã chạy sống đủ lâu để tin ngưỡng.
- [ ] **T7 — Trục agent-as-judge tuỳ chọn (đo đúng-sai nghiệp vụ, không chỉ an toàn/quy trình) — TẮT mặc định, khuôn `trace-grader.config.yaml`'s `judge_trajectory()` STUB.** Verify: (default) — mở khi có model+ngưỡng đã verify.

## Agent Task Assignment

| Task | Agent (CLI) | Lý do chọn | Status |
|---|---|---|---|
| T1 | Claude | Field additive vào hàm dùng chung — cần đọc kỹ mọi call-site (`build_report`, `--json`) để chắc không phá hành vi cũ | pending |
| T2 | Claude | Glue logic mới (cắt lát + import chéo qua `importlib`) — cần hiểu đúng contract `runs_from_transcript`/`grade_run` để không gọi sai shape input | pending |
| T3 | Claude | Ngưỡng + report leaderboard là quyết định thiết kế (cách đếm, cách xếp hạng), không phải thao tác cơ học | pending |
| T4 | Claude | Định vị SKILL.md nguồn + soạn draft giàu ngữ cảnh cần đọc đúng registry, tránh đoán sai đường dẫn (FR-008 cấm đoán) | pending |
| T5 | OpenCode (rẻ) | Viết fixture test theo khuôn đã có sẵn ở `trace-grader.py --self-test`, thao tác lặp lại một pattern đã biết | pending |
| T6 | OpenCode (rẻ) | Thêm một dòng gọi vào `/lint` theo đúng chỗ `skill-usage.py --weekly` đã được gọi | pending |
| T7 | Claude | Thiết kế trục judge cần phán đoán, không phải thao tác cơ học | pending |

## Self-review

**Phủ yêu cầu.** Yêu cầu gốc "distill SkillRL → loop tự cải thiện skill" về đủ: cơ chế phân tầng skill-bank của SkillRL → khái niệm "verdict per-skill tích luỹ" (T1-T3); cơ chế "ngưỡng rớt → tự sinh candidate cải tiến" → T4 (draft giàu ngữ cảnh, khác `failure-flywheel`'s stub rỗng); khác biệt RL-thật vs markdown-skill → khai rõ ở Context + Non-goals, không giả vờ port nguyên khối.

**Quét placeholder.** Rà toàn văn không còn mục nào bỏ ngỏ kiểu "việc này để sau tính" hay "xử lý cho hợp lý" — mọi mục Non-goals có lý do cụ thể, mọi Assumption có tag `(default)` hoặc `(default, find-out-later → U-NN)`.

**Nhất quán tên-kiểu.** `skill_id`/`skill-evolve.py`/`skill-evolve-ledger.jsonl`/`skill-evolve.config.yaml`/`skill-evolve.state.json` dùng thống nhất xuyên FR/Plan/Assumptions — không lẫn với `failure-flywheel`'s `failures.jsonl` hay `trace-grader`'s `traces.json`.

## Origin
- **Source:** GitHub issue [Rheinmir/setup#84](https://github.com/Rheinmir/setup/issues/84) — "skill improve loop", body trỏ `https://github.com/aiming-lab/SkillRL.git`.
- **Research:** agent Explore (phiên 2026-07-24) — WebFetch README SkillRL + đọc `failure-flywheel.md`/`trace-grader.md`/`skill-usage.py`/`orca-eval.md`/`new-skill.md`; xác nhận tại chỗ tiền lệ `importlib.util.spec_from_file_location` (grep `harness/scripts/*.py`, `fdk/tools/*.py`) và contract `runs_from_transcript(lines, task_hint)` (đọc trực tiếp `harness/scripts/trace-grader.py`).
- **Concept nền:** `[[problem-tree]]` (nợ framework chưa trả) — nhánh hẹp: nợ chất lượng per-skill.
- **Task:** `T-260724-01`
