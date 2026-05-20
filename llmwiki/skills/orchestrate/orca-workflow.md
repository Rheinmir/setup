# Skill: orca-workflow

## Purpose

Điều phối luồng làm việc hàng ngày qua Orca orchestration — propose → gate → dispatch → verify. khi chia agent làm việc chia các agent của từng engine 1:1 (claude cli , antigravity cli, opencode,...)  
  
claude sẽ chủ yếu phân tích, các model còn lại đảm nhiệm việc thực thi.  
  
với opencode có thể chú ý kill và bỏ ra khỏi pool phân phối nếu chờ quá lâu.

## Triggers

- User nói "propose &lt;tính năng&gt;", "feature request", "implement &lt;tên&gt;"
- User nói "chạy lint", "verify wiki"
- User nói "sync template", "upstream"

## Workflow: propose

1. **query**: Gather context từ wiki/ về tính năng được yêu cầu
2. **propose**: Tạo draft tại `llmwiki/wiki/sources/draft/DDMMYY-tên.md`
3. **gate**: `orca orchestration gate-create --question "Duyệt proposal này?"` → chờ user
4. **Sau duyệt**: Phân rã tasks từ proposal → `orca orchestration task-create` mỗi task
5. **dispatch**: `orca orchestration dispatch --task <id> --to <agent> --inject`
6. **Chờ**: `orca orchestration check --wait --types worker_done --timeout-ms 300000`
7. **Kiểm tra**: `verify-before-commit` tự động chạy trước mỗi commit

## Commands chính

```bash
orca orchestration run --spec "Propose: <tính năng>. Query wiki, tạo draft, gate chờ duyệt."
```

