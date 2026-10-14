# Behavioral guidelines — distilled from Karpathy's CLAUDE.md
Giảm lỗi LLM-coding phổ biến. Thiên về cẩn trọng hơn tốc độ; task tầm thường thì dùng phán đoán.

1. **Think before coding.** Đừng đoán, đừng giấu chỗ mơ hồ. Khai assumption; nhiều cách hiểu → trình ra, đừng tự chọn; có cách đơn giản hơn → nói + push back; chưa rõ → dừng, hỏi.
2. **Simplicity first.** Code tối thiểu giải đúng vấn đề, không suy diễn — không thêm feature/abstraction/"flexibility"/error-handling cho ca bất khả. 200 dòng mà 50 đủ → viết lại. "Senior có chê overcomplicated không?" → đơn giản hoá.
3. **Surgical changes.** Chỉ chạm cái buộc phải chạm. Đừng "cải thiện"/refactor code lân cận; giữ style cũ; dead-code lạ thì nêu, đừng xoá. Chỉ dọn orphan do CHÍNH thay đổi của bạn tạo ra. Mỗi dòng đổi phải truy về đúng yêu cầu.
4. **Goal-driven execution.** Biến task thành mục tiêu kiểm chứng được ("add validation" → viết test fail rồi làm pass). Việc nhiều bước → nêu plan ngắn, mỗi bước kèm cách verify. Success criteria mạnh giúp loop độc lập; criteria yếu ("làm cho chạy") thì phải hỏi liên tục.

Đạt khi: diff bớt thừa, bớt viết-lại do overcomplicate, câu hỏi làm rõ đến TRƯỚC khi sai — không phải sau.

(Nguồn: 4 nguyên tắc của Karpathy CLAUDE.md, bản distill của Forrest Chang — `multica-ai/andrej-karpathy-skills`. Bối cảnh framework: rule + skill cụ thể nằm ngay dưới.)

## 5-Why — chạy TRƯỚC mọi việc, không phải tuỳ chọn

Trước khi sửa hay xây bất cứ thứ gì, hỏi **"vì sao"** cho tới khi chạm **cấu trúc** sinh ra nó — thường là năm tầng. Bỏ qua bước này là cách nhanh nhất để vá triệu chứng, và bug sẽ tái sinh dưới một cái tên khác.

- **Viết chuỗi ra, đừng nghĩ thầm.** Chuỗi viết ra thì người khác kiểm được; chuỗi nghĩ trong đầu luôn "hợp lý" với chính người nghĩ.
- **Dừng đúng chỗ.** Chạm cấu trúc thì dừng: một vòng phản hồi thiếu, một cái tên hứa nhiều hơn hành vi, một cổng chỉ báo mà không chặn. Dừng ở *"vì người ta quên"* là chưa tới đáy — quên là hằng số của con người, không phải nguyên nhân.
- **Tìm HỘI TỤ trước khi sửa.** Chạy 5-Why cho vài triệu chứng đang có cùng lúc; nhiều cái đổ về một root thì sửa root **một lần**, đừng vá N chỗ. Đo 2026-07-20: thẻ ghi-tạm tồn **19/20**, issue mở **24**, pattern lệch upstream **15**, file chưa rà wiki **39**, task orchestration treo **17** — năm cái sổ khác nhau, **một** root: hệ rất giỏi PHÁT HIỆN nợ và không có nhịp TRẢ nợ. Lúc đó phản xạ sai là thêm bộ phát hiện thứ sáu.
- **Nghi ngờ chẩn đoán đầu tiên của chính mình.** Nó thường là suy luận từ triệu chứng chứ chưa đọc code. Cùng ngày: tôi kết luận code-graph "ghi và đọc trỏ hai DB khác nhau" — sai; đọc code thì ra *một* DB thiếu schema giết cả fan-out. Chẩn đoán chỉ được tin sau khi **tái hiện** được.
- **Ngoại lệ duy nhất:** việc không chứa chẩn đoán nào — đổi tên, format, regen artifact, chép nguyên văn. Việc nào có chữ "sửa", "hỏng", "vì sao", "sao lại thế" thì luôn chạy.

## Chứng cứ trong CHAT — opt-in qua `/graph-mode`, không auto-bơm mỗi phiên

Luật chuỗi-lập-luận-phải-chạm-chứng-cứ (6 loại điểm cuối, chi tiết [[evidence-terminal-chain]])
GIỜ nằm ở `skills/graph-mode/SKILL.md`, không còn bơm mặc định vào mọi phiên — kỷ luật này buộc
trích dẫn/mở file nhiều hơn mỗi câu trả lời (nặng token), nên chỉ bật khi thật cần độ tin cậy cao
(audit, ADR, chẩn đoán lan rộng). Gọi `/graph-mode` để bật, "tắt graph mode"/"normal mode" để tắt.
Validator máy trên tài liệu ```evidence-chain (R19, `harness/validators/evidence_terminal.py`) KHÔNG
phụ thuộc skill này — luôn chạy qua `harness/policy.yaml` bất kể graph-mode bật hay tắt.

## Cái thang chống over-engineering — chạy khi VIẾT/SỬA code
Karpathy ở trên là "vì sao"; đây là "làm sao". (Chưng cất từ ponytail, MIT — nguồn `060726-ponytail-distill`.)

**Hiểu bài trước, leo thang sau.** Đọc code, trace flow end-to-end rồi mới sửa. Diff nhỏ ĐẶT SAI CHỖ = bug thứ hai.

**Cái thang — dừng ở bậc đầu tiên đứng vững:** (1) YAGNI — thứ này có cần tồn tại không? bậc rẻ nhất là xoá → (2) codebase đã có chưa? tái dùng → (3) stdlib giải được không? → (4) native platform? CSS thay JS, DB constraint thay app-code → (5) dependency đã cài rồi? → (6) 1 dòng được không? → (7) cuối cùng mới viết code tối thiểu.

**Bug = root cause, không vá triệu chứng.** Grep mọi caller, sửa 1 lần ở hàm chung — fix root-cause thường diff NHỎ HƠN vá từng caller.

**Marker nợ có kỷ luật** — shortcut cố ý phải để lại comment `shortcut: <trần hiện tại>, <trigger nâng cấp>` (vd `# shortcut: global lock, đổi per-account nếu throughput thành vấn đề`). Grep được → nợ có hạn, không thành "never". Marker thiếu trigger bị `/lint` cắn.

**Carve-out — KHÔNG lười ở:** validation tại trust boundary, error-handling chống mất data, security, a11y, calibration phần cứng, và bất cứ thứ gì user YÊU CẦU rõ. Logic non-trivial phải để lại ĐÚNG 1 check chạy được (assert demo / 1 test nhỏ) — YAGNI áp cho cả test, nhưng không phải 0 test.

**Format báo cáo rút gọn (vd khi chạy `/simplify`):** mỗi finding 1 dòng `L<line>: <tag>: <trước> → <sau>`, tag ∈ {delete, stdlib, native, yagni, shrink}; chốt `net: -N dòng`. Không có gì để cắt → "Lean already. Ship."

**Output:** code trước, tối đa 3 dòng "skipped X, add when Y". Giải thích dài hơn code → xoá giải thích.

## Rules
- 🧰 **Đồ nghề bạn CÓ — đừng làm lại thứ đã tồn tại:** bản đồ năng lực sinh-bằng-code, luôn-mới (ADR-005): repo framework → `fdk/CAPABILITIES.md` (skill+rule+tool); dự án downstream → `CAPABILITIES.md` ở gốc (build-capabilities deploy cạnh hooks, đọc global skills + rule đã cài). Không chắc có gì cho việc đang làm → ĐỌC nó, hoặc `find-skills "<việc>"`. Sinh lại: `python3 fdk/tools/build-capabilities.py` (downstream tự nhận bối cảnh khi chạy với `--root`).
- **Đang phát triển CHÍNH framework này (skill/rule/validator/script/hook/wiki)? Gọi `/fdk`** — on-demand front-door: pre-flight + không miss rule + không dẫm module cũ. KHÔNG auto-bơm đầu phiên vì phần lớn phiên là dùng framework để dev DỰ ÁN KHÁC (xem `ADR-004`).
- **Nhiều phiên chung một working tree → KHÔNG `git add -A` / `git add .` / `git commit -a`:** chỉ stage pathspec tường minh của đúng file mình sửa. Phiên khác có thể đang dở việc trên cùng cây, stage hàng loạt sẽ cuốn việc của họ vào commit của mình (2 sự cố 03/07/2026). Ở repo framework, rule P1 `harness-local/validators/no_bulk_stage.py` chặn lệnh này và chặn commit file mà phiên khác ghi lần cuối (`OVS_ALLOW_CROSS_SESSION=1` nếu cố ý). Việc dài thì tách worktree riêng.
- **Design rule (feedback 2026-06-27):** thứ gì auto-fire/tự-bơm context vào MỌI phiên (hook SessionStart/UserPromptSubmit, dòng auto-load) chỉ được phục vụ *dự án hiện tại*; context *nội-bộ-framework* (FDK, inventory, runbook sửa rule) phải **opt-in** qua skill gọi chủ động. Luật này nằm ở đây (theo repo) vì memory cá nhân là máy-local, kéo repo máy khác sẽ mất. Xem `ADR-004`.
- FOLLOW the instructions in README.md in wiki folder
- EVERY wiki file must have an `## Origin` section — source is always traceable
- NEVER write to `raw/`
- ALWAYS update `wiki/index.md` when adding or removing a wiki file
- Cột Summary trong `index.md` PHẢI là một câu mô tả nội dung thật (cái gì, để làm gì) — KHÔNG được chỉ là ngày tháng hay lặp lại tên file; ngày đã có sẵn trong tên file rồi, một dòng summary trơ ngày là vô dụng với người đọc. `wiki-health.py --fail-on summary` bắt lỗi này.
- ALWAYS append to `wiki/log.md` after every operation
- Use `[[wikilinks]]` to cross-reference entries in `wiki/`
- Wiki files live in `concepts/`, `entities/`, `sources/`, `draft/`, `architecture/`, or `tours/` — never in `wiki/` root (enforced by R5 validator)
- Wiki entries are only created AFTER code is committed — never during proposal or planning
- Match a file's verbosity to its reader. Markdown that a machine or agent reads and executes (SKILL.md, policy.yaml, AGENT.md, pure reference tables) may be concise. Documentation a human reads or reviews (review reports, ADRs, README, CONTRIBUTING and runbooks, output-reports, HTML pages) must be full, readable prose with complete sentences — never caveman or over-compressed shorthand there; caveman is only for ephemeral agent-to-agent messages. (Feedback 2026-06-27.)

## Skills

Skill **không còn nằm trong repo này**: nguồn là [Rheinmir/skills](https://github.com/Rheinmir/skills), cài global vào `~/.claude/skills`
(`npx -y skills add rheinmir/skills#main --global --all`; bootstrap của overstack tự làm). Danh sách + mô tả đang có trên máy:
`CAPABILITIES.md` (sinh bằng `build-capabilities.py`). Mỗi SKILL.md khai `metadata.loop` (wiki-loop · dev-loop · orchestrate · utils)
và `metadata.requires` (sàn harness, binary, script engine) — kiểm bằng `python3 ~/.claude/harness/harness/scripts/skill-requires.py check --installed`.

## Invocation rules
- New file in `raw/` → invoke `ingest` immediately
- New feature request → invoke `propose` first, stop, wait for approval
- Edit to shared code → invoke `impact-check` then `safe-change`
