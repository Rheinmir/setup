---
name: harness-tour
description: Tour 3 phút — Claude tự diễn cho user xem harness chặn mình thế nào trên project thật (bị deny ghi raw/, bị ép thêm Origin, bị Stop hook giữ). Tự dọn sạch demo. Trigger: "harness tour", "xem harness làm gì", "/harness-tour".
---

# Skill: harness-tour

## Purpose
Cho user THẤY (không phải đọc) harness hoạt động: bạn — Claude — cố tình vi phạm từng rule trên project thật, bị chặn, và tường thuật lại. Kết thúc không để lại bất kỳ rác nào.

## Pre-check
```bash
test -f llmwiki/.claude/hooks/pre_tool_use.py && echo ON || echo MISSING
```
Nếu MISSING → dừng, gợi ý: `bash harness/scripts/install-harness.sh .`
Nếu session hiện tại không load hooks (project root khác llmwiki, không có .claude/settings.json ở root) → nói rõ "tour cần mở session tại project đã cài" và dừng.

## Harness là HOOK, KHÔNG phải MCP (giải thích nếu user hỏi "sao /mcp không thấy")
Harness KHÔNG xuất hiện trong `/mcp` — và sẽ không bao giờ. Lớp chặn là PreToolUse/PostToolUse/Stop **hook** → kiểm bằng `/hooks` hoặc khối `hooks` trong `.claude/settings.json`, KHÔNG phải `/mcp`. MCP là thứ khác (tool cho model gọi). Hai installer KHÁC nhau, đừng lẫn:
- `harness/scripts/install-harness.sh` — harness CHÍNH, cài đúng các hook mà tour này diễn.
- `harness/poc-vendor-neutral/install.sh` — PoC vendor-neutral (CLI + gen-converters; cài qua hook `claude-hook`), cơ chế khác, cũng KHÔNG phải MCP.

## Kịch bản — diễn TUẦN TỰ, tường thuật TRƯỚC mỗi cảnh

**Mở màn** — nói: "Tôi sẽ cố tình vi phạm 3 rule. Hãy xem hệ thống chặn tôi."

**Cảnh 1 — Ghi vào raw/ (R1):**
- Tường thuật: "raw/ là inbox của con người, tôi không được ghi."
- Thử Write `llmwiki/raw/tour-demo.md` → sẽ bị `permissions.deny` hoặc PreToolUse chặn.
- Tường thuật kết quả: trích nguyên văn lý do bị chặn. KHÔNG retry.

**Cảnh 2 — Wiki file thiếu Origin (R2):**
- Tường thuật: "Tôi sẽ tạo wiki page mà 'quên' section Origin."
- Write `llmwiki/wiki/concepts/tour-demo.md` chỉ với `# Tour Demo\nmột dòng nội dung`.
- PostToolUse sẽ exit 2 → bạn nhận stderr → tường thuật: "Hook vừa bắt tôi, nguyên văn: …" → sửa file thêm `## Origin\n- harness-tour demo` → xác nhận lần ghi này pass.

**Cảnh 3 — Kết thúc lượt khi index nói dối (R3):**
- Tường thuật: "tour-demo.md đã tồn tại nhưng tôi cố tình KHÔNG cập nhật index.md, giờ tôi thử kết thúc lượt."
- Kết thúc response tại đó (không cập nhật index) → Stop hook sẽ block và đưa danh sách lệch về.
- Khi bị block: tường thuật nguyên văn thông báo, rồi cập nhật `wiki/index.md` đúng 1 row cho tour-demo, và tiếp tục sang dọn dẹp.

**Dọn dẹp (BẮT BUỘC):**
- Xóa `llmwiki/wiki/concepts/tour-demo.md` + xóa row của nó trong `index.md` (xóa cả hai cùng lượt để index không lệch).
- KHÔNG đụng bất kỳ file có sẵn nào khác.

**Kết màn** — tóm tắt 1 đoạn: 3 rule vừa chặn, kèm "mọi tool call vừa rồi đã nằm trong `.claude/audit/*.jsonl` — máy ghi, tôi không thể quên" (cat vài dòng cuối file audit làm bằng chứng). Nhắc: bản máy-diễn không cần phiên: `bash harness/scripts/tour.sh`.

## Rules
- Mỗi cảnh: tường thuật → vi phạm → trích nguyên văn lý do chặn → khắc phục. Không diễn tắt.
- Tuyệt đối không sửa/xóa file có sẵn của project; chỉ đụng file tên `tour-demo.*`.
- Nếu một cảnh KHÔNG bị chặn như kỳ vọng → dừng tour, báo rõ "hàng rào hỏng ở rule X" — đó là bug thật cần xử lý.
