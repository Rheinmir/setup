# Backlog — nợ kỹ thuật harness (chỉ ghi, chưa xử lý)

Ngày ghi: 2026-10-13. Ngữ cảnh: đợt sửa truy hồi BM25 + cạnh file và phía ghi (nhánh `feat/retrieval-bm25-edges`).
Bằng chứng đo trên repo openship (`~/orca/openship`), 19 phiên thật.

Chi phí từng stage (trước/sau, token và ms): xem `bench/retrieval/README.md` mục "Chi phí từng stage".

## 1. session-provenance vô nghĩa — nguồn "did" lấy sai chỗ

**Hiện trạng.** `scratch-log.py distill` (gọi từ Stop-hook `secondary_memory`) sinh mỗi ngày một trang
`.llmwiki/wiki/sources/provenance/DDMMYY-session-provenance.md`. Trên openship 16/16 trang có cùng một dòng "vì sao":
`auto: Merge pull request #930 ... — trích từ git`, 0/16 dòng why thủ công, danh sách file chạm là `git status` của repo
(toàn thư mục untracked `.harness/`, `.llmwiki/`, `.archify/`), chỉ khác số đếm 10 → 16.

**Nguyên nhân gốc.** "Việc đã làm" được suy từ `git log -1` (HEAD, là commit upstream) và `git status` (working tree),
không phải từ việc thật trong phiên. Cùng lỗi gốc với episode trùng (đã sửa một phần: 1 episode/phiên, nhưng did vẫn là HEAD).

**Việc cần làm (chọn một hoặc kết hợp).**
- [ ] Tắt distill tự động; chỉ sinh trang khi có ≥1 dòng why thủ công trong `scratch-log.jsonl` của phiên.
- [ ] Đổi nguồn did/files cho cả episode lẫn provenance: lấy từ transcript phiên (prompt đầu của user, file agent đã Edit/Write),
      không lấy HEAD và `git status`.
- [ ] Dọn 16 trang hiện có trên openship + dòng tương ứng trong `wiki/index.md` (không có thông tin để giữ).
- [ ] Tạm thời: okf-scan đã bỏ qua `sources/provenance/` theo mặc định (`OKF_SCAN_SKIP`), nên không còn chiếm slot recall.

## 2. Truy vấn recall đầu phiên = commit subject → episode luôn thắng wiki

**Hiện trạng.** `session_start.py recall` dùng did của episode gần nhất (= commit subject) làm truy vấn okf-scan.
Episode có text y hệt nên luôn đứng đầu BM25; trang wiki chỉ nổi nhờ cạnh file dirty.

**Việc cần làm.**
- [x] (13/10) Hook UserPromptSubmit `prompt_recall`: quét theo PROMPT đầu phiên qua `okf-scan query --prompt` (định danh → từ vựng → bảng cầu Việt→Anh), chỉ bơm trang SessionStart chưa in. Bench `bench_prompt_query.py`: vi nguyên văn 0.004 → 0.18 R@1 (0.31 khi có tên file). SessionStart vẫn quét theo did để giữ biên lai (test session-chain).
- [ ] Bỏ hẳn quét theo did ở SessionStart khi đã có biên lai prompt (cần đổi test session-chain).
- [ ] Hoặc giảm trọng số kênh chữ cho mục `episode` trong `okf-scan.rank`.

## 3. Thứ tự trong khối recall — 3/10 case hụt ở mọi mức nhiễu

**Hiện trạng.** `bench_attention.py` (haiku, 0 → 650k token nhiễu): model dùng khối 100%, nhưng khi khối có 2 trang hợp lý
(vd `active-work.md` hub và trang concept đúng) thì chọn ngẫu nhiên → hit 0.70–0.80.

**Việc cần làm.**
- [ ] Hạ trang hub (`active-work`, `architecture`, `index`) xuống dưới trang concept/entity cụ thể khi cùng điểm cạnh.
- [ ] In lý do bên cạnh mỗi gợi ý ("trích dẫn 3 file bạn đang sửa") để model có cơ sở chọn.
- [ ] Chạy lại bench_attention trên model lớn hơn haiku để xác nhận.

## 4. docs-gate global đếm thông báo nền là prompt

**Hiện trạng.** `user_prompt_submit.py` tăng bộ đếm ở mọi UserPromptSubmit, kể cả task-notification của Monitor/background.
Phiên 13/10: nhắc 5 lần trong 25 "prompt" mà user không gõ.

**Việc cần làm.**
- [ ] Bỏ qua payload có prompt bắt đầu bằng `<task-notification>` / `[SYSTEM NOTIFICATION` khi đếm và khi soi cửa sổ.

## 5. Đo lại phía đọc trên phiên thật sau sửa

**Hiện trạng.** Số "gợi ý được mở thật" 7/72 là số TRƯỚC sửa. Sau sửa chưa có phiên thật nào để đo.

**Việc cần làm.**
- [ ] Sau ~10 phiên, chạy `bench/retrieval/bench_cost_sessions.py ~/.claude/projects/-Users-admin-orca-openship/` và so với bảng trong README.

## 6. Phát hành

- [ ] Commit nhánh `feat/retrieval-bm25-edges` (user quyết định), bump `harness/version.json` (`.template-manifest.json` đã thêm `lexrank.py`).
- [ ] Re-curl bootstrap trên openship để stamp khớp global (hiện v1.3.124 ≠ v1.3.125).

## 7. Phát hiện từ rà soát toàn bộ writer (13/10, chi tiết: `bench/retrieval/wiki-data-lifecycle-audit.md`)

- [ ] **Hai cây sổ**: writer dùng `overstack_paths.harness_dir()` ghi `.harness/metrics/` (memory, receipts, scratch); writer viết cứng `harness/metrics` đẻ cây lạc `openship/harness/metrics/` (cost-by-session, events, failures, self-report, sync-log, tasks). Gom về một chỗ qua overstack_paths.
- [ ] **Writer hỏng ở dự án khách vì đường cứng** `llmwiki/` hoặc `parents[2]`: code-logger `render_md` (log.md), memory-map, mem-rank `export-okf`, flywheel `--draft`, unknown-ledger, docs-curate, prefix trong post_tool_use (`llmwiki/` không khớp `.llmwiki/`), glob của ledger-snapshot (bỏ sót `.harness/`).
- [ ] **distill ghi đè cả file theo ngày** → một ngày nhiều phiên chỉ còn phiên cuối (scratch-log.py:219).
- [ ] **Khối cuối `regen_docs` của Stop** (wiki-graph → provenance-log → token-budget → agent-trace) gần như không chạy tới ở openship: wiki-graph.html mtime 24/09, không có provenance-log.jsonl, tokens.jsonl. Suy từ đĩa: wiki-graph hết ngân sách 20s. Cần đo thật.
- [ ] **27 trang kiến thức có MỘT nguồn sinh** (orca-onboard 24/09) và không hook nào cập nhật nội dung từ đó; wiki-sync chưa có neo `.last-sync.json` nên không đo được code trôi. Cần nhịp cập nhật wiki từ diff code (skill lint/ingest theo lịch hoặc theo commit).
- [ ] **Sổ ghi mà không ai đọc**: self-report.jsonl, sync-log.jsonl, guardrails/*.md ở khách, problem-tree.html (control-room chỉ đọc fdk-problem-tree.html), log.md. Quyết định: nối người đọc hoặc bỏ ghi.
- [ ] **Stop hook của dự án đăng ký 2 lần** trong openship `.claude/settings.json` (harness-events stop).
- [ ] **mem-rank ghi đè cả memory.jsonl không khoá** (14/10): 36 phiên `claude -p` chạy song song 4 luồng trên openship → 22 episode gốc mất sạch, chỉ còn 19 của phiên thử; khôi phục từ `memory.jsonl.bak-20261013T060717` + compact (mất các episode 13/10 sau 06:07). Người dùng thật hay mở nhiều phiên cùng repo → cần ghi atomic (tmp + rename) và khoá file (fcntl.flock) ở mem-rank; scratch-log/receipts là append nên không sao.

## 8. Sau khi tách skill ra repo Rheinmir/skills (14/10, PLAN `141026-skills-split-PLAN.md`)
- [ ] **fdk-gate trên `orca` đỏ sẵn 3 bước** (đo ở worktree sạch becf0a4, trước mọi sửa của đợt tách): `wiki-health` (wikilink hỏng `orca-graph`, `ADR-018-…` trong 3 trang sources/120926-*, 200926-*), `task-lifecycle` (T-2607xx `proposed→done` nhảy bước, T-260924-01 state `implemented`), BNAL `wikieval.py --self-test` (3 golden teach-me không thoả assert của chính nó). Không thuộc đợt tách; sửa riêng.
- [ ] **Host overstack-mcp tại skills.giatbh.io.vn** (T7, handoff — RUNBOOK §7): cần người vận hành trên k8s2 (máy dev không có khoá SSH/token devops-agent; token Cloudflare dán trong chat bị khoá IP → xoay, cất Vault `secret/infra/cloudflare`). Sau khi lên: dev đặt `OVERSTACK_VERSION_URL=https://skills.giatbh.io.vn/healthz`.
- [ ] **`fdk/skills.search.json` không còn sinh trong setup** (chỉ mục BM25 cho consumer ngoài/cheatsheet); nếu còn ai dùng thì sinh ở CI repo skills (`build-skill-search.py --skills skills --out skills.search.json`) và publish cùng catalog.
- [ ] **`build-cheatsheet.py` / `whiteboard-skill-map.py`** trong repo framework đọc `~/.claude/skills` (bản cài máy) khi không đặt `OVERSTACK_SKILLS_DIR` — trang sinh ra phụ thuộc máy; không có `--check` nên không gãy CI, nhưng nên trỏ `OVERSTACK_SKILLS_DIR=<checkout skills>/skills` khi build docs chính thức.
- [ ] **Ảnh chụp `fdk/skills.catalog.json`** phải kéo lại (`sync-skill-catalog.py`) + `capability-stamp --update` mỗi khi phát hành setup — chưa có nhắc tự động; cân nhắc probe medic `--check` (cần mạng → advisory).
- [ ] **`llmwiki/skills/` mirror + `.template-manifest.json`** đã bỏ 23 mục skill: dự án downstream đang có `llmwiki/skills/` cũ sẽ không được sync nữa (file cũ nằm lại, không hại); `/sync-template` không xoá.
