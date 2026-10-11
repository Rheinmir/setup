# overstack-mcp — toàn bộ skill, rule, tool của overstack như MỘT MCP server

Server MCP (Model Context Protocol) đóng gói đồ nghề của overstack để **agent khác** (dsh, Claude Code, devops-agent, PM agent…)
dùng được mà không cần cài harness vào máy mình:

| Overstack có | MCP lộ ra | Cách dùng |
|---|---|---|
| 106 skill (`skills/*/SKILL.md`) | **prompt** cùng tên (`/plan`, `/md-to-html`…) + **resource** `overstack://skill/{name}` | `prompts/get plan` trả nguyên văn SKILL.md kèm task; `skill_find` xếp hạng skill cho một việc |
| 22 rule (`harness/policy.yaml`) | **resource** `overstack://rule/{id}` + tool `rule_check` | chạy validator của rule lên file trong workspace: rc 0 pass · rc 2 vi phạm |
| 146 script (`harness/scripts`, `fdk/tools`, `harness/validators`) | tool `tool_run` (+ `tool_help`, `tools_list`); `OVERSTACK_TOOLS=all` → thêm một tool mỗi script | argv cố định, không shell, cwd = workspace |
| engine orca-graph | tool `orca_graph` | `build / ask / next / lock / set / audit / add-node…` trên `.llmwiki/graph` của workspace |
| `fdk/CAPABILITIES.md`, `harness/policy.yaml` | resource `overstack://capabilities`, `overstack://policy` | đọc một phát toàn bộ năng lực |

Catalog sinh **bằng code** từ đĩa (`scripts/gen-catalog.py` → `catalog.json`): thêm skill/script vào repo → chạy lại generator;
`--check` rc 2 khi lệch (Dockerfile và test gọi nó). Không có danh sách chép tay.

## Kiến trúc

```
client MCP (dsh · Claude Code · devops-agent)
   │ stdio (src/stdio.ts, cùng máy)            │ Streamable HTTP  POST /mcp  + Authorization: Bearer <OVERSTACK_MCP_TOKEN>
   ▼                                           ▼
 buildServer()  ← catalog.json ← gen-catalog.py ← skills/ · harness/policy.yaml · harness/scripts · fdk/tools · harness/validators
   │ prompts (skill) · resources · tools
   ▼
 run.ts: spawn [python3|node|bash, OVERSTACK_ROOT/<script>, ...args]  cwd = WORKSPACES_DIR/<workspace>
         env scrub (không mang token server) · timeout · trần 256 KiB/luồng · tham số 1 dòng ≤ 2000 ký tự · path phải nằm trong workspace
 workspace.ts: workspace_sync kéo repo có prefix trong OVERSTACK_GIT_ALLOW (fetch --depth 1, checkout -f, không hook, không prompt)
```

Container (xem `../Dockerfile.mcp`, `../docker-compose.stack.yml`): node 22 + python3 + pyyaml + git + engine orca-graph clone ở
`/opt/orca-graph`; chạy user `node`, root filesystem **read-only**, `/tmp` và `HOME` trên tmpfs, `cap_drop ALL`,
`no-new-privileges`, cổng chỉ map ra `127.0.0.1` (hoặc IP tailnet qua `OVERSTACK_MCP_BIND`), network `ai-net` alias
`overstack-mcp`. Workspace là volume `/workspaces`.

## Tools

| Tool | Loại | Làm gì |
|---|---|---|
| `skills_list` | read | Danh sách skill (lọc theo group `wiki-loop` · `dev-loop` · `orchestrate` · `utils`) |
| `skill_find` | read | BM25 (k1 1.5, b 0.75 — như `build-skill-search.py`) trên tên + description + 4 KB đầu SKILL.md; trả top-k có điểm |
| `skill_get` | read | Nguyên văn SKILL.md một skill |
| `rules_list` | read | 22 rule với `checkable` (có validator chạy được hay không) |
| `rule_check` | read | Chạy validator của rule lên `files[]` (đường dẫn tương đối workspace); `pass` = rc 0 |
| `tools_list` | read | 146 script, lọc theo `kind` hoặc chuỗi trong tên/summary |
| `tool_help` | read | usage · options · positionals (parse từ `--help`) + help thô |
| `tool_run` | write (trong workspace) | Chạy một script: `{name, args[], workspace, stdin?, timeoutMs?}` → `{rc, stdout, stderr, ms, truncated, timedOut}` |
| `workspace_list` | read | Workspace dưới `WORKSPACES_DIR`: có `.git`, `.llmwiki`, `.harness` không |
| `workspace_sync` | write | Kéo `ref` của `repo` vào workspace (tạo lần đầu); chỉ repo trong `OVERSTACK_GIT_ALLOW` |
| `orca_graph` | write (trong workspace) | `orca-graph.py <args…>` — engine từ `ORCA_GRAPH_ENGINE_DIR` |
| *(all)* `<tên script>` | theo loại | `OVERSTACK_TOOLS=all`: mỗi script là một tool, input `{args, workspace, stdin?, timeoutMs?}` |

Kết quả tool trả **nguyên văn** rc/stdout/stderr: validator rc 2 nghĩa là luật bị vi phạm, không phải lỗi gọi. dsh thấy tool dưới
tên `mcp__overstack__<tool>`.

## Biến môi trường

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `OVERSTACK_MCP_TOKEN` | *(bắt buộc cho HTTP, ≥ 16 ký tự)* | Bearer cho `/mcp`; `/healthz` không cần |
| `OVERSTACK_ROOT` | cha của `mcp/` | Gốc repo overstack chứa `skills/`, `harness/`, `fdk/` |
| `WORKSPACES_DIR` | `/workspaces` | Thư mục cha của các workspace |
| `OVERSTACK_TOOLS` | `core` | `core` = 11 tool ở trên · `all` = thêm một tool mỗi script |
| `OVERSTACK_GIT_ALLOW` | `https://github.com/Rheinmir/` | Prefix repo cho `workspace_sync` (phân cách dấu phẩy) |
| `OVERSTACK_GIT_TOKEN` | — | Token read-only cho repo private (đi qua env của git, scrub khỏi log) |
| `OVERSTACK_TOOL_TIMEOUT_MS` / `OVERSTACK_TOOL_MAX_TIMEOUT_MS` | 120000 / 900000 | Trần mặc định / trần cứng một lần chạy tool |
| `ORCA_GRAPH_ENGINE_DIR` | `/opt/orca-graph/engine` (container) · `~/.orca-graph/repo/engine` (dev) | Engine cho shim `orca-graph.py`, `graph-viz.py`, `graph-atlas.py` |
| `PORT` / `BIND` | 8791 / `0.0.0.0` (trong container) | HTTP; compose map ra `OVERSTACK_MCP_BIND:8791` |

## Phát triển

```sh
cd mcp && npm install
npm run catalog          # sinh lại catalog.json (probe --help từng script, ~1 phút)
npm run catalog:check    # rc 2 khi catalog lệch đĩa
npm test                 # node:test — workspace/arg validation, chạy tool thật, server qua InMemoryTransport, HTTP 401/200
npm run typecheck
WORKSPACES_DIR=$HOME/orca npm run mcp:check -- both      # smoke client thật: stdio + HTTP (spawn server trên cổng ngẫu nhiên)
bash scripts/stack-smoke.sh                             # build ảnh + up stack cục bộ + workspace_sync + mcp-check remote + down
KEEP=1 bash scripts/stack-smoke.sh                      # giữ container trên :8791, token ở mcp/.token.local
OVERSTACK_MCP_TOKEN=$(cat .token.local) bash scripts/dsh-smoke.sh   # dsh thật gọi mcp__overstack__skill_find trong một lượt model (chạy từ repo dsh)
```

Client mẫu: `clients/dsh.overlay.yml` (dsh `--patch`), `clients/claude-code.mcp.json` (`claude mcp add`). Deploy lên host riêng
qua devops-agent: [RUNBOOK.md](RUNBOOK.md).

## Giới hạn (nói thẳng)

- Allow-list chỉ soát **đường dẫn trong argv**; một script tự mở file ngoài workspace theo logic riêng của nó thì server không
  thấy. Cô lập thật = container read-only + volume workspace (đã có) — không phải sandbox từng lần gọi.
- Script hook (đọc stdin JSON của Claude Code) chạy được qua `stdin`, nhưng ngữ cảnh phiên (`CLAUDE_*`, `.claude/`) không có.
- `--help` của 40/146 script không trả lời (hook, shim, validator đọc argv) → catalog ghi `help: null`, summary lấy từ docstring.
- Không có hàng đợi: một lần gọi `tool_run` chạy ngay; trần thời gian là `timeoutMs`, không có job nền.
