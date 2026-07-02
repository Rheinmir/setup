---
type: draft
title: "Chốt cứng Trụ 4 (CI gate) + persona-lens cho council"
status: proposed
tags: [build-now-adapt-later, quality-gates, council, output-report]
proposed: 2026-07-01
id: 010726-trupillar4-council-persona
---

# 010726-trupillar4-council-persona

**Type:** draft · **Status:** proposed · **Proposed:** 2026-07-01

## What
Hai việc tách biệt, đều theo build-now-adapt-later: (B) chốt cứng Trụ 4 Quality Gates bằng một cổng CI tất định không-LLM; và triển khai lớp persona-lens "18 vĩ nhân" cho council (cơ chế bốc roster theo case).

## Boundary

**B — code-health (Trụ 4):**
- Contract (hard-gate, build now): mọi `.py` phải `py_compile` sạch — tất định, không model, chạy ở `fdk-gate` VÀ CI `repo-health` (chặn cả khi merge).
- Quarantine: lint sâu (ruff/pyflakes: undefined/import/unused) chưa cài + 81 file chưa từng lint → chạy **advisory** (in finding, không chặn); adapt later = dọn ruff-clean rồi `--enforce-lint`.

**Persona — council:**
- Contract (tất định, build now): thư viện 18 persona + 13 cặp đối-trọng + bảng case→roster + lệnh `council.py roster` (thuần lookup, ép ≥1 cặp đối-trọng). Engine rank/anonymize/mean-rank không đụng (selftest 12/12 vẫn pass).
- Quarantine: "model nào fill mỗi seat" vẫn ở `council.config.yaml` (`verified` flag) — persona-lens độc lập với nó.

## Unknowns (⚠️) pending verification
| Unknown | Best-guess source | Finalize by |
|---------|-------------------|-------------|
| Lint sâu (undefined/import/unused) | ruff default rules | cài ruff → dọn code → bật `--enforce-lint` ở code_health |
| Model nào fill mỗi council seat | `council.config.yaml` (ASSUMPTION) | chạy council thật → flip `verified:true` |
| Multi-model dispatch (orca cross-provider) | live test: chỉ claude+opencode khả dụng | wiring live-run + cài thêm provider CLI |

## Output
- **Trụ 4 → STRONG** (cổng CI tất định độc lập đang chặn; lint sâu + coverage là adapt-later — ghi trung thực trong eval HTML).
- **Persona dùng được ngay:** `council.py roster --case risk` → 3 ghế + cặp tension; `--profile lean`, `--personas a,b,c`, `--size 5`. Còn lại: wiring live-run + đưa vào overstack.html eval (session sau).

## Files
| File | Action |
|------|--------|
| `harness/validators/code_health.py` | created |
| `harness/scripts/fdk-gate.py` | modified (step code-health) |
| `.github/workflows/harness.yml` | modified (CI step) |
| `harness/council.personas.yaml` | created |
| `harness/scripts/council.py` | modified (cmd roster) |
| `harness/council.config.yaml` | modified (persona field) |
| `skills/council/SKILL.md` (+ mirror) | modified |

## Notes
- Invoked via: `/build-now-adapt-later` (trong /fdk).
- Commit: `490df16` (Trụ 4 code-health) + `04b3fcd` (persona). fdk-gate 20/20.
- Persona KHÔNG chữa PARTIAL Trụ 4 — B (cổng CI) mới chữa; persona làm giàu trục phán-xử Trụ 4.

## Origin
- **Draft:** `wiki/draft/orca/010726-trupillar4-council-persona.md`
- **Commit:** `490df16` + `04b3fcd`
- **Date promoted:** 2026-07-01 (output-report — giữ ở draft/orca)
