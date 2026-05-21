# Skill: sync-template

## Purpose
Synchronize structural and template improvements between the current project and the master template repository `https://github.com/Rheinmir/setup.git`.

## When to use
- **Upstream**: After improving a template file localy and wanting to save it to Master.
- **Downstream**: When the Master repo has newer features or fixes that you want to bring into the current project.

## Steps
1. **Load Manifest**: Read `.template-manifest.json` for the inclusion list.
 2. **Clone Master Repo**:
   - Get the target repository URL from `.template-manifest.json`.
   - Clone the target repository to a temporary directory.
   - **Branch Audit (CRITICAL)**: Always list all remote branches (`git branch -a`). Check if there is an active branch containing newer or more complete template improvements (e.g., `orca`, `orchestrate`, or active development branches). Do not blindly assume the default branch (`master` / `main`) is the only or most up-to-date one.
   - **Checkout Target Branch**: If a newer branch exists or if requested by the user, checkout that branch (`git checkout <branch-name>`) in the cloned repository before proceeding.
   - **Delete `.opencode/` from the cloned copy** to avoid conflicts (`Remove-Item -Recurse -Force "$tmpDir\.opencode"`).
 3. **Compare Manifest Files with Master**:
    - Run `diff` between local template files and Master files listed in the manifest.
 4. **Scan for New Files**:
    - Extract all unique directories from the manifest `includes` list (e.g., `skills/`, `wiki/concepts/`).
    - **Local scan**: List all files in those directories, excluding `excludes` patterns.
    - **Master scan**: Same scan on the cloned copy.
    - Cross-reference both lists against the manifest:
      - `[NEW]` — File exists locally but not on Master, and not in manifest. Candidate for upstream + manifest update.
      - `[MISSING]` — File exists on Master but not locally. Candidate for downstream.
 5. **Stage 1: Presentation (Sync Plan)**:
    - Present a table showing the differences:
      - `[UPSTREAM]` -> File is newer in Local, can be pushed to Master.
      - `[DOWNSTREAM]` -> File is newer in Master, can be pulled to Local.
      - `[CONFLICT]` -> Both have changed (manual review required).
      - `[NEW]` -> File only exists locally, candidate for upstream + manifest registration.
      - `[MISSING]` -> File only exists on Master, candidate for downstream.
    - **STOP**. Ask the user which direction to sync (e.g., "Pull all", "Push all", or specific files).
 6. **Stage 2: Execution**:
    - Copy each file in the requested direction one by one (not bulk `cp -R`).
    - **Downstream (Master → Local)**: Before copying any file, always run `mkdir -p` on the target directory — the local project may not yet have the folder structure from Master.
    - **For `[NEW]` files**: Add the file path to `.template-manifest.json` `includes` before copying upstream.
    - **For `[MISSING]` files**: Add the file path to `.template-manifest.json` `includes` after copying downstream.
    - If Upstreaming: Commit and push to Master.
    - If Downstreaming: Update local files and log the update in `wiki/log.md`.
    - Cleanup temporary directory.
 7. **Stage 3: Install as Slash Skills** *(chạy lại mỗi lần sync — không phải một lần)*:
    - Sau mỗi downstream sync, thu thập tất cả skill files đã được copy (files dưới `llmwiki/skills/` hoặc `skills/` trong manifest).
    - Với mỗi skill file, derive tên slash-skill: bỏ directory prefix và `.md` extension (vd. `skills/utils/sync-template.md` → `sync-template`).
    - **Skip** các file không phải skill definition: `README.md`, `index.md`, `log.md`, và bất kỳ file nào không có `## Purpose` hoặc `## Steps`.
    - Hỏi user scope để install (default: project-level). Áp dụng cho **tất cả agent CLI** trong pool:

    **Claude Code CLI**
    ```bash
    # Project-level (default):
    mkdir -p .claude/commands/
    cp <skill-file> .claude/commands/<name>.md

    # User-level (cần user approval):
    mkdir -p ~/.claude/commands/
    cp <skill-file> ~/.claude/commands/<name>.md
    ```
    Skill available ngay dưới dạng `/<name>` — không cần restart.

    **OpenCode CLI**
    ```bash
    # Skills phải là thư mục chứa SKILL.md — không phải flat file:
    mkdir -p ~/.agents/skills/<name>/
    cp <skill-file> ~/.agents/skills/<name>/SKILL.md
    # Restart OpenCode để discover.
    ```

    **Antigravity CLI**
    ```bash
    # Dùng chung pool với OpenCode:
    mkdir -p ~/.agents/skills/<name>/
    cp <skill-file> ~/.agents/skills/<name>/SKILL.md
    ```

    - Copy từng file một — không dùng `cp -R`.
    - Sau khi xong, report bảng install:
      ```
      | Agent       | Skill         | Installed at                            |
      |-------------|---------------|-----------------------------------------|
      | claude-cli  | sync-template | .claude/commands/sync-template.md       |
      | opencode    | sync-template | ~/.agents/skills/sync-template/SKILL.md |
      | antigravity | sync-template | ~/.agents/skills/sync-template/SKILL.md |
      ```

 8. **Stage 4: Restart & Verify**:
    - **Verify disk first** — chạy check này trước khi restart bất cứ thứ gì:
      ```bash
      # Claude Code
      for name in <skill-list>; do
        [ -f ~/.claude/commands/$name.md ] && echo "✓ $name" || echo "✗ $name MISSING"
      done

      # OpenCode / Antigravity
      for name in <skill-list>; do
        [ -f ~/.agents/skills/$name/SKILL.md ] && echo "✓ $name" || echo "✗ $name MISSING"
      done
      ```
      Nếu có `✗` → fix copy trước, không restart.

    - **Claude Code**: không cần restart — skills ở `~/.claude/commands/` available ngay.

    - **OpenCode** (terminal CLI):
      - **KHÔNG kill** các session đang chạy — sẽ mất context.
      - Disk đã đúng là đủ. Hướng dẫn user: *"New opencode sessions sẽ tự pick up skills. Restart terminal session cũ nếu muốn dùng ngay."*
      - Không attempt restart từ background shell.

    - **Antigravity** (GUI app):
      - **KHÔNG launch từ background shell** — app sẽ không start được qua terminal (`open -a` và exec trực tiếp đều fail khi không có user session context).
      - Dùng `osascript` để quit gracefully: `osascript -e 'tell application "Antigravity" to quit'`
      - Sau đó hướng dẫn user: *"Mở lại Antigravity thủ công từ /Applications hoặc Dock."*
      - Verify bằng: `osascript -e 'tell application "System Events" to (name of processes) contains "Antigravity"'`

    - **Thứ tự thực hiện**:
      1. Verify disk (tất cả `✓`) → nếu không, fix trước
      2. Quit Antigravity qua osascript
      3. Hướng dẫn user mở lại Antigravity thủ công
      4. Hướng dẫn user restart OpenCode terminal sessions nếu muốn dùng ngay
      5. Claude Code — không cần làm gì thêm

## Agent Compatibility (tested 2026-05-21)

| Agent | Có thể chạy sync-template? | Lý do |
|-------|--------------------------|-------|
| **Claude Code CLI** | Có | Full tool access |
| **OpenCode** | Có | Full tool access |
| **Antigravity CLI** | **Không** | Sandbox chặn `view_file`, `run_command`, `ask_permission` — không thể đọc file, clone repo, hay gửi `worker_done` |

**Khi được dispatch từ Orca đến Antigravity:**
- Antigravity hiểu task nhưng không thể thực thi bất kỳ bước nào.
- `worker_done` sẽ không bao giờ đến inbox — `orca orchestration send` cũng bị block.
- Coordinator phải fallback: `terminal wait --for tui-idle` → `terminal read` để đọc output text.
- **Giải pháp**: dispatch `sync-template` sang claude-cli hoặc opencode, không phải antigravity.

## Rules
- NEVER sync sensitive data (`.env`, credentials).
- NEVER sync business-specific documentation.
- ALWAYS show the `diff` for any file marked as `[CONFLICT]` and wait for user instruction on which version to keep.
- NEVER use bulk recursive copy (e.g., `cp -R folder/*`). Copy file by file based on the inclusion list.
- Use `impact-check` if the template change affects shared logic in `skills/`.
- `[NEW]` files MUST be added to `.template-manifest.json` `includes` before upstream commit so the manifest stays in sync.
- `[MISSING]` files MUST be added to `.template-manifest.json` `includes` after downstream copy so the manifest stays in sync.
- **ALWAYS audit remote branches** (`git branch -a`) when cloning the template repository. Template improvements may live on custom branches (like `orca`, `orchestrate`, or development branches) containing critical new skills or structural components not yet merged into the default branch.
- **Stage 3 runs every downstream sync** — không phải chỉ lần đầu. Mỗi lần sync là mỗi lần install để đảm bảo tất cả agent CLI đều có bản mới nhất.
- **NEVER restart Antigravity from a shell** — `open -a` và exec trực tiếp đều không work từ background process. Luôn quit bằng osascript rồi hướng dẫn user mở thủ công.
- **NEVER kill OpenCode terminal sessions** — sẽ mất context. Disk install là đủ; new sessions tự pick up.
- **Verify disk trước khi restart bất cứ thứ gì** — `[ -f <path> ]` check cho từng skill. Fix missing files trước.
- Source of truth cho install là disk, không phải process state.
- Install cho **tất cả agent CLI trong pool** (claude-cli, opencode, antigravity) — không chỉ agent đang chạy skill này.
- User-level install (`~/.claude/commands/`, `~/.agents/skills/`) phải được user approve trước.
- OpenCode và Antigravity dùng format **thư mục + SKILL.md** (`~/.agents/skills/<name>/SKILL.md`) — không phải flat `.md` file.
- Claude Code dùng format **flat `.md` file** (`.claude/commands/<name>.md` hoặc `~/.claude/commands/<name>.md`).
- Copy từng file một — không dùng `cp -R`.
- Chỉ copy file có `## Purpose` hoặc `## Steps` — skip `README.md`, `index.md`, `log.md`.

