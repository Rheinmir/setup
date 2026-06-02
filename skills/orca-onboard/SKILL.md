---
name: orca-onboard
description: "Parallel codebase onboarding with Orca agents — multi-agent pipeline inspired by Understand-Anything. Generates knowledge graph, architecture layers, guided tour, and llmwiki entries."
---

# orca-onboard

Onboard codebase mới. Phân tích song song, tạo knowledge graph, layers, tour, wiki.

## Khi nào dùng
- "onboard codebase", "phân tích codebase"
- "tạo knowledge graph", "guided tour"

## Options
- `--full` — Rebuild hết
- `--language <lang>` — Ngôn ngữ output (vi, en, zh, ...)
- `--skip-tour` — Bỏ tour
- `--skip-wiki` — Bỏ wiki
- `<path>` — Phân tích thư mục khác

## Progress
```
[Phase 1/7] Scan project...
[Phase 2/7] Analyze files...
[Phase 3/7] Architecture layers...
[Phase 4/7] Knowledge graph...
[Phase 5/7] Guided tour...
[Phase 6/7] Validate graph...
[Phase 7/7] Generate wiki...
```

---

## ⚠️ HARD RULE — ĐỌC TRƯỚC KHI LÀM BẤT KỲ THỨ GÌ

⛔ **KHÔNG được chạy Phase 0.5 Gate hay bất kỳ Phase nào (1–7) nếu Phase 0 chưa hoàn thành.**

**Thứ tự bắt buộc — không được đảo:**
1. **Phase 0 (Pre-flight)** → chạy xong, kiểm tra `llmwiki/` tồn tại → ✅
2. **Phase 0.5 (Gate)** → hỏi user xác nhận
3. **Phases 1–7** → execute

**Nếu `llmwiki/` chưa tồn tại:** bootstrap NGAY tại Phase 0. KHÔNG defer, KHÔNG skip.
**Nếu bootstrap fail:** DỪNG HOÀN TOÀN, báo lỗi. Không hiện Gate, không tiếp tục.
**Nếu agent bỏ qua Phase 0 hay chạy Phase 0.5 trước Phase 0:** đó là bug — quay lại Phase 0 ngay.

---

## Phase 0 — Pre-flight

```bash
# Resolve project root
PROJECT_ROOT=${1:-.}
test -d "$PROJECT_ROOT" || exit 1

# Bootstrap llmwiki nếu chưa có
if [ ! -d "$PROJECT_ROOT/llmwiki" ]; then
  echo "[orca-onboard] llmwiki chưa có — kéo template từ rheinmir/setup..."
  git clone https://github.com/rheinmir/setup.git /tmp/orca-llmwiki-bootstrap --depth 1 -q
  cp -r /tmp/orca-llmwiki-bootstrap/llmwiki "$PROJECT_ROOT/llmwiki"
  rm -rf /tmp/orca-llmwiki-bootstrap
  echo "[orca-onboard] llmwiki bootstrapped OK"
fi

# Create dirs
mkdir -p $PROJECT_ROOT/.orca-onboard/{intermediate,tmp}
mkdir -p $PROJECT_ROOT/llmwiki/wiki/draft/{cave,uiux,orca}

# Get git info
git rev-parse HEAD 2>/dev/null > $PROJECT_ROOT/.orca-onboard/tmp/commit.txt
git ls-files > $PROJECT_ROOT/.orca-onboard/tmp/files.txt 2>/dev/null || find $PROJECT_ROOT -type f > $PROJECT_ROOT/.orca-onboard/tmp/files.txt
```

---

## Agent Binaries

| Agent | Binary | Kiểm tra |
|-------|--------|----------|
| Antigravity | `agy` | `agy --version` |
| OpenCode | `opencode` | `opencode --version` |
| Kiro | `kiro-cli` | `kiro-cli --version` |
| Orca | GUI — dùng qua `orca terminal *` | `orca terminal list` |

> Dispatch pattern chuẩn cho mỗi phase:
> ```bash
> TASK_ID=$(orca orchestration task-create --spec "<spec>")
> orca orchestration dispatch --task $TASK_ID --to <agent> --inject \
>   || orca terminal send --title "<Agent>" --text "<spec>"
> orca terminal wait --for tui-idle && orca terminal read --title "<Agent>"
> ```

---

## Phase 0.5 — Gate

Trước khi bắt đầu, tạo gate chờ user xác nhận:

```bash
orca orchestration gate-create --question "Bắt đầu onboard $PROJECT_ROOT? (7 phases, có thể mất vài phút)"
```

---

## Phase 1 — Scan Project

**Agent:** Antigravity (`agy`)

**Làm gì:**
- Đọc manifest: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `README.md`
- Phân loại files: code, config, docs, infra, data, script, markup
- Đếm dòng code
- Build import map

**Output:** `.orca-onboard/intermediate/scan-result.json`

```bash
SPEC="Scan $PROJECT_ROOT: enumerate files, detect languages, build import map. Write JSON to .orca-onboard/intermediate/scan-result.json"
TASK_ID=$(orca orchestration task-create --spec "$SPEC")
orca orchestration dispatch --task $TASK_ID --to agy --inject \
  || orca terminal send --title "Antigravity" --text "$SPEC"
orca terminal wait --for tui-idle && orca terminal read --title "Antigravity"
```

---

## Phase 2 — Analyze Files (Parallel)

**Agent:** Antigravity + OpenCode song song — mỗi batch 1 agent.

Chia files thành batches (10-20 files/batch).

**Mỗi file extract:** functions, classes, exports, call graph, tags.

**Output:** `.orca-onboard/tmp/batch-{N}.json`

```bash
for batch in $(seq 1 $NUM_BATCHES); do
  AGENT=$( [ $((batch % 2)) -eq 0 ] && echo "opencode" || echo "agy" )
  TITLE=$( [ $((batch % 2)) -eq 0 ] && echo "OpenCode" || echo "Antigravity" )
  SPEC="Analyze batch $batch: extract functions, classes, exports. Write to .orca-onboard/tmp/batch-$batch.json"
  TASK_ID=$(orca orchestration task-create --spec "$SPEC")
  orca orchestration dispatch --task $TASK_ID --to $AGENT --inject \
    || orca terminal send --title "$TITLE" --text "$SPEC"
done
# Chờ tất cả batches xong
orca terminal wait --for tui-idle && orca terminal read --title "Antigravity"
orca terminal wait --for tui-idle && orca terminal read --title "OpenCode"
```

---

## Phase 3 — Architecture Layers

**Agent:** OpenCode

**Làm gì:**
- Group files theo directory
- Match pattern: routes/api → API layer, services/core → Service layer, models/db → Data layer
- Phân tích dependency direction
- Tạo 3-10 layers

**Output:** `.orca-onboard/intermediate/layers.json`

```bash
SPEC="Analyze architecture from .orca-onboard/intermediate/scan-result.json: group files into layers. Write to .orca-onboard/intermediate/layers.json"
TASK_ID=$(orca orchestration task-create --spec "$SPEC")
orca orchestration dispatch --task $TASK_ID --to opencode --inject \
  || orca terminal send --title "OpenCode" --text "$SPEC"
orca terminal wait --for tui-idle && orca terminal read --title "OpenCode"
```

---

## Phase 4 — Knowledge Graph

**Agent:** Antigravity

**Làm gì:**
- Merge nodes từ tất cả batches
- Merge edges, thêm layer + import edges
- Validate node IDs unique, mỗi file node đúng 1 layer

**Output:** `.orca-onboard/intermediate/knowledge-graph.json`

```bash
SPEC="Assemble knowledge graph from scan-result.json, batch-*.json, layers.json. Write to .orca-onboard/intermediate/knowledge-graph.json"
TASK_ID=$(orca orchestration task-create --spec "$SPEC")
orca orchestration dispatch --task $TASK_ID --to agy --inject \
  || orca terminal send --title "Antigravity" --text "$SPEC"
orca terminal wait --for tui-idle && orca terminal read --title "Antigravity"
```

---

## Phase 5 — Guided Tour

**Agent:** OpenCode

**Làm gì:**
- Tìm entry points: README.md → index.ts/main.py/app.go
- BFS traversal, identify clusters (2-5 files liên kết chặt)
- Thêm non-code stops: README, Dockerfile, schema, CI/CD
- Viết 5-15 steps

**Output:** `.orca-onboard/intermediate/tour.json`

```bash
SPEC="Build 5-15 step onboarding tour from knowledge-graph.json entry points. Write to .orca-onboard/intermediate/tour.json"
TASK_ID=$(orca orchestration task-create --spec "$SPEC")
orca orchestration dispatch --task $TASK_ID --to opencode --inject \
  || orca terminal send --title "OpenCode" --text "$SPEC"
orca terminal wait --for tui-idle && orca terminal read --title "OpenCode"
```

---

## Phase 6 — Validate

**Agent:** Antigravity

**Check:**
- Schema: nodes có đủ fields (id, type, name, summary, tags, complexity)
- Referential integrity: edges reference node tồn tại
- Layer coverage: mỗi file node trong đúng 1 layer
- Tour: sequential 5-15 steps, no empty summaries

**Output:** `.orca-onboard/intermediate/validation.json`

```bash
SPEC="Validate knowledge-graph.json and tour.json. Write validation report to .orca-onboard/intermediate/validation.json"
TASK_ID=$(orca orchestration task-create --spec "$SPEC")
orca orchestration dispatch --task $TASK_ID --to agy --inject \
  || orca terminal send --title "Antigravity" --text "$SPEC"
orca terminal wait --for tui-idle && orca terminal read --title "Antigravity"
# Nếu validation fail → list issues, offer fix trước khi tiếp tục Phase 7
```

---

## Phase 7 — Wiki Generation

**Agent:** OpenCode

**Tạo:**
- `llmwiki/wiki/concepts/` — mỗi layer 1 file
- `llmwiki/wiki/entities/` — mỗi domain entity 1 file
- `llmwiki/wiki/architecture/` — index, layers, dependencies, entry-points
- `llmwiki/wiki/tours/onboarding-tour.md`
- `llmwiki/wiki/index.md` — master index

**Output structure:**
```
llmwiki/wiki/
├── index.md
├── concepts/*.md
├── entities/*.md
├── architecture/*.md
└── tours/onboarding-tour.md
```

```bash
SPEC="Generate wiki from knowledge-graph.json and tour.json. Write to llmwiki/wiki/ with index.md, concepts/, entities/, architecture/, tours/"
TASK_ID=$(orca orchestration task-create --spec "$SPEC")
orca orchestration dispatch --task $TASK_ID --to opencode --inject \
  || orca terminal send --title "OpenCode" --text "$SPEC"
orca terminal wait --for tui-idle && orca terminal read --title "OpenCode"
```

---

## Rules

- KHÔNG bịa file paths. Chỉ dùng file thật.
- KHÔNG include file không tồn tại.
- Validate node IDs unique.
- Mỗi file node đúng 1 layer.
- Tour 5-15 steps, bắt đầu bằng project overview.
- Wiki dùng wikilink format.

## Error

- Phase 1 fail → check permissions
- Phase 2 batch fail → skip batch đó
- Phase 3 < 3 layers → merge groups nhỏ
- Phase 6 fail → list issues, offer fix


---

## Output Report

After all main skill tasks complete, write a propose draft to the wiki.

### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/draft/orca/DDMMYY-<ten>.md`:

```
# DDMMYY-<ten>
**Type:** draft
**Status:** proposed
**Tags:** <skill-name>, output-report
**Proposed:** YYYY-MM-DD

## Agent Task Assignment
| Task | Agent | Status |
|------|-------|--------|
| <mô tả task 1> | <tên agent> | pending / in-progress / done |
| <mô tả task 2> | <tên agent> | pending / in-progress / done |

## What
<One sentence — what this skill invocation produced or decided>

## Output
<Key artefacts, files created/modified, or decisions made>

## Files
| File | Action |
|------|--------|
| `path/to/file` | created / modified |

## Notes
- Invoked via: `/<skill-name>` skill

## Origin
- **Draft:** `wiki/draft/orca/DDMMYY-<ten>.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
```

**3. Update wiki index & log:**
- `llmwiki/wiki/index.md` — append one row: `| [DDMMYY-<ten>](draft/orca/DDMMYY-<ten>.md) | draft | YYYY-MM-DD |`
- `llmwiki/wiki/log.md` — append: `## YYYY-MM-DD — <skill-name> — <ten>`

**4. Update agent statuses & sync push — BẮT BUỘC, không bỏ qua:**
- Mở lại file `llmwiki/wiki/draft/orca/DDMMYY-<ten>.md`
- Cập nhật cột **Status** trong bảng `## Agent Task Assignment` theo trạng thái thực tế của từng agent (pending → in-progress → done)
- Clone `rheinmir/setup` nhánh `orca`, copy các skill file đã sửa, rồi push ngược lên:
  ```bash
  git clone git@github.com:rheinmir/setup.git /tmp/rheinmir-setup-sync -b orca --depth 1
  cp /path/to/skill.md /tmp/rheinmir-setup-sync/skills/<skill-name>/SKILL.md
  cd /tmp/rheinmir-setup-sync
  git add .
  git commit -m "skill: sync update — DDMMYY-<ten>"
  git push origin orca
  rm -rf /tmp/rheinmir-setup-sync
  ```

> Skip chỉ khi skill không tạo ra artifact hoặc quyết định nào.