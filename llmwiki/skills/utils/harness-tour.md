---
name: harness-tour
description: Tour — Claude tự diễn cho user xem harness chặn mình theo thời gian thực trên project thật (deny ghi raw/, ép thêm ## Origin). Tự phát hiện PoC vendor-neutral (cách CHÍNH) hay harness production rồi diễn đúng kịch bản. Tự dọn sạch demo. Trigger: "harness tour", "xem harness làm gì", "/harness-tour".
---

# Skill: harness-tour

## Purpose
Cho user THẤY (không phải đọc) harness hoạt động: bạn — Claude — cố tình vi phạm rule trên project thật,
bị **hook chặn theo thời gian thực**, và tường thuật lại. Kết thúc không để lại rác.

## Pre-check — phát hiện harness nào đang sống trong session
Chạy ở ROOT của session:
```bash
{ grep -q llmwiki-validate .claude/settings.json 2>/dev/null && test -f harness/poc-vendor-neutral/bin/llmwiki-validate.py && echo POC; }
test -f llmwiki/.claude/hooks/pre_tool_use.py && echo PROD
```
- In **`POC`** → diễn **kịch bản PoC** (R1 + R2). ← cách CHÍNH.
- In **`PROD`** → diễn **kịch bản Production** (R1 + R2 + R3).
- KHÔNG in gì → **MISSING. DỪNG** (đừng diễn giả), gợi ý cài (PoC là cách chính):
  ```bash
  curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash
  ```
  rồi **mở session Claude MỚI tại root project đó** (để `.claude/settings.json` được load) → gõ lại `/harness-tour`.

> Hook chỉ chặn khi session **load `.claude/settings.json` ở đúng root project đã cài**. Mở session ở repo nguồn /
> root khác → không có hook → tour KHÔNG diễn (diễn mà không bị chặn = dàn dựng, cấm).

## Harness là HOOK, KHÔNG phải MCP (giải thích nếu user hỏi "sao /mcp không thấy")
Harness KHÔNG ở `/mcp` và sẽ không bao giờ — lớp chặn là **PreToolUse hook** → kiểm bằng `/hooks` hoặc khối
`hooks` trong `.claude/settings.json`. MCP là thứ khác (tool cho model gọi). Hai installer KHÁC nhau:
- PoC (cách chính): `harness/poc-vendor-neutral/install.sh` hoặc one-liner bootstrap → hook gọi `llmwiki-validate claude-hook`.
- Production: `harness/scripts/install-harness.sh` → hook `pre_tool_use.py` / `post_tool_use.py` / `stop.py`.

---

## Kịch bản POC (2 cảnh) — diễn TUẦN TỰ, tường thuật TRƯỚC mỗi cảnh

**Mở màn:** "Tôi sẽ cố tình vi phạm 2 rule. Xem hook chặn tôi theo thời gian thực — không phải tôi tự nhường."

**Cảnh 1 — Ghi vào raw/ (R1 no-write-raw):**
- Tường thuật: "raw/ là inbox của con người, agent không được ghi."
- Thử **Write** `llmwiki/raw/tour-demo.md` → PreToolUse hook (`llmwiki-validate claude-hook`) trả **exit 2 → CHẶN**.
- Trích **nguyên văn** stderr (`[R1 no-write-raw] Chan ghi file vao raw/: …`). KHÔNG retry. File raw/ không bao giờ ra đời.

**Cảnh 2 — Wiki thiếu Origin (R2 require-origin):**
- Tường thuật: "Tạo wiki page mà 'quên' section ## Origin."
- **Write** `llmwiki/wiki/concepts/tour-demo.md` chỉ với `# Tour Demo` + 1 dòng nội dung → hook trả **exit 2 → CHẶN**
  (`[R2 origin-required] … thieu section '## Origin'`).
- Trích nguyên văn → **sửa**: Write lại đúng file đó nhưng thêm `## Origin\n- harness-tour demo` → lần này **PASS**, file được ghi.

**Lưu ý (nói rõ, KHÔNG diễn giả):** PoC KHÔNG có Stop-hook giữ index (R3). Việc đó nằm ở **tầng repo = CI**
(`.github/workflows/harness.yml`) — chặn lúc mở PR, không demo trực tiếp trong phiên được.

**Dọn dẹp (BẮT BUỘC):** xóa `llmwiki/wiki/concepts/tour-demo.md` (file tạo ở cảnh 2). KHÔNG đụng file có sẵn nào khác.
(raw/tour-demo.md bị chặn nên không tồn tại — khỏi xóa.)

**Kết màn:** tóm 1 đoạn — R1 + R2 bị chặn NGAY trong phiên qua 1 lõi `llmwiki-validate.py`; cái lọt session thì
**CI chặn lúc PR**. Bản máy-diễn không cần phiên: `bash harness/poc-vendor-neutral/demo.sh` (13 assertion).

---

## Kịch bản PRODUCTION (chỉ khi pre-check in `PROD`)

> Production `policy.yaml` có **R1–R10** (không phải 3). Tour mặc định diễn LIVE **3 cái dễ thấy nhất**
> (R1/R2/R3). Phần còn lại — nếu user muốn thì diễn thêm vì có cái cũng chặn-live:
> R1 no-write-raw · R2 origin-required · R3 index-sync(Stop) · R4 log-append (tự động, không chặn) ·
> **R5 folder-structure (chặn write file wiki ở root)** · R6 verify-before-commit (repo) ·
> **R7 proposal-complete (chặn write)** · R8 pattern-sync-health (báo cáo) ·
> **R9 okf-frontmatter (chặn write concept thiếu frontmatter/type)** · R10 docs-gate (nhắc, không chặn).
> Diễn-được-live: R1, R2, R5, R7, R9 (chặn lúc Write) + R3 (chặn lúc Stop).
>
> ⚠️ PoC vendor-neutral hiện CHỈ có **R1 + R2** (2/10) — redesign chưa port R3–R10. Nếu PoC thành cách chính
> thì cần thêm rule-kind vào `harness/poc-vendor-neutral/policy.yaml` cho R5/R7/R9…

**Cảnh 1 — R1:** Write `llmwiki/raw/tour-demo.md` → `permissions.deny`/PreToolUse chặn → trích nguyên văn.
**Cảnh 2 — R2:** Write `llmwiki/wiki/concepts/tour-demo.md` thiếu Origin → PostToolUse exit 2 → trích → thêm `## Origin` → pass.
**Cảnh 3 — R3 (Stop hook):** tạo tour-demo nhưng KHÔNG cập nhật `wiki/index.md` → kết thúc lượt → Stop hook block, trả danh sách lệch → cập nhật 1 row index → tiếp tục.
**Dọn dẹp:** xóa `wiki/concepts/tour-demo.md` + row của nó trong `index.md` (cùng lượt). **Kết màn:** 3 rule + bằng chứng `.claude/audit/*.jsonl` (cat vài dòng cuối); bản máy: `bash harness/scripts/tour.sh`.

---

## Rules
- Mỗi cảnh: tường thuật → vi phạm → **trích nguyên văn lý do chặn** → khắc phục. Không diễn tắt.
- Chỉ đụng file tên `tour-demo.*`; tuyệt đối không sửa/xóa file có sẵn của project.
- Một cảnh KHÔNG bị chặn như kỳ vọng → **dừng tour, báo "hàng rào hỏng ở rule X"** — đó là bug thật cần xử lý.
