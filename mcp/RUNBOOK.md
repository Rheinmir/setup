# RUNBOOK — host overstack-mcp như một stack riêng qua devops-agent

Mục tiêu: `overstack-mcp` chạy trên host k8s2 (hoặc host nào devops-agent quản) như **một compose stack riêng**, kéo từ git và
bật bằng chính devops-agent (`stack_sync` → `stack_deploy` của sidecar hostops), không SSH tay, không rsync. Mọi lệnh ghi hạ
tầng của devops-agent **chờ người duyệt** trên web UI của nó.

## 0. Những gì cần có

| Thứ | Ở đâu | Ghi chú |
|---|---|---|
| devops-agent đang chạy | `~/orca/devops-agent`, host k8s2, URL qua Cloudflare Tunnel | `AGENT_URL`, `AGENT_AUTH_TOKEN` của người vận hành |
| Allow-list repo của hostops | `HOSTOPS_GIT_ALLOW` (mặc định `https://github.com/Rheinmir/`) | `Rheinmir/setup` public → không cần `HOSTOPS_GIT_TOKEN` |
| Thư mục stack trên host | `/home/rhein/stacks/overstack-mcp/` (`HOSTOPS_STACKS_DIR`) | `stack_fetch` tạo lần đầu — không cần staging tay |
| `.env` của stack | `/home/rhein/stacks/overstack-mcp/.env` | tuỳ chọn (token tự sinh vào volume nếu vắng); operator viết, hostops không bao giờ đọc hay in |
| Network `ai-net` | trên host (devops-agent tạo sẵn) | compose của stack khai `external: true` |

## 1. Đường ngắn: `devops-release.ts` (qua MCP của devops-agent, không cần chạm host)

```sh
cd ~/orca/setup/mcp
export DEVOPS_AGENT_URL=http://100.114.107.68:8787/mcp   # hoặc https://<tunnel-host>/mcp
export DEVOPS_AGENT_TOKEN=<AGENT_AUTH_TOKEN của người vận hành>
npm run -s devops -- release feat/overstack-mcp   # asset_upsert overstack-mcp (repo/ref) → flow stack_release (stack_fetch + stack_deploy)
npm run -s devops -- wait 900                     # poll stacks_list tới khi service healthy
npm run -s devops -- status                       # state/health/port + sha đang chạy (stack_source)
```

`hostops_stack_fetch` **tạo thư mục stack lần đầu**, nên không cần staging tay. Không có `.env` → server **tự sinh token**
lần đầu và giữ trong volume `/workspaces/.overstack-mcp-token`; `/healthz` báo `tokenSource: generated|file|env`.
Operator đọc token một lần: `docker exec overstack-mcp cat /workspaces/.overstack-mcp-token` (trên host). Muốn tự chọn token
hoặc đổi `OVERSTACK_TOOLS=all`, `OVERSTACK_MCP_BIND=<ip tailnet>`: viết `/home/rhein/stacks/overstack-mcp/.env` (mẫu
`.env.mcp.example`) rồi `stack_deploy` lại. **Không** đặt `OVERSTACK_MCP_BIND=0.0.0.0`.

Hai bước ghi của flow (`stack_fetch`, `stack_deploy`) **luôn** tạo approval chờ người, kể cả ở autonomy `all`; mỗi approval
**hết hạn sau 15 phút** không ai bấm → flow lỗi, phải `release` lại. `release` không chặn: phát flow rồi poll status + approvals
(in id đang chờ), dừng rc 1 khi approval hết hạn. Người vận hành đã đồng ý trước và không ngồi canh web UI →
`APPROVE=yes npm run -s devops -- release <ref>`: script tự duyệt approval của đúng stack này qua REST `POST /api/approvals/:id`
cùng bearer (MCP cố ý không lộ `approval_decide`). Không đặt `APPROVE=yes` mặc định trong CI hay cron.

## 2. Đường dài: qua chat / flow bằng CLI của devops-agent

Qua chat (agent gọi tool hostops, mỗi lệnh ghi chờ duyệt ở tab Approvals):

```sh
export AGENT_URL=https://<tunnel-host> AGENT_AUTH_TOKEN=<token>
cd ~/orca/devops-agent
npm run agent -- chat-create                       # → <chatId>
npm run agent -- chat-send <chatId> "stack_sync overstack-mcp từ https://github.com/Rheinmir/setup ref feat/overstack-mcp, rồi stack_deploy overstack-mcp"
npm run agent -- approvals                          # duyệt 2 lệnh ghi: stack_sync, stack_deploy
npm run agent -- approve <approvalId> yes
```

Hoặc qua flow có sẵn (0 token model) sau khi khai asset `overstack-mcp` trong inventory:

```sh
npm run agent -- asset-upsert --kind stack --name overstack-mcp --facts repo=https://github.com/Rheinmir/setup,ref=feat/overstack-mcp --tags mcp
npm run agent -- flow-run stack_deploy --params asset=overstack-mcp      # build có thể vài phút → trả job id, theo bằng flow stacks_list
```

`stack_sync` làm gì (hostops `src/hostops/stacks.ts`): `git init` lần đầu, `fetch --depth 1 origin <ref>`, `checkout -f -B deploy
FETCH_HEAD` — file untracked (`.env`) giữ nguyên; trả `sha` mới và `previous` để rollback. `stack_deploy`:
`docker compose --project-directory <dir> -f docker-compose.stack.yml -p overstack-mcp up -d --build --remove-orphans`.

## 3. Kiểm

```sh
# trên host hoặc qua devops-agent (flow stacks_list → service overstack-mcp state running, health healthy)
curl -fsS http://127.0.0.1:8791/healthz
# {"ok":true,"name":"overstack-mcp","version":"0.1.0","skills":106,"rules":22,"tools":146,"mode":"core"}

# từ máy dev, qua tunnel/tailnet:
cd ~/orca/setup/mcp
MCP_URL=https://<overstack-mcp-host>/mcp OVERSTACK_MCP_TOKEN=<token> CHECK_WORKSPACE=overstack npm run mcp:check -- remote
```

Lần đầu workspace rỗng → gọi `workspace_sync {name: "overstack", repo: "https://github.com/Rheinmir/setup", ref: "orca"}` để có một
workspace có `llmwiki/wiki` (mcp-check remote tự làm trong `stack-smoke.sh`).

## 4. Nối client

- **dsh:** `OVERSTACK_MCP_URL=https://<host>/mcp OVERSTACK_MCP_TOKEN=… pnpm dsh headless --patch <setup>/mcp/clients/dsh.overlay.yml "…"` —
  tool hiện là `mcp__overstack__*`. Bằng chứng một lượt thật: `scripts/dsh-smoke.sh` (log phiên có `tool/call mcp__overstack__skill_find`).
- **Claude Code:** `claude mcp add --transport http overstack https://<host>/mcp --header "Authorization: Bearer <token>"`
  (hoặc stdio cùng máy: `clients/claude-code.mcp.json`).
- **devops-agent / PM agent (cùng `ai-net`):** `mcp-connection-upsert --name overstack --url http://overstack-mcp:8791/mcp --tokenEnv OVERSTACK_MCP_TOKEN --readOnlyTools skills_list,skill_find,skill_get,rules_list,rule_check,tools_list,tool_help,workspace_list`
  (token để trong vault của devops-agent: `cred-set OVERSTACK_MCP_TOKEN <value>` rồi `--tokenEnv cred:OVERSTACK_MCP_TOKEN`).

## 5. Cập nhật / rollback

```sh
# cập nhật: sync ref mới rồi deploy lại (ảnh build lại, workspace volume giữ nguyên)
chat-send <chatId> "stack_sync overstack-mcp ref orca rồi stack_deploy overstack-mcp"
# rollback: sync đúng sha `previous` mà lần sync trước trả về, rồi deploy
chat-send <chatId> "stack_sync overstack-mcp ref <previous-sha> rồi stack_deploy overstack-mcp"
```

Đổi token: sửa `.env` trên host → `stack_deploy` (compose recreate container). Đổi `OVERSTACK_TOOLS=all` tương tự.

## 6. Trạng thái deploy

| Ngày | Host | Ref / sha | Kết quả |
|---|---|---|---|
| 2026-10-11 | máy dev (macOS, Docker 29.8) | nhánh `feat/overstack-mcp` | `stack-smoke.sh` build + up + `workspace_sync` + `mcp-check remote` OK; `dsh-smoke.sh` qua OpenRouter: dsh gọi `mcp__overstack__skill_find` → `md-to-html` |
| 2026-10-11 | k8s2 qua MCP devops-agent (`http://100.114.107.68:8787/mcp`) | `feat/overstack-mcp` @ `1bbd846` | `APPROVE=yes devops-release.ts release`: `hostops_stack_fetch` 7 s (tạo `/home/rhein/stacks/overstack-mcp`), `hostops_stack_deploy` job `d-mv3nw7qv` build 10:09→10:12 UTC, service `running/healthy`, cổng `127.0.0.1:8791`, không `.env` → token tự sinh trong volume (đọc bằng `docker exec overstack-mcp cat /workspaces/.overstack-mcp-token` trên host). Hai lần trước approval hết hạn 15 phút vì không ai bấm web UI. |
