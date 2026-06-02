---
name: onboard-codebase
description: "Onboard to a new codebase by building a structured map — multi-phase pipeline with knowledge graph, architecture layers, guided tour, and wiki generation."
---

# onboard-codebase

Phân tích codebase, tạo knowledge graph, layers, tour, wiki. Không cần Orca.

## Khi nào dùng
- Onboard project mới
- Wiki outdated
- Cần context gap

## Options
- `--full` — Rebuild hết
- `--language <lang>` — Ngôn ngữ output
- `--skip-tour` — Bỏ tour
- `--skip-wiki` — Bỏ wiki
- `<path>` — Phân tích thư mục khác

## Progress
```
[Phase 1/7] Scan project...
[Phase 2/7] Analyze files...
[Phase 3/7] Deep analysis...
[Phase 4/7] Architecture layers...
[Phase 5/7] Knowledge graph...
[Phase 6/7] Guided tour...
[Phase 7/7] Generate wiki...
```

---

## Phase 0 — Pre-flight

```bash
PROJECT_ROOT=${1:-.}
test -d "$PROJECT_ROOT" || exit 1

mkdir -p $PROJECT_ROOT/.onboard/{intermediate,tmp}
mkdir -p $PROJECT_ROOT/llmwiki/wiki/{concepts,entities,architecture,tours}

git rev-parse HEAD 2>/dev/null > $PROJECT_ROOT/.onboard/tmp/commit.txt
git ls-files > $PROJECT_ROOT/.onboard/tmp/files.txt 2>/dev/null || find $PROJECT_ROOT -type f > $PROJECT_ROOT/.onboard/tmp/files.txt
```

---

## Phase 1 — Scan Project

**Làm gì:**
- Đọc manifest: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `README.md`
- Phân loại files: code, config, docs, infra, data, script, markup
- Đếm dòng code
- Build import map

**Output:** `.onboard/intermediate/scan-result.json`

---

## Phase 2 — Analyze Files (Parallel)

Chia files thành batches (10-20 files/batch). Dùng Task tool chạy song song.

**Mỗi file extract:**
- Functions, classes, exports
- Tags: "api-handler", "data-model", "utility", ...

**Output:** `.onboard/tmp/batch-{N}.json`

```
Task agent-1: Analyze batch 1 (files 1-15)
Task agent-2: Analyze batch 2 (files 16-30)
... run all parallel
```

---

## Phase 3 — Deep Code Analysis

**Làm gì:**
- **Infrastructure:** Directory structure, tech stack, entry points, build scripts
- **Patterns:** Repository, Event-driven, MVC, State management, Data fetching
- **Business rules:** Reverse-engineer user stories, extract domain logic
- **Frontend style:** UI framework, CSS, design tokens, components, routing

**Output:** `.onboard/intermediate/deep-analysis.json`

---

## Phase 4 — Architecture Layers

**Làm gì:**
- Group files theo directory
- Match pattern: routes → API, services → Service, models → Data, components → UI, utils → Utility
- Phân tích dependency direction
- Tạo 3-10 layers

**Output:** `.onboard/intermediate/layers.json`

---

## Phase 5 — Knowledge Graph

**Làm gì:**
- Merge nodes từ batches
- Merge edges
- Thêm layer membership + import edges
- Validate node IDs unique
- Mỗi file node đúng 1 layer

**Output:** `.onboard/intermediate/knowledge-graph.json`

---

## Phase 6 — Guided Tour

**Làm gì:**
- Tìm entry points: README → index.ts/main.py/app.go
- BFS traversal từ entry points
- Identify clusters (2-5 files chặt)
- Thêm stops: README, Dockerfile, schema, CI/CD
- Viết 5-15 steps

**Output:** `.onboard/intermediate/tour.json`

---

## Phase 7 — Wiki Generation

**Tạo:**
- `llmwiki/wiki/concepts/` — mỗi layer 1 file
- `llmwiki/wiki/entities/` — domain entities + `project-structure.md` + `fe-style.md`
- `llmwiki/wiki/architecture/` — index, layers, dependencies, entry-points
- `llmwiki/wiki/tours/onboarding-tour.md`
- `llmwiki/wiki/index.md` — master index
- `AGENT-business.md` — business rules

**Output structure:**
```
llmwiki/wiki/
├── index.md
├── concepts/*.md
├── entities/*.md
├── architecture/*.md
└── tours/onboarding-tour.md
AGENT-business.md
```

---

## Rules

- KHÔNG bịa file paths. Chỉ dùng file thật.
- KHÔNG include file không tồn tại.
- Validate node IDs unique.
- Mỗi file node đúng 1 layer.
- Tour 5-15 steps, bắt đầu bằng project overview.
- Wiki dùng wikilink format.
- LUÔN verify business claims bằng code thật.
- Focus "Why" và "How", không chỉ "What".
- Không overwrite wiki entries có `## Origin`.
- `fe-style.md`: ghi giá trị thật (hex, px, class names).

## Error

- Phase 1 fail → check permissions
- Phase 2 batch fail → skip batch đó
- Phase 4 < 3 layers → merge groups nhỏ
- Phase 6 fail → list issues, offer fix


---

## Output Report

After all main skill tasks complete, write a propose draft to the wiki.

### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/sources/draft/DDMMYY-<ten>.md`:

```
# DDMMYY-<ten>
**Type:** draft
**Status:** proposed
**Tags:** <skill-name>, output-report
**Proposed:** YYYY-MM-DD

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
- **Draft:** `wiki/sources/draft/DDMMYY-<ten>.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
```

**3. Update wiki index & log:**
- `llmwiki/wiki/index.md` — append one row: `| [DDMMYY-<ten>](sources/draft/DDMMYY-<ten>.md) | draft | YYYY-MM-DD |`
- `llmwiki/wiki/log.md` — append: `## YYYY-MM-DD — <skill-name> — <ten>`

> Skip only when the skill produces zero artefacts and zero decisions (e.g., a pure display mode like `/caveman-stats`).