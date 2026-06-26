# Rheinmir / setup — llmwiki AI-agent project template

Bộ khung biến AI Agent (Claude Code · opencode · Antigravity · Cursor…) thành **Tech Lead tự setup**
một dự án: nền tri thức (`llmwiki/`), quy trình dựng dự án, và **guardrail** chặn agent làm bậy.

> Nhánh làm việc chính: **`orca`**.

## ⚡ Cài guardrail (harness) — 1 dòng

Chạy trong thư mục gốc dự án của bạn:

```bash
curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash
```

Cài **1 lõi validator vendor-neutral**: chặn agent ghi vào `raw/`, bắt buộc mọi file wiki có `## Origin`,
qua **hook native** của công cụ (Claude/opencode) + **CI** làm sàn đảm bảo. Tự dò vendor, có `--clean` / `uninstall`.

- Chi tiết, gỡ, cài thủ công: [`harness/poc-vendor-neutral/README.md`](harness/poc-vendor-neutral/README.md)
- Bản tải về (offline): [Releases](../../releases)
- Dán vào system prompt AI để agent tự cài: xem code panel trong README của harness.

## 🏗️ Dựng dự án mới (workflow 3 bước prompt)

1. Copy thư mục `llmwiki/` sang gốc dự án mới.
2. Feed `01-Project-Kickoff.md` cho Agent → hỏi 3 câu → tạo `AGENT-business.md` / `AGENT-code.md`.
3. Feed `02-Setup-Knowledge-Base.md` → dựng cấu trúc `wiki/` · `skills/` · `commands/` · `raw/`.
4. Feed `04-Scaffold-Application.md` → scaffold codebase MVP.

Chi tiết: [`setup.md`](setup.md). Cài bộ skills: `npx skills add rheinmir/setup#orca --global --all`.

## 📂 Cấu trúc

| Thư mục / file | Là gì |
|---|---|
| `llmwiki/` | Khung tri thức: `wiki/` (concepts/entities/sources/draft), `skills/`, rules (`CLAUDE.md`/`AGENT.md`), `html/` docs |
| `harness/` | **Guardrail.** `validators/` + `scripts/install-harness.sh` = bản chính (hooks). `poc-vendor-neutral/` = PoC **1 lõi CLI vendor-neutral** (đề xuất redesign + installer 1-dòng) |
| `01/02/04-*.md`, `setup.md` | Prompt workflow dựng dự án |
| `.github/workflows/harness.yml` | CI: chạy validator + self-test mỗi PR |

## 📖 Tài liệu (single-file HTML, mở trực tiếp)

- `llmwiki/html/250626-walkthroughs.html` — walkthrough tương tác: harness & CI/CD chạy thế nào, từng bước.
- `llmwiki/html/250626-harness-cli-docs.html` — cách hoạt động & cài đặt harness vendor-neutral.
- `llmwiki/html/250626-harness-architecture-vs-current.html` — kiến trúc đề xuất vs hiện tại.
