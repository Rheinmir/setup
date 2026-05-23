---
name: lint
description: Periodic wiki health check — orphans, missing links, contradictions, stale, index gaps
---

# Skill: lint

## When to invoke
After every 10 ingests, or when wiki feels stale/inconsistent.

## Steps

1. **Orphans** — `RUN: grep -rL "wiki/" --include="*.md" llmwiki/wiki/concepts/ llmwiki/wiki/entities/` → files not referenced anywhere. Flag each.

2. **Missing links** — scan pages for entity/concept names that exist as wiki files but aren't written as `[[wikilinks]]`. Fix in place.

3. **Contradictions** — compare claims about the same entity across ≤2 pages at a time. Flag pairs (file:line vs file:line). Do NOT pick a winner — flag for human review.

4. **Stale claims** — `RUN: grep -rl "raw/" --include="*.md" llmwiki/wiki/` → pages referencing raw/. Flag each.

5. **Index gaps** — `RUN: comm -23 <(find llmwiki/wiki -name "*.md" | sort) <(grep -o "llmwiki/wiki/[^)]*" llmwiki/wiki/index.md | sort)` → files missing from index. Add rows.

6. **Empty pages** — `RUN: for f in llmwiki/wiki/**/*.md; do [ $(wc -l < "$f") -lt 5 ] && echo "$f"; done` → flag for deletion or content.

7. **Missing Origin** — `RUN: grep -rL "## Origin" llmwiki/wiki/concepts/ llmwiki/wiki/entities/` → flag each as incomplete.

8. Append to `llmwiki/wiki/log.md`: `## YYYY-MM-DD — lint` with issues found/fixed vs flagged.

## Rules
- Fix automatically: missing links (step 2), index gaps (step 5).
- Flag, do not resolve: contradictions, orphans, empty pages — need human decision.
