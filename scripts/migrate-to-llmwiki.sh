#!/usr/bin/env bash
set -euo pipefail

# migrate-to-llmwiki.sh
# Chạy 1 lần ở dự án cũ (phiên bản flat) để gom mọi thứ vào llmwiki/

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
err()   { echo -e "${RED}[✗]${NC} $1"; }

if [ -d "llmwiki" ]; then
  err "llmwiki/ đã tồn tại — bỏ qua (đã migrate rồi?)"
  exit 1
fi

echo "=== Migrate to llmwiki/ ==="
echo ""

mkdir -p llmwiki
mkdir -p llmwiki/skills/wiki-loop
mkdir -p llmwiki/skills/dev-loop
mkdir -p llmwiki/skills/utils
mkdir -p llmwiki/wiki/concepts
mkdir -p llmwiki/wiki/entities
mkdir -p llmwiki/wiki/sources/draft
mkdir -p llmwiki/wiki/sources/adr
mkdir -p llmwiki/commands
mkdir -p llmwiki/html/assets
mkdir -p llmwiki/raw
mkdir -p llmwiki/orca/flows 2>/dev/null || true

# Di chuyển file (và track rename trong git)
migrate_file() {
  local src="$1"
  local dst="$2"
  if [ -f "$src" ] && [ ! -f "$dst" ]; then
    git mv "$src" "$dst" 2>/dev/null || mv "$src" "$dst"
    info "$src → $dst"
  elif [ -f "$src" ] && [ -f "$dst" ]; then
    warn "$dst đã tồn tại — giữ nguyên, xoá $src"
    git rm "$src" 2>/dev/null || rm "$src"
  fi
}

# Root files
migrate_file ".agent"           "llmwiki/.agent"
migrate_file "AGENT.md"         "llmwiki/AGENT.md"
migrate_file "CLAUDE.md"        "llmwiki/CLAUDE.md"

# Skills — wiki-loop
migrate_file "skills/ingest.md" "llmwiki/skills/wiki-loop/ingest.md"
migrate_file "skills/query.md"  "llmwiki/skills/wiki-loop/query.md"
migrate_file "skills/lint.md"   "llmwiki/skills/wiki-loop/lint.md"

# Skills — dev-loop
migrate_file "skills/propose.md"              "llmwiki/skills/dev-loop/propose.md"
migrate_file "skills/impact-check.md"         "llmwiki/skills/dev-loop/impact-check.md"
migrate_file "skills/safe-change.md"          "llmwiki/skills/dev-loop/safe-change.md"
migrate_file "skills/verify-before-commit.md" "llmwiki/skills/dev-loop/verify-before-commit.md"
migrate_file "skills/onboard-codebase.md"     "llmwiki/skills/dev-loop/onboard-codebase.md"

# Skills — utils
migrate_file "skills/sync-template.md"            "llmwiki/skills/utils/sync-template.md"
migrate_file "skills/md-to-html.md"               "llmwiki/skills/utils/md-to-html.md"
migrate_file "skills/docs-site-macos-skill.md"    "llmwiki/skills/utils/docs-site-macos-skill.md"
migrate_file "skills/README.md"                   "llmwiki/skills/README.md"

# Wiki
migrate_file "wiki/README.md"              "llmwiki/wiki/README.md"
migrate_file "wiki/index.md"               "llmwiki/wiki/index.md"
migrate_file "wiki/log.md"                 "llmwiki/wiki/log.md"
migrate_file "wiki/concepts/README.md"     "llmwiki/wiki/concepts/README.md"
migrate_file "wiki/concepts/_template.md"  "llmwiki/wiki/concepts/_template.md"
migrate_file "wiki/entities/README.md"     "llmwiki/wiki/entities/README.md"
migrate_file "wiki/entities/_template.md"  "llmwiki/wiki/entities/_template.md"
migrate_file "wiki/sources/README.md"      "llmwiki/wiki/sources/README.md"
migrate_file "wiki/sources/_template.md"   "llmwiki/wiki/sources/_template.md"
migrate_file "wiki/sources/draft/README.md"   "llmwiki/wiki/sources/draft/README.md"
migrate_file "wiki/sources/draft/_template.md" "llmwiki/wiki/sources/draft/_template.md"

# Commands / html / raw
migrate_file "commands/serve"          "llmwiki/commands/serve"
migrate_file "html/README.md"          "llmwiki/html/README.md"
migrate_file "html/assets/style.css"   "llmwiki/html/assets/style.css"
migrate_file "raw/README.md"           "llmwiki/raw/README.md"

# Tạo file mới (nếu chưa có)
[ ! -f "llmwiki/wiki/decisions.md" ] && cat > "llmwiki/wiki/decisions.md" <<- 'EOF'
# Decisions Log

> Ghi lại các quyết định quan trọng (approve/reject proposal, chọn hướng kỹ thuật).

| Date | Decision | Type | Context | Outcome |
|------|----------|------|---------|---------|
|      |          |      |         |         |
EOF
info "llmwiki/wiki/decisions.md created"

[ ! -f "llmwiki/wiki/sources/adr/README.md" ] && cat > "llmwiki/wiki/sources/adr/README.md" <<- 'EOF'
# Architecture Decision Records

> ADR ghi lại các quyết định kiến trúc quan trọng, lý do chọn giải pháp.

## Template
```markdown
# ADR-<số>: <Tiêu đề>

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
Vấn đề cần giải quyết, các ràng buộc.

## Decision
Giải pháp được chọn.

## Consequences
Tác động tích cực/tiêu cực.
```
EOF
info "llmwiki/wiki/sources/adr/README.md created"

# Root pointer files
if [ ! -f ".agent" ]; then
  echo "Đọc toàn bộ hướng dẫn tại llmwiki/.agent, llmwiki/AGENT.md và llmwiki/CLAUDE.md trước khi làm việc." > .agent
  info ".agent pointer created"
fi

if [ ! -f "CLAUDE.md" ]; then
  echo "Xem hướng dẫn đầy đủ tại \`llmwiki/\`. Ưu tiên đọc \`llmwiki/AGENT.md\` và \`llmwiki/CLAUDE.md\`." > CLAUDE.md
  info "CLAUDE.md pointer created"
fi

# Xoá thư mục rỗng
rmdir skills wiki commands html raw 2>/dev/null || true
info "Cleaned up empty old dirs"

echo ""
echo "=== Done ==="
echo "Run 'git status' và commit để hoàn tất."
