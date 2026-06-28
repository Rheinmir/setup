---
type: concept
title: FDK — Framework Development Kit (bộ xương phát triển framework)
status: active
tags: [fdk, framework, harness, workflow, front-door, anti-drift, anti-collision]
timestamp: 2026-06-27
---

# FDK — Framework Development Kit

Đây là **lối vào duy nhất** cho mọi việc phát triển *bản thân* framework này (thêm/sửa skill, rule, validator, script, hook, hay tài liệu wiki). Mục đích của FDK chỉ có hai: **không bao giờ miss một rule** và **không bao giờ dẫm/đá lên phần đã có**. Đọc trang này trước khi đụng vào bất kỳ phần nào của framework.

Nguyên tắc nền: FDK **không chép lại** nội dung của các tài liệu con và **không hardcode con số** (số skill, số file…). Con số luôn lấy *trực tiếp từ đĩa* bằng lệnh inventory bên dưới, nên FDK tự miễn nhiễm với chính loại drift mà nó phòng. Mỗi mục dưới đây chỉ trỏ tới nguồn chân lý tương ứng.

**Bản đọc HTML:** `llmwiki/html/270626-fdk-docs.html` (docs-site-macos glass, offline-proof) — trang đọc đẹp của chính file này.

**Cửa chủ động — gọi `/fdk`, KHÔNG auto-bơm:** gọi skill `/fdk` khi — và chỉ khi — đang phát triển *chính* framework. Nó nạp front-door (trang này) + in inventory *live* (skill / validator / script / hook / rule đếm từ đĩa) + nhắc pre-flight. **Cố ý KHÔNG đăng ký vào SessionStart**: phần lớn phiên là dùng framework để dev *dự án khác*, nên auto-bơm nội-bộ-framework vào đó là nhiễu — framework-dev context phải opt-in (xem [[ADR-004-framework-dev-context-opt-in]]). Pointer `/fdk` nằm trong `AGENT.md`/`CLAUDE.md` (auto-load) dưới dạng điều kiện, không phải directive vô điều kiện.

## "Đã có chưa?" — tình trạng bộ xương (2026-06-27)

| Mảnh xương | Trạng thái | Nguồn |
|---|---|---|
| Danh sách rule (never-miss) | ✅ có | [[rule-registry]] + `harness/poc-vendor-neutral/policy.yaml` |
| Runbook thêm/sửa rule | ✅ có | `fdk/docs/CONTRIBUTING.md` |
| Kiến trúc harness + cách cook vendor | ✅ có | `harness/recipe.md`, `harness/poc-vendor-neutral/DOCS.md` |
| Quyết định kiến trúc | ✅ có | [[ADR-001-policy-as-source-of-truth]], [[ADR-002-pull-before-change-gates]], [[ADR-003-skill-as-single-source-of-truth]] |
| Luồng dev (propose → verify) | ✅ có | skill `propose`, `impact-check`, `safe-change`, `verify-before-commit` |
| **Front-door hợp nhất** | ❌ thiếu → **trang này lấp** | — (AGENT.md trước đây không trỏ tới gì) |
| **Module map chống-dẫm-chân** | ⚠️ có nhưng **drift** | [[project-structure]], [[architecture]] (số liệu cũ) → dùng lệnh inventory ở Phần 3 |

Tóm lại: phần *rule* gần đủ, nhưng *trước nay rải rác và không có cổng vào*; phần *chống va chạm module* yếu vì map cũ đã lệch. FDK hợp nhất chúng thành một spine + cổng pre-flight.

---

## Phần 1 — Cổng pre-flight cho MỌI thay đổi framework

Chạy theo đúng thứ tự này. Mỗi bước trỏ tới công cụ/runbook chịu trách nhiệm; FDK chỉ điều phối.

1. **Đồng bộ trước (R12).** `bash harness/poc-vendor-neutral/bin/pull-gate-sweep.sh` (nhiều subrepo) hoặc `pull-gate.sh` (1 repo). Không bao giờ sửa trên base cũ.
2. **Biết luật (Phần 2).** Mở [[rule-registry]]; nếu việc bạn làm tạo file wiki / seq-html / proposal / sửa raw → có rule gác. Đừng đoán.
3. **Đừng dẫm module cũ (Phần 3).** Chạy lệnh inventory + grep tên trước khi tạo skill/validator/script/hook mới. Sửa code dùng-chung → `impact-check` rồi `safe-change`.
4. **Propose trước (dev-loop).** Mọi thay đổi → skill `propose` tạo cặp `.md`+`.html`, STOP chờ duyệt. Nếu là thêm/sửa **rule harness** → theo `fdk/docs/CONTRIBUTING.md` (có cổng quyết định ADR-001/002 riêng).
5. **Làm — surgical.** Chỉ chạm cái phải chạm; giữ style cũ; bản sao mirror phải giữ `diff` = SAME.
6. **Verify trước commit.** `verify-before-commit` + drift-test liên quan (`policy-converters-drift-test.sh` nếu đụng policy). CI thật = `harness.yml` (`llmwiki-validate files` + `demo.sh` + `test-broad.sh`).
7. **Ghi vết.** Cập nhật [[rule-registry]] (nếu rule), `decisions.md`/`log.md` 1 dòng, ADR nếu là quyết định kiến trúc.

> **Design rule — khi thêm bất kỳ auto-fire / injected context nào** (hook SessionStart/UserPromptSubmit, dòng auto-load trong AGENT/CLAUDE, banner đầu phiên): hỏi *"phục vụ DỰ ÁN HIỆN TẠI hay nội-bộ-framework?"*. Chỉ loại đầu được auto-fire; context nội-bộ-framework (FDK, inventory, runbook sửa rule) phải **opt-in** qua skill gọi chủ động. Đừng lặp lỗi auto-bơm FDK — xem [[ADR-004-framework-dev-context-opt-in]]. Luật ghim trong repo (AGENT/CLAUDE + đây) vì memory cá nhân không theo git.

---

## Phần 2 — Không bao giờ MISS rule

Nguồn chân lý máy-đọc là `harness/poc-vendor-neutral/policy.yaml`; bản người-đọc hợp nhất là [[rule-registry]]. Để xem **danh sách rule hiện hành ngay lúc này** (đừng tin số nhớ trong đầu):

```bash
grep -E 'id: R' harness/poc-vendor-neutral/policy.yaml          # liệt kê R1..Rn đang active
```

Rule được gác ở ba tầng, hiểu để biết cái nào chặn bạn lúc nào:

- **PreToolUse / write-time** — validator chặn ngay khi ghi file (vd R7 chặn proposal thiếu cặp html, R1 chặn ghi `raw/`).
- **pre-commit / commit-time** — `.pre-commit-config.yaml` chạy lại toàn bộ validator (R2/R5/R7/R9/R3/L4…).
- **CI / push-time** — `harness.yml` chạy `llmwiki-validate files` trên file đổi + `demo.sh`/`test-broad.sh`.

Muốn THÊM/SỬA một rule → KHÔNG sửa ở đây. Theo `fdk/docs/CONTRIBUTING.md` (phân loại content-check / hook-event / process-gate, "thick policy / thin adapter", số hiệu kế tiếp là **R13**).

---

## Phần 3 — Không bao giờ DẪM module cũ

Trước khi tạo một thứ "mới", kiểm tra nó **chưa tồn tại**. Map theo *loại* (loại thì ổn định, số lượng thì không — nên đếm live):

| Loại module | Ở đâu | Trước khi thêm, chạy |
|---|---|---|
| Skill (published) | `skills/<name>/SKILL.md` | `ls -d skills/*/` rồi `grep -ri "<từ khoá>" skills/*/SKILL.md` |
| Skill (canonical, theo loop) | `llmwiki/skills/<loop>/<name>.md` | `ls llmwiki/skills/*/` |
| Validator (content rule) | `harness/validators/*.py` | `ls harness/validators/` |
| Script (vận hành) | `harness/scripts/*.py`, `*.sh` | `ls harness/scripts/` |
| Lõi vendor-neutral | `harness/poc-vendor-neutral/bin/*` | `ls harness/poc-vendor-neutral/bin/` |
| Hook phiên (Claude) | `llmwiki/.claude/hooks/*.py` | `ls llmwiki/.claude/hooks/` |
| Policy | `harness/policy.yaml` (L0 prod) · `harness/poc-vendor-neutral/policy.yaml` (PoC executable) | xem [[rule-registry]] §"Hai file policy.yaml" |
| Thư mục wiki | `fdk/wiki/{concepts,entities,sources,sources/adr,sources/draft,draft}` | `ls fdk/wiki/` |

Một lệnh quét nhanh toàn bộ bề mặt (in inventory hiện tại, không drift):

```bash
echo "skills:        $(ls -d skills/*/ | wc -l)"
echo "canon-skills:  $(ls llmwiki/skills/*/*.md | wc -l)"
echo "validators:    $(ls harness/validators/*.py | wc -l)"
echo "scripts:       $(ls harness/scripts/* | wc -l)"
echo "poc-bin:       $(ls harness/poc-vendor-neutral/bin/* | wc -l)"
echo "hooks:         $(ls llmwiki/.claude/hooks/*.py | wc -l)"
echo "rules:         $(grep -cE 'id: R' harness/poc-vendor-neutral/policy.yaml)"
```

Khi sửa **code dùng-chung** (một symbol gọi từ nhiều nơi): chạy skill `impact-check` (liệt kê caller/dependent) rồi `safe-change` (sửa mà không vỡ caller cũ). Đây là tuyến phòng "đá chân" ở mức code, bổ sung cho map ở mức file.

Quy ước **single source of truth** để không tạo bản trùng phân kỳ: skill có *canonical* + *mirror* phải giữ `diff` = SAME; rule sống ở `policy.yaml`, không nhân bản; tài liệu người-đọc do người viết, phần render/markup có thể delegate (xem [[ADR-003-skill-as-single-source-of-truth]]).

---

## Bản đồ toàn bộ xương (index của các bone)

| Bone | File | Vai trò |
|---|---|---|
| **FDK (trang này)** | `fdk/wiki/concepts/fdk.md` | Front-door + pre-flight + map |
| Rule registry | [[rule-registry]] | R1..Rn, đánh dấu chỗ lệch |
| Runbook rule | `fdk/docs/CONTRIBUTING.md` | Thêm/sửa rule không cần đọc đầu tác giả |
| **Kit folder (vật lý)** | `fdk/` | `tools/` (build-cheatsheet…) + `docs/` (CONTRIBUTING) + README map |
| Recipe harness | `harness/recipe.md` | Kiến trúc 5 lớp, cook vendor mới |
| DOCS vendor-neutral | `harness/poc-vendor-neutral/DOCS.md` | Cách hoạt động + cài đặt chi tiết |
| ADR | `fdk/wiki/sources/adr/ADR-00N-*.md` | Quyết định kiến trúc |
| Module map | [[project-structure]], [[architecture]] | Tổng quan (kiểm chéo bằng lệnh Phần 3) |
| Dev-loop skills | `propose`, `impact-check`, `safe-change`, `verify-before-commit` | Vòng làm-việc an toàn |

## Phần 4 — Cơ chế adapt: framework đã đủ mở để luôn thêm cái mới chưa?

Câu hỏi sống còn của một framework: thêm một năng lực mới có phải sửa lõi không, hay chỉ cần cắm vào một điểm mở rộng có sẵn? Nếu mỗi cái mới đều đụng lõi thì framework sẽ cứng lại và chết. Dưới đây là các **điểm cắm (extension points)** — nơi thêm cái mới mà KHÔNG đụng engine, cùng câu trả lời cho "đủ mở chưa".

### Điểm cắm — thêm cái mới ở đâu (không sửa lõi)

| Thêm gì | Cắm vào đâu | Không đụng |
|---|---|---|
| **Rule mới** | thêm 1 entry vào `harness/poc-vendor-neutral/policy.yaml` (thick policy / thin adapter, [[ADR-001-policy-as-source-of-truth]]) | `llmwiki-validate.py` (chỉ thêm `kind` mới mới đụng) |
| **Skill mới** | `skills/<name>/SKILL.md` + canonical mirror + `LOOP_MAP` + bảng AGENT/CLAUDE — hoặc một lệnh `/new-skill` | engine |
| **Tool mới** | `fdk/tools/<x>.py` (dev-framework) hoặc `harness/scripts/<x>.py` (vận hành) | engine |
| **Ẩn số chưa rõ** | một **adapter + config** (`verified:false`) — BNAL; `adapt-registry` gác không cho rò | mọi nơi khác |
| **Gate mới (định-nghĩa-hoàn-thành)** | thêm 1 dòng vào `STEPS` của `fdk-gate.py` + checklist dưới | engine |

### Tự-gác để adapt mà KHÔNG vỡ
Mở rộng dễ thì dễ vỡ — nên mỗi điểm cắm có một validator code canh: `harness-lint` (hằng số/wiring không drift), `agent_claude_parity` + `skill-registry` (skill khai đủ mọi bề mặt), `duplicate_basename` (không trùng), `harness-doctor` (rail còn cắn), `adapt-registry` (ẩn số không rò), `build-capabilities` (agent biết đúng đồ nghề), và `fdk-gate` gom tất cả thành "đủ step mới cho push".

### Audit — câu trả lời: **ĐỦ MỞ** (có điều kiện)
Bằng chứng sống: trong **một phiên** đã thêm hơn **14 chức năng** (registry, harness-lint, artifacts, harness-doctor, health-dashboard, wiki-graph, adapt-registry, docs-index, new-skill, skill-search, council, loop-runner, wikieval, trace-grader, failure-flywheel, code-logger, build-capabilities, fdk-gate, index_sync --fix) mà **lõi `llmwiki-validate.py` không đổi một dòng** — mọi cái đều cắm vào điểm mở rộng có sẵn. Pattern **BNAL adapter** khiến cả ẩn số cũng adapt được bằng cách sửa MỘT file. Đó là định nghĩa "đủ mở".

**Điều kiện/giới hạn còn lại** (hướng adapt tiếp, từ khảo sát trend 2026): (1) **durable-execution / checkpoint-resume** — chưa snapshot được trạng thái run để hồi phục sau crash; (2) **layered guardrails 4 điểm** (input / tool-call / tool-response / final-output) như một config tường minh; (3) **permissions + lọc prompt-injection/credential** mặc định. (Ba hướng đã được lấp một phần: eval-gate = WikiEval, trajectory = TraceGrader, self-evolving = FailureFlywheel.) → framework mở đủ để thêm cả ba cái này theo đúng pattern điểm-cắm, không cần viết lại.

## Checklist — dev MỘT chức năng mới cho HỢP LỆ (fdk-gate enforce)

Khi thêm một chức năng/skill/rule/tool mới, để được push hợp lệ phải đủ các bước sau (bản máy-đọc là `harness/scripts/fdk-gate.py`):

1. **Code + self-test** — script chạy được, có test dương + **test âm** (cố tình sai → đỏ).
2. **Nếu là RULE** → thêm vào `policy.yaml`, regen converters, drift-test xanh, cập nhật [[rule-registry]].
3. **Nếu là SKILL** → canonical + mirror byte-identical, khai `LOOP_MAP`, thêm dòng vào **CẢ** AGENT.md & CLAUDE.md (giữ parity), rồi `build-capabilities` để CAPABILITIES.md cập nhật.
4. **Nếu là VALIDATOR/GATE** → wire vào `.pre-commit-config.yaml` + CI (`harness.yml`) + thêm step vào `fdk-gate.py`.
5. **Nếu có ẩn số** → nhốt sau 1 adapter (`verified:false`) + ADAPT-CHECKLIST; `adapt-registry --check` phải xanh.
6. **Wiki "vì sao"** — một entry/dòng giải thích tại sao cần nó (`## Origin` + frontmatter).
7. **Docs người-đọc** — cập nhật bản đọc tổng (master-wiki HTML) / trang docs liên quan.
8. **`python3 harness/scripts/fdk-gate.py` → GREEN** (mọi step pass) → mới push.

## Origin
- **Source:** khảo sát trực tiếp `harness/` + `llmwiki/` phiên 2026-06-27 — hợp nhất rule-registry, CONTRIBUTING-harness, recipe, DOCS, ADR và dev-loop skills thành một front-door; lấp gap "không có lối vào" + "map module drift".
- **Request:** user — `/goal` "bộ xương phát triển framework (FDK) chuẩn: không miss rule, không dẫm module cũ".
- **Liên quan:** [[rule-registry]], [[architecture]], [[project-structure]], [[ADR-001-policy-as-source-of-truth]], [[ADR-003-skill-as-single-source-of-truth]].
