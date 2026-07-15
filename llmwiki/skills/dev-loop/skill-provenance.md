---
name: skill-provenance
disable-model-invocation: true
description: Ghi và kiểm provenance (nguồn + sha256 checksum) cho skill — dùng khi 'cài skill từ ngoài', 'skill này từ đâu', 'audit nguồn skill', 'checksum skill', 'supply-chain skill', phát hiện skill bị sửa lén; bổ trợ orca-sec-scans. Chạy fdk/tools/skill-provenance.py. /skill-provenance
---

# Skill: skill-provenance

Sổ nguồn gốc + toàn vẹn cho từng skill. `orca-sec-scans` quét vuln/secret trong NỘI DUNG;
skill này trả lời hai câu hỏi khác của chuỗi cung ứng (supply-chain): skill **từ đâu tới**
và **có bị sửa lén sau khi cài không**. Store là `fdk/skills.provenance.json` (nguồn +
ngày ghi + sha256 mọi file trong `skills/<name>/`). Verify bằng cách tính lại checksum và
so với sổ — lệch = MODIFIED, có skill trên đĩa mà chưa ghi sổ = UNTRACKED.

## When to use
- Vừa **cài / chưng cất một skill từ nguồn ngoài** (marketplace, repo khác, distill trong phiên dự án khác) → `record` để chốt nguồn + checksum.
- Nghi ngờ / muốn kiểm **skill có bị sửa ngoài luồng** không → `check`.
- Hỏi "skill này **từ đâu** ra", "audit nguồn skill", "checksum skill", "supply-chain skill".
- CI muốn chặn skill lạ hoặc skill bị sửa mà chưa cập nhật sổ.

## Steps
1. **Backfill một lần** (nếu sổ trống) — ghi mọi skill hiện có là tự viết:
   ```bash
   python3 fdk/tools/skill-provenance.py record --all --source local-authored
   ```
2. **Khi cài / thêm skill mới** — ghi nguồn thật (URL, `repo#ref`, hoặc `local-authored`):
   ```bash
   python3 fdk/tools/skill-provenance.py record <name> --source "https://github.com/<owner>/<repo>#<ref>"
   ```
3. **Kiểm toàn vẹn** bất cứ lúc nào (in OK / MODIFIED / UNTRACKED / MISSING):
   ```bash
   python3 fdk/tools/skill-provenance.py check          # xem tất cả
   python3 fdk/tools/skill-provenance.py check <name>   # một skill
   ```
4. **Gate CI** — exit 1 nếu có MODIFIED hoặc UNTRACKED (đã gắn trong `.github/workflows/skills-sync.yml`):
   ```bash
   python3 fdk/tools/skill-provenance.py check --ci
   ```
5. Sau khi **cố ý sửa** một skill, chạy lại `record <name> --source <nguồn cũ>` để cập nhật checksum — nếu không, `check --ci` sẽ báo MODIFIED (đúng: mọi thay đổi phải qua sổ).

## Rules
- **Không tự bịa nguồn.** `--source` phải là URL/ref thật hoặc `local-authored`; provenance sai còn tệ hơn không có.
- **record sau MỌI lần cài/sửa hợp lệ** — sổ là nguồn chân lý; skill sửa mà không re-record sẽ bị CI chặn như sửa đổi lạ (đúng ý đồ).
- **Không thay `orca-sec-scans`** — skill này lo provenance/toàn vẹn, không quét vuln/secret nội dung; dùng cả hai.
- `check --ci` coi MISSING (skill đã gỡ) là không-phải-lỗi; chỉ MODIFIED/UNTRACKED mới chặn.
- Store `fdk/skills.provenance.json` là file curated — commit cùng thay đổi skill, đừng để drift.
