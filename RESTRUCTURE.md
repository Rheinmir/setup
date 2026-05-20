# Restructure LLM Wiki — agent-executable plan

> Một file duy nhất. Agent đọc và tự làm hết, không hỏi lại.

**Template repo gốc:** `https://github.com/Rheinmir/setup.git` (nhánh `master`)
**Dùng làm chuẩn để so sánh cấu trúc đích.** Nếu đang ở dự án downstream, clone repo này về temp để diff.

---

## 1. Tạo branch `restructure` từ master

```bash
git checkout master
git pull
git checkout -b restructure
```

## 2. Gom toàn bộ framework vào `llmwiki/`

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

Tất cả path `raw/` → `llmwiki/raw/`, `wiki/` → `llmwiki/wiki/`, `html/` → `llmwiki/html/`, `skills/` → `llmwiki/skills/<loop>/` trong:
- `llmwiki/skills/wiki-loop/ingest.md`
- `llmwiki/skills/wiki-loop/query.md`
- `llmwiki/skills/wiki-loop/lint.md`
- `llmwiki/skills/dev-loop/propose.md`
- `llmwiki/skills/dev-loop/impact-check.md`
- `llmwiki/skills/dev-loop/safe-change.md`
- `llmwiki/skills/dev-loop/verify-before-commit.md`
- `llmwiki/skills/dev-loop/onboard-codebase.md`
- `llmwiki/skills/utils/sync-template.md`
- `llmwiki/skills/utils/md-to-html.md`

Mỗi path dạng `` `raw/` `` → `` `llmwiki/raw/` ``, `` `wiki/concepts/` `` → `` `llmwiki/wiki/concepts/` ``, v.v.

## 4. Cập nhật skill table trong AGENT.md + CLAUDE.md

Thêm cột Loop, sửa path thành `skills/<loop>/<skill>.md`:
- ingest → `skills/wiki-loop/ingest.md` (wiki-loop)
- query → `skills/wiki-loop/query.md` (wiki-loop)
- lint → `skills/wiki-loop/lint.md` (wiki-loop)
- propose → `skills/dev-loop/propose.md` (dev-loop)
- impact-check → `skills/dev-loop/impact-check.md` (dev-loop)
- safe-change → `skills/dev-loop/safe-change.md` (dev-loop)
- verify-before-commit → `skills/dev-loop/verify-before-commit.md` (dev-loop)
- onboard-codebase → `skills/dev-loop/onboard-codebase.md` (dev-loop)
- sync-template → `skills/utils/sync-template.md` (utils)
- md-to-html → `skills/utils/md-to-html.md` (utils)
- docs-site-macos → `skills/utils/docs-site-macos-skill.md` (utils)

## 5. Cập nhật 02-Setup-Knowledge-Base.md + 04-Scaffold-Application.md

Sửa path `wiki/` → `llmwiki/wiki/`, `skills/` → `llmwiki/skills/<loop>/` trong 2 file này.

## 6. Cập nhật .template-manifest.json

```json
{
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
  ]
}
```

## 7. Cập nhật skills/README.md

Phân loại skill theo loop.

## 8. Commit

```bash
git add -A
git commit -m "restructure: gom setup vào llmwiki/ + tổ chức skills theo loop"
git push origin restructure
```

## 9. Dự án cũ cập nhật (downstream)

Sau khi template repo đã có cấu trúc mới, chạy ở mỗi dự án cũ:

```bash
# Xác định remote
REMOTE="https://github.com/Rheinmir/setup.git"

# Clone template về temp để diff
TMPDIR=$(mktemp -d)
git clone "$REMOTE" "$TMPDIR" --depth 1

# So sánh cấu trúc thư mục giữa local và template
# Nếu template có llmwiki/ mà local chưa có → pull về
diff -r "$TMPDIR/llmwiki" llmwiki 2>/dev/null || {
  echo "Template có cấu trúc mới. Chạy sync-template hoặc copy thủ công."
}

# Dọn root: xoá thư mục cũ đã được gom vào llmwiki/
rm -rf skills wiki commands html raw 2>/dev/null
rm AGENT.md 2>/dev/null

# Đảm bảo root pointers
echo 'Đọc toàn bộ hướng dẫn tại llmwiki/.agent, llmwiki/AGENT.md và llmwiki/CLAUDE.md trước khi làm việc.' > .agent
echo 'Xem hướng dẫn đầy đủ tại `llmwiki/`. Ưu tiên đọc `llmwiki/AGENT.md` và `llmwiki/CLAUDE.md`.' > CLAUDE.md

# Commit
git add -A && git commit -m "sync: cập nhật cấu trúc llmwiki/"

# Dọn temp
rm -rf "$TMPDIR"
```
