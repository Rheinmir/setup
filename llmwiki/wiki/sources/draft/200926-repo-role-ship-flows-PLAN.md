---
type: draft
title: "PLAN — (việc 1) nhãn repo_role để /ship và installer đi đúng luồng framework · module · downstream · foreign; (việc 2) font mặc định Lexend Deca Light cho mọi HTML framework sinh ra; kèm theo: đóng 2 gốc lỗi luồng cài engine"
status: proposed
tags: [plan, orca-graph, ship, repo-role, installer, harness-update, uat, font, lexend-deca, html]
timestamp: 2026-09-20
---

# PLAN 200926 — repo_role cho /ship · font Lexend Deca Light · (kèm theo) hai gốc lỗi luồng cài

User giao HAI việc qua `/orca-graph` ngày 20/09/2026. **Việc 1** (Task 1–4): `/ship` phải phân biệt được đang đứng ở repo nào. **Việc 2** (Task 9–12): mọi file HTML do framework sinh ra dùng font mặc định **Lexend Deca Light** cho phần nội dung. Task 5–7 là phần tôi đề xuất KÈM THEO vì chung gốc với việc 1 (công cụ không biết mình ở loại repo nào); user chưa yêu cầu, cắt được mà không ảnh hưởng hai việc chính — khi đó Task 8 chỉ bỏ hai cạnh tương ứng.

Bối cảnh: ngày 20/09/2026 engine orca-graph tách sang repo riêng. Ngay sau đó lộ ba chuyện cùng một gốc là "công cụ không biết mình đang đứng ở loại repo nào". Thứ nhất, installer chạy nhầm trong repo framework và ghi đè `.github/workflows/harness.yml` cùng `.claude/settings.json`. Thứ hai, `/ship` chỉ có một luồng, viết cho repo framework (`medic --ci`, `ci-local`, `capability-stamp`), nên khi ship repo engine phải tự nhớ một quy trình khác hẳn, và đã hai lần đẩy trước khi đọc kết quả gate. Thứ ba, bảng liệt kê luồng cài/cập nhật cho thấy shim đi theo bốn đường copy engine còn việc kéo engine thật chỉ nằm ở một đường, nên `/harness-update` làm hỏng `/orca-graph`, mà không cổng nào phát hiện.

Ngoài phạm vi (nói thẳng): tín hiệu "engine có bản mới" ở đầu phiên (luồng B5, B7), chính sách gỡ `~/.orca-graph` khi uninstall (C7), tương thích hai máy khác bản engine trên cùng store (C8), checklist trên Windows thật (A5). Các mục này ghi vào bảng luồng, chưa làm trong PLAN này.

## Global constraints
- Nhãn là KHAI BÁO, đặt ở `.overstack.yaml` khoá `repo_role:` với đúng bốn giá trị `framework | module | downstream | foreign`. Suy luận theo hình dạng thư mục chỉ dùng khi thiếu nhãn, và kết quả suy luận phải được hỏi lại user một lần rồi ghi thành nhãn.
- Repo `foreign`: công cụ của ta KHÔNG ghi file cấu hình nào vào đó, kể cả `.overstack.yaml`. Nhãn cho repo này lưu ở máy (`~/.claude/harness/repo-roles.json`), khoá theo remote URL.
- `/ship` luôn in dòng đầu `repo_role=<role> (<khai báo|suy luận|ép tay>)` trước mọi gate, và dừng chờ duyệt trước side-effect như hiện nay.
- Installer gặp `repo_role: framework` (hoặc suy ra framework) thì dừng với thông báo rõ, không ghi file nào; chỉ chạy tiếp khi có cờ `--i-know-this-is-the-framework`.
- Kéo engine orca-graph nằm ở ĐÚNG chỗ copy shim (`install-harness.sh --global`); `install.sh` chỉ giữ phần hỏi và truyền quyết định xuống bằng `ORCA_GRAPH_SKIP`.
- Đường dẫn xuống máy khách không ghi cứng `llmwiki/` hay `harness/` (bare-path-lint); test cài đặt cô lập `HOME` và `ORCA_GRAPH_HOME`, không để lại daemon.
- Gate phải được ĐỌC trước khi đẩy: mọi lệnh push trong PLAN này đứng sau một lệnh in rc của gate, không nối bằng `;`.
- Không AI-attribution trong commit (R15).
- Font (việc 2): MỘT nguồn token duy nhất cho framework (`fdk/tools/html_font.py`); generator import nó, không chép chuỗi font. Phần NỘI DUNG (`--font-text`, và `--font-display` cho tiêu đề) là `'Lexend Deca'` weight 300; `--font-mono` cho code GIỮ NGUYÊN. Luôn có fallback hệ thống phía sau để trang không vỡ khi font chưa nạp. Tiếng Việt phải hiển thị đủ dấu (Lexend Deca có bộ glyph Vietnamese — subset phải giữ nó).
- Trang framework sinh ra mở bằng `file://`, nhiều trang phải đọc được KHÔNG CẦN MẠNG → **user chốt 20/09/2026 ở cổng duyệt: NHÚNG HẾT** (mọi trang nhúng woff2 base64, không `<link>` ra ngoài). Đo thật: subset latin + vietnamese (449 glyph) giữ trục weight 300–700 = 36,6 KB woff2 = 48,9 KB base64 mỗi trang; bản chỉ-300 là 23,7 KB nhưng chữ đậm/tiêu đề sẽ bị giả đậm nên không chọn. Nguồn font: file OFL đã cài trên máy (`LexendDeca-VariableFont_wght.ttf`) — `fonts.googleapis.com` bị egress-guard chặn, không lách. User cũng chốt GIỮ Task 5–7.

### Task 1: repo_role.py — đọc nhãn, suy luận có bằng chứng
**Kind:** build
**Thoả:** câu hỏi user 20/09 "cần từ khoá hay đánh nhãn khác nhau cho các repo không" · gốc chung của C1 và lỗi luồng `/ship`
**Depends:** —
**Files:**
- Tạo: `harness/scripts/repo_role.py`
- Tạo: `harness/tests/test_repo_role.py`
**Interfaces:**
- Consumes: —
- Produces: `resolve(root) -> {"role", "source": "declared|inferred|machine", "evidence": [..]}`; CLI `repo_role.py [root] [--json] [--set ROLE]` (dùng bởi Task 2, Task 3, Task 4)
```python
ROLES = ("framework", "module", "downstream", "foreign")
def resolve(root) -> dict:
    # 1) .overstack.yaml: repo_role → source=declared
    # 2) ~/.claude/harness/repo-roles.json theo remote URL → source=machine (dành cho foreign)
    # 3) suy luận, kèm bằng chứng: fdk/wiki/ → framework · upstream_pin trong .overstack.yaml hoặc AGENTS.md có "upstream:" → module
    #    · .llmwiki/.harness-stamp hoặc llmwiki/.harness-stamp (không fdk/wiki) → downstream · còn lại → foreign
    ...
```
**Verify:** `python3 -m pytest -q harness/tests/test_repo_role.py`

### Task 2: gắn nhãn cho các repo đang có + installer ghi nhãn downstream
**Kind:** infra
**Thoả:** Global constraint "nhãn là khai báo"
**Depends:** Task 1 (contract)
**Resources:** installer-files(exclusive)
**Files:**
- Tạo: `.overstack.yaml`
- Sửa: `harness/poc-vendor-neutral/install.sh`
**Interfaces:**
- Consumes: `repo_role.py --set`
- Produces: repo framework khai `repo_role: framework`; repo engine khai `repo_role: module` kèm `upstream_pin: {repo: Rheinmir/setup, file: fdk/skills.provenance.json, key: orca-graph}` (commit ở repo engine); dự án mới cài có `repo_role: downstream` trong `.overstack.yaml` (không đè nếu đã có khoá này)
```yaml
# .overstack.yaml của repo framework
repo_role: framework        # /ship đi luồng framework; installer TỪ CHỐI ghi vào repo này
```
**Verify:** `test "$(python3 harness/scripts/repo_role.py . --json | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d["role"],d["source"])')" = "framework declared"`

### Task 3: /ship rẽ luồng theo repo_role
**Kind:** docs
**Thoả:** yêu cầu user 20/09 "/ship phải phân biệt được các luồng khác nhau: repo develop framework, repo downstream, dự án của người khác"
**Depends:** Task 1 (contract)
**Files:**
- Sửa: `skills/ship/SKILL.md`
- Sửa: `llmwiki/skills/dev-loop/ship.md`
**Interfaces:**
- Consumes: `repo_role.py --json`
- Produces: bước W00 "xác định repo_role, in ra, thiếu nhãn thì hỏi rồi `--set`"; bảng gate theo role; cờ `--as <role>`; luật "đọc rc gate trước khi push, cấm nối `;`"; luồng `module` có bước cuối "re-pin ở framework"; luồng `foreign` chỉ `pr`/`mr`, không `push` nhánh chính
```text
framework : medic --ci → ci-local (trên checkout SẠCH của commit) → [UAT nếu năng lực mới] → capability-stamp --update nếu file xuống máy khách đổi → push
module    : commit → tests + evals + install-test (đọc rc) → bump VERSION/CHANGELOG → push → CI xanh → tag + release → re-pin provenance ở framework
downstream: test của dự án + llmwiki-validate + medic (downstream) → push/pr   · KHÔNG ci-local, KHÔNG stamp, KHÔNG UAT
foreign   : git sạch + test/CI của họ → CHỈ pr/mr · theo luật commit của họ · không ghi cấu hình overstack
```
**Verify:** `grep -q "repo_role" skills/ship/SKILL.md && grep -q "foreign" skills/ship/SKILL.md && python3 fdk/tools/swh-lint.py --ci`

### Task 4: installer từ chối ghi vào repo framework
**Kind:** fix
**Thoả:** luồng C1 (đo thật 20/09 11:10: `harness.yml` −202 dòng, `settings.json` +67 dòng)
**Depends:** Task 1 (data)
**Resources:** installer-files(exclusive)
**Files:**
- Sửa: `harness/poc-vendor-neutral/install.sh`
- Sửa: `harness/scripts/install-harness.sh`
**Interfaces:**
- Consumes: `repo_role.resolve`
- Produces: gặp role `framework` → in lý do + lệnh đúng (`/harness-update` không áp cho repo này) và thoát rc 3 TRƯỚC khi ghi bất cứ file nào; cờ `--i-know-this-is-the-framework` để ép
```bash
ROLE="$(python3 "$SRC/../scripts/repo_role.py" "$ROOT" 2>/dev/null || echo unknown)"
if [ "$ROLE" = framework ] && [ "$FORCE_FRAMEWORK" != 1 ]; then
  warn "đây là REPO FRAMEWORK (repo_role=framework) — installer sẽ ghi đè CI + settings của chính framework. Dừng."; exit 3
fi
```
**Verify:** `bash harness/tests/install-flows-test.sh C1`

### Task 5: kéo engine orca-graph ở đúng chỗ copy shim
**Kind:** fix
**Thoả:** gốc 1 của bảng luồng — đóng A7, B3 (`/harness-update`), B4 (`--all-subrepos`)
**Depends:** —
**Resources:** installer-files(exclusive)
**Files:**
- Sửa: `harness/scripts/install-harness.sh`
- Sửa: `harness/poc-vendor-neutral/install.sh`
**Interfaces:**
- Consumes: `install.sh` của repo engine
- Produces: hàm `ensure_orca_graph` trong nhánh `--global` của `install-harness.sh` — chưa có engine thì kéo, có rồi thì cập nhật, `ORCA_GRAPH_SKIP=1` thì bỏ, fail-open; `install.sh` chạy checklist TRƯỚC khi gọi global và export `ORCA_GRAPH_SKIP` theo lựa chọn; khối kéo ở `install.sh` chỉ còn cho ca `--harness-only`
```bash
ensure_orca_graph() {   # shim vừa được copy ở trên — engine phải tới cùng một chuyến, nếu không /orca-graph chết sau /harness-update
  [ -n "${ORCA_GRAPH_SKIP:-}" ] && { log "  · orca-graph: bỏ qua (ORCA_GRAPH_SKIP)"; return 0; }
  ...
}
```
**Verify:** `bash harness/tests/install-flows-test.sh A7 B3`

### Task 6: cổng kiểm "engine tới nơi" trong smoke và UAT
**Kind:** test
**Thoả:** gốc 2 của bảng luồng — D1, D2, D3 xanh kể cả khi engine không tới
**Depends:** Task 5 (acceptance)
**Files:**
- Sửa: `harness/scripts/fresh-install-smoke.sh`
- Sửa: `skills/fdk-uat/SKILL.md`
- Sửa: `llmwiki/skills/utils/fdk-uat.md`
**Interfaces:**
- Consumes: máy vừa cài theo đường người-mới
- Produces: assert sau cài `python3 <global>/harness/scripts/orca-graph.py --version` rc 0 và in `orca-graph <X.Y.Z>`; ca `--no-graph` thì assert rc 3 kèm lệnh cài; UAT ghi bước này vào checklist
```bash
V="$(HOME="$FXHOME" python3 "$GH/harness/scripts/orca-graph.py" --version 2>&1)"; case "$V" in orca-graph\ [0-9]*) ok "engine tới nơi ($V)";; *) bad "engine KHÔNG tới: $V";; esac
```
**Verify:** `bash harness/scripts/fresh-install-smoke.sh --local`

### Task 7: install-flows-test — mỗi ô của bảng luồng là một ca
**Kind:** test
**Thoả:** yêu cầu user 20/09 "tránh việc này cứ xảy ra mãi, list ra hết các luồng"
**Depends:** Task 4 (acceptance), Task 5 (acceptance), Task 13
**Resources:** ci-workflow(exclusive)
**Files:**
- Tạo: `harness/tests/install-flows-test.sh`
- Sửa: `.github/workflows/harness.yml`
**Interfaces:**
- Consumes: installer sau Task 4, Task 5
- Produces: ca `A3 A7 B1 B3 B4 C1` chạy kín mạng trong HOME cô lập (engine lấy từ bản cài local), gọi được từng ca theo tên; không ca nào để lại daemon hay ghi registry thật; step CI tương ứng
```bash
bash harness/tests/install-flows-test.sh            # mọi ca
bash harness/tests/install-flows-test.sh B3         # chỉ ca /harness-update: engine v2 → shim + engine v3 cùng tới
```
**Verify:** `bash harness/tests/install-flows-test.sh`

### Task 8: bảng luồng thành trang wiki + review + ship
**Kind:** release
**Thoả:** AGENT.md "wiki chỉ cập nhật sau khi code xong" · Global constraint "đọc gate trước khi đẩy"
**Depends:** Task 2 (data), Task 3 (acceptance), Task 6 (acceptance), Task 7 (acceptance), Task 12 (acceptance)
**Files:**
- Tạo: `fdk/wiki/concepts/install-update-flows.md`
- Sửa: `fdk/wiki/index.md`
- Sửa: `fdk/wiki/log.md`
**Interfaces:**
- Consumes: kết quả Task 1–7
- Produces: trang concept giữ bảng A/B/C/D (mỗi ô trỏ ca test hoặc ghi "chưa làm, vì sao"); review độc lập phần installer; ship bằng chính luồng `framework` mới của `/ship`
```bash
python3 harness/scripts/repo_role.py . --json      # /ship in dòng này đầu tiên
python3 fdk/tools/medic.py --ci; echo "medic rc=$?"   # ĐỌC rồi mới chạy lệnh kế
```
**Verify:** `test -s fdk/wiki/concepts/install-update-flows.md && grep -q "install-update-flows" fdk/wiki/index.md`

### Task 9: html_font.py — một nguồn token font + cách nạp Lexend Deca Light
**Kind:** build
**Thoả:** việc 2 user giao 20/09: "toàn bộ font chữ mặc định cho nội dung file html sinh ra nhờ framework là Lexend Deca Light"
**Depends:** —
**Mode:** HITL
**Files:**
- Tạo: `fdk/tools/html_font.py`
- Tạo: `harness/tests/test_html_font.py`
**Interfaces:**
- Consumes: quyết định user về cách nạp font — (a) `<link>` Google Fonts + fallback hệ thống: nhẹ, nhưng mở offline thì rơi về font hệ thống; (b) nhúng woff2 subset latin + vietnamese dạng base64 vào từng trang: tự chứa, offline vẫn đúng font, mỗi trang nặng thêm cỡ vài chục KB (số thật đo ở bước này); (c) lai: nhúng cho trang framework tự sinh, link cho trang do skill/agent sinh
- Produces: `FONT_TEXT`, `FONT_DISPLAY`, `FONT_MONO` (chuỗi font-family), `head_css(mode)` trả khối `<link>`/`@font-face` + `:root{--font-text:…;--font-display:…}`, hằng `WEIGHT_TEXT = 300` (dùng bởi Task 10, Task 11, Task 12)
```python
FONT_TEXT = "'Lexend Deca',-apple-system,BlinkMacSystemFont,'Segoe UI','Roboto','Helvetica Neue',sans-serif"
WEIGHT_TEXT = 300            # Light
def head_css(mode: str = "link") -> str:   # mode ∈ link | inline — theo quyết định user ở cổng duyệt
    ...
```
**Verify:** `python3 -m pytest -q harness/tests/test_html_font.py`

### Task 10: áp token font vào mọi generator HTML của framework
**Kind:** build
**Thoả:** việc 2 — phần trang do CODE của framework sinh
**Depends:** Task 9 (contract)
**Files:**
- Sửa: `fdk/tools/build-overstack-docs.py`
- Sửa: `fdk/tools/build-docs-index.py`
- Sửa: `fdk/tools/build-health-dashboard.py`
- Sửa: `fdk/tools/build-line-status.py`
- Sửa: `fdk/tools/build-wiki-graph.py`
- Sửa: `fdk/tools/build-control-room.py`
- Sửa: `fdk/tools/br-contract.py`
- Sửa: `fdk/tools/council.py`
**Interfaces:**
- Consumes: `html_font.head_css`, `FONT_TEXT`
- Produces: mọi generator lấy font từ `html_font` (không còn chuỗi `-apple-system,…` chép tay cho phần nội dung); `body{font-weight:300}`; chữ đậm/tiêu đề giữ tương phản (strong ≥ 500); regen lại các trang đang track
```python
from html_font import head_css, FONT_TEXT   # nạp qua importlib như các tool khác nếu chạy từ global harness
CSS = head_css(MODE) + CSS.replace(OLD_TEXT_STACK, "var(--font-text)")
```
**Verify:** `python3 fdk/tools/build-overstack-docs.py >/dev/null && grep -q "Lexend Deca" llmwiki/html/overstack.html && python3 fdk/tools/medic.py --ci`

### Task 11: áp font vào engine graph-viz (repo module) và template của skill
**Kind:** build
**Thoả:** việc 2 — phần trang do ENGINE ở repo riêng và do SKILL/agent sinh
**Depends:** Task 9 (contract)
**Files:**
- Sửa: `skills/docs-site-macos/SKILL.md`
- Sửa: `llmwiki/skills/utils/docs-site-macos.md`
- Sửa: `skills/orca-onboard/assets/docs-site-skeleton.html`
- Sửa: `fdk/skills.provenance.json`
**Interfaces:**
- Consumes: giá trị token của Task 9 (repo engine KHÔNG import được từ framework → chép HẰNG SỐ, ghi rõ nguồn; đổi ở framework thì test của Task 12 bắt lệch)
- Produces: `engine/graph-viz.py` của `Rheinmir/orca-graph` dùng cùng `--font-text` + weight 300 (commit, test, tag ở repo engine theo luồng `module`, rồi re-pin provenance ở đây); template `docs-site-macos` và skeleton `orca-onboard` khai token mới nên trang agent dựng từ đó cũng ra Lexend Deca Light. NGOÀI phạm vi, nói thẳng: `hallmark`/`prd-grade-fe` sinh UI SẢN PHẨM theo `design.md` của từng dự án — không ép font framework lên đó
```css
:root{ --font-text:'Lexend Deca',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; --font-display:var(--font-text); }
body{ font-family:var(--font-text); font-weight:300; }
```
**Verify:** `grep -q "Lexend Deca" skills/docs-site-macos/SKILL.md && grep -q "Lexend Deca" "$HOME/.orca-graph/repo/engine/graph-viz.py" && python3 fdk/tools/swh-lint.py --ci`

### Task 12: cổng html-font-lint + nghiệm thu bằng mắt
**Kind:** test
**Thoả:** việc 2 — "toàn bộ" phải được GÁC, không dựa vào nhớ; luật repo: HTML phải có toggle sáng/tối, không vỡ layout
**Depends:** Task 10 (acceptance), Task 11 (acceptance)
**Resources:** ci-workflow(exclusive)
**Files:**
- Tạo: `fdk/tools/html-font-lint.py`
- Tạo: `harness/tests/html-font-lint-test.sh`
- Sửa: `.github/workflows/harness.yml`
**Interfaces:**
- Consumes: mọi `.html` framework sinh ra đang track + hằng số trong engine
- Produces: lint rc 2 khi một trang framework sinh không khai `'Lexend Deca'` cho `--font-text`/`body`, hoặc hằng số ở engine lệch `html_font.FONT_TEXT`; ảnh chụp Playwright 3 trang (overstack, 1 graph, control-room) ở cả sáng và tối, kiểm chữ Việt đủ dấu, weight 300 không làm chữ xám trên nền tối kém tương phản (đo contrast AA)
```bash
python3 fdk/tools/html-font-lint.py <trang.html …>      # rc 2 + tên trang thiếu font (đặt ở fdk/tools, không ở harness/validators: nó không phải rule của policy.yaml)
```
**Verify:** `bash harness/tests/html-font-lint-test.sh`

### Task 13: harness-update đi đúng đường v4: cập nhật GLOBAL qua bootstrap, không chép engine vào dự án dot-layout
**Kind:** fix
**Thoả:** câu hỏi user 20/09 "cơ chế update qua installer thì sao?" · luồng B3 — đo thật: `install-harness.sh . --self-heal` trên máy 1.3.109 KHÔNG cập nhật global và chép 77 script vào dự án (node thêm bằng `add-node` giữa lúc chạy)
**Depends:** Task 5 (data)
**Files:**
- Sửa: `skills/harness-update/SKILL.md`
- Sửa: `llmwiki/skills/utils/harness-update.md`
- Sửa: `harness/scripts/install-harness.sh`
**Interfaces:**
- Consumes: —
- Produces: per-project mode gặp dự án dot-layout (.llmwiki/.harness-stamp) thì DỪNG rc 3 + chỉ lệnh bootstrap; skill /harness-update gọi bootstrap (refresh global + engine + stamp) rồi mới self-heal nợ wiki
**Resources:** installer-files(exclusive)
```bash
# install-harness.sh, trước mục "1. Detect mode":
if [ -f "$ROOT/.llmwiki/.harness-stamp" ] && [ ! -d "$ROOT/fdk/wiki" ]; then warn "DỪNG — dự án dot-layout: cập nhật qua BOOTSTRAP"; exit 5; fi
```
**Verify:** `bash harness/tests/install-flows-test.sh B3`

## Origin

- Việc 2, tin nhắn user cùng lượt: "toàn bộ font chữ mặc định cho nội dung file html sinh ra nhờ framework để font mặc định là font Lexend Deca Light". Khảo sát trước PLAN: token `--font-text/--font-display/--font-mono` định nghĩa rải ở 7 generator `.py`, `engine/graph-viz.py`, template `docs-site-macos`, skeleton `orca-onboard`; chưa chỗ nào dùng Lexend.
- Câu hỏi user ngày 20/09/2026 qua `/orca-graph`: "/ship lên remote phải phân biệt được các luồng khác nhau (repo develop framework, repo downstream, dự án của người khác) — cần từ khoá hay đánh nhãn cho các repo không".
- Bảng luồng cài/cập nhật A1–D5 lập cùng ngày trong phiên, sau khi tái hiện `install-harness.sh --global` để lại shim không có engine.
- Sự cố đo thật cùng ngày: installer ghi đè `harness.yml` và `settings.json` của repo framework lúc 11:10:55; hai lần push trước khi đọc kết quả gate (`c83b065`, tag `v3.0.1`).
- PLAN cùng dòng: `200926-orca-graph-v3-PLAN`.
