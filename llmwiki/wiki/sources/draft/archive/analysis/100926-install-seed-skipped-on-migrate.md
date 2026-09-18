---
type: issue
kind: tech-debt
title: "install-harness.sh chỉ seed khung llmwiki ở MODE=new — project migrate thiếu thư mục vĩnh viễn"
status: done
assignee: "@Rheinmir"
dispatch: Claude
entry: /fdk
priority: P2
tags: [issue, install, migrate, llmwiki, seed, uat]
timestamp: 2026-09-10
id: 100926-install-seed-skipped-on-migrate
source_session: "Phiên chạy thử game rhein-farm/walleye — user hỏi vì sao không thấy thư mục inbox tài liệu trong llmwiki, truy ngược ra installer"
---

# Issue: install-harness.sh chỉ seed khung llmwiki ở MODE=new

## Vấn đề (một câu)

`MODE` được quyết bằng đúng một phép thử `[ -d "$ROOT/llmwiki" ]`, nên project nào
đã có sẵn **một** thư mục con bất kỳ dưới `llmwiki/` sẽ vĩnh viễn rơi vào `migrate`
và không bao giờ được bổ sung những thư mục còn thiếu — chạy lại installer bao
nhiêu lần cũng vậy.

## Bối cảnh & bằng chứng

`harness/scripts/install-harness.sh` trước commit `c1b3814`:

```sh
487: if [ -d "$ROOT/llmwiki" ]; then MODE="migrate"; else MODE="new"; fi
...
492: if [ "$MODE" = "new" ]; then
493:   mkdir -p "$ROOT/llmwiki/wiki"/{concepts,entities,sources/adr,sources/draft,draft/orca} \
494:            "$ROOT/llmwiki"/{raw,html,skills}
495:   touch "$ROOT/llmwiki/raw/.gitkeep"
496:   [ -f "$ROOT/llmwiki/wiki/index.md" ] || printf ... 
497:   [ -f "$ROOT/llmwiki/wiki/log.md" ]   || printf ...
498: fi
```

Khối 492–498 là **chỗ duy nhất** trong installer tạo inbox tài liệu và
`llmwiki/skills/`. Nằm trọn trong `if MODE = new` nên nhánh migrate không chạm tới.

**Đo thật trên `rhein-farm/walleye`** (2026-09-10):

- `llmwiki/` có `wiki/` và `html/`, **thiếu cả inbox tài liệu lẫn `skills/`** — đúng
  hai thứ chỉ khối đó tạo ra.
- `git log --all -- '*<inbox>/*'` → **rỗng**: chưa từng có commit nào đụng tới, tức
  không phải bị xoá mà là **chưa từng được tạo**.
- `.gitignore` không hề nhắc tới nó → nếu từng có file thì git đã thấy.
- Nguyên nhân rơi vào migrate: `llmwiki/wiki/sources/draft/050926-nong-trai-vui-ve-brd-prd.md`
  (tài liệu BRD nguồn) được đặt vào trước, tạo ra `llmwiki/` → mọi lần chạy sau là migrate.

**Hệ quả người dùng thấy:** không có chỗ để thả tài liệu/ảnh vào cho `/br interview`
và `/ingest` đọc. Người dùng đi tìm thư mục theo tài liệu hướng dẫn thì không thấy,
và tự tay `mkdir` thì bị hook `R1 no-write-raw` chặn nếu nhờ agent làm.

Liên quan (không trùng): [[040926-downstream-dot-layout]] — cũng về layout thư mục
do installer đặt ra, nhưng ở `harness/poc-vendor-neutral/install.sh` và về chuyện
có/không dấu chấm, không phải về nhánh migrate bỏ seed.

Đối chiếu: `harness/poc-vendor-neutral/install.sh:263` tạo đủ thư mục, nhưng chỉ khi
`WITH_WIKI=1` — cài `--harness-only` thì cũng không có, và đó là **chủ ý** (không cài
trụ wiki), khác bản chất với lỗi này.

## Phạm vi

- `harness/scripts/install-harness.sh` — khối seed khung llmwiki (dòng ~491–498).
- Ảnh hưởng **mọi project downstream** đã cài từ trước và mọi project có `llmwiki/`
  được tạo bởi bước khác trước khi chạy installer. Universal, không local.

## Không thuộc phạm vi

- `harness/poc-vendor-neutral/install.sh` — hành vi `WITH_WIKI` ở đó là chủ ý, không sửa.
- Việc dọn/backfill các project downstream đã lỡ thiếu thư mục — nếu cần thì là issue riêng.
- Luật `R1 no-write-raw`. Nó đúng; chỉ ghi nhận rằng nó chặn cả lệnh bash *nhắc tới*
  đường dẫn inbox (kể cả khi đang sửa source của installer hoặc ghi vào tmp) — false
  positive đáng xem lại ở một issue khác.

## Hướng gợi ý

Đã áp ở `c1b3814`: đưa `mkdir -p` + `touch` ra ngoài `if MODE = new`. Cả hai đều
idempotent, `index.md`/`log.md` đã có guard `[ -f ] ||`, nên chạy ở migrate không đè
gì của project đang có.

## Tiêu chí HOÀN THÀNH

1. Project **mới trắng** cài xong có đủ khung — như trước, không hồi quy.
2. Project **đã có `llmwiki/wiki/` mà thiếu inbox + `skills/`**, chạy lại installer →
   hai thư mục đó xuất hiện, và **không file nào có sẵn bị đè** (`index.md`, `log.md`,
   nội dung `wiki/` giữ nguyên).
3. Chạy installer hai lần liên tiếp trên cùng project → lần hai không đổi gì (idempotent).
4. Kiểm chứng bằng **UAT thật** qua `/fdk-uat` (curl bootstrap đường người mới), không
   phải chỉ `bash -n`.

## Assign & lý do

`@Rheinmir` / dispatch **Claude** / entry `/fdk`. Phần sửa đã xong và nhỏ; việc còn
lại chủ yếu là **kiểm chứng hành vi**, cần dựng project sạch và chạy installer thật —
đúng địa hạt của `/fdk-uat`. Không giao headless CLI rẻ vì tiêu chí 2 đòi phán đoán
"có đè file có sẵn không".

**Trạng thái thật lúc raise:** code đã sửa (`c1b3814`, nhánh `orca`, chưa push),
`bash -n` xanh, **chưa chạy test hành vi nào**. Trong phiên raise, hook `R1` chặn mọi
lệnh bash chứa đường dẫn inbox — kể cả repro trong thư mục tạm — nên không dựng được
bằng chứng chạy. Issue này tồn tại chủ yếu để **khoản kiểm chứng đó không bị bỏ quên**,
không phải để làm lại phần sửa.

## Kiểm chứng hành vi — 2026-09-11

`harness/tests/install-seed-test.sh` chạy installer thật trong sandbox (project tạm + `HOME` tạm) và đã được gắn vào CI `harness.yml`. Kết quả 11/11 assert xanh:

- **Tiêu chí 1** — project trắng chạy ở mode `new`, có đủ bốn thư mục khung và `index.md`.
- **Tiêu chí 2** — project đã có sẵn `llmwiki/wiki/sources/draft/brd.md` cùng một `index.md` riêng chạy ở mode `migrate`. Installer thoát `rc=3` ("MIGRATE CÓ NỢ": hooks vẫn cài xong, audit baseline báo BRD thiếu Origin), thư mục khung được bổ sung đủ bốn, còn BRD và `index.md` giữ nguyên từng byte.
- **Tiêu chí 3** — chạy lần hai thì cây `llmwiki/` giống hệt lần một. Chính bài test này bắt thêm một lỗi mà `c1b3814` chưa sửa: mỗi lần chạy lại, installer đẻ thêm một file `settings.json.bak.<timestamp>` (cả trong `llmwiki/.claude/` lẫn `.claude/` gốc) dù phép merge không đổi gì. Cách sửa: merge xong mà file giống hệt bản backup thì xoá backup, chỉ giữ backup khi thật sự có thay đổi. Hai chỗ backup ở nhánh `--global` cùng loại lỗi nhưng không có test phủ nên chưa đụng.
- **Fire-drill** — thay installer bằng bản trước khi sửa backup thì test đỏ ở tiêu chí 3; thay bằng bản `c1b3814^` (trước khi sửa seed) thì đỏ ở tiêu chí 2 ("mong 4, được 2"). Test cắn đúng cả hai lỗi.
- **Tiêu chí 4 (UAT qua `/fdk-uat`, pha 2 main-URL smoke @ `90334c3`)** — chạy nguyên văn lệnh README (`curl … bootstrap.sh | bash`, không override biến nào) vào project trắng `~/orca/overstack-uat-260911-1421`, sau khi raw CDN đã phục vụ bản mới (sentinel `html_docs_shell` trong policy). Kết quả: rc=0, demo 13 và test-broad 80 xanh, đủ ba trụ, khung `.llmwiki/{html,raw,wiki}` được seed, harness global lên 1.3.88, và workspace Orca `uat-260911-1421` hiện thật trong app (đã assert đúng tên). Mô phỏng migrate trên chính project đó — đặt sẵn `brd.md` cùng một `index.md` riêng, commit, rồi chạy lại lệnh README — thì BRD và `index.md` giữ nguyên từng byte.
- **UAT bắt thêm một lỗi cùng loại tiêu chí 3 trên đường curl** — lần chạy thứ hai để lại `.claude/settings.json.bak` (untracked, hiện `??` trong `git status` của dự án người dùng) dù `settings.json` không đổi byte nào. Đường curl đi qua `harness/poc-vendor-neutral/install.sh` chứ không qua `install-harness.sh`, nên sửa riêng ở đó theo cùng mẫu: merge không đổi thì không backup và không ghi lại; dòng log cũng nói thật "(không đổi)". Case 4 của `install-seed-test.sh` gác lỗi này, và fire-drill với bản cũ cho đỏ ("mong 0, được 1").
- **Ghi chú phạm vi** — đường curl chỉ gọi `install-harness.sh --global`, không đi qua khối seed per-project. Vì vậy lỗi gốc của issue này (seed chỉ ở `MODE=new`) chưa từng chạm người cài bằng curl; nó chạm người cài per-project bằng `install-harness.sh <root>`, và phần đó do case 1–3 phủ.

## Origin

Raise bởi phiên Claude Opus 5 ngày 2026-09-10 (session `016D4EHCU84xKYaGino8sAQM`),
trong lúc chạy thử game `rhein-farm/walleye`. User hỏi "không thấy folder inbox trong
llmwiki nữa vậy" rồi bác lại giả thuyết đầu của tôi ("tự tạo tay đi") bằng lập luận
đúng: *"chạy installer thì nó cũng phải tạo ra folder"*. Truy ngược từ đó ra dòng 487
và 492 của `install-harness.sh`.

Bằng chứng: đọc source `harness/scripts/install-harness.sh` @ `1da1de5`; trạng thái
đĩa và `git log --all` của `/Users/giatran/orca/workspaces/rhein-farm/walleye`.
