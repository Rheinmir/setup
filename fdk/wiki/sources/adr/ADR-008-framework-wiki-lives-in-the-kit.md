---
type: decision
title: "ADR-008: wiki RIÊNG của framework sống trong the kit (fdk/wiki); llmwiki/wiki là khuôn per-project"
status: accepted
tags: [adr, fdk, wiki, kit, architecture, separation]
timestamp: 2026-06-28
---

# ADR-008: framework wiki sống trong the kit (fdk/wiki)

## Status
Accepted (2026-06-28).

## Context
Repo gốc (Rheinmir/setup) vừa là FRAMEWORK vừa là nguồn TEMPLATE cho mọi project downstream. Wiki riêng của framework (ADR-001..007, concepts harness/fdk/rule-registry, decisions…) đang nằm trong CHÍNH cái slot `llmwiki/wiki/` mà mọi project tiêu thụ dùng cho knowledge của họ. Không có "nhà riêng" cho meta-knowledge của framework → lẫn khái niệm "wiki framework" với "wiki một project".

Nguyên tắc (mở rộng ADR-004 "framework-dev context opt-in"): mọi thứ distill / dev-harness nên nằm trong **the kit** (`fdk/`) — gồm cả wiki riêng của framework.

Ràng buộc cứng: `llmwiki/wiki/` là HỢP ĐỒNG shipped — 8 skill + 2 installer `mkdir` nó cho project tiêu thụ, nên không đổi tên / bỏ được. Thuận lợi: validators ăn `--wiki-dir` (tham số hoá, không hardcode) nên một wiki-root thứ hai validate được mà gần như không tốn kém.

## Decision
1. **Wiki riêng của framework → `fdk/wiki/`** (the kit): toàn bộ ADR / concepts / entities / sources / evals / decisions / index / log chuyển sang đây, vẫn được harness validate đầy đủ.
2. **`llmwiki/wiki/` trong repo gốc = khuôn per-project**, giữ **1 file demo** (`concepts/example-concept.md`) để CI vẫn dogfood luật wiki trên cả hai root.
3. **Repath ~10 invocation** trỏ phần kiểm framework sang `fdk/wiki`: CI `repo-health`, pre-commit (3 always-run + 4 `files:` mở sang `^(fdk|llmwiki)/wiki/`), `hooklib.find_wiki_dir` thêm `fdk/wiki` ưu tiên, `wikieval` evals-dir, `docs-skill-okf-test`, `.gitignore` (draft/archive). Per-file validator R2/R5/R9 vốn match generic theo `(?:^|/)wiki/` nên KHÔNG cần đổi.
4. **Downstream KHÔNG đổi** — vẫn `llmwiki/wiki/`; project tiêu thụ không có `fdk/` nên `find_wiki_dir` fall-through đúng về `llmwiki/wiki`.

## Consequences
- (+) Tách bạch rõ: "wiki framework = `fdk/wiki` (the kit)" vs "khuôn per-project = `llmwiki/wiki`". Nhất quán ADR-004 / ADR-005 (mọi thứ dev-harness sống trong kit).
- (+) Framework wiki vẫn được gác đủ tầng (CI repo-health + pre-commit + Stop hook đều trỏ `fdk/wiki`) — không mất dogfood.
- (+) Downstream sạch y như trước (seed `llmwiki/wiki` rỗng, không kế thừa 64 file framework).
- (−) Repo gốc có hai wiki-root (`fdk/wiki` thật + `llmwiki/wiki` demo) — chấp nhận để dogfood cả hình dạng template.
- (−) ~10 invocation hardcode path phải bảo trì khi đổi — liệt kê rõ ở Decision-3 để không lạc.

## Origin
- **Source:** quyết định phiên 2026-06-28 — user: "wiki repo gốc cần chỗ lưu riêng… trong fdk folder, mọi thứ distill/dev-harness nên nằm trong kit". Thực thi: `mv llmwiki/wiki → fdk/wiki` + repath + tạo demo + verify (validators cả hai root xanh: index_sync/wiki-health/duplicate-basename/audit debt=False).
- **Liên quan:** [[ADR-004-framework-dev-context-opt-in]], [[ADR-005-logger-and-capabilities-travel-downstream]], [[fdk]].
- **Date:** 2026-06-28
