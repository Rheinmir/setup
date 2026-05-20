# Migrate dự án cũ sang cấu trúc llmwiki/

## Cách chạy

```bash
# 1. Copy script vào root dự án cũ
# 2. Chạy
bash scripts/migrate-to-llmwiki.sh
# 3. Kiểm tra git status
git status
# 4. Commit
git add -A && git commit -m "migrate: gom setup vào llmwiki/"
```

## Kết quả

```
trước:                         sau:
root/                          root/
├── AGENT.md                   ├── CLAUDE.md        ← pointer
├── CLAUDE.md                  ├── .agent           ← pointer
├── .agent                     └── llmwiki/
├── skills/                        ├── AGENT.md
├── wiki/                         ├── CLAUDE.md
├── commands/                     ├── .agent
├── html/                         ├── skills/
├── raw/                          │   ├── wiki-loop/   (ingest, query, lint)
│                                 │   ├── dev-loop/    (propose, impact-check, safe-change, verify, onboard)
│                                 │   └── utils/       (sync-template, md-to-html, docs-site)
│                                 ├── wiki/
│                                 │   ├── decisions.md ← MỚI
│                                 │   └── sources/adr/ ← MỚI
│                                 ├── commands/
│                                 ├── html/
│                                 └── raw/
```

## Lưu ý

- Script dùng `git mv` — giữ nguyên lịch sử file
- File mới: `wiki/decisions.md` (decision log), `wiki/sources/adr/` (ADR)
- Không xoá file dự án — chỉ di chuyển file của llmwiki framework
