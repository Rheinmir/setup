---
type: draft
title: "PLAN — tách hệ skill ra repo Rheinmir/skills, installer kéo về, MCP skills.giatbh.io.vn làm nguồn phiên bản"
status: proposed
tags: [plan, skills, installer, mcp, cloudflare, ci]
timestamp: 2026-10-14
---

# 141026-skills-split-PLAN

**Status:** proposed

## Context
Bản đánh giá `141026-skills-split-mcp-danh-gia.md` (commit fe713cb) đo được: 106 skill trong `skills/` của Rheinmir/setup,
40 skill gọi ~80 script engine, một dòng SKILL.md đổi phải trả skills-sync 15 s + harness.yml ~364 s + medic 72 s + fdk-uat.
User 14/10 quyết: **tách**, và **host MCP** tại `skills.giatbh.io.vn` vì overstack-mcp đã serve nhiều người (deploy k8s2
11/10, RUNBOOK §6) và dev bị lệch phiên bản harness giữa máy. Thí nghiệm 14/10 (phiên haiku thật, `probe3.out`): Claude Code
nạp và gọi được skill có `metadata.requires` lồng (block map + flow sequence) → khai phụ thuộc trong frontmatter là an toàn.
Đường vào k8s2 từ máy này: không có khoá SSH, không có token devops-agent, token Cloudflare bị khoá theo IP
("Cannot use the access token from location") → bước deploy là handoff, không chạy được trong phiên.

Yêu cầu của user (đánh số để các task khai **Thoả:**):
- YC-1 tách hoàn toàn hệ skill vào một repo riêng, vẫn kéo về bằng installer.
- YC-2 dev/cập nhật skill không phải chạy full CI và test của framework.
- YC-3 cân nhắc từng skill về bộ tool phụ thuộc.
- YC-4 MCP host trên Cloudflare tại `skills.giatbh.io.vn`, là nguồn phiên bản đồng nhất giữa các dev.

## Global constraints
- Sàn version: skill lớp B khai `harness: ">=1.3.127"` (bản setup phát hành cùng đợt tách); không khai sàn thấp hơn 1.3.126.
- Không ghi `raw/`; mọi wiki .md tạo mới có frontmatter OKF (type/title/status/tags/timestamp) và `## Origin`.
- Repo mới `Rheinmir/skills` là **nguồn chân lý duy nhất** của 106 skill; setup không giữ bản sao nào (xoá `skills/`, `llmwiki/skills/`, `.claude-plugin/`).
- Tool engine (swh-lint, skill-provenance, build-skill-search, skill-resolve-eval, new-skill, skill-reuse) **ở lại setup** nhưng nhận `OVERSTACK_SKILLS_DIR` / `--skills-dir`; CI repo skills checkout setup (depth 1) để chạy chúng. Không chép tool sang repo skills.
- Mọi cổng đang có của setup phải xanh trước khi push: `medic --ci`, `fdk-gate`, `test-broad`, `mcp` npm test; rồi fdk-uat 2 pha với `SKILLS_REF=rheinmir/skills#main`. Đỏ thì không push `orca`.
- Không in, không dùng token Cloudflare đã dán vào chat; bí mật đi qua Vault k8s2 `secret/infra/cloudflare`.
- Commit bằng tiếng Việt, kết thúc bằng `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

### Task 1 — `requires` + `loop` trong frontmatter 106 skill, validator `skill-requires.py`
**Thoả:** YC-3 (mỗi skill khai bộ tool phụ thuộc, kiểm được bằng lệnh).

**Files:** `harness/scripts/skill-requires.py` (mới), `harness/tests/test_skill_requires.py` (mới), `bench/skills/gen_requires.py` (mới, chạy một lần sinh frontmatter), `skills/*/SKILL.md`, `skills/external/*/SKILL.md`, `harness/scripts/sync-skills.py` (nguồn LOOP_MAP để sinh `loop`).

**Interfaces:**
- Consumes: `skills/<tên>/**` (grep `harness/scripts|fdk/tools|harness/validators|harness/poc-vendor-neutral/*.py|sh|mjs` và tên binary), `sync-skills.py:LOOP_MAP`, `~/.claude/harness/version.json:template_version`.
- Produces: frontmatter `metadata.loop: <wiki-loop|dev-loop|orchestrate|utils>` và `metadata.requires: {harness, bin[], scripts[]}` (khoá vắng khi rỗng); CLI `skill-requires.py check [--skills-dir D] [--harness-home H] [--json] [--ci]` rc 0 đủ / rc 2 thiếu; hàm `parse_requires(text) -> dict`, `check_skill(dir, harness_home) -> {"name","ok","missing_bin","missing_scripts","harness_floor","harness_have"}`.

```python
# harness/scripts/skill-requires.py — lõi
def check_skill(skill_dir: Path, harness_home: Path, have_version: str) -> dict:
    fm = frontmatter((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
    req = (fm.get("metadata") or {}).get("requires") or {}
    floor = str(req.get("harness") or "").lstrip(">=").strip()
    missing_bin = [b for b in req.get("bin", []) if shutil.which(b) is None]
    missing_scripts = [s for s in req.get("scripts", []) if not (harness_home / s).is_file()]
    floor_ok = (not floor) or cmp_semver(have_version, floor) >= 0
    return {"name": skill_dir.name, "ok": floor_ok and not missing_bin and not missing_scripts,
            "harness_floor": floor or None, "harness_have": have_version,
            "missing_bin": missing_bin, "missing_scripts": missing_scripts}
```

### Task 2 — tạo repo `Rheinmir/skills` giữ lịch sử, CI ≤30 s
**Thoả:** YC-1, YC-2 (repo riêng, CI riêng chỉ kiểm skill).

**Files:** `~/orca/skills/` (checkout mới), `~/orca/skills/skills/<tên>/`, `~/orca/skills/.claude-plugin/marketplace.json`, `~/orca/skills/skills.provenance.json`, `~/orca/skills/evals/skill-resolve/*.md`, `~/orca/skills/tools/catalog.py`, `~/orca/skills/tools/registry.py`, `~/orca/skills/catalog.json`, `~/orca/skills/version.json`, `~/orca/skills/.github/workflows/ci.yml`, `~/orca/skills/README.md`.

**Interfaces:**
- Consumes: lịch sử `git subtree split --prefix=skills` của setup@orca; tool engine của setup (`fdk/tools/swh-lint.py --root`, `skill-provenance.py`, `build-skill-search.py`, `harness/scripts/skill-resolve-eval.py --skills-dir --goldens`, `skill-requires.py`).
- Produces: `catalog.json` = `{"schema":1,"version":"<version.json>","generated_at","skills":[{"name","loop","description","requires","external","sha"}]}` + `catalog_sha`; `version.json` = `{"schema":1,"version":"1.0.0","harness_floor":"1.3.127","generated_commit"}`; `npx skills add rheinmir/skills#main --global --all` cài đúng 106 skill; CI job `skills` (checkout + setup depth 1 + 5 lệnh).

```bash
# tạo repo từ lịch sử skills/ của setup
cd ~/orca/setup && git subtree split --prefix=skills -b skills-split
mkdir -p ~/orca/skills && cd ~/orca/skills && git init -b main && git pull ~/orca/setup skills-split
mkdir skills && git mv $(ls | grep -v '^skills$') skills/ && git commit -m "chore: dời 106 skill vào skills/ (lịch sử giữ nguyên qua subtree split)"
gh repo create Rheinmir/skills --public --source . --remote origin --push
```

### Task 3 — setup bỏ skill, mọi tool/test/gate/doc đi theo `OVERSTACK_SKILLS_DIR`
**Thoả:** YC-1, YC-2 (setup không còn skill, CI framework không còn kiểm skill).

**Files:** `harness/scripts/overstack_paths.py` (thêm `skills_dir()`), `fdk/tools/build-capabilities.py`, `fdk/tools/build-overstack-docs.py`, `fdk/tools/build-cheatsheet.py`, `fdk/tools/build-health-dashboard.py`, `fdk/tools/whiteboard-skill-map.py`, `fdk/tools/swh-lint.py`, `fdk/tools/skill-provenance.py`, `fdk/tools/build-skill-search.py`, `fdk/tools/new-skill.py`, `fdk/tools/medic.py`, `harness/scripts/capability-stamp.py`, `harness/scripts/skill-resolve-eval.py`, `harness/scripts/fdk-gate.py`, `harness/scripts/fresh-install-smoke.sh`, `harness/scripts/install-harness.sh`, `harness/scripts/arch-scan.py`, `harness/tests/ge-reachability-test.sh`, `harness/tests/engines-smoke-test.sh`, `harness/tests/html-visual-gate-test.sh`, `harness/tests/docs-skill-okf-test.sh`, `.github/workflows/harness.yml`, `.github/workflows/skills-sync.yml` (xoá), `.template-manifest.json`, `llmwiki/AGENT.md`, `llmwiki/CLAUDE.md`, `README.md`, `fdk/README.md`, `fdk/docs/fresh-install-gate.md`, `harness/version.json`.

**Interfaces:**
- Consumes: `OVERSTACK_SKILLS_DIR` (env) → `<root>/skills` nếu có → `~/.claude/skills`; `https://raw.githubusercontent.com/Rheinmir/skills/main/catalog.json` (parity hứa↔giao trong fresh-install-smoke, override `SKILLS_RAW`).
- Produces: `overstack_paths.skills_dir(root: Path) -> Path`; `build-capabilities` đọc `metadata.loop` (fallback LOOP_MAP nếu còn); `fresh-install-smoke` so tên trong `catalog.json` với `~/.agents/skills`; `capability-stamp` không còn `skill:` → `--update` bump 1.3.127; AGENT.md/CLAUDE.md `## Skills` thành một đoạn trỏ `CAPABILITIES.md` + repo skills (bảng rỗng → `agent_claude_parity` vẫn khớp).

```python
# harness/scripts/overstack_paths.py
def skills_dir(root: "Path | None" = None) -> Path:
    """Thư mục skill: env OVERSTACK_SKILLS_DIR > <root>/skills (checkout repo Rheinmir/skills) > ~/.claude/skills (đã cài)."""
    env = os.environ.get("OVERSTACK_SKILLS_DIR")
    if env:
        return Path(env).expanduser()
    if root is not None and (Path(root) / "skills").is_dir():
        return Path(root) / "skills"
    return Path.home() / ".claude" / "skills"
```

### Task 4 — installer kéo skill từ repo mới, lệnh cập nhật riêng, nhắc lệch bản đầu phiên
**Thoả:** YC-1 (installer vẫn kéo về), YC-4 (dev thấy mình lệch bản ngay đầu phiên).

**Files:** `harness/poc-vendor-neutral/install.sh`, `harness/poc-vendor-neutral/bootstrap.sh`, `llmwiki/.claude/hooks/session_start.py`, `harness/tests/test_session_start_remote_version.py` (mới), `skills/harness-update/SKILL.md` (sửa trong repo skills), `README.md`.

**Interfaces:**
- Consumes: `SKILLS_REF` (mặc định mới `rheinmir/skills#main`), cờ `--skills-only` của install.sh, `REPO_RAW/harness/version.json`, `OVERSTACK_VERSION_URL` (tuỳ chọn, trỏ `https://skills.giatbh.io.vn/healthz`), cache `~/.claude/harness/.remote-version.json` (1 lần/ngày).
- Produces: `install.sh --skills-only` = chỉ `npx skills add` + `skill-requires.py check --installed`; `session_start.remote_version_nudge(root)` in đúng một dòng `⬆ [harness] bản chuẩn X > máy bạn Y → curl bootstrap` khi `cmp_semver(local, remote) < 0`, im lặng khi bằng, fail-open khi mạng lỗi (timeout 2 s).

```python
# llmwiki/.claude/hooks/session_start.py
def remote_version_nudge(root: Path) -> None:
    try:
        gv = HARNESS_HOME / "version.json"
        if not gv.is_file():
            return
        local = json.loads(gv.read_text()).get("template_version", "0")
        cache = HARNESS_HOME / ".remote-version.json"
        today = datetime.date.today().isoformat()
        doc = json.loads(cache.read_text()) if cache.is_file() else {}
        if doc.get("date") != today:
            url = os.environ.get("OVERSTACK_VERSION_URL",
                                 "https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/version.json")
            with urllib.request.urlopen(url, timeout=2) as r:
                body = json.load(r)
            remote = body.get("template_version") or body.get("harness") or "0"
            doc = {"date": today, "remote": remote}
            cache.write_text(json.dumps(doc))
        if cmp_semver(local, doc.get("remote", "0")) < 0:
            print(f"⬆ [harness] bản chuẩn v{doc['remote']} mới hơn máy bạn v{local} — "
                  "cập nhật: curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash")
    except Exception:
        pass
```

### Task 5 — MCP đọc skill từ repo mới, công bố phiên bản, chế độ `read` cho hostname công khai
**Thoả:** YC-4 (MCP là nguồn phiên bản; phần đọc mở ra internet, phần chạy script không).

**Files:** `mcp/scripts/gen-catalog.py`, `mcp/src/catalog.ts`, `mcp/src/server.ts`, `mcp/src/http.ts`, `mcp/tests/server.test.ts`, `Dockerfile.mcp`, `docker-compose.stack.yml`, `.env.mcp.example`, `mcp/RUNBOOK.md`, `mcp/README.md`.

**Interfaces:**
- Consumes: `OVERSTACK_SKILLS_ROOT` (env; Docker: `/opt/skills/skills` clone `Rheinmir/skills#${SKILLS_REF}`), `metadata.loop` trong frontmatter, `harness/version.json`, `/opt/skills/version.json`.
- Produces: `GET /healthz` → `{ok, name, version, harness: "<template_version>", skills: {count, version, sha}, rules, tools, mode}`; `OVERSTACK_TOOLS=read` → chỉ `skills_list`, `skill_find`, `skill_get`, `rules_list`, `tools_list`, `tool_help`, `workspace_list` (không `tool_run`, `workspace_sync`, `orca_graph`, `rule_check`); compose service `cloudflared` (profile `tunnel`, `TUNNEL_TOKEN`) trỏ `http://overstack-mcp:8791`.

```ts
// mcp/src/server.ts
export type ToolMode = "read" | "core" | "all";
export function toolModeFromEnv(): ToolMode {
  const v = process.env.OVERSTACK_TOOLS;
  return v === "all" ? "all" : v === "read" ? "read" : "core";
}
// trong buildServer: if (mode !== "read") { registerTool("rule_check" …); registerTool("tool_run" …); registerTool("workspace_sync" …); registerTool("orca_graph" …); }
```

### Task 6 — nghiệm thu: cổng cục bộ, CI repo skills, fdk-uat 2 pha, số đo
**Thoả:** YC-2 (đo CI skill-only), YC-1 (người mới cài vẫn nhận đủ skill).

**Files:** `fdk/tools/medic.py` (chạy), `harness/scripts/fdk-gate.py` (chạy), `harness/poc-vendor-neutral/test-broad.sh` (chạy), `mcp/tests/*.test.ts` (chạy), `~/orca/skills/.github/workflows/ci.yml` (chạy trên GitHub, đọc thời gian bằng `gh run view`), `llmwiki/wiki/log.md`, `bench/skills/README.md` (số đo).

**Interfaces:**
- Consumes: canary `uat/<ts>` của setup + `SKILLS_REF=rheinmir/skills#main`; dự án trống `~/orca/overstack-uat-<ts>`; Orca worktree assert.
- Produces: bảng số đo (CI skills s, `npx skills add` s, skill LIVE sau cài, `skill-requires check` 0 thiếu trên máy này, medic xanh), dòng log `wiki/log.md`, release setup 1.3.127 trên `orca`.

```bash
cd ~/orca/setup && python3 fdk/tools/medic.py --ci && python3 harness/scripts/fdk-gate.py \
  && bash harness/poc-vendor-neutral/test-broad.sh && (cd mcp && npm test) \
  && python3 harness/scripts/skill-requires.py check --skills-dir ~/orca/skills/skills --harness-home ~/.claude/harness --ci
```

### Task 7 — host MCP tại skills.giatbh.io.vn (handoff vì chưa có đường vào k8s2)
**Thoả:** YC-4 (hostname công khai, nguồn phiên bản cho mọi dev).

**Files:** `mcp/RUNBOOK.md` (§7 skills.giatbh.io.vn), `docker-compose.stack.yml`, `.env.mcp.example`, `backlog.md`.

**Interfaces:**
- Consumes: trên k8s2: `/home/rhein/stacks/overstack-mcp/.env` có `TUNNEL_TOKEN` (từ Vault `secret/infra/cloudflare`), `OVERSTACK_TOOLS=read`, `SKILLS_REF=main`; Cloudflare Zero Trust tunnel có public hostname `skills.giatbh.io.vn → http://overstack-mcp:8791`.
- Produces: `curl https://skills.giatbh.io.vn/healthz` trả `harness` + `skills.version`; `claude mcp add --transport http overstack https://skills.giatbh.io.vn/mcp --header "Authorization: Bearer <token>"`; hook session_start đọc `OVERSTACK_VERSION_URL=https://skills.giatbh.io.vn/healthz` khi dev cấu hình.

```sh
# trên k8s2 (qua devops-agent stack_sync + stack_deploy, RUNBOOK §1)
printf 'OVERSTACK_TOOLS=read\nSKILLS_REF=main\nTUNNEL_TOKEN=<từ Vault secret/infra/cloudflare>\n' >> /home/rhein/stacks/overstack-mcp/.env
docker compose --project-directory /home/rhein/stacks/overstack-mcp -f docker-compose.stack.yml -p overstack-mcp --profile tunnel up -d --build
curl -fsS https://skills.giatbh.io.vn/healthz
```

## Origin
- User 14/10/2026: "thực hiện tách đi, còn MCP host trên cloudflared sao lại không nên thế, vì thực tế nó đã serve nhiều người và harness bị feedback là không đồng nhất phiên bản giữa các dev".
- Bản đánh giá `141026-skills-split-mcp-danh-gia.md` (fe713cb) và thí nghiệm nạp frontmatter 14/10 (`probe3.out`, haiku, 2 skill zz-ctrl/zz-nest gọi được qua tool Skill).
