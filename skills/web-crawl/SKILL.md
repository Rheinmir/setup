---
name: web-crawl
description: >-
  Crawl/scrape a website or single page into clean LLM-ready MARKDOWN. Use when the user wants to
  fetch a URL's content, scrape a site, extract an article/page as text, pull docs from the web
  into the wiki, or "crawl this link". Markdown (not raw HTML) = 5-10x fewer tokens. Built-now-
  adapt-later: works offline with no key via a builtin urllib→markdown backend; premium backends
  (Firecrawl/Crawl4AI/Jina) are a one-config adapter.
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: web-crawl

Fetch a web page and turn it into clean markdown for the wiki / an LLM. Backend is a quarantined
adapter (`harness/web-crawl.config.yaml`, `verified:false`) — the builtin works now, no key.

## WHAT

### Purpose và context
- **Purpose:** turn a URL (or a site) into clean markdown and land it in `raw/` or a wiki draft, never raw HTML.
- **Trigger (when to use):**
  - User gives a URL and wants its content ("crawl this", "scrape", "fetch the page", "đọc trang này").
  - Pulling external docs/articles into `raw/` or a wiki draft.
  - Bulk reading many pages for research (prefer a premium backend then).
- **Non-goals:** not cloning a page's UI/look (that is `/web-clone`); not writing straight into `wiki/` (goes via `/propose` / `ingest`); not crawling auth-walled or disallowed content.

### Mental model
`URL → backend (WebFetch in-session · builtin urllib+regex · premium adapter firecrawl/crawl4ai/jina) → markdown → raw/ or wiki draft → /propose or ingest → wiki`. The backend is a build-now-adapt-later quarantine: builtin = offline fallback, premium = the real upgrade behind one config file.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | URL | có | page or site to fetch; or a local `.html` file for `md` mode |
| In | `--out` path | không | where to save; convention `raw/<slug>.md` |
| In | premium backend config | không | `backend` + `api_key_env`/`endpoint` + `verified:true` in `harness/web-crawl.config.yaml` |
| Out | markdown file | có | clean text in `raw/` or a wiki draft |
| Out | backend disclosure | có | which backend produced it; builtin quality limits stated, never passed off as premium |

### Rules và capabilities
- RULE-01 (MUST): Markdown, not raw HTML — that is the point (token savings + clean text).
- RULE-02 (MUST): Respect robots.txt / site Terms; do not crawl auth-walled or disallowed content.
- RULE-03 (MUST): The builtin backend is the offline fallback; the premium backend is the BNAL adapter — never present an un-wired premium backend as working.
- RULE-04 (MUST): Self-test: `python3 harness/scripts/web-crawl.py --self-test`.
- Capabilities: outbound HTTP fetch (or in-session web fetch with JS render); HTML→markdown conversion; write to `raw/` or wiki draft only.

### Failure boundaries
- Site is JS-rendered and only the builtin is available → **partial** (builtin has no JS render); prefer WebFetch in-session or wire premium.
- Whole-site crawl requested without a wired premium backend → **blocked** on config (builtin is single page only); say so, do not fake it.
- robots.txt / Terms disallow or page is auth-walled → **blocked**, do not crawl.
- Fetch error → **failed**, report URL + error.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | judgment | URL, session type | JS-heavy / rendered site in an agent session → WebFetch tool (B01) | markdown | not in session → W02 |
| W02 | effect | URL | Scripted single static page: `web-crawl.py fetch` builtin (or `md` for local HTML) | `raw/<slug>.md` | JS/whole-site need → W03 |
| W03 | effect | config | Real crawling → wire premium backend in `harness/web-crawl.config.yaml`, flip `verified:true` (B02) | premium output | not wired → report limit, do not claim |
| W04 | effect | markdown | Land in `raw/` or wiki draft, then `/propose` / `ingest` | file saved | never into `wiki/` directly |

Chi tiết từng bước (nguồn chân lý cho W01–W04):

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

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | capability_optional | running in an agent session with WebFetch, page is JS-heavy | use WebFetch instead of the builtin script | no WebFetch → W02 builtin (no JS render, partial) | W04 |
| B02 | capability_optional | premium backend configured and `verified:true` | crawl via firecrawl/crawl4ai/jina adapter (JS, whole-site) | not wired → stay on builtin, state its limits (RULE-03) | W04 |
| B03 | user_optional | local HTML already downloaded | `web-crawl.py md <file.html>` instead of fetch | — | W04 |

### Validation và stopping
Backend is healthy when `python3 harness/scripts/web-crawl.py --self-test` passes. Done when the markdown file exists in `raw/` or a draft and the reply names the backend used. Quality of builtin output (extraction, JS content) is review-only, not claimed.

### Examples
- **Positive:** "crawl https://example.com/blog/post into raw" (static page, no key) → `python3 harness/scripts/web-crawl.py fetch "https://example.com/blog/post" --out raw/example-post.md` → markdown saved, then suggest `ingest`.
- **Boundary/failure:** "scrape the whole docs site" with `verified:false` → builtin is single page only → report that a premium backend must be wired in `harness/web-crawl.config.yaml`; do not claim the site was crawled.

### Reference — Related
- `harness/scripts/web-crawl.py` + `harness/web-crawl.config.yaml` (the backend adapter).
- **Real engines (the upgrade):** Firecrawl (`github.com/mendableai/firecrawl`, managed + MCP),
  Crawl4AI (`github.com/unclecode/crawl4ai`, OSS self-host), Jina Reader. MinerU (in your stars) for PDFs/docs.
- `/web-clone` — when you want the page's UI/look, not its text.
- `build-now-adapt-later` — the quarantine pattern this backend follows.
