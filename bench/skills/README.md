# bench/skills — số đo đợt tách skill ra repo riêng (14/10/2026, PLAN `141026-skills-split-PLAN.md`)

Mọi số dưới đây là đo thật trong phiên 14/10/2026 trên máy dev (macOS 13, node 24, python 3.9) và GitHub Actions; cách đo ghi cạnh số.

## Trước / sau — chi phí sửa MỘT skill

| Việc | Trước (skill trong Rheinmir/setup) | Sau (Rheinmir/skills) | Cách đo |
|---|---|---|---|
| CI khi push đổi 1 SKILL.md | skills-sync.yml 15 s **+** harness.yml ~364 s (mọi push `orca`) | ci.yml **10–19 s** (2 lần đầu: 10 s, 19 s; bản xanh cuối `bdf47be` sau `--no-bin`: 16 s; checkout setup depth 1 + 7 cổng) | `gh run list -R Rheinmir/skills --json createdAt,updatedAt` |
| Cổng cục bộ trước push | `medic --ci` 34–72 s + `fdk-gate` ~61 s + fdk-uat 2 pha | `bash tools/check.sh <setup>` **1.0 s** (7 cổng) | `time bash tools/check.sh ~/orca/setup` |
| Cập nhật skill trên máy người dùng | chạy lại bootstrap trọn bộ (harness + skill + wiki) | `bootstrap.sh \| bash -s -- --skills-only` **19.8 s** (npx skills add + dấu version + kiểm requires), không đụng `~/.claude/harness` | `time`, so mtime `version.json` trước/sau |
| Cài mới trọn bộ từ canary (harness 1.3.126→1.3.127 + skill + orca-graph) | — | **38.1 s** | `time` bootstrap pha 1 |
| Skill tới tay sau cài | 116 (doc hứa 106) | **106/106 catalog có mặt** trong `~/.claude/skills` (+9 skill cục bộ khác nguồn) | parity `fdk/skills.catalog.json` ↔ thư mục |
| Hợp đồng phụ thuộc | không có | 106 skill khai `metadata.loop`; 41 khai `requires` (sàn harness ≥1.3.127, bin, scripts); `check --installed` **115/115 đủ** trên máy này, 8 skill lớp C chỉ đủ trong checkout framework | `skill-requires.py check --installed` |

## Nguồn phiên bản đồng nhất

| Kiểm | Kết quả |
|---|---|
| MCP image (Dockerfile.mcp, clone Rheinmir/skills#main) build | 22 s (cache), `/healthz` → `harness: 1.3.127`, `skills: {count 106, version 1.0.2, catalog_sha 0c842d4c…}`, `mode: read` |
| `OVERSTACK_TOOLS=read` | `tools/list` = 7 tool đọc; `/mcp` không token → 401 |
| Hook SessionStart `remote_version_nudge` (bản cài global, payload thật) | bản chuẩn 9.9.9 → đúng 1 dòng `⬆ [version] … harness v1.3.127 < v9.9.9 … bộ skill v1.0.2 < v9.9.9`; bản chuẩn bằng → im; nguồn mặc định raw GitHub (orca còn 1.3.126) → im; cache `~/.claude/harness/.remote-version.json` ghi ngày |
| Phiên `claude -p` thật trong dự án UAT (haiku) | xem `llmwiki/wiki/log.md` mục 141026-uat-skills-split |

## Cổng của setup sau khi tách (orca@23e53d2 → f1f0173)

- CI `harness` trên orca: 23e53d2 đỏ bare-path-lint (file mới skill-requires.py) → a75a85e đỏ html-font-lint (test còn đọc `skills/` trong setup + engine lệch) → **f1f0173 xanh, 9 phút 08 s** (02:00:51 → 03:09:59 UTC, run 38504042493). Job repo-health clone Rheinmir/skills vào `$RUNNER_TEMP`, env `OVERSTACK_SKILLS_DIR` chỉ cho step html-font-lint. Lớp nền html_font/html_base lấy lại bản mới hơn từ engine orca-graph 3.2.4 (parity ✓, visual gate 28/28).
- Repo skills: trang mẫu hallmark sinh lại → provenance record + `catalog.py --update` v1.0.3 (1e92a60, CI 15 s); ảnh chụp `fdk/skills.catalog.json` kéo lại.

- `medic --ci`: 0 fail · 2 warn (pre-commit chưa cài máy này; frontend 6 WARN) · 17 ok · 2 skip.
- `fdk-gate`: 16/19 — 3 bước đỏ **đã đỏ sẵn ở orca@becf0a4** (đo ở worktree sạch): `wiki-health` (wikilink hỏng `orca-graph`, `ADR-018-…`), `task-lifecycle` (T-2607xx nhảy bước), BNAL `wikieval.py --self-test` (3 golden teach-me). Ghi backlog §8.
- `test-broad` 80/80 · `demo` 13/13 · pytest 41 passed (swh-lint, skill-reuse, design-showcase, skill-requires, prompt-recall, session-start-remote-version) · engines-smoke 25/25 · ge-reachability 10/10 · capproof PASS · install-seed 15/15 · harness-update 31/31 · openclaude-install 25/25 · mcp npm test 16/16.

## Lặp lại

```bash
cd ~/orca/skills && time bash tools/check.sh ~/orca/setup
gh run list -R Rheinmir/skills --limit 5 --json status,conclusion,createdAt,updatedAt
cd <dự án downstream> && time (curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash -s -- --skills-only)
python3 ~/.claude/harness/harness/scripts/skill-requires.py check --installed
cd ~/orca/setup && docker build -f Dockerfile.mcp -t overstack-mcp:local . && docker run --rm -e OVERSTACK_TOOLS=read -e OVERSTACK_MCP_TOKEN=$(openssl rand -hex 16) -p 127.0.0.1:18791:8791 overstack-mcp:local & sleep 6; curl -s http://127.0.0.1:18791/healthz
```
