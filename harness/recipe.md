# Harness Recipe — kiến trúc 5 lớp, vendor-agnostic

> Mục đích: đây là **recipe kiến trúc**. Khi cần đem llmwiki harness sang một CLI vendor khác
> (Codex, OpenCode, Gemini CLI, Cursor...), đọc file này + context của vendor đó là cook ra
> bản mới ngay — không thiết kế lại từ đầu.

## 1. Kiến trúc 5 lớp

```
L0 POLICY      harness/policy.yaml — bất biến R1..R6, thuần khai báo. KHÔNG dính vendor.
L1 SESSION     adapter mỏng theo vendor — chặn realtime trong phiên agent.
               Chỉ làm 1 việc: normalize event của vendor → gọi validators → block theo exit code.
L2 REPO        .pre-commit-config.yaml — backstop tại git. 100% vendor-neutral:
               agent nào (hay người nào) commit cũng bị gate. Đây là hàng rào cứng cuối cùng.
L3 AUDIT       hook append JSONL (.claude/audit/*.jsonl) + ccusage (đã multi-vendor sẵn).
               log.md sinh từ máy, model không thể "quên log".
L4 EVALS       wiki-health.py (0 token, vendor-neutral) + promptfoo golden questions
               (đổi provider = đổi vendor).
```

**Bất biến thiết kế:** logic enforcement chỉ sống ở `harness/validators/` — L1 của mọi vendor
đều là wrapper mỏng. ~80% hệ thống (L0, validators, L2, L4) dùng lại nguyên xi khi đổi vendor.

## 2. Contract của validator (trái tim của recipe)

Mỗi rule trong `policy.yaml` có một validator Python độc lập, hai chế độ gọi:

```
Chế độ stdin (L1 — realtime):           Chế độ argv (L2 — pre-commit/CLI):
  echo '<event-json>' | validator.py      validator.py file1.md file2.md ...
                                          index_sync.py --wiki-dir path/wiki
Exit code:  0 = pass    2 = vi phạm (lý do trên stderr, viết cho agent đọc và tự sửa)
```

Normalized event JSON (L1 adapter của vendor nào cũng phải quy về dạng này):

```json
{ "action": "write" | "bash" | "stop",
  "file_path": "wiki/concepts/x.md",   // action=write
  "content": "...",                     // optional; thiếu thì validator đọc disk
  "command": "...",                     // action=bash
  "wiki_dir": "path/to/wiki" }          // action=stop
```

Validators hiện có: `no_write_raw.py` (R1) · `origin_required.py` (R2) · `index_sync.py` (R3) ·
`folder_structure.py` (R5) · `proposal_complete.py` (R7 — proposal chờ duyệt phải có bảng Agent
Task Assignment + seq diagram per-task). R4 = tự động hóa L3, R6 = chính pre-commit (xem policy.yaml).

## 3. Bản tham chiếu: Claude Code (vendor đầu tiên)

| Enforcement point | File | Việc |
|---|---|---|
| `permissions.deny` | `llmwiki/.claude/settings.json` | Chặn Write/Edit vào `raw/**` trước cả hook |
| PreToolUse (block được) | `.claude/hooks/pre_tool_use.py` | normalize Write/Edit/Bash → R1, R5; exit 2 = deny tool call |
| PostToolUse | `.claude/hooks/post_tool_use.py` | audit JSONL + R2 trên file đã ghi; exit 2 = Claude phải sửa ngay |
| Stop (block được) | `.claude/hooks/stop.py` | nếu phiên sửa wiki → R3; exit 2 = không cho kết thúc lượt. Guard `stop_hook_active` chống lặp |
| SessionEnd | `.claude/hooks/session_end.py` | audit + append dòng tổng kết vào `wiki/log.md` |
| SessionStart (advisory) | `.claude/hooks/code_graph_keeper.py` | giữ luồng code-graph MCP bền: re-register repo vào `~/.graph-agent/repos.txt` nếu rớt + cảnh báo repo chưa index. **No-op nếu project không có `.graph-agent/index.db`** (không dùng code-graph). Không bao giờ block, không reindex per-edit (watcher của code-graph server đã lo) |

Resolve validators theo thứ tự: env `LLMWIKI_VALIDATORS` → `.claude/hooks/validators/` (bản copy
khi deploy standalone) → `harness/validators/` ở repo cha. Hook luôn **fail-open** (không tìm thấy
validator thì cho qua) — L2 vẫn đỡ, và phiên làm việc không bao giờ bị brick vì harness lỗi.

## 4. Cook bản vendor mới — 4 bước

1. **Viết adapter L1** — tìm enforcement point tương đương của vendor (bảng §5), viết wrapper
   normalize payload của vendor → event JSON §2 → subprocess validator → map exit 2 sang cơ chế
   block của vendor. Thường < 100 dòng.
2. **Trỏ L3** — tìm transcript/log format của vendor, thêm parser append cùng schema JSONL
   (`ts, event, session_id, tool_name, file_path, command`). ccusage hỗ trợ sẵn 15+ CLI.
3. **Đổi provider L4** — sửa block `providers:` trong `harness/evals/promptfooconfig.yaml`
   (promptfoo có sẵn provider cho Codex SDK, Claude Agent SDK...).
4. **L0 + validators + L2 giữ nguyên.** Copy `.pre-commit-config.yaml` sang repo root của
   project mới, sửa prefix đường dẫn (`llmwiki/wiki` → vị trí wiki thực tế).

## 5. Bảng enforcement point per vendor

| Vendor | Block realtime (≈PreToolUse) | Post-edit feedback | Chặn kết thúc lượt | Mức enforcement đạt được |
|---|---|---|---|---|
| **Claude Code** | hooks PreToolUse exit 2 / `permissionDecision: deny` + `permissions.deny` | PostToolUse exit 2 | Stop hook exit 2 | **Đủ cả 3 tầng — chuẩn tham chiếu** |
| **OpenCode** | plugin `tool.execute.before` (throw = block) | `tool.execute.after` | event `session.idle` (không block cứng) | Realtime tốt; tầng stop yếu → dồn vào L2 |
| **Cursor** | hooks (beta 2026) `beforeShellExecution`/file edit | có (audit) | không | Trung bình → L2 là gate chính |
| **Codex CLI** | sandbox/approval policy (không có hook block tùy ý) | không | không | Yếu nhất → **L2 là gate cứng duy nhất**; cân nhắc statewright |
| **Gemini CLI** | kiểm tra version hiện tại khi cook (hook system thay đổi nhanh) | — | — | Xác định lúc cook |
| **Mọi vendor** | — | — | — | **L2 pre-commit luôn hoạt động** — đó là lý do nó tồn tại |

> Cross-vendor engine: [statewright](https://github.com/statewright/statewright) (Rust, Apache 2.0,
> deterministic, tích hợp Claude Code/Codex/Cursor/opencode qua MCP+hooks) — ứng viên thay toàn bộ
> L1 bằng một engine duy nhất nếu số vendor nhiều lên. Hiện để ở mức PoC (Task 8).

## 6. Cân bằng chi phí

| Lớp | Tần suất chạy | Chi phí token | Slash command mới |
|---|---|---|---|
| L0-L2 | mỗi tool call / mỗi commit | **0** (Python/shell local) | 0 |
| L3 | mỗi event | **0** (append file; ccusage parse local) | 0 |
| L4 tĩnh | cron/pre-commit | **0** | 0 |
| L4 LLM | weekly | ~$1-5/lượt (generation only, không judge) | 0 |

Nguyên tắc: thứ gì chạy thường xuyên phải là 0 token; LLM chỉ xuất hiện ở eval định kỳ tắt được.

## 6b. wiki-graph downstream — opt-in & scope code (GH#69)

`llmwiki/html/wiki-graph.html` là bản đồ quan hệ wiki + code-graph cho người xem. Ở repo framework nó luôn
tự sinh; ở dự án **downstream** nó chỉ chạy khi bật opt-in (triết lý Taleb: engine chạy trên máy người khác
thì không tự-bật ngầm). `install-harness.sh` lo sẵn cả hai điều kiện nên **không cần set tay**:

- **Bật opt-in.** Ghi `env.OVERSTACK_WIKIGRAPH="1"` vào `.claude/settings.json` ở root dự án (dùng
  `setdefault` nên không đè giá trị bạn đã đặt). Tắt lại: đổi thành `"0"` hoặc xoá khoá.
- **Khai vùng quét code.** Sinh `.overstack.yaml` ở root với hai khoá:

  ```yaml
  wiki_dir: llmwiki/wiki
  # code_root: MỘT hay NHIỀU vùng code, ngăn bằng dấu phẩy (đa sub-repo downstream)
  code_root: payroll-backend-prd, payroll-frontend-prd, syncservice-develop
  ```

  Autodetect lúc cài = các thư mục con NGAY dưới root có `.git` lồng (sub-repo clone); không thấy → `code_root: .`.
  Mỗi vùng phải **nằm trong** cwd — id node = path tương-đối-cwd nên khớp quan hệ `touches` (wiki ghi theo
  repo-root) và không đụng nhau khi hai sub-repo cùng có `app/main.py`. Sửa file này để thu hẹp/relocate.
- **Khi nào vẽ.** Stop hook regen wiki-graph khi git-status có đổi ở `wiki/`, engine, hoặc file code; ngoài ra
  `install-harness` seed-once ngay lúc cài (nếu wiki đã có nội dung) để vector tồn tại mà không phải chờ diff.

## 7. Nguồn (crawl verified 2026-06-10)

- [ai-boost/awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering) (1.8k★) — khung 12 primitive
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) — pattern 13 hook events
- [dwarvesf/claude-guardrails](https://github.com/dwarvesf/claude-guardrails) (v0.3.8, 04/2026) — deny rules + npx installer
- [ryoppippi/ccusage](https://github.com/ryoppippi/ccusage) (15.9k★, v20.0.9 09/06/2026) — multi-vendor cost tracking
- [promptfoo — evaluate coding agents](https://www.promptfoo.dev/docs/guides/evaluate-coding-agents/) — provider `anthropic:claude-agent-sdk`
- [statewright](https://statewright.ai/) — state-machine guardrails cross-vendor
- [pre-commit](https://pre-commit.com) · [lychee](https://github.com/lycheeverse/lychee) · [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2)
