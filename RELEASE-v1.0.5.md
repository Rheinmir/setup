# overstack v1.0.5

_release gần nhất: v1.0.4 → v1.0.5 (patch)._ Giọng patch note theo council 2026-07-03 (Rams/Kahneman): **trung thực về ranh giới hoàn thiện, không phóng đại.**

## Thêm (Added)
- **Engine tự-index SELF-CONTAINED** — không còn phụ thuộc phần mềm ngoài (code-graph MCP) cho trục code:
  - `fdk/tools/code_imports.py` — trích quan hệ `imports` đa-ngôn-ngữ (TS/JS/Go/Rust + Python), chỉ stdlib, fail-open, resolve tsconfig-alias/relative, dynamic→unresolved (không bịa đích).
  - `build-wiki-graph.py` — Mảnh A-D: wire imports đa-ngôn-ngữ, strip code-fence trước wikilink, `detect_cycles`, quarantine YAML hỏng, `impact_reverse` (touches lan-truyền cap=1); thêm flag CLI `--code-root` / `--json`.
- **`medic`** — cổng sức khoẻ tổng / tuyến phòng thủ cuối: 1 lệnh gom rules-bite (harness-doctor) + drift + docs-fresh + code-compile + eval. CLI `medic` (symlink) + `/medic` slash skill. Tự-mở-coverage (đọc policy.yaml LIVE).
- **`skill-whiteboard.html`** — bản đồ quan hệ skill tĩnh (hub theo cấu trúc, ◆ = skill bao trùm), generator `whiteboard-skill-map.py`; link mỏng từ overstack.
- **fdk kim chỉ nam 2** (hub-UX) ghi vào `skills/fdk/SKILL.md` (travel, cạnh Meadows).

## Sửa (Fixed)
- **Council report hiện TÊN uỷ viên + lens** thay vì `seat-N` (map seat→persona từ config).
- **Council report redesign** — font Việt-an-toàn (bỏ Iowan/Palatino vỡ dấu), lens có style riêng, lead + accent chống wall-of-text.
- **Validator drift** `proposal_complete.py` (hooks-copy ≠ src) — sync đúng hướng.
- **overstack** phân nhóm `orca-issue` → `--check` xanh.

## Xóa / Vệ sinh (Removed / Hygiene)
- `.gitignore` **thêm `scratchpad/`** (rác ephemeral không vào repo).
- ⚠ **CẦN trước khi tag:** `git rm -r --cached scratchpad/` — vài file `scratchpad/co-council/*` đã bị track từ trước, phải untrack.

## Known limitations (khai thẳng — chưa xong, đừng đọc nhầm là hoàn thiện)
- **`medic` mới phủ 5/17 rule** có bite-test; 12 rule còn lại **CHƯA được chứng minh cắn** (không phải đã kiểm & pass). "HỆ KHOẺ" = 5/17 đã đo, **KHÔNG suy ra toàn hệ**.
- **`medic` CHƯA là cổng bắt buộc** — chưa wire pre-commit/CI; pre-commit hook đang **tắt**. Đây là bước tiếp theo (proposal `030726-medic` T3-5).
- **Benchmark self-index 10/10** chạy trên **app tự dựng, out-of-sample, N nhỏ (10 đòn)** — là 10 điểm dữ liệu, không phải statistical guarantee.
- **2 proposal** (`030726-medic`, `020726-council-chon-de-thi`) vẫn ở `wiki/sources/draft/` — trạng thái *proposed*, chưa duyệt.
- **eval self-index** còn ở `scratchpad/` (chưa promote canonical) — cố ý, để cọ xát thêm 1 chu kỳ (Taleb).
