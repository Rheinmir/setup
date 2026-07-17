---
name: fdk-poc
description: >-
  POC luồng /br: tạo PROJECT THẬT trong Orca (orca-cli) → CURL cài overstack từ REMOTE (đường
  người mới) → nạp context bằng cách copy tài liệu THẬT sang llmwiki/raw/ → chạy /br TỪ ĐẦU, ghi
  lại TỪNG BƯỚC THẬT (rc + log) rồi render trang visualize để người xem ĐỌC LOG + CHẤM từng bước.
  Luật cốt lõi: tool KHÔNG BAO GIỜ BỊA BƯỚC — mọi bước hoặc do tool chạy thật, hoặc do agent chạy
  thật rồi `record`. Có `probe` để soi một /br project có sẵn bằng tool thật (frame-lint/pytest/
  line-status/checkpoint). KHÁC /fdk-uat (test nhanh xanh-đỏ "người mới curl về chạy không"):
  fdk-poc nhắm CHỨC NĂNG THỰC TẾ chạy ra sao. Gọi khi user nói "fdk-poc", "poc luồng", "chạy thử
  project mới", "visualize luồng br chạy", "/fdk-poc".
---

# Skill: fdk-poc — POC luồng /br chạy THẬT + visualize

## When to use
- Muốn THẤY một luồng ĐẦY ĐỦ chạy thật trên một project MỚI (không phải nghe kể).
- Chứng năng lực mới **tới tay người dùng** qua đường remote + chạy được trên tài liệu thật.
- KHÔNG dùng để: test nhanh xanh/đỏ (đó là `/fdk-uat`) hay chạy sản phẩm thật (đó là `/br`).

## Luật CỐT LÕI (rút từ lần fail 16/07/26)
**Tool KHÔNG BAO GIỜ BỊA BƯỚC.** Bản đầu tự scaffold artifact giả trong `/tmp` rồi vẽ timeline →
user không thấy project đâu, không có luồng thật ⇒ POC vô giá trị (đúng luật "bằng chứng > lời").
Nay mọi bước trong trace đến từ MỘT trong hai nguồn:
- lệnh tool NÀY thực sự chạy (`new`, `probe`), hoặc
- bước agent THỰC SỰ chạy rồi `record` lại (kèm `rc` + log thật).

## Luồng ĐÚNG (user chốt 16/07/26)
```
1) orca repo add + orca WORKTREE create → WORKSPACE hiện ở panel Orca
2) CURL cài overstack từ REMOTE          → đường NGƯỜI MỚI, chứng năng lực travel được
3) nạp CONTEXT: copy tài liệu THẬT       → <workspace>/llmwiki/raw/
4) chạy /br TỪ ĐẦU (interview → auto → compile → slice → run → qc → status)
```

### Bẫy 1 — `repo add` KHÔNG đủ (bài học 17/07/26)
`orca repo add` chỉ đăng ký repo (hiện ở `orca repo list`). Panel **Workspaces** liệt kê **worktree**
→ thiếu `orca worktree create` thì **user KHÔNG THẤY project** ⇒ POC fail. Layout khớp Orca:
repo ở `~/orca/<name>/<name>`, workspace ở `~/orca/workspaces/<name>/<wt>`.

### Bẫy 2 — `curl` KHÔNG mang skill của nhánh canary
`install.sh:230` **hardcode** `npx -y skills add rheinmir/setup#orca --global --all` — KHÔNG có
`SKILLS_REF` override. Nên: **harness** tới từ `--ref` bạn chọn, nhưng **skill LUÔN tới từ nhánh `orca`**.
⇒ Skill MỚI ở nhánh canary **chưa tới tay user** qua đường remote cho tới khi merge vào `orca`.
Đây đúng lớp lỗi *"hardcode tên nhánh"* mà `/fdk-uat` pha-2 sinh ra để bắt. POC ghi cảnh báo này
vào log bước curl thay vì im lặng giả xanh.
```bash
# bước 1–3 (tool chạy thật, ghi 3 bước vào trace)
python3 fdk/tools/fdk-poc.py new --raw "<dir tài liệu>" [--name <proj>] [--ref <nhánh>] [--dest ~/orca/workspaces]

# bước 4: agent chạy /br THẬT, ghi lại từng bước
python3 fdk/tools/fdk-poc.py record --project <p> --cmd "/br interview" --rc 0 --log-file <out> --llm \
        --sentinel "br/spec-filled.md:provenance"

# render trang visualize từ trace THẬT
python3 fdk/tools/fdk-poc.py render --project <p>

# soi một /br project CÓ SẴN bằng tool thật (không scaffold)
python3 fdk/tools/fdk-poc.py probe --project br/payroll [--fresh]
```
`--ref` trỏ nhánh remote cho `curl` (mặc định `orca`; canary thì đưa tên nhánh — `bootstrap.sh` nhận
`HARNESS_BASE`). `--skip-curl` CHỈ dùng khi offline/self-test — bỏ nó là bỏ mất phần chứng minh.

## "Không tất định từ raw thì TRỎ thế nào?"
`/br auto` (`br-fill.py fill`) **không** tất định-từ-raw: nó cần `br/spec-filled.md` có trước, mà file
đó do **LLM đọc .docx** sinh ra. Cơ chế trỏ nằm ở **provenance per-field**:
- mỗi field S1–S10 mang `status: filled|missing|conflict|assumed` + `provenance: raw:<file>|user|lens:<tên>`
  ⇒ field nào cũng **trỏ ngược về đúng tài liệu nguồn** → bước LLM vẫn audit được.
- `br-fill.py fill` chỉ điền field `missing` từ registry defaults (`skills/br/assets/defaults.yaml`,
  project override `br/defaults.yaml` thắng) — phần này TẤT ĐỊNH.
- mọi thứ `assumed` nổi lên bảng **"Giả định đang gánh"** trong BR.md → nhìn một phát biết đang cược gì.
POC vì thế ghi bước interview là `--llm` + log thật + sentinel `br/spec-filled.md:provenance`.

## Đọc kết quả
- **bước THẬT đã chạy** + **sentinel PASS** → luồng thật tạo đủ artifact (không phải khai).
- **LOG mỗi bước** (`rc` + output) → người xem tự chấm, không tin lời model.
- **bước LLM (cam)** là biến; **tất định (tím)** là chi phí harness.

## Rules
- **KHÔNG bịa bước** — không có log thật thì không vào trace.
- **Curl từ remote là bắt buộc** cho POC đầy đủ — cài từ working-tree/`file://` KHÔNG chứng minh năng lực travel (bài học fdk-uat / GH#77).
- **Không khoe "skill tới qua remote" khi chưa kiểm** — `install.sh` hardcode `#orca`; skill có mặt ở global có thể do copy tay. Kiểm nguồn trước khi tuyên bố (bài học 17/07/26).
- **Project phải hiện ở panel Workspaces** (worktree), không chỉ `repo list`.
- **Bước LLM đánh dấu trung thực** (`--llm`), không giả vờ tất định.
- **Project phải THẤY ĐƯỢC** (orca repo add) — POC mà user không mở được project thì fail.
- HTML self-contained + in full-path (R16).

## Related
- `fdk/tools/fdk-poc.py` — new · record · render · probe.
- `~/.claude/skills/fdk-uat` — test nhanh đường remote (xanh/đỏ), tầng TRÊN medic.
- `skills/br/SKILL.md` — vòng đời được demo · `fdk/tools/br-fill.py` — engine `/br auto`.
