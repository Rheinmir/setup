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

## 7. Hostname công khai `skills.giatbh.io.vn` (PLAN 141026-skills-split T7 — handoff, chưa chạy từ máy dev)

Mục tiêu: `https://skills.giatbh.io.vn/healthz` trả bản harness + bản skill chuẩn; `/mcp` phục vụ **đọc** skill/rule/tool cho mọi dev
và agent (Claude Code: `claude mcp add --transport http overstack https://skills.giatbh.io.vn/mcp --header "Authorization: Bearer <token>"`).
Trạng thái 14/10/2026: hostname đã có bản ghi proxied nhưng trả 530 (tunnel tắt); máy dev không có khoá SSH tới k8s2, không có token
devops-agent, token Cloudflare dán trong chat bị khoá theo IP (`Cannot use the access token from location`) → cần người vận hành làm trên k8s2.

```sh
# (a) .env của stack — TUNNEL_TOKEN lấy từ Vault k8s2: vault kv get secret/infra/cloudflare (hoặc tạo tunnel mới ở Zero Trust → Networks → Tunnels)
cat >> /home/rhein/stacks/overstack-mcp/.env <<'EOF'
OVERSTACK_TOOLS=read
SKILLS_REF=main
TUNNEL_TOKEN=<token tunnel>
EOF
# (b) Zero Trust → Tunnels → <tunnel> → Public hostnames: skills.giatbh.io.vn → HTTP → overstack-mcp:8791  (cùng network compose)
# (c) kéo bản mới (có cloudflared profile) + dựng lại, bật profile tunnel
#     qua devops-agent: stack_sync overstack-mcp ref orca → stack_deploy overstack-mcp   (RUNBOOK §1/§2)
#     hoặc trên host:
docker compose --project-directory /home/rhein/stacks/overstack-mcp -f docker-compose.stack.yml -p overstack-mcp --profile tunnel up -d --build
# (d) kiểm
curl -fsS https://skills.giatbh.io.vn/healthz
# {"ok":true,"name":"overstack-mcp","version":"0.1.0","harness":"1.3.127","skills":{"count":106,"version":"1.0.x","catalog_sha":"…"},"rules":22,"tools":147,"mode":"read",…}
```

Sau khi lên: mỗi dev đặt `OVERSTACK_VERSION_URL=https://skills.giatbh.io.vn/healthz` (hoặc để mặc định raw GitHub) — hook đầu phiên
tự nhắc khi máy cũ hơn bản chuẩn. Token Cloudflare "toàn năng" đã lộ trong chat ngày 14/10 → xoay, cấp token giới hạn zone
`giatbh.io.vn` (DNS edit + Tunnel edit), cất vào Vault `secret/infra/cloudflare`.

## 8. Cloudflare Workers — hostname công khai không cần k8s2 (mode read, Free plan)

Thay cho §7 khi chỉ cần **đọc** (skill, rule, tool help, `/healthz` nguồn phiên bản): Worker + static assets, không tunnel, không
container, 0 đồng ở Free (100.000 request/ngày, 10 ms CPU/request). Thực thi script (`tool_run`, `orca_graph`) vẫn là §1/§2.

```sh
cd ~/orca/setup/mcp
npx wrangler whoami || npx wrangler login                 # (a) đăng nhập một lần — mở trình duyệt, không dán token vào chat
OVERSTACK_SKILLS_ROOT=~/orca/skills/skills npm run catalog   # (b) catalog theo checkout skills (skillsVersion = version.json của repo skills)
npm test && npm run typecheck                              # (c) tests/worker.test.ts: AssetsSource ≡ NodeSource, assets đủ 106 skill
npx wrangler secret put OVERSTACK_MCP_TOKEN -c worker/wrangler.jsonc   # (d) token (≥ 16 ký tự) — lần đầu, hoặc khi xoay
OVERSTACK_SKILLS_ROOT=~/orca/skills/skills npm run worker:deploy       # (e) gom assets + deploy → in URL *.workers.dev
# (f) kiểm
curl -fsS https://overstack-mcp.<account>.workers.dev/healthz        # {"ok":true,"harness":"1.3.128","skills":{"count":106,"version":"1.0.3",…},"mode":"read"}
curl -s https://overstack-mcp.<account>.workers.dev/mcp -H "authorization: Bearer <token>" -H "content-type: application/json" \
  -H "accept: application/json, text/event-stream" -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'   # 6 tool đọc
claude mcp add --transport http overstack https://overstack-mcp.<account>.workers.dev/mcp --header "Authorization: Bearer <token>"
```

- Tên miền riêng `skills.giatbh.io.vn`: gỡ bản ghi DNS trỏ tunnel (§7), rồi thêm vào `worker/wrangler.jsonc`:
  `"routes": [{ "pattern": "skills.giatbh.io.vn", "custom_domain": true }]` và deploy lại; sau đó dev đặt
  `OVERSTACK_VERSION_URL=https://skills.giatbh.io.vn/healthz`.
- Cập nhật: skill đổi (repo skills bump version) hoặc harness đổi → (b) rồi (e). Rollback: `npx wrangler rollback -c worker/wrangler.jsonc`.
- Dashboard: https://dash.cloudflare.com → Workers & Pages → `overstack-mcp` (log, metrics, secret, custom domain).
- Giới hạn: Free 10 ms CPU/request — `skill_find` BM25 trên 106 skill đo ≈ vài ms; vượt thì bật Workers Paid (5 USD/tháng, 30 s CPU).

