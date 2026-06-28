# System Design — Patterns & Anti-patterns

> Protected reference (overstack pattern library). Seeded best-guess — pending curation.

## Patterns

### Stateless Horizontal Scaling
- **When:** Traffic outgrows a single node and you need elastic, fault-tolerant capacity.
- **Do:** Keep app servers stateless (session/state in Redis or DB) and run many identical instances behind a load balancer.
- **Why:** You scale out by adding nodes, and any instance can fail or be replaced without losing user state.

### Cache-Aside (with Write-Through)
- **When:** Read-heavy workloads repeat expensive queries against a hot dataset.
- **Do:** On read, check cache then fall back to DB and populate it (cache-aside); for hot writes, write-through to keep the cache fresh.
- **Why:** Cuts latency and database load, while explicit TTL and invalidation bound how stale reads can get.

### Asynchronous Processing via Message Queues
- **When:** Slow, spiky, or non-critical work should not block the request path.
- **Do:** Producers enqueue work; consumers process at their own rate while the queue absorbs bursts and decouples services.
- **Why:** It smooths load, isolates failures, and provides natural backpressure instead of cascading timeouts.

### Sharding & Replication
- **When:** Data volume or read traffic exceeds what one database can serve.
- **Do:** Shard by a stable key to spread writes, and add read replicas for read scaling and failover.
- **Why:** Enables horizontal data growth and high availability — accepting eventual consistency on replicas per CAP trade-offs.

### Idempotency Keys for Safe Retries
- **When:** Clients retry, networks duplicate, or at-least-once queues redeliver messages.
- **Do:** Require a client-supplied idempotency key and dedupe so repeated requests apply exactly once.
- **Why:** Retries and redeliveries become safe, preventing double charges or duplicate orders.

## Anti-patterns

### Premature Optimization
- **Smell:** Sharding, microservices, or caching are added before any load or profiling data exists.
- **Why bad:** It wastes effort and adds complexity that slows delivery and hides the real bottlenecks.
- **Instead:** Start simple, measure with profiling and observability, then optimize the proven hot path.

### Distributed Monolith
- **Smell:** "Microservices" deploy together, share one database, and break in lockstep.
- **Why bad:** You pay the network and ops cost of distribution but keep monolithic coupling.
- **Instead:** Define clear boundaries with private data per service, or stay a modular monolith until splitting is justified.

### Single Point of Failure
- **Smell:** One database, load balancer, or node whose failure takes the whole system down.
- **Why bad:** System availability is capped by your weakest non-redundant component.
- **Instead:** Replicate, add failover or standby, remove shared choke points, and rehearse with failure drills.

### Chatty Services
- **Smell:** One request fans out into dozens of fine-grained synchronous calls between services.
- **Why bad:** Latency and failure probability compound; tail latency dominates and timeouts cascade.
- **Instead:** Batch or coalesce calls, expose coarser APIs, cache results, or move work async.

### No Backpressure
- **Smell:** Producers accept unbounded work and queues grow without limit until memory or latency explodes.
- **Why bad:** Overload cascades into timeouts, OOMs, and full outages instead of graceful degradation.
- **Instead:** Bound queues, apply rate limiting and load shedding, and signal producers to slow down.

## Origin
- Seeded from /last30days research + System Design Interview notes (liquidslr/system-design-notes) — 2026-06-29.
