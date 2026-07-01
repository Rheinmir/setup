# COR — Controlled Output Renderer (adopt guide)

`harness/scripts/lib/cor.py` gom các **bất biến cơ học** để một script biến dữ liệu
deterministic thành file HTML/md chia sẻ được — an toàn, versioned, cô lập lỗi.
Chưng từ `council.py` Stage-4, đã qua `/council` thẩm định (verdict: **KHẢ THI nhưng
HẸP** — microlib opt-in, KHÔNG god-lib; xem `wiki/decisions.md`).

## 6 bất biến (checklist review mọi script sinh doc)

1. **Data/present split** — render KHÔNG thêm phán xét mới; mọi số liệu từ nguồn deterministic.
2. **Escape mọi input** — `cor.esc(x)` cho mọi chuỗi người/agent nhập (chống vỡ + injection).
3. **Offline / self-contained** — no CDN, no external skill; `cor.page()` cho shell tối thiểu.
4. **Versioned, no-overwrite** — `cor.write_versioned()`; mỗi run 1 bản ghi bất biến.
5. **Isolation** — render bọc try/except; lỗi report KHÔNG được giết artifact core (ghi core TRƯỚC).
6. **Deterministic** — trách nhiệm consumer: KHÔNG Date/random trong render (cùng input → cùng output).

`cor` lo #2 #3 #4 #5; #1 #6 do consumer giữ.

## API (stateless, pure, ≤200 dòng, zero third-party)

```python
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))  # hoặc đường dẫn tới lib/
import cor
assert cor.__version__.startswith("0.")      # PIN: cor add-only, fail-fast nếu lệch major

# ghi CORE artifact TRƯỚC (json/md…) — không nằm trong try của report
core_path.write_text(...)

# rồi report (versioned + cô lập): render_fn được gọi BÊN TRONG try/except của cor
path, idx = cor.write_versioned(lambda: my_render(data), out_dir, stem="xxx-report", tag="seed42")
#   -> out_dir/xxx-report-001-seed42.html + latest.html ; (None,0) nếu render lỗi (chỉ WARN)

cor.esc(x)                       # html.escape (None->"", số->str)
cor.page(title, body_html, meta="…")   # shell offline no-CDN (dùng khi không có layout riêng)
```

Consumer chỉ viết `my_render(data) -> str`. Không đụng versioning/escape/isolation.

## Roster adopter (quarantine — `verified` = đã wire + test thật)

| Skill/script | verified | Ghi chú |
|---|---|---|
| `harness/scripts/council.py` | **true** | reference + dogfood; `_write_report` gọi `cor.write_versioned` |
| `harness/scripts/wikieval.py` | false | verdict md từ goldens+outputs — ứng viên #1 (data thuần) |
| `harness/scripts/trace-grader.py` | false | verdict trace.json+config — ứng viên #2 |
| `harness/scripts/failure-flywheel.py` | false | taxonomy jsonl → report |
| `harness/scripts/retrieval-eval.py` | false | eval report |
| skill `propose` (guidance) | false | áp **contract** (checklist) không import lib — sinh .md+.html qua agent |

**Adapt sau = một file:** wire thêm 1 consumer chỉ là thêm `cor.write_versioned(render_fn, …)`
rồi flip `verified: true` ở bảng trên. KHÔNG đổi `cor.py`.

## Ranh giới (không chồng vai)
- `docs-site-macos` / `md-to-html` = **renderer/tool** (layout glass, markdown→html). COR
  KHÔNG thay chúng — khi cần glass-shell đẹp, `my_render` có thể gọi chúng; COR chỉ lo
  data/escape/versioning/isolation quanh output.
- Skill cần render **sáng tạo** (cursor-animated-sites, uat-nonit-testcase, extract-site)
  KHÔNG ép vào COR (council loại khỏi scope) — chúng tự do layout.

## Antifragile (Taleb barbell)
- `cor.py` stateless pure, ≤200 dòng → tái bản 30'. Consumer **pin** `__version__`.
- Backwards-compat: chỉ ADD chữ ký, không BREAK. Escape hatch: cor chết → inline 5 bất biến tạm.
- `python3 harness/scripts/lib/cor.py` = selftest 5 bất biến (gate CI được).

## Origin
- Draft overnight; nguồn: council.py + /council COR verdict. Xem `wiki/draft/…/cor-pattern.md`.
