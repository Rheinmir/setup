# Chỉ dẫn đã học — spec-violation (71×)

Lớp `spec-violation` lặp 71 lần (ngưỡng 3). Thẻ này do máy gói từ chính các lần đã ghi; đọc TRƯỚC khi làm việc cùng loại.

## Lần gần nhất
- **Triệu chứng:** egress-guard chặn Bash cat /Users/giatran/orca/setup/setup/scratchpad/intake-serve.log; curl -s -o /dev
- **Đã sửa bằng:** [egress-guard] egress to non-allow-listed host: 127.0.0.1  (block)

## Các lần đã gặp (71)

| Khi | Triệu chứng | Cách sửa đã dùng |
|---|---|---|
| 2026-09-23 09:58 | egress-guard chặn Bash cd /Users/giatran/orca/setup/setup/scratchpad; curl -sS -m 30 -A "Mozilla/5.0" - | [egress-guard] egress to non-allow-listed host: superops.com  (block) |
| 2026-09-23 09:58 | egress-guard chặn Bash cd /Users/giatran/orca/setup/setup/scratchpad; curl -sS -m 30 -A "Mozilla/5.0" - | [egress-guard] egress to non-allow-listed host: superops.com  (block) |
| 2026-09-23 09:58 | egress-guard chặn Bash cd /Users/giatran/orca/setup/setup; python3 - <<'EOF' p='harness/egress-guard.co | [egress-guard] egress to non-allow-listed host: superops.com  (block) |
| 2026-09-23 09:58 | egress-guard chặn Bash cd /Users/giatran/orca/setup/setup; python3 - <<'EOF' p='harness/egress-guard.co | [egress-guard] egress to non-allow-listed host: superops.com  (block) |
| 2026-09-24 10:42 | egress-guard chặn Bash (curl -s -o /dev/null localhost:8777 \|\| (nohup python3 -m http.server 8777 --bin | [egress-guard] egress to non-allow-listed host: localhost  (block) |
| 2026-09-24 10:42 | egress-guard chặn Bash (curl -s -o /dev/null localhost:8777 \|\| (nohup python3 -m http.server 8777 --bin | [egress-guard] egress to non-allow-listed host: localhost  (block) |
| 2026-09-24 14:19 | egress-guard chặn Bash cat /Users/giatran/orca/setup/setup/scratchpad/intake-serve.log; curl -s -o /dev | [egress-guard] egress to non-allow-listed host: 127.0.0.1  (block) |
| 2026-09-24 14:19 | egress-guard chặn Bash cat /Users/giatran/orca/setup/setup/scratchpad/intake-serve.log; curl -s -o /dev | [egress-guard] egress to non-allow-listed host: 127.0.0.1  (block) |

## Trạng thái
- `đã học, CHƯA duyệt` — đây là chỉ dẫn đọc-để-nhớ, KHÔNG phải luật cắn được.
- Thành luật/skill chính thức: `flywheel.py --kind failure --draft spec-violation` rồi `/propose`.
