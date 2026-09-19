---
name: new-skill
disable-model-invocation: true
description: Scaffold a new skill into both publish trees at once — skills/<name>/SKILL.md plus its byte-identical llmwiki mirror — via fdk/tools/new-skill.py, then print the exact commands to register it on the curated surfaces (LOOP_MAP, marketplace.json, AGENT.md/CLAUDE.md). Use when the user says "create a skill", "add a new skill", "scaffold a skill", "make a new skill", "new skill", or invokes /new-skill.
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: new-skill

Adding a skill touches four places — the canonical `skills/<name>/SKILL.md`, its `llmwiki/skills/<loop>/<name>.md` mirror, the `sync-skills.py` LOOP_MAP, the `marketplace.json` publish list, and a row in the AGENT.md/CLAUDE.md `## Skills` table. Miss one and the trees drift (that is how `marketplace.json` fell ~30 skills behind). This skill drives `fdk/tools/new-skill.py`, which writes the two mechanical files identically and prints the exact lines for the three curated places — it never edits them itself.

## WHAT

### Purpose và context
- **Purpose:** tạo một skill mới ở cả hai cây phát hành cùng lúc (canonical + mirror byte-identical) theo khung `solid-what-how/1`, rồi đưa đúng các dòng cần dán để đăng ký nó trên các bề mặt curated.
- **Trigger (when to use):**
- The user asks to create / add / scaffold a new skill, or invokes `/new-skill`.
- You are about to hand-create a `skills/<name>/SKILL.md` and would otherwise forget the mirror or the registry surfaces.

> **Viết cho đúng nghề — đọc `[[skill-craft]]` trước.** Bộ từ vựng để một skill đoán được: hai loại phí (context load ↔ cognitive load — skill chỉ-gọi-tay thì khai `disable-model-invocation: true`, khỏi tốn context), completion criterion cho mỗi bước, leading word thay ba câu, và năm failure mode phải tránh (duplication/sediment/sprawl/no-op/negation). `/lint` bước 8b đo các thứ này bằng máy.
- **Non-goals:** không tự sửa LOOP_MAP / marketplace.json / AGENT.md / CLAUDE.md; không migrate skill đã có (sửa tại chỗ); không tạo skill kéo từ upstream (thứ đó vào `skills/external/`).

### Mental model
`tên + loop + description (trigger) → new-skill.py → skills/<tên>/SKILL.md (khung WHAT/HOW) + llmwiki/skills/<loop>/<tên>.md → điền TODO → swh-lint → sync-skills → đăng ký 3 bề mặt curated → sync-skills --check + skill-registry --check`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | `<name>` | có | kebab-case, chưa tồn tại trong `skills/` |
| In | `--loop` | có | `dev-loop` · `orchestrate` · `wiki-loop` · `utils` |
| In | `--desc` | có | một dòng giàu trigger phrase (router khớp theo nó) |
| Out | `skills/<name>/SKILL.md` + mirror | có | hai file giống hệt, khung SWH đã điền xong TODO |
| Out | 3 bề mặt curated đã đăng ký | có | hai lệnh check cuối đều xanh |

### Rules và capabilities
- RULE-01 (MUST): The tool writes ONLY the two mechanical files (canonical + mirror). It never edits LOOP_MAP, marketplace.json, AGENT.md, or CLAUDE.md — those are user-curated; you add the printed lines by hand.
- RULE-02 (MUST): After editing the generated skeleton, ALWAYS re-run `sync-skills.py` — parity is enforced, and your edits will have made the mirror stale.
- RULE-03 (MUST): A vague `--desc` is a skill that never fires. Put concrete trigger phrases and `/`-commands in it.
- RULE-04 (MUST): Never overwrite an existing skill — if the name is taken, edit `skills/<name>/SKILL.md` in place or pick another name.
- Capabilities: ghi hai file skill; đọc chỉ mục skill hiện có (BM25) để cảnh báo trùng; các bề mặt curated do người dán tay.

### Failure boundaries
- Tên đã tồn tại → **blocked** (tool từ chối), sửa tại chỗ hoặc đổi tên.
- Trùng năng lực trên ngưỡng BM25 → cảnh báo; với `--strict` thì **blocked**.
- `swh-lint` hoặc hai lệnh check cuối đỏ → chưa xong, sửa rồi chạy lại.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | judgment | yêu cầu user | chốt `<name>`, `--loop`, `--desc` giàu trigger | 3 input | mơ hồ → hỏi |
| W02 | effect | 3 input | `new-skill.py --dry-run` (in mẫu catalog khớp) rồi chạy thật — có mẫu hợp thì `--from <asset_id> --params p.json` | 2 file + recipe `reuse_decision` | tên trùng → blocked · tham số sai → INVALID_PARAMETER |
| W03 | judgment | khung | điền mọi TODO của WHAT/HOW, chạy `swh-lint` | skill đạt cấu trúc | đỏ → sửa, lặp W03 |
| W04 | effect | skill | `sync-skills.py` để mirror khớp | mirror giống hệt | — |
| W05 | effect | dòng tool in ra | đăng ký LOOP_MAP, marketplace, bảng AGENT/CLAUDE | 3 bề mặt | — |
| W06 | deterministic | repo | `sync-skills.py --check` + `skill-registry.py --check` | cả hai xanh | đỏ → sửa bề mặt lệch |

Chi tiết từng bước (nguồn chân lý cho W01–W06):

1. Settle three inputs: a kebab-case `<name>`, a `--loop` (`dev-loop` | `orchestrate` | `wiki-loop` | `utils`), and a `--desc` that is **rich with trigger phrases** (the description is what the skill router matches on). Skill chỉ-gọi-tay (chỉ user gõ, không skill nào khác gọi) → thêm `disable-model-invocation: true`, `--desc` rút thành một dòng người-đọc (xem `[[skill-craft]]`).
2. Preview first, then create:
   ```bash
   python3 fdk/tools/new-skill.py <name> --loop <loop> --desc "<description>" --dry-run   # preview body + next steps
   python3 fdk/tools/new-skill.py <name> --loop <loop> --desc "<description>"             # write both files
   ```
   It refuses if `skills/<name>/` already exists.
3. Fill in the generated `skills/<name>/SKILL.md` — the skeleton is the compact `solid-what-how/1` template (`## WHAT` purpose/contract/rules/failure + `## HOW` main workflow table/branches/examples, see `[[solid-what-how]]`). Replace every TODO with real, verifiable content, then check the shape:
   ```bash
   python3 fdk/tools/swh-lint.py --skills <name> --ci
   ```
4. Re-mirror after editing so the llmwiki copy stays byte-identical:
   ```bash
   python3 harness/scripts/sync-skills.py
   ```
5. Register on the curated surfaces by pasting the exact lines the tool printed: add the LOOP_MAP entry in `harness/scripts/sync-skills.py`, (optionally) the `./skills/<name>` line in `.claude-plugin/marketplace.json`, and one row in BOTH `llmwiki/AGENT.md` and `llmwiki/CLAUDE.md` `## Skills` tables.
6. Verify every surface agrees — both must pass:
   ```bash
   python3 harness/scripts/sync-skills.py --check        # mirror parity
   python3 harness/scripts/skill-registry.py --check      # cross-surface drift
   ```

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | skill chỉ-gọi-tay | thêm `disable-model-invocation: true`, rút `--desc` thành một dòng người đọc | skill model-invoked → skip | W02 |
| B03 | user_optional | catalog có template khớp contract (lọc effect trước, xếp hạng sau) | `--from` render template typed + pin sha256 vào `fdk/skill-catalog/recipes/<name>.recipe.json`; không hợp thì scratch kèm `--reason` | catalog không đọc được → decision `catalog_unavailable`, vẫn sinh khung compact | W03 |
| B02 | recovery | BM25 báo trùng năng lực | đổi tên dạng biến thể + làm description khác biệt, hoặc sửa skill có sẵn | `--strict` → dừng | W01 |

### Validation và stopping
Mỗi lần chạy đều ghi `reuse_decision` (reuse · scratch · catalog_unavailable) — Reuse Layer SWH v1.1, catalog `fdk/skill-catalog/`, tool `fdk/tools/skill-reuse.py`. Reuse không miễn cổng nào: skill sinh từ template vẫn phải qua `swh-lint`.
Xong khi `swh-lint --skills <name> --ci`, `sync-skills.py --check` và `skill-registry.py --check` đều rc 0. Hành vi thật (skill có được gọi đúng không) thử bằng 1–2 câu mẫu, lint không chứng minh được.

### Examples
- **Positive:** `new-skill.py csv-preview --loop utils --desc "Xem trước CSV… Trigger: 'preview csv'"` → hai file khung, điền WHAT/HOW, ba check xanh.
- **Boundary/failure:** `new-skill.py ship …` → tool từ chối vì `skills/ship/` đã tồn tại; sửa `skills/ship/SKILL.md` tại chỗ.
