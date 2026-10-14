#!/usr/bin/env bash
# Phát hành overstack-mcp (mode read) lên Cloudflare Workers từ TRONG ảnh overstack-mcp — service `worker-deploy` của
# docker-compose.stack.yml (hostops stack_deploy creds:[deploy-…]) hoặc chạy tay với 3 biến môi trường.
#   CLOUDFLARE_API_TOKEN   token API có quyền Workers Scripts:Edit (+ Workers Routes nếu dùng tên miền riêng)
#   CLOUDFLARE_ACCOUNT_ID  account id (dashboard → Workers & Pages → góc phải)
#   OVERSTACK_MCP_TOKEN    bearer của /mcp (≥ 16 ký tự) — đặt thành secret của Worker; vắng thì giữ secret cũ
# Thứ tự: gom assets (catalog + SKILL.md + chỉ mục) → deploy → secret → curl /healthz. Lỗi ở đâu dừng ở đó, rc ≠ 0.
set -euo pipefail
: "${CLOUDFLARE_API_TOKEN:?thiếu CLOUDFLARE_API_TOKEN (két devops-agent: deploy-cloudflare-api-token)}"
: "${CLOUDFLARE_ACCOUNT_ID:?thiếu CLOUDFLARE_ACCOUNT_ID (két devops-agent: deploy-cloudflare-account-id)}"
cd "$(dirname "$0")/.."
WRANGLER="${WRANGLER:-npx --yes wrangler@4.150.0}"
CFG=worker/wrangler.jsonc
echo "→ assets"; node scripts/build-worker-assets.mjs
echo "→ wrangler deploy"; $WRANGLER deploy -c "$CFG" 2>&1 | tee /tmp/worker-deploy.log
URL=$(grep -oE 'https://[a-z0-9.-]+\.workers\.dev' /tmp/worker-deploy.log | head -1 || true)
if [ -n "${OVERSTACK_MCP_TOKEN:-}" ]; then
  [ "${#OVERSTACK_MCP_TOKEN}" -ge 16 ] || { echo "✗ OVERSTACK_MCP_TOKEN phải ≥ 16 ký tự" >&2; exit 2; }
  echo "→ secret OVERSTACK_MCP_TOKEN"; printf '%s' "$OVERSTACK_MCP_TOKEN" | $WRANGLER secret put OVERSTACK_MCP_TOKEN -c "$CFG" >/dev/null
else
  echo "ℹ OVERSTACK_MCP_TOKEN vắng — giữ secret đang có trên Worker (lần đầu thì /mcp trả 503 cho tới khi đặt)"
fi
if [ -n "$URL" ]; then
  echo "→ kiểm $URL/healthz"; sleep 3
  curl -fsS --max-time 20 "$URL/healthz" || { echo "✗ /healthz chưa trả lời" >&2; exit 3; }; echo
  echo "✓ worker: $URL/mcp"
else
  echo "ℹ không thấy URL *.workers.dev trong log (tên miền riêng?) — kiểm bằng curl https://<host>/healthz"
fi
