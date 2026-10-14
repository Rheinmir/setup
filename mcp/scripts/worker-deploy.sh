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
  # token "Edit Cloudflare Workers" không phải lúc nào cũng đọc được /accounts → thử lần lượt /accounts, /memberships,
  # rồi zone của tên miền riêng (Zone DNS:Edit đủ để thấy zone, zone mang account.id). Không -f: cần thân lỗi để in lý do.
  echo "→ account id (suy từ token)"
  pick='let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{let d;try{d=JSON.parse(s)}catch{d={success:false,errors:[s.slice(0,200)]}}
    if(!d.success){console.error("  · "+process.argv[1]+": Cloudflare từ chối token: "+JSON.stringify(d.errors));process.exit(5)}
    const ids=[...new Set((d.result||[]).map(r=>process.argv[1]==="accounts"?r.id:r.account&&r.account.id).filter(Boolean))];
    if(ids.length===1){console.log(ids[0]);return}
    console.error("  · "+process.argv[1]+": token thấy "+ids.length+" account");process.exit(ids.length?6:5)})'
  ZONE=""; [ -n "$DOMAIN" ] && ZONE=$(printf '%s' "$DOMAIN" | awk -F. '{print (NF>=3 && length($(NF-1))<=3 && length($NF)==2) ? $(NF-2)"."$(NF-1)"."$NF : $(NF-1)"."$NF}')
  CLOUDFLARE_ACCOUNT_ID=""
  for q in "accounts?per_page=5" "memberships?per_page=5" ${ZONE:+"zones?name=$ZONE"}; do
    kind=${q%%\?*}
    id=$(curl -sS --max-time 20 -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "$CF_API/$q" | node -e "$pick" "$kind") && { CLOUDFLARE_ACCOUNT_ID=$id; echo "  account từ $kind"; break; }
    [ $? = 6 ] && { echo "✗ token thấy nhiều account — đặt CLOUDFLARE_ACCOUNT_ID" >&2; exit 4; }
  done
  [ -n "$CLOUDFLARE_ACCOUNT_ID" ] || { echo "✗ không suy được account id (token cần Account Settings:Read, hoặc Zone DNS:Edit trên zone $ZONE) — đặt CLOUDFLARE_ACCOUNT_ID" >&2; exit 4; }
  export CLOUDFLARE_ACCOUNT_ID
fi
# chẩn đoán token (KHÔNG in giá trị): id + loại (user/account token) để khớp với dashboard, rồi thử quyền Workers Scripts
echo "→ token"
for v in "user/tokens/verify" "accounts/$CLOUDFLARE_ACCOUNT_ID/tokens/verify"; do
  curl -sS --max-time 20 -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "$CF_API/$v" | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{try{const d=JSON.parse(s);
    console.log("  "+process.argv[1]+": "+(d.success?"id "+d.result.id+" · "+d.result.status+(d.result.expires_on?" · hết hạn "+d.result.expires_on:""):"✗ "+JSON.stringify(d.errors)))}catch{console.log("  "+process.argv[1]+": ✗ "+s.slice(0,120))}})' "${v%%/tokens*}" || true
done
# đúng lời gọi đầu tiên của `wrangler deploy` (check-remote-secrets-override): GET secrets của script — cần Workers Scripts:EDIT
# (Read chỉ đủ liệt kê script). 200 = có script và quyền; 404/10007 = chưa có script, quyền ổn; còn lại = thiếu Edit.
probe=$(curl -sS --max-time 20 -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "$CF_API/accounts/$CLOUDFLARE_ACCOUNT_ID/workers/scripts/overstack-mcp/secrets" || true)
verdict=$(printf '%s' "$probe" | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{try{const d=JSON.parse(s);
  console.log(d.success||(d.errors||[]).some(e=>e.code===10007)?"ok":"no")}catch{console.log("no")}})')
case "$verdict" in
  ok) echo "  Workers Scripts: ghi được";;
  *) echo "✗ token chưa GHI được Workers Scripts: ${probe:0:200}" >&2
     echo "  cần Account · Workers Scripts: Edit (không phải Read) với Account Resources = Include <account>; id token in ở trên" >&2; exit 6;;
esac
echo "→ wrangler"; WV=$($WRANGLER --version 2>&1 | tail -1) || { echo "✗ không chạy được wrangler ($WRANGLER): $WV — trong container: /tmp phải mount exec (esbuild postinstall)" >&2; exit 5; }; echo "  $WV"
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
