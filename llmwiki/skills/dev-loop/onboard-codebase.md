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
   - Store findings in `llmwiki/wiki/entities/project-structure.md`.
2. **Deep Code Analysis**:
   - Scan for core domain logic (Services, Models, Controllers).
   - Identify patterns (e.g., Repository pattern, Event-driven, etc.).
   - Extract "Concepts" for `llmwiki/wiki/concepts/`.
3. **Frontend & Style Audit** *(skip if no frontend)*:
   - Identify UI framework (Next.js, React, Vue, etc.) and CSS approach (Tailwind, CSS Modules, styled-components, SCSS).
   - Extract design tokens: color palette, typography scale, spacing system, breakpoints — from `tailwind.config.*`, CSS variables, or theme files.
   - Identify component library in use (shadcn/ui, MUI, Ant Design, Radix, Headless UI, etc.) and any local component wrappers around it.
   - Trace global styles: `globals.css`, base layout files, font loading strategy.
   - Document naming conventions for components (PascalCase, feature-folder, colocated stories, etc.).
   - Note state management for UI (Zustand, Jotai, Context, Redux, etc.) and data-fetching pattern (React Query, SWR, server actions, etc.).
   - Capture routing conventions (file-based, nested layouts, auth guards).
   - Store all findings in `llmwiki/wiki/concepts/fe-style.md`.
4. **Business Logic Extraction**:
   - Reverse-engineer user stories and business rules from the code.
   - Generate/Update `AGENT-business.md`.
5. **Entity Cataloging**:
   - List all internal services, external APIs, and database tables.
   - Create detailed entries in `llmwiki/wiki/entities/`.
6. **Knowledge Injection**:
   - Synthesize all data into the Wiki structure.
   - Update `llmwiki/wiki/index.md` and `llmwiki/wiki/log.md`.
7. **Final Verification**:
   - Run a `lint` on the generated wiki to ensure no contradictions.

## Rules
- ALWAYS look at the code (implementation) to verify business claims.
- If documentation exists in `README.md` or comments, cross-reference it but prioritize truth in code.
- Focus on "Why" and "How" things work at the code level, not just "What" they do.
- NEVER overwrite existing manual wiki entries without checking the `## Origin` section.
- For `fe-style.md`: record actual values (hex codes, px/rem sizes, class names), not just descriptions — the goal is to let any agent reproduce the visual style without guessing.
