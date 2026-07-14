---
name: fdk-uat
description: >-
  UAT THẬT cho một bản framework sắp phát hành - dựng một dự án TRỐNG hoàn toàn mới, cài overstack
  đúng đường NGƯỜI MỚI (curl bootstrap từ GitHub raw, không phải file:// working-tree), rồi kiểm chứng
  năng lực MỚI của chính bản đó có tới tay người dùng không (skill reachable, rule CẮN thật, docs khớp).
  Vì curl chỉ kéo được thứ đã nằm trên remote, luồng này CỐ Ý push trước rồi mới test - và nếu UAT
  KHÔNG PASS thì TỰ GỠ commit vừa đẩy khỏi remote (revert hoặc reset), không để bản hỏng nằm lại.
  Gọi khi user nói "uat", "test thật", "test downstream", "kiểm tra người mới cài có chạy không",
  "acceptance", "/fdk-uat", hoặc trước khi công bố một bản có năng lực mới. KHÁC medic --ci và
  fresh-install-smoke (cả hai cài từ working-tree qua file:// nên KHÔNG chứng minh được đường remote).
---

# Skill: fdk-uat

## Vấn đề nó giải
`medic --ci` và `fresh-install-smoke --local` cài từ **working-tree** qua `file://`. Chúng chứng minh "code trong máy tôi lành", **không** chứng minh "người lạ `curl` về là chạy được". Hai thứ khác nhau: tarball thiếu file, `.gitignore` nuốt mất thứ cần ship, skill hỏng frontmatter bị CLI bỏ qua trong im lặng, engine global không refresh — mọi lỗi này chỉ lộ ra trên **đường remote thật**.

Nhưng đường remote chỉ tồn tại **sau khi push**. Đó là nghịch lý con-gà-quả-trứng, và cách duy nhất thoát ra là chấp nhận **push trước, test sau, hỏng thì gỡ**. Skill này chuẩn hoá chính vòng đó để nó an toàn.

## When to use
- Sắp công bố một bản có **năng lực mới** (skill mới, rule mới, engine mới).
- Nghi ngờ "doc hứa mà user không nhận được" (lớp lỗi GH#77).
- Sau khi `medic --ci` đã xanh — UAT là tầng TRÊN nó, không thay thế nó.

## Steps

### 0. Tiền đề — không được bỏ
```bash
python3 fdk/tools/medic.py --ci          # PHẢI xanh. Đỏ mà vẫn push là cố ý đẩy rác lên remote.
git status --short                        # sạch (không untracked lạc)
git log --oneline origin/<nhánh>..HEAD    # in ĐÚNG những commit sắp đẩy — ghi lại, đây là thứ sẽ gỡ nếu fail
```
**Ghi lại `BASE=$(git rev-parse origin/<nhánh>)`** — mốc để quay về.

### 1. Khai năng lực mới của bản này (checklist UAT)
Trước khi push, viết ra **cụ thể** bản này hứa gì mới. Mỗi dòng phải kiểm được bằng lệnh:
- Skill mới → `~/.claude/skills/<tên>/SKILL.md` tồn tại sau khi cài, và có trong `CAPABILITIES.md` của dự án mới.
- Rule mới → phải **CẮN THẬT** trong dự án mới (viết một file BAD → bị chặn; file GOOD → qua).
- Engine/tool mới → reachable trong global harness home.

Không khai được thành lệnh thì **không tính là năng lực** — đó là lời hứa suông.

### 2. Push (bước không thể tránh)
```bash
git push origin <nhánh>
```
Từ giây này, remote đang mang bản chưa được UAT. Bước 5 là cam kết dọn nếu hỏng.

### 3. Dựng dự án TRỐNG + cài như người mới
```bash
D=~/orca/overstack-uat-$(date +%y%m%d-%H%M)
mkdir -p "$D" && cd "$D" && git init
curl -fsSL https://raw.githubusercontent.com/<owner>/<repo>/<nhánh>/harness/poc-vendor-neutral/bootstrap.sh | bash
git add -A && git commit -m "fresh overstack install"    # Orca cần ≥1 commit mới nhận repo
```

### 4. UAT — chạy checklist bước 1 trong dự án ĐÓ
Tối thiểu, theo `fdk/docs/fresh-install-gate.md`:
1. **3 trụ có mặt:** `harness/poc-vendor-neutral/policy.yaml` · `.claude/settings.json` · `.pre-commit-config.yaml` · `llmwiki/wiki/index.md` · `CAPABILITIES.md`.
2. **Harness cắn thật:** `bash harness/poc-vendor-neutral/test-broad.sh` → PASS (validator GOOD-pass / BAD-block).
3. **Năng lực MỚI tới tay** — phần riêng của bản này (checklist bước 1). Đây là mục hay bị bỏ nhất, và cũng là mục duy nhất chứng minh bản MỚI có giá trị.
4. **Orchestration-ready:** skill `orchestration` / `orca-cli` / `orca-dispatch-reference` reachable.
5. *(tuỳ chọn — thấy được bằng mắt)* dựng workspace Orca thật:
```bash
orca repo add --path "$D" --json                          # CHÚ Ý: --path, KHÔNG positional
orca worktree create --repo id:<repoId> --name uat --agent claude \
                     --setup skip --no-parent --activate --json
```
> Cạm bẫy đã dính: `orca repo add <path>` positional → `Unknown command`. Repo chưa có commit → Orca không nhận. `repo add` **không** làm workspace hiện trong app — phải `worktree create`.

### 5. KHÔNG PASS → gỡ commit khỏi remote NGAY
Chọn theo tình huống, đừng để bản hỏng nằm lại:
```bash
# (a) Nhánh chia sẻ / đã có người kéo → REVERT (không viết lại lịch sử):
git revert --no-edit <sha>..HEAD && git push origin <nhánh>

# (b) Nhánh chỉ mình dùng, vừa đẩy xong, chắc chắn chưa ai kéo → RESET:
git reset --hard "$BASE" && git push --force-with-lease origin <nhánh>
```
`--force-with-lease` chứ **không** `--force`: nếu trong lúc đó có người đẩy lên, lệnh sẽ từ chối thay vì xoá mất việc của họ.

Gỡ xong: ghi lại **vì sao fail** vào `llmwiki/html/fdk-problem-tree.html` (node mới, `status: open`) — thất bại UAT là dữ liệu, không phải chuyện xấu hổ.

### 6. PASS → chốt
- Dọn dự án UAT (hoặc giữ lại `--keep` nếu cần soi).
- Ghi kết quả (số đo thật, không phải lời hứa) vào `wiki/log.md`.
- Bản trên remote coi như đã được nghiệm thu ở tầng "người mới cài".

## Rules
- **Không bao giờ push rồi bỏ mặc.** Đã push để UAT thì phải chạy UAT trong cùng phiên. Push xong đi ngủ là để lại một bản chưa nghiệm thu cho người khác kéo về.
- **Không đếm skill/rule bằng trí nhớ** — đếm LIVE trong dự án vừa cài. Con số trên đĩa repo **không** phải con số tới tay người dùng (đã cháy: doc báo 74 skill, installer giao 67 — 7 skill hỏng frontmatter bị CLI nuốt im lặng).
- **Rule mới phải CẮN, không chỉ có mặt.** File `policy.yaml` có dòng luật ≠ luật chặn được. Luôn test bằng một file BAD thật.
- **Trần (ceiling) cố ý:** UAT headless không spin được model LLM, nên "`/orchestration` chạy được" chỉ kiểm ở mức tất định (cài đủ + reachable + ping runtime). Live-run bằng model thật vẫn là acceptance làm tay.
- Fail thì **gỡ**, không "để đó sửa sau". Remote là thứ người khác kéo về.

## Origin
- Luồng distill từ `fdk/docs/fresh-install-gate.md` (§ "Luồng chuẩn: dựng workspace Orca mới rồi test fresh-install") + yêu cầu của user 2026-07-14: cho phép push trước để test thật, không pass thì gỡ commit khỏi remote.
