#!/usr/bin/env bash
# Phát hành overstack-mcp (mode read) lên Cloudflare Workers từ TRONG ảnh overstack-mcp — service `worker-deploy` của
# docker-compose.stack.yml (hostops stack_deploy creds:[deploy-…]) hoặc chạy tay.
#   CLOUDFLARE_API_TOKEN    BẮT BUỘC. Token API: mẫu "Edit Cloudflare Workers" + Zone DNS:Edit cho zone của tên miền riêng.
#   CLOUDFLARE_ACCOUNT_ID   tuỳ chọn — vắng thì suy từ token (token thấy đúng 1 account)
#   OVERSTACK_WORKER_DOMAIN tên miền riêng (mặc định skills.giatbh.io.vn; đặt rỗng để chỉ dùng *.workers.dev).
#                           Bản ghi DNS cũ của tên miền (vd CNAME tunnel) bị thay bằng Worker.
#   OVERSTACK_MCP_TOKEN     tuỳ chọn — bearer của /mcp (≥ 16 ký tự). Vắng: Worker không có secret = đọc công khai (mode read).
# Thứ tự: gom assets → deploy (+ tên miền) → secret → curl /healthz. Lỗi ở đâu dừng ở đó, rc ≠ 0.
set -euo pipefail
: "${CLOUDFLARE_API_TOKEN:?thiếu CLOUDFLARE_API_TOKEN (két devops-agent: deploy-cloudflare-api-token)}"
cd "$(dirname "$0")/.."
WRANGLER="${WRANGLER:-npx --yes wrangler@4.150.0}"
CF_API="${CF_API:-https://api.cloudflare.com/client/v4}"
CFG=worker/wrangler.jsonc
DOMAIN="${OVERSTACK_WORKER_DOMAIN-skills.giatbh.io.vn}"
if [ -z "${CLOUDFLARE_ACCOUNT_ID:-}" ]; then
  echo "→ account id (suy từ token)"
  CLOUDFLARE_ACCOUNT_ID=$(curl -fsS --max-time 20 -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "$CF_API/accounts?per_page=5" | node -e '
    let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{const d=JSON.parse(s);
      if(!d.success){console.error("✗ Cloudflare từ chối token: "+JSON.stringify(d.errors));process.exit(4)}
      if(d.result.length!==1){console.error("✗ token thấy "+d.result.length+" account — đặt CLOUDFLARE_ACCOUNT_ID");process.exit(4)}
      console.log(d.result[0].id)})') || { echo "✗ không suy được account id" >&2; exit 4; }
  export CLOUDFLARE_ACCOUNT_ID
fi
echo "→ assets"; ${BUILD_ASSETS:-node scripts/build-worker-assets.mjs}
DOM_ARGS=(); [ -n "$DOMAIN" ] && DOM_ARGS=(--domain "$DOMAIN")
echo "→ wrangler deploy ${DOMAIN:+(tên miền $DOMAIN)}"; $WRANGLER deploy -c "$CFG" ${DOM_ARGS[@]+"${DOM_ARGS[@]}"} 2>&1 | tee /tmp/worker-deploy.log
URL=$(grep -oE 'https://[a-z0-9.-]+\.workers\.dev' /tmp/worker-deploy.log | head -1 || true)
if [ -n "${OVERSTACK_MCP_TOKEN:-}" ]; then
  [ "${#OVERSTACK_MCP_TOKEN}" -ge 16 ] || { echo "✗ OVERSTACK_MCP_TOKEN phải ≥ 16 ký tự" >&2; exit 2; }
  echo "→ secret OVERSTACK_MCP_TOKEN"; printf '%s' "$OVERSTACK_MCP_TOKEN" | $WRANGLER secret put OVERSTACK_MCP_TOKEN -c "$CFG" >/dev/null
else
  echo "ℹ OVERSTACK_MCP_TOKEN vắng — Worker không có secret thì đọc công khai (mode read); có secret cũ thì giữ nguyên"
fi
ok=0
for base in ${URL:+"$URL"} ${DOMAIN:+"https://$DOMAIN"}; do
  echo "→ kiểm $base/healthz"
  for i in 1 2 3 4 5 6; do curl -fsS --max-time 20 "$base/healthz" && { echo; echo "✓ $base/mcp"; ok=1; break; }; sleep 5; done
done
[ "$ok" = 1 ] || { echo "✗ /healthz chưa trả lời ở địa chỉ nào" >&2; exit 3; }
