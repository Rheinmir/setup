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
expect(){ # expect <tên> <file> <chuỗi phải có | OK> [WARN = phải có dòng ⚠ mà rc vẫn 0]
  local out; out="$($GATE "$2" 2>&1)"; local rc=$?
  if [ "$3" = OK ]; then { [ $rc = 0 ] && ! grep -q "⚠" <<<"$out"; } && ok "$1: trang tốt qua sạch" || no "$1: trang tốt bị bắt nhầm — $(echo "$out" | sed -n 2,4p | tr '\n' ' ')"
  elif [ "${4:-}" = WARN ]; then { [ $rc = 0 ] && grep -q "⚠ $3" <<<"$out"; } && ok "$1: cảnh báo (WARN, rc 0) ($(grep -m1 "$3" <<<"$out" | sed 's/^ *//' | cut -c1-90))" || no "$1: KHÔNG cảnh báo '$3' dạng WARN rc 0 (rc=$rc) — $(echo "$out" | tail -3 | tr '\n' ' ')"
  else { [ $rc = 2 ] && grep -q "$3" <<<"$out"; } && ok "$1: bắt được ($(grep -m1 "$3" <<<"$out" | sed 's/^ *//' | cut -c1-90))" || no "$1: KHÔNG bắt được '$3' (rc=$rc) — $(echo "$out" | tail -3 | tr '\n' ' ')"; fi; }

expect good     "$(mk good '' '<div class="card"><h2>Tiêu đề</h2><p>Nội dung đủ tương phản ở cả hai chế độ.</p></div><div class="card"><p>Thẻ thứ hai cách thẻ trên 16px.</p></div>')" OK
expect contrast "$(mk contrast '.dim{color:#b8bec9}' '<div class="card"><p class="dim">Chữ xám nhạt trên nền trắng khó đọc</p></div>')" "contrast(sáng)"
expect contrast-dark "$(mk cdark '.fixed{color:#14161a}' '<div class="card"><p class="fixed">Màu chữ ghi cứng, sang tối thì trùng nền</p></div>')" "contrast(tối)"
expect tight    "$(mk tight '.card.t{margin:0}' '<div class="card t"><p>Khối một</p></div><div class="card t"><p>Khối hai dính sát khối một</p></div>')" "khối dính nhau"
expect tight-pad "$(mk pad '.np{padding:0}' '<div class="card np">Chữ chạm sát mép thẻ,<br>không có khoảng thở nào cả,<br>ba dòng liền</div>')" "padding quá hẹp"
expect stripe-before "$(mk sb '.s::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:#30b0c7;border-radius:12px 0 0 12px}' '<div class="card s"><p>Thẻ có sọc vẽ bằng ::before</p></div>')" "stripe:"
expect stripe-border "$(mk sl '.l{border-left:4px solid #0a84ff}' '<div class="card l"><p>Thẻ có border-left màu</p></div>')" "stripe:"
expect rounded-edge-color "$(mk rc '.rc{border-left-color:#2563eb}' '<div class="card rc"><p>Thẻ bo góc, viền 1px nhưng cạnh trái đổi màu</p></div>')" "rounded-edge:"
expect rounded-edge-top "$(mk rt '.rt{border-top:3px solid #e23b2d}' '<div class="card rt"><p>Thẻ bo góc có cạnh trên màu đỏ</p></div>')" "rounded-edge:"
expect rounded-edge-divider "$(mk rd '.dv{border:0;border-bottom:1px solid #9aa3b0}' '<div class="card dv"><p>Thẻ bo góc chỉ có đường kẻ xám dưới đáy</p></div>')" OK
expect rounded-edge-opposite "$(mk ro '.ro{border-left:3px solid #e23b2d;border-right:3px solid #e23b2d}' '<div class="card ro"><p>Thẻ bo góc có hai cạnh đối diện màu</p></div>')" "rounded-edge:"
expect rounded-edge-tab "$(mk rtab '.tab{border:1px solid var(--bd);border-bottom:2px solid #0a84ff;border-radius:8px 8px 0 0;padding:8px 12px;display:inline-block;background:var(--card)}' '<div class="card"><span class="tab">Tab đang chọn</span></div>')" "rounded-edge:"
expect rounded-edge-dark "$(mk rdk '[data-theme="dark"] .rk{border-left-color:#3b82f6}' '<div class="card rk"><p>Cạnh màu chỉ hiện ở chế độ tối</p></div>')" "rounded-edge:.*chỉ ở tối"
expect rounded-edge-spinner "$(mk rsp '.sp{width:40px;height:40px;border:3px solid #e5e5e5;border-top-color:#0a84ff;border-radius:50%}' '<div class="card"><div class="sp"></div><p>Đang tải</p></div>')" OK
expect overlap  "$(mk ov '.n{position:relative;height:60px}.n svg{position:absolute;left:14px;top:14px}.n span{position:absolute;left:18px;top:16px}' '<div class="card n"><svg width="20" height="20" viewBox="0 0 20 20"><circle cx="10" cy="10" r="9" fill="#0a84ff"/></svg><span>Task PLAN.md</span></div>')" "overlap:"
expect overlap-svg "$(mk ovs '' '<div class="card"><svg width="300" height="80" viewBox="0 0 300 80" role="img"><title>n</title><g><rect x="10" y="10" width="120" height="50" fill="none" stroke="#888"/><g aria-hidden="true" class="semantic-sigil" transform="translate(16 16)"><circle cx="8" cy="8" r="8" fill="#0a84ff"/></g><text x="20" y="30" font-size="13" fill="currentColor">Task PLAN.md</text></g></svg></div>')" "overlap:"
# PLAN 210926 t7 — bốn luật đo ở trình duyệt thật (fixture theo fdk/wiki/sources/210926-slop-code-checkable.md mục 3)
expect hscroll "$(mk hs '' '<div style="width:1200px;height:10px"></div>')" "horizontal-scroll:.*320px" WARN
expect hscroll-ok "$(mk hso '' '<div style="max-width:100%;width:1200px;height:10px"></div>')" OK
expect clickable-wrap "$(mk cw 'a{color:inherit}' '<nav style="width:80px"><a href="#">Bắt đầu dùng miễn phí ngay</a></nav>')" "clickable-wrap:" WARN
expect clickable-wrap-ok "$(mk cwo 'a{color:inherit}' '<nav style="width:80px"><a href="#" style="white-space:nowrap;display:inline-block;padding:4px 0">Dùng thử</a></nav><p style="width:80px">Đoạn văn có <a href="#">liên kết dài bẻ dòng trong câu</a> thì được tha</p>')" OK
expect italic-display "$(mk it '' '<p class="hero__title" style="font-size:40px;font-style:italic">Tiêu đề</p>')" "italic-display:"
expect italic-display-ok "$(mk ito '' '<p class="hero__title" style="font-size:40px;font-weight:700">Tiêu đề</p><p>Chữ thân <em>nghiêng</em> thì được</p>')" OK
expect upper-tight "$(mk ut '' '<h2 style="font-size:48px;line-height:.94;text-transform:uppercase">HAI DÒNG, KHÁC NHAU</h2>')" "uppercase-tight-leading:"
expect upper-tight-ok "$(mk uto '' '<h2 style="font-size:48px;line-height:1.05;text-transform:uppercase">HAI DÒNG, KHÁC NHAU</h2>')" OK
# PLAN 220926 t4 — nhịp chữ & khoảng cách (chuẩn fdk/wiki/sources/220926-spacing-standards.md)
L2="Đoạn văn đủ dài để chắc chắn xuống nhiều dòng khi khối chứa hẹp, dùng để đo nhịp chữ, độ dài dòng và khoảng cách giữa các dòng của nội dung thân bài trong trang."
expect line-height-body "$(mk lhb '.tl p{line-height:1.3}' "<div class=\"card tl\" style=\"max-width:320px\"><p>$L2</p></div>")" "line-height-body:"
expect line-height-body-ok "$(mk lhbo '.tl p{line-height:1.6}.one{line-height:1.1}' "<div class=\"card tl\" style=\"max-width:320px\"><p>$L2</p><p class=\"one\">Một dòng thì được</p></div>")" OK
expect measure-too-wide "$(mk mw '' "<p>$L2 $L2 $L2 $L2</p>")" "measure-too-wide:" WARN
expect measure-ok "$(mk mwo '' "<p style=\"max-width:34em\">$L2 $L2 $L2 $L2</p>")" OK
expect heading-proximity "$(mk hp '.hp h2{margin:8px 0 24px}' '<div class="card hp"><p>Đoạn trước.</p><h2>Tiêu đề</h2><p>Đoạn sau.</p></div>')" "heading-proximity:" WARN
expect heading-proximity-ok "$(mk hpo '.hp h2{margin:40px 0 12px}' '<div class="card hp"><p>Đoạn trước.</p><h2>Tiêu đề</h2><p>Đoạn sau.</p></div>')" OK
NAV='<nav><div class="grp">Nhóm</div><a href="#">Mục một</a><a href="#">Mục hai</a></nav>'
expect hierarchy-flat "$(mk hf 'a{color:inherit;display:block;padding:8px 0}' "$NAV")" "hierarchy-flat:"
expect hierarchy-flat-ok "$(mk hfo 'a{color:inherit;display:block;padding:8px 0}.grp{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.08em}' "$NAV")" OK
# ca user 22/09 (sidebar kanban cũ): nhãn nhóm khác mục ở 2–3 thuộc tính nhưng CHÌM hơn (xám nhạt, nhỏ, không đậm) → vẫn phải FAIL
expect hierarchy-flat-dim "$(mk hfd 'a{color:#111;display:block;padding:8px 0;font-size:12px}.grp{font-size:10.5px;color:#8a8f99;text-transform:uppercase;letter-spacing:.06em}' "$NAV")" "CHÌM hơn mục"
expect tap-target "$(mk tt 'a{color:inherit}' '<nav><a href="#" style="font-size:12px">Nhỏ</a></nav>')" "tap-target:" WARN
expect tap-target-ok "$(mk tto 'a{color:inherit}' '<nav><a href="#" style="display:inline-block;padding:8px 12px">Đủ lớn</a></nav><p>Câu có <a href="#">liên kết</a> nội dòng.</p><ul><li><a href="#">mục</a></li></ul>')" OK
# toggle: bỏ hẳn nút / nút bấm không đổi gì
NOTOGGLE="${BASE/<button class=\"theme-switch\" aria-label=\"Đổi giao diện\">Giao diện<\/button>/}"; NOTOGGLE="${NOTOGGLE/document.querySelector(\".theme-switch\").addEventListener/0&&document.addEventListener}"
h="${NOTOGGLE/EXTRA_CSS/}"; printf '%s' "${h/BODY/<div class=\"card\"><p>Trang không có nút đổi giao diện</p></div>}" > "$T/notoggle.html"; expect toggle-missing "$T/notoggle.html" "toggle: MISSING"
DEAD="${BASE/d.setAttribute(\"data-theme\",n);try/try}"; h="${DEAD/EXTRA_CSS/}"; printf '%s' "${h/BODY/<div class=\"card\"><p>Nút có nhưng bấm không đổi gì</p></div>}" > "$T/dead.html"; expect toggle-dead "$T/dead.html" "toggle: NO-EFFECT"
expect glass    "$(mk glass '.g{backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}[data-theme="dark"] .g{backdrop-filter:none;-webkit-backdrop-filter:none}' '<div class="card g"><p>Kính chỉ còn ở chế độ sáng</p></div>')" "glass:"

# ── PLAN 220926 (user 22/09): chữ hoa đầu · thang tiêu đề to → nhỏ · tên trang to hơn nav/tab · khoảng nghỉ cho mắt
expect sentence-case "$(mk sc 'h2,h3{margin:32px 0 8px}' '<h2>bảng dispatch</h2><p>Nội dung.</p>')" "sentence-case:"
expect sentence-case-ok "$(mk sco 'h2,h3{margin:32px 0 8px}' '<h2>Bảng dispatch</h2><p>Mở đầu.</p><h3>orca-graph · t1</h3><p>Một.</p><h3><code>scope</code> phải dính</h3><p>Hai.</p><h3 data-case="keep">herdr</h3><p>Nội dung.</p>')" OK
expect heading-scale "$(mk hs 'h2{font-size:14px;margin:32px 0 8px}h3{font-size:18px;margin:32px 0 8px}' '<h2>Mục lớn</h2><p>Nội dung ngắn.</p><h3>Mục con</h3><p>Nội dung.</p>')" "heading-scale:"
expect heading-scale-ok "$(mk hso 'h2{font-size:24px;margin:32px 0 8px}h3{font-size:18px;margin:32px 0 8px}' '<h2>Mục lớn</h2><p>Nội dung ngắn.</p><h3>Mục con</h3><p>Nội dung.</p>')" OK
expect title-scale "$(mk ts 'nav a{display:block;font-size:14px;padding:8px;color:inherit}nav .brand{font-size:14px;font-weight:700}' '<nav><div class="brand">Tên trang</div><a href="#a">Một</a><a href="#b">Hai</a></nav><p>Nội dung.</p>')" "title-scale:"
expect title-scale-ok "$(mk tso 'nav a{display:block;font-size:13px;padding:8px;color:inherit}nav .brand{font-size:18px;font-weight:700}' '<nav><div class="brand">Tên trang</div><a href="#a">Một</a><a href="#b">Hai</a></nav><p>Nội dung.</p>')" OK
DENSE=$(for i in $(seq 1 40); do printf '<div class="card" style="margin:0 0 8px;border-radius:0">Khối số %s dày đặc chữ chữ chữ chữ chữ chữ chữ chữ chữ chữ chữ chữ chữ chữ chữ chữ chữ chữ chữ chữ chữ chữ chữ</div>' "$i"; done)
expect eye-rest "$(mk er '' "$DENSE")" "eye-rest:" WARN
expect eye-rest-ok "$(mk ero 'h2,h3{margin:32px 0 8px}' '<h2>Tiêu đề</h2><p>Một đoạn ngắn, nhiều khoảng trắng quanh nó.</p>')" OK

# ── kanban-uniform (user 22/09): mọi thẻ cùng size cố định + cùng style
KB='<div class="board"><div class="lane"><h3>Cần làm</h3><div class="kc">Thẻ ngắn</div><div class="kc">Thẻ dài<br>dòng hai<br>dòng ba</div></div><div class="lane"><h3>Xong</h3><div class="kc">Một</div></div></div>'
KBC='.board{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.kc{padding:8px;margin:0 0 8px;border:1px solid #ccc;border-radius:8px}'
expect kanban-uniform "$(mk kb "$KBC" "$KB")" "kanban-uniform:"
expect kanban-uniform-style "$(mk kbs "$KBC.kc{height:80px;overflow:hidden}.lane:last-child .kc{border-radius:0}" "$KB")" "style khác nhau"
expect kanban-uniform-ok "$(mk kbo "$KBC.kc{height:80px;overflow:hidden}" "$KB")" OK

# ── line-over-text (user 22/09): vạch tiến độ absolute trong khung cuộn đè lên mục ở mép dưới
LOT='<div class="sb"><a href="#x">Mục một</a><a href="#x">Mục hai</a><div class="bar"></div></div>'
expect line-over-text "$(mk lot '.sb{position:relative;width:240px}.sb a{display:block;padding:8px;color:inherit}.bar{position:absolute;left:0;right:0;bottom:12px;height:3px;background:#0a84ff}' "$LOT")" "line-over-text:"
expect line-over-text-ok "$(mk loto '.sb{position:relative;width:240px}.sb a{display:block;padding:8px;color:inherit}.bar{position:fixed;left:0;right:0;top:0;height:3px;background:#0a84ff}' "$LOT")" OK

# ── band-misaligned (user 24/09, hàng "Giao diện" sidebar): dải nền riêng margin âm lệch cả mép nav lẫn cột mục
BM='<nav class="nv"><a href="#x">Mục một</a><a href="#x">Mục hai</a><div class="row">Giao diện</div></nav>'
BMC='.nv{display:flex;flex-direction:column;width:232px;padding:16px 12px;background:var(--card)}.nv a{padding:6px 10px;color:inherit}'
expect band-misaligned "$(mk bm "$BMC.row{margin:24px -8px 0;padding:12px 8px;border-top:1px solid var(--bd);background:#fff}" "$BM")" "band-misaligned:"
expect band-misaligned-ok "$(mk bmo "$BMC.row{margin:auto 0 0;padding:12px 10px;border-top:1px solid var(--bd);background:inherit}" "$BM")" OK

# ── toggle-jump (user 24/09): ripple đổi static→relative khi bấm, bottom/right sót lại đẩy nút lệch 16px
TJC='.theme-switch{position:static;bottom:16px;right:16px}'
TJS='<script>document.addEventListener("pointerdown",function(e){var b=e.target.closest("button");if(b){b.style.position="relative";setTimeout(function(){b.style.position=""},500)}})</script>'
expect toggle-jump "$(mk tj "$TJC" "$TJS")" "NHẢY chỗ"
expect toggle-jump-ok "$(mk tjo "$TJC" "${TJS/b.style.position=\"relative\"/b.style.position=\"relative\";b.style.inset=\"auto\"}")" OK

# ── design-showcase (PLAN 220926-design-showcase t7): trang MẪU CHUẨN phải sạch tuyệt đối — 0 FAIL, 0 WARN
expect design-showcase "$ROOT/skills/hallmark/references/design-showcase.html" OK

echo ""; echo "html-visual-gate-test: $PASS PASS · $FAIL FAIL · $SKIP SKIP"; [ "$FAIL" = 0 ]
