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
[Phase 1/8] Scan project...
[Phase 2/8] Analyze files...
[Phase 3/8] Architecture layers...
[Phase 4/8] Knowledge graph...
[Phase 5/8] Guided tour...
[Phase 6/8] Validate graph...
[Phase 7/8] Generate wiki...
[Phase 8/8] Generate HTML docs...
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

**Bắt buộc:** Tạo draft file TRƯỚC, rồi mới hỏi user. Không được đảo thứ tự.

**Bước 1 — Probe agent CLI availability:**

```bash
# Kiểm tra từng agent binary có usable không
AGY_OK=$(agy --version 2>/dev/null && echo "✅ usable" || echo "❌ not found")
OC_OK=$(opencode --version 2>/dev/null && echo "✅ usable" || echo "❌ not found")
KIRO_OK=$(kiro-cli --version 2>/dev/null && echo "✅ usable" || echo "❌ not found")
ORCA_OK=$(orca terminal list 2>/dev/null && echo "✅ usable" || echo "❌ not found")

# Fallback assignment nếu agent không available:
# - agy unavailable → dùng opencode hoặc Claude
# - opencode unavailable → dùng agy hoặc Claude
# - cả hai đều unavailable → Claude đảm nhận hết
```

**Bước 2 — Tạo draft file (với agent availability thực tế):**

```bash
DATE=$(date +%d%m%y)
PROJECT_SLUG=$(basename "$PROJECT_ROOT" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
DRAFT_FILE="$PROJECT_ROOT/llmwiki/wiki/draft/orca/${DATE}-onboard-${PROJECT_SLUG}.md"
FILE_COUNT=$(wc -l < "$PROJECT_ROOT/.orca-onboard/tmp/files.txt")

# Resolve agent cho từng phase dựa vào availability
AGENT_SCAN=$( agy --version 2>/dev/null && echo "Antigravity (agy)" || echo "Claude (fallback)" )
AGENT_ANALYZE=$( (agy --version 2>/dev/null || opencode --version 2>/dev/null) && echo "Antigravity + OpenCode (parallel)" || echo "Claude (fallback, sequential)" )
AGENT_LAYERS=$( opencode --version 2>/dev/null && echo "OpenCode" || echo "Claude (fallback)" )
AGENT_GRAPH=$( agy --version 2>/dev/null && echo "Antigravity (agy)" || echo "Claude (fallback)" )
AGENT_TOUR=$( opencode --version 2>/dev/null && echo "OpenCode" || echo "Claude (fallback)" )
AGENT_VALIDATE=$( agy --version 2>/dev/null && echo "Antigravity (agy)" || echo "Claude (fallback)" )
AGENT_WIKI=$( opencode --version 2>/dev/null && echo "OpenCode" || echo "Claude (fallback)" )

cat > "$DRAFT_FILE" << EOF
# ${DATE}-onboard-${PROJECT_SLUG}
**Type:** draft
**Status:** proposed
**Tags:** orca-onboard, output-report
**Proposed:** $(date +%Y-%m-%d)

## Agent CLI Availability
| Agent | Binary | Status |
|-------|--------|--------|
| Antigravity | \`agy\` | $AGY_OK |
| OpenCode | \`opencode\` | $OC_OK |
| Kiro | \`kiro-cli\` | $KIRO_OK |
| Orca Terminal | \`orca terminal\` | $ORCA_OK |

## Agent Task Assignment
| Task | Agent | Status |
|------|-------|--------|
| Phase 1 — Scan project ($FILE_COUNT files) | $AGENT_SCAN | pending |
| Phase 2 — Analyze files (parallel batches) | $AGENT_ANALYZE | pending |
| Phase 3 — Architecture layers | $AGENT_LAYERS | pending |
| Phase 4 — Knowledge graph assembly | $AGENT_GRAPH | pending |
| Phase 5 — Guided tour (5-15 steps) | $AGENT_TOUR | pending |
| Phase 6 — Validate graph + tour | $AGENT_VALIDATE | pending |
| Phase 7 — Wiki generation | $AGENT_WIKI | pending |
| Phase 8 — HTML docs (docs-site-macos) | Claude | pending |

## What
Onboard codebase \`$PROJECT_ROOT\` — knowledge graph, architecture layers, guided tour, wiki, HTML docs.

## Output
- \`.orca-onboard/intermediate/scan-result.json\`
- \`.orca-onboard/intermediate/layers.json\`
- \`.orca-onboard/intermediate/knowledge-graph.json\`
- \`.orca-onboard/intermediate/tour.json\`
- \`.orca-onboard/intermediate/validation.json\`
- \`llmwiki/wiki/\` (index, concepts, entities, architecture, tours)
- \`llmwiki/html/onboarding-${PROJECT_SLUG}.html\`

## Files
| File | Action |
|------|--------|
| \`llmwiki/wiki/index.md\` | created/modified |
| \`llmwiki/wiki/architecture/*.md\` | created |
| \`llmwiki/wiki/concepts/*.md\` | created |
| \`llmwiki/wiki/entities/*.md\` | created |
| \`llmwiki/wiki/tours/onboarding-tour.md\` | created |
| \`llmwiki/html/onboarding-${PROJECT_SLUG}.html\` | created |

## Notes
- Invoked via: \`/orca-onboard\` skill
- Project root: \`$PROJECT_ROOT\`
- Files tracked: $FILE_COUNT

## Origin
- **Draft:** \`wiki/draft/orca/${DATE}-onboard-${PROJECT_SLUG}.md\`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
EOF
echo "DRAFT_FILE=$DRAFT_FILE"
```

Cập nhật wiki index và log:
```bash
echo "| [${DATE}-onboard-${PROJECT_SLUG}](draft/orca/${DATE}-onboard-${PROJECT_SLUG}.md) | draft | $(date +%Y-%m-%d) |" >> "$PROJECT_ROOT/llmwiki/wiki/index.md"
echo "## $(date +%Y-%m-%d) — orca-onboard — onboard-${PROJECT_SLUG}" >> "$PROJECT_ROOT/llmwiki/wiki/log.md"
```

**Bước 2 — Trình bày cho user review:**

Hiển thị cho user:
- Path của draft file vừa tạo
- Bảng Agent Task Assignment (8 phases, tất cả `pending`)
- Số files sẽ phân tích

**Bước 3 — Hỏi xác nhận:**

```bash
orca orchestration gate-create --question "Draft plan tại $DRAFT_FILE. Bắt đầu onboard $PROJECT_ROOT? (8 phases)"
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

## Phase 8 — HTML Docs (docs-site-macos)

**Agent:** Claude (main thread — không dispatch ra ngoài)

**Làm gì:**
- Đọc các wiki MD files vừa tạo ở Phase 7: `llmwiki/wiki/architecture/`, `llmwiki/wiki/concepts/`, `llmwiki/wiki/tours/onboarding-tour.md`
- Invoke skill `docs-site-macos` để render thành HTML đẹp
- Output file: `llmwiki/html/onboarding-<project-slug>.html`
- Cập nhật `llmwiki/html/README.md` nếu có

**Quy tắc bắt buộc:**
- Output LUÔN vào `llmwiki/html/` — KHÔNG được tạo ở project root hay nơi khác
- Tên file: `onboarding-<project-slug>.html` (slug = tên thư mục project, lowercase, dấu cách → gạch ngang)
- Nội dung HTML phải cover: architecture overview, knowledge graph summary, layer diagram, guided tour steps
- Dùng animated SVG cho architecture diagram
- Checklist trong HTML phải dùng `<input type="checkbox">` thật — KHÔNG dùng `☐` Unicode

**Invoke:**
```
Skill: docs-site-macos
Args: Synthesize onboarding HTML from wiki files at llmwiki/wiki/. 
      Cover: project overview, architecture layers, knowledge graph, guided tour.
      Output: llmwiki/html/onboarding-<slug>.html
```

**Sau khi tạo xong:**
```bash
# Kiểm tra file tồn tại
ls llmwiki/html/onboarding-*.html

# Nếu port 8765 chưa chạy
lsof -ti :8765 || nohup npx serve -p 8765 > /tmp/serve.log 2>&1 &
```

Thông báo user: `http://localhost:8765/llmwiki/html/onboarding-<slug>.html`

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