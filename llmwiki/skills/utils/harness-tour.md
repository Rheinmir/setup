---
name: harness-tour
description: Tour — Claude tự diễn cho user xem harness chặn mình theo thời gian thực trên project thật. Hai độ dài — "short" = 3 cảnh (R1·R2·R3), "full" = 10 (R1–R10). Tự phát hiện PoC vendor-neutral (cách CHÍNH) hay harness production. Tự dọn sạch demo. Trigger: "harness tour", "xem harness làm gì", "/harness-tour", "test short", "test full".
---

# Skill: harness-tour

## Purpose
Cho user THẤY (không phải đọc) harness hoạt động: bạn — Claude — cố tình vi phạm rule trên project thật,
bị **hook chặn theo thời gian thực**, và tường thuật lại. Kết thúc không để lại rác.

## Chọn độ dài tour (đọc ARGUMENTS)
- Chứa `full` / `10` / "đầy đủ" → **FULL** (R1–R10).
- Còn lại (mặc định, hay `short`/`3`) → **SHORT** (3 cảnh: R1 · R2 · R3).

## Pre-check — phát hiện harness nào đang sống trong session
Chạy ở ROOT của session:
```bash
{ grep -q llmwiki-validate .claude/settings.json 2>/dev/null && test -f harness/poc-vendor-neutral/bin/llmwiki-validate.py && echo POC; }
test -f llmwiki/.claude/hooks/pre_tool_use.py && echo PROD
```
- In **`POC`** → cách CHÍNH. PoC nay đủ **R1–R10** (5 rule chặn ở PreToolUse + R3/R4/R8/R10 qua hook sự kiện).
- In **`PROD`** → harness production. Cùng R1–R10, cùng kịch bản short/full dưới đây; chỉ khác **tên hook script**
  (`pre_tool_use.py`/`post_tool_use.py`/`stop.py`) và R1 có thể chặn qua `permissions.deny`. Diễn y hệt.
- KHÔNG in gì → **MISSING. DỪNG** (đừng diễn giả), gợi ý cài (PoC là cách chính):
  ```bash
  curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash
  ```
  rồi **mở session Claude MỚI tại root project đó** (để `.claude/settings.json` được load) → gõ lại `/harness-tour`.

> Hook chỉ chặn khi session **load `.claude/settings.json` ở đúng root project đã cài**. Mở session ở repo nguồn /
> root khác → không có hook → tour KHÔNG diễn (diễn mà không bị chặn = dàn dựng, cấm).

## Harness là HOOK, KHÔNG phải MCP (giải thích nếu user hỏi "sao /mcp không thấy")
Lớp chặn là **PreToolUse hook** → kiểm bằng `/hooks` hoặc khối `hooks` trong `.claude/settings.json`, KHÔNG ở `/mcp`.
MCP là thứ khác (tool cho model gọi). PoC: hook gọi `llmwiki-validate claude-hook`. Production: `pre_tool_use.py`…

---

## Bảng map path → rule (DÙNG ĐÚNG path để mỗi cảnh chỉ kích 1 rule)
Nhiều rule cùng soi `wiki/` → chọn sai path là 2 rule cùng chặn, rối. Map chuẩn (theo `policy.yaml`):

| Rule | File để vi phạm | Vì sao CHỈ rule đó kích |
|---|---|---|
| **R1** no-write-raw | `llmwiki/raw/tour-demo.md` | deny_write glob `raw/**` |
| **R2** origin-required | `llmwiki/wiki/sources/draft/tour-demo.md` — body KHÔNG có `## Origin`, KHÔNG có `## Plan` | R9 không áp `sources/`; R7 cần `## Plan`+`proposed` mới kích |
| **R3** index-sync | (Stop) chính file R2 vừa tạo, CHƯA có trong `wiki/index.md` | `m_stop` quét `concepts/entities/sources/draft` so với index |
| **R5** folder-structure | `llmwiki/wiki/tour-demo.md` (ngay dưới `wiki/`, basename lạ) | forbid_root: `wiki/*.md` không thuộc allow-list |
| **R7** proposal-complete | `llmwiki/wiki/sources/draft/tour-demo-proposal.md` — CÓ `## Origin` + `## Plan` + `proposed`, THIẾU `## Agent Task Assignment` & `Sequence diagram` | có Origin nên R2 qua → R7 là cái chặn |
| **R9** okf-frontmatter | `llmwiki/wiki/concepts/tour-demo.md` — CÓ `## Origin` nhưng KHÔNG có YAML frontmatter | có Origin nên R2 qua; thiếu `type:` → R9 chặn |

Không-chặn-live (chỉ cho XEM artifact, nói rõ "không chặn"): **R4** (`.claude/audit/audit.jsonl` + `log.md`),
**R8** (dòng `[harness] N rule…` lúc SessionStart), **R10** (`.claude/audit/.docs-gate.json` đếm prompt).
Tầng repo: **R6** (pre-commit + CI `.github/workflows/harness.yml` + skill `/verify-before-commit`).

---

## KỊCH BẢN SHORT (mặc định) — 3 cảnh, diễn TUẦN TỰ, tường thuật TRƯỚC mỗi cảnh

**Mở màn:** "Tôi sẽ cố tình vi phạm 3 rule. Xem hook chặn tôi theo thời gian thực — không phải tôi tự nhường."

**Cảnh 1 — R1 (PreToolUse · deny ghi raw/):**
- Tường thuật: "raw/ là inbox của con người, agent không được ghi."
- **Write** `llmwiki/raw/tour-demo.md` → exit 2 → CHẶN. Trích **nguyên văn** stderr `[R1 no-write-raw] …`. KHÔNG retry. File không ra đời.

**Cảnh 2 — R2 (PreToolUse · ép `## Origin`):**
- Tường thuật: "Tạo file nguồn mà 'quên' `## Origin` → không truy được gốc."
- **Write** `llmwiki/wiki/sources/draft/tour-demo.md` body `# Tour Demo` + 1 dòng (KHÔNG có `## Origin`) → exit 2 → CHẶN. Trích `[R2 origin-required] …`.
- **Sửa**: Write lại đúng file đó, thêm `## Origin\n- harness-tour demo` → lần này **PASS**, file được ghi.

**Cảnh 3 — R3 (Stop · index nói dối):**
- Tường thuật: "File tour-demo vừa tạo nhưng tôi cố tình KHÔNG ghi nó vào `wiki/index.md`. Giờ thử kết thúc lượt."
- **Kết thúc response tại đây** mà không cập nhật index → Stop hook (`harness-events.py stop`) trả exit 2, đưa danh sách lệch về.
- Khi bị block: trích nguyên văn `[R3 index-sync] wiki/index.md chưa liệt kê: …`, rồi thêm đúng 1 row cho tour-demo vào `wiki/index.md`, sang dọn dẹp.

→ tiếp **Dọn dẹp** (dưới).

---

## KỊCH BẢN FULL (khi ARGUMENTS có `full`) — R1–R10 tuần tự

Diễn 6 cảnh **chặn-live** (R1,R2,R3,R5,R7,R9) + 3 cái **không-chặn cho xem artifact** (R4,R8,R10) + 1 cái **repo** (R6).
Nói rõ trước nhóm không-chặn: "3 rule sau KHÔNG chặn lúc gõ — chúng GHI/NHẮC; tôi sẽ chỉ artifact làm bằng."

**R1 — Write `llmwiki/raw/tour-demo.md`** → CHẶN (deny raw/). Trích, không retry.

**R2 — Write `llmwiki/wiki/sources/draft/tour-demo.md`** (thiếu `## Origin`) → CHẶN → sửa thêm `## Origin` → PASS.

**R3 — (Stop)** kết thúc lượt khi file R2 chưa vào `index.md` → Stop block → thêm row index → tiếp.
*(Trong FULL, để liền mạch có thể gộp R3 vào cuối: sau khi tạo các file PASS bên dưới, thử kết thúc 1 lượt còn lệch index → block → cập nhật index.)*

**R4 — log-append (KHÔNG chặn):** sau một Write PASS, chỉ `.claude/audit/audit.jsonl` vừa có dòng mới (tool+path+timestamp) và `.claude/audit/log.md` được sinh lại. `cat` vài dòng cuối làm bằng — "máy ghi, tôi không xoá được."

**R5 — Write `llmwiki/wiki/tour-demo.md`** (ngay dưới `wiki/`) → CHẶN `[R5 folder-structure] …` (file wiki phải nằm trong concepts/entities/…). Không retry.

**R6 — verify-before-commit (repo, KHÔNG chặn-live):** chỉ ra cổng commit gồm pre-commit hook + CI `.github/workflows/harness.yml` (gọi lõi `files` mode trên .md đổi) + skill `/verify-before-commit` (Claude tự soi code mới trước khi commit). Đây là tầng repo, không phải session — không demo block trực tiếp.

**R7 — Write `llmwiki/wiki/sources/draft/tour-demo-proposal.md`** có `## Origin` + `## Plan` + `proposed` nhưng THIẾU `## Agent Task Assignment` & `Sequence diagram` → CHẶN `[R7 proposal-complete] …` → sửa thêm 2 mục đó → PASS.

**R8 — pattern-health (KHÔNG chặn):** chạy `python3 harness/poc-vendor-neutral/bin/harness-events.py session` để hiện dòng `[harness] N rule đang gác…` (+ cảnh báo drift nếu policy lệch remote). Đây là thứ in lúc SessionStart.

**R9 — Write `llmwiki/wiki/concepts/tour-demo.md`** có `## Origin` nhưng KHÔNG có YAML frontmatter → CHẶN `[R9 okf-frontmatter] …` (thiếu `type`) → sửa thêm `---\ntype: concept\n---` lên đầu → PASS.

**R10 — docs-gate (KHÔNG chặn):** `cat .claude/audit/.docs-gate.json` cho thấy bộ đếm prompt; giải thích mỗi `LLMWIKI_DOCS_GATE_EVERY` (mặc định 5) lượt, UserPromptSubmit chèn directive đề nghị gọi `/docs-site-macos`.

**Kết FULL:** bảng 10 rule — cái nào chặn-live, cái nào ghi/nhắc, cái nào ở repo; trích `.claude/audit/*.jsonl` làm bằng.

---

## Dọn dẹp (BẮT BUỘC — cùng một lượt, kẻo R3 chặn)
Xóa MỌI file `tour-demo*` đã **PASS** (được tạo) **và** xóa row tương ứng trong `wiki/index.md` **trong cùng lượt**
(xóa file mà để row → index lệch → Stop hook chặn chính lượt dọn):
- SHORT: `wiki/sources/draft/tour-demo.md` + row của nó.
- FULL: thêm `wiki/sources/draft/tour-demo-proposal.md`, `wiki/concepts/tour-demo.md` + các row.
- Các file bị CHẶN (raw/tour-demo, wiki/tour-demo R5) không tồn tại → khỏi xóa.
- Artifact harness (`audit.jsonl`, `log.md`, `.docs-gate.json`) là bản ghi máy hợp lệ → **giữ nguyên**, không xóa.
- TUYỆT ĐỐI không đụng file có sẵn khác của project.

**Kết màn:** tóm 1 đoạn các rule vừa chặn + "mọi tool call vừa rồi nằm trong `.claude/audit/*.jsonl` — máy ghi, tôi không quên được" (cat vài dòng cuối). Bản máy-diễn không cần phiên: `bash harness/poc-vendor-neutral/demo.sh` (13 assertion) · `test-broad.sh` (63).

## Rules
- Mỗi cảnh: tường thuật → vi phạm → **trích nguyên văn lý do chặn** → khắc phục. Không diễn tắt.
- Chỉ đụng file tên `tour-demo*`; tuyệt đối không sửa/xóa file có sẵn của project.
- Một cảnh đáng-lẽ-chặn mà KHÔNG bị chặn → **dừng tour, báo "hàng rào hỏng ở rule X"** — đó là bug thật cần xử lý
  (KHÔNG áp dụng cho nhóm không-chặn R4/R6/R8/R10 — chúng vốn không block).
