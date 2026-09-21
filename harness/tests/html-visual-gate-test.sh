#!/usr/bin/env bash
# html-visual-gate-test — mỗi luật của cổng chạy-thật có MỘT trang XẤU phải bị bắt, và một trang TỐT phải qua sạch.
# Vì sao: 20/09/2026 bộ đo nháp trả 0 ở hai cột trong khi user thấy lỗi bằng mắt — cổng không chứng minh được nó CẮN là cổng trang trí.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"; T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
GATE="node fdk/tools/html-visual-gate.mjs"; PASS=0; FAIL=0; SKIP=0
ok(){ PASS=$((PASS+1)); echo "  PASS  $*"; }; no(){ FAIL=$((FAIL+1)); echo "  FAIL  $*"; }
$GATE "$T/none.html" >/dev/null 2>&1; [ $? = 4 ] && { if [ -n "${CI:-}" ]; then echo "  FAIL  không có Playwright trên CI"; exit 1; fi; echo "  SKIP  không có Playwright — html-visual-gate-test: 0 PASS · 0 FAIL · 1 SKIP"; exit 0; }

BASE='<!doctype html><html data-theme="light"><head><meta charset="utf-8"><style>
:root{--bg:#f4f7fb;--ink:#14161a;--card:#ffffff;--bd:#d5dae2}[data-theme="dark"]{--bg:#0c0f16;--ink:#e8ebf0;--card:#161b26;--bd:#2a3140}
body{margin:0;padding:32px;background:var(--bg);color:var(--ink);font:16px/1.5 sans-serif}.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:16px;margin:0 0 16px;position:relative}
.theme-switch{padding:8px 12px;border:1px solid var(--bd);background:var(--card);color:var(--ink);border-radius:8px;margin:0 0 16px;display:block}EXTRA_CSS</style></head><body>
<button class="theme-switch" aria-label="Đổi giao diện">Giao diện</button>
<script>(function(){var d=document.documentElement,k="theme";try{var s=localStorage.getItem(k);if(s)d.setAttribute("data-theme",s)}catch(e){}
document.querySelector(".theme-switch").addEventListener("click",function(){var n=d.getAttribute("data-theme")==="dark"?"light":"dark";d.setAttribute("data-theme",n);try{localStorage.setItem(k,n)}catch(e){}})})()</script>
BODY</body></html>'
mk(){ local f="$T/$1.html"; local h="${BASE/EXTRA_CSS/$2}"; printf '%s' "${h/BODY/$3}" > "$f"; echo "$f"; }
expect(){ # expect <tên> <file> <chuỗi phải có | OK>
  local out; out="$($GATE "$2" 2>&1)"; local rc=$?
  if [ "$3" = OK ]; then { [ $rc = 0 ]; } && ok "$1: trang tốt qua sạch" || no "$1: trang tốt bị bắt nhầm — $(echo "$out" | sed -n 2,4p | tr '\n' ' ')"
  else { [ $rc = 2 ] && grep -q "$3" <<<"$out"; } && ok "$1: bắt được ($(grep -m1 "$3" <<<"$out" | sed 's/^ *//' | cut -c1-90))" || no "$1: KHÔNG bắt được '$3' (rc=$rc) — $(echo "$out" | tail -3 | tr '\n' ' ')"; fi; }

expect good     "$(mk good '' '<div class="card"><h2>Tiêu đề</h2><p>Nội dung đủ tương phản ở cả hai chế độ.</p></div><div class="card"><p>Thẻ thứ hai cách thẻ trên 16px.</p></div>')" OK
expect contrast "$(mk contrast '.dim{color:#b8bec9}' '<div class="card"><p class="dim">Chữ xám nhạt trên nền trắng khó đọc</p></div>')" "contrast(sáng)"
expect contrast-dark "$(mk cdark '.fixed{color:#14161a}' '<div class="card"><p class="fixed">Màu chữ ghi cứng, sang tối thì trùng nền</p></div>')" "contrast(tối)"
expect tight    "$(mk tight '.card.t{margin:0}' '<div class="card t"><p>Khối một</p></div><div class="card t"><p>Khối hai dính sát khối một</p></div>')" "khối dính nhau"
expect tight-pad "$(mk pad '.np{padding:0}' '<div class="card np">Chữ chạm sát mép thẻ,<br>không có khoảng thở nào cả,<br>ba dòng liền</div>')" "padding quá hẹp"
expect stripe-before "$(mk sb '.s::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:#30b0c7;border-radius:12px 0 0 12px}' '<div class="card s"><p>Thẻ có sọc vẽ bằng ::before</p></div>')" "stripe:"
expect stripe-border "$(mk sl '.l{border-left:4px solid #0a84ff}' '<div class="card l"><p>Thẻ có border-left màu</p></div>')" "stripe:"
expect overlap  "$(mk ov '.n{position:relative;height:60px}.n svg{position:absolute;left:14px;top:14px}.n span{position:absolute;left:18px;top:16px}' '<div class="card n"><svg width="20" height="20" viewBox="0 0 20 20"><circle cx="10" cy="10" r="9" fill="#0a84ff"/></svg><span>Task PLAN.md</span></div>')" "overlap:"
expect overlap-svg "$(mk ovs '' '<div class="card"><svg width="300" height="80" viewBox="0 0 300 80" role="img"><title>n</title><g><rect x="10" y="10" width="120" height="50" fill="none" stroke="#888"/><g aria-hidden="true" class="semantic-sigil" transform="translate(16 16)"><circle cx="8" cy="8" r="8" fill="#0a84ff"/></g><text x="20" y="30" font-size="13" fill="currentColor">Task PLAN.md</text></g></svg></div>')" "overlap:"
# toggle: bỏ hẳn nút / nút bấm không đổi gì
NOTOGGLE="${BASE/<button class=\"theme-switch\" aria-label=\"Đổi giao diện\">Giao diện<\/button>/}"; NOTOGGLE="${NOTOGGLE/document.querySelector(\".theme-switch\").addEventListener/0&&document.addEventListener}"
h="${NOTOGGLE/EXTRA_CSS/}"; printf '%s' "${h/BODY/<div class=\"card\"><p>Trang không có nút đổi giao diện</p></div>}" > "$T/notoggle.html"; expect toggle-missing "$T/notoggle.html" "toggle: MISSING"
DEAD="${BASE/d.setAttribute(\"data-theme\",n);try/try}"; h="${DEAD/EXTRA_CSS/}"; printf '%s' "${h/BODY/<div class=\"card\"><p>Nút có nhưng bấm không đổi gì</p></div>}" > "$T/dead.html"; expect toggle-dead "$T/dead.html" "toggle: NO-EFFECT"
expect glass    "$(mk glass '.g{backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}[data-theme="dark"] .g{backdrop-filter:none;-webkit-backdrop-filter:none}' '<div class="card g"><p>Kính chỉ còn ở chế độ sáng</p></div>')" "glass:"

echo ""; echo "html-visual-gate-test: $PASS PASS · $FAIL FAIL · $SKIP SKIP"; [ "$FAIL" = 0 ]
