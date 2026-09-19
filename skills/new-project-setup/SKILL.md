---
name: new-project-setup
disable-model-invocation: true
description: Deploy llmwiki từ đầu vào project mới — template pull, skill install, RTK, wiki seed, onboard
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: new-project-setup

## WHAT

### Purpose và context
- **Purpose:** dựng `llmwiki/` từ đầu cho một project: pull template + install skill, khung thư mục wiki, RTK (WSL), seed wiki, rồi onboard codebase.
- **Trigger (when to use):** Project chưa có `llmwiki/`. Hoặc reset từ đầu.
- **Non-goals:** không tự cài skill riêng (sync-template step 7 lo); không gọi lint riêng (onboard-codebase đã gồm); không cài RTK ngoài WSL; không tự kích hoạt (`disable-model-invocation: true`).

### Mental model
`check llmwiki → sync-template (template + skills) → khung thư mục wiki → RTK (chỉ WSL) → seed (project-requirements + log + index) → onboard-codebase (concepts + entities + lint) → output report`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | thư mục project | có | chạy tại root project |
| In | README.md, package.json hoặc go.mod | không | nguồn project name + stack cho seed |
| In | trả lời reset | khi `llmwiki/` đã tồn tại | có reset hay không |
| Out | `llmwiki/wiki/{concepts,entities,sources/draft}`, `llmwiki/{skills,raw}` | có | khung thư mục + `index.md`, `log.md`, `raw/.gitkeep` |
| Out | `llmwiki/wiki/sources/project-requirements.md` | có | frontmatter OKF + `## Origin` |
| Out | RTK đã hook | chỉ WSL | `rtk init -g` + hook trong `~/.claude/settings.json` |
| Out | wiki đã onboard + draft output report | có | concepts/entities do onboard-codebase sinh |

### Rules và capabilities
- RULE-01 (MUST): Skill install: sync-template step 7 xử lý — không duplicate
- RULE-02 (MUST): onboard-codebase includes lint — không gọi lint thêm
- RULE-03 (MUST): RTK guard `uname -r | grep -qi microsoft` bắt buộc trước curl
- Capabilities: ghi filesystem project; mạng (pull template, tải RTK); sửa config agent global (`~/.claude/settings.json`) chỉ qua `rtk init -g`; gọi skill con sync-template và onboard-codebase.

### Failure boundaries
- `llmwiki/` đã tồn tại → **clarify**: hỏi user reset không; không reset thì dừng.
- Không phải WSL → bước RTK skip (không phải lỗi).
- Hook RTK không thấy trong settings.json → **partial**, in "MANUAL: add rtk hook to settings.json".
- sync-template hoặc onboard-codebase lỗi → **failed** ở bước đó, báo user.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | project root | CHECK llmwiki tồn tại | `exists` hoặc `missing` | exists → B01 |
| W02 | effect | mạng | INVOKE sync-template: pull template + install skills | commands + skills đã cài | lỗi → failed |
| W03 | effect | — | Init wiki folder structure | khung thư mục | — |
| W04 | effect | OS | RTK token proxy (WSL only) — B02 | RTK hooked | không WSL → skip; thiếu hook → MANUAL |
| W05 | judgment | README/package.json/go.mod | Seed wiki: project-requirements, log, index | trang seed | — |
| W06 | effect | codebase | INVOKE onboard-codebase | concepts + entities + lint | lỗi → failed |
| W07 | effect | kết quả | Output Report draft | draft + index + log | — |

Chi tiết từng bước (nguồn chân lý cho W01–W07):

**1. CHECK llmwiki tồn tại:**
```bash
test -d llmwiki && echo exists || echo missing
```
`exists` → hỏi user reset không. Reset = xóa `concepts/` + `entities/`, **GIỮ** `log.md` + `sources/`.

**2. Pull template + install skills:**
```bash
# INVOKE: sync-template
# sync-template tự pull từ rheinmir/setup@orca và install skills vào:
#   .claude/commands/           → Claude Code
#   ~/.agents/skills/*/SKILL.md → OpenCode / Antigravity
```

**3. Init wiki folder structure:**
```bash
mkdir -p llmwiki/wiki/{concepts,entities,sources/draft} llmwiki/{skills,raw}
touch llmwiki/wiki/index.md llmwiki/wiki/log.md llmwiki/raw/.gitkeep
```

**4. RTK token proxy (WSL only):**
```bash
# Guard — chỉ chạy trong WSL:
uname -r | grep -qi microsoft || { echo "RTK install: WSL only — skip"; exit 0; }

# CHECK đã cài chưa:
rtk --version 2>/dev/null || {
  curl -fsSL https://github.com/rtk-ai/rtk/releases/latest/download/rtk-x86_64-unknown-linux-musl.tar.gz \
    | tar xz -C /usr/local/bin
}

# Init global config + patch ~/.claude/settings.json:
rtk init -g

# Verify hook:
grep -q "rtk hook claude" ~/.claude/settings.json && echo "RTK hooked" || echo "MANUAL: add rtk hook to settings.json"
```

**5. Seed wiki:**
```bash
# Đọc README.md, package.json hoặc go.mod → project name + stack
```
- Tạo `llmwiki/wiki/sources/project-requirements.md` — frontmatter + `## Origin`
- **OKF v0.1 (R9):** frontmatter là khối YAML `---` có `type` không rỗng — copy `_template.md`, đừng dùng `**Type:**` bold (format cũ).
- Append `llmwiki/wiki/log.md`: `## YYYY-MM-DD — init — <project-name>`
- Tạo `llmwiki/wiki/index.md` — header + empty table

**6. INVOKE: onboard-codebase** → populate `concepts/` + `entities/` + lint.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | W01 trả `exists` | hỏi user reset; reset = xóa `concepts/` + `entities/`, GIỮ `log.md` + `sources/` | user không reset → dừng | W02 |
| B02 | conditional_required | kernel chứa "microsoft" (WSL) | cài RTK nếu chưa có, `rtk init -g`, verify hook | không WSL → skip bước 4 | W05 |

### Validation và stopping
Kiểm bằng lệnh: `test -d llmwiki` ra `exists`; trên WSL grep settings.json in "RTK hooked"; `project-requirements.md` có frontmatter `type` (R9) + `## Origin`. Lint chạy trong onboard-codebase, không chạy lại. Dừng sau output report.

### Examples
- **Positive:** repo Go mới chưa có `llmwiki/` trên macOS → W01 `missing` → sync-template → mkdir khung → bước RTK in "RTK install: WSL only — skip" → seed từ `go.mod` → onboard-codebase → draft `DDMMYY-init-<project>.md`.
- **Boundary/failure:** chạy lại trên project đã có `llmwiki/` → W01 `exists` → hỏi reset; user đồng ý → chỉ xóa `concepts/` + `entities/`, `log.md` và `sources/` còn nguyên.

### Delivery — Output Report

After all main skill tasks complete, write a propose draft to the wiki.

#### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/sources/draft/DDMMYY-<ten>.md`:

```
---
type: draft
title: "DDMMYY-<ten>"
status: proposed
tags: [<skill-name>, output-report]
timestamp: YYYY-MM-DD
---

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
