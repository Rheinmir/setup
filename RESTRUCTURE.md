# Restructure LLM Wiki — agent-executable plan

> Một file duy nhất. Agent đọc và tự làm hết, không hỏi lại.

---

## 1. Tạo branch `restructure` từ master

```bash
git checkout master && git pull && git checkout -b restructure
```

## 2. Gom toàn bộ framework vào `llmwiki/`

Chạy các lệnh sau theo đúng thứ tự:

```bash
# Tạo thư mục đích
mkdir -p llmwiki/skills/wiki-loop \
         llmwiki/skills/dev-loop \
         llmwiki/skills/utils \
         llmwiki/wiki/concepts \
         llmwiki/wiki/entities \
         llmwiki/wiki/sources/draft \
         llmwiki/wiki/sources/adr \
         llmwiki/commands \
         llmwiki/html/assets \
         llmwiki/raw

# Di chuyển (git mv để giữ history)
git mv .agent llmwiki/
git mv AGENT.md llmwiki/
git mv CLAUDE.md llmwiki/
git mv skills/README.md llmwiki/skills/
git mv skills/ingest.md llmwiki/skills/wiki-loop/
git mv skills/query.md  llmwiki/skills/wiki-loop/
git mv skills/lint.md   llmwiki/skills/wiki-loop/
git mv skills/propose.md llmwiki/skills/dev-loop/
git mv skills/impact-check.md llmwiki/skills/dev-loop/
git mv skills/safe-change.md llmwiki/skills/dev-loop/
git mv skills/verify-before-commit.md llmwiki/skills/dev-loop/
git mv skills/onboard-codebase.md llmwiki/skills/dev-loop/
git mv skills/sync-template.md llmwiki/skills/utils/
git mv skills/md-to-html.md llmwiki/skills/utils/
git mv skills/docs-site-macos-skill.md llmwiki/skills/utils/
git mv wiki/README.md llmwiki/wiki/
git mv wiki/index.md llmwiki/wiki/
git mv wiki/log.md llmwiki/wiki/
git mv wiki/concepts/README.md llmwiki/wiki/concepts/
git mv wiki/concepts/_template.md llmwiki/wiki/concepts/
git mv wiki/entities/README.md llmwiki/wiki/entities/
git mv wiki/entities/_template.md llmwiki/wiki/entities/
git mv wiki/sources/README.md llmwiki/wiki/sources/
git mv wiki/sources/_template.md llmwiki/wiki/sources/
git mv wiki/sources/draft/README.md llmwiki/wiki/sources/draft/
git mv wiki/sources/draft/_template.md llmwiki/wiki/sources/draft/
git mv commands/serve llmwiki/commands/
git mv html/README.md llmwiki/html/
git mv html/assets/style.css llmwiki/html/assets/
git mv raw/README.md llmwiki/raw/
touch llmwiki/raw/.gitkeep

# File mới
cat > llmwiki/wiki/decisions.md << 'EOF'
# Decisions Log

| Date | Decision | Type | Context | Outcome |
|------|----------|------|---------|---------|
EOF

cat > llmwiki/wiki/sources/adr/README.md << 'EOF'
# Architecture Decision Records

> ADR ghi lại các quyết định kiến trúc quan trọng.

## Template
```markdown
# ADR-<số>: <Tiêu đề>
## Status [Proposed | Accepted | Deprecated | Superseded]
## Context
## Decision
## Consequences
```
EOF

# Root pointers
cat > .agent << 'EOF'
Đọc toàn bộ hướng dẫn tại llmwiki/.agent, llmwiki/AGENT.md và llmwiki/CLAUDE.md trước khi làm việc.
EOF

cat > CLAUDE.md << 'EOF'
Xem hướng dẫn đầy đủ tại `llmwiki/`. Ưu tiên đọc `llmwiki/AGENT.md` và `llmwiki/CLAUDE.md`.
EOF

# Xoá thư mục rỗng
rmdir skills wiki commands html raw 2>/dev/null || true
```

## 3. Cập nhật path trong skill files

Chạy các lệnh `sed` sau để thay thế toàn bộ path references trong mọi file:

### wiki-loop skills
```bash
# llmwiki/skills/wiki-loop/ingest.md
sed -i '' 's/`raw\/`/`llmwiki\/raw\/`/g' llmwiki/skills/wiki-loop/ingest.md
sed -i '' 's/`wiki\/concepts\/`/`llmwiki\/wiki\/concepts\/`/g' llmwiki/skills/wiki-loop/ingest.md
sed -i '' 's/`wiki\/entities\/`/`llmwiki\/wiki\/entities\/`/g' llmwiki/skills/wiki-loop/ingest.md
sed -i '' 's/`wiki\/sources\/`/`llmwiki\/wiki\/sources\/`/g' llmwiki/skills/wiki-loop/ingest.md
sed -i '' 's/`wiki\/index\.md`/`llmwiki\/wiki\/index.md`/g' llmwiki/skills/wiki-loop/ingest.md
sed -i '' 's/`wiki\/log\.md`/`llmwiki\/wiki\/log.md`/g' llmwiki/skills/wiki-loop/ingest.md

# llmwiki/skills/wiki-loop/query.md
sed -i '' 's/`raw\/`/`llmwiki\/raw\/`/g' llmwiki/skills/wiki-loop/query.md
sed -i '' 's/`wiki\/index\.md`/`llmwiki\/wiki\/index.md`/g' llmwiki/skills/wiki-loop/query.md
sed -i '' 's/`wiki\/log\.md`/`llmwiki\/wiki\/log.md`/g' llmwiki/skills/wiki-loop/query.md

# llmwiki/skills/wiki-loop/lint.md
sed -i '' 's/`raw\/`/`llmwiki\/raw\/`/g' llmwiki/skills/wiki-loop/lint.md
sed -i '' 's/`wiki\/index\.md`/`llmwiki\/wiki\/index.md`/g' llmwiki/skills/wiki-loop/lint.md
sed -i '' 's/`wiki\/log\.md`/`llmwiki\/wiki\/log.md`/g' llmwiki/skills/wiki-loop/lint.md
```

### dev-loop skills
```bash
# llmwiki/skills/dev-loop/propose.md
sed -i '' 's/`wiki\/sources\/draft\//`llmwiki\/wiki\/sources\/draft\//g' llmwiki/skills/dev-loop/propose.md
sed -i '' 's/`wiki\/index\.md`/`llmwiki\/wiki\/index.md`/g' llmwiki/skills/dev-loop/propose.md
sed -i '' 's/`wiki\/log\.md`/`llmwiki\/wiki\/log.md`/g' llmwiki/skills/dev-loop/propose.md

# llmwiki/skills/dev-loop/impact-check.md
sed -i '' 's/`wiki\/`/`llmwiki\/wiki\/`/g' llmwiki/skills/dev-loop/impact-check.md

# llmwiki/skills/dev-loop/verify-before-commit.md
sed -i '' 's/`wiki\/sources\/draft\//`llmwiki\/wiki\/sources\/draft\//g' llmwiki/skills/dev-loop/verify-before-commit.md
sed -i '' 's/`wiki\/concepts\/`/`llmwiki\/wiki\/concepts\/`/g' llmwiki/skills/dev-loop/verify-before-commit.md
sed -i '' 's/`wiki\/entities\/`/`llmwiki\/wiki\/entities\/`/g' llmwiki/skills/dev-loop/verify-before-commit.md
sed -i '' 's/`wiki\/sources\/`/`llmwiki\/wiki\/sources\/`/g' llmwiki/skills/dev-loop/verify-before-commit.md
sed -i '' 's/`wiki\/index\.md`/`llmwiki\/wiki\/index.md`/g' llmwiki/skills/dev-loop/verify-before-commit.md
sed -i '' 's/`wiki\/log\.md`/`llmwiki\/wiki\/log.md`/g' llmwiki/skills/dev-loop/verify-before-commit.md

# llmwiki/skills/dev-loop/onboard-codebase.md
sed -i '' 's/`wiki\//`llmwiki\/wiki\//g' llmwiki/skills/dev-loop/onboard-codebase.md
```

### utils skills
```bash
# llmwiki/skills/utils/sync-template.md
sed -i '' 's/`skills\/`/`llmwiki\/skills\/`/g' llmwiki/skills/utils/sync-template.md
sed -i '' 's/`wiki\/concepts\/`/`llmwiki\/wiki\/concepts\/`/g' llmwiki/skills/utils/sync-template.md
sed -i '' 's/`wiki\/log\.md`/`llmwiki\/wiki\/log.md`/g' llmwiki/skills/utils/sync-template.md

# llmwiki/skills/utils/md-to-html.md
sed -i '' 's/`html\/`/`llmwiki\/html\/`/g' llmwiki/skills/utils/md-to-html.md
```

### Các file còn lại (AGENT.md, CLAUDE.md, template, README, raw/README)
```bash
# llmwiki/AGENT.md — update Rules + skill table + invocation
sed -i '' 's/`raw\/`/`llmwiki\/raw\/`/g' llmwiki/AGENT.md
sed -i '' 's/`wiki\/index\.md`/`llmwiki\/wiki\/index.md`/g' llmwiki/AGENT.md
sed -i '' 's/`wiki\/log\.md`/`llmwiki\/wiki\/log.md`/g' llmwiki/AGENT.md
sed -i '' 's/`wiki\/`/`llmwiki\/wiki\/`/g' llmwiki/AGENT.md
sed -i '' 's/`concepts\//`llmwiki\/wiki\/concepts\//g' llmwiki/AGENT.md
sed -i '' 's/`entities\//`llmwiki\/wiki\/entities\//g' llmwiki/AGENT.md
sed -i '' 's/`sources\//`llmwiki\/wiki\/sources\//g' llmwiki/AGENT.md

# llmwiki/CLAUDE.md — same updates as AGENT.md
sed -i '' 's/`raw\/`/`llmwiki\/raw\/`/g' llmwiki/CLAUDE.md
sed -i '' 's/`wiki\/index\.md`/`llmwiki\/wiki\/index.md`/g' llmwiki/CLAUDE.md
sed -i '' 's/`wiki\/log\.md`/`llmwiki\/wiki\/log.md`/g' llmwiki/CLAUDE.md
sed -i '' 's/`wiki\/`/`llmwiki\/wiki\/`/g' llmwiki/CLAUDE.md

# Template files
sed -i '' 's/`raw\/<filename>`/`llmwiki\/raw\/<filename>`/g' llmwiki/wiki/concepts/_template.md
sed -i '' 's/`wiki\/sources\/draft\/<filename>`/`llmwiki\/wiki\/sources\/draft\/<filename>`/g' llmwiki/wiki/concepts/_template.md
sed -i '' 's/`raw\/<filename>`/`llmwiki\/raw\/<filename>`/g' llmwiki/wiki/entities/_template.md
sed -i '' 's/`wiki\/sources\/draft\/<filename>`/`llmwiki\/wiki\/sources\/draft\/<filename>`/g' llmwiki/wiki/entities/_template.md
sed -i '' 's/`wiki\/sources\/draft\//`llmwiki\/wiki\/sources\/draft\//g' llmwiki/wiki/sources/draft/_template.md

# README files
sed -i '' 's/`raw\/`/`llmwiki\/raw\/`/g' llmwiki/wiki/sources/README.md
sed -i '' 's/`raw\/`/`llmwiki\/raw\/`/g' llmwiki/wiki/README.md
sed -i '' 's/`raw\/`/`llmwiki\/raw\/`/g' llmwiki/skills/README.md
sed -i '' 's/`raw\/`/`llmwiki\/raw\/`/g' llmwiki/raw/README.md
sed -i '' 's/`wiki\/`/`llmwiki\/wiki\/`/g' llmwiki/raw/README.md
sed -i '' 's/`wiki\/sources\/draft\//`llmwiki\/wiki\/sources\/draft\//g' llmwiki/skills/README.md
```

## 4. Cập nhật skill table trong `llmwiki/AGENT.md` + `llmwiki/CLAUDE.md`

Thay thế skill table header để thêm cột Loop, và thêm các skill đang thiếu.

```bash
# Trong llmwiki/AGENT.md — header đã có cột Loop, chỉ cần thêm 4 skill còn thiếu vào cuối bảng
# Thêm các dòng sau ngay dòng cuối bảng (trước ## Invocation rules):
# | `onboard-codebase` | Deep analysis of legacy code to populate Wiki | `skills/dev-loop/onboard-codebase.md` | dev-loop |
# | `sync-template` | Upstreaming template improvements to master repo | `skills/utils/sync-template.md` | utils |
# | `md-to-html` | User wants to render a professional HTML report | `skills/utils/md-to-html.md` | utils |
# | `docs-site-macos` | User wants macOS-style documentation site | `skills/utils/docs-site-macos-skill.md` | utils |

# Thêm invocation rules bị thiếu
sed -i '' '/^## Invocation rules$/,/^$/{
  /^## Invocation rules$/a\
- Before every commit → invoke `verify-before-commit`
}' llmwiki/AGENT.md

# Trong llmwiki/CLAUDE.md — thay thế toàn bộ skill section
```

Nội dung `llmwiki/CLAUDE.md` phần Skills cần ghi đè thành:

```markdown
## Skills

| Skill | Invoke when | File | Loop |
|-------|------------|------|------|
| `ingest` | A new file appears in `llmwiki/raw/` | `skills/wiki-loop/ingest.md` | wiki-loop |
| `query` | User asks a question requiring wiki synthesis | `skills/wiki-loop/query.md` | wiki-loop |
| `lint` | After every 10 ingests, or wiki feels stale | `skills/wiki-loop/lint.md` | wiki-loop |
| `propose` | Any new feature or change is requested | `skills/dev-loop/propose.md` | dev-loop |
| `impact-check` | Before modifying any shared symbol | `skills/dev-loop/impact-check.md` | dev-loop |
| `safe-change` | Editing code called from more than one place | `skills/dev-loop/safe-change.md` | dev-loop |
| `verify-before-commit` | Before every commit | `skills/dev-loop/verify-before-commit.md` | dev-loop |
| `onboard-codebase` | Deep analysis of legacy code to populate Wiki | `skills/dev-loop/onboard-codebase.md` | dev-loop |
| `sync-template` | Upstreaming template improvements to master repo | `skills/utils/sync-template.md` | utils |
| `md-to-html` | User wants to render a professional HTML report | `skills/utils/md-to-html.md` | utils |
| `docs-site-macos` | User wants macOS-style documentation site | `skills/utils/docs-site-macos-skill.md` | utils |
```

## 5. Cập nhật `02-Setup-Knowledge-Base.md` + `04-Scaffold-Application.md` + `README.md`

```bash
# 02-Setup-Knowledge-Base.md — body text paths
sed -i '' 's/\*\*`raw\/`\*\*/\*\*`llmwiki\/raw\/`\*\*/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/\*\*`wiki\/`\*\*/\*\*`llmwiki\/wiki\/`\*\*/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/`skills\/`/`llmwiki\/skills\/`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/`commands\/`/`llmwiki\/commands\/`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/`html\/`/`llmwiki\/html\/`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/a `raw\/` folder/a `llmwiki\/raw\/` folder/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/anything in `raw\/`/anything in `llmwiki\/raw\/`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/reads `raw\/`/reads `llmwiki\/raw\/`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/into `wiki\/`/into `llmwiki\/wiki\/`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/a `wiki\/` folder/a `llmwiki\/wiki\/` folder/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/from `raw\/`/from `llmwiki\/raw\/`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/Create `wiki\//Create `llmwiki\/wiki\//g' 02-Setup-Knowledge-Base.md
sed -i '' 's/NEVER write to `raw\/`/NEVER write to `llmwiki\/raw\/`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/update `wiki\/index\.md`/update `llmwiki\/wiki\/index.md`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/append to `wiki\/log\.md`/append to `llmwiki\/wiki\/log.md`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/`wiki\/`/`llmwiki\/wiki\/`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/New file in `raw\/`/New file in `llmwiki\/raw\/`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/move to correct `wiki\/`/move to correct `llmwiki\/wiki\/`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/add row to `wiki\/index\.md`/add row to `llmwiki\/wiki\/index.md`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/log the move in `wiki\/log\.md`/log the move in `llmwiki\/wiki\/log.md`/g' 02-Setup-Knowledge-Base.md
sed -i '' 's/raw\/<filename>/llmwiki\/raw\/<filename>/g' 02-Setup-Knowledge-Base.md

# Nếu đã có `llmwiki/` prefix rồi thì bỏ qua (không thay đổi gấp đôi)

# 04-Scaffold-Application.md — thường đã đúng, kiểm tra:
# Line nói "Create llmwiki/wiki/concepts/Architecture.md" → keep

# README.md — update output tree và description
sed -i '' 's/`skills\/`/`llmwiki\/skills\/`/g' README.md
sed -i '' 's/`commands\/`/`llmwiki\/commands\/`/g' README.md
sed -i '' 's/`raw\/`/`llmwiki\/raw\/`/g' README.md
sed -i '' 's/`wiki\/`/`llmwiki\/wiki\/`/g' README.md
```

## 6. Cập nhật `.template-manifest.json`

Ghi đè toàn bộ nội dung `.template-manifest.json`:

```bash
cat > .template-manifest.json << 'EOF'
{
  "remote": "https://github.com/Rheinmir/setup.git",
  "includes": [
    "SKILL.md", "NOTE-migration.md",
    "CLAUDE.md", ".agent", ".template-manifest.json",
    "01-Project-Kickoff.md", "02-Setup-Knowledge-Base.md",
    "03-Cognee-MCP-Setup-Check.md", "04-Scaffold-Application.md",
    "RESTRUCTURE.md",
    "llmwiki/.agent", "llmwiki/AGENT.md", "llmwiki/CLAUDE.md",
    "llmwiki/commands/serve",
    "llmwiki/html/README.md", "llmwiki/html/assets/style.css",
    "llmwiki/raw/README.md",
    "llmwiki/skills/README.md",
    "llmwiki/skills/wiki-loop/ingest.md",
    "llmwiki/skills/wiki-loop/query.md",
    "llmwiki/skills/wiki-loop/lint.md",
    "llmwiki/skills/dev-loop/propose.md",
    "llmwiki/skills/dev-loop/impact-check.md",
    "llmwiki/skills/dev-loop/safe-change.md",
    "llmwiki/skills/dev-loop/verify-before-commit.md",
    "llmwiki/skills/dev-loop/onboard-codebase.md",
    "llmwiki/skills/utils/sync-template.md",
    "llmwiki/skills/utils/md-to-html.md",
    "llmwiki/skills/utils/docs-site-macos-skill.md",
    "llmwiki/wiki/README.md",
    "llmwiki/wiki/index.md",
    "llmwiki/wiki/log.md",
    "llmwiki/wiki/decisions.md",
    "llmwiki/wiki/concepts/README.md",
    "llmwiki/wiki/concepts/_template.md",
    "llmwiki/wiki/entities/README.md",
    "llmwiki/wiki/entities/_template.md",
    "llmwiki/wiki/sources/README.md",
    "llmwiki/wiki/sources/_template.md",
    "llmwiki/wiki/sources/adr/README.md",
    "llmwiki/wiki/sources/draft/README.md",
    "llmwiki/wiki/sources/draft/_template.md"
  ],
  "excludes": [
    ".env",
    "node_modules",
    "backend/server",
    "data/*.db"
  ]
}
EOF
```

## 7. Cập nhật `llmwiki/skills/README.md`

Ghi đè nội dung:

```bash
cat > llmwiki/skills/README.md << 'EOF'
# skills/

Multi-step reusable workflows the agent invokes autonomously based on context. Each file defines one skill: when to use it, the steps, and the rules.

## wiki-loop — Quản lý tri thức (ingest → query → lint)
| Skill | File | Purpose |
|-------|------|---------|
| `ingest` | `wiki-loop/ingest.md` | Process a new `llmwiki/raw/` file into wiki pages |
| `query` | `wiki-loop/query.md` | Synthesize an answer from the wiki; persist new insights |
| `lint` | `wiki-loop/lint.md` | Health-check the wiki for orphans, contradictions, stale content |

## dev-loop — Feature lifecycle (propose → impact-check → safe-change → verify)
| Skill | File | Purpose |
|-------|------|---------|
| `propose` | `dev-loop/propose.md` | Plan a feature before coding; create a draft in `llmwiki/wiki/sources/draft/` |
| `impact-check` | `dev-loop/impact-check.md` | Map all dependents of a symbol before modifying it |
| `safe-change` | `dev-loop/safe-change.md` | Modify shared code without breaking existing behaviour |
| `verify-before-commit` | `dev-loop/verify-before-commit.md` | Gate every commit; promote draft to wiki after success |
| `onboard-codebase` | `dev-loop/onboard-codebase.md` | Deep analysis of legacy code to populate Wiki |

## utils — Công cụ phụ trợ
| Skill | File | Purpose |
|-------|------|---------|
| `sync-template` | `utils/sync-template.md` | Sync template improvements to master repo |
| `md-to-html` | `utils/md-to-html.md` | Render markdown → professional HTML |
| `docs-site-macos` | `utils/docs-site-macos-skill.md` | Build macOS-style documentation site |
EOF
```

## 8. Commit

```bash
git add -A
git commit -m "restructure: gom setup vào llmwiki/ + tổ chức skills theo loop"
git push origin restructure
```

## 9. Dự án cũ cập nhật (downstream)

```bash
# Pull cấu trúc mới từ sync-template
# Sau đó dọn root:
rm -rf skills wiki commands html raw 2>/dev/null
rm AGENT.md 2>/dev/null
git add -A && git commit -m "sync: cập nhật cấu trúc llmwiki/"
```
