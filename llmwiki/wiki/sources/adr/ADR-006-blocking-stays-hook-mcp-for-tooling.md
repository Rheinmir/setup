---
type: decision
title: "ADR-006: lớp CHẶN giữ là hook/CI — MCP chỉ cho phần công cụ/đọc"
status: accepted
tags: [adr, harness, mcp, hook, enforcement, boundary]
timestamp: 2026-06-28
---

# ADR-006: lớp chặn giữ là hook/CI, MCP chỉ cho công cụ/đọc

## Status
Accepted (2026-06-28) — chốt lại một phân tích từ 2026-06-25, promote từ draft local lên wiki.

## Context
Có ý tưởng "biến harness thành một MCP server" để mọi vendor dùng chung qua giao thức MCP. Câu hỏi kiến trúc: phần nào của harness nên là MCP, phần nào không?

Điểm mấu chốt: harness có hai loại việc rất khác nhau. Một là **CHẶN** — từ chối agent ghi vào `raw/`, ép mọi trang wiki có `## Origin`, chặn proposal thiếu cặp `.md`+`.html`. Hai là **CÔNG CỤ/ĐỌC** — đồng bộ template, kiểm tra sức khoẻ, truy vấn wiki, soi OKF, phát hiện drift nền.

MCP là cơ chế mà **agent CHỦ ĐỘNG gọi** một tool khi nó thấy cần. Bản chất đó không thể dùng để CHẶN: một lớp deny phải chặn agent *trước khi* nó kịp ghi, và phải chạy *dù agent không muốn*. Nếu lớp chặn là một MCP tool, agent chỉ việc… không gọi nó, và hành vi xấu lọt qua. Lớp chặn vì thế phải sống ở **hook** (PreToolUse của Claude Code, chạy trên mọi tool-call) và ở **CI** (chạy trên mọi PR/merge) — những nơi không thể bị bỏ qua.

## Decision
1. **Lớp chặn GIỮ là hook + CI, KHÔNG chuyển MCP.** Cụ thể: validators (`no_write_raw`, `origin_required`, `okf_frontmatter`, `index_sync`, `folder_structure`, `proposal_complete`) + `policy.yaml` được thực thi qua hook ở phiên (exit 2 = chặn) và qua pre-commit/CI ở repo. Đây là phần "không bypass được".
2. **Chỉ phần công cụ/đọc mới nên là MCP** — `sync-template`, `health-check`, truy vấn wiki, `okf-check`, và việc *check-drift nền* (so phiên bản template, báo lệch). Đây là việc agent gọi khi cần, không cần ép buộc, nên hợp với MCP.
3. **Ranh giới rõ:** *chặn → hook/CI*; *đọc/đồng-bộ/báo → MCP-able*. Một thứ chỉ lên MCP nếu việc "agent quên gọi nó" KHÔNG gây hại.

## Consequences
- (+) Lớp đảm bảo cốt lõi không bao giờ bị bypass (hook luôn chạy; CI là sàn cuối — xem [[harness-enforcement-floor]]).
- (+) Phần công cụ vẫn tiện lợi hoá qua MCP cho mọi vendor, không phải mỗi vendor viết lại.
- (+) Có tiêu chí dứt khoát cho mọi đề xuất "đưa X lên MCP": X có cần *ép* không? Cần ép → hook/CI. Không → MCP.
- (−) Hai cơ chế song song (hook để chặn, MCP để công cụ) thay vì một — nhưng đúng vai, không phải trùng lặp.

## Origin
- **Source:** distill từ draft local `250626-harness-mcp-scenarios.md` (một trang docs-site phân tích "harness ≠ MCP — lớp chặn phải ở hook") — promote lên wiki để bản chất sống sót (draft local là gitignored). Quyết định đã phản ánh trong kiến trúc đang chạy (hook + CI là lớp gác, MCP chưa được dùng cho lớp chặn).
- **Liên quan:** [[ADR-001-policy-as-source-of-truth]], [[harness-enforcement-floor]], [[rule-registry]].
