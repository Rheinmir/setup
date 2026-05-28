---
name: orca-onboard
description: Onboard new agent to Orca workspace — discover worktree, skills, inbox
---

# Skill: orca-onboard

## Purpose
Onboard codebase mới với Orca orchestration — phân tích song song 4 mảng.

## Triggers
- "onboard codebase", "phân tích codebase cũ", "onboard-codebase"

## Workflow
1. `orca orchestration task-create --spec "Phân tích infra: Docker, package.json, CI/CD"`
2. `orca orchestration task-create --spec "Phân tích backend: models, services, controllers"`
3. `orca orchestration task-create --spec "Phân tích frontend: components, routing, state"`
4. `orca orchestration task-create --spec "Phân tích business logic: domain entities, rules"`
5. `orca orchestration run` — coordinator dispatch song song
6. Agent ghi vào `llmwiki/wiki/concepts/` hoặc `llmwiki/wiki/entities/`
7. Sau: `lint` verify wiki