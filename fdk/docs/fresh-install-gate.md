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

## Hợp đồng downstream — chặn "xanh trong repo, hỏng ở downstream"

`harness/downstream-contract.yaml` khai thứ một dự án **cài mới BẮT BUỘC** phải có; smoke assert từng dòng: `must_exist` · `must_bite` · `must_reach_skills` · **`must_reach_global_engines`** · `rule_parity`.

### Kiến trúc — ĐỌC TRƯỚC KHI "SỬA"

Engine **không** sống trong project. Chúng sống ở **global harness home** (`$OVERSTACK_HARNESS_HOME`, mặc định `~/.claude/harness/` — gồm `hooks/`, `harness/`, `fdk/`, `version.json`). `install.sh` còn **chủ động xoá** bản engine per-project (khối **U10**) vì bản global mới là bản dùng. Skill global trỏ tới `~/.claude/harness/…` là **đúng thiết kế**, không phải "quên ship".

> Đây là cái bẫy dễ hiểu sai nhất trong installer: thấy `harness/scripts/*` vắng mặt trong dự án cài mới rồi kết luận "installer quên ship" — rồi đi "sửa" bằng cách ship engine vào project, để chính U10 xoá lại. Nếu bạn định chạm vào chỗ này: đọc U10 trước.

### Gap thật mà gate gác

`install.sh` gọi `install-harness.sh --global` ở chế độ **FAIL-OPEN** (cố ý: lỗi global không chặn install project). Hệ quả: bước đó hỏng thì project vẫn báo **"cài thành công"**, nhưng **mọi engine của skill biến mất** — người dùng nhận một overstack **rỗng ruột** mà không ai báo.

`must_reach_global_engines` bịt đúng lỗ đó: sau fresh install, các engine chủ chốt phải reachable trong global harness, không thì gate **ĐỎ** kèm lệnh sửa (`install-harness.sh --global`).

**Đã negative-test cả hai chiều:** trỏ `OVERSTACK_HARNESS_HOME` vào thư mục rỗng → gate **FAIL** đúng như thiết kế; khai một `must_exist` không được ship → gate cũng **FAIL**. Cổng biết cắn, không phải đồ trang trí.

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
