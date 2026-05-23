---
name: join-project
description: Orient nhanh vào dự án đang chạy đã có llmwiki — read-only, không ghi wiki
---

# Skill: join-project

## When to use
Agent hoặc dev mới vào giữa dự án đã có `llmwiki/` — cần hiểu context nhanh mà không re-phân tích toàn bộ code.

## Steps

**1. CHECK — llmwiki hợp lệ không?**
```bash
test -f llmwiki/wiki/index.md && echo ok || echo "llmwiki missing — run new-project-setup instead"
```
Nếu missing: dừng, gợi ý chạy `new-project-setup`.

**2. Đọc tổng quan:**
```bash
# Đọc theo thứ tự:
READ: llmwiki/wiki/index.md           # danh sách toàn bộ wiki pages
READ: llmwiki/wiki/log.md (20 entries mới nhất)   # recent changes
READ: llmwiki/wiki/concepts/Architecture.md       # nếu tồn tại
```

**3. Tìm 3 concepts được reference nhiều nhất:**
```bash
grep -roh '\[\[.*?\]\]' llmwiki/wiki/ | sort | uniq -c | sort -rn | head -5
```
→ Pick 3 concept files từ danh sách, READ từng file.
Fallback nếu kết quả rỗng:
```bash
ls -t llmwiki/wiki/concepts/ | head -3
```
READ 3 files đầu theo mtime.

**4. CHECK tools:**
```bash
ls .claude/commands/ 2>/dev/null || echo "Claude skills: not installed"
ls ~/.agents/skills/ 2>/dev/null  || echo "Agent skills: not installed"
```
Nếu thiếu: `INVOKE: sync-template` (step 7 auto-installs tất cả).

**5. Synthesize & report:**
In ra:
- Project là gì, stack chính (từ Architecture.md hoặc index)
- 3 điểm kỹ thuật quan trọng nhất (từ concepts vừa đọc)
- Recent changes & open items (từ log.md)
- Skills state (installed / missing)
- Nếu có gaps lớn trong wiki: đề nghị `INVOKE: onboard-codebase` cho phần đó

## Rules
- Read-only — không tạo hoặc sửa bất kỳ wiki file nào
- Không setup RTK hay tools khác — đó là việc của `new-project-setup`
- Nếu wiki trống hoặc stale: nói rõ, đừng fabricate context
