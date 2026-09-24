#!/usr/bin/env bash
# button-harmony-test — cổng hài hòa nút phải BẮT bố cục lệch (bản BAD) và THA bố cục đúng (bản GOOD).
# Thiếu Playwright → SKIP (rc 0 kèm dòng SKIP), không báo đạt giả.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; TOOL="$ROOT/fdk/tools/button-harmony.mjs"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
page() { printf '<!doctype html><html><head><style>body{font:16px sans-serif;margin:0;padding:24px}.row{display:flex;gap:8px;margin-top:12px}.end{justify-content:flex-end}.card{border:1px solid #ccc;padding:16px}button{min-height:40px;padding:8px 16px}.hd{display:flex;justify-content:space-between;align-items:center}input{width:100%%}</style></head><body>%s</body></html>' "$1" > "$T/$2.html"; }
page '<section class="card"><h1>Việc</h1><div class="row end"><button>+ Mới</button></div><p>danh sách việc</p></section>' lone_bad
page '<section class="card"><div class="hd"><h1>Việc</h1><button>+ Mới</button></div><p>danh sách việc</p></section>' lone_good
page '<form class="card"><label>Tên</label><input><p>ghi chú</p><div class="row end"><button>Gửi</button></div></form>' closing_good
page '<header class="row" style="justify-content:space-between"><b>Brand</b><span style="margin-left:auto">A</span><span>B</span><p style="max-width:300px;flex-basis:100%;margin:0"></p></header>' gap_bad
page '<header class="row"><b>Brand</b><span style="flex:1"></span><button>B</button></header>' spacer_good
pass=0; fail=0
check() { # file rule want(1=must find, 0=must not)
  out="$(cd "$ROOT" && NODE_PATH="${NODE_PATH:-$(npm root -g 2>/dev/null)}" node "$TOOL" "$T/$1.html" --widths 1200 2>&1)"; rc=$?
  if [ $rc -eq 2 ]; then echo "SKIP button-harmony-test: không có Playwright"; exit 0; fi
  if grep -q "$2" <<<"$out"; then got=1; else got=0; fi
  if [ "$got" = "$3" ]; then pass=$((pass+1)); echo "  PASS $1 ${2:-sạch}"; else fail=$((fail+1)); echo "  FAIL $1 (muốn $2=$3)"; echo "$out" | sed 's/^/      /'; fi
}
check lone_bad lone-action 1
check lone_good lone-action 0
check closing_good lone-action 0
check gap_bad edge-gap 1
check gap_bad empty-occupant 1
check spacer_good 'empty-occupant\|edge-gap' 0
echo "button-harmony-test: $pass PASS · $fail FAIL"
[ $fail -eq 0 ]
