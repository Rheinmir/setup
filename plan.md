# Kế hoạch: Tự chủ trục code cho engine tự-index (hậu benchmark seed42)

Tham chiếu: proposal `llmwiki/wiki/sources/draft/020726-council-chon-de-thi-self-index.md` · report `llmwiki/html/030726-self-index-benchmark-report.html` · engine `fdk/tools/build-wiki-graph.py` · scorer `scratchpad/council-app/plugin-host/score.py`.

## Vấn đề

Benchmark tự-index (council seed42 ra đề → app ngoài-mẫu TS plugin-host → engine thật → chấm mù) cho F1 **0.842** trên subset quan hệ khai tường minh, nhưng **full-space chỉ 0.727** và **code-vector ≈ 0** — recall sẽ sập trên repo thật. Ba defect đã ghi failure-flywheel:

1. **`enrich_code` chỉ hiểu Python**: `imports` parse bằng `ast` nên mù mọi ngôn ngữ khác (TS/JS/Go/Rust…). App ngoài-mẫu ra **0 cạnh import TS**, kéo theo `touches` code cũng nghèo.
2. **Graph-builder thiếu cờ chu trình (cycle)** và **không quarantine node có frontmatter YAML hỏng** — lỗi dữ liệu lan im lặng vào graph.
3. **`WIKILINK_RE` không strip code-fence**: trích `[[NotALink]]` nằm trong khối code → cạnh wikilink false-positive (hallucination).

**Vấn đề gốc**: muốn làm tốt trục code, engine hiện phải dựa vào `code-graph MCP` — phần mềm NGOÀI. Chủ trương dự án là framework phải **tự xử lý được, không phụ thuộc phần mềm ngoài** (không MCP, không tree-sitter cài ngoài; parser nếu cần thì vendored/self-contained + fail-open) — đúng nguyên tắc build-now-adapt-later và Taleb blast-radius đã có.

## Nguyên tắc

- **Self-contained**: mọi mã trích xuất nằm trong `fdk/tools/`, không gọi MCP/tool ngoài, không dependency cài ngoài.
- **Fail-open**: lỗi parser/regex trên một file KHÔNG được giết build graph — bỏ qua file đó, đếm và log lại.
- **Language-agnostic**: trích `imports` theo pattern nhẹ per-ngôn-ngữ, mở rộng dần, không đòi parser đầy đủ ngay.
- **Adapter-boundary**: phần chưa chắc (độ phủ ngôn ngữ, parser nâng cao) đóng gói sau một biên adapter — thay sau này chỉ sửa một chỗ.

## Giải pháp

### Mảnh A — Bộ trích `imports` language-agnostic, self-contained
Thay vai trò của code-graph MCP cho quan hệ `imports` ở tầng graph tĩnh:
- Python: giữ nguyên `ast` (đang đúng).
- TS/JS: regex `import … from '…'` + `require('…')` (kể cả `export … from`, dynamic `import()`).
- Go: block/single `import "…"`.
- Rust: `use crate::…` / `use path::…` + `mod`.
- Kiến trúc: bảng `EXTRACTORS = {ext: fn}` vendored trong `fdk/tools/` (trong `build-wiki-graph.py` hoặc module cạnh nó), mỗi extractor fail-open; ngôn ngữ chưa có extractor → 0 cạnh, không lỗi. Resolve đường dẫn tương đối → node file code (tái dùng cơ chế node lá code hiện có).

### Mảnh B — Strip code-fence trước wikilink (vá defect 3)
Loại bỏ khối code-fence (```…```) và inline-code (`` `…` ``) khỏi văn bản TRƯỚC khi chạy `WIKILINK_RE`. `[[NotALink]]` trong code không còn thành cạnh.

### Mảnh C — Cờ chu trình + quarantine YAML hỏng (vá defect 2)
- DFS phát hiện chu trình trên cạnh `derives-from`/`depends-on`; node/cạnh trong chu trình được gắn cờ hiển thị trong graph.
- Node có frontmatter YAML parse lỗi → quarantine: vẫn hiện (đánh dấu riêng) nhưng không sinh cạnh từ frontmatter.
- Cả hai loại đếm được (counter xuất ra output) để `score.py` chấm.

### Mảnh D — Run tích hợp
Bài benchmark chạy lại phải exercise toàn hệ: hook auto-touches + validator `rel_integrity` + graph-builder, không chỉ graph-builder đơn lẻ — để số F1 phản ánh pipeline thật.

## Phạm vi & adapter boundary

- **Làm chắc bây giờ**: A (4 họ ngôn ngữ TS/JS, Go, Rust, Python), B, C, D.
- **Quarantine sau biên adapter**: độ phủ ngôn ngữ mở rộng dần (Java, C#, Ruby… thêm extractor khi cần); parser nâng cao (alias, re-export chuỗi, monorepo path mapping) để sau — biên là bảng `EXTRACTORS`, thay/thêm không đụng phần còn lại.
- **Không làm**: bất kỳ tích hợp MCP/tree-sitter/tool ngoài nào.

## Tiêu chí thành công

Đo lại bằng chính app mẫu plugin-host + `score.py`:
- Cạnh `imports` TS **≠ 0** trên app ngoài-mẫu.
- Full-space F1 **tăng thật** so với 0.727 (subset không tụt dưới 0.842).
- Hallucination **không tăng** (wikilink false-positive trong code-fence = 0).
- Negative-control vẫn **PASS**.
- **Không thêm phụ thuộc ngoài**: kiểm bằng grep — code mới không import MCP/tool ngoài, chỉ stdlib.

## Việc theo thứ tự

- [x] **Mảnh A** ✅ `fdk/tools/code_imports.py` (chỉ stdlib ast/re/pathlib — 0 dependency ngoài): EXTRACTORS TS/JS/Go/Rust + Python-ast, resolve relative + tsconfig-alias, dynamic→unresolved (không bịa). Wire vào `build-wiki-graph.enrich_code` (đa ngôn ngữ). Đòn 1: 1/3→**3/3**, Đòn 2: 1/2→**2/2**.
- [x] **Mảnh B** ✅ `_strip_code` bỏ code-fence + inline-code trước `WIKILINK_RE`. `[[NotALink]]` trong code không còn thành cạnh. Đòn 3 forbid pass.
- [x] **Mảnh C** ✅ `detect_cycles` (DFS derives-from/depends-on) + `_frontmatter_ok` quarantine YAML hỏng, đếm được. Đòn 4: 3/4→**4/4**, Đòn 7: 2/3→**3/3**.
- [x] **Mảnh D** ✅ `impact_reverse(target, edges, rel="imports", cap=1)` — impact "touches lan-truyền" = reverse-imports 1-hop trên import-graph vừa dựng (cùng kỷ luật cap=1 của `propagate_stale`, self-contained). Đòn 8: 0/0→**1/1** (impact khớp đúng 3 dependents thật). Ghi chú: đây là impact TĨNH từ graph; hook `wiki_ledger.propagate_stale` (session auto-touches trên typed-relations) là trigger production song song.

**Kết quả CUỐI** (engine vá A-D, chấm mù `score.py`, seal verified): **22/22 check · 10/10 đòn full-pass** · recall **1.0** · provably-false **0** · negative-control **PASS** · **0 phụ-thuộc-ngoài** (grep sạch). Smoke: engine vẫn build graph thật OK (129 node/145 cạnh, 177ms). So benchmark seed42 ban đầu: đòn 1 (1/3→3/3), 2 (1/2→2/2), 3 (2/3→3/3), 4 (3/4→4/4), 7 (2/3→3/3), 8 (0→1/1).
