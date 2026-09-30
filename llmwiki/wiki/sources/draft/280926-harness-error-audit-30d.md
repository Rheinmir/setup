---
type: report
title: "280926-harness-error-audit-30d"
status: draft
tags: [harness, audit, hooks, failure-flywheel, subagent, github-issues]
timestamp: 2026-09-28
---

# 280926 — Kiểm toán lỗi harness 30 ngày (29/08 → 28/09/2026)

**Status:** draft · chờ user chọn gói fix

## Tóm tắt

Nguồn: 389 transcript phiên trong `~/.claude/projects` (284 phiên chính và 105 phiên sub-agent), cộng 30 issue GitHub `Rheinmir/setup` mở trong 30 ngày. Trong các transcript có **1.199 sự kiện lỗi dính tới harness**: 1.152 ở phiên chính, 47 ở sub-agent.

Ghi chú về nguồn dữ liệu: `harness/metrics/provenance-log.jsonl` chỉ ghi sự kiện artifact (code.change, docs.change…) và **không có trường lỗi**. `events.jsonl` cũng vậy. Vì thế nguồn lỗi thật là transcript (gồm các attachment `hook_cancelled`, `hook_*_error` và `tool_result.is_error`). Đây cũng là một lỗ hổng: harness **không có sổ lỗi hook**, xem mục F6.

Ba lỗi đầu bảng chiếm 84% tổng số và đều là **lỗi của chính hook harness**, không phải lỗi của agent:

| # | Lỗi | Số lần | Tái hiện được | Mức |
|---|---|---|---|---|
| 1 | `stop.py` timeout 30s | **731** (03/08 → 28/09, gần như ngày nào cũng có) | ✅ đo được 70,2s | 🔴 critical |
| 2 | Luật R7/R16/R2/R9 chặn khi ghi file (PostToolUse) | 106 blocking + 24 deny | — hành vi đúng thiết kế, nhưng lặp lại | 🟠 friction |
| 3 | `user_prompt_submit.py` in ra JSON không hợp lệ | 35 (18/09 → 25/09) | ✅ đọc code thấy | 🔴 high |
| 4 | egress-guard chặn nhầm `localhost` / `127.0.0.1` | 10/30 lần egress chặn | ✅ `check_bash` trả vi phạm | 🟠 medium |
| 5 | zsh `echo =====` → `(eval):1: ==== not found` làm exit 1 | 16, **chủ yếu ở sub-agent** | ✅ | 🟡 low (gây nhiễu) |
| 6 | Worktree isolation từ chối lệnh do hook rtk bọc `git` | 11 (sub-agent + worktree) | ✅ | 🟡 medium |
| 7 | Issue CI tự mở nhưng không tự đóng khi đã xanh | #172, #167 vẫn OPEN dù `--check` hiện rc=0 | ✅ | 🟡 low |
| 8 | Script tự import `bnal_config` / `hooklib` → `ModuleNotFoundError` khi nạp qua importlib | 7 | ✅ | 🟡 low |
| 9 | `orca-graph.py` crash `KeyError: 'T1'` khi gõ sai node id | 3 | ✅ | 🟡 low |

## Chi tiết và root cause

### F1 — `stop.py` luôn vượt 30s → bị kill, cổng Stop không chạy tới cuối (🔴)

**Bằng chứng.** 731 attachment `hook_cancelled` có `timedOut: true` và `durationMs` từ 30016 đến 30027 ms. Trong đó 445 lần ở repo framework, 231 ở `projects/payrol` và phần còn lại ở các workspace downstream khác. Có thêm 2 traceback `subprocess.TimeoutExpired` (25/09).

**Tái hiện** (bọc `subprocess.run` để đo, chạy `stop.py` thật trên repo framework):

```
14.0s  fdk/tools/build-wiki-graph.py
 2.6s  harness/scripts/provenance-log.py record-changed
 1.8s  harness/scripts/dym-sync.py
42.8s  fdk/tools/medic.py --ci        ← "medic gương-soi"
 2.7s ×2 validators (…)               ← chạy SAU 30s: thực tế bị kill, không bao giờ tới
TOTAL 70.2s   (hook timeout = 30s trong ~/.claude/settings.json)
```

**Root cause.** `stop.py` gọi tuần tự khoảng 15 subprocess, và các timeout con cộng lại lên tới hơn 500s (`medic` 120s, `wiki-graph` 90s, `agent-trace` 60s, `sync-skills` 40s…). Không có ngân sách tổng nào cho cả hook. Timeout của Claude Code giết cả tiến trình, nên mọi bước đứng sau `medic` **âm thầm không chạy**: validator R3 index-sync, ghi recall/episode và scratch-log. Đây là lý do gốc của nhiều self-report như #156 ("quá nửa phiên không quét context") và #159 ("chuỗi phiên gãy").

Ở downstream (payrol, 231 lần) thì không có `medic`, nên thủ phạm nhiều khả năng là `build-wiki-graph` cộng `agent-trace`. **Phần này chưa đo**, cần chạy cùng probe trong một workspace downstream.

**Fix đề xuất (hệ thống):**
1. Chia `stop.py` làm hai tầng. **Đồng bộ và nhanh** (chỉ validator và ghi sổ, ngân sách tổng khoảng 10s): chạy trước, không bao giờ đứng sau việc nặng. **Nặng** (`medic --ci`, `wiki-graph`, `build-*`, `agent-trace`, `dym-sync`): tách sang một tiến trình nền (`Popen(..., start_new_session=True)`, stdout vào log). Kết quả sẽ hiện ở SessionStart hoặc lượt Stop kế tiếp.
2. Đặt deadline tổng: mỗi `subprocess.run` nhận `timeout=min(t, deadline-now)`. Hết ngân sách thì bỏ qua bước và ghi vào sổ lỗi hook (F6).
3. Thêm test `stop-budget-test.sh` để assert `stop.py` chạy dưới 15s trên fixture framework và fixture dot-layout.

### F2 — Luật chặn khi ghi (R7 plan/proposal, R16 report-show-path, R2, R9) lặp lại 130 lần (🟠)

**Bằng chứng.** R7 xuất hiện 77 lần (`plan-executable` 34, `proposal-complete` 40), R16 18 lần, R2 14 lần, R9 8 lần. Agent viết file trước, bị chặn, rồi mới sửa. Mỗi lần như vậy tốn 1–3 lượt.

**Root cause.** Luật chỉ **cắn sau khi viết**. Không có template hay scaffold nào để agent **viết đúng ngay từ đầu**. Ví dụ R7 `(b) seq html khong ton tai`: proposal phải trỏ tới file seq HTML mà lúc đó chưa được sinh.

**Fix đề xuất:**
1. Khi PreToolUse gặp Write vào `wiki/sources/draft/*`, hook bơm (additionalContext) **checklist của luật sẽ áp** trước khi ghi, thay vì chặn sau. Cách này rẻ và không chặn gì.
2. Thêm lệnh scaffold `new-draft.py <kind>` sinh sẵn frontmatter, `## Origin`, link seq và placeholder. `/propose` và `/plan` gọi lệnh này thay vì viết tay.
3. Theo dõi chỉ số "bite lặp trên cùng file". Nếu cùng file bị cùng luật chặn từ 2 lần trở lên thì đẩy vào failure-flywheel.

### F3 — `user_prompt_submit.py` in nhiều object JSON → Claude Code bỏ toàn bộ context (🔴)

**Bằng chứng.** 35 `hook_non_blocking_error`: *"Hook output looks like a JSON object but is not valid JSON"*. Stdout có dạng `{"hookSpecificOutput":…}\n{"hookSpecificOutput":…}`.

**Root cause.** Hàm `emit()` (`llmwiki/.claude/hooks/user_prompt_submit.py:69`) `print` một object mỗi lần được gọi. Khi có từ 2 thông điệp trở lên trong cùng một lượt (orca-graph đang chạy node **và** goal directive…) thì stdout thành 2 object liền nhau, parse fail, và **mất cả hai** context.

**Fix đề xuất:** gom các thông điệp vào một list rồi `emit` **đúng một lần** cuối hook, nối bằng `"\n"`. Thêm test: gọi hook với state có hai nguồn thông điệp, rồi assert `json.loads(stdout)` thành công. `orca_guard.py:28` cũng có mẫu tương tự, cần rà cùng lúc. Nên kiểm cả mọi hook: **stdout chỉ được là một JSON**.

### F4 — egress-guard coi loopback là egress (🟠)

**Bằng chứng.** Trong 30 lần egress bị chặn, có 10 lần là `localhost` hoặc `127.0.0.1`: agent `curl` server dev của chính nó (R21 còn in link những server này ra). Kiểm trực tiếp: `check_bash('curl -s http://localhost:8765/')` trả về `egress to non-allow-listed host: localhost`.

**Fix đề xuất:** trong `egress-guard.py`, `_allowed()` luôn cho qua `localhost`, `127.0.0.0/8`, `::1` và `*.localhost`. Không nên đưa chúng vào `allow_domains`, vì loopback không phải egress theo định nghĩa. Thêm ca vào `egress-guard-falsepos-test.py`. Các lần chặn còn lại (`fonts.googleapis.com`, `superops.com`…) là đúng thiết kế.

### F5 — Nhiễu shell ở sub-agent: zsh EQUALS và worktree-isolation (🟡)

**zsh `=word`.** Có 16 lần, phần lớn trong sub-agent (9398848d: 7 agent song song cùng dính). Nguyên nhân là `echo =====` trong zsh bị hiểu thành `=cmd` expansion, sinh `(eval):1: ==== not found` và rc=1, trong khi output vẫn đúng. Agent tưởng lệnh lỗi rồi chạy lại. **Fix:** thêm một dòng vào `llmwiki/AGENT.md`/CLAUDE.md: "shell là zsh — dùng `echo '====='` (có nháy) hoặc `echo ---`". Có thể thêm guard PreToolUse cảnh báo (không chặn) khi gặp `echo =`.

**Worktree isolation × rtk.** Có 11 lần. Hook rtk viết lại lệnh thành `rtk <cmd>`, và bộ kiểm worktree của Claude Code không đọc xuyên qua được, nên từ chối (*"runs rtk with a git command among its operands"*). **Fix:** hook rtk nên **không rewrite** khi phiên hoặc agent đang ở worktree-isolated (phát hiện qua cwd `.claude/worktrees/`), hoặc không rewrite lệnh có `git`.

### F6 — Harness không có sổ lỗi của chính nó (🟠, gốc hệ thống)

Toàn bộ báo cáo này phải moi từ transcript thô. `failures.jsonl` (94 dòng) chỉ nhận lỗi mà agent **tự khai** qua failure-flywheel. Không có dòng nào ghi `stop.py` timeout, dù nó xảy ra 731 lần. Hook fail-open (`except Exception: pass`) nuốt lỗi.

**Fix đề xuất:**
1. Hook ghi `harness/metrics/hook-errors.jsonl` gồm hook, bước, loại (`timeout`/`exception`/`invalid-output`) và thời lượng. Ghi ở mọi chỗ đang `except: pass` và mọi bước bị bỏ vì hết ngân sách.
2. Đưa `scratchpad/harness-err/scan.py` vào thành `harness/scripts/hook-audit.py`: quét transcript N ngày và đếm `hook_cancelled`/`hook_*_error`. `medic` gọi nó như một probe, fail khi tỉ lệ timeout trên 5% số lượt Stop.
3. `self-report.py` thêm fingerprint `hook-timeout-rate` để downstream tự mở issue.

### F7 — Vòng đời issue CI tự động (🟡)

Trong 30 ngày có 10 issue "CI đỏ" (`skills-sync` và `harness`). #172 (skills-sync) và #167 (adapt-registry) vẫn OPEN, trong khi `sync-skills.py --check` và `adapt-registry.py --check` **hiện đều trả rc=0**. `ci-raise-issue` chỉ mở issue mà không đóng. **Fix:** khi workflow đó xanh trên cùng nhánh thì workflow tự đóng issue `ci-fail` tương ứng (khớp theo `workflow:`) và comment run_url xanh. Nhóm skills-sync đỏ lặp lại vì mirror `skills/` ↔ `llmwiki/skills/` bị lệch. Nên để pre-commit chạy `sync-skills.py` (không chỉ `--check`).

### F8 — Lỗi nhỏ, sửa một lần

- `bnal_config` / `hooklib` `ModuleNotFoundError` (7 lần) xảy ra khi script bị nạp qua `importlib` hoặc từ cwd khác. Fix: đầu mỗi script thêm `sys.path.insert(0, str(Path(__file__).parent))`, giống cách một số script đã làm.
- `orca-graph.py` `KeyError: 'T1'` (3 lần): `nodes[a.node]` trần. Fix: ở một chỗ chung (hàm lookup node), trả lỗi dạng *"node 'T1' không có — node hợp lệ: t1, t2…"* (không phân biệt hoa/thường). Engine nằm ở repo `Rheinmir/orca-graph`, nên sửa ở đó rồi re-pin.
- `orca-onboard` gọi `opencode/deepseek-v4-flash-free` thì bị "Model not found" hoặc "No payment method" (11/09). Model trong config đã chết. Theo memory, chỉ `mimo-v2.5-free` và `muse-spark-1.3` còn chạy.
- Issue Windows #168/#169 (HOME của WSL vs Windows, cp1252): đã có mô tả đầy đủ, chưa có fix. Đây là mảng portability riêng, không nằm trong gói hook.

## Thứ tự fix đề xuất

| Gói | Nội dung | Công | Hiệu quả |
|---|---|---|---|
| **A (làm ngay)** | F3 emit-một-lần · F4 loopback · F8 sys.path | ~1h | hết 35 + 10 + 7 lỗi, sửa từng điểm |
| **B** | F1 tách `stop.py` nhanh/nền + deadline + test ngân sách | ~3h | hết khoảng 731 timeout, cổng Stop cắn lại thật |
| **C** | F6 `hook-errors.jsonl` + `hook-audit.py` + probe medic | ~2h | lỗi hook tự hiện, không phải moi tay nữa |
| **D** | F2 checklist PreToolUse + `new-draft.py` · F5 luật zsh + rtk bỏ qua worktree · F7 tự đóng issue CI | ~3h | giảm khoảng 150 lượt bị chặn hoặc nhiễu |

## Cách tái lập

```bash
python3 scratchpad/harness-err/scan.py scratchpad/harness-err/raw.json   # quét 30 ngày transcript
echo '{"session_id":"probe"}' | CLAUDE_PROJECT_DIR=$PWD python3 scratchpad/harness-err/timeit.py >/dev/null  # đo stop.py
```

## Origin

- Transcript `~/.claude/projects/**/*.jsonl` (mtime ≤ 30 ngày, 389 file), quét bằng `scratchpad/harness-err/scan.py` ngày 2026-09-28.
- GitHub issues `Rheinmir/setup` tạo từ 2026-08-29 (`gh issue list --search created:>=2026-08-29`).
- Đo trực tiếp `llmwiki/.claude/hooks/stop.py`, `harness/scripts/egress-guard.py` (`check_bash`), `sync-skills.py --check`, `adapt-registry.py --check`.
