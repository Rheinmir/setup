---
name: web-crawl
description: >-
  Crawl/scrape a website or single page into clean LLM-ready MARKDOWN. Use when the user wants to
  fetch a URL's content, scrape a site, extract an article/page as text, pull docs from the web
  into the wiki, or "crawl this link". Markdown (not raw HTML) = 5-10x fewer tokens. Built-now-
  adapt-later: works offline with no key via a builtin urllib→markdown backend; premium backends
  (Firecrawl/Crawl4AI/Jina) are a one-config adapter.
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
2. **Scripted, single static page (offline, no key):**
   `python3 harness/scripts/web-crawl.py fetch "<URL>" --out raw/<slug>.md`
   ⚠️ The `builtin` backend is **BASIC on purpose**: `urllib` fetch + regex HTML→markdown — **no JS
   rendering, single page only, no smart extraction**. It is the offline fallback, NOT Firecrawl-quality.
   Local HTML already downloaded? `web-crawl.py md <file.html>`.
3. **Real crawling (JS render, whole-site, clean extraction) → wire the real engine:** the premium
   backend is where the quality is — `backend: firecrawl|crawl4ai|jina` + `api_key_env`/`endpoint`
   in `harness/web-crawl.config.yaml`, then flip `verified:true`. **Firecrawl** (managed, crawl-to-
   markdown, ~5-10x token reduction, ships an **MCP** for agent loops) or **Crawl4AI** (open-source,
   self-host, adaptive selectors). The builtin exists so the skill runs today; these are the real upgrade.
4. **Land it:** save markdown to `raw/` (human inbox) or a wiki draft, then `/propose` / `ingest`
   to bring the distilled bits into the wiki — never write straight into `wiki/` (R1/R2).

## Rules
- Markdown, not raw HTML — that is the point (token savings + clean text).
- Respect robots.txt / site Terms; do not crawl auth-walled or disallowed content.
- The builtin backend is the offline fallback; the premium backend is the BNAL adapter — never
  present an un-wired premium backend as working.
- Self-test: `python3 harness/scripts/web-crawl.py --self-test`.

## Related
- `harness/scripts/web-crawl.py` + `harness/web-crawl.config.yaml` (the backend adapter).
- **Real engines (the upgrade):** Firecrawl (`github.com/mendableai/firecrawl`, managed + MCP),
  Crawl4AI (`github.com/unclecode/crawl4ai`, OSS self-host), Jina Reader. MinerU (in your stars) for PDFs/docs.
- `/web-clone` — when you want the page's UI/look, not its text.
- `build-now-adapt-later` — the quarantine pattern this backend follows.
