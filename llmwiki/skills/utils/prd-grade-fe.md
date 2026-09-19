---
name: prd-grade-fe
description: "Pipeline MỘT CỬA ra frontend chuẩn production có CỔNG MÁY GÁC: phỏng vấn nguồn theme một tin nhắn (A preset macOS glassmorphism mặc định · B folder/file tài liệu thiết kế · C paste URL trang đích), khoá thông số vào MỘT file design.md (hallmark và impeccable đọc chung) rồi sinh tokens.css + frontmatter bằng design-sync.py, dựng trang token-only theo hallmark, chạy fe-gate.sh (impeccable detect 61 luật tất định rc 0/1/2 + Playwright 4 viewport) và rubric audit/harden/polish, KHÔNG giao khi cổng chưa xanh. Gọi khi user nói 'frontend production', 'production-grade frontend', 'dựng FE chuẩn production', 'giao diện kỷ luật', 'prd-grade-fe', '/prd-grade-fe'. Khác hallmark (sàn design, không có gate impeccable) và khác /br (dây chuyền BR→frame, không lo riêng tầng frontend)."
version: 1.0.0
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# prd-grade-fe

`$SKILL` dưới đây = **Base directory của skill này** (dòng "Base directory for this skill" khi skill được nạp; trong repo framework là `skills/prd-grade-fe`). Mọi script và reference đi kèm thư mục skill, không phụ thuộc repo.

Hub mỏng. Không sở hữu luật thiết kế: thẩm mỹ là của **hallmark** (`skills/hallmark/SKILL.md`), luật tất định là của **impeccable** (`npx -y impeccable@3.6.1 detect`, pin cứng). Hub sở hữu **thứ tự** và **hợp đồng giữa các pha**, cộng hai script có `--self-test`:

| File | Vai trò |
|---|---|
| `scripts/design-sync.py` | `design.md` là nguồn chân lý: block ```css :root{}``` → frontmatter YAML (impeccable đọc) + `tokens.css`. `--check` rc 1 khi drift. |
| `scripts/fe-gate.sh` | Cổng trước khi giao: assert target tồn tại → `detect --json` → rc 0/1/2 đúng nghĩa → `viewport-check.mjs` 320/375/414/768. Exit 0 xanh · 1 lỗi impeccable · 2 finding/viewport đỏ · 3 skipped (thiếu node/mạng) · 4 target thiếu. |
| `scripts/badge-consistency.py` | Rule tất định impeccable không có (GH#164): trong MỘT file, badge trạng thái (`render*Badge`/`*Status*`/`*Pill*`/span pill) phải cùng chữ ký icon-hay-dot · `rounded-*` · hằng token (`STATUS_GLASS`); badge lệch đa số (≥2) → `file:line`, fe-gate tính là finding rc 2. |
| `references/presets/macos-glass.design.md` | Preset mặc định đã qua detect rc 0; bằng chứng ở `macos-glass.evidence.md`. |
| `references/intake.md` | Route A/B/C → `design.md`. |
| `references/impeccable-audit.md` | Rubric audit (5 trục /20) · harden · polish, distill có nguồn. |

## WHAT

### Purpose và context
- **Purpose:** ra một trang/màn hình frontend chuẩn production có CỔNG MÁY GÁC — theme khoá vào MỘT `design.md`, dựng token-only theo hallmark, không giao khi `fe-gate.sh` chưa xanh và P0 chưa = 0.
- **Trigger (when to use)** — mục `## When to use` cũ:
  - User muốn một trang/màn hình frontend **đưa vào production**, không phải mockup nhanh (mockup nhanh → `/br` hoặc hallmark trần).
  - User đưa theme dưới dạng "mặc định đi", "đây là tài liệu thiết kế", hoặc "làm giống trang này: <URL>".
  - Project đã có `design.md` và cần thêm màn hình **cùng hệ** kèm cổng kiểm.
- **Non-goals:** không phải mockup nhanh (→ `/br` hoặc hallmark trần); không sở hữu luật thiết kế (thẩm mỹ = hallmark, luật tất định = impeccable); không lo dây chuyền BR→frame.

### Mental model
`nguồn theme (A preset · B tài liệu · C URL) → design.md (nguồn chân lý) → design-sync.py → tokens.css + frontmatter → build token-only (hallmark) → fe-gate.sh (impeccable detect + badge-consistency + 4 viewport) → audit/harden/polish → report`. Hub sở hữu **thứ tự** và **hợp đồng giữa các pha**; luật nằm ở hallmark/impeccable.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | brief trang/màn hình | có | thứ cần dựng |
| In | nguồn theme A/B/C, audience, use case, tone | không | "go ahead"/bỏ trống → A + suy luận 2–4 từ brief, công bố một câu |
| In | `design.md` có sẵn | không | có + `--check` rc 0 → dùng lại, nhảy Pha 3 |
| Out | `design.md` + `tokens.css` đồng bộ | có | `design-sync.py --check` rc 0 |
| Out | HTML output token-only có stamp design + critique | có | toggle sáng/tối, footer path tương đối |
| Out | `fe-gate.report.json` + report 8 mục (Pha 5) | có | "sẵn sàng production" chỉ khi fe-gate exit 0 và P0 = 0 |

### Rules và capabilities
- RULE-01 (MUST): Không chép rubric hallmark vào đây; sửa luật thì sửa ở hallmark hoặc `references/impeccable-audit.md` (có nguồn + sha).
- RULE-02 (MUST): **Không bao giờ** gọi `npx impeccable install` (bản 3.6.1 không có `--help` cho install, nó cài thật vào `$HOME`). `--scope` luôn viết dính (`--scope=type`). Tin JSON ở stdout, không tin stderr (npx gộp luồng).
- RULE-03 (MUST): Vòng sửa quá 3 mà còn finding → giao kèm bảng dư và nói thẳng; hoặc waiver có lý do trong `.impeccable/config.json` (`{"ignores":[...]}`) được nêu trong report. Không ignore lén.
- RULE-04 (MUST): Thiếu node/mạng → report ghi `skipped: <lý do>`, exit gate ≠ 0. Không có ngoại lệ "chắc cũng ổn".
- RULE-05 (MUST): `design.md` đã tồn tại → không ghi đè; đổi hệ thì AMEND `## Variants` (no-overwrite policy của hallmark design-md).
- RULE-06 (MUST): Self-check khi sửa skill: `python3 $SKILL/scripts/design-sync.py --self-test && python3 $SKILL/scripts/badge-consistency.py --self-test && bash $SKILL/scripts/fe-gate.sh --self-test`, rồi `bash fdk/tools/sync-skill.sh prd-grade-fe`.
- Capabilities: đọc/ghi file design + output trong project; chạy script đồng bộ token và cổng phát hiện antipattern tất định (pin phiên bản); điều khiển trình duyệt headless đo 4 viewport; đọc URL/tài liệu thiết kế làm nguồn theme.

### Failure boundaries
- Thiếu node/mạng → `skipped: <lý do>`, gate exit ≠ 0, report KHÔNG nói sạch (**partial**).
- fe-gate rc 1 / 3 / 4 → **blocked**, dừng, ghi nguyên nhân; không có đường nào từ 1/3/4 tới "sạch".
- rc 2 sau 3 vòng sửa → **partial**: giao kèm bảng finding dư hoặc waiver có lý do nêu trong report.
- `design-sync.py --check` rc 1 (drift) → chưa đi tiếp Pha 3.
- User đòi đổi theme khi `design.md` đã có → AMEND `## Variants`, không ghi đè.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | project | Pha 0 pre-flight: `ls design.md …`, `command -v node`, `design-sync.py --check` | hệ đã khoá hay chưa, node có không | đã khoá → B01; không node → B02 |
| W02 | judgment | brief | Pha 1 interview MỘT tin nhắn (nguồn theme · audience · use case · tone) | đáp án hoặc suy luận công bố | — |
| W03 | effect | nguồn theme | Pha 2 khoá biến A/B/C → `design.md` → `design-sync.py && --check` | rc 0 | rc 1 → sửa drift |
| W04 | effect | `design.md` | Pha 3 build theo hallmark, token-only, stamp đầu file | HTML output | critique trục < 3 → sửa trước W05 |
| W05 | deterministic | output | Pha 4 gate: `fe-gate.sh` (≤ 3 vòng) → audit /20 → harden/polish → slop-test → fe-gate lần cuối | exit 0 + P0 = 0 | rc 1/3/4 → blocked; rc 2 sau 3 vòng → partial |
| W06 | judgment | kết quả | Pha 5 deliver + report 8 mục | report | — |

Chi tiết từng bước (nguồn chân lý cho W01–W06) — mục `## Steps` cũ, nguyên văn:

#### Pha 0 — Pre-flight (không hỏi thứ máy tự thấy)
```bash
ls design.md DESIGN.md tokens.css 2>/dev/null; command -v node && echo node-ok
python3 $SKILL/scripts/design-sync.py --check 2>/dev/null; echo sync-rc=$?
```
- Có `design.md` và `--check` rc 0 → nói "hệ đã khoá, dùng lại" và nhảy Pha 3 (trừ khi user đòi đổi theme → `references/intake.md` § "Khi project đã có design.md").
- Không có `node` → vẫn làm Pha 1–3, nhưng Pha 4 sẽ ghi `skipped` và report KHÔNG được nói sạch.

#### Pha 1 — Interview MỘT tin nhắn (gộp câu của hallmark, không hỏi nối đuôi)
> Trước khi dựng, cần 4 thứ. Trả lời phần nào cũng được, hoặc nói **"go ahead"**:
> 1. **Nguồn theme** — [A] macOS glass mặc định · [B] đường dẫn tài liệu thiết kế (file/folder) · [C] URL trang đích
> 2. **Audience** — ai dùng, họ biết gì sẵn?
> 3. **Use case** — một hành động trang này phải dẫn tới?
> 4. **Tone** — chọn một cực: editorial · brutalist · soft · utilitarian · luxury · playful · technical · austere

"go ahead" hoặc bỏ trống → chọn **A**, suy luận 2–4 từ brief, **công bố suy luận một câu ở đầu reply** (hallmark Step 1 opt-out protocol). Không có ngoại lệ "brief đã đủ rõ": vẫn hỏi, user vẫy qua trong hai giây.

#### Pha 2 — Khoá biến (`references/intake.md`)
- **A**: `cp $SKILL/references/presets/macos-glass.design.md ./design.md`, đổi tên project ở dòng đầu.
- **B**: đọc tài liệu → bảng schema có nguồn file:dòng → MỘT câu hỏi bù → ghi `design.md` + § Provenance.
- **C**: hallmark `study <URL>` (URL mode, refuse list + attestation) → "lock the DNA" → `design.md` có § Provenance + § Notes (rhythm blind spot, anti-pattern không mang theo).
- Rồi: `python3 $SKILL/scripts/design-sync.py && python3 $SKILL/scripts/design-sync.py --check` → rc 0 mới đi tiếp.
- Công bố Genre / Macrostructure / Theme ra lời (hallmark Step 2.5).

#### Pha 3 — Build theo hallmark, hệ đã khoá
- Chạy hallmark default flow (Step 2 macrostructure → 3 ruleset → 5 preview → 6 build) với `design.md` locked: diversification **đảo chiều** (màn hình phải CHUNG hệ).
- Mọi màu, font, radius, motion qua `var(--…)` từ `tokens.css` (hallmark discipline 3). Không hex/oklch inline; thiếu token thì thêm vào block `:root` của `design.md` rồi chạy `design-sync.py` lại.
- Output HTML cho người xem: toggle sáng/tối bằng nút gạt có nhãn + `html[data-theme]` + localStorage + chống FOUC; thang chữ compact 13″; footer ghi path **tương đối** của chính file.
- Stamp đầu file: `<!-- design: macrostructure=<M> theme=<T> -->` và `/* Hallmark · pre-emit critique: P? H? E? S? R? V? */` (6 trục, trục nào < 3 thì sửa trước khi sang Pha 4).

#### Pha 4 — Gate (máy trước, người sau)
1. `bash $SKILL/scripts/fe-gate.sh <output.html …>`; đọc bảng `antipattern | file:line | snippet` và `fe-gate.report.json`.
   - Dòng `badge lệch pattern so với N badge anh em` = badge-consistency: sửa badge lệch theo anh em (đa số), không sửa ngược.
   - rc 2 → sửa đúng finding (đổi token trong `design.md` → sync lại, hoặc sửa markup) → chạy lại. **Tối đa 3 vòng.** Ghi số finding từng vòng để đưa vào report.
   - rc 1 / 3 / 4 → dừng, ghi nguyên nhân. Không có đường nào từ 1/3/4 tới "sạch".
2. Nạp `references/impeccable-audit.md`: chấm 5 trục /20, liệt kê P0–P3; làm checklist Harden rồi Polish. **P0 phải = 0.**
3. Chạy hallmark slop-test (`skills/hallmark/references/slop-test.md`) trên output; gate nào đỏ thì sửa.
4. Chạy lại `fe-gate.sh` một lần cuối sau mọi chỉnh sửa (sửa harden/polish có thể tái sinh finding).

#### Pha 5 — Deliver + report
Report gồm, theo thứ tự: (1) suy luận/đáp án Pha 1; (2) Genre/Macrostructure/Theme + nguồn theme; (3) 6 điểm critique; (4) bảng finding vòng 1..n và rc cuối; (5) điểm audit /20 + P0 count; (6) 4 viewport; (7) path output tương đối; (8) `skipped` nếu có. Câu "sẵn sàng production" chỉ được viết khi fe-gate exit 0 và P0 = 0.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | có `design.md` và `--check` rc 0 | nói "hệ đã khoá, dùng lại", bỏ W02–W03 | user đòi đổi theme → `references/intake.md` § "Khi project đã có design.md" | W04 |
| B02 | recovery | không có `node` / mạng | vẫn làm Pha 1–3; Pha 4 ghi `skipped` | report KHÔNG được nói sạch | W06 |
| B03 | user_optional | nguồn theme = B (tài liệu) | bảng schema có nguồn file:dòng → MỘT câu hỏi bù → `design.md` + § Provenance | — | W03 (sync) |
| B04 | user_optional | nguồn theme = C (URL) | hallmark `study <URL>` → "lock the DNA" → `design.md` + § Provenance + § Notes | — | W03 (sync) |
| B05 | recovery | fe-gate rc 2 | sửa đúng finding (token trong `design.md` → sync, hoặc markup) → chạy lại, tối đa 3 vòng | quá 3 vòng → giao kèm bảng dư hoặc waiver có lý do | W05 |

### Validation và stopping
Cổng máy: `fe-gate.sh` exit 0 (impeccable detect rc 0 + badge-consistency + 4 viewport 320/375/414/768) và `design-sync.py --check` rc 0. Cổng người/rubric: audit 5 trục /20 với P0 = 0, slop-test không đỏ. Vòng sửa gate trần 3; fe-gate chạy lại một lần cuối sau mọi chỉnh sửa.

### Examples
- **Positive:** `/prd-grade-fe dựng trang danh sách đơn hàng cho app quản lý kho, mặc định theme` → chọn A, `cp` preset macos-glass thành `design.md`, sync rc 0, build token-only, fe-gate vòng 1 rc 2 (2 finding) → sửa → vòng 2 exit 0, P0 = 0 → report 8 mục, được ghi "sẵn sàng production".
- **Boundary/failure:** máy không có `node` → Pha 1–3 vẫn làm, fe-gate exit 3 → report ghi `skipped: thiếu node`, KHÔNG viết "sẵn sàng production".

#### Ví dụ gọi
```
/prd-grade-fe dựng trang danh sách đơn hàng cho app quản lý kho, mặc định theme
/prd-grade-fe trang pricing, theme lấy từ docs/brand/ (folder)
/prd-grade-fe landing cho sản phẩm X, làm giống https://example.com
```
