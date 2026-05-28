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

## Phase 0 — Pre-flight

```bash
# Resolve project root
PROJECT_ROOT=${1:-.}
test -d "$PROJECT_ROOT" || exit 1

# Create dirs
mkdir -p $PROJECT_ROOT/.orca-onboard/{intermediate,tmp}
mkdir -p $PROJECT_ROOT/llmwiki/wiki/{concepts,entities,architecture,tours}

# Get git info
git rev-parse HEAD 2>/dev/null > $PROJECT_ROOT/.orca-onboard/tmp/commit.txt
git ls-files > $PROJECT_ROOT/.orca-onboard/tmp/files.txt 2>/dev/null || find $PROJECT_ROOT -type f > $PROJECT_ROOT/.orca-onboard/tmp/files.txt
```

---

## Phase 1 — Scan Project

1 agent scan toàn bộ project.

**Làm gì:**
- Đọc manifest: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `README.md`
- Phân loại files: code, config, docs, infra, data, script, markup
- Đếm dòng code
- Build import map

**Output:** `.orca-onboard/intermediate/scan-result.json`

```bash
orca orchestration task-create --spec "Scan $PROJECT_ROOT: enumerate files, detect languages, build import map. Write to .orca-onboard/intermediate/scan-result.json"
```

---

## Phase 2 — Analyze Files (Parallel)

Chia files thành batches (10-20 files/batch). Mỗi batch 1 agent chạy song song.

**Mỗi file extract:**
- Functions, classes, exports
- Call graph
- Tags: "api-handler", "data-model", "utility", ...

**Output:** `.orca-onboard/tmp/batch-{N}.json`

```bash
for batch in $(seq 1 $NUM_BATCHES); do
  orca orchestration task-create --spec "Analyze batch $batch: extract functions, classes, exports. Write to .orca-onboard/tmp/batch-$batch.json"
done
```

---

## Phase 3 — Architecture Layers

1 agent phân tích architecture.

**Làm gì:**
- Group files theo directory
- Match pattern: routes/api → API layer, services/core → Service layer, models/db → Data layer, ...
- Phân tích dependency direction
- Tạo 3-10 layers

**Output:** `.orca-onboard/intermediate/layers.json`

```bash
orca orchestration task-create --spec "Analyze architecture: group files into layers. Write to .orca-onboard/intermediate/layers.json"
```

---

## Phase 4 — Knowledge Graph

1 agent gộp tất cả thành knowledge graph.

**Làm gì:**
- Merge nodes từ tất cả batches
- Merge edges
- Thêm layer membership edges
- Thêm import edges
- Validate node IDs unique
- Mỗi file node chỉ xuất hiện trong 1 layer

**Output:** `.orca-onboard/intermediate/knowledge-graph.json`

```bash
orca orchestration task-create --spec "Assemble knowledge graph from scan, batches, layers. Write to .orca-onboard/intermediate/knowledge-graph.json"
```

---

## Phase 5 — Guided Tour

1 agent tạo tour onboarding.

**Làm gì:**
- Tìm entry points: README.md → index.ts/main.py/app.go
- BFS traversal từ entry points
- Identify clusters (2-5 files liên kết chặt)
- Thêm non-code stops: README, Dockerfile, schema, CI/CD
- Viết 5-15 steps

**Output:** `.orca-onboard/intermediate/tour.json`

```bash
orca orchestration task-create --spec "Build 5-15 step tour from entry points. Write to .orca-onboard/intermediate/tour.json"
```

---

## Phase 6 — Validate

1 agent validate graph.

**Check:**
- Schema: nodes có đủ fields (id, type, name, summary, tags, complexity)
- Referential integrity: edges reference node có tồn tại
- Layer coverage: mỗi file node có trong đúng 1 layer
- Tour: sequential 5-15 steps
- Quality: no empty summaries, no self-refs, no orphans

**Output:** `.orca-onboard/intermediate/validation.json`

```bash
orca orchestration task-create --spec "Validate knowledge graph. Write to .orca-onboard/intermediate/validation.json"
```

---

## Phase 7 — Wiki Generation

1 agent convert knowledge graph thành wiki.

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
orca orchestration task-create --spec "Generate wiki from knowledge graph. Write to llmwiki/wiki/"
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
