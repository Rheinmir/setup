21 Quy Tắc Không Thể Phá Vỡ  
Đây không phải hướng dẫn — chúng được CI, Husky hooks và review code thực thi. Vi phạm sẽ chặn PR của bạn.  
  
Quy tắc code  
Không commit bí mật hay thông tin xác thực (#1)  
Không thêm logic vào localDb.ts (#2)cái này là cái gì không rõ  
Không dùng eval() / new Function() (#3)cái này là cái gì không rõ  
Không commit thẳng vào main (#4)  
Không SQL thô trong route — dùng src/lib/db/ (#5)cái này là cái gì không rõ  
Không nuốt lặng lỗi trong SSE stream (#6)cái này là cái gì không rõ  
Luôn validate input bằng Zod schema (#7)cái này là cái gì không rõ  
Luôn kèm tests khi thay đổi production code (#8)  
Phủ code ≥ 60% statements/lines/functions/branches (#9)  
Không bỏ qua Husky hooks (#10) cái này là cái gì không rõ  
Quy tắc bảo mật  
Không nhúng OAuth client_id/secret thẳng — dùng resolvePublicCred() (#11)cái này là cái gì không rõ  
Không trả về err.stack/err.message thô trong response — dùng buildErrorBody() (#12)cái này là cái gì không rõ  
Không nội suy đường dẫn vào shell script — dùng env option (#13)cái này là cái gì không rõ  
Không bác bỏ alert CodeQL mà không có lý do kỹ thuật (#14)cái này là cái gì không rõ  
Không expose route spawn process mà không có isLocalOnlyPath() (#15, #17)cái này là cái gì không rõ  
Không ghi công AI trong commit/PR — không Co-Authored-By Claude/GPT (#16)  
PII redaction là opt-in, mặc định TẮT — không lật default (#20)cái này là cái gì không rõ  
Mọi bugfix cần TDD hoặc bằng chứng test live VPS (#18)  
Quy tắc quy trình phát triển  
Không dev trên shared main — luôn dùng worktree (#19)  
Xác nhận nhánh gốc trước khi tạo worktree  
Worktree PHẢI nằm trong .claude/worktrees/ — không chỗ khác  
Chỉ dọn dẹp worktree của bạn — không wildcard delete  
Cả hai runner phải pass: test:unit VÀ test:vitest cái này là cái gì không rõ  
Release-freeze: giữ merge khi nhãn release-freeze đang mở (#21)cái này là cái gì không rõ  
Tiền tố nhánh: feat/ fix/ refactor/ docs/ test/ chore/  
Định dạng commit: Conventional Commits (feat/fix/chore…)