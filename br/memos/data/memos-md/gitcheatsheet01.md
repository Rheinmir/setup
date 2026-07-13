---
uid: gitcheatsheet01
creator_id: 1
created_ts: 1782404235
updated_ts: 1782404235
row_status: NORMAL
visibility: PUBLIC
pinned: 0
---

## ⚡ Git Commands I Keep Forgetting #dev #cheatsheet

Pinning this so I stop googling the same things every week.

```bash
# Show the last commit in detail
git show --stat HEAD

# Undo the last commit, keep changes staged
git reset --soft HEAD~1

# Stash including untracked files
git stash push -u -m "wip: before refactor"

# Find which commit introduced a string
git log -S "function_name" --source --all
```

The `-S` one is gold for archaeology — way better than scrolling blame.