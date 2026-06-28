---
name: web-crawl
description: Crawl/scrape a website or single page into clean LLM-ready MARKDOWN. Use when the user wants to fetch a URL's content, scrape a site, extract an article/page as text, pull docs from the web into the wiki, or "crawl this link". Markdown (not raw HTML) = 5-10x fewer tokens. Built-now-adapt-later: works offline with no key via a builtin urllib→markdown backend; premium backends (Firecrawl/Crawl4AI/Jina) are a one-config adapter.
---

# Skill: web-crawl

Fetch a web page and turn it into clean markdown for the wiki / an LLM. Backend is a quarantined
adapter (`harness/web-crawl.config.yaml`, `verified:false`) — the builtin works now, no key.

## When to use
- User gives a URL and wants its content ("crawl this", "scrape", "fetch the page", "đọc trang này").
- Pulling external docs/articles into `raw/` or a wiki draft.
- Bulk reading many pages for research (prefer a premium backend then).

## Steps
1. **JS-heavy / rendered site?** In an agent session, prefer the in-session **WebFetch** tool
   (it renders JS + returns markdown). That is the richest path and needs no setup.
2. **Otherwise / scripted:** run the builtin (offline, no key):
   `python3 harness/scripts/web-crawl.py fetch "<URL>" --out raw/<slug>.md`
   (urllib fetch → deterministic HTML→markdown: headings, links, lists, code; strips script/style).
   Local HTML already downloaded? `web-crawl.py md <file.html>`.
3. **Many pages / better fidelity:** wire a backend in `harness/web-crawl.config.yaml`
   (`backend: firecrawl|crawl4ai|jina` + `api_key_env`/`endpoint`), then flip `verified:true`.
   Firecrawl also ships an MCP for agent loops.
4. **Land it:** save markdown to `raw/` (human inbox) or a wiki draft, then `/propose` / `ingest`
   to bring the distilled bits into the wiki — never write straight into `wiki/` (R1/R2).

## Rules
- Markdown, not raw HTML — that is the point (token savings + clean text).
- Respect robots.txt / site Terms; do not crawl auth-walled or disallowed content.
- The builtin backend is the offline fallback; the premium backend is the BNAL adapter — never
  present an un-wired premium backend as working.
- Self-test: `python3 harness/scripts/web-crawl.py --self-test`.

## Related
- `harness/scripts/web-crawl.py` + `harness/web-crawl.config.yaml` (the adapter).
- `/web-clone` — when you want the page's UI/look, not its text.
- `build-now-adapt-later` — the quarantine pattern this backend follows.
