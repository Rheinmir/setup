#!/usr/bin/env bash
# Build + chạy stack overstack-mcp cục bộ như devops-agent sẽ làm trên host, rồi gọi mcp-check vào container, rồi dọn.
#   bash mcp/scripts/stack-smoke.sh            # project name overstack-mcp-local, cổng 8791 trên 127.0.0.1
#   KEEP=1 bash mcp/scripts/stack-smoke.sh     # giữ container chạy sau khi kiểm (để dsh-smoke.sh nối vào)
set -euo pipefail
cd "$(dirname "$0")/../.."
ROOT="$(pwd)"
P="${PROJECT:-overstack-mcp-local}"
PORT="${PORT:-8791}"
ENV_FILE="$(mktemp)"
trap 'rm -f "$ENV_FILE"' EXIT
TOKEN="$(openssl rand -hex 24)"
sed "s/^OVERSTACK_MCP_TOKEN=.*/OVERSTACK_MCP_TOKEN=$TOKEN/" .env.mcp.example > "$ENV_FILE"
mkdir -p mcp && printf '%s\n' "$TOKEN" > mcp/.token.local && chmod 600 mcp/.token.local

docker network inspect ai-net >/dev/null 2>&1 || docker network create ai-net >/dev/null
# đường dẫn tuyệt đối: cleanup chạy sau khi đã `cd mcp`
COMPOSE=(docker compose --project-directory "$ROOT" -f "$ROOT/docker-compose.stack.yml" --env-file "$ENV_FILE" -p "$P")
echo "→ config"; "${COMPOSE[@]}" config -q
echo "→ build + up"; "${COMPOSE[@]}" up -d --build --remove-orphans
cleanup() { if [[ "${KEEP:-0}" != "1" ]]; then echo "→ down"; "${COMPOSE[@]}" down -v --remove-orphans >/dev/null; fi; rm -f "$ENV_FILE"; }
trap cleanup EXIT

echo "→ wait healthz"
for _ in $(seq 1 60); do curl -fsS "http://127.0.0.1:$PORT/healthz" >/dev/null 2>&1 && break; sleep 1; done
curl -fsS "http://127.0.0.1:$PORT/healthz"; echo

echo "→ seed a workspace inside the container (workspace_sync from the allow-listed repo, shallow)"
cd mcp
MCP_URL="http://127.0.0.1:$PORT/mcp" OVERSTACK_MCP_TOKEN="$TOKEN" node --import tsx -e '
  import { Client } from "@modelcontextprotocol/sdk/client/index.js";
  import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
  const c = new Client({ name: "seed", version: "0" });
  await c.connect(new StreamableHTTPClientTransport(new URL(process.env.MCP_URL), { requestInit: { headers: { authorization: `Bearer ${process.env.OVERSTACK_MCP_TOKEN}` } } }));
  const r = await c.callTool({ name: "workspace_sync", arguments: { name: "overstack", repo: "https://github.com/Rheinmir/setup", ref: process.env.SEED_REF ?? "orca" } });
  console.log(r.isError ? "✖ workspace_sync" : "✔ workspace_sync", r.content[0].text.slice(0, 300));
  if (r.isError) process.exit(1);
  await c.close();
'
echo "→ mcp-check remote (CHECK_WORKSPACE=overstack: repo framework có llmwiki/wiki)"
MCP_URL="http://127.0.0.1:$PORT/mcp" OVERSTACK_MCP_TOKEN="$TOKEN" CHECK_WORKSPACE=overstack npm run -s mcp:check -- remote
echo "stack-smoke: OK (token in mcp/.token.local${KEEP:+, container kept running on :$PORT})"
