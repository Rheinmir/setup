---
name: orca-onboard
description: "Parallel codebase onboarding — wraps understand-anything for graph quality, then domain enrichment (Claude), wiki + HTML via opencode+DeepSeek Flash v4."
requires:
  - name: docs-site-macos
    source: rheinmir/setup@orca
    install: "npx skills add rheinmir/setup@orca --skill docs-site-macos --global -y"
---

# orca-onboard

Onboard codebase via understand-anything graph, then domain enrichment + wiki + HTML.

## Triggers
- "onboard codebase", "analyze codebase", "knowledge graph", "guided tour"

## Options
- `--full` — Delete `.understand-anything/` and rebuild
- `--update` — Incremental: re-analyze only changed files since last run
- `--language <lang>` — Output language (vi, en, zh, ...)
- `--skip-wiki` — Skip wiki generation
- `<path>` — Target directory (default: `.`)

## Progress
```
[Phase 1/4] Graph generation (agy → /understand)...
[Phase 2/4] Domain enrichment (Claude)...
[Phase 3/4] Wiki generation (opencode + DeepSeek Flash v4)...
[Phase 4/4] HTML docs (opencode + DeepSeek Flash v4)...
```

---

## ⚠️ HARD RULES

⛔ **DO NOT run Phase 0.5 or Phases 1–4 until Phase 0 completes.**

**Strict order — no reversal:**
1. **Phase 0** → complete, verify `llmwiki/` exists ✅
2. **Phase 0.5 (Gate)** → create draft file FIRST, then ask user
3. **Phases 1–4** → execute, update status after EACH phase immediately

- `llmwiki/` missing → bootstrap in Phase 0, NEVER defer
- Bootstrap fail → STOP completely, report error
- After EACH phase → update draft status NOW, never at end

---

## Dispatch Rules

```
TASK TYPE        → AGENT               → MODEL
────────────────────────────────────────────────────
Graph building   → agy (/understand)   → Claude inside agy (tree-sitter + Louvain)
Domain reasoning → Claude main thread  → Sonnet (never dispatch out)
Architecture     → Claude main thread  → Sonnet (never dispatch out)
Mechanical       → opencode            → deepseek/deepseek-flash-v4
Scripts          → bash/python direct  → (no LLM)
```

**Reasoning tasks MUST stay in Claude main thread. NO reasoning to opencode/agy.**
**opencode + DeepSeek: template fill, wiki render, HTML only.**

---

## Agent Binaries

| Agent | Binary | Default model | Check |
|-------|--------|--------------|-------|
| Antigravity | `agy` | Claude (Sonnet/Opus) | `agy --version` |
| OpenCode | `opencode` | Configurable | `opencode --version` |
| Kiro | `kiro-cli` | — | `kiro-cli --version` |

**OpenCode with DeepSeek Flash v4:**
```bash
opencode --model deepseek/deepseek-flash-v4 --print "$SPEC"
# Fallback if flag unsupported:
echo "$SPEC" | opencode --model deepseek/deepseek-flash-v4
# Last resort: Claude main thread
```

---

## Update Mode — `--update`

Use after code changes. understand-anything incremental — re-analyzes affected files only.

```
.understand-anything/meta.json stores file hashes
agy "/understand" (no --full) → diff hashes vs git → re-run affected batches only
→ merge new nodes into existing knowledge-graph.json + update ONBOARDING.md
```

**Prerequisites for `--update`:**
```bash
UPDATE_MODE=false
for arg in "$@"; do
  [ "$arg" = "--update" ] && UPDATE_MODE=true
done

if [ "$UPDATE_MODE" = "true" ]; then
  [ ! -f "$PROJECT_ROOT/.understand-anything/knowledge-graph.json" ] \
    && echo "❌ --update requires existing graph. Run without --update first." && exit 1
  [ ! -f "$PROJECT_ROOT/.understand-anything/meta.json" ] \
    && echo "❌ --update requires meta.json. Run without --update first." && exit 1
  echo "[update] Incremental mode — reading changed files from meta.json"
fi
```

**Per-phase update behavior:**
- Phase 1: run `/understand` without `--full` → understand-anything detects changed batches
- Phase 2: read `changedFiles[]` from meta.json → update only domain steps referencing changed files
- Phase 3: grep wiki for refs to changed files → regenerate stale pages only
- Phase 4: always rebuild HTML (fast — small wiki input)

**Read changed files from meta.json:**
```bash
CHANGED_FILES=$(python3 -c "
import json, sys
meta = json.load(open('$PROJECT_ROOT/.understand-anything/meta.json'))
changed = meta.get('changedFiles', meta.get('changed', []))
print('\n'.join(changed))
" 2>/dev/null || echo "")

if [ -z "$CHANGED_FILES" ]; then
  echo "[update] no changedFiles in meta.json — falling back to full rebuild"
  UPDATE_MODE=false
else
  echo "[update] Changed files:"; echo "$CHANGED_FILES"
fi
```

---

## Resume Mode — `/orca-onboard @DDMMYY-onboard-<slug>.md`

Argument starts with `@` → resume mode. Skip Phase 0 and Phase 0.5.

```bash
if [[ "$1" == @* ]]; then
  DRAFT_FILE="${1#@}"
  DRAFT_FILE=$(echo "$DRAFT_FILE" | tr '\\' '/')
  RESUME_MODE=true
  PROJECT_ROOT=$(grep "Project root:" "$DRAFT_FILE" | grep -oP '(?<=`)[^`]+(?=`)' | head -1)
  PROJECT_ROOT=$(echo "$PROJECT_ROOT" | tr '\\' '/')
else
  RESUME_MODE=false
fi
```

**Parse statuses:**
```bash
parse_status() {
  local keyword="$1"
  awk '/## Agent Task Assignment/{p=1} p && /^## [^A]/{p=0} p' "$DRAFT_FILE" \
    | grep "$keyword" | grep -oE 'pending|in-progress|done' | head -1
}

if [ "$RESUME_MODE" = true ]; then
  PHASE1_STATUS=$(parse_status "Phase 1 —")
  PHASE2_STATUS=$(parse_status "Phase 2 —")
  PHASE3_STATUS=$(parse_status "Phase 3 —")
  PHASE4_STATUS=$(parse_status "Phase 4 —")
  echo "[Resume] P1=$PHASE1_STATUS P2=$PHASE2_STATUS P3=$PHASE3_STATUS P4=$PHASE4_STATUS"
fi
```

**Skip rule:** `RESUME_MODE=true` + status `done` → skip phase, continue next.
**Retry rule:** `RESUME_MODE=true` + status `in-progress` → treat as interrupted, re-run.

---

## Status Update Helper

```bash
update_phase_status() {
  local keyword="$1"
  local status="$2"
  [ -z "$DRAFT_FILE" ] && echo "[WARN] DRAFT_FILE unset" && return 0
  local f=$(echo "$DRAFT_FILE" | tr '\\' '/')
  [ ! -f "$f" ] && echo "[WARN] DRAFT_FILE not found: $f" && return 0
  perl -i -pe "s/(\Q$keyword\E.*?)\| (?:pending|in-progress|done)/\$1| $status/g if /\Q$keyword\E/" "$f" \
    || sed -i "s/\(.*$(echo "$keyword" | sed 's/[^^]/[&]/g').*\)| [a-z-]*/\1| $status/" "$f" \
    || echo "[WARN] status update failed for: $keyword"
}
```

---

## Phase 0 — Pre-flight

```bash
# --- Dependency check ---
MISSING=()
agy --version >/dev/null 2>&1       || MISSING+=("agy (Antigravity)")
opencode --version >/dev/null 2>&1  || MISSING+=("opencode")
ls ~/.agents/skills/docs-site-macos/SKILL.md >/dev/null 2>&1 || MISSING+=("docs-site-macos skill")

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "❌ Missing dependencies:"
  for dep in "${MISSING[@]}"; do echo "   - $dep"; done
  echo ""
  echo "docs-site-macos: npx skills add rheinmir/setup@orca --skill docs-site-macos --global -y"
  exit 1
fi

# --- Resolve project root ---
PROJECT_ROOT=${1:-.}
test -d "$PROJECT_ROOT" || exit 1

# --- Bootstrap llmwiki if missing ---
if [ ! -d "$PROJECT_ROOT/llmwiki" ]; then
  echo "[orca-onboard] bootstrapping llmwiki..."
  git clone https://github.com/rheinmir/setup.git /tmp/orca-llmwiki-bootstrap --depth 1 -b orca -q
  cp -r /tmp/orca-llmwiki-bootstrap/llmwiki "$PROJECT_ROOT/llmwiki"
  rm -rf /tmp/orca-llmwiki-bootstrap
  echo "[orca-onboard] llmwiki bootstrapped OK"
fi

# --- Create dirs ---
mkdir -p $PROJECT_ROOT/.orca-onboard/{intermediate,tmp}
mkdir -p $PROJECT_ROOT/llmwiki/wiki/draft/{cave,uiux,orca}

# --- File count (display only — understand-anything handles batching) ---
git rev-parse HEAD 2>/dev/null > $PROJECT_ROOT/.orca-onboard/tmp/commit.txt
git ls-files > $PROJECT_ROOT/.orca-onboard/tmp/files.txt 2>/dev/null \
  || find $PROJECT_ROOT -type f \
       ! -path "*/.orca-onboard/*" ! -path "*/llmwiki/*" ! -path "*/.git/*" \
     > $PROJECT_ROOT/.orca-onboard/tmp/files.txt
FILE_COUNT=$(wc -l < $PROJECT_ROOT/.orca-onboard/tmp/files.txt | tr -d ' ')

# --- Probe agent availability ---
AGY_OK=$(agy --version 2>/dev/null && echo "✅ usable" || echo "❌ not found")
OC_OK=$(opencode --version 2>/dev/null && echo "✅ usable" || echo "❌ not found")
KIRO_OK=$(kiro-cli --version 2>/dev/null && echo "✅ usable" || echo "❌ not found")

echo "[pre-flight] $FILE_COUNT files | agy=$AGY_OK | opencode=$OC_OK"
```

---

## Phase 0.5 — Gate

**Required: create draft file FIRST, then ask user. Never reverse this order.**

```bash
DATE=$(date +%d%m%y)
PROJECT_SLUG=$(basename "$PROJECT_ROOT" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
DRAFT_FILE="$PROJECT_ROOT/llmwiki/wiki/draft/orca/${DATE}-onboard-${PROJECT_SLUG}.md"

# Determine graph agent (prefer agy, fallback opencode, fallback Claude)
AGY_AVAIL=$(agy --version 2>/dev/null && echo "yes" || echo "no")
OC_AVAIL=$(opencode --version 2>/dev/null && echo "yes" || echo "no")
if [ "$AGY_AVAIL" = "yes" ]; then
  AGENT_GRAPH="agy → /understand (tree-sitter + Louvain + Claude)"
elif [ "$OC_AVAIL" = "yes" ]; then
  AGENT_GRAPH="opencode → /understand (fallback, agy unavailable)"
else
  AGENT_GRAPH="Claude main thread (fallback — both agents unavailable)"
fi

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

## Agent Task Assignment
| Task | Agent | Model | Status |
|------|-------|-------|--------|
| Phase 1 — Graph generation ($FILE_COUNT files) | $AGENT_GRAPH | Claude (inside agy) | pending |
| Phase 2 — Domain enrichment | Claude main thread | Sonnet | pending |
| Phase 3 — Wiki generation | opencode | DeepSeek Flash v4 | pending |
| Phase 4 — HTML docs | opencode | DeepSeek Flash v4 | pending |

## What
Onboard \`$PROJECT_ROOT\` — understand-anything graph, domain enrichment, wiki, HTML.

## Output
- \`.understand-anything/knowledge-graph.json\` (tree-sitter + Louvain)
- \`.understand-anything/ONBOARDING.md\` (~20k tokens distilled)
- \`.orca-onboard/intermediate/domain-graph.json\`
- \`llmwiki/wiki/\` (index, concepts, entities, architecture, tours)
- \`llmwiki/html/onboarding-${PROJECT_SLUG}.html\`

## Files
| File | Action |
|------|--------|
| \`.understand-anything/knowledge-graph.json\` | created by agy |
| \`.understand-anything/ONBOARDING.md\` | created by agy |
| \`.orca-onboard/intermediate/domain-graph.json\` | created by Claude |
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
- Reasoning phases in Claude main thread — NOT dispatched to cheap models
- Mechanical phases: opencode + DeepSeek Flash v4

## Cost Estimate
| Phase | Agent | Est. tokens | Est. cost |
|-------|-------|-------------|-----------|
| Phase 1 (graph) | agy internal | ~1.5M | ~\$2-5 (agy's cost) |
| Phase 2 (domain) | Claude Sonnet | ~50k | ~\$0.50 |
| Phase 3 (wiki) | DeepSeek Flash | ~100k | ~\$0.02 |
| Phase 4 (HTML) | DeepSeek Flash | ~50k | ~\$0.01 |

## Origin
- **Draft:** \`wiki/draft/orca/${DATE}-onboard-${PROJECT_SLUG}.md\`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
EOF

# Update wiki index + log
echo "| [${DATE}-onboard-${PROJECT_SLUG}](draft/orca/${DATE}-onboard-${PROJECT_SLUG}.md) | draft | $(date +%Y-%m-%d) |" >> "$PROJECT_ROOT/llmwiki/wiki/index.md"
echo "## $(date +%Y-%m-%d) — orca-onboard — onboard-${PROJECT_SLUG}" >> "$PROJECT_ROOT/llmwiki/wiki/log.md"

echo "DRAFT_FILE=$DRAFT_FILE"
```

Show user: draft path, Agent Task Assignment table (4 phases + model), file count, cost estimate.
Ask for confirmation before continuing.

---

## Phase 1 — Graph Generation

**Agent:** agy → `/understand` | **Model:** Claude (inside agy)

> **READ FIRST** (before dispatch):
> - Check `.understand-anything/knowledge-graph.json` exists → decide skip/rebuild/incremental
> - Check `.understand-anything/meta.json` exists → decide if UPDATE_MODE is viable

**DO:** Dispatch `agy "/understand $PROJECT_ROOT"` — understand-anything handles everything internally: scan → Louvain batch → file analysis → architecture → tour → validation. DO NOT do batch analysis yourself.

**Required output:**
- `.understand-anything/knowledge-graph.json`
- `.understand-anything/ONBOARDING.md`
- `.understand-anything/meta.json`

**Skip check:** `RESUME_MODE=true` + `PHASE1_STATUS=done` → skip to Phase 2.

**Decision table (read file state first, then decide):**

| Graph exists | Flag | Action |
|-------------|------|--------|
| No | (none) | run `/understand` full |
| Yes | (none) | skip Phase 1, use existing graph |
| Yes | `--update` | run `/understand` incremental |
| Yes | `--full` | delete graph, run `/understand` full |

```bash
if [ "$RESUME_MODE" != "true" ] || [ "$PHASE1_STATUS" != "done" ]; then
  update_phase_status "Phase 1 —" "in-progress"

  if [ "$1" = "--full" ]; then
    rm -rf "$PROJECT_ROOT/.understand-anything"
    echo "[Phase 1] --full: cleared existing graph"
  fi

  if [ "$UPDATE_MODE" = "true" ]; then
    SPEC="/understand $PROJECT_ROOT"
    echo "[Phase 1] Incremental update — understand-anything re-analyzes changed batches only"
  elif [ -f "$PROJECT_ROOT/.understand-anything/knowledge-graph.json" ]; then
    echo "[Phase 1] Graph exists — skipping. Pass --full to rebuild or --update for incremental."
    update_phase_status "Phase 1 —" "done"
    continue 2>/dev/null || true
    SPEC=""
  else
    SPEC="/understand $PROJECT_ROOT"
  fi

  if [ -n "$SPEC" ]; then
    if agy --version >/dev/null 2>&1; then
      agy "$SPEC"
    elif opencode --version >/dev/null 2>&1; then
      opencode --print "$SPEC"
    else
      echo "[Phase 1] FALLBACK: Claude main thread runs understand-anything phases"
      # See onboard-codebase skill for fallback phases
    fi
  fi

  [ ! -f "$PROJECT_ROOT/.understand-anything/knowledge-graph.json" ] \
    && echo "❌ Phase 1 FAIL: knowledge-graph.json missing" && exit 1
  [ ! -f "$PROJECT_ROOT/.understand-anything/ONBOARDING.md" ] \
    && echo "❌ Phase 1 FAIL: ONBOARDING.md missing" && exit 1

  echo "✅ Phase 1 done"
  update_phase_status "Phase 1 —" "done"
fi
```

---

## Phase 2 — Domain Enrichment

**Agent:** Claude main thread (no dispatch) | **Model:** Sonnet

> **READ FIRST** (in order, before writing anything):
> 1. `.understand-anything/ONBOARDING.md` — full read (~20k tokens)
> 2. `.understand-anything/knowledge-graph.json` — read `layers` array + `entry-point` tagged nodes ONLY (⛔ NOT full file — context overflow)
> 3. If `UPDATE_MODE=true`: read existing `.orca-onboard/intermediate/domain-graph.json` (merge, don't overwrite)

**DO:**
1. From entry points → identify HTTP endpoints / CLI commands / events / cron jobs
2. Reverse-engineer: entry point → flow (process) → steps (actions @ file:line)
3. Build `domain → flow → step` hierarchy
4. Write `.orca-onboard/intermediate/domain-graph.json`

**Domain graph schema:**
```json
{
  "domains": [
    {
      "id": "domain:order-management",
      "name": "Order Management",
      "flows": [
        {
          "id": "flow:create-order",
          "name": "Create Order",
          "steps": [
            { "order": 0.1, "id": "step:validate-input", "file": "src/orders/validator.ts", "line": 42 },
            { "order": 0.2, "id": "step:check-inventory", "file": "src/inventory/checker.ts", "line": 15 }
          ]
        }
      ]
    }
  ]
}
```

**Output:** `.orca-onboard/intermediate/domain-graph.json`

**Skip check:** `RESUME_MODE=true` + `PHASE2_STATUS=done` → skip to Phase 3.

```bash
if [ "$RESUME_MODE" != "true" ] || [ "$PHASE2_STATUS" != "done" ]; then
  update_phase_status "Phase 2 —" "in-progress"
  # Claude main thread — no dispatch
  if [ "$UPDATE_MODE" = "true" ] && [ -n "$CHANGED_FILES" ]; then
    echo "[Phase 2] Update mode: re-enrich domain steps for changed files only"
    # Read existing domain-graph.json
    # Filter steps with filePath in CHANGED_FILES
    # Re-analyze those steps from ONBOARDING.md
    # Merge back into domain-graph.json (keep unchanged steps)
  else
    echo "[Phase 2] Full domain enrichment from ONBOARDING.md"
    # Read ONBOARDING.md + layers from knowledge-graph.json, write new domain-graph.json
  fi
  update_phase_status "Phase 2 —" "done"
fi
```

---

## Phase 3 — Wiki Generation

**Agent:** opencode | **Model:** `deepseek/deepseek-flash-v4`

> **READ FIRST** (inject into SPEC before dispatch — DeepSeek won't read files unless injected):
> 1. `.understand-anything/ONBOARDING.md` — full read
> 2. `.orca-onboard/intermediate/domain-graph.json` — full read
> 3. If `UPDATE_MODE=true`: grep `llmwiki/wiki/` for refs to `CHANGED_FILES` → identify stale pages
> - ⛔ DO NOT read `.understand-anything/knowledge-graph.json` — too large, context overflow

**DO:** Fill wiki templates from distilled content. No reasoning — mechanical template fill.

**Output structure:**
```
llmwiki/wiki/
├── index.md
├── concepts/          ← one file per architecture layer
├── entities/          ← domain entities + project-structure.md
├── architecture/      ← index, layers, dependencies, entry-points
└── tours/
    └── onboarding-tour.md
```

**Skip check:** `RESUME_MODE=true` + `PHASE3_STATUS=done` → skip to Phase 4.

```bash
if [ "$RESUME_MODE" != "true" ] || [ "$PHASE3_STATUS" != "done" ]; then
  update_phase_status "Phase 3 —" "in-progress"

  if [ "$UPDATE_MODE" = "true" ] && [ -n "$CHANGED_FILES" ]; then
    STALE_PAGES=$(grep -rl "$CHANGED_FILES" "$PROJECT_ROOT/llmwiki/wiki/" 2>/dev/null | tr '\n' ' ')
    if [ -n "$STALE_PAGES" ]; then
      echo "[Phase 3] Stale wiki pages: $STALE_PAGES"
      SPEC="Update these wiki pages based on changes in ONBOARDING.md: $STALE_PAGES
Changed source files: $CHANGED_FILES
Do NOT regenerate unchanged pages. Preserve existing content in unchanged pages."
    else
      echo "[Phase 3] No stale wiki pages — skipping"
      update_phase_status "Phase 3 —" "done"
    fi
  else
    SPEC="Generate wiki pages from .understand-anything/ONBOARDING.md and .orca-onboard/intermediate/domain-graph.json.
Create: llmwiki/wiki/index.md, llmwiki/wiki/concepts/*.md (one per architecture layer),
llmwiki/wiki/entities/*.md (domain entities), llmwiki/wiki/architecture/*.md,
llmwiki/wiki/tours/onboarding-tour.md.
Use wikilink format [[page-name]]. Do NOT read knowledge-graph.json directly."
  fi

  opencode --model deepseek/deepseek-flash-v4 --print "$SPEC" \
    || opencode --print "$SPEC" \
    || echo "[WARN] opencode unavailable — Claude main thread fallback for wiki"

  update_phase_status "Phase 3 —" "done"
fi
```

---

## Phase 4 — HTML Docs

**Agent:** opencode | **Model:** `deepseek/deepseek-flash-v4`

> **READ FIRST** (inject into SPEC before dispatch — DeepSeek won't read files unless injected):
> 1. `llmwiki/wiki/index.md` — list all wiki pages
> 2. `llmwiki/wiki/architecture/index.md` — architecture overview
> 3. `llmwiki/wiki/tours/onboarding-tour.md` — tour steps
> 4. `llmwiki/wiki/concepts/*.md` — layer descriptions

**Required output rules:**
- Output to `llmwiki/html/onboarding-<project-slug>.html` — NEVER project root
- Cover: architecture overview, graph summary (from ONBOARDING.md), layer diagram, tour steps
- Animated SVG for architecture diagram
- Checkboxes: `<input type="checkbox">` — NO `☐` Unicode
- Apply `docs-site-macos` style (glassmorphism, macOS chrome)

**Skip check:** `RESUME_MODE=true` + `PHASE4_STATUS=done` → skip.

```bash
if [ "$RESUME_MODE" != "true" ] || [ "$PHASE4_STATUS" != "done" ]; then
  update_phase_status "Phase 4 —" "in-progress"

  SPEC="Generate onboarding HTML doc from wiki files at llmwiki/wiki/.
Cover: project overview, architecture layers, domain flows, guided tour.
Apply docs-site-macos style (glassmorphism, macOS window chrome, animated SVG diagrams).
Output: llmwiki/html/onboarding-${PROJECT_SLUG}.html
Use real <input type='checkbox'> not Unicode checkboxes."

  opencode --model deepseek/deepseek-flash-v4 --print "$SPEC" \
    || opencode --print "$SPEC" \
    || {
      echo "[Phase 4] opencode unavailable — falling back to docs-site-macos skill (Claude)"
      # Invoke docs-site-macos skill in Claude main thread as fallback
    }

  ls "$PROJECT_ROOT/llmwiki/html/onboarding-${PROJECT_SLUG}.html" \
    && echo "✅ Phase 4 done" \
    || echo "❌ Phase 4 FAIL: HTML not found"

  update_phase_status "Phase 4 —" "done"
fi
```

**After completion:**
```bash
lsof -ti :8765 >/dev/null 2>&1 || nohup npx serve -p 8765 > /tmp/serve.log 2>&1 &
echo "→ http://localhost:8765/llmwiki/html/onboarding-${PROJECT_SLUG}.html"
```

---

## Rules

- **READ BEFORE ACT** — each phase reads all inputs in `READ FIRST` block before any action. Never ask user about something already in a file.
- **NO full `knowledge-graph.json` reads after Phase 1** — use `ONBOARDING.md` instead
- Real file paths only — never fabricate
- Domain graph: only reference real file:line, verify against code
- Wiki: wikilink format `[[page-name]]`
- Tour: 5-15 steps, start with project overview
- Reasoning tasks (domain, architecture): Claude main thread only

## Errors

- Phase 1 fail (agy) → check `/understand` skill installed in agy; fallback to opencode
- Phase 1 fail (no graph) → check permissions; manual: `agy "/understand $PROJECT_ROOT"`
- Phase 2 domain empty → no HTTP/CLI/event entry points found; write empty domains array
- Phase 3 fail → check opencode model config; fallback Claude main thread
- Phase 4 fail → fallback: invoke docs-site-macos skill directly in Claude

---

## Output Report

After all phases complete, write propose draft to wiki.

**1. Filename:** `DDMMYY-<ten>.md` — today's date + 2-4 kebab-case summary words

**2. Write** `llmwiki/wiki/draft/orca/DDMMYY-<ten>.md`:

```
# DDMMYY-<ten>
**Type:** draft
**Status:** proposed
**Tags:** orca-onboard, output-report
**Proposed:** YYYY-MM-DD

## Agent Task Assignment
| Task | Agent | Model | Status |
|------|-------|-------|--------|
| Phase 1 — Graph generation | agy /understand | Claude (agy) | done |
| Phase 2 — Domain enrichment | Claude main | Sonnet | done |
| Phase 3 — Wiki generation | opencode | DeepSeek Flash v4 | done |
| Phase 4 — HTML docs | opencode | DeepSeek Flash v4 | done |

## What
<One sentence>

## Output
<Key artefacts>

## Files
| File | Action |
|------|--------|
| `.understand-anything/knowledge-graph.json` | created |
| `llmwiki/wiki/index.md` | created/modified |
| `llmwiki/html/onboarding-<slug>.html` | created |

## Notes
- Invoked via: `/orca-onboard` skill

## Origin
- **Draft:** `wiki/draft/orca/DDMMYY-<ten>.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
```

**3. Update wiki index & log:**
- `llmwiki/wiki/index.md` — append: `| [DDMMYY-<ten>](draft/orca/DDMMYY-<ten>.md) | draft | YYYY-MM-DD |`
- `llmwiki/wiki/log.md` — append: `## YYYY-MM-DD — orca-onboard — <ten>`

**4. Update statuses & sync push — REQUIRED:**
- Update Status column in draft file to reflect actual run
- Clone `rheinmir/setup` branch `orca`, copy updated SKILL.md, push:
  ```bash
  git clone git@github.com:rheinmir/setup.git /tmp/rheinmir-setup-sync -b orca --depth 1
  cp ~/.agents/skills/orca-onboard/SKILL.md /tmp/rheinmir-setup-sync/skills/orca-onboard/SKILL.md
  cd /tmp/rheinmir-setup-sync
  git add .
  git commit -m "skill: orca-onboard — wrap understand-anything, DeepSeek mechanical dispatch"
  git push origin orca
  rm -rf /tmp/rheinmir-setup-sync
  ```

> Skip Output Report only if skill produced zero artefacts and zero decisions.
