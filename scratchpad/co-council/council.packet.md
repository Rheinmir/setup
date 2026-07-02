# Council - Blind Review Packet (Stage 2 setup)

**Question:** <the question put to the council>

## Blind answers (identities stripped)

| Label | Answer |
|-------|--------|
| A | Không generalize toàn bộ — chỉ EXTRACT helpers I/O (30% effort, 80% payoff): versioning+atomic-write (no-overwrite), html.escape wrapper, try/except context-manager scaffold, version naming+cleanup. KHÔNG share renderer transform (data-shape riêng mỗi skill, error-handling khác, generalize làm chậm). API minimal chạy ngay: safe_render(out_dir, version, data, renderer_fn, max_versions) — renderer_fn do skill sở hữu, COR lo atomic write+versioning+escape+fallback. Adoption low-risk: tuần này extract cor_helpers.py (optional, không đặt lib chung), áp PROPOSE trước (data-shape đơn giản nhất) làm proof; tuần sau offer 1-2 skill nếu họ muốn; 11 skill còn lại ship riêng không rủi ro. Verdict: propose tuần này, mở helpers nếu +1 skill muốn. Không lib, không thiết kế trước. |
| B | Invert — cách ĐẢM BẢO thất bại: (1) god-module 13 skill phụ thuộc, 1 breaking vỡ all; (2) ép khuôn cứng lên skill cần creative (cursor-animated-sites, uat, extract-site) → phải patch/bỏ qua; (3) sai abstraction boundary → refactor lại; (4) maintenance debt > gain (39 integration point nhưng DRY chỉ lợi ở 3-4); (5) docs-site-macos đã build full render → COR duplicate. Điều kiện TỐI THIỂU không thất bại: microlib KHÔNG god-module (chỉ 6 bất biến lõi, render sáng tạo = hook optional); OPT-IN không bắt buộc; boundary hẹp ổn định 1-2 hàm public; SCOPE 3-4 skill MAX (propose, docs-curate, onboard, tour-guide) — LOẠI cursor-animated/uat/extract-site (cần creative); checksum per output phát hiện regress. ROI: DRY chỉ thực ở 3-4 skill; lớn hơn = fragility > reuse. Kết: áp đúng 3 skill, bỏ ám thị generalize-thành-13. |
| C | Shared-lib tạo systemic tail-risk NẾU có state/tight-coupling/breaking-change/không pin version. Copy-in cũng nhầm: 6 bất biến đơn giản nhưng thiết kế lại 13 lần = drift/inconsistency → lỗi subtle (tệ hơn breaking rõ ràng). Barbell: (1) COR là stateless PURE-FUNCTION lib, không side-effect; (2) semantic versioning + explicit pin mỗi skill (assert __version__, fail-fast); (3) sacred backwards-compat: cor.py chỉ ADD never BREAK, 6 bất biến không đổi; (4) emergency copy-in escape hatch nếu cor.py chết. Điều kiện chấp nhận shared-lib: ≤200 dòng (tái bản 30 phút), zero runtime error (pure/typed/tested), version-pin enforced (CI fail floating import), deprecation path rõ. Kết: shared-lib OK nếu THIẾT KẾ CHO FAILURE MODE — không phải 'không bao giờ gãy' mà 'khi gãy isolated + dễ restore'. Small+pinned+backwards-compat = antifragile ở đuôi. |
| D | Leverage: cả 3 tầng nhưng THỨ TỰ khác. Cao nhất = RULE/GATE harness (b) — 65 skill hành xử độc lập nên lib (a) sẽ ngồi yên; chuẩn hoá TỪ HÀNH ĐỘNG (gate buộc conform trước merge) mới đổi tâm lý quyết định (structural constraint mạnh nhất). Sau đó (c) tái dùng docs-site-macos làm shell COR — KHÔNG viết renderer thứ 3: renderer là TOOL không phải POLICY; 2 renderer sẵn có là tool, COR chứa logic CHỌN cái nào fit + kiểm soát data/escape. Cuối (a) lib chỉ để codify bất biến thành schema/validator, KHÔNG generator. Rủi ro không làm gì: drift tích luỹ, khi breach (ghi đè lịch sử/quên escape) khó trace root. Rủi ro ép sớm: khoá use-case hợp lệ (vd CDN cho heavy-asset) — đợi ~3 sprint observe rồi mới ép. COR bổ sung, không chồng vai 2 renderer. |
| E | KHÔNG nên làm LIB — over-abstraction. 13 fit-high nhưng chỉ 1-2 thực sự share code render; 11-12 chỉ cần TUÂN 6 nguyên tắc (html.escape/try-except/no-overwrite quá generic, mỗi skill độc lập). LIB = coupling: COR đổi thì 13 skill test lại, nhưng 11 không dùng logic core. SKILL guidance = thêm indirect layer làm chậm iteration; author đã biết nguyên tắc, họ cần VÍ DỤ không wrapper. NÊN: (1) RULE/GATE harness kiểm 6 bất biến trước push (linter, non-blocking) + (2) DOCUMENT harness/docs/cor-guide.md: template copy-paste + checklist 6 điểm, mỗi skill tự implement → owned. Ít hơn nhưng tốt hơn: đừng xây cầu cho 2 skill. Quyết: Document + Gate, KHÔNG lib. |

## Anchor guard - per-judge presentation order

Seed: `42`. Show each judge its answers in THIS order to cancel position bias.

| Judge | Show in this order |
|-------|--------------------|
| seat-1 | C -> E -> D -> B -> A |
| seat-2 | B -> D -> A -> C -> E |
| seat-3 | A -> C -> B -> D -> E |

Hand each judge its blind answers in its row's order; collect a ranking of the labels (best first) into judges.json, then re-run `council.py rank ... --judges judges.json`.

