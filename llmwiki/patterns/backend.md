# Backend — Patterns & Anti-patterns

> Protected reference (overstack pattern library). Seeded best-guess — pending curation.

## Patterns
### Backend-for-Frontend (BFF)
- **When:** Multiple clients (web, mobile, partner) need different shapes, payload sizes, and auth flows from the same core services.
- **Do:** Give each client a dedicated, thin backend that aggregates and tailors downstream calls for that client's exact needs.
- **Why:** Eliminates over- and under-fetching, lets client teams ship independently, and keeps core domain services client-agnostic.

### Idempotency Keys for Safe Retries
- **When:** Clients retry writes (payments, orders, sign-ups) over flaky networks where a response may be lost after the server acted.
- **Do:** Require a client-supplied idempotency key on mutating requests; store the first result and replay it on duplicates.
- **Why:** Retries become safe — no double charges or duplicate records — the foundation for all client-side resilience.

### Server Components + Edge Rendering
- **When:** Content-heavy or personalized pages need fast first paint, small client bundles, and data fetching kept off the browser.
- **Do:** Render data-bound components on the server or edge, stream HTML, and hydrate only the interactive "islands."
- **Why:** Secrets and queries stay server-side, JavaScript shipped drops sharply, and rendering near users cuts latency.

### Transactional Outbox + Event-Driven Messaging
- **When:** Services must stay decoupled and a state change has to reliably trigger downstream work despite crashes or broker outages.
- **Do:** Write the event to an outbox table inside the same DB transaction, then relay it to the broker asynchronously.
- **Why:** Eliminates dual-write loss — database and event stream never diverge — enabling resilient, loosely-coupled consumers.

### Cache-Aside with Jittered TTL + Explicit Invalidation
- **When:** Read-heavy data tolerates brief staleness and you need to cut database load and tail latency.
- **Do:** Read from cache; on a miss load from source, populate with a jittered TTL, and invalidate on write.
- **Why:** Offloads hot reads cheaply while jitter and explicit invalidation prevent synchronized expiry and stale-forever bugs.

## Anti-patterns
### Distributed Monolith
- **Smell:** "Microservices" that deploy together, share one database, and call each other synchronously in long request chains.
- **Why bad:** You pay the full operational cost of distribution while keeping monolith coupling; one slow service stalls everything.
- **Instead:** Enforce per-service data ownership and async boundaries with contract tests — or consolidate back into a modular monolith.

### Retry Storm / Missing Timeouts
- **Smell:** Remote calls with no timeout, or retries with no backoff, jitter, or cap, layered across multiple hops.
- **Why bad:** A brief downstream blip amplifies into a self-inflicted DDoS as synchronized retries multiply and exhaust connection pools.
- **Instead:** Bound every call with a timeout; add exponential backoff with jitter, a circuit breaker, retry budgets, and deadline propagation.

### Breaking API Changes Without Versioning
- **Smell:** Fields renamed or removed in place; deployed clients, especially shipped mobile apps, break the moment the API ships.
- **Why bad:** Producer and consumer releases become tightly coupled, and old app versions in the wild silently fail.
- **Instead:** Make changes additive and backward-compatible, version explicitly, and deprecate on a published schedule backed by telemetry.

### Fat / Shared BFF
- **Smell:** One BFF serves every client and accumulates core business logic, so every client team queues behind it to ship.
- **Why bad:** The BFF becomes a shared bottleneck and a seed for a distributed monolith, defeating its decoupling purpose.
- **Instead:** Keep each BFF thin and client-specific; push domain logic down into the services it merely orchestrates.

### Synchronous Blocking on Async Work
- **Smell:** A request handler enqueues a job, then blocks or polls in-process while holding the HTTP connection until it finishes.
- **Why bad:** Server threads and connections stay pinned, throughput collapses under load, and the queue's decoupling benefit is lost.
- **Instead:** Return 202 with a job id; let clients poll a status endpoint or subscribe via webhook, SSE, or WebSocket.

## Origin
- Seeded from /last30days research (backend & system design 2026, BFF pattern) — 2026-06-29.
