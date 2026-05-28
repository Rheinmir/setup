---
name: join-project
description: Orient nhanh vào dự án đang chạy đã có llmwiki — read-only, không ghi wiki
---

# Skill: join-project

## When to use
Agent/dev mới vào giữa dự án đã có `llmwiki/` — hiểu context nhanh, không re-phân tích toàn bộ code.

## Steps

**1. CHECK llmwiki hợp lệ:**
```bash
test -f llmwiki/wiki/index.md && echo ok || echo "llmwiki missing — run new-project-setup instead"
```
Missing → dừng, gọi `new-project-setup`.

**2. Đọc tổng quan:**
```bash
# Đọc theo thứ tự:
READ: llmwiki/wiki/index.md           # danh sách toàn bộ wiki pages
READ: llmwiki/wiki/log.md (20 entries mới nhất)   # recent changes
READ: llmwiki/wiki/concepts/Architecture.md       # nếu tồn tại
```

**3. Top 3 concepts:**
```bash
grep -roh '\[\[.*?\]\]' llmwiki/wiki/ | sort | uniq -c | sort -rn | head -5
```
Pick 3 từ danh sách, READ từng file. Fallback nếu rỗng:
```bash
ls -t llmwiki/wiki/concepts/ | head -3
```

**4. CHECK tools:**
```bash
ls .claude/commands/ 2>/dev/null || echo "Claude skills: not installed"
ls ~/.agents/skills/ 2>/dev/null  || echo "Agent skills: not installed"
```
Thiếu → `INVOKE: sync-template`.

**5. Report:**
- Project + stack (từ Architecture.md/index)
- 3 kỹ thuật quan trọng (từ concepts)
- Recent changes + open items (log.md)
- Skills: installed/missing
- Wiki gaps lớn → `INVOKE: onboard-codebase`

## Rules
- Read-only — không tạo/sửa wiki file nào
- Không setup RTK/tools — việc của `new-project-setup`
- Wiki trống/stale: nói rõ, không fabricate context
