---
name: doyourmagic
proof: skills/doyourmagic/references/example-setup/workflows.md
description: "Given a freshly-cloned external repo/tool, run clone→explore→verify→write to produce a bundle of RUNNABLE workflow skills under .overstack/doyourmagic/<repo>/skills/ — one hub skill /dym-<repo> (1 dòng context, chỉ nạp workflow con khi được gọi) + N sub-skills dạng SKILL.md promote thẳng lên repo chính (npx skills add) — plus workflows.md (index + bảng kiểm chứng) and flow.html (docs-site-macos, sơ đồ luồng skill→sản phẩm→skill kế). Trigger on 'kéo repo mới về', 'clone tool này làm workflow', 'doyourmagic', 'onboard external tool/repo', 'generate workflow docs/skills for this repo', or /doyourmagic. Options: --name <prefix> · --humanize."
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: doyourmagic

## WHAT

### Purpose và context
- **Purpose:** biến một repo/tool ngoài vừa clone thành bundle skill workflow CHẠY ĐƯỢC (hub `/dym-<repo>` + N sub-skill) kèm `workflows.md` (bảng kiểm chứng) và `flow.html`, mọi lệnh đã đối chiếu với code/`--help`/chạy thật — rồi đưa một verdict adapt-modes.
- **Trigger (when to use):**
  - User just cloned/installed an external repo/CLI/tool and wants "how do I actually use this thing" as something **gõ được**, not a README to re-read each time.
  - User says "kéo repo mới về", "doyourmagic <repo>", "làm workflow cho tool này", "generate workflow docs for this repo", "viết hộ cách dùng runnable cho repo này".
  - Before folding an external tool into project conventions/CI — produce the bundle first so the integration decision is grounded in verified commands, not README paraphrase.
- **Non-goals:** không paraphrase README; không sửa clone (read-only); không tự scaffold/tích hợp vào repo chính khi verdict chưa được user duyệt; không promote hub.

### Mental model
`clone (sandbox, read-only) → manifest → README = giả thuyết → đối chiếu parser/--help/exit thật → chạy thật (scope pin) → workflow chia theo ĐỐI TƯỢNG → sub-skill + hub → workflows.md + flow.html → verdict adapt-modes → (tuỳ) dym-sync push / install / promote`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | repo/URL tool ngoài | có | thứ cần làm workflow |
| In | `--name <prefix>` / `--humanize` | không | chế độ đặt tên (mặc định `dym-<repo>`) |
| In | bản tích hợp thật trên máy | không | có thì thắng fixture trong clone |
| Out | `.overstack/doyourmagic/<repo>/skills/<hub>/SKILL.md` + `<hub>-<slug>/SKILL.md` | có | hub có `domains:`; mọi skill `disable-model-invocation: true` |
| Out | `workflows.md` + `flow.html` | có | bảng kiểm chứng (khẳng định → file:dòng / ca chạy / rc); flow mở thật trước khi giao |
| Out | verdict adapt-modes | có | HÒA TAN · KÉO NGOÀI · NHÚNG-SỞ-HỮU · KHÔNG LẤY |

### Rules và capabilities
- RULE-01 (MUST): Không paraphrase README thành "runnable" — mỗi lệnh phải có trong manifest scripts / `--help` thật / argument parser.
- RULE-02 (MUST): Không giả định mã thoát 0/1 — đọc literal exit; tool có thể dùng 2 = "có finding" hay fail-open 0 khi thiếu file, người gọi phải rẽ nhánh đúng.
- RULE-03 (MUST): Không bê `.github/workflows/*.yml` của tool vào skill CI cho người tiêu thụ — viết ví dụ tối giản riêng.
- RULE-04 (MUST): Lệnh chat và lệnh shell không chung một skill.
- RULE-05 (MUST): **Không chạy installer của tool mà không pin scope** (đo 2026-09-04: `npx impeccable install --help` cài thật vào `$HOME` 13 thư mục). Sandbox + `HOME` cô lập + cờ scope tường minh.
- RULE-06 (MUST): Read-only với clone; chỉ ghi vào `.overstack/doyourmagic/<repo>/`.
- RULE-07 (MUST): Mỗi sub-skill tự chứa; hub chỉ đọc đúng file được gọi — không nhồi cả bundle vào context.
- RULE-08 (MUST): `flow.html` tự chứa (không CDN, không path tuyệt đối cục bộ), đọc được cả sáng/tối, mở qua `file://`.
- RULE-09 (MUST): Ưu tiên bằng chứng chạy thật hơn trích dẫn; cái gì chưa chạy được thì ghi "chưa kiểm chứng" ngay tại chỗ.
- Capabilities: clone + đọc repo ngoài trong sandbox cô lập; chạy lệnh của tool với scope pin; ghi chỉ dưới `.overstack/doyourmagic/<repo>/`; mở trang HTML bằng trình duyệt để verify; (tuỳ) đẩy bundle lên kho chung qua công cụ đồng bộ + PR.

### Failure boundaries
- Lệnh không đối chiếu được với code/`--help`/chạy thật → không viết như "runnable"; ghi **"chưa kiểm chứng"** tại chỗ (partial).
- Installer không pin được scope → **blocked** cho ca đó, không chạy.
- `--humanize` trùng tên skill có sẵn → rơi về chế độ mặc định và nói rõ.
- Kho `rheinmir/dym` đã có bundle của repo → kéo về thay vì chạy lại (**clarify** với user nếu muốn chạy lại).
- Verdict HÒA TAN/NHÚNG → **dừng hỏi** trước khi scaffold.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | effect | repo | Clone vào sandbox (bước 1); xem `rheinmir/dym` đã có bundle chưa | clone read-only | đã có bundle → B03 |
| W02 | deterministic | clone | Manifest trước, README là giả thuyết, đối chiếu parser/`--help`/exit thật (bước 2–3) | danh sách lệnh đã đối chiếu | không đối chiếu được → "chưa kiểm chứng" |
| W03 | effect | lệnh | Chạy thật trong sandbox, scope pin; đọc bản tích hợp thật nếu có (bước 4–5) | rc từng ca | không pin được scope → bỏ ca đó |
| W04 | judgment | kết quả | Chia workflow theo đối tượng, chốt tên (bước 6–7) | danh sách hub/slug | trùng tên `--humanize` → mặc định |
| W05 | effect | workflow | Viết sub-skill + hub + `workflows.md` (bước 8–10) | bundle trên đĩa | `dym-sync.py lint` đỏ → sửa |
| W06 | effect | bundle | Sinh `flow.html` theo `docs-site-macos`, mở thật bằng trình duyệt (bước 11) | flow.html đã verify | lỗi hiển thị → sửa, mở lại |
| W07 | judgment | bundle | Gate adapt-modes: MỘT verdict (bước 12) | verdict | HÒA TAN/NHÚNG → hỏi trước khi scaffold |

Chi tiết từng bước (nguồn chân lý cho W01–W07):

1. **Clone vào sandbox** (scratch dir) — không khám phá tại chỗ trong cây dự án của user. Exploration là **read-only** với clone.
2. **Manifest trước, prose sau**: tìm `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` / installer script TRƯỚC khi đọc README — nó cho lệnh cài thật, entry point/bin, danh sách script.
3. **README/AGENTS.md/docs là giả thuyết**, không phải sự thật. Mỗi lệnh định viết ra phải đối chiếu với argument parser / `--help` chạy thật / literal `process.exit(...)` `sys.exit(...)` — đọc mã thoát thật, đừng giả định 0/1.
4. **Chạy thật những gì chạy được** trong sandbox với scope pin chặt (`HOME` cô lập, `--scope=project`, `--no-verify`…): installer, validator trên input bẩn/sạch, mode lạ, file thiếu. Ghi rc từng ca — bảng kiểm chứng của `workflows.md` lấy từ đây.
5. **Nếu máy đã có một bản tích hợp thật** (config đã commit ở dự án khác) → đọc nó; nó thắng fixture trong clone về "dùng đúng ngoài đời trông thế nào". Tái hiện lỗi trên bản thật là bằng chứng mạnh nhất.
6. **Chia workflow theo ĐỐI TƯỢNG, không theo tính năng**: tiêu thụ (dùng tool trong dự án của mình) vs đóng góp (sửa chính tool). Lệnh chat (`/x`) và lệnh shell tách skill riêng — trộn là copy-paste gãy.
7. **Chốt tên** theo bảng Naming (kiểm trùng nếu `--humanize`).
8. **Viết mỗi workflow thành một sub-skill** `.overstack/doyourmagic/<repo>/skills/<hub>-<slug>/SKILL.md`:
   - frontmatter `name: <hub>-<slug>`, `description` = một câu nói KHI NÀO gọi + từ khoá trigger, và **`disable-model-invocation: true`** — để khi cài cả bundle qua `npx skills add` (7 skill) cũng không có dòng description nào tự nhồi vào context; chỉ nạp khi gõ.
   - `## When to use` — tình huống + "tại sao chạy / sinh ra gì".
   - `## Steps` — lệnh copy-paste được, đường dẫn chính xác, output/mã thoát kỳ vọng. Lệnh nào đã chạy thật thì ghi rc đo được.
   - `## Rules` — bẫy đã ĐO (không phải đoán), kèm cách né; carve-out "không được làm".
   - Self-contained: không trỏ tới file chỉ có trong clone; cần thì "nếu file X có mặt thì…".
9. **Viết hub** `.overstack/doyourmagic/<repo>/skills/<hub>/SKILL.md`:
   ```
   ---
   name: <hub>
   disable-model-invocation: true
   domains: [<domain-1>, <domain-2>]      # bắt buộc — /dym định tuyến theo đây (chart · frontend · diagram · security · …)
   source: <url repo gốc>
   description: "<một dòng: tool gì · gõ /<hub> <slug> · slugs: a · b · c>"
   ---
   ## Steps
   1. Đọc ARGUMENTS → <slug>. Không có slug → in bảng slug + một dòng mục đích, dừng.
   2. Tìm file con theo thứ tự, lấy file ĐẦU TIÊN tồn tại rồi đọc ĐÚNG MỘT file:
      (1) `.claude/skills/<hub>-<slug>/SKILL.md` — đã cài qua `npx skills add rheinmir/dym`;
      (2) `.overstack/doyourmagic/<repo>/skills/<hub>-<slug>/SKILL.md` — bundle nằm trong dự án, hub symlink;
      (3) `doyourmagic-bundles/<repo>/skills/<hub>-<slug>/SKILL.md` — clone `rheinmir/dym` cạnh dự án.
      Làm theo Steps/Rules của file đó; không đọc file con khác; không thấy cả 3 → nói rõ, dừng.
   ```
10. **`workflows.md`**: bảng (skill · mục đích · nhánh · lệnh gọi), "thứ tự chạy đề xuất", "bẫy đắt nhất", bảng **"kiểm chứng thế nào"** (khẳng định → file:dòng / ca chạy thật / rc), chế độ đặt tên đã dùng, và **lệnh symlink 1 dòng** (mục Install bên dưới).
11. **`flow.html`** — sinh theo skill `docs-site-macos` (BẮT BUỘC: sidebar kính, background orbs, mind map collapsible, nút gạt sáng/tối ở footer sidebar + chống FOUC, cỡ chữ compact 13″, skip-link/focus ring, footer hiện **đường dẫn tuyệt đối** của chính file). Nội dung = **luồng chính xác các skill thực hiện**: mỗi skill một node, cạnh `skill → sản phẩm → skill kế` (connector do JS vẽ từ `getBoundingClientRect`, vẽ lại khi resize — không hardcode toạ độ), thứ tự chạy theo nhánh, mỗi node ghi lệnh gọi + sản phẩm + bẫy 1 dòng. Thuật ngữ có giải nghĩa trong ngoặc. **Mở thật bằng trình duyệt** (hoặc `/playwright-verify`) trước khi giao — đọc code không đủ.
12. **Gate adapt-modes** — bundle không phải đích đến. Đưa MỘT verdict cho user: **HÒA TAN** (rewrite thành code/skill của ta) · **KÉO NGOÀI** (pointer + pin) · **NHÚNG-SỞ-HỮU** (vendor) · **KHÔNG LẤY** (đã có gì phủ, ghi path). So trên trục quyết định chi phí — số lượt agent/lần dùng, code sinh được không cần LLM — không so byte. Verdict HÒA TAN/NHÚNG → hỏi trước khi scaffold.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | user_optional | `--name <prefix>` hoặc `--humanize` | đặt tên theo bảng Naming; `--humanize` phải kiểm trùng trước | trùng → rơi về mặc định, nói rõ | W05 |
| B02 | capability_optional | máy đã có bản tích hợp thật (config commit ở dự án khác) | đọc nó, ưu tiên hơn fixture trong clone; tái hiện lỗi trên bản thật | không có → bỏ qua | W04 |
| B03 | conditional_required | `rheinmir/dym` đã có bundle của repo | kéo về (`npx skills add rheinmir/dym` hoặc clone) thay vì chạy lại | user muốn chạy lại → W02 | kết thúc |
| B04 | user_optional | sau khi bundle xong, muốn chia sẻ/dùng | `dym-sync.py` lint/index/install/check/push; hoặc symlink hub tại chỗ; hoặc promote sub-skill lên repo chính | thiếu `gh` → push dừng | kết thúc |

### Validation và stopping
Bảng "kiểm chứng thế nào" trong `workflows.md`: mỗi khẳng định trỏ về file:dòng / ca chạy thật / rc — thiếu thì ghi "chưa kiểm chứng". `python3 harness/scripts/dym-sync.py lint` xanh (bundle dạng SKILL, hub có `domains:`). `flow.html` phải được mở thật. Dừng ở verdict adapt-modes; scaffold chỉ sau khi user duyệt.

### Examples
- **Positive:** `/doyourmagic https://github.com/Rheinmir/setup` → clone sandbox, đọc installer + `--help` thật, chạy validator trên input bẩn/sạch ghi rc → hub `dym-setup` + 6 sub-skill, `workflows.md` bảng kiểm chứng 30 dòng, `flow.html` mở thật → verdict (xem `references/example-setup/`).
- **Boundary/failure:** tool có `npx <tool> install` mà `--help` không liệt kê cờ scope → không chạy installer (cài thật vào `$HOME`), sub-skill ghi "chưa kiểm chứng" cho lệnh cài kèm bẫy đã biết.

### Reference — Output shape (what a finished run leaves behind)
```
.overstack/doyourmagic/<repo>/
  workflows.md                  # chỉ mục + thứ tự chạy + bảng "kiểm chứng thế nào" (thứ không thuộc về một skill nào)
  flow.html                     # docs-site-macos: sidebar · mind map · SƠ ĐỒ LUỒNG skill→sản phẩm→skill kế · toggle sáng/tối
  skills/
    <hub>/SKILL.md              # /<hub> <slug> — 1 dòng description, disable-model-invocation, đọc ĐÚNG file con được gọi
    <hub>-<slug-1>/SKILL.md     # mỗi workflow = một skill đầy đủ (frontmatter + When/Steps/Rules), tự chứa, promote được
    <hub>-<slug-2>/SKILL.md
```
- **Hub** là thứ duy nhất được symlink vào `.claude/skills/` → context chỉ tốn **một** dòng description; thân workflow con chỉ được đọc khi user gõ `/<hub> <slug>`. Đây là "hub 1-tên, mô tả phạm vi" của `/fdk`, không phải N skill rải trong context.
- Sub-skill là **SKILL.md thật** (không phải doc): copy nguyên thư mục sang `skills/` của repo chính là thành skill cài bằng `npx skills add`.
- Không còn `NN-*.md`: nội dung runnable nằm trong Steps của sub-skill — một nguồn, không có bản doc song song để drift.

### Reference — Naming — 3 chế độ, ghi chế độ đã dùng vào `workflows.md`
| Chế độ | Hub | Sub-skill | Khi nào |
|---|---|---|---|
| **mặc định** | `dym-<repo>` | `dym-<repo>-<slug>` | user không nói gì. Không bao giờ trùng, nhìn tên biết nguồn; đổi tên lúc promote |
| `--name <prefix>` | `<prefix>` | `<prefix>-<slug>` | user tự đặt |
| `--humanize` | agent đặt tên ngắn gõ được bằng cơ bắp (vd `overstack`) | `<hub>-<slug>` | phải `ls ~/.claude/skills .claude/skills` kiểm trùng TRƯỚC khi chốt; trùng → rơi về mặc định và nói rõ |
`<repo>` = tên repo (segment cuối của URL, bỏ `.git`), chữ thường, `-` thay ký tự lạ. `<slug>` = 1–2 từ nói việc (`install`, `ci`, `contributor`), không đánh số.

### Reference — Đồng bộ + định tuyến — `harness/scripts/dym-sync.py` (stdlib, 0 token)
```bash
S=harness/scripts/dym-sync.py
python3 $S lint                       # mọi bundle phải ở DẠNG SKILL (hub có `domains:`); dạng cũ NN-*.md → `migrate <repo> --domains chart,report`
python3 $S index                      # sinh meta-hub .overstack/doyourmagic/dym/SKILL.md: bảng domain → hub → slug
python3 $S install [dym|<repo>] [--auto slug,slug]   # symlink vào .claude/skills; --auto = bỏ disable-model-invocation, agent tự nạp theo description
python3 $S check [--yes]              # đĩa ↔ baseline ↔ dym: NEW-LOCAL/SAME/LOCAL/REMOTE-AHEAD/CONFLICT; hỏi y/N rồi push. Hook Stop tự nhắc khi phiên đụng bundle.
python3 $S push <repo> [--yes]        # copy vào clone dym → nhánh dym/<repo> → PR (gh); ghi .dym-baseline.json
```
Hub bắt buộc khai `domains: [a, b]` trong frontmatter — `/dym` (1 dòng context, model-invocable) đọc bảng domain để tự chọn bundle: chart → lieflat-charts, frontend → impeccable… Hub và sub-skill vẫn `disable-model-invocation`, chỉ nạp khi được gọi.

### Reference — Kho bundle đã chạy — `rheinmir/dym`
Mỗi lượt chạy xong, `dym-sync.py push <repo>` đẩy `.overstack/doyourmagic/<repo>/` lên https://github.com/Rheinmir/dym thành `<repo>/` (PR) để người sau **kéo về thay vì chạy lại**: `npx skills add rheinmir/dym` (cài hub + sub-skill, project-scope; thêm `-g` cho global) hoặc `git clone --depth 1 https://github.com/Rheinmir/dym.git doyourmagic-bundles`. Trước khi chạy `/doyourmagic <repo>` mới: **xem ở đó đã có bundle chưa**.

### Reference — Install (dùng tại chỗ) — một lệnh, chỉ nạp khi cần
```bash
mkdir -p .claude/skills && ln -sfn ../../.overstack/doyourmagic/<repo>/skills/<hub> .claude/skills/<hub>
```
Chỉ hub vào context. Gõ `/<hub>` để xem bảng slug, `/<hub> <slug>` để chạy một workflow. Muốn gọi thẳng `/<hub>-<slug>` thì symlink thêm đúng thư mục đó — mỗi symlink thêm là thêm một dòng context, cân nhắc.

### Reference — Promote lên repo chính (skill cài bằng npx)
Đường `/fdk` có sẵn, không đẻ tool:
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/fdk/tools/fdk-kit.sh) pull   # lần đầu
cp -R .overstack/doyourmagic/<repo>/skills/<hub>-<slug> .overstack/kit/skills/<tên-mới>          # đổi tên nếu bỏ tiền tố dym-
cd .overstack/kit && python3 fdk/tools/new-skill.py <tên-mới> --dry-run                # in checklist register
# register: LOOP_MAP (sync-skills.py) · LOOP_GROUPS · marketplace.json · bảng AGENT.md+CLAUDE.md · provenance
bash fdk/tools/fdk-kit.sh check && bash fdk/tools/fdk-kit.sh submit skill/<tên-mới> "<mô tả>"
```
Sửa `name:` trong frontmatter cho khớp tên mới; giữ `description` trigger. Hub KHÔNG promote (nó chỉ có nghĩa cạnh bundle).

### Reference example
`references/example-setup/` — một lượt chạy thật của skill này trên `rheinmir/setup` (overstack: bootstrap + 19 luật + 87 skill): hub `dym-setup` + 6 sub-skill (file con lưu dạng `<tên>.skill.md` để không bị loader quét nhầm thành skill), `workflows.md` với bảng kiểm chứng 30 dòng, `flow.html`. Lượt đó tìm ra 5 lỗi thật (đã vá ở PR #114–#117) — đó là mức "kiểm chứng" cần khớp.
