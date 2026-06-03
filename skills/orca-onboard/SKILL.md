---
name: orca-onboard
description: "Parallel codebase onboarding with Orca agents — multi-agent pipeline inspired by Understand-Anything. Generates knowledge graph, architecture layers, guided tour, and llmwiki entries."
requires:
  - orchestration
  - orca-cli
  - docs-site-macos
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

⛔ **KHÔNG được chạy Phase 0.5 Gate hay bất kỳ Phase nào (1–8) nếu Phase 0 chưa hoàn thành.**

**Thứ tự bắt buộc — không được đảo:**
1. **Phase 0 (Pre-flight)** → chạy xong, kiểm tra `llmwiki/` tồn tại → ✅
2. **Phase 0.5 (Gate)** → tạo draft file + hỏi user xác nhận
3. **Phases 1–8** → execute, cập nhật status sau MỖI phase

**Skills phụ thuộc bắt buộc:** `orchestration` (task-create, dispatch, gate-create), `orca-cli` (terminal send/wait/read), `docs-site-macos` (Phase 8). Phase 0 kiểm tra và DỪNG nếu thiếu.

**Nếu `llmwiki/` chưa tồn tại:** bootstrap NGAY tại Phase 0. KHÔNG defer, KHÔNG skip.
**Nếu bootstrap fail:** DỪNG HOÀN TOÀN, báo lỗi. Không hiện Gate, không tiếp tục.
**Nếu agent bỏ qua Phase 0 hay chạy Phase 0.5 trước Phase 0:** đó là bug — quay lại Phase 0 ngay.

**Sau MỖI phase hoàn thành:** cập nhật status trong draft file NGAY — không defer đến cuối.

---

## Resume Mode — `/orca-onboard @DDMMYY-onboard-<slug>.md`

Khi invoked với argument bắt đầu bằng `@`, đây là resume mode. KHÔNG chạy Phase 0 hay Phase 0.5.

**Bước 1 — Detect và load:**

```bash
if [[ "$1" == @* ]]; then
  DRAFT_FILE="${1#@}"        # strip leading @
  DRAFT_FILE=$(echo "$DRAFT_FILE" | tr '\\' '/')  # normalize Windows paths
  RESUME_MODE=true
  PROJECT_ROOT=$(grep "Project root:" "$DRAFT_FILE" | grep -oP '(?<=`)[^`]+(?=`)' | head -1)
  PROJECT_ROOT=$(echo "$PROJECT_ROOT" | tr '\\' '/')
else
  RESUME_MODE=false
fi
```

**Bước 2 — Parse statuses (chỉ từ bảng Agent Task Assignment):**

```bash
parse_status() {
  local keyword="$1"
  # Scope awk to lines between "## Agent Task Assignment" and next "## " heading
  awk '/## Agent Task Assignment/{p=1} p && /^## [^A]/{p=0} p' "$DRAFT_FILE" \
    | grep "$keyword" | grep -oE 'pending|in-progress|done' | head -1
}

if [ "$RESUME_MODE" = true ]; then
  PHASE1_STATUS=$(parse_status "Phase 1 —")
  PHASE2_STATUS=$(parse_status "Phase 2 —")
  PHASE3_STATUS=$(parse_status "Phase 3 —")
  PHASE4_STATUS=$(parse_status "Phase 4 —")
  PHASE5_STATUS=$(parse_status "Phase 5 —")
  PHASE6_STATUS=$(parse_status "Phase 6 —")
  PHASE7_STATUS=$(parse_status "Phase 7 —")
  PHASE8_STATUS=$(parse_status "Phase 8 —")
  echo "[Resume] Draft: $DRAFT_FILE"
  echo "[Resume] Statuses: P1=$PHASE1_STATUS P2=$PHASE2_STATUS P3=$PHASE3_STATUS P4=$PHASE4_STATUS P5=$PHASE5_STATUS P6=$PHASE6_STATUS P7=$PHASE7_STATUS P8=$PHASE8_STATUS"
fi
```

**Bước 3 — Hiển thị bảng status cho user, confirm, rồi continue từ phase chưa done.**

**Skip rule (áp dụng cho TỪNG phase):**
> Nếu `RESUME_MODE=true` VÀ phase status = `done` → bỏ qua phase đó, chuyển sang phase tiếp theo.
> Nếu `RESUME_MODE=true` VÀ phase status = `in-progress` → coi như interrupted, chạy lại từ đầu.
> KHÔNG dùng `exit` để skip — chỉ skip logic của phase đó rồi tiếp tục.

---

## Status Update Helper

Gọi NGAY khi phase bắt đầu (`in-progress`) và khi xong (`done`). KHÔNG defer đến cuối.

```bash
update_phase_status() {
  local keyword="$1"    # phải khớp chính xác với text trong bảng, ví dụ: "Phase 1 —"
  local status="$2"     # "in-progress" | "done"
  [ -z "$DRAFT_FILE" ] && echo "[WARN] DRAFT_FILE unset" && return 0
  local f=$(echo "$DRAFT_FILE" | tr '\\' '/')
  [ ! -f "$f" ] && echo "[WARN] DRAFT_FILE not found: $f" && return 0
  # Replace status token on the specific row matching keyword
  # Uses perl for reliable cross-platform in-place edit
  perl -i -pe "s/(\Q$keyword\E.*?)\| (?:pending|in-progress|done)/\$1| $status/g if /\Q$keyword\E/" "$f" \
    || sed -i "s/\(.*$(echo "$keyword" | sed 's/[^^]/[&]/g').*\)| [a-z-]*/\1| $status/" "$f" \
    || echo "[WARN] status update failed for: $keyword"
}
```

---

## Phase 0 — Pre-flight

```bash
# --- Dependency check (STOP if missing) ---
MISSING_SKILLS=()
# Check orchestration skill loaded (needed for task-create, dispatch, gate-create)
orca orchestration --help >/dev/null 2>&1 || MISSING_SKILLS+=("orchestration")
# Check orca-cli skill loaded (needed for terminal send/wait/read)
orca terminal list >/dev/null 2>&1 || MISSING_SKILLS+=("orca-cli")
# Check docs-site-macos skill present in agent skills dir
ls ~/.agents/skills/docs-site-macos/SKILL.md >/dev/null 2>&1 || MISSING_SKILLS+=("docs-site-macos")

if [ ${#MISSING_SKILLS[@]} -gt 0 ]; then
  echo "❌ orca-onboard: missing required skills: ${MISSING_SKILLS[*]}"
  echo "   Install with: npx skills add rheinmir/setup@orca --skill ${MISSING_SKILLS[*]} --global -y"
  exit 1
fi
echo "✅ Dependencies OK: orchestration, orca-cli, docs-site-macos"

# --- Resolve project root ---
PROJECT_ROOT=${1:-.}
test -d "$PROJECT_ROOT" || exit 1

# Bootstrap llmwiki nếu chưa có
if [ ! -d "$PROJECT_ROOT/llmwiki" ]; then
  echo "[orca-onboard] llmwiki chưa có — kéo template từ rheinmir/setup..."
  git clone https://github.com/rheinmir/setup.git /tmp/orca-llmwiki-bootstrap --depth 1 -b orca -q
  cp -r /tmp/orca-llmwiki-bootstrap/llmwiki "$PROJECT_ROOT/llmwiki"
  rm -rf /tmp/orca-llmwiki-bootstrap
  echo "[orca-onboard] llmwiki bootstrapped OK"
fi

# Create dirs
mkdir -p $PROJECT_ROOT/.orca-onboard/{intermediate,tmp}
mkdir -p $PROJECT_ROOT/llmwiki/wiki/draft/{cave,uiux,orca}

# Get git info
git rev-parse HEAD 2>/dev/null > $PROJECT_ROOT/.orca-onboard/tmp/commit.txt
# Exclude .orca-onboard/ and llmwiki/ from file list to avoid inflated counts
git ls-files > $PROJECT_ROOT/.orca-onboard/tmp/files.txt 2>/dev/null \
  || find $PROJECT_ROOT -type f \
       ! -path "*/.orca-onboard/*" \
       ! -path "*/llmwiki/*" \
       ! -path "*/.git/*" \
     > $PROJECT_ROOT/.orca-onboard/tmp/files.txt
FILE_COUNT=$(wc -l < $PROJECT_ROOT/.orca-onboard/tmp/files.txt | tr -d ' ')
# Compute batch count: 1 batch per 15 files, minimum 1
NUM_BATCHES=$(( (FILE_COUNT + 14) / 15 ))
[ $NUM_BATCHES -lt 1 ] && NUM_BATCHES=1
echo "[pre-flight] $FILE_COUNT files → $NUM_BATCHES batches"
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
AGY_AVAIL=$(agy --version 2>/dev/null && echo "yes" || echo "no")
OC_AVAIL=$(opencode --version 2>/dev/null && echo "yes" || echo "no")
if [ "$AGY_AVAIL" = "yes" ] && [ "$OC_AVAIL" = "yes" ]; then
  AGENT_ANALYZE="Antigravity + OpenCode (parallel)"
elif [ "$AGY_AVAIL" = "yes" ]; then
  AGENT_ANALYZE="Antigravity (sequential, OpenCode unavailable)"
elif [ "$OC_AVAIL" = "yes" ]; then
  AGENT_ANALYZE="OpenCode (sequential, agy unavailable)"
else
  AGENT_ANALYZE="Claude (fallback — both agents unavailable, sequential)"
fi
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

**Skip check:** Nếu `RESUME_MODE=true` và `PHASE1_STATUS=done` → bỏ qua Phase 1, sang Phase 2 ngay.

```bash
# Only run if not already done
if [ "$RESUME_MODE" != "true" ] || [ "$PHASE1_STATUS" != "done" ]; then
  update_phase_status "Phase 1 —" "in-progress"
  SPEC="Scan $PROJECT_ROOT: enumerate files, detect languages, build import map. Write JSON to .orca-onboard/intermediate/scan-result.json"
  TASK_ID=$(orca orchestration task-create --spec "$SPEC")
  orca orchestration dispatch --task $TASK_ID --to agy --inject \
    || orca terminal send --title "Antigravity" --text "$SPEC"
  orca terminal wait --for tui-idle && orca terminal read --title "Antigravity"
  update_phase_status "Phase 1 —" "done"
fi
```

---

## Phase 2 — Analyze Files (Parallel)

**Agent:** Antigravity + OpenCode song song — mỗi batch 1 agent.

Chia files thành batches (10-20 files/batch).

**Mỗi file extract:** functions, classes, exports, call graph, tags.

**Output:** `.orca-onboard/tmp/batch-{N}.json`

**Skip check:** Nếu `RESUME_MODE=true` và `PHASE2_STATUS=done` → bỏ qua Phase 2, sang Phase 3 ngay.

```bash
if [ "$RESUME_MODE" != "true" ] || [ "$PHASE2_STATUS" != "done" ]; then
  update_phase_status "Phase 2 —" "in-progress"
  # NUM_BATCHES set in Phase 0 pre-flight; re-compute if resuming
  [ -z "$NUM_BATCHES" ] && FILE_COUNT=$(wc -l < $PROJECT_ROOT/.orca-onboard/tmp/files.txt | tr -d ' ') && NUM_BATCHES=$(( (FILE_COUNT + 14) / 15 ))
  [ $NUM_BATCHES -lt 1 ] && NUM_BATCHES=1
  for batch in $(seq 1 $NUM_BATCHES); do
    # Alternate agents: odd batches → agy, even → opencode (fallback to whichever available)
    if [ $((batch % 2)) -eq 1 ] && agy --version 2>/dev/null; then
      AGENT="agy"; TITLE="Antigravity"
    elif opencode --version 2>/dev/null; then
      AGENT="opencode"; TITLE="OpenCode"
    else
      AGENT="claude"; TITLE="Claude"
    fi
    SPEC="Analyze batch $batch of $NUM_BATCHES: extract functions, classes, exports from files listed in .orca-onboard/tmp/files.txt lines $(( (batch-1)*15 + 1 ))-$(( batch*15 )). Write to .orca-onboard/tmp/batch-$batch.json"
    TASK_ID=$(orca orchestration task-create --spec "$SPEC")
    orca orchestration dispatch --task $TASK_ID --to $AGENT --inject \
      || orca terminal send --title "$TITLE" --text "$SPEC"
  done
  # Wait for all agents
  orca terminal wait --for tui-idle && orca terminal read --title "Antigravity" 2>/dev/null
  orca terminal wait --for tui-idle && orca terminal read --title "OpenCode" 2>/dev/null
  update_phase_status "Phase 2 —" "done"
fi
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

**Skip check:** Nếu `RESUME_MODE=true` và `PHASE3_STATUS=done` → bỏ qua Phase 3, sang Phase 4 ngay.

```bash
if [ "$RESUME_MODE" != "true" ] || [ "$PHASE3_STATUS" != "done" ]; then
  update_phase_status "Phase 3 —" "in-progress"
  SPEC="Analyze architecture from .orca-onboard/intermediate/scan-result.json: group files into layers. Write to .orca-onboard/intermediate/layers.json"
  TASK_ID=$(orca orchestration task-create --spec "$SPEC")
  orca orchestration dispatch --task $TASK_ID --to opencode --inject \
    || orca terminal send --title "OpenCode" --text "$SPEC"
  orca terminal wait --for tui-idle && orca terminal read --title "OpenCode"
  update_phase_status "Phase 3 —" "done"
fi
```

---

## Phase 4 — Knowledge Graph

**Agent:** Antigravity

**Làm gì:**
- Merge nodes từ tất cả batches
- Merge edges, thêm layer + import edges
- Validate node IDs unique, mỗi file node đúng 1 layer

**Output:** `.orca-onboard/intermediate/knowledge-graph.json`

**Skip check:** Nếu `RESUME_MODE=true` và `PHASE4_STATUS=done` → bỏ qua Phase 4, sang Phase 5 ngay.

```bash
if [ "$RESUME_MODE" != "true" ] || [ "$PHASE4_STATUS" != "done" ]; then
  update_phase_status "Phase 4 —" "in-progress"
  SPEC="Assemble knowledge graph from scan-result.json, batch-*.json, layers.json. Write to .orca-onboard/intermediate/knowledge-graph.json"
  TASK_ID=$(orca orchestration task-create --spec "$SPEC")
  orca orchestration dispatch --task $TASK_ID --to agy --inject \
    || orca terminal send --title "Antigravity" --text "$SPEC"
  orca terminal wait --for tui-idle && orca terminal read --title "Antigravity"
  update_phase_status "Phase 4 —" "done"
fi
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

**Skip check:** Nếu `RESUME_MODE=true` và `PHASE5_STATUS=done` → bỏ qua Phase 5, sang Phase 6 ngay.

```bash
if [ "$RESUME_MODE" != "true" ] || [ "$PHASE5_STATUS" != "done" ]; then
  update_phase_status "Phase 5 —" "in-progress"
  SPEC="Build 5-15 step onboarding tour from knowledge-graph.json entry points. Write to .orca-onboard/intermediate/tour.json"
  TASK_ID=$(orca orchestration task-create --spec "$SPEC")
  orca orchestration dispatch --task $TASK_ID --to opencode --inject \
    || orca terminal send --title "OpenCode" --text "$SPEC"
  orca terminal wait --for tui-idle && orca terminal read --title "OpenCode"
  update_phase_status "Phase 5 —" "done"
fi
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

**Skip check:** Nếu `RESUME_MODE=true` và `PHASE6_STATUS=done` → bỏ qua Phase 6, sang Phase 7 ngay.

```bash
if [ "$RESUME_MODE" != "true" ] || [ "$PHASE6_STATUS" != "done" ]; then
  update_phase_status "Phase 6 —" "in-progress"
  SPEC="Validate knowledge-graph.json and tour.json. Write validation report to .orca-onboard/intermediate/validation.json"
  TASK_ID=$(orca orchestration task-create --spec "$SPEC")
  orca orchestration dispatch --task $TASK_ID --to agy --inject \
    || orca terminal send --title "Antigravity" --text "$SPEC"
  orca terminal wait --for tui-idle && orca terminal read --title "Antigravity"
  # Nếu validation fail → list issues, offer fix trước khi tiếp tục Phase 7
  update_phase_status "Phase 6 —" "done"
fi
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

**Skip check:** Nếu `RESUME_MODE=true` và `PHASE7_STATUS=done` → bỏ qua Phase 7, sang Phase 8 ngay.

```bash
if [ "$RESUME_MODE" != "true" ] || [ "$PHASE7_STATUS" != "done" ]; then
  update_phase_status "Phase 7 —" "in-progress"
  SPEC="Generate wiki from knowledge-graph.json and tour.json. Write to llmwiki/wiki/ with index.md, concepts/, entities/, architecture/, tours/"
  TASK_ID=$(orca orchestration task-create --spec "$SPEC")
  orca orchestration dispatch --task $TASK_ID --to opencode --inject \
    || orca terminal send --title "OpenCode" --text "$SPEC"
  orca terminal wait --for tui-idle && orca terminal read --title "OpenCode"
  update_phase_status "Phase 7 —" "done"
fi
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

**Skip check:** Nếu `RESUME_MODE=true` và `PHASE8_STATUS=done` → bỏ qua Phase 8.

**Invoke (chỉ chạy nếu không skip):**

```bash
if [ "$RESUME_MODE" != "true" ] || [ "$PHASE8_STATUS" != "done" ]; then
  update_phase_status "Phase 8 —" "in-progress"
  # Invoke docs-site-macos skill (main thread — không dispatch)
```
```
Skill: docs-site-macos
Args: Synthesize onboarding HTML from wiki files at llmwiki/wiki/. 
      Cover: project overview, architecture layers, knowledge graph, guided tour.
      Output: llmwiki/html/onboarding-<slug>.html
```
```bash
  update_phase_status "Phase 8 —" "done"
fi
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