---
type: issue
kind: foundation
title: "code-graph MCP hỏng — đường GHI và đường ĐỌC trỏ hai DB khác nhau, mọi phiên vẫn được khuyên dùng nó trước"
status: open
assignee: maintainer
dispatch: human
entry: /fdk
priority: P1
tags: [issue, code-graph, mcp, orientation, foundation]
timestamp: 2026-07-20
id: 200726-code-graph-index-broken
source_session: "T-260719-02 — đo A/B code-graph (task T2 của proposal 190726-graph-lessons-grapuco)"
---

# Issue: code-graph MCP hỏng, nhưng orientation vẫn dặn mọi phiên dùng nó TRƯỚC

## Triệu chứng

Mọi truy vấn đọc của code-graph MCP đều lỗi schema:

```
mcp__code-graph__get_stats       → Error: no such table: files
mcp__code-graph__search_symbols  → Error: no such table: symbols
mcp__code-graph__list_projects   → trả 17 mục, TẤT CẢ đều tên "index.db"
```

Đã tự tay tái hiện trong phiên chính (không chỉ nghe agent báo), và **5 subagent độc lập** đều gặp đúng ba lỗi này.

## Nguyên nhân gốc (đã khoanh)

`mcp__code-graph__reindex_repo` **BÁO THÀNH CÔNG** — 2660 file, 21972 symbol, 276595 edge — nhưng ngay sau đó `search_symbols` vẫn `no such table: symbols`.

Nghĩa là **đường GHI và đường ĐỌC trỏ vào hai database khác nhau**. Dấu hiệu phụ củng cố: `list_projects` trả về 17 mục cùng tên `"index.db"` — server đang lấy *tên project* từ *tên file DB*, rồi query một DB chưa hề có schema.

Server nằm ngoài repo này: `/Volumes/giatbhSSD(APFS)/workspace/graph/server.py` (khai trong `~/.claude.json` → `mcpServers.code-graph`, chạy kèm `--watch`).

## Vì sao P1 chứ không phải "tool phụ hỏng thì thôi"

Hook orientation in ở **mỗi phiên** dòng đại ý: *"QUERY trước khi đọc/grep rộng — dùng `mcp__code-graph__*` để ĐỊNH VỊ code nhanh, đừng grep mù."*

Nên đây không phải một tool hỏng nằm im. Đây là một tool hỏng mà framework **chủ động lùa mọi phiên vào**. Agent nghe lời, gọi code-graph, ăn lỗi, rồi mới quay về grep — trả phí cho cả hai đường.

## Bằng chứng định lượng (đo trong phiên này)

5 nhiệm vụ định-vị-code, mỗi nhiệm vụ chạy 2 nhánh (`harness/metrics/code-graph-ab.json`):

| Nhiệm vụ | Nhánh code-graph | Nhánh chỉ grep/Read |
|---|---|---|
| `flag_stale` | 5 | 2 |
| `HARD_CAP` | 5 | 3 |
| `detect_wiki_dir` | 13 | 3 |
| `cmd_roster` | 6 | 3 |
| `CONTENT_DIRS` | 8 | 3 |
| **Tổng** | **37** | **14** |

Độ chính xác **hoà 5/5 — hai nhánh ra cùng đáp án**. Khác biệt duy nhất là chi phí: nhánh được khuyên dùng đắt **2.64×**.

Đọc cho đúng: con số này **KHÔNG** nói code-graph vô dụng. Nó nói *chi phí của một tool đang hỏng mà ta bắt mọi phiên thử trước*. Giá trị thật của code-graph vẫn **chưa đo được** — phải sửa server rồi đo lại.

## Việc phải làm

- [ ] Sửa server `graph/server.py`: thống nhất DB giữa đường ghi (`reindex_repo`) và đường đọc (`search_symbols`/`get_stats`); sửa luôn `list_projects` để lấy tên project thay vì tên file DB.
- [ ] Trong lúc chưa sửa: hạ giọng dòng orientation — đừng khuyên dùng code-graph như bước ĐẦU TIÊN khi nó có thể đang hỏng; hoặc để `code_graph_keeper.py` tự thăm dò một truy vấn rẻ rồi mới quảng cáo.
- [ ] Sau khi sửa: chạy lại A/B (5 task × 2 nhánh) để cuối cùng cũng trả lời được câu hỏi gốc — code-graph có đáng bật không.

## Tiêu chí xong

`search_symbols` trả kết quả thật ngay sau `reindex_repo`, `list_projects` trả tên project thật, và bảng A/B chạy lại cho ra **giá trị thật** của code-graph thay vì chi phí của lỗi.

## Giới hạn của bằng chứng

Số tool-call là **agent tự khai**, không phải log hệ thống: `harness/metrics/events.jsonl` chỉ ghi tool GHI (`Edit`/`Write`, 1455 + 306 bản ghi), **không ghi** `Read`/`Grep`/MCP. Muốn đo đường tìm-kiếm một cách chống-gian-lận thì phải thêm telemetry phía đọc — đó là việc riêng, chưa làm.

## Bối cảnh

- Sinh từ task **T2** của [[190726-graph-lessons-grapuco]] (proposal đọc thread cộng đồng Grapuco qua lens Grower/Prototyper/Maintainer).
- Chặn luôn task **T5** của cùng proposal (nháp cross-repo impact FE/BE) — nháp đó dựa trên `list_projects` để nối hai project, nên nền hỏng thì nháp không chạy được. T5 chốt **no-go**, lý do là nền chứ không phải ý tưởng.
- Handoff này ghi qua đúng cơ chế vừa dựng ở task **T6** (ranh giới persona không còn là ngõ cụt): Grower chạm giới hạn nghề — sửa server MCP là việc hardening, không phải việc đo — nên chuyển cho **Maintainer**.

## Origin
- **Source:** phiên đo A/B task T2, proposal `wiki/sources/draft/190726-graph-lessons-grapuco.md`
- **Bằng chứng:** `harness/metrics/code-graph-ab.json`
- **Task:** `T-260719-02`
