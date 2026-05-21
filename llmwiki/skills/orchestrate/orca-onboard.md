# Skill: orca-onboard

## Purpose
Onboarding codebase mới với Orca orchestration — phân tích song song 4 mảng.

## Triggers
- "onboard codebase", "phân tích codebase cũ", "onboard-codebase"

## Workflow
1. `orca orchestration task-create --spec "Phân tích infra: Docker, package.json, CI/CD"`
2. `orca orchestration task-create --spec "Phân tích backend: models, services, controllers"`
3. `orca orchestration task-create --spec "Phân tích frontend: components, routing, state"`
4. `orca orchestration task-create --spec "Phân tích business logic: domain entities, rules"`
5. `orca orchestration run` — coordinator tự dispatch song song
6. Mỗi agent ghi vào `llmwiki/wiki/concepts/` hoặc `llmwiki/wiki/entities/` tương ứng
7. Sau cùng: `lint` verify toàn bộ wiki
