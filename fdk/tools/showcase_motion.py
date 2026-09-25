"""showcase_motion — khối MOTION + HƯỚNG DẪN + TRẠNG THÁI của design-showcase (PLAN 220926-design-showcase t5).

Motion mặc định: im lặng, chỉ phản hồi khi người dùng làm gì đó; ease-out, 180–240ms; chỉ animate transform/opacity/màu
(không transition: all); prefers-reduced-motion thì còn crossfade ngắn hoặc tắt hẳn. Quy ước khối: build-design-showcase.py.

proof: harness/tests/test_design_showcase.py
"""

GROUP = "Motion và trạng thái"

_RM = "@media (prefers-reduced-motion:reduce){{{}}}"

BLOCKS = [
    dict(
        id="motion-reveal", title="Hiện chi tiết khi bấm", rules=["motion-ease-out", "minimal-disclosure", "transition-all"],
        note="Mở bằng grid-template-rows 0fr → 1fr + opacity, 220ms ease-out: bắt đầu nhanh nên đọc như phản hồi tức thì. Ease-in ở đây đọc như bị trễ.",
        html=('<div class="sc-motion-reveal"><button class="t" type="button" aria-expanded="false">Hiện chi tiết</button>'
              '<div class="p"><div><p>Chi tiết chỉ hiện khi cần. Màn đầu giữ khoảng nghỉ cho mắt.</p></div></div></div>'),
        css=(".sc-motion-reveal .t{min-height:36px;padding:0 16px;border:1px solid var(--ovs-border);border-radius:999px;background:var(--ovs-surface2);color:var(--ovs-ink);font:inherit;cursor:pointer}"
             ".sc-motion-reveal .p{display:grid;grid-template-rows:0fr;opacity:0;transition:grid-template-rows .22s ease-out,opacity .22s ease-out}"
             ".sc-motion-reveal .p>div{overflow:hidden}.sc-motion-reveal .p p{margin:12px 0 0}"
             ".sc-motion-reveal.open .p{grid-template-rows:1fr;opacity:1}"
             + _RM.format(".sc-motion-reveal .p{transition:opacity .15s linear}")),
        js=("const t=root.querySelector('.t');t.addEventListener('click',()=>{const o=root.classList.toggle('open');"
            "t.setAttribute('aria-expanded',o);t.textContent=o?'Ẩn chi tiết':'Hiện chi tiết'});")),
    dict(
        id="motion-circle", title="Đổi sáng tối kiểu vòng tròn loang", rules=["motion-ease-out", "reduced-motion", "toggle"],
        note="Vòng tròn loang từ đúng chỗ bấm (clip-path circle), 360ms ease-out. Bản đầy đủ cho cả trang: skill dark-mode-maker. Giảm chuyển động thì đổi ngay, không loang.",
        html=('<div class="sc-motion-circle"><div class="stage"><span class="lb">Bấm vào khung</span><i class="wave"></i></div></div>'),
        css=(".sc-motion-circle .stage{position:relative;height:120px;border-radius:12px;overflow:hidden;background:var(--ovs-surface2);border:1px solid var(--ovs-border);cursor:pointer;display:grid;place-items:center}"
             ".sc-motion-circle .lb{position:relative;z-index:1;font-weight:600;padding:4px 12px;border-radius:999px;background:var(--ovs-bg);color:var(--ovs-ink)}"
             ".sc-motion-circle .wave{position:absolute;inset:0;background:var(--ovs-ink);clip-path:circle(0 at var(--x,50%) var(--y,50%));transition:clip-path .36s ease-out}"
             ".sc-motion-circle .stage.on .wave{clip-path:circle(150% at var(--x,50%) var(--y,50%))}"
             + _RM.format(".sc-motion-circle .wave{transition:none}")),
        js=("const s=root.querySelector('.stage');s.addEventListener('click',e=>{const r=s.getBoundingClientRect();"
            "s.style.setProperty('--x',(e.clientX-r.left)+'px');s.style.setProperty('--y',(e.clientY-r.top)+'px');s.classList.toggle('on')});")),
    dict(
        id="reduced-motion", title="Tôn trọng giảm chuyển động", rules=["reduced-motion", "transition-all"],
        note="Mọi animation có nhánh prefers-reduced-motion: chuyển động lớn đổi thành crossfade ≤ 150ms hoặc tắt. Chỉ animate transform, opacity, màu — không transition: all.",
        html=('<div class="sc-reduced-motion"><div class="box">Trượt vào 16px</div><p>Hệ điều hành bật "giảm chuyển động" thì khối chỉ hiện dần, không trượt.</p></div>'),
        css=(".sc-reduced-motion .box{display:inline-block;padding:12px 16px;border-radius:12px;background:var(--ovs-accent-bg);animation:sc-slide .24s ease-out both}"
             ".sc-reduced-motion p{margin:12px 0 0;color:var(--ovs-ink2)}"
             "@keyframes sc-slide{from{transform:translateY(16px);opacity:0}to{transform:none;opacity:1}}"
             "@keyframes sc-fade{from{opacity:0}to{opacity:1}}"
             + _RM.format(".sc-reduced-motion .box{animation:sc-fade .15s linear both}"))),
    dict(
        id="guide-steps", title="Hướng dẫn sử dụng từng bước", rules=["minimal-disclosure", "sentence-case", "ligature-off"],
        note="Mỗi bước: số thứ tự · việc cần làm (một câu) · lệnh chép được · chi tiết gập lại. Tối đa 5 bước một màn; lệnh trong <code> tắt ligature để -- không thành gạch dài.",
        html=('<ol class="sc-guide-steps">'
              + "".join(f'<li><div class="n">{i}</div><div class="c"><div class="t">{t}</div><code>{cmd}</code>'
                        f'<details><summary>Chi tiết</summary><p>{more}</p></details></div></li>'
                        for i, (t, cmd, more) in enumerate([
                            ("Cài harness vào dự án", "curl -fsSL …/bootstrap.sh | bash", "Chạy ở thư mục gốc dự án. Lệnh tạo .llmwiki và .harness."),
                            ("Soạn đề xuất", "/propose tên-tính-năng", "Đề xuất nằm trong wiki/sources/draft, chờ bạn duyệt."),
                            ("Chạy theo graph", "orca-graph build PLAN.md", "Việc song song được chạy cùng lúc, việc phụ thuộc chờ nhau.")], 1))
              + '</ol>'),
        css=(".sc-guide-steps{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:minmax(0,1fr);gap:16px}"
             ".sc-guide-steps li{display:flex;gap:16px}"
             ".sc-guide-steps .n{flex:none;width:32px;height:32px;border-radius:50%;display:grid;place-items:center;font-weight:700;background:var(--ovs-ink);color:var(--ovs-bg)}"
             ".sc-guide-steps .c{min-width:0;flex:1}.sc-guide-steps .t{font-weight:600;margin:4px 0 8px}"
             ".sc-guide-steps code{display:block;overflow-x:auto;white-space:nowrap;padding:8px 12px;border-radius:8px;background:var(--ovs-surface2);border:1px solid var(--ovs-border);font-size:13px}"
             ".sc-guide-steps details{margin:8px 0 0}.sc-guide-steps summary{cursor:pointer;font-size:13px;color:var(--ovs-ink2)}"
             ".sc-guide-steps p{margin:4px 0 0;font-size:14px;color:var(--ovs-ink2)}")),
    dict(
        id="empty-state", title="Trạng thái rỗng", rules=["svg-a11y", "tap-target"],
        note="Nói rõ vì sao rỗng và việc làm tiếp theo, kèm MỘT nút chính. Icon trang trí gắn aria-hidden.",
        html=('<div class="sc-empty-state"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16v12H4z"/><path d="M4 7l2-3h12l2 3"/></svg>'
              '<div class="t">Chưa có graph nào</div><p>Viết PLAN.md rồi dựng graph để thấy việc nào chạy song song.</p>'
              '<button type="button">Dựng graph đầu tiên</button></div>'),
        css=(".sc-empty-state{text-align:center;padding:24px}.sc-empty-state svg{width:40px;height:40px;fill:none;stroke:var(--ovs-ink2);stroke-width:1.5}"
             ".sc-empty-state .t{font-family:var(--font-display);font-size:17px;font-weight:var(--fw-heading,600);margin:8px 0 4px}.sc-empty-state p{margin:0 auto 16px;max-width:32em;color:var(--ovs-ink2)}"
             ".sc-empty-state button{min-height:36px;padding:0 16px;border:0;border-radius:999px;background:var(--ovs-ink);color:var(--ovs-bg);font:inherit;font-weight:600;cursor:pointer;white-space:nowrap}")),
    dict(
        id="loading", title="Đang tải", rules=["reduced-motion", "eight-states"],
        note="Khung xương đúng hình nội dung sắp tới (không spinner giữa trang trống); vùng đang tải gắn aria-busy; giảm chuyển động thì bỏ ánh quét.",
        html='<div class="sc-loading" aria-busy="true" aria-label="Đang tải danh sách"><i class="l w1"></i><i class="l w2"></i><i class="l w3"></i></div>',
        css=(".sc-loading{display:grid;gap:12px}.sc-loading .l{display:block;height:12px;border-radius:6px;"
             "background:linear-gradient(90deg,var(--ovs-surface2) 0%,var(--ovs-accent-bg) 50%,var(--ovs-surface2) 100%);background-size:200% 100%;animation:sc-shimmer 1.2s linear infinite}"
             ".sc-loading .w1{width:60%}.sc-loading .w2{width:90%}.sc-loading .w3{width:40%}"
             "@keyframes sc-shimmer{to{background-position:-200% 0}}" + _RM.format(".sc-loading .l{animation:none}"))),
    dict(
        id="error-state", title="Trạng thái lỗi", rules=["contrast", "side-stripe", "eight-states"],
        note="Ba phần: chuyện gì xảy ra · vì sao · làm gì tiếp (nút thử lại). Nền nhạt màu lỗi CẢ khối, viền đều; không sọc đỏ một cạnh.",
        html=('<div class="sc-error-state" role="alert"><div class="t">Không tải được bảng dispatch</div>'
              '<p>Không đọc được file graph.json (hết quyền đọc). Kiểm quyền thư mục llmwiki/graph rồi thử lại.</p>'
              '<button type="button">Thử lại</button></div>'),
        css=(".sc-error-state{padding:16px 20px;border:1px solid var(--ovs-bad);border-radius:14px;background:var(--ovs-bad-bg)}"
             ".sc-error-state .t{font-family:var(--font-display);font-weight:var(--fw-heading,600);color:var(--ovs-bad)}.sc-error-state p{margin:4px 0 12px}"
             ".sc-error-state button{min-height:36px;padding:0 16px;border:1px solid var(--ovs-bad);border-radius:999px;background:transparent;color:var(--ovs-bad);font:inherit;font-weight:600;cursor:pointer}")),
    dict(
        id="progress-read", title="Vạch tiến độ đọc", rules=["motion-ease-out", "reduced-motion", "line-over-text", "fixed-trapped"],
        note="Vạch 4px ở mép trên, chạy theo phần đã cuộn; cập nhật bằng transform: scaleX (không đổi width) nên không giật. Trang docs-shell: lớp nền tự gắn ở mép trên CỬA SỔ (fixed), không đặt absolute trong sidebar cuộn (vạch sẽ cắt ngang mục). Vạch fixed phải là con TRỰC TIẾP của body: đặt trong nav có backdrop-filter/transform thì nav thành khung chứa và vạch bị nhốt trong sidebar (luật fixed-trapped).",
        html=('<div class="sc-progress-read"><i class="bar"></i><div class="scroll" tabindex="0" aria-label="Vùng cuộn ví dụ">'
              + "".join(f"<p>Đoạn {i}: cuộn trong khung này để thấy vạch chạy.</p>" for i in range(1, 9)) + '</div></div>'),
        css=(".sc-progress-read{position:relative;border:1px solid var(--ovs-border);border-radius:12px;overflow:hidden}"
             ".sc-progress-read .bar{position:absolute;inset:0 0 auto 0;height:4px;background:var(--ovs-accent);transform-origin:0 50%;transform:scaleX(0)}"
             ".sc-progress-read .scroll{height:140px;overflow-y:auto;padding:12px 16px}.sc-progress-read p{margin:0 0 12px}"),
        js=("const s=root.querySelector('.scroll'),b=root.querySelector('.bar');s.addEventListener('scroll',()=>{"
            "b.style.transform='scaleX('+(s.scrollTop/(s.scrollHeight-s.clientHeight||1))+')'},{passive:true});")),
]
