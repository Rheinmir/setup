#!/usr/bin/env bash
# worker-deploy-test — mcp/scripts/worker-deploy.sh (service worker-deploy, flow worker_release của devops-agent) chỉ cần MỘT cred:
#   (1) chỉ CLOUDFLARE_API_TOKEN → account id suy từ /accounts, deploy gắn --domain skills.giatbh.io.vn, kiểm healthz, rc 0
#   (2) token bị Cloudflare từ chối → dừng TRƯỚC deploy, rc 4, lý do in ra
#   (3) token thấy 2 account → đòi CLOUDFLARE_ACCOUNT_ID, rc 4; đặt rồi thì không gọi /accounts
#   (4) OVERSTACK_WORKER_DOMAIN rỗng → không --domain; (5) healthz chết → rc 3; (6) thiếu token → rc ≠ 0, chưa gọi gì
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
S="$ROOT/mcp/scripts/worker-deploy.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
PASS=0; FAIL=0; ok(){ PASS=$((PASS+1)); echo "  PASS  $*"; }; no(){ FAIL=$((FAIL+1)); echo "  FAIL  $*"; }
mkdir -p "$T/bin"
# curl giả: /accounts trả theo $ACCOUNTS (one|two|denied); /healthz trả theo $HEALTH (up|down)
cat > "$T/bin/curl" <<'C'
#!/usr/bin/env bash
url="${@: -1}"; echo "curl $url" >> "$LOG"
case "$url" in
  */accounts*) case "$ACCOUNTS" in
      one) echo '{"success":true,"result":[{"id":"acc111","name":"me"}]}';;
      two) echo '{"success":true,"result":[{"id":"a1"},{"id":"a2"}]}';;
      *)   echo '{"success":false,"errors":[{"code":9109,"message":"Cannot use the access token from location"}]}';; esac;;
  */healthz) [ "$HEALTH" = up ] && echo '{"ok":true,"mode":"read"}' || exit 22;;
  *) exit 6;;
esac
C
cat > "$T/bin/wrangler" <<'W'
#!/usr/bin/env bash
echo "wrangler $* acct=${CLOUDFLARE_ACCOUNT_ID:-}" >> "$LOG"; echo "Deployed overstack-mcp https://overstack-mcp.me.workers.dev"
W
cat > "$T/bin/sleep" <<'Z'
#!/bin/sh
exit 0
Z
chmod +x "$T/bin/"*
run(){ : > "$T/log"; env -i PATH="$T/bin:$PATH" HOME="$T" LOG="$T/log" WRANGLER="$T/bin/wrangler" BUILD_ASSETS=true "$@" bash "$S" > "$T/out" 2>&1; echo $?; }

rc=$(run CLOUDFLARE_API_TOKEN=tok ACCOUNTS=one HEALTH=up)
grep -q "wrangler deploy -c worker/wrangler.jsonc --domain skills.giatbh.io.vn acct=acc111" "$T/log" && [ "$rc" = 0 ] \
  && grep -q "curl https://skills.giatbh.io.vn/healthz" "$T/log" && ok "(1) một cred: account suy ra, --domain, healthz, rc 0" || { no "(1) rc=$rc"; cat "$T/log" "$T/out"; }
rc=$(run CLOUDFLARE_API_TOKEN=tok ACCOUNTS=denied HEALTH=up)
[ "$rc" = 4 ] && ! grep -q "^wrangler" "$T/log" && grep -q "từ chối token" "$T/out" && ok "(2) token bị từ chối → dừng trước deploy, rc 4" || { no "(2) rc=$rc"; cat "$T/out"; }
rc=$(run CLOUDFLARE_API_TOKEN=tok ACCOUNTS=two HEALTH=up)
[ "$rc" = 4 ] && grep -q "2 account" "$T/out" && ! grep -q "^wrangler" "$T/log" && ok "(3a) 2 account → đòi CLOUDFLARE_ACCOUNT_ID" || { no "(3a) rc=$rc"; cat "$T/out"; }
rc=$(run CLOUDFLARE_API_TOKEN=tok CLOUDFLARE_ACCOUNT_ID=a2 ACCOUNTS=two HEALTH=up)
[ "$rc" = 0 ] && ! grep -q "/accounts" "$T/log" && grep -q "acct=a2" "$T/log" && ok "(3b) account đặt sẵn → không gọi /accounts" || { no "(3b) rc=$rc"; cat "$T/log"; }
rc=$(run CLOUDFLARE_API_TOKEN=tok ACCOUNTS=one HEALTH=up OVERSTACK_WORKER_DOMAIN=)
[ "$rc" = 0 ] && ! grep -q -- "--domain" "$T/log" && ! grep -q "giatbh" "$T/log" && ok "(4) tên miền rỗng → chỉ workers.dev" || { no "(4) rc=$rc"; cat "$T/log"; }
rc=$(run CLOUDFLARE_API_TOKEN=tok ACCOUNTS=one HEALTH=down)
[ "$rc" = 3 ] && ok "(5) healthz chết → rc 3" || { no "(5) rc=$rc"; cat "$T/out"; }
rc=$(run ACCOUNTS=one HEALTH=up)
[ "$rc" != 0 ] && [ ! -s "$T/log" ] && ok "(6) thiếu token → dừng, chưa gọi gì" || { no "(6) rc=$rc"; cat "$T/log"; }
echo; echo "worker-deploy: $PASS PASS · $FAIL FAIL"; [ "$FAIL" = 0 ]
