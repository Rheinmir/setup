"""showcase_components — khối THÀNH PHẦN của design-showcase (PLAN 220926-design-showcase t4): thẻ, list, kanban, nút đủ 8
trạng thái, tab, disclosure, dialog, bảng, form, công tắc sáng/tối, chấm trạng thái. Quy ước khối: xem build-design-showcase.py.

Màu chỉ lấy từ token lớp nền (--ovs-*), có giá trị riêng cho sáng/tối nên đạt tương phản ở cả hai chế độ.

proof: harness/tests/test_design_showcase.py
"""

GROUP = "Thành phần"

# 9 task thật của PLAN 220926-design-showcase (số tệp đếm từ dòng **Files:**) — không bịa số
_ROWS = [('t1', 'Kiểm kê luật thiết kế', 'research', 'Xong', 1), ('t2', 'Builder và index', 'build', 'Xong', 1), ('t3', 'Khối bố cục', 'design', 'Xong', 1), ('t4', 'Khối thành phần', 'design', 'Xong', 1), ('t5', 'Khối motion và trạng thái', 'design', 'Xong', 1), ('t6', 'Khối biểu đồ và sơ đồ', 'design', 'Xong', 1), ('t7', 'Cổng tự gác', 'test', 'Xong', 2), ('t8', 'Nối vào luật và downstream', 'docs', 'Xong', 8), ('t9', 'Duyệt bằng mắt', 'review', 'Chờ duyệt', 1)]

_KCARDS = {
    "Cần làm": [("t4", "Viết khối thành phần", "build", "Chưa ai nhận"),
                ("t5", "Khối motion và hướng dẫn sử dụng từng bước cho người mới", "design", "Chưa ai nhận")],
    "Đang làm": [("t2", "Builder và index", "build", "claude")],
    "Xong": [("t1", "Kiểm kê luật", "research", "claude")],
}


def _kanban_html() -> str:
    lanes = []
    for lane, cards in _KCARDS.items():
        cs = "".join(
            f'<div class="card" tabindex="0" role="button" aria-haspopup="dialog" data-full="{title}">'
            f'<div class="top"><span class="id">{cid}</span><span class="kind">{kind}</span></div>'
            f'<div class="title">{title}</div><div class="who">{who}</div></div>' for cid, title, kind, who in cards)
        lanes.append(f'<div class="lane"><div class="head">{lane}<span class="n">{len(cards)}</span></div>{cs}</div>')
    return (f'<div class="sc-kanban"><div class="board">{"".join(lanes)}</div>'
            '<dialog class="detail" aria-label="Chi tiết thẻ"><div class="body"></div>'
            '<form method="dialog"><button class="close">Đóng</button></form></dialog></div>')


BLOCKS = [
    dict(
        id="card", title="Thẻ", rules=["side-stripe", "rounded-edge", "stripe", "tight", "glass"],
        note="Một style cho cả trang: nền mặt, viền 1px đều bốn cạnh, bo 14px, padding 16–24px. Phân loại bằng chấm màu hoặc nền nhạt CẢ thẻ, không bao giờ bằng sọc một cạnh.",
        html=('<div class="sc-card"><article class="c"><div class="k"><i class="dot ok"></i>Đang chạy</div><div class="t">Bản dựng đêm qua</div>'
              '<p>Mười hai bước, không lỗi. Bấm để xem nhật ký.</p></article>'
              '<article class="c warn"><div class="k"><i class="dot warn"></i>Cần xem</div><div class="t">Hai cảnh báo độ tương phản</div>'
              '<p>Nền nhạt cả thẻ báo trạng thái; viền vẫn đều bốn cạnh.</p></article></div>'),
        css=(".sc-card{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(240px,100%),1fr));gap:16px}"
             ".sc-card .c{padding:20px;border:1px solid var(--ovs-border);border-radius:14px;background:var(--ovs-surface2)}"
             ".sc-card .c.warn{background:var(--ovs-warn-bg)}"
             ".sc-card .k{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--ovs-ink2)}"
             ".sc-card .dot{width:8px;height:8px;border-radius:50%}.sc-card .dot.ok{background:var(--ovs-ok)}.sc-card .dot.warn{background:var(--ovs-warn)}"
             ".sc-card .t{font-family:var(--font-display);font-size:17px;font-weight:var(--fw-heading,600);margin:8px 0 4px}.sc-card p{margin:0;font-size:14px;color:var(--ovs-ink2)}")),
    dict(
        id="list", title="List mặc định", rules=["line-height-body", "tap-target", "minimal-disclosure"],
        note="Mỗi dòng: chấm hoặc icon · nhãn · một dòng phụ nhạt; dòng cách nhau bằng đường kẻ mảnh, cao ≥ 48px; quá 7 dòng thì gập phần còn lại.",
        html=('<ul class="sc-list">'
              + "".join(f'<li><i class="dot" style="background:var(--ovs-{c})"></i><div><div class="l">{t}</div><div class="s">{s}</div></div>'
                        f'<span class="m">{m}</span></li>'
                        for c, t, s, m in [("ok", "Cài đặt harness", "Chạy một lệnh curl", "2 phút"),
                                           ("accent", "Viết PLAN đầu tiên", "Dùng /propose rồi /plan", "10 phút"),
                                           ("warn", "Dựng graph phụ thuộc", "orca-graph build", "1 phút")])
              + '</ul>'),
        css=(".sc-list{list-style:none;margin:0;padding:0}"
             ".sc-list li{display:flex;align-items:center;gap:12px;min-height:48px;padding:8px 0;border-bottom:1px solid var(--ovs-border)}"
             ".sc-list li:last-child{border-bottom:0}.sc-list .dot{width:8px;height:8px;border-radius:50%;flex:none}"
             ".sc-list li>div{flex:1;min-width:0}.sc-list .l{font-weight:600}.sc-list .s{font-size:13px;color:var(--ovs-ink2)}"
             ".sc-list .m{font-size:13px;color:var(--ovs-ink2);white-space:nowrap}")),
    dict(
        id="kanban", title="Kanban", rules=["kanban-uniform", "minimal-disclosure", "clickable-wrap", "tap-target"],
        note="Mọi thẻ MỘT style và MỘT kích thước (cao cố định 112px, tiêu đề cắt 2 dòng); bấm thẻ hoặc Enter mở chi tiết; kéo thả giữa các cột bằng chuột hoặc cảm ứng (kéo quá 6px mới tính là kéo), bàn phím Alt + ←/→ chuyển cột, Alt + ↑/↓ đổi thứ tự; số đếm cột tự cập nhật.",
        html=_kanban_html(),
        css=(".sc-kanban .board{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;container-type:inline-size}"
             ".sc-kanban .lane{padding:12px;border:1px solid var(--ovs-border);border-radius:14px;background:var(--ovs-surface2);min-width:0;min-height:176px;transition:background-color .15s ease-out,border-color .15s ease-out}"
             ".sc-kanban .lane.over{border-color:var(--ovs-accent);background:var(--ovs-accent-bg)}"
             ".sc-kanban .head{display:flex;justify-content:space-between;align-items:center;font-weight:600;margin:0 0 12px}"
             ".sc-kanban .n{font-size:12px;padding:0 8px;border-radius:999px;background:var(--ovs-accent-bg)}"
             ".sc-kanban .card{display:flex;flex-direction:column;height:112px;box-sizing:border-box;overflow:hidden;margin:0 0 8px;padding:12px;"
             "border:1px solid var(--ovs-border);border-radius:12px;background:var(--ovs-surface);cursor:grab;touch-action:none;user-select:none}"
             ".sc-kanban .card.dragging{position:relative;z-index:5;cursor:grabbing;pointer-events:none;box-shadow:0 12px 32px rgba(0,0,0,.18)}"
             ".sc-kanban .card:hover,.sc-kanban .card:focus-visible{border-color:var(--ovs-accent);outline:none}"
             ".sc-kanban .top{display:flex;gap:8px;font-size:12px;white-space:nowrap;overflow:hidden}.sc-kanban .id{font-weight:600}"
             ".sc-kanban .kind{color:var(--ovs-ink2)}"
             ".sc-kanban .title{margin:4px 0;font-size:14px;line-height:1.45;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}"
             ".sc-kanban .who{margin-top:auto;font-size:12px;color:var(--ovs-ink2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
             ".sc-kanban .detail{max-width:min(480px,calc(100% - 32px));padding:24px;border:1px solid var(--ovs-border);border-radius:14px;background:var(--ovs-bg);color:var(--ovs-ink)}"
             ".sc-kanban .detail::backdrop{background:rgba(0,0,0,.35)}.sc-kanban .detail .title{display:block;font-size:17px}"
             ".sc-kanban .close{margin-top:16px;min-height:36px;padding:0 16px;border:1px solid var(--ovs-border);border-radius:999px;background:none;color:inherit;font:inherit;cursor:pointer}"
             "@container (max-width:600px){.sc-kanban .board{grid-template-columns:minmax(0,1fr)}}"),
        js=("const d=root.querySelector('.detail'),b=d.querySelector('.body'),lanes=[...root.querySelectorAll('.lane')];"
            "const open=c=>{b.innerHTML=c.innerHTML;b.querySelector('.title').textContent=c.dataset.full;d.showModal()};"
            "const count=()=>lanes.forEach(l=>{l.querySelector('.n').textContent=l.querySelectorAll('.card').length});"
            # kéo thả bằng pointer events (chuột + cảm ứng); nhả tay: rơi vào cột dưới con trỏ, TRƯỚC thẻ đầu tiên có tâm thấp hơn con trỏ
            "let g=null;root.addEventListener('pointerdown',e=>{const c=e.target.closest('.card');if(!c||e.button)return;"
            "g={c,x:e.clientX,y:e.clientY,on:false};c.setPointerCapture(e.pointerId)});"
            "const laneAt=(x,y)=>{const el=document.elementFromPoint(x,y);return el&&el.closest('.sc-kanban .lane')};"
            "root.addEventListener('pointermove',e=>{if(!g)return;const dx=e.clientX-g.x,dy=e.clientY-g.y;if(!g.on&&Math.hypot(dx,dy)<6)return;"
            "g.on=true;g.c.classList.add('dragging');g.c.style.transform='translate('+dx+'px,'+dy+'px)';"
            "const l=laneAt(e.clientX,e.clientY);lanes.forEach(x=>x.classList.toggle('over',x===l))});"
            "root.addEventListener('pointerup',e=>{if(!g)return;const c=g.c;"
            "if(g.on){const l=laneAt(e.clientX,e.clientY);c.classList.remove('dragging');c.style.transform='';lanes.forEach(x=>x.classList.remove('over'));"
            "if(l){const nx=[...l.querySelectorAll('.card')].find(k=>k!==c&&k.getBoundingClientRect().top+k.offsetHeight/2>e.clientY);l.insertBefore(c,nx||null);count()}}"
            "else open(c);g=null});"
            "root.addEventListener('pointercancel',()=>{if(g){g.c.classList.remove('dragging');g.c.style.transform='';lanes.forEach(x=>x.classList.remove('over'));g=null}});"
            # bàn phím: Enter/Space mở; Alt+←/→ chuyển cột; Alt+↑/↓ đổi thứ tự — focus giữ trên thẻ
            "root.addEventListener('keydown',e=>{const c=e.target.closest('.card');if(!c)return;"
            "if(e.key==='Enter'||e.key===' '){e.preventDefault();open(c);return}if(!e.altKey)return;"
            "const l=c.closest('.lane'),i=lanes.indexOf(l);"
            "if(e.key==='ArrowRight'&&i<lanes.length-1)lanes[i+1].appendChild(c);else if(e.key==='ArrowLeft'&&i>0)lanes[i-1].appendChild(c);"
            "else if(e.key==='ArrowUp'&&c.previousElementSibling&&c.previousElementSibling.classList.contains('card'))l.insertBefore(c,c.previousElementSibling);"
            "else if(e.key==='ArrowDown'&&c.nextElementSibling)l.insertBefore(c.nextElementSibling,c);else return;"
            "e.preventDefault();count();c.focus()});")),
    dict(
        id="button", title="Nút đủ 8 trạng thái", rules=["eight-states", "tap-target", "transition-all", "contrast"],
        note="Mặc định · hover · focus-visible (viền focus 2px lệch 2px) · active · disabled · loading · lỗi · thành công. Cao ≥ 36px, bo viên, chỉ chuyển màu nền và màu chữ, không transition: all.",
        html=('<div class="sc-button">'
              '<button class="b" type="button">Mặc định</button><button class="b is-hover" type="button">Hover</button>'
              '<button class="b is-focus" type="button">Focus</button><button class="b is-active" type="button">Đang nhấn</button>'
              '<button class="b" type="button" disabled>Tắt</button><button class="b" type="button" aria-busy="true"><i class="spin"></i>Đang tải</button>'
              '<button class="b err" type="button">Thử lại</button><button class="b ok" type="button">Đã lưu</button>'
              '<button class="b ghost" type="button">Nút phụ</button></div>'),
        css=(".sc-button{display:flex;flex-wrap:wrap;gap:12px}"
             ".sc-button .b{display:inline-flex;align-items:center;gap:8px;min-height:36px;padding:0 16px;border:1px solid transparent;border-radius:999px;"
             "background:var(--ovs-ink);color:var(--ovs-bg);font:inherit;font-weight:600;cursor:pointer;transition:background-color .18s ease-out,color .18s ease-out}"
             ".sc-button .b:hover,.sc-button .b.is-hover{background:var(--ovs-ink2)}"
             ".sc-button .b:focus-visible,.sc-button .b.is-focus{outline:2px solid var(--ovs-accent);outline-offset:2px}"
             ".sc-button .b:active,.sc-button .b.is-active{transform:translateY(1px)}"
             ".sc-button .b:disabled{background:var(--ovs-surface2);color:var(--ovs-ink2);border-color:var(--ovs-border);cursor:not-allowed}"
             ".sc-button .b[aria-busy=true]{cursor:progress}"
             ".sc-button .spin{width:12px;height:12px;border:2px solid currentColor;border-right-color:transparent;border-radius:50%;animation:sc-spin .8s linear infinite}"
             "@keyframes sc-spin{to{transform:rotate(360deg)}}"
             ".sc-button .b.err{background:var(--ovs-bad-bg);color:var(--ovs-bad);border-color:var(--ovs-bad)}"
             ".sc-button .b.ok{background:var(--ovs-ok-bg);color:var(--ovs-ok);border-color:var(--ovs-ok)}"
             ".sc-button .b.ghost{background:transparent;color:var(--ovs-ink);border-color:var(--ovs-border)}"
             "@media (prefers-reduced-motion:reduce){.sc-button .spin{animation:none}}")),
    dict(
        id="tabs", title="Tab", rules=["sentence-case", "title-scale", "tap-target", "side-stripe"],
        note="Tab đang chọn = nền viên, không gạch chân một cạnh; chữ tab ≤ 14px để tên trang luôn lớn hơn; điều khiển bằng phím mũi tên.",
        html=('<div class="sc-tabs"><div class="list" role="tablist" aria-label="Ví dụ tab">'
              '<button role="tab" aria-selected="true" aria-controls="sc-tp1" id="sc-t1">Tổng quan</button>'
              '<button role="tab" aria-selected="false" aria-controls="sc-tp2" id="sc-t2" tabindex="-1">Cài đặt</button>'
              '<button role="tab" aria-selected="false" aria-controls="sc-tp3" id="sc-t3" tabindex="-1">Luật</button></div>'
              '<div role="tabpanel" id="sc-tp1" aria-labelledby="sc-t1"><p>Nội dung tab tổng quan.</p></div>'
              '<div role="tabpanel" id="sc-tp2" aria-labelledby="sc-t2" hidden><p>Nội dung tab cài đặt.</p></div>'
              '<div role="tabpanel" id="sc-tp3" aria-labelledby="sc-t3" hidden><p>Nội dung tab luật.</p></div></div>'),
        css=(".sc-tabs .list{display:inline-flex;max-width:100%;overflow-x:auto;gap:4px;padding:4px;border:1px solid var(--ovs-border);border-radius:999px;background:var(--ovs-surface2)}"
             ".sc-tabs [role=tab]{min-height:32px;padding:0 16px;border:0;border-radius:999px;background:none;color:var(--ovs-ink);font:inherit;font-size:14px;cursor:pointer;white-space:nowrap}"
             ".sc-tabs [role=tab][aria-selected=true]{background:var(--ovs-ink);color:var(--ovs-bg);font-weight:600}"
             ".sc-tabs [role=tabpanel] p{margin:16px 0 0}"),
        js=("const tabs=[...root.querySelectorAll('[role=tab]')];const pick=t=>{tabs.forEach(x=>{const on=x===t;x.setAttribute('aria-selected',on);"
            "x.tabIndex=on?0:-1;root.querySelector('#'+x.getAttribute('aria-controls')).hidden=!on});t.focus()};"
            "tabs.forEach((t,i)=>{t.addEventListener('click',()=>pick(t));t.addEventListener('keydown',e=>{"
            "if(e.key==='ArrowRight')pick(tabs[(i+1)%tabs.length]);if(e.key==='ArrowLeft')pick(tabs[(i-1+tabs.length)%tabs.length])})});")),
    dict(
        id="disclosure", title="Gập mở chi tiết", rules=["minimal-disclosure", "eye-rest"],
        note="Màn đầu chỉ tóm tắt; chi tiết nằm sau <details>. Dùng phần tử gốc của trình duyệt: có sẵn bàn phím và trình đọc màn hình.",
        html=('<div class="sc-disclosure"><details><summary>Vì sao thẻ kanban cố định kích thước?</summary>'
              '<p>Bảng đọc theo hàng và cột. Thẻ cao thấp khác nhau làm mắt mất nhịp; chi tiết dài đưa vào cửa sổ chi tiết khi bấm.</p></details>'
              '<details><summary>Khi nào được phá luật?</summary><p>Khi user nói rõ, hoặc trang khai miễn trừ kèm lý do bằng thẻ meta.</p></details></div>'),
        css=(".sc-disclosure details{border-bottom:1px solid var(--ovs-border);padding:12px 0}"
             ".sc-disclosure summary{cursor:pointer;font-weight:600;min-height:24px}.sc-disclosure p{margin:8px 0 0;color:var(--ovs-ink2)}")),
    dict(
        id="dialog", title="Cửa sổ chi tiết", rules=["minimal-disclosure", "contrast"],
        note="Phần tử <dialog> gốc với showModal(): khoá nền, Esc đóng, focus trả về nút mở. Nền dialog ĐẶC (không trong suốt) để chữ phía sau không lộ qua.",
        html=('<div class="sc-dialog"><button class="open" type="button">Mở chi tiết</button>'
              '<dialog aria-label="Ví dụ cửa sổ"><div class="t">Tiêu đề cửa sổ</div><p>Nội dung đầy đủ nằm ở đây, trang chính giữ gọn.</p>'
              '<form method="dialog"><button class="close">Đóng</button></form></dialog></div>'),
        css=(".sc-dialog .open,.sc-dialog .close{min-height:36px;padding:0 16px;border:1px solid var(--ovs-border);border-radius:999px;background:var(--ovs-surface2);color:var(--ovs-ink);font:inherit;cursor:pointer}"
             ".sc-dialog dialog{max-width:min(480px,calc(100% - 32px));padding:24px;border:1px solid var(--ovs-border);border-radius:14px;background:var(--ovs-bg);color:var(--ovs-ink)}"
             ".sc-dialog dialog::backdrop{background:rgba(0,0,0,.35)}.sc-dialog .t{font-size:17px;font-weight:800}"),
        js="const d=root.querySelector('dialog');root.querySelector('.open').addEventListener('click',()=>d.showModal());"),
    dict(
        id="table", title="Bảng", rules=["line-height-body", "sentence-case", "horizontal-scroll", "eight-states"],
        note="Ô lọc không phân biệt dấu (gõ \"kiem\" khớp \"Kiểm\"); bấm tiêu đề cột để sắp xếp tăng/giảm theo thứ tự tiếng Việt (cột số so theo số), có mũi tên + aria-sort; kéo mép phải tiêu đề để giãn cột (focus vào tay nắm rồi ← → cũng được); bảng rộng thì cuộn TRONG khung. Không khớp dòng nào thì nói rõ.",
        html=('<div class="sc-table"><label class="f"><span>Lọc</span><input type="search" placeholder="Gõ tên việc, loại hoặc trạng thái"></label>'
              '<div class="wrap"><table><thead><tr>'
              + "".join(f'<th aria-sort="none"{c}><button class="sort" type="button">{t}</button>'
                        f'<span class="rz" role="separator" tabindex="0" aria-orientation="vertical" aria-label="Đổi độ rộng cột {t}"></span></th>'
                        for t, c in [("Mã", ""), ("Việc", ""), ("Loại", ""), ("Trạng thái", ""), ("Số tệp", ' class="num"')])
              + '</tr></thead><tbody>'
              + "".join(f'<tr><td>{i}</td><td>{t}</td><td>{k}</td><td>{st}</td><td class="num" data-v="{n}">{n}</td></tr>' for i, t, k, st, n in _ROWS)
              + '<tr class="empty" hidden><td colspan="5">Không có dòng nào khớp. Thử bỏ bớt chữ trong ô lọc.</td></tr></tbody></table></div></div>'),
        css=(".sc-table .f{display:flex;align-items:center;gap:12px;margin:0 0 12px;font-size:14px;font-weight:600}"
             ".sc-table .f input{flex:1;max-width:320px;min-height:36px;padding:0 12px;border:1px solid var(--ovs-border);border-radius:10px;background:var(--ovs-surface2);color:var(--ovs-ink);font:inherit;font-weight:400}"
             ".sc-table .f input:focus-visible{outline:2px solid var(--ovs-accent);outline-offset:1px}"
             ".sc-table .wrap{overflow-x:auto;border:1px solid var(--ovs-border);border-radius:12px}"
             ".sc-table table{width:max-content;min-width:100%;border-collapse:collapse;font-size:14px}"
             ".sc-table th{position:relative;text-align:left;padding:0;border-bottom:1px solid var(--ovs-border);background:var(--ovs-surface2)}"
             ".sc-table .sort{display:flex;align-items:center;gap:4px;width:100%;min-height:40px;padding:0 12px;border:0;background:none;color:var(--ovs-ink2);font:inherit;font-weight:600;text-align:left;cursor:pointer;white-space:nowrap}"
             ".sc-table .sort:hover{color:var(--ovs-ink)}.sc-table .sort:focus-visible{outline:2px solid var(--ovs-accent);outline-offset:-2px}"
             ".sc-table th[aria-sort=ascending] .sort::after{content:'↑'}.sc-table th[aria-sort=descending] .sort::after{content:'↓'}"
             ".sc-table th[aria-sort=ascending] .sort,.sc-table th[aria-sort=descending] .sort{color:var(--ovs-ink)}"
             ".sc-table .num,.sc-table .num .sort{text-align:right;justify-content:flex-end;font-variant-numeric:tabular-nums}"
             ".sc-table .rz{position:absolute;top:0;right:-4px;bottom:0;width:8px;z-index:1;cursor:col-resize;touch-action:none}"
             ".sc-table .rz:hover,.sc-table .rz:focus-visible{background:var(--ovs-accent-bg);outline:none}"
             ".sc-table td{padding:12px;border-bottom:1px solid var(--ovs-border);line-height:1.5}"
             ".sc-table tbody tr:last-child td{border-bottom:0}.sc-table .empty td{color:var(--ovs-ink2);text-align:center}"),
        js=("const tb=root.querySelector('tbody'),empty=tb.querySelector('.empty'),rows=[...tb.rows].filter(r=>r!==empty),"
            "q=root.querySelector('input'),ths=[...root.querySelectorAll('th')],col=new Intl.Collator('vi',{numeric:true,sensitivity:'base'});"
            "const norm=s=>s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/đ/gi,'d').toLowerCase();"
            "q.addEventListener('input',()=>{const k=norm(q.value.trim());let n=0;rows.forEach(r=>{const ok=!k||norm(r.textContent).includes(k);r.hidden=!ok;n+=ok});empty.hidden=n>0});"
            "ths.forEach((th,i)=>{th.querySelector('.sort').addEventListener('click',()=>{const asc=th.getAttribute('aria-sort')!=='ascending';"
            "ths.forEach(x=>x.setAttribute('aria-sort','none'));th.setAttribute('aria-sort',asc?'ascending':'descending');"
            "const v=r=>{const c=r.cells[i];return c.dataset.v!==undefined?Number(c.dataset.v):c.textContent.trim()};"
            "rows.sort((a,b)=>{const x=v(a),y=v(b);return (typeof x==='number'?x-y:col.compare(x,y))*(asc?1:-1)}).forEach(r=>tb.insertBefore(r,empty))});"
            "const rz=th.querySelector('.rz'),set=w=>{th.style.minWidth=Math.max(64,w)+'px'};"
            "rz.addEventListener('pointerdown',e=>{e.preventDefault();const x0=e.clientX,w0=th.offsetWidth;rz.setPointerCapture(e.pointerId);"
            "const mv=ev=>set(w0+ev.clientX-x0),up=()=>{rz.removeEventListener('pointermove',mv);rz.removeEventListener('pointerup',up)};"
            "rz.addEventListener('pointermove',mv);rz.addEventListener('pointerup',up)});"
            "rz.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();set(th.offsetWidth+(e.key==='ArrowRight'?16:-16))}})});")),
    dict(
        id="form", title="Form", rules=["eight-states", "contrast", "tap-target"],
        note="Nhãn luôn hiện phía trên ô (không dùng placeholder thay nhãn); ô cao 40px; lỗi = viền đỏ + dòng giải thích dưới ô, không chỉ đổi màu.",
        html=('<form class="sc-form" onsubmit="return false"><label>Tên dự án<input value="overstack"></label>'
              '<label>Email<input type="email" value="sai-dinh-dang" aria-invalid="true" aria-describedby="sc-err"></label>'
              '<p class="err" id="sc-err">Email thiếu ký tự @.</p>'
              '<label>Khoá API<input value="Không đổi được" disabled></label></form>'),
        css=(".sc-form{display:grid;gap:12px;max-width:360px}.sc-form label{display:grid;gap:4px;font-size:14px;font-weight:600}"
             ".sc-form input{min-height:40px;padding:0 12px;border:1px solid var(--ovs-border);border-radius:10px;background:var(--ovs-surface2);color:var(--ovs-ink);font:inherit;font-weight:400}"
             ".sc-form input:focus-visible{outline:2px solid var(--ovs-accent);outline-offset:1px}"
             ".sc-form input[aria-invalid=true]{border-color:var(--ovs-bad)}"
             ".sc-form input:disabled{color:var(--ovs-ink2);cursor:not-allowed}"
             ".sc-form .err{margin:-8px 0 0;font-size:13px;color:var(--ovs-bad)}")),
    dict(
        id="mode-switch", title="Công tắc sáng tối", rules=["toggle", "no-theme-toggle", "no-dark-mode"],
        note="Mọi trang có công tắc; lựa chọn nhớ trong localStorage (khoá ovs-theme) và áp TRƯỚC khi vẽ để không nháy. Lớp nền html_base tự chèn — mẫu này cho trang tự dựng.",
        html='<div class="sc-mode-switch"><button class="sw" type="button" aria-pressed="false"><span class="knob"></span><span class="lb">Chế độ tối</span></button></div>',
        css=(".sc-mode-switch .sw{display:inline-flex;align-items:center;gap:12px;min-height:36px;padding:4px 16px 4px 4px;border:1px solid var(--ovs-border);border-radius:999px;background:var(--ovs-surface2);color:var(--ovs-ink);font:inherit;cursor:pointer}"
             ".sc-mode-switch .knob{width:28px;height:28px;border-radius:50%;background:var(--ovs-ink);transition:transform .2s ease-out}"
             ".sc-mode-switch .sw[aria-pressed=true] .knob{transform:translateX(4px)}"),
        js=("const b=root.querySelector('.sw'),h=document.documentElement;const sync=()=>b.setAttribute('aria-pressed',h.dataset.theme==='dark');sync();"
            "b.addEventListener('click',()=>{const n=h.dataset.theme==='dark'?'light':'dark';h.setAttribute('data-theme',n);"
            "try{localStorage.setItem('ovs-theme',n)}catch(e){}sync()});")),
    dict(
        id="status-dot", title="Chấm trạng thái", rules=["side-stripe", "contrast"],
        note="Một bộ trạng thái = MỘT dạng, MỘT cỡ chữ cho mọi mục. Dạng chấm: chấm 8px + chữ (màu không đứng một mình). Dạng viên (khi cần nổi hơn): nền màu đặc, chữ màu CỐ ĐỊNH đạt tương phản, không dùng token đổi theo chế độ.",
        html=('<div class="sc-status-dot"><div class="row"><span class="k">Dạng chấm</span>'
              + "".join(f'<span class="s"><i style="background:var(--ovs-{c})"></i>{t}</span>'
                        for c, t in [("ok", "Xong"), ("accent", "Đang chạy"), ("warn", "Chờ duyệt"), ("bad", "Hỏng"), ("ink2", "Không rõ")])
              + '</div><div class="row"><span class="k">Dạng viên</span>'
              + "".join(f'<span class="pill" style="background:{bg};color:{fg}">{t}</span>'
                        for bg, fg, t in [("#15803d", "#fff", "Xong"), ("#0059b8", "#fff", "Đang chạy"), ("#fcd34d", "#0f0f12", "Chờ duyệt"),
                                          ("#b91c1c", "#fff", "Hỏng"), ("#f97316", "#0f0f12", "Không rõ")])
              + '</div></div>'),
        css=(".sc-status-dot{display:grid;gap:16px}.sc-status-dot .row{display:flex;flex-wrap:wrap;gap:16px;align-items:center}"
             ".sc-status-dot .k{width:88px;font-size:13px;color:var(--ovs-ink2)}"
             ".sc-status-dot .s,.sc-status-dot .pill{display:inline-flex;align-items:center;gap:8px;font-size:14px;line-height:1.4}"
             ".sc-status-dot i{width:8px;height:8px;border-radius:50%}.sc-status-dot .pill{padding:2px 12px;border-radius:999px;font-weight:600}")),
]
