# Skill: onboard-codebase

## Purpose
Analyze an existing, unmapped codebase to extract deep technical and business context, then populate the Agentic Knowledge Base (Wiki) according to project standards.

## When to use
- When installing the agentic setup into a legacy or existing project.
- When the Wiki feels outdated or has a significant "context gap" regarding recent code changes.

## Steps
1. **Infrastructure Audit**:
   - Map the directory structure.
   - Identify the tech stack, entry points, and build/deploy scripts.
   - Store findings in `wiki/entities/project-structure.md`.
2. **Deep Code Analysis**:
   - Scan for core domain logic (Services, Models, Controllers).
   - Identify patterns (e.g., Repository pattern, Event-driven, etc.).
   - Extract "Concepts" for `wiki/concepts/`.
3. **Business Logic Extraction**:
   - Reverse-engineer user stories and business rules from the code.
   - Generate/Update `AGENT-business.md`.
4. **Entity Cataloging**:
   - List all internal services, external APIs, and database tables.
   - Create detailed entries in `wiki/entities/`.
5. **Knowledge Injection**:
   - Synthesize all data into the Wiki structure.
   - Update `wiki/index.md` and `wiki/log.md`.
6. **Final Verification**:
   - Run a `lint` on the generated wiki to ensure no contradictions.

## Rules
- ALWAYS look at the code (implementation) to verify business claims.
- If documentation exists in `README.md` or comments, cross-reference it but prioritize truth in code.
- Focus on "Why" and "How" things work at the code level, not just "What" they do.
- NEVER overwrite existing manual wiki entries without checking the `## Origin` section.
