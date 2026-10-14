#!/usr/bin/env bash
# worker-deploy-test — mcp/scripts/worker-deploy.sh (service worker-deploy, flow worker_release của devops-agent) chỉ cần MỘT cred:
#   (1) chỉ CLOUDFLARE_API_TOKEN → account id suy từ /accounts, deploy gắn --domain skills.giatbh.io.vn, kiểm healthz, rc 0
#   (2) token bị Cloudflare từ chối → dừng TRƯỚC deploy, rc 4, lý do in ra
#   (3) token thấy 2 account → đòi CLOUDFLARE_ACCOUNT_ID, rc 4; đặt rồi thì không gọi /accounts
#   (7)-(9) /accounts rỗng (token thật 14/10) → /memberships → zone của tên miền; không nguồn nào → rc 4 + quyền cần
#   (10) wrangler không chạy → rc 5 · (12) token thiếu Workers Scripts → rc 6, in id token (không in giá trị)
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
url="${@: -1}"; echo "curl $url" >> "$LOG"; F=0; for a in "$@"; do case "$a" in -*f*) [ "${a#--}" = "$a" ] && F=1;; esac; done
case "$url" in
  */tokens/verify) echo '{"success":true,"result":{"id":"tokid","status":"active"}}';;
  */workers/scripts/overstack-mcp/secrets) case "${SCRIPTS:-ok}" in ok) printf '{\n  "result": [],\n  "success": true\n}\n';; new) printf '{\n  "result": null,\n  "success": false,\n  "errors": [\n    {\n      "code": 10007,\n      "message": "This Worker does not exist on your account."\n    }\n  ]\n}\n';; *) echo '{"success":false,"errors":[{"code":10000,"message":"Authentication error"}]}';; esac;;
  */memberships*) [ "${MEMBERS:-}" = one ] && echo '{"success":true,"result":[{"account":{"id":"accmem"}}]}' || echo '{"success":true,"result":[]}';;
  */accounts*) case "$ACCOUNTS" in
      one) echo '{"success":true,"result":[{"id":"acc111","name":"me"}]}';;
      two) echo '{"success":true,"result":[{"id":"a1"},{"id":"a2"}]}';;
      zero) echo '{"success":true,"result":[]}';;
      *)   [ "$F" = 1 ] && exit 22; echo '{"success":false,"errors":[{"code":9109,"message":"Cannot use the access token from location"}]}';; esac;;
  */zones\?name=giatbh.io.vn) [ "${ZONES:-}" = one ] && echo '{"success":true,"result":[{"id":"z1","account":{"id":"acczone"}}]}' || echo '{"success":true,"result":[]}';;
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
[ "$rc" = 4 ] && ! grep -q "^wrangler" "$T/log" && grep -q "từ chối token.*Cannot use the access token from location" "$T/out" && ok "(2) token bị từ chối → dừng trước deploy, rc 4, in lý do của Cloudflare" || { no "(2) rc=$rc"; cat "$T/out"; }
rc=$(run CLOUDFLARE_API_TOKEN=tok ACCOUNTS=two HEALTH=up)
[ "$rc" = 4 ] && grep -q "2 account" "$T/out" && ! grep -q "^wrangler" "$T/log" && ok "(3a) 2 account → đòi CLOUDFLARE_ACCOUNT_ID" || { no "(3a) rc=$rc"; cat "$T/out"; }
rc=$(run CLOUDFLARE_API_TOKEN=tok CLOUDFLARE_ACCOUNT_ID=a2 ACCOUNTS=two HEALTH=up)
[ "$rc" = 0 ] && ! grep -q "/accounts?per_page" "$T/log" && grep -q "acct=a2" "$T/log" && ok "(3b) account đặt sẵn → không gọi /accounts" || { no "(3b) rc=$rc"; cat "$T/log"; }
rc=$(run CLOUDFLARE_API_TOKEN=tok ACCOUNTS=one HEALTH=up OVERSTACK_WORKER_DOMAIN=)
[ "$rc" = 0 ] && ! grep -q -- "--domain" "$T/log" && ! grep -q "giatbh" "$T/log" && ok "(4) tên miền rỗng → chỉ workers.dev" || { no "(4) rc=$rc"; cat "$T/log"; }
rc=$(run CLOUDFLARE_API_TOKEN=tok ACCOUNTS=one HEALTH=down)
[ "$rc" = 3 ] && ok "(5) healthz chết → rc 3" || { no "(5) rc=$rc"; cat "$T/out"; }
rc=$(run ACCOUNTS=one HEALTH=up)
[ "$rc" != 0 ] && [ ! -s "$T/log" ] && ok "(6) thiếu token → dừng, chưa gọi gì" || { no "(6) rc=$rc"; cat "$T/log"; }
rc=$(run CLOUDFLARE_API_TOKEN=tok ACCOUNTS=zero ZONES=one HEALTH=up)
[ "$rc" = 0 ] && grep -q "acct=acczone" "$T/log" && grep -q "zones?name=giatbh.io.vn" "$T/log" && ok "(7) token không đọc được account (như token thật 14/10) → account từ zone giatbh.io.vn" || { no "(7) rc=$rc"; cat "$T/log" "$T/out"; }
rc=$(run CLOUDFLARE_API_TOKEN=tok ACCOUNTS=zero MEMBERS=one HEALTH=up)
[ "$rc" = 0 ] && grep -q "acct=accmem" "$T/log" && ! grep -q "zones?" "$T/log" && ok "(8) memberships có account → dùng, không hỏi zone" || { no "(8) rc=$rc"; cat "$T/log"; }
rc=$(run CLOUDFLARE_API_TOKEN=tok ACCOUNTS=zero HEALTH=up)
[ "$rc" = 4 ] && ! grep -q "^wrangler" "$T/log" && grep -q "Zone DNS:Edit" "$T/out" && ok "(9) không nguồn nào ra account → rc 4, nói cần quyền gì" || { no "(9) rc=$rc"; cat "$T/out"; }
printf '#!/bin/sh\necho "npm error code 1" >&2; exit 1\n' > "$T/bin/wrangler-broken"; chmod +x "$T/bin/wrangler-broken"
: > "$T/log"; env -i PATH="$T/bin:$PATH" HOME="$T" LOG="$T/log" WRANGLER="$T/bin/wrangler-broken" BUILD_ASSETS=true CLOUDFLARE_API_TOKEN=tok ACCOUNTS=one HEALTH=up bash "$S" > "$T/out" 2>&1; rc=$?
[ "$rc" = 5 ] && grep -q "không chạy được wrangler" "$T/out" && ok "(10) wrangler không chạy (tmpfs noexec 14/10) → rc 5, nói lý do, không im lặng" || { no "(10) rc=$rc"; cat "$T/out"; }
grep -A2 "^  worker-deploy:" "$ROOT/docker-compose.stack.yml" >/dev/null && awk '/^  worker-deploy:/{f=1} f&&/tmpfs:/{getline; print; exit}' "$ROOT/docker-compose.stack.yml" | grep -q "/tmp:exec" && ok "(11) compose: worker-deploy mount /tmp:exec" || no "(11) worker-deploy tmpfs thiếu :exec"
rc=$(run CLOUDFLARE_API_TOKEN=tok ACCOUNTS=zero ZONES=one HEALTH=up SCRIPTS=denied)
[ "$rc" = 6 ] && ! grep -q "^wrangler deploy" "$T/log" && grep -q "id tokid" "$T/out" && grep -q "Workers Scripts: Edit (không phải Read)" "$T/out" && ok "(12) token thiếu quyền Workers (14/10) → rc 6 trước deploy, in id token + quyền cần" || { no "(12) rc=$rc"; cat "$T/out"; }
rc=$(run CLOUDFLARE_API_TOKEN=tok ACCOUNTS=one HEALTH=up SCRIPTS=new)
[ "$rc" = 0 ] && grep -q "^wrangler deploy" "$T/log" && ok "(13) script chưa tồn tại (10007, lần deploy đầu) → vẫn deploy" || { no "(13) rc=$rc"; cat "$T/out"; }
echo; echo "worker-deploy: $PASS PASS · $FAIL FAIL"; [ "$FAIL" = 0 ]
