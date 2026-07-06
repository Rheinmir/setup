---
type: decision
title: "ADR-017: Global-shared engine + repo-data travel (harness ở ~/.claude, chỉ dữ liệu đi theo git)"
status: accepted
tags: [adr, install, global-shared, travel, harness, engine, council-036, resolve-tool]
timestamp: 2026-07-06
id: ADR-017-global-shared-engine-repo-data-travel
---

# ADR-017: Global-shared engine + repo-data travel

## Bối cảnh
Trước đây có hai lối lẫn lộn: (a) bootstrap copy TOÀN BỘ engine vào TỪNG repo (GH#51 fix reachability) → trùng
lặp, mỗi update phải re-bootstrap từng repo ("mỗi lần 1 cái"); (b) hoặc "ship 30 tool vào manifest" (council-034
lo bloat per-repo). User phản biện: 30 tool KHÔNG phải feature mới cần chứng minh consumer — chúng là NĂNG LỰC NỀN,
mọi project nên có sẵn. Council-036 chốt: đặt engine 1 bản ở global, dùng chung.

## Quyết định
**Engine = GLOBAL-SHARED; chỉ DỮ LIỆU travel theo repo.** (khung 3 tầng — xem `harness/travel-policy.yaml` v2)
1. **`~/.claude/harness/`** (cài 1 lần qua `install-harness --global`, bootstrap tự gọi nếu thiếu): hooks +
   ENGINE (`fdk/tools/*`, `harness/scripts/*`) + `*.yaml` + `version.json`, **mirror cấu trúc repo**.
   Mọi project được gác dùng CHUNG; update 1 chỗ, mọi project hưởng.
   **ĐÍNH CHÍNH (test 2026-07-06):** RÀO CHẮN CI/pre-commit (`harness/poc-vendor-neutral/`, `harness/validators/`,
   `.github/workflows`, `.pre-commit-config.yaml`) **KHÔNG global** — chúng travel-in-repo (tầng 2). Lý do: GitHub-CI
   runner checkout repo (không có `~/.claude`); pre-commit chạy máy team (commit vào repo mới bảo vệ team). Bản đầu
   ADR này gộp `validators` vào global là SAI. `install-harness --global` copy validators xuống global CHỈ để hooks
   runtime fallback (find_validators), KHÔNG thay vai trò travel-in-repo cho CI/pre-commit.
2. **Repo (travel theo git)**: CHỈ `llmwiki/` (wiki-data, nguồn chân lý) + `.overstack.yaml` + `.harness-stamp`
   `{guarded_by: vX}` + hooks-wiring. Engine KHÔNG copy vào repo.
3. **Resolution** `hooklib.resolve_tool(root, rel)`: REPO-LOCAL (`root/rel`) → GLOBAL (`~/.claude/harness/rel`).
   Fail-open: thiếu cả hai → None → caller bỏ qua (không chặn phiên). `find_validators` cũng fallback global.
4. **Đánh dấu repo gác = STAMP TRAVEL** (`llmwiki/.harness-stamp`), KHÔNG registry global (council-036: registry
   drift + chết khi clone). Guard đổi `[ -d llmwiki ]` → `[ -f llmwiki/.harness-stamp ]` (kế hoạch).

## Hệ quả
- ✅ DRY: 30 tool 1 bản global, không bloat per-repo, update-once.
- ✅ Data travel + sống sót clone (wiki committed).
- ⚠️ Engine KHÔNG sống sót clone sang máy CHƯA cài global → clone máy mới phải `install-harness --global` 1 lần
  (như cài `git`/`node`). Data thì travel, engine cài-máy-một-lần.
- ⚠️ Version-skew: máy có global vY, repo stamp vX → `session_start` phải cảnh báo lệch major (stamp = hợp đồng,
  không tự ép chuẩn mới lên repo cũ — Taleb blast-radius).

## Kiểm chứng (test airtight trên 5 repo THẬT, 2026-07-06)
- **Tầng 1 engine → global (5 repo Orca thật, xoá HẲN engine local):** POSITIVE 5/5 (vẽ được qua global) ·
  NEGATIVE-CONTROL 5/5 (xoá engine global → KHÔNG vẽ → chứng minh gọi từ global, không ẩn local) · RESTORE 5/5.
  Global cô lập qua `OVERSTACK_HARNESS_HOME` (không đụng `~/.claude` thật). Giới hạn: chưa test chuỗi
  settings.json→hook-fire live-session (chạy `regen_docs` qua sys.path).
- **Tầng 2 poc → travel-in-repo:** poc local (`harness/poc-vendor-neutral/bin/llmwiki-validate.py` TRONG repo)
  chặn vi phạm R2 (thiếu `## Origin`) exit 1; file hợp lệ exit 0 → rào chắn hoạt động từ repo, CI/pre-commit đọc được.

## Origin
- Chốt bởi council-036 (`llmwiki/html/council/council-report-036-seed42.html`) + phản biện user 2026-07-06.
- Implement + verify phiên 2026-07-06. Chính sách: [[travel-policy]] (`harness/travel-policy.yaml` v2).
