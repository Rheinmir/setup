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

## Cổng gác chính nó: model ở dự án local có BIẾT framework có gì mới không?

Hai câu hỏi khác nhau, phải gác riêng:

1. **"Model có biết framework tồn tại và có đồ nghề gì?"** → cần `CAPABILITIES.md` ở gốc dự án. Hook `session_start.py` (global, kích hoạt khi thấy `llmwiki/.harness-stamp`) sẽ trỏ model tới file này. **Trước đây không ai sinh nó** → hook câm → cài xong mà model vẫn mù. Nay `install.sh` chạy `build-capabilities.py --root` và hợp đồng đưa `CAPABILITIES.md` vào `must_exist` → không tái phát được.

2. **"Dự án có biết mình đang CŨ không?"** → `session_start.py` so `.harness-stamp.guarded_by` (dự án) với `version.json.template_version` (global). Cơ chế này *có sẵn và đúng* — **nhưng tín hiệu của nó từng chết**: không gì ép bump version khi framework thêm năng lực, nên cả hai đầu cùng `1.3.6` và dự án tưởng mình current mãi mãi (đây là **p-08**).

### `capability-stamp.py` — forcing function cho (2)

Đóng dấu **bề mặt năng lực** thành một sha: `skills/*/SKILL.md` (tên + trigger) · rule id trong `policy.yaml` · engine trong `harness/scripts/` + `llmwiki/.claude/hooks/`. Cố ý **không** hash nội dung engine — sửa một dòng log trong `council.py` không phải "năng lực mới"; thứ downstream cần biết là *danh sách và trigger*.

```
python3 harness/scripts/capability-stamp.py --check    # sha đĩa ≠ sha trong version.json → exit 1
python3 harness/scripts/capability-stamp.py --update   # ghi sha + bump template_version
```

Probe medic **`capsurface`** gọi `--check`. Đổi bề mặt mà chưa bump → `medic --ci` ĐỎ → **không push được**. Không phải lời nhắc — là bị chặn.

### Chuỗi đầy đủ — và mắt xích từng đứt ở đâu

```
[thêm năng lực]
   │  ① capsurface CHẶN PUSH tới khi bump          (forcing function — trước đây KHÔNG có)
   ▼
[harness/version.json: 1.3.6 → 1.3.7]
   │  ② user re-curl bootstrap → install.sh thấy global CŨ → refresh global
   ▼                                              (trước đây chỉ cài KHI VẮNG → global kẹt mãi)
[global harness: 1.3.7]
   │  ③ hook harness_integrity so stamp(1.3.6) ≠ global(1.3.7) → in ⟳ nhắc re-curl
   ▼
[dự án re-curl → stamp 1.3.7 + CAPABILITIES.md regen]
   ▼
[model đọc CAPABILITIES.md → BIẾT mình có đồ nghề mới]
```

**Hai mắt xích từng đứt (đều đã vá + verify bằng chạy thật):**

- **①** không gì ép bump → framework thêm cả một cổng mới mà version vẫn `1.3.6` → mọi mũi tên sau không bao giờ khởi động. → `capability-stamp.py` + probe `capsurface`.
- **②** `install.sh` chỉ cài global **khi VẮNG** → re-curl **không** refresh global → global kẹt bản cũ → `stamp == global` → hook `harness_integrity` thấy bằng nhau → **im lặng tuyệt đối**. → nay so version, khác thì cập nhật.

**③ vốn đã đúng từ trước** (hook có sẵn nhánh non-major) — nó chỉ câm vì ② không bao giờ cho global mới hơn stamp.

**Đã verify từng bước, không suy luận:**
- Hạ global về `1.3.5` → chạy install → log `global harness CŨ (v1.3.5 → v1.3.7) → cập nhật` → global thành `1.3.7` ✓
- Dự án stamp `1.3.6` + global `1.3.7` → chạy hook thật → in `⟳ [harness-integrity] stamp v1.3.6 ≠ global v1.3.7` ✓

## Bảng năng lực có ONDATE không? — 7 skill từng biến mất không dấu vết

Bản đồ downstream sinh từ **skills GLOBAL** (npx kéo từ GitHub) + policy đã cài. Nên nó chỉ đúng tới mức npx *thật sự kéo được*. Đo ngày 2026-07-11:

- `npx skills add … --all` báo **"Installed 67 skills"** — trong khi repo có **74**.
- **7 skill không bao giờ tới tay ai:** `web-crawl` · `web-clone` · `harness-tour` · `harness-update` · `health-check` · `trace-grader` · `uat-nonit-testcase`.

### Nguyên nhân: frontmatter YAML hỏng → CLI nuốt skill trong im lặng

`description:` inline chứa `": "` chưa quote → YAML `ScannerError: mapping values are not allowed here` → CLI `skills` **bỏ qua skill, không in một dòng lỗi nào**. Skill không vào global → không vào `CAPABILITIES.md` → **người dùng vĩnh viễn không biết năng lực đó tồn tại**. Framework có 74 năng lực nhưng chỉ giao được 67, và không ai hay.

Sửa: gấp description thành block YAML (giữ nguyên nội dung).

```yaml
description: >-
  Dòng 1 của mô tả…
  Dòng 2…
```

**Đã verify đầu-cuối:** sửa 7 skill → `npx` báo **"Installed 74 skills"** → cả 7 vào global → bản đồ downstream **80 → 82 skill** (2 cái mới, 5 cái kia vốn còn sót bản cũ).

### Điều tệ nhất: tài liệu KHÔNG thiếu — nó NÓI QUÁ

`overstack.html` và `CAPABILITIES.md` đều đọc từ **đĩa**, nên cả hai luôn báo **74 skill** — kể cả khi installer chỉ giao **67**. Ba nguồn soi lẫn nhau và cùng đúng *với nhau*, cùng **sai** so với thứ thật sự tới tay người dùng. Không cái nào soi ra ngoài.

Người dùng đọc doc thấy `/web-crawl`, gõ vào → **không có gì**. Đây là mất uy tín trực tiếp.

### Hai lớp gác (nguyên nhân + hệ quả)

| Lớp | Gác gì | Ở đâu |
|---|---|---|
| **Nguyên nhân** | frontmatter YAML hỏng → CLI nuốt skill | probe `capsurface` |
| **Hệ quả** | *bất kể nguyên nhân gì*: skill trên đĩa mà không tới được người dùng | **parity hứa↔giao** trong `fresh-install-smoke` (GH#77) |

Cả hai đều nằm trong `medic --ci` → **chặn push**. Cần cả hai: `capsurface` chỉ biết một nguyên nhân đã gặp; parity bắt **mọi** nguyên nhân — skill không đăng ký `marketplace.json`, CLI đổi luật validate, tarball lỗi, mạng đứt giữa chừng.

> **Bẫy đã dính (2026-07-11):** parity ban đầu bị nhét vào riêng nhánh `--remote`, trong khi cổng required chạy `--local` → **parity không bao giờ chạy trong cổng**, chỉ chạy khi có người nhớ gõ tay. Đúng bệnh mà cả cổng này sinh ra để chống: *guard phải-nhớ-gọi = guard không tồn tại*. Nay parity chạy ở **mọi mode** (nó chỉ so đĩa ↔ global, không cần mạng).

**Negative-test qua chính cổng required:** xoá `web-crawl` khỏi global → `medic freshinstall` **FAIL**. Không phải chạy tay mới thấy.

### Gác: đừng đoán, hãy PARSE

Probe `capsurface` (qua `capability-stamp.py`) nay **parse frontmatter bằng YAML thật** và ĐỎ nếu skill nào hỏng.

> Hai giả thuyết SAI đã thử và bị bác bỏ, ghi lại để khỏi đi lại: **(a)** "description dài quá thì bị drop" — sai, `brandkit` 464 ký tự vẫn ship; **(b)** "chứa `': '` là hỏng" — sai, `ship`/`raise-issue`/`frontier-scan` đều có mà vẫn ship. Chỉ **parser thật** mới phân biệt được. Heuristic regex ở đây tạo cả false-positive lẫn false-negative.

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
