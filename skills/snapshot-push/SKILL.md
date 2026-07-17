---
name: snapshot-push
disable-model-invocation: true
description: Push bonbon-ai outer repo as full snapshot, including be/ and fe/ content
---

# Skill: snapshot-push

## Purpose
Push toàn bộ outer repo `bonbon-ai` lên GitLab như một snapshot — kể cả content của `be/` và `fe/` (các sub-repos có `.git` riêng). Dùng script `scripts/snapshot-push.sh` để tự động hide/restore `.git` dirs.

## Triggers
- "push snapshot", "snapshot push", "đẩy snapshot", "push outer repo"

## Steps
1. Verify đang ở đúng repo root (`/Volumes/giatbhSSD(APFS)/workspace/bonbon-ai`)
2. Chạy: `bash scripts/snapshot-push.sh "<optional message>"`
3. Report kết quả: commit hash + số files changed
