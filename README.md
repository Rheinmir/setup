# overstack — the self-disciplined AI-agent framework

**overstack** là một lớp khung (*a stack you put over your project*) biến AI Agent (Claude Code · opencode · Antigravity · Cursor…) thành một **cộng sự kỹ thuật tự-kỷ-luật**: có trí nhớ (nền tri thức `llmwiki/`), có nguyên tắc không thể phá (**guardrail** tất định chặn agent làm bậy, 0 token), có tay nghề đóng gói sẵn (skills), và biết điều phối nhiều agent (Orca).

> Nhánh làm việc chính: **`orca`**.

## ⚡ Cài / update — 1 dòng (cả 3 trụ)

Chạy trong thư mục gốc dự án của bạn — **1 lệnh lo trọn harness + skills + llmwiki**, khỏi nhớ cờ.

**Cách 1 — dán cho Agent** (agent tự cài rồi tự kiểm tra mọi thứ đã đúng chỗ):

```
chạy curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash và kiểm tra xem mọi thứ đã ở đúng chỗ chưa
```

**Cách 2 — chạy thẳng trong terminal (macOS/Linux/WSL):**

```bash
curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash
```

**Windows (PowerShell, không cần curl):** dòng trên tải-và-chạy trong CÙNG một lệnh — hình dạng
mà nhiều EDR/antivirus/agent-safety-filter gắn cờ "malware" bất kể nội dung. Trên Windows, tải
thành file rồi chạy ở bước riêng — không cần cài thêm gì, PowerShell đã có sẵn `Invoke-WebRequest`
(`iwr`) trên mọi máy, kể cả máy chỉ có `winget` mà không có `curl`:

```powershell
iwr -useb https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/install.ps1 -OutFile install.ps1
.\install.ps1
```

`install.ps1` cần **Git Bash hoặc WSL** đã có sẵn trên máy (đa số máy dev đã có Git); không có thì
script tự dừng và chỉ đường cài Git for Windows. Chưa có gói `winget`/MSIX riêng cho overstack —
đây vẫn là script, không phải app đóng gói, nên không đăng ký được vào winget. Chi tiết đầy đủ:
[`harness/poc-vendor-neutral/README.md#windows`](harness/poc-vendor-neutral/README.md#windows-vì-sao-không-dùng-một-dòng-irm--iex).

Mặc định cài/update **cả 3 trụ**: **Harness** (validator tất định vendor-neutral — chặn ghi `raw/`, ép wiki có `## Origin`… qua hook native + CI làm sàn) · **Skills** (global `~/.claude/skills`) · **llmwiki** (khung wiki). Cuối lần chạy in **bảng trạng thái 3 trụ**. Cờ: `--harness-only` · `--clean` · `uninstall` (bản PowerShell: `-HarnessOnly` · `-Clean`).

**Module tuỳ chọn — orca-graph.** Engine đồ thị phân việc (`/orca-graph`, `/tc-run`, control-room) sống ở repo riêng [`Rheinmir/orca-graph`](https://github.com/Rheinmir/orca-graph) để có lịch sử, test và bộ eval riêng; trình cài chỉ kéo nó khi option được tick. Option này **đã tick sẵn**: chạy trong terminal sẽ thấy checklist dưới đây, **chỉ cần Enter là kéo đủ**; gõ `1` để bỏ tick, `n` để bỏ hết. Agent hoặc CI chạy (không có terminal) thì kéo luôn, không hỏi.

```
[install] Module tuỳ chọn (repo riêng — CHỈ tải mục được tick):
     [x] 1. orca-graph — engine đồ thị phân việc: /orca-graph, /tc-run, control-room (github.com/Rheinmir/orca-graph)
     Enter = cài các mục đang tick · gõ số để tick/bỏ · n = bỏ hết   (60s không gõ = Enter) >
```

Bỏ hẳn bằng cờ `--no-graph` (PowerShell: `-NoGraph`); ghim nhánh/tag engine bằng `ORCA_GRAPH_REF=<ref>`. Engine nằm ở `~/.orca-graph/repo/`, trong overstack chỉ còn shim ở đường dẫn cũ nên lệnh gõ không đổi. Bỏ qua lúc cài thì về sau `/orca-graph` sẽ in đúng một lệnh để cài bù.

Tự bảo trì về sau (cập nhật + trả nợ wiki + refresh bản đồ năng lực + health-check trong một lệnh): gọi skill **`/harness-update`**.

## 📖 Tài liệu chính thức (cho người đọc)

Mở trực tiếp file self-contained — **đi theo dự án khi bạn cài** (không cần mạng, không build):

**[`llmwiki/html/overstack.html`](llmwiki/html/overstack.html)** — bắt đầu ở **Quickstart** (chạy được trong 2 phút), rồi hàng chục tab đi sâu: cài đặt · ba trụ (wiki / harness / skills) · workflow propose→gate→dispatch · Orca · build-now-adapt-later · eval/council/loop · tự bảo trì · FDK · và ★ *dev một cái mới thì cần update gì cho hợp lệ*.

Trang này **sinh bằng code** (`fdk/tools/build-overstack-docs.py`) nên bảng skill/rule luôn khớp đĩa. Bản máy-đọc của bản đồ năng lực: `fdk/CAPABILITIES.md`.

## 🏗️ Dựng dự án mới — dán 1 prompt

Không copy folder, không feed từng file: mở agent ở thư mục gốc dự án mới rồi **dán nội dung [`00-New-Project.md`](00-New-Project.md)**. Agent tự cài overstack → kickoff (hỏi 3 câu) → dựng knowledge base → scaffold MVP, dừng hỏi đúng lúc cần.

Chi tiết + bản từng pha (`01`/`02`/`03`): [`setup.md`](setup.md). Cài bộ skills: `npx skills add rheinmir/setup#orca --global --all`.

## 📂 Cấu trúc

| Thư mục / file | Là gì |
|---|---|
| `llmwiki/` | **Trụ tri thức** (khuôn per-project). `wiki/` = khung wiki dự án (concepts/entities/sources/adr/draft), `skills/` (mirror), rules (`CLAUDE.md`/`AGENT.md`), `html/overstack.html` (docs). *Wiki RIÊNG của framework ở `fdk/wiki/` — ADR-008.* |
| `harness/` | **Trụ guardrail.** `validators/` + `scripts/` (install, fdk-gate, code-logger, council/loop/eval…). `poc-vendor-neutral/` = lõi CLI vendor-neutral + installer 1-dòng |
| `skills/` | **Trụ kỹ năng** — mỗi `SKILL.md` gọi bằng `/tên`; canonical, mirror sang `llmwiki/skills/` |
| `fdk/` | **Framework Dev Kit** — đồ nghề phát triển CHÍNH overstack + **`wiki/`** (wiki RIÊNG của framework: ADR-001..010, concepts harness/fdk, decisions), `CAPABILITIES.md`, `tools/`. Không travel xuống dự án (ADR-004/008) |
| `00–03-*.md`, `setup.md` | Prompt dựng dự án mới — **bắt đầu ở `00-New-Project.md`** (1 lần dán) |
| `.github/workflows/harness.yml` | CI: validator + self-test mỗi PR |

## 🛠️ Phát triển chính overstack

Gọi skill **`/fdk`** (front-door on-demand: pre-flight + inventory live). Định-nghĩa-hoàn-thành cho mọi thay đổi: `python3 harness/scripts/fdk-gate.py`. Quyết định kiến trúc: `fdk/wiki/sources/adr/` — gate **R13** ép `decisions.md` (architecture) phải ref ADR, cho edit + xóa khi đã bị đè.

- Cài thủ công / gỡ / chi tiết: [`harness/poc-vendor-neutral/README.md`](harness/poc-vendor-neutral/README.md)
- Bản tải về (offline): [Releases](../../releases)
