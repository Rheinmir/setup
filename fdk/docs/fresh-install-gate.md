# Cổng fresh-install → orchestration (probe `freshinstall`)

> Runbook nội-bộ framework. Đặt tại `fdk/docs/` vì đây là tài liệu người-đọc (không phải wiki OKF).
> Distill 2026-07-11 từ một plugin học-tập cộng đồng: *một guard phải TỰ chạy — cái gì phải-nhớ-gọi sẽ bị bỏ đúng lúc cần nhất*. Nguồn chỉ để tham khảo ý tưởng, không kèm tác giả/repo.

## Vấn đề nó giải

Overstack có đường cài (`bootstrap.sh` → `install.sh`) và có bộ skill orchestration, nhưng trước đây **không có cổng nào chứng minh** rằng "một người mới `curl`-cài overstack vào một dự án trống là chạy được `/orchestration` ngay". Đường cài có thể hỏng âm thầm — mọi test khác vẫn xanh trong khi trải nghiệm người-mới đã gãy. Đây đúng là loại lỗi mà một guard *tự chạy* mới bắt được, còn một bước test *phải nhớ làm tay* thì sẽ bị bỏ qua.

## Nó làm gì

`harness/scripts/fresh-install-smoke.sh` cài overstack vào một thư mục **cô lập** (`mktemp`, nằm ngoài repo dev — có guard `FATAL` nếu thư mục lỡ rơi vào trong repo), rồi kiểm chứng theo tầng:

1. **Cài như người mới** — chạy `bootstrap.sh` thật.
2. **3 trụ có mặt** — `harness/poc-vendor-neutral/policy.yaml`, `.claude/settings.json`, `.pre-commit-config.yaml`, `llmwiki/wiki/index.md`.
3. **Harness cắn thật** — chạy `test-broad.sh` trong dự án mới (validator GOOD-pass / BAD-block), không chỉ kiểm tra file tồn tại.
4. **Orchestration-ready** — các skill `orchestration`, `orca-cli`, `orca-dispatch-reference` reachable (global `~/.claude/skills`).
5. **Ping runtime** — nếu `orca` CLI có trên PATH và runtime đang bật thì ping; vắng thì **SKIP (không fail)**.

## Ba chế độ

| Lệnh | Dùng khi | Mạng |
|---|---|---|
| `fresh-install-smoke.sh` (mặc định `--local`) | Cổng pre-push: cài từ working-tree qua `file://` (offline, tất định) | Không |
| `fresh-install-smoke.sh --remote` | Acceptance: `curl` thật từ GitHub raw đúng đường người-mới (gồm `npx skills`) | Có |
| `fresh-install-smoke.sh --self-test` | Tự kiểm cấu trúc script, không cài gì | Không |

Thêm `--keep` để giữ lại thư mục cô lập mà soi.

## Là cổng REQUIRED của push

Probe `freshinstall` đã cắm vào `fdk/tools/medic.py`. Vì `/fdk` và `/ship` đều chạy `medic --ci` trước khi đẩy, một fresh-install hỏng sẽ làm `medic --ci` đỏ → **không push được**. Đường cài người-mới không còn rot âm thầm.

```
python3 fdk/tools/medic.py freshinstall   # chỉ chạy probe này
python3 fdk/tools/medic.py --ci           # toàn cổng (gồm freshinstall)
```

## Hợp đồng downstream — chặn "xanh trong repo, vắng ở downstream"

`harness/downstream-contract.yaml` khai thứ một dự án **cài mới BẮT BUỘC** phải có; smoke assert từng dòng (`must_exist` · `must_bite` · `must_reach_skills` · `rule_parity`).

**Vì sao cần:** installer **hardcode** danh sách file. Bạn có thể dev xong một tính năng trong repo framework, test xanh hết, mà installer không ship file đó → **người dùng downstream không hề có nó**. "Xanh trong repo" ≠ "đúng ở downstream".

**Luật dùng:** dev một tính năng *hướng downstream* → **thêm vào hợp đồng TRƯỚC**. Gate sẽ đỏ cho tới khi installer thật sự ship được. Không phải "nhớ kiểm tra" — mà là **bị chặn**.

Đã negative-test để chắc cổng biết cắn: khai `harness/scripts/council.py` (thứ fdk có, installer không ship) → gate **FAIL** đúng như thiết kế, kèm gợi ý sửa `install.sh`/`bootstrap.sh`.

**Nợ đã biết (khai thẳng, không allowlist ngầm):** `harness/scripts/*` (council, claim-receipts, mem-rank…) và `CAPABILITIES.md` **chưa** được ship xuống downstream — dù `llmwiki/CLAUDE.md` có nhắc downstream sẽ có `CAPABILITIES.md`. Cố ý *chưa* đưa vào `must_exist` vì fix đúng là **install theo manifest (GH#51)** + **ship engine downstream (GH#41)**, không phải vá danh sách. Hai issue đó xong → nâng các dòng nợ lên `must_exist`.

## Ceiling (giới hạn cố ý)

Một cổng headless **không** spin được model LLM + Orca runtime, nên "`/orchestration` chạy được" chỉ được kiểm ở mức **tất định**: stack đã cài đủ + reachable + (ping runtime nếu máy đang bật). **Live-run `/orchestration` bằng model thật vẫn là acceptance làm tay** — đó là ngưỡng trên, không nhồi vào cổng để cổng khỏi flaky (một cổng required mà chập chờn thì chặn nhầm mọi push).

## Vết liên quan

- Script: `harness/scripts/fresh-install-smoke.sh`
- Cổng: `fdk/tools/medic.py` (probe `freshinstall`)
- Checklist push: `skills/ship/SKILL.md` §1
- Sổ vấn đề: node `p-freshinstall` trong `llmwiki/html/fdk-problem-tree.html`

## Luồng chuẩn: dựng workspace Orca mới rồi test fresh-install (2026-07-11)

Đây là luồng **tham khảo được** — chạy lại y hệt là ra kết quả. Cạm bẫy chính nằm ở bước 3.

```bash
# 1) Dự án mới, trống, CÔ LẬP (ngoài repo dev)
mkdir -p ~/orca/overstack-fresh-e2e && cd ~/orca/overstack-fresh-e2e && git init

# 2) Cài như NGƯỜI MỚI — curl github raw thật (gồm npx skills global)
curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash
git add -A && git commit -m "fresh overstack install"      # cần 1 commit trước khi Orca nhận

# 3) Đăng ký repo vào Orca  (CHÚ Ý: --path, KHÔNG phải positional)
orca repo add --path ~/orca/overstack-fresh-e2e --json

# 4) Tạo WORKSPACE thật — đây mới là thứ app HIỆN
orca worktree create --repo id:<repoId> --name fresh-e2e --agent claude \
                     --setup skip --no-parent --activate --json
```

**Cạm bẫy đã dính (ghi lại để khỏi dính lại):**
- `orca repo add <path>` (positional) → `Unknown command`. Phải là `--path <path>`.
- Repo chưa có commit nào → Orca không nhận. Commit trước.
- **`orca repo add` KHÔNG làm workspace hiện trong app.** Nó chỉ ghi vào state (thấy ở `orca repo list`). Thứ app vẽ trên sidebar là **worktree** — nên phải `orca worktree create` (bước 4) thì mới nhìn thấy. Đây là lỗi đã mắc lần đầu: tưởng `repo add` là xong.

## Kết quả chạy thật

Workspace sinh ra: `~/orca/workspaces/overstack-fresh-e2e/fresh-e2e` (branch `fresh-e2e`), có terminal agent `✳ Claude Code` — hiện trong app.

| Kiểm | Kết quả |
|---|---|
| 3 trụ có mặt (policy / settings / pre-commit / wiki index) | ✓ đủ 4/4 |
| Harness **cắn thật** — `test-broad.sh` chạy trong dự án mới | ✓ PASS (81 dòng output) |
| `test-broad.sh` chạy lại **trong workspace Orca** | ✓ PASS |
| Skills `orchestration` / `orca-cli` / `orca-dispatch-reference` reachable | ✓ đủ 3/3 (global) |
| `orca status` runtime | ✓ UP → `/orchestration` live-able |

**Kết luận:** người mới `curl`-cài overstack vào một dự án trống là có ngay 3 trụ + orchestration-ready — chứng minh trên **workspace Orca thật nhìn thấy được**, không phải chỉ thư mục tạm. (Ceiling giữ nguyên: live-run `/orchestration` bằng model vẫn là acceptance tay.)
