---
name: qc-uiux
description: >-
  Audit UI/UX phong cách SENIOR — bốn mục accessibility · visual-hierarchy · consistency · antipattern,
  mỗi mục cho ĐIỂM/10 + LỖI NẶNG NHẤT + CÁCH SỬA, rồi một kết luận PASS-sang-bước-kế hay CẦN-SỬA.
  Phần ĐO ĐƯỢC (contrast WCAG, tap-target, overlap/misalign hình học, missing-label) chạy tất định
  qua engine visual-qa (headless, 0-token, KHÔNG LLM); phần cần MẮT (hierarchy, drift design-system,
  dark-pattern) là LLM audit. Gọi khi user nói "qc uiux", "audit ui", "soi giao diện", "dẹp antipattern
  ui", "/qc-uiux", hoặc SAU khi có mockup/UI. NHÂN KHUÔN /qc-code (đắt=LLM tay, rẻ=test tất định auto).
  KHÁC /redesign (đổi mới thẩm mỹ) và /visual-qa (chụp+gác pixel) — qc-uiux là verdict senior 4-mục.
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: qc-uiux

## WHAT

### Purpose và context
- **Purpose:** cho một verdict SENIOR về UI/UX của route/màn đang có — bốn mục (accessibility · visual-hierarchy · consistency · antipattern), mỗi mục điểm/10 + lỗi nặng nhất + cách sửa — với phần đo được lấy từ engine tất định, phần cần mắt do LLM audit.
- **Trigger (when to use):**
  - Vừa dựng/đổi UI (mockup `/br`, trang mới, component) và muốn một cặp mắt senior soi trước khi chốt.
  - Trước commit thay đổi UI đáng kể — cắm tùy chọn vào `/orca-workflow` trước `verify-before-commit`, và tự-động sau mỗi `/br run` frame có UI.
  - User nói "qc uiux", "audit ui", "soi giao diện", "dẹp antipattern ui", "/qc-uiux".
- **Non-goals:** KHÔNG dùng cho: đổi mới thẩm mỹ tổng thể (đó là `/redesign-existing-projects`), hay chỉ chụp+so pixel (đó là `/visual-qa` — qc-uiux GỌI nó làm engine đo). Không review CODE (đó là `/qc-code`). Verdict không chặn commit.

### Mental model
`route/màn → engine tất định (DESIGN_AUDIT đo rect thật) = DỮ KIỆN → 4 mục × (điểm/10 · lỗi nặng nhất · cách sửa) = Ý KIẾN có dẫn số → verdict PASS | CẦN SỬA (theo mục/route yếu nhất) → sửa → engine lại (đỏ→xanh)`. Đắt (LLM, gọi tay) tách rẻ (engine, auto hook).

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | route/màn | không (mặc định = mockup/route hiện có) | user chỉ định thì soi cái đó |
| In | `<base-url>` chạy được | có cho phần đo | engine headless cần server; không dựng được → fail-open |
| In | loại route (list/table?) | tự xác định | có → nạp `references/list-control-checklist.md` |
| Out | 4 mục × điểm/10 · lỗi nặng nhất · cách sửa | có | mục 3 kèm bảng drift; mục có lỗi đo được dẫn số engine |
| Out | verdict | có | `PASS` hoặc `CẦN SỬA` + danh sách phải sửa — ADVISORY |
| Out | draft `llmwiki/wiki/sources/draft/DDMMYY-qc-uiux-<route>.md` + index + log | có (trừ khi chỉ chạy engine) | mục Output Report |

### Rules và capabilities
- RULE-01 (MUST): **Tách đắt/rẻ:** LLM audit (4 mục) = gọi tay / bước workflow tùy chọn. Đo tất định = auto qua engine visual-qa. KHÔNG gọi LLM trong hook (nguyên tắc hook-0-token).
- RULE-02 (MUST): **Verdict advisory, engine đo gác cứng** — không để LLM verdict chặn commit; số đo (contrast/tap-target/geometry) mới là dữ kiện.
- RULE-03 (MUST): **Đọc CSS là MÙ hình học** — mọi nhận định layout/kích cỡ/contrast phải ĐO rect thật qua engine, không suy từ CSS tĩnh.
- RULE-04 (MUST): **Không dẫm:** `/redesign-existing-projects` = đổi mới thẩm mỹ · `/visual-qa` = chụp+gác pixel-diff · `/qc-code` = review CODE. `/qc-uiux` = verdict senior 4-mục UI/UX + reuse engine đo.
- RULE-05 (MUST): **Chức năng trước thẩm mỹ, không bình quân điểm** (học từ skill `qa` của browser-use, 09/2026):
  nếu route/luồng đang soi có tác vụ người dùng (submit, checkout, đăng nhập) mà tác vụ KHÔNG
  hoàn thành được → verdict `CẦN SỬA` bất kể 4 mục điểm cao — đẹp không cứu được luồng gãy.
  Verdict tổng lấy theo mục/route YẾU NHẤT, không lấy trung bình cộng.
- RULE-06 (MUST): **Ảnh chụp sạch không chứng minh gì** — khi engine chạy headless, moi thêm lỗi ẩn: console
  `error`, `pageerror`, response `>= 400`, `requestfailed` (xem `/playwright-verify` Rules).
  Trang trông đẹp mà ném lỗi ở mọi cú bấm → ghi vào mục 4, không cho PASS.
- RULE-07 (MUST): **a11y là luật, không phải gu** — carve-out CLAUDE.md: không lười ở contrast/tap-target/label. Chỉ ~30% WCAG tự-động → phần còn lại ghi rõ "cần mắt người / nợ `[[150726-unknown-ledger]]`".
- Capabilities: chạy trang trong trình duyệt headless để đo DOM/rect/contrast (0-token); đọc CSS/DOM; ghi draft wiki. Không sửa UI trong lúc audit.

### Failure boundaries
- Không dựng được server/headless → engine **fail-open** (không chặn); audit LLM vẫn chạy nhưng phải ghi phần đo được là chưa có số.
- Tác vụ người dùng trên route không hoàn thành được → verdict `CẦN SỬA` bất kể điểm 4 mục.
- Console `error`/`pageerror`/response `>= 400`/`requestfailed` → ghi vào mục 4, không cho PASS.
- Tiêu chí WCAG không tự-động được → ghi rõ "cần mắt người / nợ `[[150726-unknown-ledger]]`", không tự cho PASS.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W00 | judgment | route | Route là list/table? → nạp `references/list-control-checklist.md` | checklist bổ sung | không → bỏ qua |
| W01 | deterministic | route, `<base-url>` | Xác định phạm vi + chạy engine `route-shots.mjs --audit` trước | issues theo route | không dựng được → fail-open, ghi chú |
| W02 | judgment | issues + DOM | Chấm bốn mục: điểm/10 · lỗi nặng nhất · cách sửa | 4 mục đủ ba phần | — |
| W03 | deterministic | issues engine | Gắn dữ kiện engine vào mục có lỗi đo được | số đo dẫn nguồn | — |
| W04 | judgment | 4 mục | Kết luận `PASS` / `CẦN SỬA` (theo mục/route yếu nhất) | verdict + phải-sửa | — |
| W05 | deterministic | UI đã sửa | Chạy lại engine chứng minh lỗi đo-được hết (đỏ→xanh) | engine xanh | còn đỏ → vẫn CẦN SỬA |
| W06 | effect | kết quả | Ghi draft Output Report + index + log | draft | chỉ chạy engine → skip |

Chi tiết từng bước (nguồn chân lý cho W00–W06):

#### Phạm vi audit (mặc định = mockup/route hiện có)
Mặc định soi **UI đang có** — các route/trang mockup vừa dựng. User chỉ định route/màn thì soi cái đó. Đọc DOM + đo rect thật (getBoundingClientRect) qua engine; KHÔNG đoán từ CSS tĩnh (đọc CSS MÙ lỗi render — bài học 15/07/26).

#### Steps
0. **Route là list/table?** (queue, admin grid, ticket/request list, dashboard summary strip) → load thêm [`references/list-control-checklist.md`](references/list-control-checklist.md) — 11 lỗi hay gặp riêng cho list/table (chồng hệ màu trên row, sort bucket, overflow-clip popover, mobile filter collapse…), mỗi lỗi đã gắn sẵn mục nào trong 4 mục dưới.
1. **Xác định phạm vi** — route/màn nào. Chạy engine tất định trước để có DỮ KIỆN đo được (mục "Engine" dưới).
2. **Chấm bốn mục** (mục dưới). Mỗi mục: **điểm/10 · lỗi nặng nhất · cách sửa**. → Xong khi cả bốn mục đủ ba phần.
3. **Mục có lỗi ĐO ĐƯỢC: gắn dữ kiện engine** (contrast fail ở đâu, control nào <24px, cặp nào overlap…) — số đo là dữ kiện, verdict là ý kiến.
4. **Kết luận** — `PASS` (sang bước kế) hay `CẦN SỬA` (liệt kê phải sửa gì). → Xong khi verdict rõ + danh sách phải-sửa nếu CẦN SỬA.
5. **Chạy lại engine sau khi sửa** để chứng minh lỗi đo-được đã hết (đỏ→xanh), giống test tái hiện của qc-code.

#### Bốn mục

##### 1. Accessibility (a11y) — điểm/10 · lỗi nặng nhất · cách sửa
Soi (phần lớn ĐO ĐƯỢC — engine bắt): **contrast** (chữ thường ≥4.5:1, chữ lớn ≥3:1, control/viền/icon ≥3:1 — WCAG 2.2 AA) · **tap-target** (control tương tác ≥24×24px CSS là sàn AA 2.5.8; khuyến 44/48px mobile) · **focus-visible** (có vòng focus rõ, tương phản ≥3:1) · **missing-label** (nút/icon/link screen-reader đọc rỗng — thiếu aria-label/text). Đây là ranh giới tiếp cận — không lười (a11y là LUẬT, không phải gu). Lưu ý: chỉ ~30% tiêu chí WCAG tự-động được → phần còn lại (keyboard trap, thứ tự focus, alt có NGHĨA) là mắt người.

##### 2. Visual hierarchy — điểm/10 · lỗi nặng nhất · cách sửa
Soi (mắt LLM): **nút trông như nút, link trông như link, heading phân cấp kích cỡ rõ** (bắt user phải "giải mã" giao diện = fail) · **CTA rõ ràng** (hành động chính nổi bật, không mơ hồ) · **content density** (không nhồi quá nhiều lên một màn — quá tải = mất hierarchy). Chỉ ra đâu là điểm mắt dừng ĐẦU TIÊN và nó có đúng là hành động chính không.

##### 3. Consistency (design-system) — điểm/10 · lỗi nặng nhất · bảng drift
Soi (mắt LLM, vài phần đo được): **spacing theo token** (thang 4/8px — gap lộn xộn = mất nhịp) · **màu nhất quán** (không bảng màu chỏi/lẫn) · **shadow** (không lạm dụng/sai độ sâu — engine bắt `shadow-clipped`/`monochrome-surface`) · **typography** (cặp font/size nhất quán) · **đồng nhất xuyên trang** (cùng thứ gọi cùng kiểu ở mọi màn). **Trả bảng drift:**

| Chỗ | Lệch chuẩn | Sửa về |
|-----|-----------|--------|
| card padding | 14px / 20px / 17px lẫn lộn | token `--sp-4` (16px) |

##### 4. Antipattern & interaction — điểm/10 · lỗi nặng nhất · bằng chứng đo
Soi: **dark-mode readability** (chữ washed-out quá nhạt/quá tối — lỗi dark-mode kinh điển, engine bắt qua contrast-aa ở theme tối) · **hình học vỡ** (overlap ≥4px, row-misalign — control chồng/không cao bằng nhau, engine ĐO rect) · **feedback thiếu** (hành động không có phản hồi hệ thống) · **responsive vỡ** (tràn ngang, chồng ở khổ hẹp) · **dark-pattern** (ép buộc, gài lựa chọn, khó thoát). Mỗi lỗi đo-được → **dẫn số từ engine** (route nào, cặp nào, chồng bao nhiêu px).

#### Kết luận (verdict)
Một trong hai, kèm lý do:
- **PASS** — không lỗi nặng ở mục nào; a11y đo-được sạch; sang bước kế được.
- **CẦN SỬA** — liệt kê **cụ thể** phải sửa gì (ưu tiên a11y đo-được + hình học vỡ trước hierarchy/consistency).

> **Verdict là ADVISORY — người quyết, không chặn commit.** Thứ gác cứng là engine tất định (contrast/tap-target/overlap/misalign đỏ→xanh). Đừng để user tưởng "qc-uiux PASS = UI hoàn hảo"; nó là cặp mắt senior, không phải bằng chứng.

#### Engine tất định (0-token, KHÔNG LLM) — reuse visual-qa
Phần ĐO ĐƯỢC dùng chung engine của `/visual-qa` (`skills/visual-qa/assets/route-shots.mjs`, headless playwright), hàm `DESIGN_AUDIT` đo rect thật trong trang và bắt các rule: `contrast-aa` · `tap-target` · `missing-label` · `overlap` · `row-misalign` · `shadow-clipped` · `monochrome-surface` · `rogue-slab`. Chạy:

```bash
node skills/visual-qa/assets/route-shots.mjs <base-url> --audit    # in issues theo route; exit ≠0 nếu a11y/hình học fail
```

Đây là phần "tự động hook khi UI đổi" — **chỉ hook phần rẻ tất định**, LLM audit (skill này, 4 mục) giữ gọi tay. Fail-open nếu chưa dựng được server/headless (không chặn). Giống `qc-regression.py --run` của qc-code: `verify-before-commit` bước 3b gọi nó; UI đổi → antipattern đo-được không âm thầm quay lại.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | route là list/table (queue, admin grid, ticket/request list, dashboard summary strip) | nạp `references/list-control-checklist.md`, 11 lỗi gắn sẵn vào 4 mục | route khác → skip | W01 |
| B02 | recovery | không dựng được server/headless | engine fail-open (không chặn), audit LLM tiếp, ghi phần đo được là chưa có số | — | W02 |
| B03 | conditional_required | route có tác vụ người dùng (submit, checkout, đăng nhập) không hoàn thành được | verdict `CẦN SỬA` bất kể điểm 4 mục | — | W04 |

### Validation và stopping
Phần đo được (contrast, tap-target, overlap, misalign, missing-label…) do engine tất định quyết, exit ≠0 khi fail; phần hierarchy/drift/dark-pattern là review LLM, verdict chỉ advisory. Dừng khi 4 mục đủ ba phần + verdict rõ; sau sửa, engine phải xanh (W05).

### Examples
- **Positive:** `/qc-uiux` sau `/br run` frame form đăng ký → engine sạch, 4 mục 8–9/10, lỗi nặng nhất mục 3 là card padding 14/20/17px → bảng drift về `--sp-4` → verdict `PASS`, draft `DDMMYY-qc-uiux-signup.md`.
- **Boundary/failure:** dark mode chữ phụ contrast 2.8:1 + nút icon 20×20px → engine `contrast-aa` + `tap-target` fail có số → mục 1 lỗi nặng nhất + cách sửa → `CẦN SỬA`; sửa xong chạy lại engine phải xanh.
- **Boundary:** trang đẹp, 4 mục điểm cao nhưng nút submit ném `pageerror` → mục 4 ghi lỗi, verdict `CẦN SỬA`.

### Reference — Related
- `references/list-control-checklist.md` — 11 lỗi riêng cho list/table (đọc Steps bước 0).
- `skills/visual-qa/assets/route-shots.mjs` — engine đo tất định (DESIGN_AUDIT) mà skill này reuse.
- `llmwiki/skills/dev-loop/qc-code.md` — skill anh em: cùng khuôn đắt-LLM / rẻ-tất-định, cho CODE.
- `harness/scripts/qc-regression.py` — runner test qc-* tất định (qc-code) chạy ở verify-before-commit.
- `llmwiki/skills/dev-loop/build-now-adapt-later.md` — quA khuôn tách quarantine đắt/rẻ.

### Delivery — Output Report
Sau khi audit xong, ghi draft `llmwiki/wiki/sources/draft/DDMMYY-qc-uiux-<route>.md` (OKF frontmatter `type: draft`, `## Origin`) tóm: route đã soi · điểm 4 mục · lỗi đo-được từ engine · verdict + phải-sửa. Thêm dòng vào `index.md` + `log.md`. Bỏ qua nếu chỉ chạy engine đo (không có phán đoán mới).
