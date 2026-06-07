---
name: orca-sec-scans
description: Quét bảo mật mã nguồn bằng Trivy — tự check/cài Trivy nếu chưa có, quét vuln + misconfig + secret trên be/fe, xuất report JSON+HTML, tóm tắt HIGH/CRITICAL, và đề xuất/áp dụng fix (bump deps, USER non-root). Dùng khi user nói "quét bảo mật", "trivy", "scan vuln", "security scan", "check CVE", "/orca-sec-scans".
---

# Skill: orca-sec-scans

## Purpose

Một luồng quét bảo mật static, **chỉ-đọc** (Trivy không sửa mã khi quét), dùng được local lẫn CI/Jenkins. Bao trùm: dependency CVE (Go/Node/Python lockfile), misconfig (Dockerfile/compose/nginx), và secret lộ trong file.

## Triggers

- User nói "quét bảo mật", "scan", "trivy", "check CVE", "security scan", "có lỗ hổng không"
- Trước khi release / merge nhánh deploy
- Định kỳ trong CI (`trivy fs . --config trivy.yaml --exit-code 1`)

## Workflow

### Bước 0 — Check + Install Trivy (BẮT BUỘC chạy trước)

```bash
if ! command -v trivy >/dev/null 2>&1; then
  echo "Trivy chưa có → cài…"
  if [[ "$(uname)" == "Darwin" ]]; then
    brew install trivy
  else
    # Linux: dùng script chính thức Aqua (không cần root nếu set BINDIR)
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh \
      | sh -s -- -b /usr/local/bin
  fi
fi
trivy --version   # xác nhận; DB vuln tự cập nhật lần chạy đầu
```

### Bước 1 — Detect ngôn ngữ (scope quét)

Tìm lockfile để biết hệ sinh thái: `go.sum`/`go.mod` (Go), `package-lock.json`/`pnpm-lock.yaml` (Node), `requirements.txt`/`poetry.lock` (Python). Bỏ qua `node_modules`, `.next`, `.contentlayer`, `_archives`, `.git`.

### Bước 2 — Quét (HIGH+CRITICAL trước cho nhanh)

```bash
trivy fs <dir> \
  --scanners vuln,misconfig,secret \
  --severity HIGH,CRITICAL \
  --skip-dirs '**/node_modules' --skip-dirs '**/.next' \
  --skip-dirs '**/.contentlayer' --skip-dirs '_archives' \
  --no-progress
```

Repo bonbon-ai: quét riêng `be` và `fe` (mỗi cái là submodule). Ưu tiên `--config trivy.yaml` nếu repo đã có.

### Bước 3 — Xuất report đầy đủ

```bash
mkdir -p security
TPL=$(find $(brew --prefix trivy 2>/dev/null || echo /opt/homebrew) -name html.tpl 2>/dev/null | head -1)
trivy fs . <cờ skip-dirs như trên> --no-progress -f json     -o security/trivy-report.json
trivy fs . <cờ skip-dirs như trên> --no-progress -f template --template "@$TPL" -o security/trivy-report.html
```

### Bước 4 — Tóm tắt & đề xuất fix

Đếm HIGH/CRITICAL theo từng target, in bảng. Sau đó đề xuất (KHÔNG auto-bump hàng loạt nếu submodule đang có thay đổi chưa commit):

- **Dep bump dễ** (direct dep, sửa thẳng manifest): vd `python-multipart` trong `requirements.txt`.
- **Dep indirect**: `go get <pkg>@<ver>` rồi `go build ./...` verify. Lưu ý `go get` có thể nâng directive `go`; nếu vượt base image trong Dockerfile thì bump luôn `FROM golang:X-alpine` cho khớp.
- **Misconfig DS-0002 (root user)**: thêm `USER` non-root vào Dockerfile (`adduser -D` alpine, `useradd -m` debian, hoặc `USER node` cho image node-alpine; nhớ `chown` thư mục ghi như volume/data).
- **Secret**: nếu Trivy flag → xoay key ngay, không chỉ xoá khỏi file.

### Bước 5 — Re-scan xác nhận

Chạy lại Bước 2 trên target đã fix, xác nhận `remaining = NONE`.

## Rules

- Trivy **không sửa mã** khi quét — an toàn chạy bất kỳ lúc nào.
- Finding đã review & chấp nhận → ghi vào `.trivyignore` (1 ID/dòng + comment lý do + ngày), KHÔNG xoá khỏi report.
- Không commit `security/*.json|html` lên server deploy — chỉ là artifact review.
- Khi deploy bonbon-ai: **chỉ push `be` và `fe`** (2 submodule) lên server; tooling (trivy.yaml, security/, skill) không lên server.
- Mọi thay đổi fix phải qua build/verify trước khi commit (`go build ./...`, `pnpm i`, …).
