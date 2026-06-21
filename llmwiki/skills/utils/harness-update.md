---
name: harness-update
description: Migrate llmwiki cũ lên harness (case B) hoặc update harness bản mới (case C) — chạy install-harness.sh, TỰ backfill nợ wiki (thiếu ## Origin, index lệch) rồi chạy lại tới khi sạch. Trigger: "migrate harness", "update harness", "nâng cấp harness", "cài harness vào dự án cũ", "/harness-update".
---

# Skill: harness-update

## Purpose
Một lệnh gọi là xong cho dự án CŨ: cài/update harness stack (L0–L4) và tự động trả nợ wiki legacy thay user. KHÔNG dùng cho project chưa có gì + cần populate wiki từ code — đó là `/new-project-setup` (case A).

## Steps

**1. Chạy installer (tự detect migrate/update; thiếu nguồn thì script tự clone template):**
```bash
test -f harness/scripts/install-harness.sh \
  && bash harness/scripts/install-harness.sh . \
  || { git clone -q --depth 1 -b orca git@github.com:rheinmir/setup.git /tmp/llmwiki-tpl \
       && bash /tmp/llmwiki-tpl/harness/scripts/install-harness.sh . ; rm -rf /tmp/llmwiki-tpl; }
```

**2. Đọc exit code:**
- `rc=0` → sạch, sang bước 4.
- `rc=3` → CÓ NỢ: danh sách vi phạm nằm ngay trong output (R2 thiếu Origin, R3 index lệch) + `harness/metrics/baseline-*.json`. Sang bước 3.
- `rc khác` (1/4) → lỗi hạ tầng (network, python3, validator hỏng) — DỪNG, báo user nguyên văn, không tự đoán.

**3. TỰ BACKFILL nợ (vòng lặp, tối đa 3 vòng):**
- File thiếu `## Origin`: với TỪNG file, lấy nguồn thật bằng `git log -1 --format='%h %ad' --date=short -- <file>`, rồi APPEND vào cuối file:
  ```
  ## Origin
  - legacy backfill (harness-update) — commit gần nhất: <hash> <date>
  ```
  CHỈ thêm section này — không sửa bất kỳ nội dung nào khác của file.
- Index lệch: thêm row cho file THIẾU vào `llmwiki/wiki/index.md` (summary lấy từ heading đầu của file); xóa row trỏ tới file không còn tồn tại.
- Chạy lại bước 1. Nếu sau 3 vòng vẫn rc=3 → DỪNG, đưa danh sách còn lại cho user quyết.

**3b. BACKFILL OKF v0.1 (convert content cũ sang YAML frontmatter):**
Dự án cũ viết metadata kiểu bold `**Type:**` — không đạt chuẩn OKF v0.1 (R9). Convert tự động:
```bash
python3 harness/scripts/okf-check.py --check      # exit 3 = còn file chưa đạt OKF
python3 harness/scripts/okf-check.py --migrate     # bold **Type:** → khối YAML ---; CHỈ thêm frontmatter, giữ body + ## Origin
```
- Chỉ THÊM frontmatter, không sửa nội dung khác (giống quy tắc backfill Origin). Idempotent; reserved tự miễn.
- Chạy lại `--check` tới khi `DAT CHUAN OKF v0.1`. Đếm số file đã convert để báo cáo ở bước 5.

**4. Kích hoạt + nghiệm thu:**
```bash
command -v pre-commit >/dev/null && pre-commit install || echo "TODO user: pipx install pre-commit && pre-commit install"
```
- Xác nhận bảng "Harness tự kiểm" có ⛔×3 BỊ CHẶN ✓ trong output bước 1.
- Append vào `llmwiki/wiki/log.md`: `## YYYY-MM-DD — harness-update — migrate/update xong, nợ đã backfill: <n> file (Origin: <a>, OKF: <b>)`

**5. Báo cáo cho user (bắt buộc đủ 4 ý):**
- Mode đã chạy (migrate hay update) + số nợ đã backfill (liệt kê file)
- Settings root: file backup `.bak.*` nếu có merge
- Nhắc: **mở session mới thì hooks mới load**
- Mời: `/harness-tour` để xem hàng rào cắn trực quan

## Rules
- Backfill là THÊM, không bao giờ sửa/xóa nội dung wiki có sẵn.
- Không đụng `raw/` dưới mọi hình thức.
- rc=3 là việc của skill này; rc khác là việc của user — phân biệt rõ, không cố chữa lỗi hạ tầng.
- Case A (chưa có llmwiki, cần đọc code populate wiki) → chuyển hướng sang `/new-project-setup`.
