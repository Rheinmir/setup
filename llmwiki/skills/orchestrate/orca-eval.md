---
name: orca-eval
disable-model-invocation: true
description: Quét N session Claude Code gần nhất, distill best practices thành report md + đề xuất action cải tiến quy trình
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: orca-eval

## WHAT

### Purpose và context
- **Purpose:** Vòng tự cải thiện quy trình: đọc lại session logs → rút best practice / anti-pattern → report md → đề xuất hành động (promote thành skill, sửa CLAUDE.md, thêm hook…). Report là **đề xuất** — mọi action phải qua `propose` → gate, không tự thực hiện.
- **Trigger (when to use):**
  - `/orca-eval [N]` — N = số session gần nhất cần quét (vd 5/10/15)
  - Không có N → chỉ quét session hiện tại
  - User nói "đánh giá session", "rút best practice", "tối ưu quy trình từ lịch sử"
- **Non-goals:** không tự thực hiện action (promote skill, sửa CLAUDE.md, thêm hook); không sửa/xoá session log; không auto-trigger mỗi 30 session (Phase 2, chưa nằm trong skill này).

### Mental model
`*.jsonl session logs → orca-eval-scan.sh digest (prompts · tool errors · lệnh lặp) → 4 tín hiệu (Correction · Repetition · Friction · Win) → finding → đúng 1 action (promote-to-skill · update-CLAUDE.md · add-hook · keep · ignore) → report draft → DỪNG chờ duyệt`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | `N` | không | số session gần nhất theo mtime `*.jsonl`; default = session hiện tại |
| In | session logs `~/.claude/projects/<project-slug>/*.jsonl` | có | chỉ đọc |
| Out | `llmwiki/wiki/draft/orca/DDMMYY-eval-report.md` | có | theo Report template |
| Out | `wiki/index.md` + `wiki/log.md` cập nhật | có | — |
| Out | bảng action hiển thị cho user | có | "xong" = user đã thấy bảng; action chưa thực thi |

### Rules và capabilities
- RULE-01 (MUST): Read-only với session logs — không sửa/xóa `*.jsonl`.
- RULE-02 (MUST): KHÔNG nạp nguyên transcript — 1 session có thể hàng trăm KB; đọc qua digest của scanner.
- RULE-03 (MUST): Mỗi finding gắn đúng 1 action; action chỉ thực hiện sau khi user duyệt (qua `propose` nếu là thay đổi code/skill).
- RULE-04 (MUST): Format JSONL của Claude Code không có spec công khai — scanner fail thì fallback session hiện tại và báo rõ, không sinh report rỗng.
- Capabilities: đọc session log cục bộ qua scanner; ghi draft wiki + index + log. Không mạng, không sửa code/config.

### Failure boundaries
- Scanner fail → **partial**: fallback session hiện tại, báo rõ; không sinh report rỗng.
- Không có tín hiệu nào → report ghi rõ 0 finding (không bịa finding).
- User chưa duyệt → action ở trạng thái **proposed**, skill dừng.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | `N` | Scan: `skills/orca-eval/assets/orca-eval-scan.sh [N]` từ repo root | digest | fail → B01 |
| W02 | judgment | digest | Distill 4 loại tín hiệu | danh sách finding + bằng chứng | — |
| W03 | effect | finding | Report theo template + cập nhật index/log | draft report | — |
| W04 | judgment | finding | Action proposal: bảng action cho user, **DỪNG** | bảng action | không duyệt → dừng |

Chi tiết từng bước (nguồn chân lý cho W01–W04):


1. **Scan** — chạy `skills/orca-eval/assets/orca-eval-scan.sh [N]` từ repo root. Script trả về digest gọn (user prompts, tool errors, lệnh Bash lặp lại). KHÔNG nạp nguyên transcript — 1 session có thể hàng trăm KB.
2. **Distill** — từ digest, tìm 4 loại tín hiệu:
   - **Correction**: user sửa lời agent ("không, dùng X", "sai rồi", "actually…") → quy tắc ứng xử mới
   - **Repetition**: chuỗi lệnh/thao tác lặp ≥ 3 lần qua các session → ứng viên skill-hóa
   - **Friction**: tool error lặp lại, permission prompt nhiều lần, retry loop → ứng viên hook/permission/config
   - **Win**: workflow user approve nhanh, không phải sửa → ghi nhận best practice giữ nguyên
3. **Report** — ghi `llmwiki/wiki/draft/orca/DDMMYY-eval-report.md` theo template dưới. Cập nhật `wiki/index.md` + `wiki/log.md`.
4. **Action proposal** — mỗi finding gắn đúng 1 action: `promote-to-skill` / `update-CLAUDE.md` / `add-hook` / `keep` / `ignore`. Hiển thị bảng action cho user. **DỪNG** — action chỉ thực hiện sau khi user duyệt (qua `propose` nếu là thay đổi code/skill).

#### Input

| Tham số | Ý nghĩa | Default |
|---------|---------|---------|
| `N` | Số session gần nhất (theo mtime của `*.jsonl`) | session hiện tại |

Session logs nằm tại `~/.claude/projects/<project-slug>/*.jsonl` — slug là cwd với `/` thay bằng `-` (vd `-Users-giatran-orca-workspaces-setup-evaluation`).


### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | recovery | scanner fail (format JSONL đổi) | fallback session hiện tại, báo rõ trong report | không có gì để quét → báo, không sinh report rỗng | W02 |
| B02 | conditional_required | action là thay đổi code/skill và user duyệt | chuyển qua `propose` → gate | user không duyệt → dừng | — |

### Validation và stopping
Scanner là tất định; phân loại tín hiệu là judgment — mỗi finding phải có bằng chứng (session + trích dẫn ngắn) trong bảng. Dừng cứng ở W04 chờ user duyệt.

### Examples
- **Positive:** `/orca-eval 10` → scan 10 `*.jsonl` mới nhất → phát hiện user 4 lần sửa "dùng ./scratchpad/ không /private/tmp" (Correction) → finding gắn `update-CLAUDE.md`; report `llmwiki/wiki/draft/orca/DDMMYY-eval-report.md` + bảng action, DỪNG.
- **Boundary/failure:** `orca-eval-scan.sh` lỗi vì đổi format JSONL → fallback session hiện tại, report ghi rõ scanner fail; không có tín hiệu nào → báo 0 finding, không sinh report rỗng.

### Reference — Report template

```markdown
---
type: draft
title: "DDMMYY-eval-report"
status: proposed
tags: [<skill-name>, output-report]
timestamp: YYYY-MM-DD
---

# DDMMYY-eval-report
**Type:** draft
**Status:** proposed
**Tags:** orca-eval, eval-report
**Proposed:** YYYY-MM-DD
**Scope:** <N session / session hiện tại> — <danh sách file jsonl đã quét>

## Best practices
| # | Tín hiệu | Loại | Bằng chứng (session, trích dẫn ngắn) |
|---|----------|------|--------------------------------------|

## Đề xuất action
| # | Finding | Action | Lý do |
|---|---------|--------|-------|

## Origin
- **Sessions:** <paths đã quét>
- **Generated by:** /orca-eval
```

### Reference — Giới hạn

- Read-only với session logs — không sửa/xóa `*.jsonl`.
- Format JSONL của Claude Code không có spec công khai — scanner fail thì fallback session hiện tại và báo rõ, không sinh report rỗng.
- Auto-trigger mỗi 30 session: **Phase 2** (cần Stop-hook + counter), chưa nằm trong skill này.

### Reference — References (community — claimed 2026-06-11)

| Repo | Áp dụng được gì |
|------|-----------------|
| [BayramAnnakov/claude-reflect](https://github.com/BayramAnnakov/claude-reflect) | Regex bắt correction ("no, use X", "remember:"), queue → review 2 giai đoạn, routing global vs project CLAUDE.md, `/reflect-skills` tìm pattern lặp để skill-hóa |
| [haddock-development/claude-reflect-system](https://github.com/haddock-development/claude-reflect-system) | Stop-hook auto-run cuối session (mẫu cho Phase 2 auto-trigger 30 session), cross-skill best-practice extraction |
| [netresearch/claude-coach-plugin](https://github.com/netresearch/claude-coach-plugin) | Friction detection — đếm permission prompts / retry loops làm tín hiệu cải tiến |
| [robonuggets/skills — calibrate](https://github.com/robonuggets/skills) | In-session self-improvement: review conversation hiện tại, đề xuất sửa skill/memory có chủ đích |
| [a-c-m reflection.md gist](https://gist.github.com/a-c-m/f4cead5ca125d2eaad073dfd71efbcfc) | Bản tối giản 1 file — giữ skill này gọn, không over-engineer |

## Origin
- **Raw:** `llmwiki/raw/evalution-engineering.md`
- **Draft:** `wiki/draft/orca/110626-orca-eval-skill.md`
